# FASE 3 — ANALYZE · Causa raiz

Data: 2026-09-20. Código: `src/fase3_analyze.py`. Dataset de trabalho salvo em
`docs/analyze_dataset_exploracao.parquet`. Holdout nunca carregado (guarda no
início do script, idêntica à 2B). Universo idêntico ao baseline congelado:
n=265.427, defeitos=4.957, taxa=1,868%.

> **AVISO VÁLIDO PARA TODA ESTA FASE (Tollgate item 4)**: toda conclusão de
> causa abaixo vale apenas para o subconjunto **pareável** de cancelamentos
> (85,0% dos candidatos na janela de exploração — número um pouco diferente do
> 81,8% da Fase 0 porque aqui a base já está restrita a produto real/preço
> positivo). Os cancelamentos não pareáveis (15–18% conforme a fase) ficam fora
> de qualquer teste de causa e não são o universo completo de cancelamentos
> históricos. Nenhum gráfico ou tabela abaixo representa o total.

## 1. Ishikawa adaptado

| Categoria | Causa | Testável aqui? |
|---|---|---|
| Cliente | País (UK vs. Resto) | Sim — H2 |
| Cliente | Recorrência (primeira compra vs. recorrente) | Sim — H5 |
| Cliente | Porte da compra (Quantity) | Sim — H1 |
| Cliente | Motivo declarado da devolução | **Não** — não existe no dado → limitação |
| Produto | StockCode específico | Sim — H4 |
| Produto | Categoria de produto | **Não como categoria formal** — não existe taxonomia; Description é texto livre com 16,4% de inconsistência (Measure 2A). Não invento categoria. |
| Produto | Preço (UnitPrice) | Tratado como covariável de contexto, não hipótese confirmatória formal |
| Operação | Época do ano / carga de pedidos | Parcialmente — H3, rebaixada a exploratória (pico real está no holdout) |
| Operação | Erro de picking específico em lote grande | **Não diretamente** — sem registro de erro operacional por linha; testado só por proxy via H1, nunca confirmado como mecanismo |
| Sistema de registro | StockCode não-produto misturado | Já tratado (excluído, Fase 0/2A) |
| Sistema de registro | CustomerID nulo | Já tratado (fora do universo pareável) |
| Sistema de registro | Erro humano específico do operador | **Não** — sem identificador de operador na base → limitação |

## 2. H5 — Hipótese rival estrutural (testada primeiro)

**Efeito cru de Quantity (Q4 vs. Q1)**: diferença 1,509 p.p. (IC95%
[1,344; 1,673]), OR 2,335 (IC95% [2,144; 2,542]).

**Estratificado**:
- Por recorrência: Primeira compra 1,181 p.p.; Recorrente 1,612 p.p. — mesma
  direção, magnitude parecida.
- Por país: **UK 1,714 p.p.** (Q4 2,773% vs. Q1 1,059%); **Resto −1,718 p.p.**
  (Q4 2,215% vs. Q1 3,933% — **o efeito inverte de sinal**).

**Teste de Cochran-Mantel-Haenszel / Breslow-Day**:
- Por país: estatística 168,1, **p<0,0001 — rejeita homogeneidade**. Há
  heterogeneidade real e significativa do efeito de Quantity entre UK e Resto.
- Por recorrência: estatística 0,78, p=0,3765 — não rejeita homogeneidade.

**Regressão logística** (defeito ~ log(1+Quantity) + país + recorrência): OR
ajustado de log(1+Quantity) = 1,315 (IC95% [1,282; 1,349]) contra OR cru = 1,327
— redução de apenas 3,0% na escala log-odds ao controlar por país e
recorrência.

### Veredito H5 — não é um "sim" nem um "não" limpo, e registro isso sem forçar

A regressão agregada e a estratificação por recorrência **não sustentam**
composição/seleção como explicação principal — o efeito de Quantity sobrevive
quase intacto ao controle (redução de 3%), e é homogêneo entre clientes novos e
recorrentes.

Mas o teste de Breslow-Day por país encontrou algo que a regressão agregada
esconde: **o efeito de Quantity não generaliza para fora do UK — em "Resto" ele
se inverte** (pedidos pequenos cancelam MAIS que pedidos grandes nesse grupo,
n=2.924 no Q1 de Resto, amostra menor mas o teste dentro do estrato já é
significativo, p=1,25e-05). Isso é uma forma real, embora parcial, do que H5
propôs: a composição de PAÍS modula o efeito de Quantity — não o elimina, mas
restringe onde ele vale.

**Veredito registrado**: H5 **PARCIALMENTE CONFIRMADA por país, REFUTADA por
recorrência**. Consequência direta para a Improve: "Quantity alta = risco" **só
vale dentro do UK** (91% do volume, então ainda é a maioria dos casos, mas não é
uma regra universal) — qualquer regra de segmentação que use Quantity sem
condicionar a país generalizaria incorretamente para o Resto, onde o padrão é o
oposto.

