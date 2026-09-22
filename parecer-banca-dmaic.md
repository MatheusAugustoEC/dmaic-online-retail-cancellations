# Parecer da banca — Cancelamentos e Devoluções, Online Retail (UCI)

2026-09-22 · rodada 1 · https://matheusaugustoec.github.io/dmaic-online-retail-cancellations/ · nível 2 (repositório local consultado para confirmar suspeitas nascidas na leitura da página) · revisão visual: **realizada** (captura via Playwright — Painel, Dashboard, Relatório, Slides; Simples e Técnica; desktop, celular e escuro), **com uma lacuna declarada**: a captura de celular e escuro não cobriu o registro Técnica, e as capturas de Slides em Técnica pararam no slide 9/9 (ver "Limites desta revisão").

Esta banca não construiu o projeto e não tinha visto a página antes desta sessão.

## Veredito

**REPROVADO** — dois achados críticos. Um muda o número que a própria página
chama de "onde está o dinheiro" (o produto de maior prejuízo é 99,5% uma
única transação, não um padrão do produto). O outro muda o número que a
página chama de "o número que decide" (a base da conta de abandono no
checkout mistura linhas de pedido com pedidos). Ambos são reversíveis: são
erros de tratamento de dado e de unidade em uma conta, não falhas no desenho
do projeto — a auditoria de qualidade, a carta de controle e o teste da
hipótese rival continuam sólidos.

## A banca

- **Gestor** — Gerente de Operações de um atacadista/varejista online de
  presentes e utilidades, Reino Unido, ~12 anos no setor, responde por
  faturamento e custo operacional.
- **Especialista do domínio** — Gerente de fulfillment/separação de pedidos e
  logística reversa, atacado online B2B, Reino Unido.
- **Cientista de dados sênior** — especializado em controle estatístico de
  processo, teste de hipótese com efeito mínimo pré-registrado e desenho de
  experimentos/inferência causal.
- **Recrutador de dados** — calibrado para uma vaga de analista de dados
  júnior, generalista, mercado brasileiro (ajuste feito pelo usuário; troquei
  o roteiro original de vaga sênior de nicho por esta calibração).

(Cartões aprovados pelo usuário, com o ajuste acima, no início desta revisão.)

## A voz de cada revisor

**Gestor:** O Painel me convence em 30 segundos do tamanho do problema e da
disciplina por trás — a meta tem origem declarada, os guardrails contra
"reduzir cancelamento vendendo menos" existem, e o cenário conservador da
conta de ganho mostra prejuízo sem disfarce. Mas quando fui ver de onde vem o
"maior prejuízo" que justifica a prioridade de ação (produto 23166,
£77.579), descobri que é uma transação de 74.215 unidades num único dia —
não um padrão de produto. E a conta do ganho usa "34.257 pedidos" num
segmento que, pelo Painel, teria mais pedidos sozinho do que os 13.081
pedidos da janela inteira. Não assino embaixo de nenhum dos dois números até
serem refeitos. O alarme de "faturamento caiu 10%" também me preocupa: eu
sei, porque vendo presentes, que fevereiro e abril já caem mais que isso sem
nenhum problema real.

**Especialista do domínio:** O raciocínio de causa é bom — testar a hipótese
rival (país) antes da principal é disciplina real, não decorativa. Mas a
trava recomendada para "pedido grande do Reino Unido" é uma confirmação no
*checkout*, do lado do cliente — enquanto a causa que o próprio projeto
suspeita é erro de separação em lote grande, do lado do meu galpão. Se a
causa nasce na expedição, por que a trava está no carrinho de compras? É
justamente essa fricção que a simulação de ganho diz que pode zerar o
resultado — a trava recomendada é o próprio risco que a conta teme.

