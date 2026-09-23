# CORREÇÕES DA BANCA — Cancelamentos e Devoluções, Online Retail (UCI)

Uma banca de revisores independentes revisou a página publicada
(https://matheusaugustoec.github.io/dmaic-online-retail-cancellations/,
2026-09-22). Abaixo estão as correções, na ordem em que devem ser feitas: as
primeiras mudam números de que as outras dependem. Faça uma por vez, na
ordem.

Se eu tiver apagado algum bloco, é porque decidi não corrigir aquele ponto —
não o reintroduza.

## Regras
- Não mexa no que a banca considerou sólido: a hierarquia de contramedidas
  (elimina causa → reduz variação → poka-yoke → detecta); o teste de H5
  antes de H1/H2 com efeito mínimo pré-registrado e correção de Holm; a
  escolha da carta p′ de Laney; a abertura única do holdout e o registro
  honesto do resultado fora da projeção; a autocrítica da seção "O que eu
  não sei".
- Toda correção abaixo é pós-hoc — o holdout já foi aberto. Registre isso no
  relatório e na página; não "reconfirme" no holdout.
- Um número mudou? Atualize todos os lugares da página em que ele aparece,
  nos dois registros de linguagem (Simples e Técnica) e nos quatro modos
  (Painel, Dashboard, Relatório, Slides).
- Ao terminar: refaça a Entrega, rode de novo a auditoria final da página, e
  me diga, em uma linha por ID, o que mudou.

---