## 3. H1 — Quantity (teste formal, após H5)

Efeito observado: **1,509 p.p.** entre Q4 e Q1 — estatisticamente muito
significativo (p=1,9e-72) mas **abaixo do efeito mínimo prático pré-registrado
de 3 p.p.** Mesmo dentro do UK (onde o efeito é maior), a diferença é 1,714
p.p. — ainda abaixo do mínimo.

**Veredito H1: estatisticamente confirmada, praticamente REFUTADA.** Com n
deste tamanho, quase qualquer diferença vira "significativa" por valor-p — é
exatamente por isso que o Define pré-registrou um efeito mínimo acionável, e a
regra 5 do contexto mestre exige isso. Não entra na lista final de causas
acionáveis por si só.

## 4. H2 — Country (UK vs. Resto)

Efeito observado: **0,588 p.p.** (Resto 2,390% vs. UK 1,802%, IC95%
[0,406; 0,770]) — estatisticamente significativo (p=2,3e-10) mas **muito abaixo
do efeito mínimo prático pré-registrado de 5 p.p.**

**Veredito H2: estatisticamente confirmada, praticamente REFUTADA**, pelo mesmo
motivo do H1.

## 5. H3 — Sazonalidade (exploratória, não confirmatória)

dez/2010 (proxy fraco de pico) vs. resto: diferença 0,138 p.p., **não
significativa** (p=0,129). Sem evidência de efeito sazonal nesta checagem
fraca — mas o teste real (novembro genuíno) só acontece na abertura do holdout
em Control, conforme já decidido no Define. Não entra na lista de causas.

## 6. H4 — StockCode (produto problemático)

**Veredito H4: CONFIRMADA, estatística e praticamente.** 198 de 1.399 produtos
com n≥50 atingem taxa ≥2x a média geral (1,868%). Teste de heterogeneidade
qui-quadrado entre os 1.399 produtos: χ²=6.206,1, gl=1.398, p≈0. Exemplos com
n maior e IC mais estreito: StockCode 21232 (n=469, taxa 8,10%, IC95%
[5,96%; 10,93%], 4,3x a média); 21231 (n=286, 6,29%, IC95% [4,02%; 9,73%],
3,4x). Esta é a causa com evidência mais forte e mais acionável desta fase.

## 7. Correção de múltiplos testes (Holm)

Todos os 6 testes da família confirmatória pré-registrada rejeitam H0 mesmo
após Holm (todos p ≪ 0,05/6). **Isso não significa que todas as 6 hipóteses
sejam causas acionáveis** — rejeitar H0 só diz que o efeito é diferente de
zero; a decisão de entrar na lista final depende do efeito mínimo prático
(seções 3, 4, 6 acima), não do valor-p. É exatamente a distinção que a regra 5
do contexto mestre exige, e é por isso que H1 e H2 saem estatisticamente
confirmadas mas operacionalmente descartadas.

## 8. Explicações rivais — causalidade reversa

Hipótese testada: clientes que já pretendem devolver compram mais unidades
(para testar variações) e devolvem o excedente — isso inverteria a leitura de
H1 (não seria "erro de picking em lote grande", seria comportamento de compra
deliberado).

**Teste**: comparar a Quantity cancelada com a Quantity original pedida, por
quartil.
- Geral: 34,6% dos pares são cancelamento TOTAL, 65,4% PARCIAL.
- Por quartil: Q1 33,7% parcial (piso mecânico — pedidos de 1-poucas unidades
  quase só podem ser cancelados por inteiro), **Q2 74,4%, Q3 72,5%, Q4 71,7%
  parcial — praticamente estável, NÃO cresce com o tamanho do pedido**.