**Cientista de dados sênior:** Metodologicamente isto está bem acima da
média de um projeto de portfólio — hipótese rival pré-registrada e testada
antes das principais, efeito mínimo definido antes de olhar o dado, correção
de Holm para a família confirmatória, carta p′ de Laney no lugar certo,
holdout aberto uma única vez com o resultado divergente explicado por
censura, não maquiado como melhora. Isso é o que torna os dois achados
críticos mais graves, não menos: um projeto que se vende pela disciplina
estatística não pode ter o número-manchete de impacto dominado por uma
transação isolada, nem confundir linha de pedido com pedido na conta que ele
mesmo chama de "o número que decide". Também vi uma célula de matriz
dominando sozinha a escala de cor (n=87, longe do piso de confiança usado em
todo o resto do projeto) e um gráfico de bolhas ilegível por sobreposição.

**Recrutador de dados:** Para uma vaga júnior, isto já entrega mais disciplina
de processo do que a maioria dos projetos de portfólio com este mesmo
dataset que eu já vi — a troca de registro Simples/Técnico é um diferencial
real, e a autocrítica na seção "o que eu não sei" é específica, não
genérica. Mas não há nome, GitHub, LinkedIn ou contato em nenhum modo da
página — para uma peça de portfólio, isso é o tipo de coisa que me faz
fechar a aba antes de saber quem fez o trabalho. E "poka-yoke" aparece duas
vezes no modo Simples — pequeno, mas é o tipo de vazamento que eu uso para
saber se a pessoa testou a própria interface nos dois registros antes de
publicar.

## Achados críticos

**C1 · CRÍTICO · O "maior prejuízo" (£77.579, produto 23166) é 99,5% uma única transação — Cientista de dados sênior, Gestor**
- Onde: Painel ("Onde está o dinheiro", "Os dois Paretos discordam de
  propósito"), Dashboard ("Onde está o dinheiro"), Relatório (seção 5 /
  "Onde o dinheiro se perde"), Slides (03 · Onde dói) — em todos os modos e
  os dois registros de linguagem.
- Evidência: no dataset da janela de exploração
  (`docs/analyze_dataset_exploracao.parquet`), as 8 linhas de cancelamento do
  StockCode 23166 somam £77.579,29 de receita estornada. Uma única linha
  (InvoiceNo 541431, Quantity 74.215, 2011-01-18) responde por £77.183,60 —
  99,49% do total; as outras 7 linhas somam £395,69. O projeto já reconhece
  esse tipo de risco e já excluiu um caso quase idêntico noutro produto: "Um
  par isolado de pedido e cancelamento de 80.995 unidades do mesmo produto,
  no mesmo dia, foi excluído da lista de produtos nomeados" (StockCode
  23843, ver Relatório/Dashboard, nota de rodapé). O mesmo critério não foi
  aplicado a 23166, que continua como o produto nº1 em prejuízo e como o
  exemplo central da narrativa "os dois Paretos discordam de propósito" em
  toda a página.
- O que corrigir: aplicar o mesmo critério de exclusão de outlier isolado já
  usado para 23843 (transação única, quantidade extrema, evento de um dia)
  ao StockCode 23166, ou — se a decisão for mantê-lo — declarar
  explicitamente na página que o "prejuízo" desse produto é dominado por uma
  transação isolada e recalcular o Pareto B e o ranking de impacto sem essa
  linha, verificando se outro produto assume o 1º lugar.
- Erro ou preferência: ERRO (inconsistência de critério — regra 3 do método,
  T10 do roteiro do Cientista de dados).
- Fase de origem: Measure/Analyze (a exclusão de outliers isolados já é uma
  regra declarada nessas fases) — pós-hoc, porque o holdout já foi aberto.

**C2 · CRÍTICO · A conta do ganho conta linhas de produto como se fossem pedidos — "o número que decide" pode estar errado — Cientista de dados sênior, Gestor**
- Onde: Relatório ("A conta do ganho, passo a passo" / seção 10 técnica:
  "pedidos nos 3 segmentos sinalizados ... 34.257"), Painel (plano de
  controle cita o mesmo ponto de indiferença 2,01%).
