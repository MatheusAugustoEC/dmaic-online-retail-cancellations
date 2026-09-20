# FASE 2B — MEASURE · Baseline, estabilidade e capabilidade

Data: 2026-09-20. Código: `src/fase2b_baseline.py`. Gráficos: `reports/2b_*.png`.
Baseline congelado: `docs/baseline_congelado.json` (**ARTEFATO IMUTÁVEL a partir
de agora** — correção futura só como adendo datado, nunca edição do JSON).
Holdout (`InvoiceDate >= 2011-10-01`) nunca foi carregado em nenhuma variável
deste script — a guarda está no próprio código (primeira linha após a leitura).

## 0. Fechamento da pendência da Measure 2A

Decisão fechada nesta fase: excluir do universo de "pedidos válidos" toda linha
de StockCode de produto real com `UnitPrice<=0`, **independente de CustomerID**
(estende a proposta da 2A, que só cobria os casos com CustomerID nulo, para
cobrir também os 33 casos com CustomerID presente e preço zerado/negativo — é
uma linha melhor definida: preço não-positivo em produto real não é venda,
ponto final). Na janela de exploração isso removeu 1.946 linhas.

**Universo final do baseline**: 265.427 linhas de pedido original (produto
real, `UnitPrice>0`, `CustomerID` presente, `InvoiceDate < 2011-10-01`).

## Pareamento linha-a-linha (extensão do teste da Fase 0 ao nível de linha individual)

Na janela de exploração: 6.086 cancelamentos com CustomerID disponíveis para
pareamento; 5.176 pareados a uma linha original específica (nearest preceding
order); 910 órfãos dentro da própria janela. 4.957 linhas originais receberam
ao menos um cancelamento pareado.

**Lag entre pedido original e cancelamento pareado**: mediana 8,9 dias, 79,4%
em até 30 dias, 90,2% em até 60 dias, 93,9% em até 90 dias.

**Aviso de censura à direita, achado desta fase**: um pedido de setembro só
conta como defeito aqui se o cancelamento correspondente TAMBÉM ocorreu antes de
01/10/2011. Qualquer cancelamento que caia no holdout é invisível por desenho.
Como 90%+ dos cancelamentos pareados acontecem em até 60 dias, meses a mais de
60-90 dias do corte (até ~jul/2011) sofrem pouco; **agosto e principalmente
setembro/2011 sofrem censura relevante** — é exatamente o que aparece na carta
(seção 2). Não corrijo isso olhando o holdout (proibido); documento e ajusto o
cálculo de capabilidade para não herdar o viés (seção 3).

## 1. Baseline

- **Taxa de cancelamento (linha, pareável, toda a janela de exploração)**:
  **1,868%** — IC 95% Wilson [1,817%; 1,920%] — n=265.427, defeitos=4.957.
- DPMO: 18.676. Nível sigma de longo prazo (sem deslocamento): **2,08σ**; com a
  convenção de deslocamento de 1,5σ: 3,58σ.
- `Quantity` por linha (universo do baseline): mediana 6, P25=2, P75=12, cauda
  longa até 74.215 (revendedor). `UnitPrice` por linha: mediana £1,95, P25=£1,25,
  P75=£3,75, cauda até £649,50. Histogramas com outlier (p99) marcado em
  `reports/2b_histogramas_quantity_unitprice.png`.

## 2. Estabilidade — carta p mensal

10 pontos (dez/2010 a set/2011) — **abaixo do mínimo de ~20 citado na
metodologia**. Alternativa semanal avaliada: 43 semanas (mais perto do mínimo),
mas n por semana varia de 1.765 a 10.768 (mediana 6.116) — limites muito mais
instáveis semana a semana; mantenho a mensal como carta oficial e cito a semanal
só como checagem de robustez, não substituição.

Gráfico: `reports/2b_carta_p_mensal.png`.

**Resultado bruto**: 5 de 10 pontos cruzam os limites de 3σ. Antes de rotular
isso como "5 causas especiais", classifico caso a caso — é o que a regra 6 do
contexto mestre pede:

