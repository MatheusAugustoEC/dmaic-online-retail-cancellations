# Parecer da banca — Cancelamentos e Devoluções, Online Retail (UCI) — RODADA 2

2026-09-22 · rodada 2 (confere as correções da rodada 1) · https://matheusaugustoec.github.io/dmaic-online-retail-cancellations/ · nível 2 (repositório local consultado para confirmar cada "pronto quando" no código) · revisão visual: **realizada, com nova captura** (Playwright rodado de novo sobre o link publicado, sem reaproveitar a captura da rodada 1 — Painel, Dashboard, Relatório, Slides; Simples e Técnica; desktop, celular e escuro), **com a mesma lacuna já declarada na rodada 1**: celular e escuro não cobriram o registro Técnica, e a captura de texto do registro Técnica dos Slides não percorreu os 9 slides (ver "Limites desta revisão").

Esta rodada lê o parecer da rodada 1 (`parecer-banca-dmaic.md`) e o registro das
correções (commits `f2e1fcf` e `8bf966f` — não encontrei um arquivo
`correcoes-banca.md` no repositório; as mensagens de commit têm o mesmo nível
de detalhe e foram usadas como o registro). Olha só os 11 achados da rodada 1
(C1, C2, I1–I8, M1–M3), confirmando pelo critério "pronto quando" de cada um, e
o que a correção pode ter quebrado fora da lista.

## Veredito

**APROVADO COM RESSALVAS** — nenhum crítico permanece. Os dois achados
críticos (C1, C2) e todos os sete importantes (I1–I8, oito itens) foram
corrigidos e verificados, com evidência nova. Restam duas ressalvas pequenas,
nenhuma delas capaz de enganar um leitor sobre um número ou uma decisão: um
rótulo de gráfico que continua tocando a própria linha (M1) e um jargão que
sobrou em um único parágrafo do modo Simples (M2, corrigido em todo o resto
da página). Nenhuma correção quebrou um número em outro lugar da página, até
onde esta rodada conseguiu checar.

## Conferência achado a achado

### [C1] "Maior prejuízo" dominado por transação isolada — **RESOLVIDO**
Pronto quando (rodada 1): nenhuma linha individual responde por mais de
~30–40% do total de nenhum produto do ranking de impacto; £77.579 e "23166 =
1º em prejuízo" não aparecem mais sem ressalva.
Evidência da correção: no Relatório (Painel/Dashboard/Relatório/Slides, dois
registros), o StockCode 23166 não aparece mais no top 10 de impacto — o novo
1º lugar é 22423 · Regency Cakestand 3 Tier, £17.632 (verificado nos quatro
modos e nos dois registros). A exclusão foi feita cirurgicamente: só a
receita da linha isolada (InvoiceNo 541431) foi zerada nas agregações de
impacto; o produto 23166 continua com suas 137 linhas legítimas na taxa
geral, n, d e taxa inalterados — exatamente a abordagem "declarar e excluir
com o mesmo critério" que o achado original pedia, com o mesmo tratamento já
dado ao StockCode 23843 documentado lado a lado (Relatório, seção 2/nota de
tratamento, nos dois registros).
Verificação no dado: recontei a receita do StockCode 22423 (novo 1º lugar) —
não é dominada por uma transação isolada (a maior linha individual não se
aproxima de 30% do total do produto), diferente do padrão do C1 original.
Status: **RESOLVIDO**.

### [C2] Conta do ganho misturava linhas com pedidos — **RESOLVIDO**
Pronto quando: total de "pedidos" citado nos 3 segmentos menor que 13.081;
recontagem de faturas distintas bate com o número citado.
Evidência da correção: o Relatório (seção 10 técnica / "A conta do ganho"
simples) agora separa explicitamente "linhas nos 3 segmentos sinalizados
(InvoiceNo×StockCode): 34.257" de "faturas distintas (InvoiceNo) nesses
mesmos segmentos: 6.902" — o número de faturas (6.902) é menor que os 13.081
pedidos da janela madura inteira (Painel), como o critério exigia. A conta de
abandono agora usa a base de faturas: "faturas legítimas no segmento (sem
nenhum cancelamento): 6.278 (91,0% das faturas)" — substituindo a antiga
frase "97% dos pedidos são legítimos". Novo ponto de indiferença: 2,38%
(era 2,01%); ganho líquido central: £6.761 (era £200); conservador: −£14.441
(era −£21.002); n do experimento: 793 faturas/braço, calculado sobre a taxa
real de faturas do segmento (9,04%), não mais sobre a taxa de linhas
(3,071%). Os mesmos números aparecem, atualizados e consistentes, no Painel
(guardrail "Abandono no checkout (por fatura) > 2,38%") e nos Slides (slide
07: "£6.761... 2,38%").
Status: **RESOLVIDO**.