- Evidência: o próprio bloco da conta, no Relatório, mistura as duas
  unidades na mesma tabela: "pedidos nos 3 segmentos sinalizados ...
  **34.257**" e "pedidos legítimos no segmento (não cancelariam) ...
  **33.205**", mas duas linhas abaixo "linhas evitadas (estimado) ...
  420,8" e "receita média **por linha** cancelada ... £100,77" — o mesmo
  número (34.257) é chamado de "pedidos" numa linha e tratado como contagem
  de linhas duas linhas depois. Confirmei no código: `src/fase4_improve.py`
  agrega com `n=("defect", "size")` sobre `docs/analyze_dataset_exploracao.parquet`,
  cuja unidade de linha é declarada em `docs/pre-registro-hipoteses.md:17`
  ("Unidade do defeito: **linha** (InvoiceNo × StockCode)") — e a mesma
  variável (`n_seg_total`) é impressa como "Pedidos nos segmentos
  sinalizados" na linha 60 do script. Recontando o dado bruto para os 3
  segmentos sinalizados (Resto×Q1×Recorrente, Resto×Q2×Recorrente,
  UK×Q4×Recorrente): são **6.902 faturas (InvoiceNo) distintas**, não
  34.257 — 4,96 linhas por fatura em média nesse segmento. Isso também
  contradiz o próprio Painel, que mostra `PEDIDOS: 13.081` (faturas
  distintas) para a janela madura inteira — um recorte de 3 segmentos não
  pode ter 2,6x mais pedidos que a base inteira. A frase "97% dos pedidos do
  segmento sinalizado são legítimos" (33.205/34.257) também está calculada
  sobre linhas, não pedidos; a proporção real de faturas com pelo menos um
  cancelamento no segmento é 624/6.902 (9,0%), uma leitura bem diferente de
  "97% legítimos".
- O que corrigir: decidir explicitamente qual é a unidade do evento
  "abandono no checkout" (um evento por fatura, não por linha de produto) e
  refazer a simulação de ganho agregando por `InvoiceNo` nos 3 segmentos
  antes de aplicar a taxa de abandono de 2% — ou, no mínimo, renomear
  "pedidos" para "linhas" em toda a seção e reescrever a frase "97% dos
  pedidos são legítimos" com a base correta. Verificável recontando
  `df[mask]["InvoiceNo"].nunique()` nos 3 segmentos sinalizados.
- Erro ou preferência: ERRO.
- Fase de origem: Improve — pós-hoc, porque o holdout já foi aberto e porque
  este é "o número que decide" citado na fase Control.

## Achados importantes

