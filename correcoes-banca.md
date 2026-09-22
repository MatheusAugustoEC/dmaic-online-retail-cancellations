# Correções da banca — registro

## Rodada 3 (2026-09-22)

Parecer V3: aprovado com ressalvas — nenhum achado muda número, conclusão ou decisão; todos são de interface/legibilidade. Reconferidos do zero os números críticos das rodadas anteriores (6.902 faturas, 66 produtos, £6.761 etc.), sem leftover. Confirmado por diff que `docs/entrega_dados.json` e `src/fase6_dados_entrega.py` não foram tocados nesta rodada — só `docs/app.js` e `docs/index.html`.

### [V2] Zoom "não funciona" no gráfico de bolhas do Dashboard — investigado, não reproduzido com o gráfico em vista

- **Achado da banca:** arrastar sobre o gráfico de dispersão só selecionava texto da página, e Ctrl+roda não mudava nada — ao contrário da carta de controle, onde a mesma interação funcionava.
- **Investigação:** medi a posição do gráfico na carga inicial da página: o `#d-scatter` fica em `y≈3413px`, bem abaixo da janela visível de 900px de altura (o Dashboard empilha vários gráficos acima dele), enquanto a carta de controle do Painel fica em `y≈490px`, dentro da janela inicial. Uma automação que calcula a posição do elemento sem antes rolar até ele tenta arrastar/rodar fora da área visível do navegador, caindo fora do SVG — o que reproduz exatamente os sintomas relatados. Repeti o teste rolando até o gráfico primeiro (como qualquer usuário real faria antes de arrastar algo que não está vendo): o zoom funciona normalmente — arrastar amplia, "Ver tudo" aparece, Ctrl+roda funciona, sobreposição limpa em claro/escuro/Simples/Técnica.
- **Correção aplicada (defensiva, a pedido, sem bug confirmado):** adicionado `user-select:none` a todo `<svg>` da página (`docs/index.html`), para que nenhum arrasto sobre ou perto de um gráfico jamais dispare seleção nativa de texto, mesmo em cenários de borda.

### [V1] Células "n insuf."/"n<50" difíceis de escanear na matriz do Dashboard

- **Antes:** células sem dado suficiente (n<50) mostravam o texto por extenso "n insuf." (Simples) ou "n<50" (Técnico) dentro da célula, bem mais longo que os números de 3-4 caracteres das outras células.
- **Depois:** o texto foi trocado por um traço curto "—", mantendo a borda tracejada e a cor neutra já usadas para marcar essas células, e mantendo a explicação completa ("poucos itens (não colorida)" / "n<50 (não colorida)") na legenda abaixo da matriz e o "n" exato no tooltip ao passar o mouse.

### [V3] Cartão "n/d" do Painel sem destaque visual

- **Antes:** o cartão "Abandono no checkout" mostrava "n/d" com o mesmo peso visual dos três cartões vizinhos com números reais; a explicação só aparecia num parágrafo abaixo da linha de cartões.
- **Depois:** o valor "n/d" ganhou estilo visualmente distinto (cor acinzentada, itálico) e a nota logo abaixo do cartão passou a dizer diretamente "não medido por desenho — ver Relatório, seção 11", em vez de "não mensurável com este dado".

### [V4] Cartão "+0,00" do Dashboard sem contexto

- **Antes:** o cartão "Diferença da média" mostrava "+0,00 pontos percentuais" no estado padrão (sem filtro), sem nenhuma explicação de por que era zero.
- **Depois:** quando nenhum filtro está ativo, a legenda do cartão passa a dizer "sem filtro, é sempre 0,00" (Simples) / "sem filtro vs. si mesma = 0" (Técnico); assim que qualquer filtro é aplicado, a legenda volta ao texto normal ("pontos percentuais").

### [V5] Linha "Erro de separação" do plano de controle sem indicar que o limite está pendente

- **Antes:** a linha "Erro de separação em pedido grande do Reino Unido" mostrava "a definir (sem dado de linha-base)" com a mesma formatação das linhas que já têm limite definido.
- **Depois:** adicionada uma etiqueta "PENDENTE" (cor de alerta, mesma usada em outros avisos da página) ao lado do texto "a definir", só nessa linha, para sinalizar visualmente que o limite ainda não tem dado real por trás.

## Rodada 2 (2026-09-22)