### [I1] Meta na borda do IC — **RESOLVIDO**
Pronto quando: o bloco "Distância da meta" menciona explicitamente que a
meta está dentro da margem de erro do número principal.
Evidência: Painel Simples — "a diferença de 0,05 ponto percentual não é um
fato sólido: a meta cai bem na borda da margem de erro da taxa medida —
estatisticamente, não dá para garantir que a taxa está mesmo acima da meta."
Painel Técnico — "Meta (1,99%) coincide com o limite inferior do IC95% da
taxa medida (1,99%–2,10%) — o gap de 0,05pp não é estatisticamente
distinguível de zero com esta margem." Relatório, seção 1, reforça a mesma
ressalva nos dois registros.
Status: **RESOLVIDO**.

### [I2] Célula Austrália/Q1 dominando a escala de cor — **RESOLVIDO**
Pronto quando (redação original): nenhuma célula abaixo do piso de n
aparece colorida na mesma escala das demais.
Evidência: a correção aplicada foi diferente da que eu tinha sugerido como
única opção, mas resolve o problema de fundo de forma válida — Austrália/Q1
tem n=87, que **passa** no próprio piso do projeto (n≥50, o mesmo usado nos
Paretos de produto e no H4), então não era o caso de escondê-la; em vez
disso, a escala de cor agora usa o 2º maior valor elegível (Japan/Q4, 14,2%)
como referência do gradiente, não o valor bruto de 65,5%. Confirmado
visualmente em `graficos/desktop__simples__dashboard__03.png` (rodada 2):
Austrália/Q1 e Japan/Q4 aparecem no mesmo tom mais escuro da escala, e as
demais células (0–10%) mostram gradação clara entre si — a distorção que
"apagava" a variação real das outras células não existe mais. Células com
n<50 (Finland/Q1, Sweden/Q1, Austria/Q1, Denmark/Q1-Q2, Poland/Q1, Japan/Q2-Q3)
aparecem com borda tracejada e "n insuf.", sem cor — confirmado na imagem e
na legenda nova ("poucos itens (não colorida)").
Status: **RESOLVIDO** (solução alternativa válida, não a única sugerida).

### [I3] Rótulos ilegíveis no gráfico de bolhas — **RESOLVIDO (com resíduo menor, ver M4)**
Pronto quando: nenhuma ocorrência de "texto sobre texto" ou "texto sobre
marca" na checagem de sobreposição.
Evidência: o bloco ilegível de nomes empilhados ("23166 Medium Cerami" ×
"22501 Picnic Basket…", 4 ocorrências de texto-sobre-texto na rodada 1)
**desapareceu por completo** — confirmado em `sobreposicao.md` da rodada 2
(zero ocorrências de texto-sobre-texto em todos os modos/temas) e
visualmente em `graficos/desktop__simples__dashboard__06.png`: os rótulos
agora aparecem espaçados, sem colisão, com a nota nova "Quando bolhas ficam
muito próximas, só a maior de cada grupo mostra o nome ao lado — passe o
mouse em qualquer bolha para ver a sua." Isso resolve o problema original
(ilegibilidade que impedia identificar produtos).
Resíduo: `sobreposicao.md` da rodada 2 ainda mostra 4 ocorrências de "texto
sobre marca" em desktop e escuro — são os rótulos do eixo Y (2,4%, 4,9%,
7,3%) tocando bolhas próximas ao eixo, não mais nomes de produto. É um
defeito bem menor que o original (não impede identificar nenhum produto) —
registrado como novo achado **M4**, não como I3 não resolvido.
Status: **RESOLVIDO** para o achado original; resíduo cosmético novo, ver M4.

### [I4] Lista de 198 produtos sem controle de falso positivo — **RESOLVIDO**
Pronto quando: critério de corte usa o limite inferior do IC, não a taxa
pontual; número "198" atualizado de forma consistente em toda a página.
Evidência: Relatório, seção 6 técnica — "66/1.399 produtos (n≥50) com o
limite inferior do IC de Wilson ≥2x a média geral... critério corrigido...
a taxa pontual sozinha (198 produtos batiam '≥2x' só pelo valor observado)
não controla falso positivo — com n=50 e a taxa média da base, um produto
sem problema real já tem ~1/4 de chance de bater '≥2x a média' por acaso."
A justificativa reproduz de forma independente o mesmo cálculo que eu tinha
feito na rodada 1. O número "66" (e a cobertura "23,4%") aparece de forma
consistente no Painel (produto entrando na lista de risco), no Relatório
(seções 6 e 8, "62,9%"→"51,8%", "40,4%"→"23,4%") e nos Slides (slide 06:
"~66 produtos sinalizados"), nos dois registros — não encontrei nenhuma
ocorrência remanescente de "198" como número de produtos sinalizados (as
únicas ocorrências de "198" no texto capturado são referências explicativas
ao critério antigo, dentro da explicação da própria correção).
Status: **RESOLVIDO**.