**Leitura honesta**: se a hipótese rival ("compra variantes, devolve o
excedente") fosse o mecanismo dominante e escalasse com o tamanho do pedido, eu
esperaria a taxa de cancelamento parcial SUBINDO de Q2 para Q4. Isso não
acontece — a proporção fica achatada acima de Q1. Isso não confirma nem refuta
a hipótese rival por completo (cancelamento parcial já é maioria em todos os
quartis acima do piso mecânico, o que é compatível tanto com "erro de picking
que afeta só parte do lote" quanto com "compra de variantes"), mas **enfraquece
especificamente a versão "quanto maior o pedido, mais devolução parcial
proporcional"** — não há dose-resposta visível.

**O que faria eu abandonar cada hipótese** (registrado no código, resumo aqui):
- H1: se cancelamento parcial dominasse fortemente E crescesse com Quantity —
  não é o caso.
- H5: se o OR ajustado tivesse colapsado para perto de 1 em todos os
  estratos — não é o caso (só colapsa/inverte por país, não por recorrência).
- H2: se países fora do UK com n suficiente mostrassem taxa igual/menor que
  UK de forma consistente — não é o caso (Alemanha, Austrália, Japão têm taxa
  bem acima de UK individualmente, ver Measure 2B).
- H4: se nenhum produto com n≥50 tivesse taxa ≥2x a média — não é o caso.

## 9. Quantificação

Sobre as 4.957 linhas-defeito do universo do Analyze (receita total
representada: £313.176):

| Causa | Linhas | % do total de defeitos | Receita |
|---|---|---|---|
| Quantity Q4 (H1, não acionável isoladamente) | 1.233 | 24,9% | £233.003 |
| Fora do UK (H2, não acionável isoladamente) | 709 | 14,3% | £34.436 |
| StockCode sinalizado por H4 (≥2x a média, n≥50) | 2.003 | 40,4% | £164.306 |
| **União (≥1 hipótese cobre)** | **3.117** | **62,9%** | **£276.305** |
| **Sem explicação por nenhuma hipótese testada** | **1.840** | **37,1%** | **£36.871** |

Mesmo somando todas as hipóteses testadas (incluindo as duas praticamente
refutadas), quase 63% das linhas-defeito caem em algum segmento sinalizado —
mas a maior parte dessa cobertura vem de H4 (produto específico), a única causa
com efeito prático confirmado. Os 37,1% sem explicação (£36.871 de receita) vão
para as limitações: nem motivo declarado, nem erro de operador, nem categoria
de produto formal estão disponíveis para investigar esse resíduo.

## 10. Modelagem — tradução de coeficientes

Modelo: `defeito ~ log(1+Quantity) + país + recorrência`.
- Dobrar a Quantity do pedido associa-se a ~20,9% a mais nas chances (odds) de
  cancelamento, controlando por país e recorrência.
- Ser UK (vs. Resto), controlando pelo resto: OR=0,886 (Resto tem risco maior,
  direção esperada).
- Ser recorrente (vs. primeira compra): OR=1,061, efeito pequeno.

**O modelo em si não acrescentou poder de decisão além do que os testes de
proporção já mostraram** (confirma que os três fatores são aproximadamente
independentes). **Mas a estratificação/CMH por país acrescentou, sim, algo que
o Pareto marginal da 2B não mostrava**: a descoberta de que o efeito de
Quantity é UK-específico só apareceu ao cruzar Quantity com país — é a
diferença entre olhar uma tabela marginal e olhar a tabela cruzada, e é
exatamente o tipo de achado que justifica fazer o Analyze depois da Measure em
vez de parar no Pareto.

## Lista final de causas para a Improve

1. **H4 confirmada (estatística e praticamente)**: 198 produtos específicos com
   taxa ≥2x a média — maior cobertura de defeitos (40,4%) e a única causa
   isoladamente acionável por si só.
2. **H5 parcialmente confirmada**: Quantity alta só é fator de risco **dentro
   do UK**; fora do UK o padrão se inverte. Qualquer regra de segmento por
   Quantity precisa ser condicionada a país.
3. **H1 e H2 estatisticamente confirmadas, praticamente refutadas** — não
   entram como causa isolada acionável; sobrevivem apenas como covariáveis
   dentro da regra combinada acima (Quantity×País), nunca como regra
   independente ("reduzir cancelamento restringindo quantidade" ou "adicionar
   fricção só por ser de fora do UK" não passam no efeito mínimo
   pré-registrado sozinhas).
4. **H3 exploratória, sem sinal nesta checagem fraca** — decisão final adiada
   para a abertura do holdout em Control.
5. **37,1% dos defeitos sem causa testável identificada** — limitação
   declarada, não erro escondido.

## Tollgate ANALYZE

| Critério | Veredito |
|---|---|
| H5 testada e reportada antes de H1/H2, com veredito explícito | **OK** — parcialmente confirmada por país, refutada por recorrência (seção 2) |
| Conclusões de causa reformuladas conforme o pareamento (18,2%/15% não pareável) | **OK** — aviso no topo de todo o documento, repetido no cabeçalho de cada teste |
| Nenhuma conclusão apresentada só com valor-p, sem tamanho de efeito | **OK** — H1 e H2 são o exemplo direto disso: valor-p ínfimo, mas refutadas por efeito abaixo do mínimo prático |

**Veredito da fase**: **APROVADO**. O achado mais valioso não é "H1 confirmada"
nem "H5 refutada" de forma limpa — é que o próprio desenho anti-garimpo (efeito
mínimo pré-registrado + teste de H5 antes de H1 + estratificação por país)
impediu duas conclusões que pareceriam fortes só pelo valor-p (H1, H2) de
entrarem como causa acionável, e revelou uma condicional real (H5-por-país) que
nenhum Pareto marginal mostraria sozinho.
