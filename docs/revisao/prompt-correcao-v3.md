# CORREÇÕES DA BANCA — V3 — Cancelamentos e Devoluções, Online Retail (UCI)

Uma banca de revisores independentes revisou o arquivo local da página
(`docs/index.html`, capturado em 2026-09-22, depois das correções M1/M2 e da
adição do zoom nos gráficos). Nenhum achado desta rodada muda um número, uma
conclusão ou uma decisão do projeto — são todos de interface, legibilidade
ou apresentação. Faça um por vez, na ordem abaixo (a primeira é a mais
visível para quem usa o projeto interativamente).

Se eu tiver apagado algum bloco, é porque decidi não corrigir aquele ponto —
não o reintroduza.

## Regras
- Nenhuma correção abaixo deveria mudar um número da análise.
- Teste em desktop, celular e tema escuro, nos dois registros de linguagem
  (Simples e Técnica), depois de cada correção.
- Ao terminar: rode de novo a captura de tela e a checagem de sobreposição,
  e me diga, em uma linha por ID, o que mudou.

---

## [V2] Zoom não funciona no gráfico de dispersão do Dashboard
Crítica: o gráfico "Volume contra frequência, por produto" (Dashboard) tem
uma legenda dizendo "Arraste sobre o gráfico para ampliar · Ctrl + roda do
mouse aproxima e afasta" — mas nenhuma das duas interações funciona.
Arrastar sobre a área do gráfico só seleciona o texto da página (como se
você tivesse arrastado sobre um parágrafo), e Ctrl+roda não muda nada nos
eixos. A mesma interação funciona corretamente na carta de controle do
Painel (arrastar restringe o eixo de datas e faz aparecer um botão "Ver
tudo").
Onde: Dashboard, gráfico "Volume contra frequência, por produto", nos dois
registros de linguagem (a legenda de instrução aparece embaixo do gráfico,
com texto ligeiramente diferente em Simples e em Técnico, mas o problema é
o mesmo nos dois).
O que fazer:
  1. Localizar o componente do gráfico de dispersão (bolhas) e comparar com
     a implementação de zoom da carta de controle do Painel (que funciona
     corretamente) — verificar se o mecanismo de arraste/Ctrl+roda está de
     fato conectado ao gráfico de dispersão ou se ficou só na legenda de
     texto.
  2. Implementar o zoom no gráfico de dispersão com o mesmo comportamento da
     carta de controle: arrastar restringe os eixos à área selecionada;
     Ctrl+roda aproxima/afasta; duplo clique ou um botão "Ver tudo" reseta
     a visão.
  3. Se a decisão for não oferecer zoom neste gráfico específico, remover a
     legenda de instrução de zoom desse gráfico nos dois registros de
     linguagem, para não anunciar uma interação inexistente.
  4. Testar em desktop, celular e tema escuro, nos dois registros.
Pronto quando: arrastar sobre a área de plotagem do gráfico de dispersão
restringe visivelmente os eixos (ou a legenda de zoom foi removida, se for
essa a decisão); nenhum arraste sobre o gráfico aciona seleção de texto
nativa do navegador; Ctrl+roda muda a escala dos eixos (se o zoom for
implementado).
Muda junto: nada além do comportamento deste gráfico.
Fase de origem: Entrega (não é correção de análise, é defeito de interface).

---

## [V1] Células "n insuf." difíceis de escanear na matriz do Dashboard
Crítica: a matriz "País e tamanho do pedido, cruzados" mostra "n insuf."
(Simples) ou "n<50" (Técnico) por extenso dentro das células sem dado
suficiente — texto bem mais longo que os números de 3-4 caracteres nas
outras células da mesma matriz, quebrando o ritmo de leitura de quem está
escaneando rapidamente.
Onde: Dashboard, matriz "País e tamanho do pedido, cruzados", células dos
países/faixas com n<50 (ex.: Finland/Q1, Sweden/Q1, Austria/Q1, Denmark/Q1
e Q2, Poland/Q1, Japan/Q2 e Q3), nos dois registros de linguagem.
O que fazer:
  1. Trocar o texto "n insuf."/"n<50" dentro da célula por um símbolo mais
     curto e discreto (por exemplo, um traço "—"), mantendo a borda
     tracejada e a cor neutra já usadas para marcar essas células.
  2. Manter a explicação completa ("poucos itens (não colorida)") na
     legenda abaixo da matriz; considerar mostrar o "n" exato num
     tooltip/hover para quem passar o mouse sobre a célula.
Pronto quando: as células sem dado suficiente mostram um símbolo curto, do
mesmo comprimento visual aproximado dos números nas outras células da
matriz.
Muda junto: nada além da formatação dessas células.
Fase de origem: Entrega.

---

## [V3] Cartão "n/d" do Painel sem destaque visual
Crítica: o cartão "Abandono no checkout" (Painel) mostra "n/d" com o mesmo
tamanho e peso visual dos três cartões vizinhos que têm números reais
(Faturamento, Pedidos, Clientes ativos) — a explicação de por que está em
branco só aparece num parágrafo abaixo da linha de cartões, não junto ao
cartão em si. Um leitor que só bate o olho na linha de cartões pode
interpretar "n/d" como dado ausente por falha, não por desenho.
Onde: Painel, linha de quatro cartões, cartão "Abandono no checkout", nos
dois registros de linguagem.
O que fazer:
  1. Aplicar um estilo visualmente mais discreto ao cartão "n/d" — por
     exemplo, texto acinzentado em vez da mesma cor/peso dos números reais
     dos outros três cartões.
  2. Adicionar uma nota curta diretamente sob o "n/d" (não só no parágrafo
     que vem depois da linha de cartões) — algo como "não medido por
     desenho — ver Relatório, seção 11".
Pronto quando: o cartão "n/d" é visualmente distinguível dos outros três à
primeira vista, com uma explicação de uma linha diretamente associada a
ele.
Muda junto: nada além do estilo e do texto deste cartão.
Fase de origem: Entrega.

---

## [V4] Cartão "+0,00" do Dashboard sem contexto
Crítica: o cartão "Diferença da média" (Dashboard) mostra "+0,00 pontos
percentuais" quando nenhum filtro está aplicado — correto, já que comparar
a base inteira com ela mesma dá zero por definição — mas nada perto do
cartão explica isso, então pode parecer um indicador quebrado.
Onde: Dashboard, linha de quatro cartões, cartão "Diferença da média",
estado padrão (sem filtro), nos dois registros de linguagem.
O que fazer:
  1. Adicionar uma frase curta junto ao cartão, ou ao texto "Nenhum filtro
     — mostrando tudo", explicando que a diferença é sempre 0,00 sem filtro
     ativo e passa a refletir o recorte assim que um filtro for aplicado.
Pronto quando: existe uma explicação de uma linha visível perto do cartão
"Diferença da média", no estado padrão da página, sobre por que ele mostra
zero.
Muda junto: nada além do texto de contexto.
Fase de origem: Entrega.

---

## Acabamento
- **[V5]** No plano de controle do Painel, a linha "Erro de separação em
  pedido grande do Reino Unido" tem o campo "Alarme em" preenchido com "a
  definir (sem dado de linha-base)" — correto e honesto, mas apresentado
  com a mesma formatação das linhas que já têm limite definido. Considerar
  um destaque visual de "pendente" para essa linha específica (por exemplo,
  um rótulo ou cor diferente), até que o limite seja definido com dado
  real.