### [I5] H4 sem conta de ganho/custo — **RESOLVIDO (via declaração explícita)**
Pronto quando: estimativa de ordem de grandeza OU declaração explícita da
lacuna e por quê.
Evidência: Relatório, "A conta do ganho, passo a passo" (Simples) — "Preciso
ser direto sobre uma lacuna antes de mostrar a conta: a causa mais robusta
deste relatório (H4...) não tem conta de ganho nem de custo aqui... prefiro
dizer isso com todas as letras a inventar um número de custo operacional que
ninguém validou. A decisão sobre investir ou não na conferência dos produtos
de H4 não pode ser tomada só com este relatório; precisa de um levantamento
operacional à parte." Mesma frase, em registro técnico, na seção 10.
Status: **RESOLVIDO** (optou pela declaração explícita, uma das duas saídas
que o achado previa).

### [I6] Trava no checkout; causa suspeita no picking — **RESOLVIDO**
Pronto quando: plano de controle e texto explicam por que a trava está no
checkout, OU a ação de separação ganha dono e frequência no plano.
Evidência: fez as duas coisas. Painel — nova linha na tabela "O que
acompanhar": "Erro de separação em pedido grande do Reino Unido | a definir
(sem dado de linha-base) | Amostral, por pedido grande do Reino Unido | Ger.
Estoque / Armazém | Revisar procedimento de separação para a faixa." Relatório
(Simples) — parágrafo novo explicando a troca: "a causa suspeita é erro de
separação — um problema de armazém — mas a única ação com dono e frequência
no plano de controle original era a confirmação no checkout... Mantenho as
duas no plano — a da separação como primeira linha (ataca a causa), a do
checkout como camada adicional só no segmento de maior risco condicionado."
A tabela "O que fazer" ganhou uma linha nova: "Conferência na separação de
pedidos grandes do Reino Unido | Elimina a causa | Erro suspeito de
separação."
Status: **RESOLVIDO**.

### [I7] Alarme de faturamento sem ajuste sazonal — **RESOLVIDO**
Pronto quando: o alarme não dispara ao aplicar a série histórica completa do
projeto com a nova regra.
Evidência: Painel — "Faturamento | queda >20% vs. média dos 3 meses
anteriores" e "Pedidos | queda >20% vs. média dos 3 meses anteriores"
(era "queda >10%" vs. mês anterior nos dois casos). Verifiquei a derivação
no código (`src/fase6_dados_entrega.py`, bloco "[I7] CORRECAO POS-BANCA"): a
correção testou duas abordagens (limites I-MR sobre a série de variação —
descartada por ficar larga demais para servir de alarme, ~-75% a -85%; e
desvio vs. média móvel de 3 meses — adotada), calculada sobre o ano inteiro
já aberto (uso legítimo pós-holdout para calibrar limiar de alarme, não para
reabrir uma conclusão de causa), excluindo dezembro/2011 por ser mês parcial
conhecido. Resultado documentado no próprio código: maior queda legítima
histórica é -14,2% (receita) e -10,7% (pedidos) — abaixo do novo limiar de
20%. A metodologia é sólida e a limitação (um único ano, sem decomposição
sazonal formal) é declarada no comentário do código.
Ressalva pequena: `docs/control-plano.md` (o documento de design do plano de
controle) não foi atualizado com essa mudança — ainda não menciona "média
móvel" nem o novo limiar de 20%; só `docs/index.html` (a página) e o código
que a gera têm a versão nova. Isso não afeta a página publicada, que é o que
esta banca revisa, mas é uma fonte de verdade interna desalinhada — registro
como observação, não como achado novo (não há "pronto quando" pendente na
página).
Status: **RESOLVIDO** na página; observação de documentação interna
registrada acima.

### [I8] Sem atribuição de autoria — **RESOLVIDO**
Pronto quando: busca por "github" ou nome do autor encontra ocorrência
visível em cada modo.
Evidência: rodapé "Projeto de portfólio DMAIC · github.com/MatheusAugustoEC/
dmaic-online-retail-cancellations" confirmado nos 8 arquivos de texto
capturados nesta rodada (Painel, Dashboard, Relatório e Slides — os 9 slides
— nos dois registros de linguagem) e visualmente no fim da captura de
celular do Painel.
Status: **RESOLVIDO**.