| ID | Achado | Evidência | O que corrigir | Fase de origem |
|---|---|---|---|---|
| I1 | A meta (1,99%) está exatamente no limite inferior do IC 95% do número principal (1,99%–2,10%) — a manchete "+0,05pp acima da meta" não avisa que, estatisticamente, não dá para afirmar com confiança que a taxa está acima da meta | Painel/Relatório técnico: "IC 95% Wilson: 1,99%–2,10%"; meta = "melhor quartil mensal" = 1,99% — o extremo inferior do intervalo é numericamente igual à meta | No bloco "Distância da meta" (Painel e Relatório), acrescentar uma frase reconhecendo que a meta cai na borda do intervalo de confiança do número principal, então a diferença de 0,05pp não é estatisticamente distinguível de zero com a margem reportada | Measure/Define (pós-hoc) |
| I2 | Célula Austrália × Q1 (menor) = 65,5% domina sozinha a escala de cor da matriz País × Quantidade, sem piso de n declarado (diferente do critério n≥50 usado nos Paretos de produto) | `graficos/desktop__simples__dashboard__03.png`; confirmado no dado agregado (`docs/entrega_dados.json`, cubo): a célula tem apenas **87 itens** e 57 cancelamentos — próxima maior célula da matriz é 14,2% (Japão/Q4) | Aplicar um piso mínimo de n à matriz (mesmo critério ou similar ao dos Paretos), ou marcar visualmente células abaixo do piso como "n insuficiente" em vez de colori-las na mesma escala | Entrega (pós-hoc) |
| I3 | Gráfico de dispersão do Dashboard tem rótulos ilegíveis por sobreposição | `sobreposicao.md`: "d-scatter · texto sobre texto: 4 ocorrências" e "texto sobre marca: 6 ocorrências", em desktop e escuro; confirmado visualmente em `graficos/desktop__simples__dashboard__06.png` — os rótulos de 23166, 22501 e outros dois produtos formam um bloco de texto ilegível | Usar leader lines ou mostrar rótulo só no hover para bolhas próximas na escala | Entrega (pós-hoc) |
| I4 | Os "198 produtos sinalizados" (H4) não têm controle de falso positivo individual — no piso de n=50 usado, um produto com a taxa média real da base ainda tem chance considerável de ser sinalizado por puro acaso | Relatório: "198 de 1.399 produtos... com n≥50... taxa ≥2x a média geral (1,868%)"; o teste citado (qui-quadrado global, χ²=6.206,1) confirma heterogeneidade na tabela inteira, mas não controla quantos dos 198 individuais são falsos positivos — com n=50 e taxa base 1,87%, um produto médio (esperado ≈0,94 cancelamento) tem ≈24% de chance de atingir ≥2 cancelamentos (≥4%, ≥2x) só por variação amostral (aproximação de Poisson) | Aplicar um piso de n mais alto para a lista final de "produtos para conferência dupla" ou usar o limite inferior do IC (como já é feito nos exemplos citados, StockCode 21232 e 21231) como critério de corte em vez da taxa pontual, para toda a lista de 198, não só nos exemplos | Analyze (pós-hoc) |
| I5 | A ação mais robusta (H4, ~198 produtos, 40,4% de cobertura) não tem conta de ganho/custo — só a ação de segmento (a mais frágil) tem número | Relatório, "A conta do ganho": "A simulação abaixo é sobre os 3 segmentos de risco... não sobre os produtos do H4, que exigiriam um teste operacional diferente" | Estimar ao menos uma ordem de grandeza do custo da auditoria física por produto e do ganho esperado, ou declarar explicitamente que a decisão sobre H4 não pode ser tomada só com este relatório | Improve (pós-hoc) |
| I6 | A trava recomendada para "pedido grande do Reino Unido" atua no checkout (lado do cliente); a causa suspeita (H1) é erro de picking em lote grande (lado do armazém) | `docs/pre-registro-hipoteses.md` atribui H1 a erro de picking/estoque em lotes grandes; a ação que vira Poka-yoke no Relatório/Painel é "confirmação obrigatória... no checkout" — o único item da hierarquia "Elimina a causa" (SOP de separação em duas etapas) não vira ação com dono e frequência no plano de controle | Levar à etapa de separação (picking) a verificação, em vez do checkout do cliente, ou declarar explicitamente essa troca (menos risco de erro físico vs. mais risco de abandono de cliente) e por que o checkout foi escolhido mesmo assim | Improve (pós-hoc) |
| I7 | Alarme "faturamento/pedidos caem >10% ao mês" no plano de controle não tem ajuste sazonal, e a base já mostra quedas mensais >10% fora do pico | `docs/control-plano.md` e Painel: alarme é "queda >10%, mensal", sem menção a sazonalidade; recalculando a receita mensal da própria janela de exploração: fev/2011 caiu 21,4% e abr/2011 caiu 22,1% em relação ao mês anterior — 2 de 8 transições mensais já excedem o limiar de 10% sem nenhum problema de processo, dentro da mesma janela usada para calibrar o projeto | Trocar o alarme por comparação ano contra ano ou por desvio da sazonalidade esperada (mesmo mês do ano anterior), não do mês anterior; o próprio Relatório já reconhece "um único pico de fim de ano" como limitação | Control (pós-hoc) |
| I8 | Nenhuma atribuição de autoria em nenhum modo da página | Capturas completas (topo e rodapé) de Painel, Dashboard e Relatório, desktop e celular: sem nome, GitHub, LinkedIn ou contato; confirmado também em `docs/index.html` (nenhuma ocorrência de "github", "linkedin" ou nome de autor) | Adicionar nome, link do repositório e/ou LinkedIn no cabeçalho ou rodapé da página, nos quatro modos | Entrega (pós-hoc) |

## Achados menores

