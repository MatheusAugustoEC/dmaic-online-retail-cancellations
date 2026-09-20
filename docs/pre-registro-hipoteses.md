# PRÉ-REGISTRO DE HIPÓTESES — Cancelamento/Devolução, Online Retail (UCI)

**ARTEFATO IMUTÁVEL.** Correção é adendo datado ao final deste arquivo, nunca
edição das seções abaixo. Se algo aqui estiver errado, o projeto para e o
responsável é avisado antes de qualquer correção.

Data de registro: **2026-09-20**
Registrado antes de qualquer teste de relação entre variáveis (Fase Analyze).
Origem: derivadas por inspeção estrutural da Fase 0 (contagens, distribuições) e,
no caso de H3, por teoria de domínio (sazonalidade de varejo é conhecimento de
domínio geral, não olhado nos dados desta base antes de escrever a hipótese) —
rotuladas individualmente abaixo, conforme regra 3 (ANTI-GARIMPO) do contexto
mestre.

## Unidade e janela

- Unidade do defeito: **linha** (InvoiceNo × StockCode), decidido no Define
  (`docs/define-charter.md`, seção 3).
- Janela de exploração (onde as hipóteses são testadas até Control):
  `InvoiceDate < 2011-10-01`.
- Holdout (fechado até Control): `InvoiceDate >= 2011-10-01` até 2011-12-09 12:50.

## Hipóteses

**H1 — [INSPEÇÃO ESTRUTURAL]**
Pedidos com Quantity total alta (típico de compra por revendedor) têm taxa de
cancelamento maior que pedidos de quantidade baixa, por erro de picking/estoque
em lotes grandes.
- Teste planejado: comparação de taxa de cancelamento por quartil de Quantity
  agregada por InvoiceNo.
- Efeito mínimo acionável: diferença de taxa ≥ 3 p.p. entre quartil superior e
  inferior.
- Ordem de teste: DEPOIS de H5 (ver abaixo).

**H2 — [INSPEÇÃO ESTRUTURAL]**
Pedidos de Country fora do Reino Unido têm taxa de cancelamento maior que UK, por
custo/tempo de frete e alfândega.
- Teste planejado: comparação de proporções UK vs. não-UK. Países com n
  insuficiente (a maioria dos 38) não sustentam teste individual e serão
  agrupados em "UK" vs. "resto"; a lista de países excluídos de teste individual
  será declarada na Measure 2B.
- Efeito mínimo acionável: diferença de taxa ≥ 5 p.p.
- Ordem de teste: DEPOIS de H5.

**H3 — [TEORIA DE DOMÍNIO] — REBAIXADA A EXPLORATÓRIA PRÉ-CONTROL**
Pedidos feitos no pico sazonal (novembro–dezembro) têm taxa de cancelamento maior
que no resto do ano, por erro operacional sob alta carga de separação/embalagem.
- Teste planejado (pré-Control, exploratório): taxa mensal, carta p, dez/2010
  (único mês de alto volume disponível na janela de exploração) como proxy de
  pico — confundido com efeito de lançamento da base, declarado em toda saída.
- Teste confirmatório real: na abertura do holdout em Control, novembro/2011
  genuíno vs. resto — não é mais teste cego, mas ainda valida generalização.
- Efeito mínimo acionável: diferença de taxa ≥ 2 p.p. entre pico e não-pico.
- Motivo do rebaixamento: holdout (out–dez/2011) contém o único pico sazonal
  real da base; ver `docs/define-charter.md`, seção 6.
- Não entra na correção de múltiplos testes da família confirmatória pré-Control.

**H4 — [INSPEÇÃO ESTRUTURAL]**
Certos StockCodes concentram taxa de cancelamento muito acima da média do
catálogo (produto problemático).
- Teste planejado: Pareto de taxa de cancelamento por StockCode, com corte
  mínimo de n por produto (a definir na 2B com base no poder disponível) para
  entrar no ranking.
- Efeito mínimo acionável: produtos no top do Pareto com taxa ≥ 2x a média geral.
- Ordem de teste: junto com H1/H2, depois de H5.

**H5 — RIVAL ESTRUTURAL de H1 e H2 — [INSPEÇÃO ESTRUTURAL] — TESTADA PRIMEIRO**
O efeito "quantidade alta → mais cancelamento" (H1) é artefato de composição:
pedidos de quantidade alta se concentram em poucos CustomerID (grandes
revendedores) e/ou em países específicos que já têm taxa de cancelamento
estruturalmente maior por outro motivo. Alternativa de seleção: clientes em sua
primeira compra registrada cancelam mais, independentemente de quantidade, e
quantidade alta correlaciona com primeira compra.
- Teste planejado: efeito de Quantity dentro de estratos de CustomerID (cliente
  recorrente vs. primeira compra) e de Country. Verificação de paradoxo de
  Simpson entre o efeito agregado e o efeito estratificado.
- Critério de veredito: se o efeito de H1 sumir ou inverter dentro dos estratos,
  H5 confirma composição/seleção, não causa direta de Quantity.
- **Esta hipótese é testada ANTES de H1 e H2, não depois.**

## Correção de múltiplos testes

Família confirmatória pré-Control: {H5 (incluindo subtestes de estratificação por
CustomerID e por Country), H1, H2, H4} — 4 hipóteses principais. Método: Holm,
aplicado sobre o conjunto de p-valores desta família. H3 fica fora da família
(ver justificativa acima) e é tratada como exploratória até a checagem em
Control.

## Efeito mínimo prático

Cada hipótese só é considerada "confirmada com relevância prática" se o efeito
observado atingir o mínimo declarado acima, mesmo que o valor-p seja
significativo — valor-p sozinho não move nenhuma hipótese para a lista de causas
validadas do Analyze.

---

*(Nenhum adendo registrado até o momento.)*