| Mês | p | Situação | Classificação |
|---|---|---|---|
| set/2011 | 0,86% (abaixo do LCL) | mês mais próximo do corte do holdout | **Causa ESPECIAL, mas de ARTEFATO DE MEDIÇÃO** (censura à direita), não do processo real — excluído da leitura de capabilidade |
| jan, fev, mar, mai/2011 | 2,12%–2,30% (acima do UCL) | breach estatístico real, magnitude pequena (~1–2 p.p. acima do centro de 20,3‰) | Estatisticamente fora de controle — com n mensal >19.000 os limites de 3σ ficam muito estreitos (~±0,08 p.p.), então a carta é hipersensível a desvios pequenos. Não descarto como ruído, mas também não afirmo causa especial confirmada sem teste — fica registrado como **pista para o Analyze** (jan logo após o pico de fim de ano é compatível com hipótese de domínio plausível de devolução pós-Natal, mas isso é [PREMISSA], não testado aqui — testar é cruzamento de variável, proibido na Measure) |
| dez, abr, jun, jul, ago/2011 | dentro dos limites | — | Causa comum |

Maior sequência de pontos consecutivos do mesmo lado da linha central: 8 (perto
do limiar de 9 da regra de Nelson 2, mas não o atinge).

**Justificativa carta p vs. I-MR**: I-MR serve a medida contínua individual
(Quantity/UnitPrice médio por período); aqui o defeito é atributo binário com n
variável mês a mês — carta p é a escolha correta.

**Consequência prática**: não posso dizer honestamente "tudo é causa comum" (a
tabela acima mostra pelo menos um artefato e um bloco de pontos com breach
pequeno mas real). Mas também não há um mês isolado de causa especial genuína e
grande o suficiente para justificar meta mensal cobrada da operação — a
resposta estrutural (checkout, verificação por segmento) continua sendo a via
correta; o padrão jan-mar/mai vira item de investigação no Analyze, não uma
meta a bater mês a mês.

## 3. Capabilidade

**Setembro/2011 excluído do cálculo de capabilidade** (seu p de 0,86% é
artefato de censura, não do processo — ver seção 2). Usar a janela inteira
contaminaria tanto a taxa pooled quanto a própria meta (um quantil das taxas
mensais) com o mesmo viés — na prática, incluir setembro sem correção inverteria
o sinal do gap (taxa pooled cairia para 1,868% e a meta p25 para 1,914%,
fazendo parecer que a base já bate a meta, o que é um artefato, não realidade).

- **Taxa pooled, janela madura (dez/2010–ago/2011, 9 meses)**: **2,046%**
  (n=225.558, defeitos=4.614).
- **Meta interna proposta (melhor quartil histórico das taxas mensais, P25,
  janela madura)**: **1,991%** — [PROPOSTA INTERNA, não referência de mercado,
  conforme decidido no Define].
- **Gap**: 0,0545 p.p.
- **Tradução de negócio**: se a meta interna fosse atingida em todos os meses,
  cerca de **14 linhas de pedido a mais por mês** ficariam "conformes"
  (não-canceladas), na média da janela madura — um gap pequeno em termos
  absolutos frente às ~25.062 linhas/mês, o que já é uma pista de que a maior
  alavanca provavelmente está concentrada em segmentos específicos (seção 4),
  não numa mudança geral de processo.

## 4. Estratificação e Pareto

Tabelas completas no output do script; resumo abaixo. Gráfico:
`reports/2b_paretos.png`.

**Por Country** (limiar n≥100 para entrar no ranking individual — 10 de 36
países abaixo disso, listados na seção 5): UK 1,80% (n=235.761), Resto agrupado
2,39% (n=29.666). Entre os países com n suficiente, os piores são Japão (9,52%,
n=273), Austrália (6,73%, n=1.026) e Alemanha (4,37%, n=6.085) — todos bem acima
de UK.

**Por faixa de Quantity (quartil, nível de linha)**: Q4 (maior) 2,67% vs. Q1
(menor) 1,16% — diferença de 1,5 p.p., na direção prevista por H1, mas isso é só
descrição estratificada aqui, o teste formal de H1 (e principalmente de H5, a
rival) é do Analyze.

**Por StockCode (n≥50)**: 1.399 de 3.502 produtos sustentam ranking individual.
Os piores (ex. 22198 a 20,75% com n=53) chegam a mais de 10x a taxa geral —
candidatos fortes para H4, com corte de n declarado.