- **M1** — Rótulo "limite do normal" sobreposto à própria linha pontilhada do limite superior, na carta de controle (Painel e Relatório, todos os modos/temas/dispositivos testados). Confirmado em `sobreposicao.md` ("texto sobre linha: 1 ocorrência") e visualmente. Corrigir com leve deslocamento vertical do rótulo. (Entrega, cosmético.)
- **M2** — "Poka-yoke" aparece no modo Simples (Painel e Relatório, tabela do plano de controle: "Adicionar à lista de conferência dupla (poka-yoke)"), quando o resto do modo Simples evita jargão técnico. Trocar por "conferência dupla" no registro Simples, mantendo "poka-yoke" só no Técnico. (Entrega, cosmético.)
- **M3** — A tabela "O que acompanhar" do Painel, no celular, é larga demais para a coluna e o texto quebra de forma apertada (`capturas/celular__simples__painel.png`); considerar layout de cartão empilhado para essa tabela no celular, como já é feito em outras seções.

## O que corrigir, passo a passo

### [C1] · Produto 23166 tem "maior prejuízo" dominado por uma transação isolada — prioridade 1
O problema, em linguagem simples: o produto que a página aponta como "o que
mais custa" (£77.579 devolvidos) deve esse número quase inteiro a um único
pedido cancelado de 74.215 unidades num único dia — não a um padrão real do
produto, como a narrativa da página sugere.
Por que importa: o exemplo "os dois Paretos discordam de propósito" — usado
em todos os quatro modos e nos slides como a peça central de "onde dói" —
usa esse produto como prova de que impacto e taxa de risco apontam para
produtos diferentes. Se o número some ao excluir a transação isolada, o
exemplo (e possivelmente o próprio 1º lugar do ranking de impacto) muda.
Onde está: Painel ("Onde está o dinheiro", "Os dois Paretos discordam de
propósito"); Dashboard ("Onde está o dinheiro (por produto)"); Relatório,
seção "Onde o dinheiro se perde"; Slides 03; nos dois registros de
linguagem. Fonte: `docs/analyze_dataset_exploracao.parquet`, linhas com
`StockCode == "23166"` e `defect == 1`; a linha isolada é `InvoiceNo ==
"541431"`.
O que fazer:
  1. Recalcular o Pareto de impacto (receita estornada por produto)
     excluindo a linha InvoiceNo 541431 do StockCode 23166, usando o mesmo
     critério já aplicado ao StockCode 23843 (transação isolada, quantidade
     extrema, evento de um único dia).
  2. Verificar qual produto assume o 1º lugar em prejuízo depois da
     exclusão, e atualizar a tabela de "PRODUTO / TAXA / RANK TAXA /
     ESTORNADO / RANK IMPACTO" do Relatório com os novos números.
  3. Atualizar todos os números derivados que citam £77.579, 23166 como
     "1º em prejuízo", ou o texto "Os dois Paretos discordam de propósito" —
     em Painel, Dashboard, Relatório e Slides, nos dois registros de
     linguagem.
  4. Registrar a exclusão nas notas de tratamento de dado (mesmo lugar onde
     a exclusão do StockCode 23843 já está documentada), com a mesma
     justificativa.
Como saber que ficou certo: o novo 1º lugar do ranking de impacto não é mais
dominado por uma única transação (verificar: a maior linha individual do
produto não passa de ~30–40% do total do produto, como já é o padrão nos
outros produtos do ranking); o número £77.579 não aparece mais em nenhum
modo associado a 23166 sem a ressalva, ou é substituído pelo valor
recalculado.
O que pode mudar junto: a tabela dos dois Paretos no Painel, Dashboard e
Relatório; o texto "Os dois Paretos discordam de propósito"; o Slide 03; a
lista de produtos do gráfico de bolhas (Dashboard) e sua legenda.
Tamanho: médio (refazer um cálculo e os textos/gráficos que dependem dele).
Fase de origem: Measure/Analyze, pós-hoc.

### [C2] · Conta do ganho mistura linhas de produto com pedidos — prioridade 2
O problema, em linguagem simples: a conta que decide se vale a pena
implantar uma verificação extra no checkout usa "34.257 pedidos" como base,
mas esse número é na verdade uma contagem de linhas de produto — o número
real de pedidos (faturas) nesses mesmos segmentos é 6.902, quase 5 vezes
menor. Como a taxa de abandono assumida (2%) é um evento por pedido, não por
linha, a conta pode estar calibrada sobre a base errada.
Por que importa: a página chama o resultado dessa conta (2,01%) de "o número
que decide" se a recomendação vale a pena — é citado no Painel, no
Relatório e nos Slides como o número mais importante de toda a fase Improve.
Também sustenta a frase "97% dos pedidos do segmento são legítimos", que na
verdade descreve 97% das linhas, não dos pedidos (a proporção real de
pedidos com algum cancelamento no segmento é maior, 9,0%, não 3,1%).
Onde está: Relatório, seção "A conta do ganho, passo a passo" (modo Simples)
/ seção 10 (Técnico); Painel, plano de controle (cita o mesmo 2,01%).
Fonte: `src/fase4_improve.py`, linhas 25–27 (`n=("defect", "size")`) e linha
60 (`print(f"Pedidos nos segmentos sinalizados: {n_seg_total}...")`);
`docs/pre-registro-hipoteses.md:17` (unidade do defeito = linha);
`docs/improve-recomendacao.md`.
O que fazer:
  1. Decidir explicitamente a unidade do evento "abandono no checkout": é
     por fatura (InvoiceNo), não por linha de produto.
  2. Recalcular, para os 3 segmentos sinalizados (Resto×Q1×Recorrente,
     Resto×Q2×Recorrente, UK×Q4×Recorrente), o número de faturas distintas
     (`nunique` de InvoiceNo) e de faturas com pelo menos um cancelamento,
     em vez do número de linhas.
  3. Refazer a simulação de ganho (cenários conservador/central/otimista) e
     o ponto de indiferença usando a contagem de faturas para o lado do
     abandono no checkout, mantendo a receita agregada como está (a conta
     de receita preservada, em total, não muda).
  4. Atualizar a frase "97% dos pedidos do segmento sinalizado são
     legítimos" com a proporção correta em nível de fatura.
  5. Atualizar o desenho experimental (seção 11/4 técnica): a taxa-base do
     segmento usada no cálculo de poder (3,071%, calculada por linha) deve
     ser recalculada em nível de fatura, o que muda o `n` necessário por
     braço.
Como saber que ficou certo: o total de "pedidos" citado nos 3 segmentos é
menor que 13.081 (o total de pedidos da janela madura inteira, mostrado no
Painel); `df.groupby("InvoiceNo").ngroups` nos 3 segmentos bate com o número
citado no Relatório.
O que pode mudar junto: o ponto de indiferença (2,01%), o ganho líquido dos
três cenários, o `n` necessário por braço do experimento, a frase sobre
"97% legítimos", e qualquer lugar do Painel/Slides que cite esses números.
Tamanho: médio (refazer um cálculo; não muda a análise de causa raiz).
Fase de origem: Improve, pós-hoc.

### Importantes — um resumo por item
- **[I1]** Meta na borda do IC do número principal: acrescentar a ressalva estatística no bloco "Distância da meta" (Painel/Relatório).
- **[I2]** Célula Austrália/Q1 (n=87) domina a escala de cor: aplicar piso mínimo de n à matriz do Dashboard.
- **[I3]** Rótulos sobrepostos no gráfico de bolhas: leader lines ou rótulo só no hover.
- **[I4]** Lista de 198 produtos sem controle de falso positivo: usar limite inferior do IC como critério de corte, não a taxa pontual.
- **[I5]** H4 sem conta de ganho/custo: estimar ordem de grandeza ou declarar a lacuna explicitamente.
- **[I6]** Trava no checkout, causa suspeita no picking: mover a verificação para a separação, ou justificar a escolha do checkout.
- **[I7]** Alarme de queda >10% sem ajuste sazonal: trocar para comparação ano contra ano.
- **[I8]** Sem autoria na página: adicionar nome/GitHub/LinkedIn no cabeçalho ou rodapé, nos quatro modos.

### Acabamento (menores)
- **[M1]** Deslocar o rótulo "limite do normal" para não sobrepor a linha do limite.
- **[M2]** Trocar "poka-yoke" por "conferência dupla" no registro Simples.
- **[M3]** Ajustar a tabela "O que acompanhar" do Painel para um layout mais largo no celular.

## O que está sólido

**Gestor**
- O ponto de indiferença é apresentado como "o número que decide", não o
  ganho bruto, e o cenário conservador (prejuízo, −£21.002) é mostrado sem
  suavização — mesmo com o problema de unidade do achado C2.
- O stakeholder ("Ger. Operações") é declarado explicitamente como persona
  simulada, sem fingir aprovação real.

**Especialista do domínio**
- As contramedidas seguem a hierarquia correta (elimina causa → reduz
  variação → poka-yoke → apenas detecta), e a trava por quantidade nunca é
  aplicada fora do critério condicionado a H5 — a heterogeneidade por país é
  respeitada na recomendação, não só na análise.
- O FMEA aponta como maior risco (NPR 216) exatamente o segmento de clientes
  recorrentes de alto volume sendo o mais penalizado pela própria
  recomendação — reconhece o ponto fraco em vez de escondê-lo.

**Cientista de dados sênior**
- H5 (hipótese rival) testada antes de H1/H2, com efeito mínimo
  pré-registrado e correção de Holm aplicada à família confirmatória inteira
  — protocolo anti-garimpo real, verificável no código, não só declarado.
- Holdout aberto uma única vez; resultado fora da projeção (censura à
  direita) registrado e explicado com evidência (queda mensal monotônica
  dentro do próprio holdout), em vez de escondido atrás de "a taxa
  melhorou".
- A carta p′ de Laney está corretamente escolhida: a carta mensal simples
  realmente teria sinalizado ~40% dos meses por sobredispersão, não causa
  especial — confirmado ao ler a lógica de σz no texto técnico.

**Recrutador de dados**
- Autocrítica específica e recorrente ("O que eu não sei", "o que a
  simulação não captura") em vez de genérica.
- No modo Painel, em uma tela, aparecem o número principal, a distância da
  meta e a limitação central, sem precisar procurar no Relatório.
- A troca de registro Simples/Técnico é executada nos quatro modos, não só
  no texto — inclusive nos títulos dos gráficos e nas notas de rodapé.

## Cobertura dos roteiros

| Revisor | Itens | OK | Achado | Não se aplica |
|---|---|---|---|---|
| Gestor | 8 (G1–G8) | 4 | 4 (C2 via G2/G4, I1 via G3, I7 via G5) | 0 |
| Especialista do domínio | 8 (E1–E8) | 6 | 2 (I6 via E3, I7 via E7) | 0 |
| Cientista de dados sênior | 12 (T1–T12) | 6 | 6 (C1 via T2/T4/T10, C2 via T1, I1 via T3, I2 via T4, I3/M1 via T11, I4 via T5) | 1 (T9 — projeto não constrói modelo preditivo comparado com baseline) |
| Recrutador de dados | 8 (R1–R8) | 6 | 2 (I8 via R1, M2 via R5) | 0 |

Notas de itens específicos, para deixar a resposta calculada visível:

- **G3** ▸ diferença para a meta = +0,05pp; intervalo do número principal =
  1,99%–2,10%; a meta está no limite inferior do intervalo, não claramente
  fora dele → achado I1.
- **T2** ▸ maior item do ranking de impacto: 23166, £77.579 ÷ £299.135 =
  25,9% do total devolvido na janela madura — acima de 20%, suspeita
  obrigatória confirmada como achado crítico (C1) após verificação no
  dado bruto.
- **T3** ▸ o IC do número principal (2,05%) foi calculado por Wilson sobre
  linhas independentes; a página mostra variação extra comprovada
  (sobredispersão, σz=2,77) na carta de controle semanal, mas não propaga
  essa sobredispersão para o IC do número-manchete → registrado como parte
  do achado I1 (a meta cair na borda de um IC que já é, na melhor das
  hipóteses, otimista).
- **E2** ▸ a métrica principal junta os eventos: cancelamento (antes da
  expedição) e devolução (depois da expedição); no setor, eles costumam ser
  tratados como eventos separados, com dono e custo diferentes (o campo de
  dado não permite diferenciar, e a página já declara isso como limitação
  explícita — "Não sei se um cancelamento foi o cliente ou o próprio
  vendedor corrigindo um erro" — por isso não vira achado novo, é uma
  limitação já reconhecida).

## Matriz de achados

| ID | Gravidade | Revisor | Fase de origem | Pós-hoc | Status |
|---|---|---|---|---|---|
| C1 | Crítico | Cientista de dados sênior, Gestor | Measure/Analyze | Sim | aguardando decisão |
| C2 | Crítico | Cientista de dados sênior, Gestor | Improve | Sim | aguardando decisão |
| I1 | Importante | Gestor, Cientista de dados sênior | Measure/Define | Sim | aguardando decisão |
| I2 | Importante | Cientista de dados sênior | Entrega | Sim | aguardando decisão |
| I3 | Importante | Cientista de dados sênior | Entrega | Sim (cosmético) | aguardando decisão |
| I4 | Importante | Cientista de dados sênior | Analyze | Sim | aguardando decisão |
| I5 | Importante | Gestor | Improve | Sim | aguardando decisão |
| I6 | Importante | Especialista do domínio | Improve | Sim | aguardando decisão |
| I7 | Importante | Gestor, Especialista do domínio | Control | Sim | aguardando decisão |
| I8 | Importante | Recrutador de dados | Entrega | Sim (cosmético) | aguardando decisão |
| M1 | Menor | Cientista de dados sênior | Entrega | Sim (cosmético) | aguardando decisão |
| M2 | Menor | Recrutador de dados | Entrega | Sim (cosmético) | aguardando decisão |
| M3 | Menor | Cientista de dados sênior | Entrega | Sim (cosmético) | aguardando decisão |

## Limites desta revisão

- **Cobertura de captura incompleta no registro Técnico**: a captura de tela
  em celular e tema escuro só rodou no registro Simples; o registro Técnico
  foi confirmado apenas em desktop (Painel, Dashboard, Relatório) e nos
  Slides só até o slide 1 de 9 (estado herdado da navegação anterior do
  script). Não é possível certificar que o registro Técnico funciona
  corretamente no celular, no tema escuro, ou que os 9 slides existem e
  renderizam em Técnico — isso não gerou achado, mas também não foi
  verificado como OK.
- **Nível 2 parcial**: o repositório local foi consultado só para confirmar
  as suspeitas nascidas na leitura da página (C1, C2, I2, I4, I7, I8) — não
  foi feita uma auditoria independente de todo o código-fonte, nem
  reexecução completa dos scripts das fases anteriores.
- Esta revisão não teve acesso a nenhum profissional real do setor de
  varejo online; toda afirmação sobre prática de fulfillment, picking ou
  comportamento de abandono de checkout (I6, I7) é conhecimento geral do
  revisor emulado — tratar como hipótese a confirmar (regra 3 da banca), não
  como fato do setor.
- Esta conversa não escreveu nenhum código deste projeto e é a primeira vez
  que vê a página e o repositório — mas o diretório de trabalho local é o
  mesmo repositório do projeto, o que permitiu o nível 2 sem clonar nada.
  Registra-se por transparência.
- Um `parecer-banca-dmaic.md` de uma rodada anterior (mesma data,
  REPROVADO, com achados C1/I1–I7/M1 sobre a mesma unidade de "pedidos" e
  os mesmos defeitos visuais) já existia neste repositório antes desta
  sessão, sem corresponder a nenhuma correção aplicada na página publicada.
  A pedido do usuário, esta rodada foi conduzida de forma independente, sem
  reler aquele parecer. O conteúdo anterior foi preservado em
  `parecer-banca-dmaic-anterior.md` antes deste arquivo ser sobrescrito.