Três ajustes pontuais de apresentação/interação, sem alteração de nenhum número de análise. Confirmado por diff: `docs/entrega_dados.json` e `src/fase6_dados_entrega.py` não foram tocados; só `docs/app.js` (lógica de renderização/interação) e `docs/index.html` (CSS e um trecho de texto) mudaram.

### [M1] Rótulo "limite do normal" encostava na linha do limite

- **Antes:** o rótulo era posicionado dinamicamente perto do ponto de menor UCL da série, com âncora de texto ajustada conforme a curva — em certas larguras de tela ficava espremido perto da borda direita e tocava a linha tracejada do limite.
- **Depois:** a carta de controle (Painel e Relatório, cartaPLaney em `docs/app.js`) ganhou uma margem direita fixa reservada (nenhuma grade ou dado é desenhado ali) onde o rótulo do limite fica sempre numa posição vertical fixa (meio do eixo Y), independente do formato da curva ou do zoom aplicado. Testado em claro, escuro, desktop e mobile, nos dois registros (Simples: "limite" / "do normal"; Técnica: "UCL/LCL" / "(Laney)") — a checagem `sobreposicao.js` não acusa nada em nenhuma combinação.

### [M2] "poka-yoke" ainda aparecia duas vezes no Relatório, modo Simples

- **Antes:** em "Onde o dinheiro se perde" (Relatório, modo Simples), o texto dizia "...uma conferência extra na separação (poka-yoke)..." e "...priorizar a lista de produtos do poka-yoke".
- **Depois:** as duas ocorrências foram trocadas por "conferência dupla" no modo Simples ("...uma conferência extra na separação (conferência dupla)..." e "...priorizar a lista de produtos da conferência dupla"). O modo Técnico mantém "poka-yoke" sem alteração. Confirmado por varredura de texto em todos os 4 modos com o registro Simples ativo: nenhuma ocorrência de "poka-yoke" restante.

### [ZOOM] Zoom na carta de controle e no gráfico de bolhas

- **Antes:** nenhum dos dois gráficos tinha zoom; a carta de controle e o gráfico de bolhas do Dashboard eram estáticos, com todo o período/todas as bolhas sempre visíveis numa única escala.
- **Depois:** implementado o padrão de zoom da regra 18 (`interacao.md`), adaptado do molde de referência (`zoomavel()`, `zoomBar()`, estado `ZOOM`) para `docs/app.js`:
  - Carta de controle (semanal, Painel e Relatório): zoom só no eixo do tempo — os limites (UCL/LCL) continuam calculados sobre o período inteiro, só a janela de datas exibida muda; o rótulo do limite (M1) permanece fixo na margem, independente do zoom.
  - Gráfico de bolhas (Dashboard): zoom nos dois eixos, com os rótulos de produto recalculados a cada zoom (bolha maior escolhe posição primeiro; rótulo que não couber fica só no balão via hover). A margem esquerda do eixo vertical também foi alargada para as bolhas não encostarem mais nos rótulos de porcentagem (2,4% / 4,9% / 7,3%).
  - Interação: arrastar sobre a área do gráfico amplia; Ctrl + roda do mouse aproxima/afasta; duplo clique ou o botão "Ver tudo" (só aparece com zoom ativo) restaura a visão completa; dica discreta abaixo do gráfico nos dois registros. A roda sozinha (sem Ctrl) continua rolando a página normalmente. No celular (`pointer: coarse`), o arrasto de zoom é desabilitado — só a pinça nativa do navegador funciona — e a dica de zoom fica oculta.
  - Um arrasto sobre uma bolha não aplica filtro (só zoom); um clique simples (sem arrastar) continua filtrando normalmente, via guarda `_arrastou`.
  - Verificado com Playwright: zoom por arrasto funciona nos dois gráficos; "Ver tudo" e duplo clique resetam; Ctrl+roda amplia sem rolar a página (confirmado com o elemento devidamente scrollado à vista — `scrollY` inalterado antes/depois); roda sozinha rola a página normalmente; arrasto no scatter não filtra, clique simples filtra; contexto touch confirma arrasto desabilitado e dica oculta. Varredura completa de `sobreposicao.js` (52 combinações: 32 sem zoom × 4 modos × 2 temas × 2 telas × 2 registros, 8 com a carta zoomada, 4 com o scatter zoomado, 8 em mobile) — 100% limpa, zero sobreposição, zero erro de console.