**Por recorrência de cliente**: Recorrente 1,92% vs. Primeira compra 1,75% —
diferença pequena e na direção OPOSTA à hipótese informal de "cliente novo
cancela mais" mencionada no memorando da Fase 0. Fica registrado como
observação descritiva; não é teste de H5.

**Pareto por TAXA (top 10, n suficiente)**: dominado por StockCodes individuais
(22198, 21258, 75049L, 23111, 22891...), todos entre 12,9% e 20,8% — o segmento
de maior risco proporcional é produto específico, não país nem faixa de
quantidade.

**Pareto por IMPACTO ABSOLUTO (corte de 80%)**: UK sozinho já responde por
85,7% do total de linhas canceladas (4.248 de 4.957) — simplesmente porque UK é
91% do volume da base. Isso não é achado de causa, é aritmética de volume.

**Os dois Paretos NÃO apontam o mesmo segmento**: o de taxa aponta produtos
específicos de nicho (alto risco proporcional, baixo volume); o de impacto
aponta UK e as faixas de Quantity médias (Q2/Q3) simplesmente por serem onde
está o volume. **Qual orienta a Improve**: nenhum dos dois sozinho — o Pareto de
taxa aponta ONDE intervir com precisão cirúrgica (produtos/segmentos de risco
concentrado) sem afetar o volume principal; o de impacto aponta que qualquer
ganho, para ser relevante em receita absoluta, precisa também mexer em algo
dentro de UK (mesmo que a taxa de UK seja baixa, é onde está o volume). A
Improve deve cruzar os dois: priorizar segmentos de alta taxa DENTRO de UK, não
tratar os dois Paretos como recomendações concorrentes.

## 5. Tamanho de amostra e poder

10 de 36 países têm n<100 e não sustentam teste individual: Czech Republic,
Saudi Arabia, Malta, European Community, Bahrain, Brazil, Lithuania, Lebanon,
USA, United Arab Emirates — todos vão para o agrupamento "Resto" no teste de H2.

Poder disponível (alfa ajustado por Holm, família de 4 testes confirmatórios):
- H1 (Quantity Q1 n=82.222 vs. Q4 n=46.176, efeito mínimo 3 p.p.): **poder
  ≈100%**.
- H2 (UK n=235.761 vs. Resto n=29.666, efeito mínimo 5 p.p.): **poder ≈100%**.
- H4 (StockCode): 1.399 de 3.502 produtos com n≥50 sustentam comparação
  individual; os 2.103 restantes ficam fora do Pareto de H4 por falta de poder.

Com n desta magnitude, poder não é o fator limitante do Analyze — o fator
limitante é a robustez da regra de pareamento (18,2% não pareável) e a
composição/seleção que H5 vai investigar.

## 6. Código e gráficos

- `reports/2b_histogramas_quantity_unitprice.png`
- `reports/2b_carta_p_mensal.png`
- `reports/2b_paretos.png`

## 7. Congelamento do baseline

Ver `docs/baseline_congelado.json` — inclui unidade, janela, filtros aplicados,
taxa, IC, DPMO, sigma, meta interna (janela madura) e a limitação de censura à
direita documentada explicitamente no próprio arquivo.

## Tollgate MEASURE 2B

| Critério | Veredito |
|---|---|
| Carta de controle rodada com agregação declarada e justificada, nº de pontos citado | **OK** — mensal (10 pontos, abaixo do mínimo de ~20, declarado), semanal avaliada e descartada como oficial |
| Os dois Paretos comparados lado a lado, não só um | **OK** — seção 4, com veredito explícito de que não coincidem e como a Improve deve cruzá-los |
| Baseline congelado como artefato imutável, com todos os filtros listados | **OK** — `docs/baseline_congelado.json` |

**Veredito da fase**: **APROVADO COM RESSALVA**. A ressalva é metodológica, não
um buraco: (1) a carta tem um ponto de artefato de medição (set/2011) que exige
leitura cuidadosa, não a conclusão automática de "sem causa especial"; (2) o
bloco jan-mar/mai com breach estatístico pequeno fica registrado como pista
para o Analyze, não testado agora. Nenhum dos dois invalida o baseline
congelado, mas ambos devem ser citados quando esse baseline for referenciado
mais adiante.