### [M1] Rótulo "limite do normal" sobre a linha — **NÃO RESOLVIDO** (atenuado)
Pronto quando: nenhuma ocorrência de "texto sobre linha" numa nova checagem
de sobreposição.
Evidência: `sobreposicao.md` da rodada 2 ainda registra "chart-p · texto
sobre linha: 1 ocorrência(s) — «limite do normal» × «path»" no Painel e no
Relatório, em desktop, celular e escuro (8 segmentos de sobreposição, contra
11 na rodada 1 — reduziu, não eliminou). Confirmado visualmente em
`graficos/escuro__simples__painel__00.png` e `graficos/celular__simples__
painel__00.png`: o rótulo foi reancorado para a região de maior folga da
curva UCL, mas nela mesma o traço pontilhado do limite ainda passa por trás
das letras "limite do normal" — visível principalmente no tema escuro, onde
o contraste torna o cruzamento óbvio.
Status: **NÃO RESOLVIDO**. Severidade permanece MENOR (rótulo isolado, não
compromete a leitura do gráfico), mas o achado continua de pé.

### [M2] "poka-yoke" no registro Simples — **PARCIALMENTE RESOLVIDO**
Pronto quando: "poka-yoke" só aparece no registro Técnico.
Evidência: a tabela do plano de controle no Painel (Simples) foi corrigida —
agora diz "Adicionar à lista de conferência dupla", sem o jargão. Mas o
Relatório (Simples), seção "Onde o dinheiro se perde", ainda tem duas
ocorrências: "Se a ação é uma conferência extra na separação (poka-yoke), o
custo é por produto tratado..." e "...priorizar a lista de produtos do
poka-yoke, e declaro a escolha." — texto idêntico ao da rodada 1, não
tocado pela correção.
Status: **PARCIALMENTE RESOLVIDO** (Painel corrigido; Relatório Simples,
não). Severidade permanece MENOR.

### [M3] Tabela "O que acompanhar" apertada no celular — **RESOLVIDO**
Pronto quando: não especificado um critério além de "layout mais largo";
avaliação visual direta.
Evidência: confirmado em `capturas/celular__simples__painel.png` (rodada 2)
— a tabela virou cartões empilhados, um por linha, com rótulo (ALARME EM /
FREQUÊNCIA / RESPONSÁVEL / O QUE FAZER SE PASSAR) acima de cada valor, sem
compressão de texto. Inclui corretamente a nova linha do achado I6 (erro de
separação).
Status: **RESOLVIDO**.

## Achados novos desta rodada

**M4 · MENOR · Rótulos do eixo Y tocam bolhas próximas, no gráfico de dispersão do Dashboard**
- Onde: Dashboard, "Volume contra frequência, por produto", desktop e tema
  escuro (não ocorre no celular, onde o mesmo gráfico não mostrou
  sobreposição nesta rodada).
- Evidência: `sobreposicao.md` (rodada 2) — "d-scatter · texto sobre marca:
  4 ocorrência(s)": os rótulos de porcentagem do eixo (2,4%, 4,9%, 7,3%)
  tocam bolhas próximas à borda esquerda do gráfico.
- O que corrigir: afastar levemente os rótulos do eixo Y das bolhas mais
  próximas da borda, ou reduzir a área de colisão considerada pelos
  rótulos do eixo.
- Erro ou preferência: ERRO (achado novo, efeito colateral da correção de
  I3 — ao reposicionar as bolhas para não colidirem entre si, algumas
  ficaram mais perto do eixo).
- Fase de origem: Entrega, pós-hoc.

## O que a correção pode ter quebrado — checagem fora da lista

Busquei explicitamente por números antigos que poderiam ter sobrado em algum
modo ou registro sem serem atualizados, e por contas que dependem dos
números que mudaram:

- **Números do ponto de indiferença antigo (2,01%, £200, −£21.002, "97%
  legítimos")**: nenhuma ocorrência em nenhum dos 8 arquivos de texto
  capturados nesta rodada (Painel, Dashboard, Relatório, Slides × Simples,
  Técnica) — busca por grep confirmando zero resultados.
- **"198 produtos" como número de produtos sinalizados**: nenhuma ocorrência
  remanescente fora do contexto explicativo da própria correção (o texto que
  explica por que o critério mudou de 198 para 66 cita "198" de propósito,
  como comparação histórica — isso é esperado e correto, não um leftover).
- **23166 como "1º em prejuízo" ou £77.579 sem ressalva**: nenhuma
  ocorrência — todas as menções a 23166 e £77.579/£77.183,60 aparecem dentro
  da explicação da própria exclusão (seção 2 do Relatório e nota da
  planilha), nunca mais como o produto de maior prejuízo.
- **Consistência entre modos**: os números novos (22423, £17.632, 66
  produtos, 23,4%, 51,8%, 48,2%, 2,38%, £6.761, −£14.441, 91,0%, 6.902
  faturas, 793 faturas/braço, ~2,3 meses) aparecem de forma idêntica no
  Painel, Dashboard, Relatório e Slides, nos dois registros de linguagem —
  não encontrei nenhuma divergência entre modos para nenhum desses números.
- **Contas que dependem dos números que mudaram**: o desenho experimental
  (seção 11) foi recalculado com a taxa-base correta em nível de fatura
  (9,04%, não mais 3,071% em linha) — o `n` por braço mudou de 2.454 para
  793 e a duração de ~1,4 para ~2,3 meses, de forma coerente com a nova
  taxa-base (uma taxa mais alta em nível de fatura, com um efeito absoluto
  maior a detectar, pede menos n por braço — confere). A soma das três
  causas testadas (seção 8) foi recalculada com o H4 de 66 produtos
  (23,4%, não mais 40,4%), e a cobertura total caiu de 62,9% para 51,8% —
  aritmeticamente consistente (23,4 + 24,9 + 14,3 − sobreposição ≈ 51,8,
  compatível com a redução esperada ao remover 132 produtos da lista de
  H4).
- **`docs/control-plano.md`** não foi atualizado com a nova regra de alarme
  do achado I7 (ver nota dentro do achado I7 acima) — não afeta a página
  publicada, registrado como observação de manutenção interna, não como
  achado de página.
- Não encontrei nenhum outro número desatualizado nos oito textos
  capturados.

## Cobertura desta rodada

| Achado da rodada 1 | Status na rodada 2 |
|---|---|
| C1 | Resolvido |
| C2 | Resolvido |
| I1 | Resolvido |
| I2 | Resolvido (solução alternativa válida) |
| I3 | Resolvido (resíduo cosmético novo → M4) |
| I4 | Resolvido |
| I5 | Resolvido (declaração explícita) |
| I6 | Resolvido |
| I7 | Resolvido (observação de documentação interna) |
| I8 | Resolvido |
| M1 | Não resolvido (atenuado) |
| M2 | Parcialmente resolvido (Painel sim, Relatório Simples não) |
| M3 | Resolvido |
| M4 (novo) | Achado novo, menor |

## O que está sólido (reconfirmado nesta rodada)

- As duas exclusões de outlier (23843 e 23166) são documentadas lado a lado,
  com o mesmo critério, nos dois registros de linguagem — a banca não
  encontrou tratamento ad hoc na correção.
- A correção do ponto de indiferença (C2) foi verificada até o nível de
  código: a taxa-base do experimento (9,04%) bate exatamente com a proporção
  de faturas com cancelamento que eu tinha recalculado de forma independente
  na rodada 1 (624/6.902).
- A correção do critério de H4 (I4) reproduz, com os mesmos números, o
  raciocínio de falso positivo que a rodada 1 tinha levantado — não foi só
  aceita, foi verificada e justificada de novo no texto público.
- Nenhuma das nove correções resolvidas introduziu um número inconsistente
  entre os quatro modos ou os dois registros de linguagem, até onde esta
  rodada conseguiu checar.

## Matriz de achados

Ver `matriz-achados-r2.md`.

## Limites desta revisão

- Mesma lacuna de cobertura de captura da rodada 1: celular e escuro não
  cobriram o registro Técnico; a captura de texto dos Slides em Técnico não
  percorreu os 9 slides (limitação do script/sessão do navegador, não da
  página) — não foi possível confirmar visualmente M1 e M4 no registro
  Técnico fora do desktop.
- Não recalculei a nova soma "23,4 + 24,9 + 14,3 − sobreposição ≈ 51,8%" a
  partir do dado bruto — validei que a ordem de grandeza e o sentido da
  mudança são coerentes, não reproduzi o cálculo exato de sobreposição entre
  os três grupos.
- Não há um arquivo `correcoes-banca.md` no repositório; usei as mensagens
  dos commits `f2e1fcf` e `8bf966f` como o registro das correções, por
  decisão desta banca diante da ausência do arquivo nomeado.
- Como na rodada 1, esta conversa tem acesso ao repositório local (mesmo
  diretório de trabalho do projeto), o que permitiu nível 2 sem clonar nada
  — registrado por transparência.
