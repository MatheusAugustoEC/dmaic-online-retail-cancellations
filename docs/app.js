(function(){
  "use strict";
  var css=getComputedStyle(document.documentElement);
  function c(n){return css.getPropertyValue(n).trim();}
  var app=document.getElementById('app');
  var NS='http://www.w3.org/2000/svg';
  function nf(v,d){return v.toLocaleString('pt-BR',{minimumFractionDigits:d,maximumFractionDigits:d});}
  function sv(w,h){return '<svg viewBox="0 0 '+w+' '+h+'" role="img" preserveAspectRatio="xMidYMid meet">';}
  function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  function attr(s){return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;');}
  function simples(){return app.getAttribute('data-reg')==='simples';}
  function RAMP(){return [c('--s5'),c('--s4'),c('--s3'),c('--s2'),c('--s1'),c('--s1')];}

  /* ================= dados do pipeline (injetados pelo build) ================= */
  var DADOS = JSON.parse(document.getElementById('dados-projeto').textContent);

  /* ================= entrega de arquivo ================= */
  function offerFile(filename, blob, hintEl){
    var viaViewer = (window.claude && typeof window.claude.use==='function')
      ? window.claude.use('downloads') : Promise.resolve(null);
    return viaViewer.then(function(dl){
      if(dl) return dl.save({filename:filename, data:blob}).catch(function(err){
        if(err && err.code==='declined') return;
        if(hintEl) hintEl.textContent='O download não pôde ser concluído aqui ('+(err&&err.code||'erro')+'). Abra a página publicada no GitHub Pages ou o arquivo direto do disco.';
      });
      var a=document.createElement('a');
      a.href=URL.createObjectURL(blob); a.download=filename;
      document.body.appendChild(a); a.click();
      setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); },800);
    });
  }

  /* ================= tooltip ================= */
  var tip=document.getElementById('tip');
  function showTip(html,e){
    tip.innerHTML=html; tip.hidden=false;
    var x=e.clientX+14, y=e.clientY+14;
    if(x+tip.offsetWidth>window.innerWidth-10) x=e.clientX-tip.offsetWidth-14;
    if(y+tip.offsetHeight>window.innerHeight-10) y=e.clientY-tip.offsetHeight-14;
    tip.style.left=x+'px'; tip.style.top=y+'px';
  }
  function hideTip(){ tip.hidden=true; }
  function clickHint(on){ return "<br><span style='opacity:.7'>"+(on?'clique para remover o filtro':'clique para filtrar')+"</span>"; }

  function wireTips(el){
    el.onmousemove=function(e){ var t=e.target.closest?e.target.closest('[data-tip]'):null; if(t) showTip(t.getAttribute('data-tip'),e); else hideTip(); };
    el.onmouseleave=hideTip;
    // [ZOOM] arrastar nao e clicar: depois de um arrasto, o clique sintetico
    // que o navegador dispara em seguida e ignorado (regra 18, interacao.md).
    el.onclick=function(e){ if(el._arrastou) return; var t=e.target.closest?e.target.closest('[data-flt]'):null; if(!t) return; hideTip(); toggleFlt(t.getAttribute('data-flt')); };
  }
  function toggleFlt(spec){
    spec.split(';').forEach(function(p){
      var k=p.slice(0,p.indexOf(':')), v=p.slice(p.indexOf(':')+1);
      var val = k==='c' ? v : +v;
      var arr=sel[k], j=arr.indexOf(val);
      if(j>=0) arr.splice(j,1); else arr.push(val);
    });
    renderDash();
  }

  function crosshair(el,o){
    var svg=el.querySelector('svg');
    var ln=document.createElementNS(NS,'line');
    [['y1',o.T],['y2',o.H-o.B],['stroke',c('--ink-3')],['stroke-width','1'],['stroke-dasharray','3 3'],['visibility','hidden'],['pointer-events','none']].forEach(function(a){ln.setAttribute(a[0],a[1]);});
    var dt=document.createElementNS(NS,'circle');
    [['r','5.5'],['stroke',c('--surface')],['stroke-width','2'],['visibility','hidden'],['pointer-events','none']].forEach(function(a){dt.setAttribute(a[0],a[1]);});
    var hit=document.createElementNS(NS,'rect');
    [['x',o.L],['y',o.T],['width',o.W-o.L-o.R],['height',o.H-o.T-o.B],['fill','transparent']].forEach(function(a){hit.setAttribute(a[0],a[1]);});
    hit.style.cursor = o.click ? 'pointer' : 'crosshair';
    svg.appendChild(ln); svg.appendChild(dt); svg.appendChild(hit);
    var a0=o.i0||0, a1=(o.i1!=null?o.i1:o.n-1); // [ZOOM] janela visivel, para o crosshair mapear certo com zoom
    function idx(e){
      var r=svg.getBoundingClientRect();
      var x=(e.clientX-r.left)*o.W/r.width;
      var i=Math.round(a0+(x-o.L)/(o.W-o.L-o.R)*(a1-a0));
      return Math.max(a0,Math.min(a1,i));
    }
    hit.addEventListener('mousemove',function(e){
      var i=idx(e), x=o.X(i), y=o.Y(i);
      ln.setAttribute('x1',x); ln.setAttribute('x2',x); ln.setAttribute('visibility','visible');
      dt.setAttribute('cx',x); dt.setAttribute('cy',y); dt.setAttribute('fill',o.color?o.color(i):c('--accent')); dt.setAttribute('visibility','visible');
      showTip(o.tip(i),e);
    });
    hit.addEventListener('mouseleave',function(){ ln.setAttribute('visibility','hidden'); dt.setAttribute('visibility','hidden'); hideTip(); });
    if(o.click) hit.addEventListener('click',function(e){ if(el._arrastou) return; hideTip(); o.click(idx(e)); });
  }

  /* ================= zoom (regra 18, interacao.md) =================
     Arrastar sobre a area do grafico amplia; Ctrl + roda aproxima/afasta;
     duplo clique ou "Ver tudo" (so aparece com zoom ativo) volta. A roda
     SOZINHA continua rolando a pagina. No celular, sem arrasto (bloquearia
     a rolagem) - so a pinca nativa do navegador. Ouvintes de arrasto no
     documento, uma vez so, lendo o estado DRAG (nunca acumulados). */
  var ZOOM={}, DRAG=null;
  var TOQUE = window.matchMedia && window.matchMedia('(pointer: coarse)').matches;
  function zoomBar(el,zoomed,reset){
    var bar=document.createElement('div'); bar.className='zoom-bar';
    bar.innerHTML='<span class="zoom-hint">'+(simples()?'Arraste sobre o gráfico para ampliar · Ctrl + roda do mouse aproxima e afasta':'Arraste para ampliar · Ctrl + roda: zoom · duplo clique: ver tudo')+'</span>'+
      (zoomed?'<button type="button" class="zoom-reset">Ver tudo</button>':'');
    el.appendChild(bar);
    if(zoomed) bar.querySelector('.zoom-reset').onclick=function(e){ e.stopPropagation(); reset(); };
  }
  function zoomavel(el,o){
    /* o: {W,H,L,R,T,B, xy (true=dois eixos; false=so o tempo), aplicar(x0,x1,y0,y1 em px), roda(fator,px,py), reset()} */
    var svg=el.querySelector('svg');
    function pt(e){ var r=svg.getBoundingClientRect(); return [(e.clientX-r.left)*o.W/r.width,(e.clientY-r.top)*o.H/r.height]; }
    function dentro(p){ return p[0]>=o.L && p[0]<=o.W-o.R && p[1]>=o.T && p[1]<=o.H-o.B; }
    if(!TOQUE){
      svg.onmousedown=function(e){
        if(e.button!==0) return; var p=pt(e); if(!dentro(p)) return;
        e.preventDefault(); DRAG={el:el,svg:svg,o:o,p0:p,box:null,pt:pt};
      };
    } else {
      svg.onmousedown=null;
    }
    svg.onwheel=function(e){
      if(!e.ctrlKey) return; e.preventDefault();
      var p=pt(e); if(!dentro(p)) return; o.roda(e.deltaY<0?0.8:1.25,p[0],p[1]);
    };
    svg.ondblclick=function(e){ e.preventDefault(); o.reset(); };
    svg.style.cursor = TOQUE ? 'default' : 'crosshair';
  }
  function clampPx(v,a,b){ return Math.max(a,Math.min(b,v)); }
  document.addEventListener('mousemove',function(e){
    if(!DRAG) return; var d=DRAG, o=d.o, p=d.pt(e);
    var x=clampPx(p[0],o.L,o.W-o.R), y=clampPx(p[1],o.T,o.H-o.B);
    if(!d.box && Math.abs(x-d.p0[0])<5 && Math.abs(y-d.p0[1])<5) return;
    if(!d.box){
      d.box=document.createElementNS(NS,'rect');
      [['fill',c('--accent')],['fill-opacity','.12'],['stroke',c('--accent')],['stroke-width','1'],['stroke-dasharray','4 3'],['pointer-events','none']].forEach(function(a){d.box.setAttribute(a[0],a[1]);});
      d.svg.appendChild(d.box); hideTip();
    }
    var x0=Math.min(d.p0[0],x), x1=Math.max(d.p0[0],x);
    var y0=o.xy?Math.min(d.p0[1],y):o.T, y1=o.xy?Math.max(d.p0[1],y):o.H-o.B;
    d.box.setAttribute('x',x0); d.box.setAttribute('y',y0); d.box.setAttribute('width',x1-x0); d.box.setAttribute('height',y1-y0);
    d.sel=[x0,x1,y0,y1];
  });
  document.addEventListener('mouseup',function(){
    if(!DRAG) return; var d=DRAG; DRAG=null;
    if(!d.box) return;
    d.el._arrastou=true; setTimeout(function(){ d.el._arrastou=false; },0);
    var s=d.sel; d.box.remove();
    if(s[1]-s[0]<8 || (d.o.xy && s[3]-s[2]<8)) return;
    d.o.aplicar(s[0],s[1],s[2],s[3]);
  });
  var medidor=document.createElement('canvas').getContext('2d');
  function larguraTexto(t,px){ medidor.font=px+'px "Public Sans",sans-serif'; return medidor.measureText(t).width; }
  function cruza(a,b){ return a[0]<b[0]+b[2] && b[0]<a[0]+a[2] && a[1]<b[1]+b[3] && b[1]<a[1]+a[3]; }

  /* ================= dimensoes (do JSON) =================
     g = pais, f = faixa de quantidade, s = recorrencia, p = produto, m = mes.
     Convencao de uma letra herdada do molde; so os ROTULOS mudam de dominio. */
  var MES = DADOS.dashboard.meses;               // ["2010-12",...,"2011-12"]
  var PAIS = DADOS.dashboard.paises;
  var FAIXA = DADOS.dashboard.faixas;
  var SEG = DADOS.dashboard.segmentos;
  var PROD = DADOS.dashboard.produtos;
  var cubo = DADOS.dashboard.cubo;                // [{m,g,f,s,p,it,ca,es}]
  var MESES_PT = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
  var MESES_PTF = ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'];
  function mesCurto(iso){ var p=iso.split('-'); return MESES_PT[+p[1]-1]+'/'+p[0].slice(2); }
  function mesLongo(iso){ var p=iso.split('-'); return MESES_PTF[+p[1]-1]+' de '+p[0]; }

  var sel={m:[],g:[],f:[],s:[],p:[],c:[]};

  function filtra(ex){
    ex=ex||[];
    function on(k){ return ex.indexOf(k)<0 && sel[k].length>0; }
    return cubo.filter(function(r){
      if(on('m') && sel.m.indexOf(r.m)<0) return false;
      if(on('g') && sel.g.indexOf(r.g)<0) return false;
      if(on('f') && sel.f.indexOf(r.f)<0) return false;
      if(on('s') && sel.s.indexOf(r.s)<0) return false;
      if(on('p') && sel.p.indexOf(r.p)<0) return false;
      if(on('c') && sel.c.indexOf(r.g+'|'+r.f)<0) return false;
      return true;
    });
  }
  function soma(rows){return rows.reduce(function(a,r){a.it+=r.it;a.ca+=r.ca;a.es+=r.es;return a;},{it:0,ca:0,es:0});}
  var TOTAL=soma(cubo), TXBASE=100*TOTAL.ca/TOTAL.it;

  /* ================= dropdowns ================= */
  var openDD=null;
  function closeDD(){ if(openDD){ openDD.pan.hidden=true; openDD.btn.setAttribute('aria-expanded','false'); openDD=null; } }
  function dropdown(hostId,key,labels,allLabel){
    var host=document.getElementById(hostId); host.innerHTML='';
    var arr=sel[key];
    var btn=document.createElement('button');
    btn.type='button'; btn.className='dd-btn'; btn.setAttribute('aria-expanded','false'); btn.setAttribute('aria-haspopup','true');
    btn.textContent = arr.length===0 ? allLabel : (arr.length===1 ? labels[arr[0]] : arr.length+' de '+labels.length+' selecionados');
    var pan=document.createElement('div'); pan.className='dd-panel'; pan.hidden=true;
    var quick=document.createElement('div'); quick.className='dd-quick';
    var bAll=document.createElement('button'); bAll.type='button'; bAll.textContent='Selecionar todos';
    var bNone=document.createElement('button'); bNone.type='button'; bNone.textContent='Limpar';
    function refresh(){
      var a=sel[key];
      btn.textContent = a.length===0 ? allLabel : (a.length===1 ? labels[a[0]] : a.length+' de '+labels.length+' selecionados');
      Array.prototype.forEach.call(pan.querySelectorAll('.chk'),function(el,i){
        var on=a.indexOf(i)>=0;
        el.setAttribute('aria-pressed',String(on));
        el.querySelector('.bx').textContent=on?'✓':'';
      });
      renderDash(true);
    }
    bAll.onclick=function(e){ e.stopPropagation(); sel[key]=labels.map(function(_,i){return i;}); refresh(); };
    bNone.onclick=function(e){ e.stopPropagation(); sel[key]=[]; refresh(); };
    quick.appendChild(bAll); quick.appendChild(bNone); pan.appendChild(quick);
    labels.forEach(function(lab,i){
      var b=document.createElement('button'); b.type='button'; b.className='chk';
      var on=arr.indexOf(i)>=0;
      b.setAttribute('aria-pressed',String(on));
      b.innerHTML='<span class="bx">'+(on?'✓':'')+'</span><span>'+esc(lab)+'</span>';
      b.onclick=function(e){ e.stopPropagation(); var j=sel[key].indexOf(i); if(j>=0) sel[key].splice(j,1); else sel[key].push(i); refresh(); };
      pan.appendChild(b);
    });
    btn.onclick=function(e){ e.stopPropagation(); var was=!pan.hidden; closeDD(); if(was) return; pan.hidden=false; btn.setAttribute('aria-expanded','true'); openDD={pan:pan,btn:btn}; };
    pan.onclick=function(e){ e.stopPropagation(); };
    host.appendChild(btn); host.appendChild(pan);
  }
  document.addEventListener('click',closeDD);
  document.addEventListener('keydown',function(e){ if(e.key==='Escape') closeDD(); });

  /* ================= graficos genericos ================= */
  function barrasH(el,rows,o){
    var W=440,rowH=32,L=150,R=68,T=4,H=T+rows.length*rowH+4,pw=W-L-R;
    var max=Math.max.apply(null,rows.map(function(r){return r[1];}))||1;
    var ramp=RAMP(), any=!!(o.selected&&o.selected.length);
    var s=sv(W,H);
    rows.forEach(function(r,i){
      var y=T+i*rowH, bw=Math.max(2,(pw*r[1])/max);
      var on = any ? o.selected.indexOf(r[3])>=0 : true;
      var tp=esc(r[0])+'<br><b>'+esc(o.fmt(r[1]))+'</b>'+(r[2]?'<br>'+esc(r[2]):'')+(o.key?clickHint(any&&on):'');
      var flt=o.key?' data-flt="'+o.key+':'+r[3]+'"':'';
      s+='<text x="'+(L-10)+'" y="'+(y+rowH/2+4)+'" text-anchor="end" font-size="11" font-weight="'+(any&&on?600:400)+'" fill="'+(on?c('--ink-2'):c('--ink-3'))+'">'+esc(r[0].length>26?r[0].slice(0,25)+'…':r[0])+'</text>';
      s+='<rect x="'+L+'" y="'+(y+7)+'" width="'+bw.toFixed(1)+'" height="'+(rowH-15)+'" rx="3" fill="'+ramp[Math.min(i,ramp.length-1)]+'" fill-opacity="'+(on?1:0.35)+'"'+(any&&on?' stroke="'+c('--ink')+'" stroke-width="1.5"':'')+' data-tip="'+attr(tp)+'"'+flt+'/>';
      s+='<text x="'+(L+bw+8).toFixed(1)+'" y="'+(y+rowH/2+4.5)+'" font-size="11" font-weight="600" font-family="IBM Plex Mono,monospace" fill="'+(on?c('--ink'):c('--ink-3'))+'" pointer-events="none">'+esc(o.fmt(r[1]))+'</text>';
    });
    el.innerHTML=s+'</svg>'; wireTips(el);
  }

  function paretoAcum(el,rows){
    var W=460,H=256,L=48,R=46,T=16,B=52;
    var pw=W-L-R, ph=H-T-B, n=rows.length;
    var tot=rows.reduce(function(a,r){return a+r[1];},0), max=rows[0][1];
    var slot=pw/n, bw=Math.min(40,slot*0.6), acc=0, ramp=RAMP();
    var s=sv(W,H);
    [0,0.5,1].forEach(function(q){
      var yy=T+ph-(ph*q);
      s+='<text x="'+(L-7)+'" y="'+(yy+3.5)+'" text-anchor="end" font-size="9.5" font-family="IBM Plex Mono,monospace" fill="'+c('--ink-3')+'">£'+nf(max*q/1000,0)+'k</text>';
      s+='<text x="'+(W-R+6)+'" y="'+(yy+3.5)+'" font-size="9.5" font-family="IBM Plex Mono,monospace" fill="'+c('--crit')+'">'+(q*100)+'%</text>';
      s+='<line x1="'+L+'" y1="'+yy+'" x2="'+(W-R)+'" y2="'+yy+'" stroke="'+c('--line')+'" stroke-width="1"/>';
    });
    var y80=T+ph*0.2;
    s+='<line x1="'+L+'" y1="'+y80+'" x2="'+(W-R)+'" y2="'+y80+'" stroke="'+c('--line-2')+'" stroke-width="1.2" stroke-dasharray="4 3"/>';
    s+='<text x="'+(W-R+6)+'" y="'+(y80+3.5)+'" font-size="9.5" font-family="IBM Plex Mono,monospace" fill="'+c('--ink-3')+'">80%</text>';
    var pts=[];
    rows.forEach(function(r,i){
      var x=L+slot*i+(slot-bw)/2, h=(ph*r[1])/max, y=T+ph-h;
      acc+=r[1];
      var tp=esc(r[0])+'<br><b>£ '+nf(r[1],0)+'</b> '+(simples()?'devolvidos':'estornados')+'<br>'+nf(100*r[1]/tot,1)+'% do total';
      s+='<rect x="'+x.toFixed(1)+'" y="'+y.toFixed(1)+'" width="'+bw.toFixed(1)+'" height="'+h.toFixed(1)+'" rx="2" fill="'+ramp[i]+'" data-tip="'+attr(tp)+'"/>';
      pts.push([x+bw/2, T+ph-(ph*acc/tot), acc, r[0]]);
      s+='<text x="'+(x+bw/2).toFixed(1)+'" y="'+(T+ph+14)+'" text-anchor="middle" font-size="9.5" fill="'+c('--ink-3')+'">'+esc(r[0].split(' ')[0])+'</text>';
    });
    var d=pts.map(function(p,i){return (i?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1);}).join('');
    s+='<path d="'+d+'" fill="none" stroke="'+c('--crit')+'" stroke-width="2" pointer-events="none"/>';
    pts.forEach(function(p){
      var tp=(simples()?'Somando até ':'Acumulado até ')+esc(p[3])+'<br><b>'+nf(100*p[2]/tot,0)+'%</b> do total<br>£ '+nf(p[2],0);
      s+='<circle cx="'+p[0].toFixed(1)+'" cy="'+p[1].toFixed(1)+'" r="7" fill="transparent" data-tip="'+attr(tp)+'"/>';
      s+='<circle cx="'+p[0].toFixed(1)+'" cy="'+p[1].toFixed(1)+'" r="3.4" fill="'+c('--crit')+'" pointer-events="none"/>';
    });
    el.innerHTML=s+'</svg>'; wireTips(el);
  }

  /* Carta p' de Laney - semanal, limites VARIAVEIS (nao uma faixa fixa),
     porque o n semanal varia e os limites de Laney sao proporcionais a
     sigma_pi de cada semana. Duas semanas ficam fora, ambas por censura a
     direita (explicado no texto ao redor, nao no grafico). */
  function cartaPLaney(el){
    var CP=DADOS.carta_p, n=CP.taxa.length;
    // [M1] R alargado para reservar uma margem FIXA, fora da area do grafico,
    // onde o rotulo do limite mora - nunca mais colado na curva ou na linha
    // pontilhada, porque essa faixa nao tem gridline nem dado nenhum.
    var W=880,H=290,L=42,R=112,T=16,B=34;
    var pw=W-L-R, ph=H-T-B;
    var z=ZOOM[el.id], i0=z?z.i0:0, i1=z?z.i1:n-1; // [ZOOM] so o eixo do tempo
    function X(i){return L+(pw*(i-i0))/(i1-i0);} function Y(v){return T+ph-(ph*v)/ymax;}
    var ymax=Math.ceil(Math.max.apply(null,CP.ucl.concat(CP.taxa))/1)+0.5;
    var s=sv(W,H), clip='clip-'+el.id;
    s+='<defs><clipPath id="'+clip+'"><rect x="'+L+'" y="'+(T-8)+'" width="'+pw+'" height="'+(ph+16)+'"/></clipPath></defs>';
    var bandTop=[],bandBot=[];
    for(var bi=i0;bi<=i1;bi++){ bandTop.push([X(bi),Y(CP.ucl[bi])]); bandBot.push([X(bi),Y(CP.lcl[bi])]); }
    var bandPath='M'+bandTop.map(function(p){return p[0].toFixed(1)+' '+p[1].toFixed(1);}).join('L')
      +'L'+bandBot.slice().reverse().map(function(p){return p[0].toFixed(1)+' '+p[1].toFixed(1);}).join('L')+'Z';
    s+='<path d="'+bandPath+'" fill="'+c('--band')+'"/>';
    for(var g=0;g<=ymax;g++){
      s+='<line x1="'+L+'" y1="'+Y(g)+'" x2="'+(W-R)+'" y2="'+Y(g)+'" stroke="'+c('--line')+'" stroke-width="1"/>';
      s+='<text x="'+(L-7)+'" y="'+(Y(g)+3.5)+'" text-anchor="end" font-size="10" font-family="IBM Plex Mono,monospace" fill="'+c('--ink-3')+'">'+g+'%</text>';
    }
    s+='<line x1="'+L+'" y1="'+Y(CP.cl)+'" x2="'+(W-R)+'" y2="'+Y(CP.cl)+'" stroke="'+c('--accent')+'" stroke-width="1" stroke-opacity=".45"/>';
    function pathOf(arr){ var d=''; for(var k=i0;k<=i1;k++) d+=(d?'L':'M')+X(k).toFixed(1)+' '+Y(arr[k]).toFixed(1); return d; }
    s+='<path d="'+pathOf(CP.ucl)+'" fill="none" stroke="'+c('--crit')+'" stroke-width="1.3" stroke-dasharray="5 4"/>';
    s+='<path d="'+pathOf(CP.lcl)+'" fill="none" stroke="'+c('--crit')+'" stroke-width="1.3" stroke-dasharray="5 4"/>';
    // [M1] rotulo do limite, FIXO na margem reservada (x > W-R), fora da area
    // plotada - nunca sobre a curva, a faixa ou a linha pontilhada, e o mesmo
    // lugar com ou sem zoom (regra 18).
    s+='<line x1="'+(W-R+14)+'" y1="'+(T+2)+'" x2="'+(W-R+14)+'" y2="'+(H-B-2)+'" stroke="'+c('--line')+'" stroke-width="1"/>';
    var yMid=(T+H-B)/2;
    s+='<text x="'+(W-R+24)+'" y="'+(yMid-8)+'" font-size="10" font-weight="600" font-family="IBM Plex Mono,monospace" fill="'+c('--crit')+'">'+(simples()?'limite':'UCL/LCL')+'</text>';
    s+='<text x="'+(W-R+24)+'" y="'+(yMid+7)+'" font-size="10" font-weight="600" font-family="IBM Plex Mono,monospace" fill="'+c('--crit')+'">'+(simples()?'do normal':'(Laney)')+'</text>';
    s+='<g clip-path="url(#'+clip+')"><path d="'+pathOf(CP.taxa)+'" fill="none" stroke="'+c('--accent')+'" stroke-width="2" stroke-linejoin="round"/>';
    for(var q=i0;q<=i1;q++){ if(CP.fora[q]) s+='<circle cx="'+X(q).toFixed(1)+'" cy="'+Y(CP.taxa[q]).toFixed(1)+'" r="5.5" fill="'+c('--crit')+'" stroke="'+c('--surface')+'" stroke-width="2"/>'; }
    s+='</g>';
    s+='<text x="'+L+'" y="'+(H-9)+'" font-size="10" fill="'+c('--ink-3')+'">'+esc(CP.semanas[i0])+'</text>';
    s+='<text x="'+(L+pw/2)+'" y="'+(H-9)+'" text-anchor="middle" font-size="10" fill="'+c('--ink-3')+'">'+esc(CP.semanas[Math.floor((i0+i1)/2)])+'</text>';
    s+='<text x="'+(W-R)+'" y="'+(H-9)+'" text-anchor="end" font-size="10" fill="'+c('--ink-3')+'">'+esc(CP.semanas[i1])+'</text>';
    el.innerHTML=s+'</svg>';
    crosshair(el,{W:W,H:H,L:L,R:R,T:T,B:B,n:n,i0:i0,i1:i1,X:X,Y:function(i){return Y(CP.taxa[i]);},
      color:function(i){ return CP.fora[i]?c('--crit'):c('--accent'); },
      tip:function(i){
        var artefato=CP.classificacao[i]==='artefato_censura';
        return 'Semana de '+esc(CP.semanas[i])+' (n='+nf(CP.n[i],0)+')'+
          '<br><b>'+nf(CP.taxa[i],2)+'%</b> '+(simples()?'voltaram':'de itens cancelados')+
          (artefato?('<br><b>'+(simples()?'sem tempo de o cancelamento aparecer':'artefato de medição · censura à direita')+'</b>'):'');
      }});
    // [ZOOM] so no eixo do tempo (regra 18) - os limites (banda, UCL/LCL) sao
    // sempre os do periodo inteiro; o zoom muda so o que se ve.
    function idxDe(px){ return i0+(px-L)/pw*(i1-i0); }
    function janela(a,b){
      a=Math.max(0,Math.floor(a)); b=Math.min(n-1,Math.ceil(b));
      if(b-a<4){ var m=(a+b)/2; a=Math.max(0,Math.round(m-2)); b=Math.min(n-1,a+4); }
      if(a<=0 && b>=n-1) delete ZOOM[el.id]; else ZOOM[el.id]={i0:a,i1:b};
      cartaPLaney(el);
    }
    zoomavel(el,{W:W,H:H,L:L,R:R,T:T,B:B,xy:false,
      aplicar:function(x0,x1){ janela(idxDe(x0),idxDe(x1)); },
      roda:function(f,px){ var m=idxDe(px); janela(m-(m-i0)*f, m+(i1-m)*f); },
      reset:function(){ delete ZOOM[el.id]; cartaPLaney(el); }});
    zoomBar(el,!!z,function(){ delete ZOOM[el.id]; cartaPLaney(el); });
  }

  function linhaMes(el,vals,counts){
    var W=880,H=250,L=42,R=14,T=14,B=28, n=vals.length, pw=W-L-R, ph=H-T-B;
    var ymax=Math.max(4,Math.ceil(Math.max.apply(null,vals)));
    function X(i){return L+(pw*i)/(n-1);} function Y(v){return T+ph-(ph*v)/ymax;}
    var s=sv(W,H), step=pw/(n-1);
    sel.m.forEach(function(i){ s+='<rect x="'+(X(i)-step/2).toFixed(1)+'" y="'+T+'" width="'+step.toFixed(1)+'" height="'+ph+'" fill="'+c('--accent-soft')+'"/>'; });
    for(var g=0;g<=ymax;g++){
      s+='<line x1="'+L+'" y1="'+Y(g)+'" x2="'+(W-R)+'" y2="'+Y(g)+'" stroke="'+c('--line')+'" stroke-width="1"/>';
      s+='<text x="'+(L-7)+'" y="'+(Y(g)+3.5)+'" text-anchor="end" font-size="10" font-family="IBM Plex Mono,monospace" fill="'+c('--ink-3')+'">'+g+'%</text>';
    }
    var d=''; vals.forEach(function(v,i){ d+=(i?'L':'M')+X(i).toFixed(1)+' '+Y(v).toFixed(1); });
    s+='<path d="'+d+'" fill="none" stroke="'+c('--accent')+'" stroke-width="2.4" stroke-linejoin="round"/>';
    vals.forEach(function(v,i){
      var on=sel.m.indexOf(i)>=0;
      s+='<circle cx="'+X(i).toFixed(1)+'" cy="'+Y(v).toFixed(1)+'" r="'+(on?5:3.2)+'" fill="'+c('--accent')+'"/>';
      s+='<text x="'+X(i).toFixed(1)+'" y="'+(H-9)+'" text-anchor="middle" font-size="10" font-weight="'+(on?700:400)+'" fill="'+(on?c('--ink'):c('--ink-3'))+'">'+mesCurto(MES[i])+'</text>';
    });
    el.innerHTML=s+'</svg>';
    crosshair(el,{W:W,H:H,L:L,R:R,T:T,B:B,n:n,X:X,Y:function(i){return Y(vals[i]);},
      tip:function(i){
        var on=sel.m.indexOf(i)>=0;
        return mesLongo(MES[i])+'<br><b>'+nf(vals[i],2)+'%</b> '+(simples()?'voltaram':'de taxa')+'<br>'+nf(counts[i],0)+' itens'+clickHint(on);
      },
      click:function(i){ toggleFlt('m:'+i); }});
  }

  /* [I2] piso de n (mesmo criterio do H4/Pareto, n>=50) para nao colorir
     celula pouco confiavel na mesma escala, e escala de cor ROBUSTA (baseada
     no 2o maior valor elegivel, nao no maximo bruto) para uma unica celula
     extrema nao lavar a escala inteira - achado: Australia x Q1 (n=87) tinha
     65,5% de taxa contra 14,2% da 2a maior, dominando sozinha o gradiente. */
  var MIN_N_MATRIX = 50;
  function heat(el,rows){
    var W=880, L=190, R=14, T=26, rh=40, cw=(W-L-R)/4, H=T+rows.length*rh+8;
    var eligible=[];
    rows.forEach(function(r){ r.v.forEach(function(x,j){ if(r.n[j]>=MIN_N_MATRIX) eligible.push(x); }); });
    eligible.sort(function(a,b){return b-a;});
    var max = eligible.length>=2 ? eligible[1] : (eligible[0]||0);
    if(!max) max = eligible[0]||1;
    var ramp=[c('--s1'),c('--s2'),c('--s3'),c('--s4'),c('--s5')];
    var s=sv(W,H);
    FAIXA.forEach(function(f,j){
      var hi=sel.f.indexOf(j)>=0;
      s+='<text x="'+(L+cw*j+cw/2)+'" y="16" text-anchor="middle" font-size="10.5" font-weight="'+(hi?700:600)+'" font-family="IBM Plex Mono,monospace" fill="'+(hi?c('--ink'):c('--ink-3'))+'">'+esc(f)+'</text>';
    });
    rows.forEach(function(r,i){
      var y=T+i*rh, gOn=!sel.g.length||sel.g.indexOf(r.gi)>=0;
      s+='<text x="'+(L-12)+'" y="'+(y+rh/2+4)+'" text-anchor="end" font-size="11" font-weight="'+(sel.g.indexOf(r.gi)>=0?600:400)+'" fill="'+(gOn?c('--ink-2'):c('--ink-3'))+'">'+esc(r.k)+'</text>';
      r.v.forEach(function(v,j){
        var key=r.gi+'|'+j;
        var picked=sel.c.indexOf(key)>=0;
        var active=gOn && (!sel.f.length||sel.f.indexOf(j)>=0) && (!sel.c.length||picked);
        var suficiente = r.n[j] >= MIN_N_MATRIX;
        var idx = suficiente ? Math.min(4,Math.floor(5*Math.min(v,max)/(max*1.001))) : 0;
        var dark = suficiente && idx>=3;
        var fillColor = suficiente ? ramp[idx] : c('--sunk');
        var tp = suficiente
          ? esc(r.k)+' · '+esc(FAIXA[j])+'<br><b>'+nf(v,2)+'%</b> '+(simples()?'voltam':'de taxa')+'<br>'+nf(r.n[j],0)+' itens · £ '+nf(r.e[j],0)+clickHint(picked)
          : esc(r.k)+' · '+esc(FAIXA[j])+'<br>'+(simples()?'poucos itens para confiar no número':'n insuficiente (&lt;'+MIN_N_MATRIX+')')+'<br>'+nf(r.n[j],0)+' itens'+clickHint(picked);
        s+='<rect x="'+(L+cw*j+2)+'" y="'+(y+2)+'" width="'+(cw-4)+'" height="'+(rh-4)+'" fill="'+fillColor+'" fill-opacity="'+(active?1:0.28)+'"'+(!suficiente?' stroke="'+c('--line-2')+'" stroke-width="1" stroke-dasharray="3 2"':'')+(picked?' stroke="'+c('--ink')+'" stroke-width="2.5"':'')+' data-tip="'+attr(tp)+'" data-flt="c:'+key+'"/>';
        var label = suficiente ? nf(v,1) : '—';
        s+='<text x="'+(L+cw*j+cw/2)+'" y="'+(y+rh/2+4)+'" text-anchor="middle" font-size="11" font-weight="600" font-family="IBM Plex Mono,monospace" fill="'+(dark&&active?c('--surface'):(suficiente?c('--ink'):c('--ink-3')))+'" fill-opacity="'+(active?1:0.5)+'" pointer-events="none">'+label+'</text>';
      });
    });
    el.innerHTML=s+'</svg>'; wireTips(el);
  }

  /* Dispersao volume x taxa, por PRODUTO (chave 'p', nao 'g' - unico uso desta
     dimensao no dashboard, por isso o filtro esta fixo em 'p' aqui dentro). */
  function scatter(el,pts){
    // [ZOOM] L alargado (era 54): a uma bolha no menor valor de X, o CENTRO
    // cai exatamente em x=L - com raio ate 30px, ela encostava nos rotulos
    // do eixo vertical (2,4% / 4,9% / 7,3%). Rotulo do eixo tambem recuado
    // (L-38, nao L-7) para sobrar um vao limpo entre texto e bolha.
    var W=880,H=330,L=95,R=170,T=18,B=42, pw=W-L-R, ph=H-T-B;
    var xmaxTotal=Math.max.apply(null,pts.map(function(p){return p.x;}))*1.12||1;
    var ymaxTotal=Math.max.apply(null,pts.map(function(p){return p.y;}))*1.18||1;
    var rmax=Math.max.apply(null,pts.map(function(p){return p.r;}))||1;
    var z=ZOOM[el.id], xa=z?z.x0:0, xb=z?z.x1:xmaxTotal, ya=z?z.y0:0, yb=z?z.y1:ymaxTotal;
    function X(v){return L+(pw*(v-xa))/(xb-xa);} function Y(v){return T+ph-(ph*(v-ya))/(yb-ya);}
    function fmtX(v){ var span=xb-xa; return span<4000 ? nf(v,0) : nf(v/1000, span<40000?1:0)+' mil'; }
    var any=sel.p.length>0, ramp=RAMP(), clip='clip-'+el.id;
    var s=sv(W,H);
    s+='<defs><clipPath id="'+clip+'"><rect x="'+L+'" y="'+T+'" width="'+pw+'" height="'+ph+'"/></clipPath></defs>';
    for(var gy=0;gy<=4;gy++){
      var yy=T+ph-(ph*gy)/4;
      s+='<line x1="'+L+'" y1="'+yy+'" x2="'+(W-R)+'" y2="'+yy+'" stroke="'+c('--line')+'" stroke-width="1"/>';
      s+='<text x="'+(L-38)+'" y="'+(yy+3.5)+'" text-anchor="end" font-size="10" font-family="IBM Plex Mono,monospace" fill="'+c('--ink-3')+'">'+nf(ya+(yb-ya)*gy/4,1)+'%</text>';
    }
    for(var gx=(z?0:1);gx<=4;gx++){
      var xx=L+(pw*gx)/4;
      s+='<text x="'+(gx?xx:xx+2)+'" y="'+(T+ph+15)+'" text-anchor="'+(gx?'middle':'start')+'" font-size="9.5" font-family="IBM Plex Mono,monospace" fill="'+c('--ink-3')+'">'+fmtX(xa+(xb-xa)*gx/4)+'</text>';
    }
    s+='<text x="'+(L+pw/2)+'" y="'+(H-6)+'" text-anchor="middle" font-size="10.5" fill="'+c('--ink-3')+'">'+(simples()?'itens vendidos →':'volume de itens →')+'</text>';
    // bolhas maiores por baixo (continuam clicaveis as pequenas por cima)
    var vis=pts.map(function(p,i){ var r=8+22*Math.sqrt(p.r/rmax); return {p:p,i:i,r:r,cx:X(p.x),cy:Y(p.y)}; })
      .filter(function(b){ return b.cx>=L-b.r && b.cx<=W-R+b.r && b.cy>=T-b.r && b.cy<=T+ph+b.r; });
    s+='<g clip-path="url(#'+clip+')">';
    vis.slice().sort(function(a,b){return b.r-a.r;}).forEach(function(g){
      var on=!any||sel.p.indexOf(g.p.pi)>=0;
      var tp=esc(g.p.k)+'<br><b>'+nf(g.p.y,2)+'%</b> '+(simples()?'voltam':'de taxa')+'<br>'+nf(g.p.x,0)+' itens<br>£ '+nf(g.p.r,0)+' '+(simples()?'devolvidos':'estornados')+clickHint(any&&on);
      s+='<circle cx="'+g.cx.toFixed(1)+'" cy="'+g.cy.toFixed(1)+'" r="'+g.r.toFixed(1)+'" fill="'+ramp[g.i%ramp.length]+'" fill-opacity="'+(on?0.88:0.2)+'" stroke="'+(any&&on?c('--ink'):c('--surface'))+'" stroke-width="'+(any&&on?2:1.5)+'" data-tip="'+attr(tp)+'" data-flt="p:'+g.p.pi+'"/>';
    });
    s+='</g>';
    // [I3] rotulos sem sobreposicao: a maior bolha escolhe primeiro; tenta a
    // direita, depois a esquerda; se nao couber sem cruzar outro rotulo ou
    // outra bolha, fica so no balao (hover). Com zoom, as bolhas se afastam
    // e mais rotulos cabem.
    var postos=[], fs=9.5;
    vis.slice().sort(function(a,b){return b.r-a.r;}).forEach(function(g){
      var lab=g.p.k.length>26?g.p.k.slice(0,25)+'…':g.p.k;
      var w=larguraTexto(lab,fs)+2, h=fs+3, y=g.cy-h/2-1;
      var opcoes=[[g.cx+g.r+6,y],[g.cx-g.r-6-w,y]];
      for(var k=0;k<opcoes.length;k++){
        var bx=[opcoes[k][0],opcoes[k][1],w,h];
        if(bx[0]<L+2 || bx[0]+w>W-4 || bx[1]<T || bx[1]+h>T+ph) continue;
        var bate=postos.some(function(o){return cruza(bx,o);}) || vis.some(function(o){
          return o!==g && cruza(bx,[o.cx-o.r,o.cy-o.r,2*o.r,2*o.r]); });
        if(bate) continue;
        postos.push(bx);
        var on=!any||sel.p.indexOf(g.p.pi)>=0;
        s+='<text x="'+bx[0].toFixed(1)+'" y="'+(bx[1]+fs).toFixed(1)+'" font-size="'+fs+'" fill="'+(on?c('--ink-2'):c('--ink-3'))+'" pointer-events="none">'+esc(lab)+'</text>';
        break;
      }
    });
    el.innerHTML=s+'</svg>'; wireTips(el);
    function dado(px,py){ return [xa+(px-L)/pw*(xb-xa), ya+(T+ph-py)/ph*(yb-ya)]; }
    function janela(x0,x1,y0,y1){
      x0=Math.max(0,x0); y0=Math.max(0,y0); x1=Math.min(xmaxTotal,x1); y1=Math.min(ymaxTotal,y1);
      if(x1-x0>=xmaxTotal*0.98 && y1-y0>=ymaxTotal*0.98) delete ZOOM[el.id]; else ZOOM[el.id]={x0:x0,x1:x1,y0:y0,y1:y1};
      scatter(el,pts);
    }
    zoomavel(el,{W:W,H:H,L:L,R:R,T:T,B:B,xy:true,
      aplicar:function(px0,px1,py0,py1){ var a=dado(px0,py1), b=dado(px1,py0); janela(a[0],b[0],a[1],b[1]); },
      roda:function(f,px,py){ var m=dado(px,py); janela(m[0]-(m[0]-xa)*f, m[0]+(xb-m[0])*f, m[1]-(m[1]-ya)*f, m[1]+(yb-m[1])*f); },
      reset:function(){ delete ZOOM[el.id]; scatter(el,pts); }});
    zoomBar(el,!!z,function(){ delete ZOOM[el.id]; scatter(el,pts); });
  }

  /* ================= dashboard ================= */
  var sortK='es', sortDir=-1, showAll=false, lastList=[];

  function renderActive(){
    var box=document.getElementById('active'), items=[];
    function add(k,v,lab){ items.push('<button type="button" class="achip" data-k="'+k+'" data-v="'+attr(String(v))+'" title="Remover este filtro">'+esc(lab)+' <b>×</b></button>'); }
    sel.m.forEach(function(v){add('m',v,mesLongo(MES[v]));});
    sel.g.forEach(function(v){add('g',v,PAIS[v]);});
    sel.f.forEach(function(v){add('f',v,FAIXA[v]);});
    sel.s.forEach(function(v){add('s',v,SEG[v]);});
    sel.p.forEach(function(v){add('p',v,PROD[v]);});
    sel.c.forEach(function(v){ var q=v.split('|'); add('c',v,PAIS[+q[0]]+' · '+FAIXA[+q[1]]); });
    box.innerHTML = items.length ? items.join('') : '<span class="noflt">'+(simples()?'Nenhum filtro — mostrando tudo.':'Sem filtros ativos.')+'</span>';
    box.onclick=function(e){
      var b=e.target.closest?e.target.closest('.achip'):null; if(!b) return;
      var k=b.getAttribute('data-k'), v=b.getAttribute('data-v'), val=k==='c'?v:+v;
      var j=sel[k].indexOf(val); if(j>=0) sel[k].splice(j,1);
      renderDash();
    };
  }

  function porDim(rows,labels,key,metric){
    return labels.map(function(lab,i){
      var r=soma(rows.filter(function(x){return x[key]===i;}));
      var v = metric==='es' ? r.es : (r.it?100*r.ca/r.it:0);
      var extra = metric==='es' ? nf(r.it,0)+' itens · '+nf(r.it?100*r.ca/r.it:0,1)+'%' : nf(r.it,0)+' itens · £ '+nf(r.es,0);
      return [lab,v,extra,i,r.it];
    });
  }

  function renderDash(fromMenu){
    if(!fromMenu){
      closeDD();
      dropdown('dd-mes','m',MES.map(mesLongo),'Ano todo');
      dropdown('dd-pais','g',PAIS,'Todos os países');
      dropdown('dd-faixa','f',FAIXA,'Todas as faixas');
      dropdown('dd-seg','s',SEG,'Todos os clientes');
      dropdown('dd-produto','p',PROD,'Todos os produtos');
    }
    renderActive();
    document.getElementById('heat-clear').hidden = sel.c.length===0;

    var rows=filtra(), t=soma(rows), vazio=t.it===0;
    var semFiltro = !sel.m.length && !sel.g.length && !sel.f.length && !sel.s.length && !sel.p.length && !sel.c.length;
    document.getElementById('d-empty').hidden=!vazio;
    document.getElementById('fcount').innerHTML='<b>'+nf(t.it,0)+'</b> de '+nf(TOTAL.it,0)+' itens · <b>'+nf(100*t.it/TOTAL.it,1)+'%</b> da base';
    var taxa=vazio?0:100*t.ca/t.it;
    document.getElementById('kpis').innerHTML=
      '<div class="kpi"><div class="k">Itens</div><div class="v">'+nf(t.it,0)+'</div><div class="s">no recorte</div></div>'+
      '<div class="kpi"><div class="k"><span class="sim">Voltam</span><span class="tec">Taxa</span></div><div class="v">'+nf(taxa,2)+'%</div><div class="s">'+(vazio||!taxa?'—':'1 a cada '+Math.round(100/taxa))+'</div></div>'+
      '<div class="kpi"><div class="k"><span class="sim">Devolvido</span><span class="tec">Estornado</span></div><div class="v">£ '+nf(t.es,0)+'</div><div class="s">'+nf(TOTAL.es?100*t.es/TOTAL.es:0,1)+'% do total</div></div>'+
      '<div class="kpi"><div class="k"><span class="sim">Diferença da média</span><span class="tec">Δ vs. base</span></div><div class="v">'+(vazio?'—':(taxa>=TXBASE?'+':'')+nf(taxa-TXBASE,2))+'</div><div class="s">'+(semFiltro?(simples()?'sem filtro, é sempre 0,00':'sem filtro vs. si mesma = 0'):'pontos percentuais')+'</div></div>';

    var rm=filtra(['m']), cnt=[];
    var porMes=MES.map(function(_,i){ var r=soma(rm.filter(function(x){return x.m===i;})); cnt.push(r.it); return r.it?100*r.ca/r.it:0; });
    linhaMes(document.getElementById('d-linha'),porMes,cnt);

    var pct=function(v){return nf(v,1)+'%';}, gbp=function(v){return '£ '+nf(v,0);};
    var rg=filtra(['g']);
    barrasH(document.getElementById('d-pais'),porDim(rg,PAIS,'g').sort(function(a,b){return b[1]-a[1];}).slice(0,14),{fmt:pct,key:'g',selected:sel.g});
    barrasH(document.getElementById('d-faixa'),porDim(filtra(['f']),FAIXA,'f'),{fmt:pct,key:'f',selected:sel.f});
    barrasH(document.getElementById('d-seg'),porDim(filtra(['s']),SEG,'s').sort(function(a,b){return b[1]-a[1];}),{fmt:pct,key:'s',selected:sel.s});
    var rp=filtra(['p']);
    barrasH(document.getElementById('d-impacto'),porDim(rp,PROD,'p','es').sort(function(a,b){return b[1]-a[1];}),{fmt:gbp,key:'p',selected:sel.p});

    var rh=filtra(['g','f','c']);
    heat(document.getElementById('d-heat'),PAIS.map(function(lab,i){
      var v=[],n=[],e=[];
      FAIXA.forEach(function(_,j){ var r=soma(rh.filter(function(x){return x.g===i&&x.f===j;})); v.push(r.it?100*r.ca/r.it:0); n.push(r.it); e.push(r.es); });
      return {k:lab,gi:i,v:v,n:n,e:e};
    }));

    scatter(document.getElementById('d-scatter'),PROD.map(function(lab,i){
      var r=soma(rp.filter(function(x){return x.p===i;}));
      return {k:lab,pi:i,x:r.it,y:r.it?100*r.ca/r.it:0,r:r.es};
    }).filter(function(p){return p.x>0;}));

    var agg={};
    rows.forEach(function(r){ var k=r.g+'|'+r.s+'|'+r.f; (agg[k]=agg[k]||{g:r.g,s:r.s,f:r.f,it:0,ca:0,es:0}); agg[k].it+=r.it; agg[k].ca+=r.ca; agg[k].es+=r.es; });
    var list=Object.keys(agg).map(function(k){var o=agg[k]; o.tx=o.it?100*o.ca/o.it:0; return o;});
    list.sort(function(a,b){
      var A,B;
      if(sortK==='g'){A=PAIS[a.g];B=PAIS[b.g];} else if(sortK==='s'){A=SEG[a.s];B=SEG[b.s];} else if(sortK==='f'){A=a.f;B=b.f;} else {A=a[sortK];B=b[sortK];}
      if(typeof A==='string') return sortDir*A.localeCompare(B,'pt-BR');
      return sortDir*(A-B);
    });
    lastList=list;
    var shown=showAll?list:list.slice(0,12);
    document.getElementById('d-tabela').innerHTML = shown.length ? shown.map(function(r){
      return '<tr><td>'+esc(PAIS[r.g])+'</td><td>'+SEG[r.s]+'</td><td>'+FAIXA[r.f]+'</td><td style="text-align:right" class="mono">'+nf(r.it,0)+'</td><td style="text-align:right" class="mono">'+nf(r.tx,1)+'%</td><td style="text-align:right" class="mono">£ '+nf(r.es,0)+'</td></tr>';
    }).join('') : '<tr><td colspan="6" style="color:var(--ink-3)">Nenhuma combinação no recorte.</td></tr>';
    var tb=document.getElementById('t-all');
    tb.hidden = list.length<=12;
    tb.textContent = showAll ? 'Mostrar só as 12 primeiras' : 'Mostrar todas ('+list.length+')';
    Array.prototype.forEach.call(document.querySelectorAll('#d-tab th.sortable'),function(th){
      if(th.getAttribute('data-k')===sortK){ th.setAttribute('aria-sort',sortDir<0?'descending':'ascending'); th.querySelector('.arw').textContent=sortDir<0?'↓':'↑'; }
      else { th.removeAttribute('aria-sort'); th.querySelector('.arw').textContent='↕'; }
    });
  }

  Array.prototype.forEach.call(document.querySelectorAll('#d-tab th.sortable'),function(th){
    th.addEventListener('click',function(){
      var k=th.getAttribute('data-k');
      if(k===sortK) sortDir=-sortDir; else { sortK=k; sortDir=(k==='g'||k==='s'||k==='f')?1:-1; }
      renderDash();
    });
  });
  document.getElementById('f-reset').addEventListener('click',function(){ sel={m:[],g:[],f:[],s:[],p:[],c:[]}; renderDash(); });
  document.getElementById('heat-clear').addEventListener('click',function(){ sel.c=[]; renderDash(); });
  document.getElementById('t-all').addEventListener('click',function(){ showAll=!showAll; renderDash(); });

  /* ================= planilha .xlsx ================= */
  function xe(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
  function cStr(ref,v,st){return '<c r="'+ref+'" t="inlineStr"'+(st?' s="'+st+'"':'')+'><is><t xml:space="preserve">'+xe(v)+'</t></is></c>';}
  function cNum(ref,v,st){return '<c r="'+ref+'"'+(st?' s="'+st+'"':'')+'><v>'+v+'</v></c>';}
  function filtrosTexto(){
    var p=[];
    if(sel.m.length) p.push('Período: '+sel.m.map(function(v){return mesLongo(MES[v]);}).join(', '));
    if(sel.g.length) p.push('País: '+sel.g.map(function(v){return PAIS[v];}).join(', '));
    if(sel.f.length) p.push('Tamanho: '+sel.f.map(function(v){return FAIXA[v];}).join(', '));
    if(sel.s.length) p.push('Cliente: '+sel.s.map(function(v){return SEG[v];}).join(', '));
    if(sel.p.length) p.push('Produto: '+sel.p.map(function(v){return PROD[v];}).join(', '));
    if(sel.c.length) p.push('Células: '+sel.c.map(function(v){var q=v.split('|');return PAIS[+q[0]]+' × '+FAIXA[+q[1]];}).join(', '));
    return p.length ? p.join(' | ') : 'Nenhum — base completa';
  }
  function buildXlsx(list){
    if(!window.JSZip) return Promise.reject({code:'sem_biblioteca'});
    var head=['País','Cliente','Tamanho do pedido','Itens','Cancelados','Taxa','Devolvido (£)'];
    var widths=[20,16,20,12,12,10,16];
    var L=['A','B','C','D','E','F','G'];
    var rows='<row r="1">'+head.map(function(h,i){return cStr(L[i]+'1',h,1);}).join('')+'</row>';
    list.forEach(function(r,k){
      var n=k+2;
      rows+='<row r="'+n+'">'+cStr('A'+n,PAIS[r.g])+cStr('B'+n,SEG[r.s])+cStr('C'+n,FAIXA[r.f])+
        cNum('D'+n,r.it,2)+cNum('E'+n,r.ca,2)+cNum('F'+n,(r.tx/100).toFixed(6),3)+cNum('G'+n,r.es,4)+'</row>';
    });
    var last=list.length+1, NSX='http://schemas.openxmlformats.org/spreadsheetml/2006/main';
    var XH='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>';
    var sheet1=XH+'<worksheet xmlns="'+NSX+'"><dimension ref="A1:G'+last+'"/>'+
      '<sheetViews><sheetView workbookViewId="0" tabSelected="1"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'+
      '<sheetFormatPr defaultRowHeight="15"/><cols>'+widths.map(function(w,i){return '<col min="'+(i+1)+'" max="'+(i+1)+'" width="'+w+'" customWidth="1"/>';}).join('')+'</cols>'+
      '<sheetData>'+rows+'</sheetData><autoFilter ref="A1:G'+last+'"/></worksheet>';
    var t=soma(filtra());
    var info=[
      ['Sobre esta planilha','',5],
      ['',''],
      ['Gerada em',new Date().toLocaleString('pt-BR')],
      ['Filtros ativos',filtrosTexto()],
      ['Combinações',String(list.length)],
      ['Itens no recorte',nf(t.it,0)],
      ['Origem','Online Retail — UCI Machine Learning Repository (Chen, Sain & Guo, 2012), varejista real do Reino Unido, dez/2010 a dez/2011.'],
      ['Base','Cubo pré-agregado (mês × país × faixa de quantidade × recorrência × produto). Não contém transações individuais.'],
      ['Janela','Cobre o ANO INTEIRO, incluindo os ~2,3 meses finais mantidos em quarentena (holdout) durante a análise e abertos só ao final — difere da taxa oficial do Painel, que usa só a janela de exploração madura.'],
      ['Exclusão conhecida (1)','StockCode 23843 (par pedido/cancelamento de 80.995 unidades no mesmo dia, evento isolado) excluído da lista de produtos nomeados pelo corte de n≥50 (mesmo critério do H4).'],
      ['Exclusão conhecida (2)','StockCode 23166 / InvoiceNo 541431 (74.215 unidades, £77.183,60, 99,5% do estorno do produto) — correção pós-banca de 2026-09-22: receita desta linha zerada apenas nas agregações de impacto (Pareto e coluna Devolvido desta planilha); o produto continua contando normalmente em itens/taxa (137 linhas legítimas).'],
    ];
    var rows2=info.map(function(r,k){ var n=k+1; return '<row r="'+n+'">'+cStr('A'+n,r[0],r[2]||(k>1?6:0))+(r[1]?cStr('B'+n,r[1]):'')+'</row>'; }).join('');
    var sheet2=XH+'<worksheet xmlns="'+NSX+'"><sheetViews><sheetView workbookViewId="0"/></sheetViews><sheetFormatPr defaultRowHeight="15"/>'+
      '<cols><col min="1" max="1" width="22" customWidth="1"/><col min="2" max="2" width="96" customWidth="1"/></cols><sheetData>'+rows2+'</sheetData></worksheet>';
    var styles=XH+'<styleSheet xmlns="'+NSX+'">'+
      '<numFmts count="1"><numFmt numFmtId="164" formatCode="&quot;£&quot; #,##0"/></numFmts>'+
      '<fonts count="4"><font><sz val="11"/><name val="Calibri"/></font>'+
      '<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>'+
      '<font><b/><sz val="14"/><color rgb="FF17476B"/><name val="Calibri"/></font>'+
      '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'+
      '<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'+
      '<fill><patternFill patternType="solid"><fgColor rgb="FF17476B"/><bgColor indexed="64"/></patternFill></fill></fills>'+
      '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'+
      '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'+
      '<cellXfs count="7">'+
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'+
        '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>'+
        '<xf numFmtId="3" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'+
        '<xf numFmtId="10" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'+
        '<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'+
        '<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>'+
        '<xf numFmtId="0" fontId="3" fillId="0" borderId="0" xfId="0" applyFont="1"/>'+
      '</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>';
    var workbook=XH+'<workbook xmlns="'+NSX+'" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'+
      '<bookViews><workbookView activeTab="0"/></bookViews><sheets><sheet name="Dados" sheetId="1" r:id="rId1"/><sheet name="Sobre" sheetId="2" r:id="rId2"/></sheets>'+
      '<definedNames><definedName name="_xlnm._FilterDatabase" localSheetId="0" hidden="1">Dados!$A$1:$G$'+last+'</definedName></definedNames></workbook>';
    var REL='http://schemas.openxmlformats.org/officeDocument/2006/relationships';
    var wbRels=XH+'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+
      '<Relationship Id="rId1" Type="'+REL+'/worksheet" Target="worksheets/sheet1.xml"/>'+
      '<Relationship Id="rId2" Type="'+REL+'/worksheet" Target="worksheets/sheet2.xml"/>'+
      '<Relationship Id="rId3" Type="'+REL+'/styles" Target="styles.xml"/></Relationships>';
    var rootRels=XH+'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+
      '<Relationship Id="rId1" Type="'+REL+'/officeDocument" Target="xl/workbook.xml"/></Relationships>';
    var CT='application/vnd.openxmlformats-officedocument.spreadsheetml';
    var types=XH+'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'+
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'+
      '<Default Extension="xml" ContentType="application/xml"/>'+
      '<Override PartName="/xl/workbook.xml" ContentType="'+CT+'.sheet.main+xml"/>'+
      '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="'+CT+'.worksheet+xml"/>'+
      '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="'+CT+'.worksheet+xml"/>'+
      '<Override PartName="/xl/styles.xml" ContentType="'+CT+'.styles+xml"/></Types>';
    var zip=new window.JSZip();
    zip.file('[Content_Types].xml',types);
    zip.file('_rels/.rels',rootRels);
    zip.file('xl/workbook.xml',workbook);
    zip.file('xl/_rels/workbook.xml.rels',wbRels);
    zip.file('xl/styles.xml',styles);
    zip.file('xl/worksheets/sheet1.xml',sheet1);
    zip.file('xl/worksheets/sheet2.xml',sheet2);
    return zip.generateAsync({type:'blob',mimeType:CT+'.sheet'});
  }
  document.getElementById('t-xlsx').addEventListener('click',function(){
    var b=this, txt=b.textContent;
    b.textContent='Gerando…'; b.disabled=true;
    buildXlsx(lastList).then(function(blob){
      return offerFile('cancelamentos-recorte.xlsx', blob, document.getElementById('t-hint'));
    }).catch(function(e){
      document.getElementById('t-hint').textContent='Não foi possível gerar a planilha neste ambiente.';
      if(window.console) console.error(e);
    }).then(function(){ b.textContent=txt; b.disabled=false; });
  });

  /* ================= textos fixos derivados do JSON (Painel/Relatorio/Slides) =================
     Preenchidos uma vez a partir de DADOS - nenhum numero abaixo foi digitado
     a mao, todos leem os campos do pipeline. */
  function preencherTextos(){
    var P=DADOS.painel, CP=DADOS.carta_p, G=DADOS.guardrails, A=DADOS.analyze, IMP=DADOS.improve, H4=DADOS.h4, HO=DADOS.holdout;
    var pct=function(v,d){return nf(v*100,d===undefined?2:d);};

    document.getElementById('hero-taxa').innerHTML=nf(P.taxa*100,2)+'<span>%</span>';
    var umEmCada=Math.round(1/P.taxa);
    document.getElementById('hero-meta-sim').innerHTML='Cerca de <b>1 a cada '+umEmCada+'</b> itens pedidos volta cancelado ou devolvido. A medição tem margem: entre <b class="mono">'+nf(P.ic95[0]*100,2)+'%</b> e <b class="mono">'+nf(P.ic95[1]*100,2)+'%</b>. Base: <b class="mono">'+nf(P.n,0)+'</b> itens ('+P.janela_label+').';
    document.getElementById('hero-meta-tec').innerHTML='IC 95% Wilson: <b class="mono">'+nf(P.ic95[0]*100,2)+'%</b>–<b class="mono">'+nf(P.ic95[1]*100,2)+'%</b> · n=<b class="mono">'+nf(P.n,0)+'</b> · <b class="mono">'+nf(P.dpmo,0)+'</b> DPMO · nível sigma <b class="mono">'+nf(P.sigma_deslocado,2)+'</b> ('+nf(P.sigma_longo_prazo,2)+' sem deslocamento de 1,5σ).';
    var gapSinal = P.gap_pp_janela_madura>=0?'+':'';
    document.getElementById('hero-gap').innerHTML='<span class="gap"><span class="mono" style="font-size:19px">'+gapSinal+nf(P.gap_pp_janela_madura,2)+' <span class="sim">ponto percentual</span><span class="tec">pp</span></span><span class="sim">acima da meta de '+nf(P.meta_interna_janela_madura*100,2)+'%</span><span class="tec">acima de '+nf(P.meta_interna_janela_madura*100,2)+'%</span></span>';
    var metaNaBorda = P.meta_interna_janela_madura <= P.ic95[0] + 0.0005; // [I1] meta dentro/na borda do IC do numero principal
    document.getElementById('hero-gap-meta-sim').innerHTML='A meta de '+nf(P.meta_interna_janela_madura*100,2)+'% não veio do mercado — é o melhor quartil mensal que o próprio negócio já teve, na mesma janela madura usada para o número principal. Não achamos benchmark de giftware no atacado.'
      +(metaNaBorda ? ' <b>E a diferença de '+nf(P.gap_pp_janela_madura,2)+' ponto percentual não é um fato sólido</b>: a meta cai bem na borda da margem de erro da taxa medida — estatisticamente, não dá para garantir que a taxa está mesmo acima da meta.'
                    : ' A diferença de '+nf(P.gap_pp_janela_madura,2)+' ponto percentual é pequena: a taxa geral está quase batendo a própria melhor meta.');
    document.getElementById('hero-gap-meta-tec').innerHTML='Meta interna: melhor quartil (P25) das taxas mensais, mesma janela madura do número principal (dez/2010–ago/2011). Sem benchmark de nicho B2B giftware citável (Gemba documental, Fase 0).'
      +(metaNaBorda ? ' <b>Meta ('+nf(P.meta_interna_janela_madura*100,2)+'%) coincide com o limite inferior do IC95%% da taxa medida ('+nf(P.ic95[0]*100,2)+'%%–'+nf(P.ic95[1]*100,2)+'%%)</b> — o gap de '+nf(P.gap_pp_janela_madura,2)+'pp não é estatisticamente distinguível de zero com esta margem.' : '');
    document.getElementById('hero-estorno').textContent='£ '+nf(P.receita_estornada,0);
    document.getElementById('hero-disclaimer').innerHTML='<span class="sim">O acompanhamento oficial deste projeto (congelado logo após a auditoria de qualidade, sobre os 10 meses inteiros da janela de exploração) mede <b class="mono">'+nf(P.baseline_congelado_10meses.taxa*100,2)+'%</b> — não usado neste bloco para não misturar duas bases sem aviso; o motivo está na seção 1 do Relatório.</span><span class="tec">Baseline congelado (Fase 2B, 10 meses, n='+nf(P.baseline_congelado_10meses.n,0)+'): <b class="mono">'+nf(P.baseline_congelado_10meses.taxa*100,2)+'%</b> (IC95% ['+nf(P.baseline_congelado_10meses.ic95[0]*100,2)+'%; '+nf(P.baseline_congelado_10meses.ic95[1]*100,2)+'%]) — não usado no bloco de hero/gap para não misturar janelas; ver Relatório seção 1.</span>';

    document.getElementById('g-receita').textContent='£ '+nf(G.receita_liquida,0);
    document.getElementById('g-pedidos').textContent=nf(G.pedidos,0);
    document.getElementById('g-clientes').textContent=nf(G.clientes_ativos,0);

    var sigmaZtxt=nf(CP.sigma_z,2);
    ['sigmaz-tec','cap-sigmaz','sigmaz-tec2','sigmaz-tec3'].forEach(function(id){
      var el=document.getElementById(id); if(el) el.textContent=sigmaZtxt;
    });

    var maiorTaxa=DADOS.pareto_taxa[0], maiorImpacto=DADOS.pareto_impacto[0];
    var rankMaiorTaxaEmImpacto = DADOS.pareto_comparacao.filter(function(r){return r.stockcode===maiorTaxa.stockcode;})[0];
    var rankMaiorImpactoEmTaxa = DADOS.pareto_comparacao.filter(function(r){return r.stockcode===maiorImpacto.stockcode;})[0];
    document.getElementById('pareto-compare-sim').innerHTML='O produto <b>'+esc(maiorTaxa.label)+'</b> tem a maior chance de voltar ('+nf(maiorTaxa.taxa,1)+'%) — mas fica só no <b>'+(rankMaiorTaxaEmImpacto?rankMaiorTaxaEmImpacto.rank_impacto+'º':'—')+' lugar</b> em prejuízo. O produto <b>'+esc(maiorImpacto.label)+'</b> é o que mais custa (£'+nf(maiorImpacto.es,0)+' devolvidos) — mas sua chance de voltar é só '+nf(maiorImpacto.taxa,2)+'% (<b>'+(rankMaiorImpactoEmTaxa?rankMaiorImpactoEmTaxa.rank_taxa+'º':'—')+' lugar</b> em risco). São os mesmos produtos, ordens diferentes.';
    document.getElementById('pareto-compare-tec').innerHTML='rank_taxa(1)='+esc(maiorTaxa.stockcode)+' → rank_impacto='+(rankMaiorTaxaEmImpacto?rankMaiorTaxaEmImpacto.rank_impacto:'—')+'. rank_impacto(1)='+esc(maiorImpacto.stockcode)+' → rank_taxa='+(rankMaiorImpactoEmTaxa?rankMaiorImpactoEmTaxa.rank_taxa:'—')+'. Correlação de ordem fraca entre os dois rankings (n≥50, mesmo grupo de produtos).';

    document.getElementById('r-taxa-sim').textContent=nf(P.taxa*100,2)+'%';

    // Relatorio: tabela de comparacao de ranking (secao 5)
    var tabHtml='<table><thead><tr><th>Produto</th><th style="text-align:right">Taxa</th><th style="text-align:right">Rank taxa</th><th style="text-align:right">Estornado</th><th style="text-align:right">Rank impacto</th></tr></thead><tbody>'+
      DADOS.pareto_comparacao.slice(0,12).map(function(r){
        return '<tr><td>'+esc(r.label)+'</td><td style="text-align:right" class="mono">'+nf(r.taxa,2)+'%</td><td style="text-align:right" class="mono">'+r.rank_taxa+'º</td><td style="text-align:right" class="mono">£'+nf(r.es,0)+'</td><td style="text-align:right" class="mono">'+r.rank_impacto+'º</td></tr>';
      }).join('')+'</tbody></table>';
    document.getElementById('tabela-pareto-compare').innerHTML=tabHtml;
    document.getElementById('pareto-narrativa-sim').innerHTML='O produto de maior risco proporcional ('+esc(maiorTaxa.label)+', '+nf(maiorTaxa.taxa,1)+'% de chance de voltar) é apenas o '+(rankMaiorTaxaEmImpacto?rankMaiorTaxaEmImpacto.rank_impacto:'—')+'º em prejuízo. O de maior prejuízo ('+esc(maiorImpacto.label)+', £'+nf(maiorImpacto.es,0)+') tem risco de só '+nf(maiorImpacto.taxa,2)+'%. As duas ordens discordam porque taxa mede risco proporcional e impacto mede volume × risco — um produto de venda baixa pode ter taxa alta sem doer no bolso, e um produto de venda alta dói mesmo com taxa baixa.';
    document.getElementById('pareto-narrativa-tec').innerHTML='Correlação de Spearman fraca entre rank_taxa e rank_impacto no conjunto de produtos com n≥50 (ver tabela acima) — divergência estrutural, não ruído amostral, dado o n de cada produto.';

    // Improve: conta central (corrigida em 2026-09-22, C2: abandono contado por
    // FATURA, nao por linha - receita preservada continua em linhas, como pedido
    // pela banca: "a receita total preservada, em soma, nao precisa mudar")
    var cen=IMP.cenarios.central, cons=IMP.cenarios.conservador;
    var linhasEvitadas = IMP.segmento_total_d*cen.f/100;
    var receitaPreservada = linhasEvitadas*IMP.receita_media_cancelada;
    var faturasAbandonadas = 0.02*IMP.faturas_legitimas;
    var receitaPerdida = faturasAbandonadas*IMP.receita_media_fatura_legit;
    document.getElementById('calc-central').innerHTML=
      'linhas nos 3 segmentos sinalizados (InvoiceNo×StockCode) '+nf(IMP.segmento_total_n,0)+'\n'+
      'faturas distintas (InvoiceNo) nesses mesmos segmentos ... '+nf(IMP.faturas_total,0)+'\n'+
      'cancelamentos observados (linhas) ........................ '+nf(IMP.segmento_total_d,0)+'\n'+
      'fração evitada pela verificação (premissa, central) ..... '+cen.f+'%\n'+
      'linhas evitadas (estimado) ............................... '+nf(linhasEvitadas,1)+'\n'+
      'receita média por linha cancelada nesses segmentos ...... £'+nf(IMP.receita_media_cancelada,2)+'\n'+
      'receita preservada (estimado, em linhas) ................. £'+nf(receitaPreservada,0)+'\n'+
      'faturas legítimas no segmento (sem nenhum cancelamento) . '+nf(IMP.faturas_legitimas,0)+' ('+nf(IMP.faturas_legitimas_pct,1)+'% das faturas)\n'+
      'receita média por fatura legítima ........................ £'+nf(IMP.receita_media_fatura_legit,2)+'\n'+
      'abandono de checkout assumido (premissa, por fatura) .... 2%\n'+
      'faturas abandonadas (estimado) ........................... '+nf(faturasAbandonadas,1)+'\n'+
      'receita perdida por abandono (estimado) .................. £'+nf(receitaPerdida,0)+'\n'+
      '<b>ganho líquido estimado (cenário central) ..................... £'+nf(cen.ganho,0)+'</b>\n'+
      '(cenário conservador, evita só '+cons.f+'%: ganho líquido = <b>£'+nf(cons.ganho,0)+'</b> — prejuízo)';

    document.getElementById('dash-janela-nota').innerHTML='<b>'+(simples()?'Isto cobre o ano inteiro, com o período de teste final incluído — por isso o número aqui é diferente do Painel.':'Cobertura: ano inteiro (dez/2010–dez/2011), incluindo o holdout.')+'</b> Os ~2,3 meses finais ficaram em quarentena durante a análise e só foram abertos ao final (ver Relatório, seção 14) — o Painel usa apenas a janela madura de exploração. Taxa do ano inteiro (referência do Dashboard): <b class="mono">'+nf(DADOS.dashboard.taxa_ano_inteiro,2)+'%</b>.';

    document.getElementById('slide3-p').innerHTML='<b>'+esc(maiorTaxa.label.split(' · ')[0])+'</b> tem a maior chance de voltar ('+nf(maiorTaxa.taxa,1)+'%) mas é só o '+(rankMaiorTaxaEmImpacto?rankMaiorTaxaEmImpacto.rank_impacto:'—')+'º em prejuízo. <b>'+esc(maiorImpacto.label.split(' · ')[0])+'</b> é o que mais custa mas tem risco de só '+nf(maiorImpacto.taxa,2)+'%.';
    document.getElementById('slide3-p-tec').innerHTML='rank_taxa(1)='+esc(maiorTaxa.stockcode)+'→rank_impacto='+(rankMaiorTaxaEmImpacto?rankMaiorTaxaEmImpacto.rank_impacto:'—')+'. rank_impacto(1)='+esc(maiorImpacto.stockcode)+'→rank_taxa='+(rankMaiorImpactoEmTaxa?rankMaiorImpactoEmTaxa.rank_taxa:'—')+'. n≥50 em ambos.';
  }

  /* ================= desenho geral ================= */
  function draw(){
    cartaPLaney(document.getElementById('chart-p'));
    barrasH(document.getElementById('chart-pa'),DADOS.pareto_taxa.map(function(r,i){return [r.label,r.taxa,'',i];}),{fmt:function(v){return nf(v,1)+'%';}});
    paretoAcum(document.getElementById('chart-pb'),DADOS.pareto_impacto.map(function(r){return [r.label,r.es];}));
    if(!document.getElementById('pane-relatorio').hidden){
      cartaPLaney(document.getElementById('rep-carta'));
      paretoAcum(document.getElementById('rep-pareto'),DADOS.pareto_impacto.map(function(r){return [r.label,r.es];}));
    }
    renderDash();
  }

  var modes=['painel','dashboard','relatorio','slides'];
  function setMode(m){
    modes.forEach(function(k){
      document.getElementById('pane-'+k).hidden=(k!==m);
      document.getElementById('m-'+k).setAttribute('aria-pressed',String(k===m));
    });
    try{ history.replaceState(null,'','#'+m); }catch(e){}
    hideTip(); draw();
  }
  modes.forEach(function(k){ document.getElementById('m-'+k).addEventListener('click',function(){ setMode(k); }); });
  function setReg(r){
    app.setAttribute('data-reg',r);
    document.getElementById('r-simples').setAttribute('aria-pressed',String(r==='simples'));
    document.getElementById('r-tecnica').setAttribute('aria-pressed',String(r==='tecnica'));
    draw();
  }
  document.getElementById('r-simples').addEventListener('click',function(){ setReg('simples'); });
  document.getElementById('r-tecnica').addEventListener('click',function(){ setReg('tecnica'); });

  preencherTextos();
  var initial=(location.hash||'').replace('#','');
  setMode(modes.indexOf(initial)>=0?initial:'painel');
  if(window.matchMedia){ var mq=window.matchMedia('(prefers-color-scheme: dark)'); if(mq.addEventListener) mq.addEventListener('change',draw); }
  window.addEventListener('scroll',hideTip,{passive:true});

  /* ================= slides ================= */
  var frames=Array.prototype.slice.call(document.querySelectorAll('.frame'));
  var cur=0, dots=document.getElementById('dots');
  frames.forEach(function(){ dots.appendChild(document.createElement('i')); });
  function show(i){
    cur=Math.max(0,Math.min(frames.length-1,i));
    frames.forEach(function(f,k){ f.classList.toggle('on',k===cur); });
    Array.prototype.forEach.call(dots.children,function(d,k){ d.classList.toggle('on',k===cur); });
    document.getElementById('prev').disabled=cur===0;
    document.getElementById('next').disabled=cur===frames.length-1;
  }
  document.getElementById('prev').addEventListener('click',function(){show(cur-1);});
  document.getElementById('next').addEventListener('click',function(){show(cur+1);});
  document.addEventListener('keydown',function(e){
    if(document.getElementById('pane-slides').hidden) return;
    if(e.key==='ArrowRight') show(cur+1);
    if(e.key==='ArrowLeft') show(cur-1);
  });
  show(0);

  /* ================= relatorio em PDF ================= */
  document.getElementById('print-rel').addEventListener('click',function(){
    var d=document.querySelector('#pane-relatorio details'); if(d) d.open=true;
    var st=document.createElement('style');
    st.textContent='@page{size:portrait; margin:16mm}';
    document.head.appendChild(st); window.print();
    setTimeout(function(){ if(st.parentNode) st.parentNode.removeChild(st); },800);
  });

  /* ================= .pptx ================= */
  var PAL={accent:'17476B',ink:'0E1618',ink2:'3B4B54',ink3:'6B7C86',rule:'AEBBC4'};
  function visText(f,q){
    var ns=f.querySelectorAll(q);
    for(var i=0;i<ns.length;i++){
      var cl=ns[i].className||'';
      if(simples() && /\btec\b/.test(cl)) continue;
      if(!simples() && /\bsim\b/.test(cl)) continue;
      return ns[i].textContent.trim();
    }
    return '';
  }
  function buildPptx(){
    var pptx=new window.PptxGenJS();
    pptx.layout='LAYOUT_16x9'; pptx.title='Cancelamentos e devoluções — Online Retail';
    frames.forEach(function(f,i){
      var sl=pptx.addSlide(); sl.background={color:'FFFFFF'};
      sl.addText(visText(f,'.eyebrow').toUpperCase(),{x:.62,y:.45,w:8.8,h:.28,fontFace:'Consolas',fontSize:11,bold:true,charSpacing:1.6,color:PAL.ink3});
      sl.addShape(pptx.ShapeType.line,{x:.62,y:.80,w:8.8,h:0,line:{color:PAL.rule,width:.75}});
      sl.addText(visText(f,'h2'),{x:.62,y:1.00,w:8.5,h:1.45,fontFace:'Georgia',fontSize:24,bold:true,color:PAL.ink,valign:'top',lineSpacingMultiple:1.05});
      var stat=f.querySelector('.fstat'), yB=2.62;
      if(stat){ sl.addText(stat.textContent.trim(),{x:.62,y:2.48,w:8.5,h:.95,fontFace:'Georgia',fontSize:38,bold:true,color:PAL.accent}); yB=3.50; }
      sl.addText(visText(f,'p'),{x:.62,y:yB,w:8.2,h:1.6,fontFace:'Calibri',fontSize:13,color:PAL.ink2,valign:'top',lineSpacingMultiple:1.25});
      sl.addText((i+1)+' / '+frames.length,{x:8.3,y:5.05,w:1.1,h:.3,fontFace:'Consolas',fontSize:10,color:PAL.ink3,align:'right'});
    });
    return pptx.write({outputType:'blob'}).then(function(blob){
      return offerFile('cancelamentos-online-retail.pptx', blob, document.getElementById('pptx-hint'));
    });
  }
  var btn=document.getElementById('dl-pptx');
  if(typeof window.PptxGenJS==='undefined'){
    btn.disabled=true; btn.style.opacity='.4'; btn.style.cursor='default';
    document.getElementById('pptx-hint').innerHTML='A biblioteca de geração de <b>.pptx</b> não carregou.';
  } else {
    btn.addEventListener('click',function(){
      var t=btn.textContent; btn.textContent='Gerando…'; btn.disabled=true;
      Promise.resolve().then(buildPptx).catch(function(e){
        document.getElementById('pptx-hint').textContent='Não foi possível gerar o arquivo neste ambiente. Abra a página publicada ou o arquivo direto do disco.';
        if(window.console) console.error(e);
      }).then(function(){ btn.textContent=t; btn.disabled=false; });
    });
  }
})();
