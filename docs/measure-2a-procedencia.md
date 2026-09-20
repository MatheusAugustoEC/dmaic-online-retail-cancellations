# FASE 2A — MEASURE · Procedência e qualidade do dado

Data: 2026-09-20. Código: `src/fase2a_msa_procedencia.py`. Auditoria de
procedência de registro histórico fixo — não há sistema/operador vivo para
recalibrar; as seis dimensões avaliam o dado como ele está, não um instrumento
de medição em uso.

## 1. Perfil

- Chave candidata (InvoiceNo, StockCode) **não é única**: 20.378 linhas (3,76%)
  compartilham uma combinação (InvoiceNo, StockCode) com outra linha. Isso não é
  erro por si — ver Unicidade abaixo, é lançamento retificado ou item duplicado no
  carrinho.
- Combinações únicas de (InvoiceNo, StockCode): 531.225.
- InvoiceNo únicos: 25.900. StockCode únicos: 4.070. CustomerID únicos: 4.372.
- InvoiceNo com prefixo "C": 9.288 [DADO, confirma a Fase 0].

## 2. Auditoria das seis dimensões

### Completude
- `CustomerID` nulo: 135.080 (24,93%). Concentração confirmada por Country: Hong
  Kong 100%, Unspecified 45,3%, **UK 27,0%** vs. não-UK (exceto HK) ≈3,2% — o
  mesmo padrão já visto na Fase 0. Por mês, o nulo acompanha grosso modo o volume
  total (pico em nov/2011 com 19.113), sem mês fora do padrão proporcional.
- `Description` nula: 1.454 (0,27%) — dentro do critério de aceite (<1%).
- **Veredito: APROVADO com ressalva** — completude é parcial e sistematicamente
  desigual por país (não aleatória), o que já foi absorvido no Define como
  limitação de cobertura do pareamento, não como falha nova.

### Unicidade
- 10.147 linhas (1,87%) são duplicata exata (todas as colunas iguais), em 4.879
  grupos. Decisão: tratar como lançamento repetido do mesmo evento, não como dois
  eventos novos — mas **não removo automaticamente** sem regra declarada, porque
  não há como confirmar se é erro de sistema (linha gravada duas vezes) ou compra
  legítima do mesmo item duas vezes na mesma fatura com atributos idênticos.
  Fica registrado como decisão pendente para a 2B: se o baseline for sensível a
  isso, dedupe explícito e declarado.
- 5.084 combinações (InvoiceNo, StockCode) têm Quantity divergente entre linhas —
  candidato a retificação (ex.: lançou 5, corrigiu para 3), não erro de
  unicidade. Não removido.
- **Veredito: APROVADO com decisão pendente** (dedupe de exatas, ver acima).

### Validade
- `Quantity == 0`: 0 linhas — aprovado sem ressalva.
- `UnitPrice <= 0`: 2.517 linhas. Composição: 20 são código não-produto (esperado
  — ajuste/taxa). **2.497 são StockCode de produto real com preço ≤0** — achado
  novo, tratado à parte abaixo (seção 2.1).
- `InvoiceDate` fora do intervalo plausível (2010-01-01 a 2012-01-01): 0 linhas.
- Grafia de `Country`: lista de 38 valores inspecionada visualmente — nenhuma
  variante duplicada de mesmo país (ex.: não há "Eire" e "EIRE" ao mesmo tempo).
  "Unspecified" e "European Community" são valores válidos de baixo volume, não
  erro de grafia.
- **Veredito: APROVADO com achado novo** (seção 2.1).

### Consistência
- 650 de 3.958 StockCodes (16,42%) têm mais de uma `Description` distinta — até 8
  variantes em um único código. Indício de digitação livre, não catálogo
  controlado. Ação: normalizar (lower/strip, ou mapear para a Description mais
  frequente por StockCode) antes de qualquer rotulagem de produto no Analyze.
- 8 de 4.372 CustomerID (0,18%) aparecem com mais de um `Country` — volume baixo,
  não distorce estratificação por país.
- **Veredito: APROVADO com ação declarada** (normalização de Description).

### Acurácia
- Não há fonte externa linha a linha para conferir. **Declarado, não simulado**:
  nenhum teste de acurácia real é possível aqui. Fica registrado como limitação
  estrutural, não como dimensão "aprovada" por omissão.

### Pontualidade
- Cobertura mensal: 13 meses, dez/2010 (42.481) a dez/2011 (25.525, mês mais
  curto — 9 dias, corte de coleta já confirmado na Fase 0, não queda de negócio).
- 43 InvoiceNo (0,166%) têm mais de um `InvoiceDate` distinto entre suas próprias
  linhas — uma fatura sendo "aberta" em momentos ligeiramente diferentes para
  linhas diferentes. Volume baixo, não compromete a janela mensal usada no
  Define.
- **Veredito: APROVADO.**

## 2.1 — Achado novo: linhas de produto real com preço ≤0 (investigado além do Insumo pedido, por ter emergido da Validade)

Das 2.497 linhas com StockCode de produto real e UnitPrice≤0:
- 2.464 (98,7%) têm CustomerID nulo.
- As 1.446 sem Description também têm CustomerID nulo em 100% dos casos.
- 1.336 têm Quantity negativa — e essas 1.336 são **exatamente** as linhas
  "Quantity<0 sem prefixo C" já contadas na Fase 0 (interseção = 1.336/1.336).