## [C1] O "maior prejuízo" (£77.579, produto 23166) é 99,5% uma única transação
Crítica: o produto apontado como "onde está o dinheiro" e usado no exemplo
central "os dois Paretos discordam de propósito" (em todos os quatro modos e
nos slides) deve seu valor de prejuízo quase inteiramente a uma única
transação isolada — 74.215 unidades canceladas num único dia — não a um
padrão real de devolução do produto.
Onde: Painel ("Onde está o dinheiro", "Os dois Paretos discordam de
propósito"); Dashboard ("Onde está o dinheiro (por produto)"); Relatório,
seção "Onde o dinheiro se perde"; Slides 03. Fonte de dado: a linha com
`StockCode == "23166"` e `InvoiceNo == "541431"` no dataset da janela de
exploração — ela sozinha soma £77.183,60 dos £77.579,29 atribuídos ao
produto.
O que fazer:
  1. Recalcular o Pareto de receita estornada por produto excluindo essa
     linha isolada, usando o mesmo critério já aplicado a outro caso
     idêntico no projeto (transação única, quantidade extrema, evento de um
     dia — StockCode 23843, já excluído da lista de produtos nomeados).
  2. Verificar qual produto assume o 1º lugar em prejuízo depois da
     exclusão e atualizar a tabela "PRODUTO / TAXA / RANK TAXA / ESTORNADO /
     RANK IMPACTO" do Relatório.
  3. Atualizar todos os números e textos que citam £77.579 ou 23166 como
     "1º em prejuízo" — Painel, Dashboard, Relatório e Slides, nos dois
     registros de linguagem — inclusive a legenda do gráfico de bolhas do
     Dashboard.
  4. Documentar a exclusão nas notas de tratamento de dado, no mesmo lugar
     onde a exclusão do StockCode 23843 já está registrada, com a mesma
     justificativa.
Pronto quando: nenhuma linha individual de nenhum produto do ranking de
impacto responde por mais de ~30–40% do total daquele produto (o padrão dos
demais produtos da lista); os números de £77.579 e "23166 = 1º em prejuízo"
não aparecem mais sem a ressalva ou foram substituídos.
Muda junto: a tabela dos dois Paretos (Painel, Dashboard, Relatório); o
texto "Os dois Paretos discordam de propósito"; o Slide 03; a lista e a
legenda do gráfico de bolhas do Dashboard.
Fase de origem: Measure/Analyze · pós-hoc

---

## [C2] Conta do ganho mistura linhas de produto com pedidos
Crítica: a conta que decide se vale a pena instalar uma confirmação extra no
checkout usa "34.257 pedidos" como base, mas esse número é uma contagem de
linhas de produto (InvoiceNo × StockCode), não de pedidos reais — o número
real de faturas distintas nesses mesmos três segmentos é 6.902, quase 5
vezes menor. Como o abandono de checkout é um evento por fatura, não por
linha de produto, a base da conta pode estar errada, e a frase "97% dos
pedidos do segmento são legítimos" descreve na verdade 97% das linhas, não
dos pedidos.
Onde: Relatório, "A conta do ganho, passo a passo" (Simples) / seção 10
(Técnico); Painel, plano de controle (cita o mesmo ponto de indiferença,
2,01%). No código: a agregação que gera "34.257" conta linhas do dataset de
linhas, não faturas distintas.
O que fazer:
  1. Decidir explicitamente que o evento "abandono no checkout" é por
     fatura (InvoiceNo), não por linha de produto.
  2. Recalcular, para os 3 segmentos sinalizados, o número de faturas
     distintas e de faturas com pelo menos um cancelamento, em vez do
     número de linhas.
  3. Refazer os três cenários da simulação de ganho e o ponto de
     indiferença usando a contagem de faturas para o lado do abandono no
     checkout (a receita total preservada, em soma, não precisa mudar — só
     a base de "pedidos legítimos" contra a qual a taxa de abandono é
     aplicada).
  4. Corrigir a frase "97% dos pedidos do segmento sinalizado são
     legítimos" com a proporção correta em nível de fatura.
  5. Recalcular a taxa-base do segmento usada no desenho experimental (hoje
     3,071%, calculada por linha) em nível de fatura, e o `n` necessário
     por braço do experimento com essa taxa corrigida.
Pronto quando: o total de "pedidos" citado nos 3 segmentos sinalizados é
menor que 13.081 (o total de pedidos da janela madura inteira, mostrado no
Painel); contar faturas distintas nos 3 segmentos reproduz o número citado
no texto.
Muda junto: o ponto de indiferença (2,01%), o ganho líquido dos três
cenários, o `n` por braço do experimento, a frase "97% legítimos", e
qualquer lugar do Painel ou Slides que cite esses números.
Fase de origem: Improve · pós-hoc

---

## [I1] Meta cai na borda do intervalo de confiança do número principal
Crítica: a manchete "+0,05 ponto percentual acima da meta" apresenta a
diferença como um fato, mas o intervalo de confiança de 95% do número
principal (1,99%–2,10%) tem seu limite inferior exatamente igual à meta
(1,99%) — estatisticamente, não dá para afirmar com confiança que a taxa
está de fato acima da meta.
Onde: Painel, bloco "Distância da meta" (Simples e Técnica); Relatório,
seção 1.
O que fazer:
  1. No bloco "Distância da meta" do Painel e na seção correspondente do
     Relatório, acrescentar uma frase reconhecendo que a meta cai na borda
     do intervalo de confiança do número principal, então a diferença de
     0,05pp não é estatisticamente distinguível de zero com a margem
     reportada.
  2. Evitar a formulação "acima da meta" como fato isolado sem essa
     ressalva nos dois registros de linguagem.
Pronto quando: o bloco "Distância da meta", em qualquer registro, menciona
explicitamente que a meta está dentro da margem de erro do número
principal.
Muda junto: nenhum número muda — só o texto de interpretação.
Fase de origem: Measure/Define · pós-hoc

---

## [I2] Célula Austrália × Q1 (n=87) domina sozinha a escala de cor da matriz
Crítica: a matriz País × Tamanho do Pedido do Dashboard tem uma célula
(Austrália, Q1 menor) mostrando 65,5% de chance de voltar — ordens de
grandeza acima de todas as outras células (a segunda maior é 14,2%) —, e
essa célula tem apenas 87 itens na base, muito abaixo do piso de confiança
usado em outras partes do projeto (n≥50, e mesmo esse piso é baixo). A
célula distorce visualmente a escala de cor de toda a matriz.
Onde: Dashboard, "País e tamanho do pedido, cruzados".
O que fazer:
  1. Definir um piso mínimo de n para a matriz (por exemplo, o mesmo n≥50
     usado nos Paretos de produto, ou um piso equivalente ajustado ao
     tamanho de cada célula da matriz).
  2. Para células abaixo do piso, não colori-las na mesma escala das
     demais — marcar como "n insuficiente" ou omitir o valor.
  3. Refazer a escala de cor da matriz depois de aplicar o piso, para que
     ela reflita a variação real entre as células com dado suficiente.
Pronto quando: nenhuma célula da matriz com n abaixo do piso definido
aparece colorida na mesma escala das demais.
Muda junto: a escala de cor de toda a matriz (as outras células ficam mais
distinguíveis entre si).
Fase de origem: Entrega · pós-hoc

---

## [I3] Gráfico de bolhas do Dashboard com rótulos ilegíveis por sobreposição
Crítica: o gráfico "Volume contra frequência, por produto" tem vários
rótulos de produto se sobrepondo a ponto de formar um bloco de texto
ilegível, em desktop e no tema escuro, nos dois registros de linguagem.
Onde: Dashboard, "Volume contra frequência, por produto" (gráfico de
bolhas).
O que fazer:
  1. Para bolhas próximas na escala (ex.: 23166, 22501 e outros dois
     produtos do canto esquerdo), usar leader lines que afastem o rótulo do
     ponto, ou mostrar o rótulo apenas no hover em vez de fixo.
  2. Testar a correção em desktop, celular e tema escuro, nos dois
     registros de linguagem.
Pronto quando: nenhuma ocorrência de "texto sobre texto" ou "texto sobre
marca" aparece para o gráfico de bolhas numa nova checagem de sobreposição.
Muda junto: nada além da renderização do próprio gráfico.
Fase de origem: Entrega · pós-hoc

---

## [I4] Lista de 198 produtos sinalizados sem controle de falso positivo individual
Crítica: os "198 produtos com taxa ≥2x a média geral" usam um piso de n=50
para entrar na lista, mas nesse piso um produto com a taxa média real da
base inteira ainda tem uma chance considerável (por volta de 1 em 4) de
atingir "≥2x a média" só por acaso, mesmo sem nenhum problema real de
qualidade.
Onde: Relatório, seção "Por que acontece" / seção 6 técnica (H4 — StockCode
específico).
O que fazer:
  1. Para a lista final de produtos recomendados para conferência dupla,
     usar o limite inferior do intervalo de confiança da taxa (como já é
     feito nos exemplos citados no texto, StockCode 21232 e 21231) como
     critério de corte, em vez da taxa pontual observada.
  2. Recalcular quantos dos 198 produtos permanecem na lista com esse
     critério mais rigoroso, e atualizar o número "198" e a cobertura de
     40,4% em todos os modos que os citam.
Pronto quando: o critério de corte da lista de produtos sinalizados usa o
limite inferior do IC, não a taxa pontual, e o número "198" (ou o que o
substituir) é consistente com esse critério em toda a página.
Muda junto: o número "198", a cobertura percentual de H4 (40,4%), e
qualquer soma de causas que dependa desse número.
Fase de origem: Analyze · pós-hoc

---

## [I5] Ação mais robusta (H4) não tem conta de ganho/custo
Crítica: a causa que mais explica o prejuízo (H4, produto específico,
40,4% de cobertura) é chamada de "a mais robusta", mas é a única ação sem
nenhuma estimativa de ganho ou custo — só a ação de segmento (a mais frágil,
com ganho de apenas £200 no cenário central) tem uma conta completa.
Onde: Relatório, "A conta do ganho, passo a passo".
O que fazer:
  1. Estimar, mesmo que em ordem de grandeza, o custo de implementar a
     conferência dupla nos ~198 produtos sinalizados (tempo de conferência
     por unidade × volume esperado) e o ganho esperado (receita hoje
     perdida nesses produtos × fração que a conferência evitaria).
  2. Se não for possível estimar com confiança, declarar explicitamente no
     texto que a decisão sobre H4 não pode ser tomada só com este relatório
     — em vez de deixar a lacuna implícita.
Pronto quando: a seção "A conta do ganho" tem uma estimativa (ainda que
grosseira, com premissas declaradas) para a ação de H4, ou uma frase
explícita reconhecendo que essa conta não foi feita e por quê.
Muda junto: nada além do próprio texto e da nova estimativa.
Fase de origem: Improve · pós-hoc

---

## [I6] Trava recomendada no checkout; causa suspeita no picking
Crítica: a causa suspeita para "pedido grande do Reino Unido cancela mais"
é erro de separação (picking) em lote grande — um problema do armazém. Mas
a única ação que vira trava com dono e frequência no plano de controle é uma
confirmação extra no checkout — do lado do cliente, não do armazém. A
verificação na separação (que atacaria a causa direto) aparece só como
"Elimina a causa", sem virar ação com dono.
Onde: Relatório, "O que fazer" / seção 9 técnica; Painel, plano de controle.
O que fazer:
  1. Avaliar se uma checagem na etapa de separação (mais perto de onde a
     causa suspeita nasce) substitui, ou complementa, a confirmação no
     checkout.
  2. Se o checkout for mantido como a ação principal, escrever
     explicitamente por que — reconhecendo a troca: menos risco de erro
     físico de separação vs. mais risco de abandono de cliente (a mesma
     fricção que a simulação de ganho já trata como risco central).
  3. Atualizar o plano de controle (Painel) para incluir a ação de
     separação como item com dono e frequência, se ela for adotada.
Pronto quando: o plano de controle e o texto do Relatório explicam
explicitamente por que a trava está no checkout e não na separação, ou a
ação de separação passa a ter dono e frequência no plano.
Muda junto: a tabela do plano de controle (Painel); a lista de ações do
Relatório.
Fase de origem: Improve · pós-hoc

---

## [I7] Alarme de queda de faturamento >10%/mês sem ajuste sazonal
Crítica: o plano de controle dispara um alarme se faturamento ou pedidos
caírem mais de 10% num mês. Mas, olhando os próprios dados usados no
projeto, fevereiro/2011 já caiu 21,4% e abril/2011 já caiu 22,1% em relação
ao mês anterior, sem nenhum problema real — a variação natural do negócio já
excede o limiar do alarme, mesmo fora do pico real de fim de ano (que nem
está incluído na janela usada para calibrar o alarme).
Onde: Painel e Relatório, tabela "O que acompanhar" / plano de controle.
O que fazer:
  1. Recalcular a variação mês a mês de faturamento e pedidos usando os
     dados já disponíveis no projeto, incluindo os meses de dezembro (o
     pico real de fim de ano, hoje parcialmente fora da janela de
     exploração).
  2. Trocar o alarme "queda >10% no mês anterior" por uma comparação ano
     contra ano (mesmo mês do ano anterior) ou por desvio da sazonalidade
     esperada, não do mês imediatamente anterior.
Pronto quando: o alarme de faturamento/pedidos no plano de controle não
dispara ao aplicar a série histórica completa do projeto (incluindo
dezembro) com a nova regra.
Muda junto: a tabela do plano de controle no Painel e no Relatório.
Fase de origem: Control · pós-hoc

---

## [I8] Nenhuma atribuição de autoria na página
Crítica: não há nome, GitHub, LinkedIn ou qualquer forma de contato em
nenhum dos quatro modos da página — para uma peça de portfólio, isso impede
o leitor de saber quem fez o trabalho.
Onde: cabeçalho ou rodapé de todos os modos (Painel, Dashboard, Relatório,
Slides).
O que fazer:
  1. Adicionar nome, link do repositório no GitHub e/ou LinkedIn no
     cabeçalho ou rodapé da página.
  2. Confirmar que aparece nos quatro modos, não só num deles.
Pronto quando: uma busca por "github" ou pelo nome do autor no HTML da
página encontra pelo menos uma ocorrência visível em cada modo.
Muda junto: nada além do cabeçalho/rodapé.
Fase de origem: Entrega · pós-hoc

---

## Acabamento
- **[M1]** Deslocar verticalmente o rótulo "limite do normal" na carta de
  controle (Painel e Relatório), para não sobrepor a linha pontilhada do
  limite superior.
- **[M2]** No registro Simples, trocar "poka-yoke" por "conferência dupla"
  na tabela do plano de controle (Painel e Relatório); manter "poka-yoke"
  só no registro Técnico.
- **[M3]** Ajustar o layout da tabela "O que acompanhar" do Painel no
  celular (cartões empilhados em vez de tabela larga), para não comprimir o
  texto.