- Nenhuma dessas 2.497 linhas tem prefixo "C".

[INFERÊNCIA, confiança média-alta] Este conjunto tem assinatura de **ajuste
interno de estoque lançado sobre StockCode de produto real** (baixa, quebra,
correção de inventário) — não de venda nem de devolução de cliente. Já não conta
como "cancelamento" na definição operacional do Define (exige prefixo "C"), mas
**ainda não havia decisão sobre se essas linhas devem contar no denominador de
"pedidos/linhas válidas"** usado nos guardrails (volume total, receita bruta).

**Proposta de decisão para a 2B**: excluir linhas com `UnitPrice<=0 AND
CustomerID nulo` do universo de pedidos válidos (numerador e denominador),
mantendo-as documentadas à parte como "ajustes de estoque", com o mesmo
tratamento dado aos StockCodes não-produto. Não decido isso unilateralmente aqui
porque muda o denominador do baseline (Measure 2B) — fica como item a confirmar
antes de congelar o baseline.

## 3. Teste de artificialidade

- `Quantity`: média 9,55, desvio 218 (cauda longuíssima, min -80.995, max
  80.995) — plausível para base com clientes revendedores comprando/devolvendo
  lotes grandes.
- `UnitPrice`: média £4,61, desvio £96,76 (min -£11.062,06 do StockCode "B",
  ajuste contábil já identificado; max £38.970,00 do StockCode "M", lançamento
  manual) — cauda longa real, não artificial.
- Lei de Benford no primeiro dígito de |UnitPrice×Quantity|: dígito 1 observado
  38,98% vs. esperado 30,10%; dígito 2 15,83% vs. 17,61%; resto com desvios
  moderados. **Desvio esperado e não alarmante**: preços de varejo se concentram
  em pontos redondos (£1,25; £2,08; £4,13 nos quartis) e valores baixos
  dominam o catálogo (mediana £2,08), o que empurra o primeiro dígito para "1"
  mais do que Benford prevê em dados sem esse padrão de precificação. Não reabro
  a suspeita de dado sintético — a sujeira estrutural (Description inconsistente,
  StockCodes não-produto, ajustes de estoque) já é assinatura de dado real muito
  mais forte que qualquer leitura de Benford.

## 4. Vieses

- **Seleção**: confirmado, não há carrinhos abandonados nem tentativas
  rejeitadas — só pedidos registrados existem no dado.
- **Sobrevivência**: confirmado, CustomerID só existe após compra completa;
  clientes que desistiram antes da primeira compra são invisíveis.
- **Vazamento**: reconfirmado o desenho da regra de pareamento da Fase 0 — usa
  exclusivamente `InvoiceDate` do pedido original **anterior** à do
  cancelamento. Nenhum preditor do Analyze pode vir de Quantity negativo ou do
  próprio InvoiceNo "C" (regra específica do projeto), e o código desta fase não
  usa nenhuma dessas colunas como feature.
- Cobertura do pareamento (herdada da Fase 0, reconfirmada): 1.689 de 9.288
  cancelamentos (18,18%) não pareáveis — 383 por CustomerID nulo, 1.306 por
  ausência de pedido original compatível.

## 5. Erro indetectável

Não é possível, só com estas colunas, saber se um cancelamento foi iniciativa do
cliente ou anulação por erro do próprio varejista, nem se o UnitPrice
efetivamente cobrado divergiu do registrado (desconto verbal, erro de sistema).
Vai para as limitações do README (Control).

## 6. Veredito fit-for-purpose

A base sustenta bem a pergunta de **priorização de segmento** — "onde e para
quem a taxa de cancelamento pareável é maior" — de forma descritiva e
estratificada. **Não sustenta**:
- "Por que o cliente cancelou" no nível de motivo declarado (não existe no
  dado).
- "Quanto custou cada devolução" (sem custo de frete reverso/reposição).
- Qualquer alegação de causa individual fina por pedido.

Isso é limitação declarada, não falha do projeto — a pergunta central pré-
registrada no Define já foi desenhada dentro do que a base sustenta.

## Tollgate MEASURE 2A

| Critério | Veredito |
|---|---|
| Seis dimensões rodadas com código | **OK** — `src/fase2a_msa_procedencia.py` |
| Taxa de pareamento confirmada estável para sustentar o Analyze | **OK** — 81,82% reconfirmado nesta fase, sem mudança |
| Lista de StockCodes não-produto fechada e documentada | **OK** — herdada da Fase 0, sem alteração |

**Novo item pendente antes de congelar o baseline (2B)**: decidir e documentar o
tratamento de linhas `UnitPrice<=0 AND CustomerID nulo` em StockCode de produto
real (seção 2.1) — proposta de exclusão do universo de pedidos válidos, a
confirmar.

**Veredito da fase**: **APROVADO COM RESSALVA** — a ressalva é o item de
tratamento das 2.497 linhas de ajuste de estoque, que precisa ser fechada antes
do congelamento do baseline na 2B (não bloqueia a auditoria em si, que já rodou
completa).
