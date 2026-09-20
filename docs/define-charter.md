# FASE 1 — DEFINE · Charter

Data de fechamento: 2026-09-20
Base: memorando da Fase 0 (tollgate APROVADO COM RESSALVA — granularidade fechada abaixo).

## Pergunta escolhida

Onde e por que os pedidos deste varejista são cancelados/devolvidos, e qual mudança
(em segmento de cliente, produto, país ou faixa de quantidade) reduziria a taxa de
cancelamento sem sacrificar o volume de vendas atendido.

## 1. Persona de decisão

**Escolhida**: Gerente de Operações/Atendimento ao Cliente. [PREMISSA DECLARADA]
- Alavanca: decide, por segmento (país, faixa de Quantity, categoria de produto),
  se adiciona uma etapa de verificação prévia (confirmação por e-mail/telefone antes
  de despachar) ou mantém o checkout sem fricção.
- Cadência: revisão semanal do volume de pedidos da semana.
- Regra de decisão assumida: se a taxa de cancelamento de um segmento estiver
  estruturalmente (causa especial, não ruído) acima da meta, adiciona verificação
  para aquele segmento; se estiver dentro, mantém frictionless.

**Frase de honestidade (vai para o README)**: "Este stakeholder é simulado; as
premissas sobre sua alçada e seus incentivos estão registradas neste Define, não
confirmadas com nenhuma pessoa real."

**Persona alternativa avaliada**: Gerente Comercial decidindo termos de conta
(ex.: exigir cadastro completo, alterar condições de pagamento) para clientes de
alto volume/possíveis revendedores com alta taxa de cancelamento.

**Por que escolhi a primeira e não a segunda**: a pergunta central pré-registrada
é sobre onde/por que o cancelamento acontece e que mudança de processo o reduz —
isso é alavanca operacional (checkout, verificação), não alavanca comercial
(condição contratual). A persona Comercial fica mais bem enquadrada como
desdobramento da Improve *se e somente se* H5 confirmar que o efeito é de
composição de cliente (grandes revendedores, não quantidade em si) — nesse caso a
pergunta 3 do memorando da Fase 0 ("vale diferenciar termos de conta para clientes
de alto volume") se torna relevante como recomendação secundária, não como
pergunta central deste ciclo. Registrado aqui para não perder o fio quando o
Analyze chegar ao veredito de H5.

## 2. Problema em uma frase

"Em pedidos no nível de LINHA (InvoiceNo × StockCode, StockCode de produto real,
CustomerID presente — ver definição operacional abaixo) da janela de exploração
(dez/2010 a set/2011; holdout out/2011–dez/2011 reservado, ver seção 6), a taxa de
cancelamento/devolução pareável está em **<a medir na Fase 2B>** quando a meta é
**<proposta interna: melhor quartil histórico de taxa de cancelamento entre
países/meses com n suficiente, a calcular na 2B — é proposta, não referência de
mercado>**, representando **<a quantificar na 2B/Analyze: nº de linhas e receita
(UnitPrice × Quantity) afetadas>** por mês."

**Sobre a meta** [DADO + INFERÊNCIA]: a busca de benchmark externo (Gemba
documental, Fase 0) encontrou apenas faixa genérica de e-commerce B2C
(2–8%, líderes <2,5%) — nenhum benchmark dedicado a atacado B2B de giftware. Essa
faixa genérica **não será usada como meta** porque a base deste projeto mistura
consumidor final e revendedor (comportamento de cancelamento provavelmente
diferente), o que a torna um comparável fraco. A meta operacional será interna
(melhor quartil histórico observado nos próprios dados, medido na 2B) e será
rotulada em todo lugar como proposta interna, nunca como referência de mercado.

## 3. Definição operacional do defeito e métrica primária

**Unidade — DECISÃO FECHADA**: **linha** (InvoiceNo × StockCode). Não fica em
aberto para depois.

Motivo: (a) é a granularidade nativa do dado — qualquer agregação por pedido é
construção minha, não fato do dado; (b) resolve de graça o caso de borda de
cancelamento parcial (cada linha recebe seu próprio rótulo defeito=1/0, sem
precisar decidir se um pedido "meio cancelado" conta inteiro ou não); (c) H4
(StockCode problemático) exige granularidade de linha por definição.
Custo aceito: a leitura de negócio "quantos pedidos foram cancelados" fica em
segundo plano. Mitigação: reporto também, como **métrica secundária de
enquadramento** (não como defeito primário), o % de InvoiceNo com pelo menos uma
linha cancelada pareada — só para dar leitura de negócio ao leitor do README, sem
que nenhuma hipótese seja testada nela.

**O que conta como defeito (linha cancelada)**:
- Linha original (StockCode de produto real, CustomerID presente) que tem uma
  fatura "C" pareada sob a regra validada na Fase 0 (mesmo CustomerID + StockCode,
  InvoiceDate do cancelamento posterior à do pedido original, casamento com o
  pedido original mais próximo no passado).

**O que NÃO conta**:
- Qualquer linha com StockCode não-produto: POST, DOT, M, C2, D, S, BANK CHARGES,
  CRUK, B, PADS, `gift_0001_*` (vale-presente) — lista fechada na Fase 0.
- Linhas de cancelamento (InvoiceNo "C") que não conseguem pareamento (órfãs) —
  entram na análise de viés de cobertura, não no numerador do defeito.

**Janela**: mês de InvoiceDate do pedido ORIGINAL (não do cancelamento) — é o mês
em que o pedido nasceu que define a que período o defeito pertence, para não
inflar artificialmente meses de baixo volume de vendas com cancelamentos que
vieram de pedidos de meses anteriores.

**Casos de borda resolvidos pela escolha de unidade**:
- Cancelamento parcial de pedido de múltiplas linhas: deixa de ser ambíguo — cada
  linha é julgada por si.
- CustomerID nulo no pedido original: torna a linha estruturalmente não-pareável;
  fica fora do numerador pareável e entra como limitação de cobertura (Fase 0:
  14,1% dos cancelamentos com CustomerID presente ficam órfãos por falta de pedido
  original compatível; mais 4,1% têm CustomerID nulo).
- Cancelamento sem par original encontrado: mesmo tratamento acima — vira parte da
  amostra não-pareável, declarada como limitação, nunca descartada silenciosamente.

**Ambiguidades remanescentes** (não resolvidas aqui, ficam documentadas):
- A regra de pareamento por (CustomerID, StockCode, data anterior mais próxima)
  não verifica se a Quantity do cancelamento é compatível com a do pedido
  candidato — um cliente que comprou o mesmo produto duas vezes antes de cancelar
  pode ser pareado com o pedido "errado" entre os dois. Fica como limitação de
  precisão do pareamento, não de cobertura.
- Não há como confirmar se um cancelamento foi iniciativa do cliente ou correção
  do próprio varejista (pedido duplicado por engano) — nenhuma hipótese depende
  dessa distinção, mas ela limita a interpretação causal do "porquê".

## 4. Métricas secundárias e guardrails

Armadilha de otimização local: é possível reduzir a taxa de cancelamento apenas
dificultando o checkout ao ponto de afastar clientes legítimos — isso reduz
pedidos totais sem reduzir insatisfação real, e não deve passar como melhoria.

**Guardrails** (acompanhados junto de qualquer recomendação, Improve/Control):
- Volume total de pedidos (contagem de InvoiceNo únicos) por período — não pode
  cair de forma atribuível à mudança.
- Receita bruta (Σ UnitPrice × Quantity de linhas não-canceladas) por período —
  idem.
- Taxa de abandono de checkout: **não mensurável com este dataset** (carrinhos
  abandonados não geram InvoiceNo). Registrado como premissa a validar apenas em
  experimento real (Improve, desenho do experimento), não em dado histórico.

## 5. Hipóteses pré-registradas

Ver artefato imutável separado: `docs/pre-registro-hipoteses.md`, datado e
versionado nesta mesma sessão. Este Define referencia esse arquivo; qualquer
ajuste às hipóteses vai como adendo datado ao FINAL daquele arquivo, nunca por
edição deste aqui ou daquele.

## 6. Anti-garimpo — holdout e correção de múltiplos testes

**Intervalo confirmado na Fase 0**: InvoiceDate mín. 2010-12-01 08:26,
máx. 2011-12-09 12:50 (12 meses e 9 dias — um único ciclo sazonal, não múltiplos
anos; confirmação de estabilidade sazonal é estruturalmente mais fraca do que
seria com vários anos, conforme já previsto no contexto mestre).

**Corte de holdout — DECISÃO FECHADA**: `InvoiceDate >= 2011-10-01 00:00:00`
até a data máxima (2011-12-09 12:50). Isso cobre outubro inteiro, novembro
inteiro (o mês de maior volume da base) e a fração de dezembro presente no
arquivo.
- Janela de exploração: `InvoiceDate < 2011-10-01` → 370.931 linhas (68,4% do
  total).
- Quarentena de holdout: 170.978 linhas (31,6% do total) — proporção de volume
  bem maior que a proporção de tempo (~2,3 de 12,3 meses), porque o holdout
  captura o pico sazonal de novembro. Declarado: prioriza integridade temporal
  (nenhum vazamento do período mais recente) sobre um split 80/20 por volume.

**Consequência declarada para H3 (sazonalidade)**: como novembro (o pico real) cai
inteiro no holdout, a janela de exploração só contém dezembro/2010 como mês de
volume alto comparável — e dezembro/2010 é também o primeiro mês de dados
(possível efeito de lançamento da base/loja, confundido com efeito sazonal
genuíno). Por isso:
- H3 **sai da família confirmatória pré-Control** de correção de múltiplos
  testes. Será tratada como **exploratória** na Measure 2B/Analyze usando
  dez/2010 como proxy fraco de pico, com a confusão declarada em todo lugar que
  aparecer.
- O teste confirmatório real de H3 (novembro genuíno vs. resto) só acontece na
  abertura do holdout em Control — nesse ponto deixa de ser cego, mas ainda serve
  como validação de generalização do padrão sazonal encontrado no Analyze,
  conforme já previsto na Parte B do Control (item 7).

**Família de correção de múltiplos testes pré-Control**: H5, H1, H2, H4 (4 testes
confirmatórios) + subtestes de estratificação de H5 (por CustomerID
novo/recorrente e por Country) contam na mesma família. Método: Holm (menos
conservador que Bonferroni simples, mantém controle de erro família a família,
adequado a 4-6 testes correlacionados). H3 fica fora dessa família, rotulada
exploratória, sem consumir alfa da família confirmatória.

## 7. Escopo

**DENTRO**: cancelamento/devolução de linhas com CustomerID presente e StockCode
de produto real, pareadas sob a regra da Fase 0, na janela de exploração.

**FORA** (inviável pela Fase 0):
- Motivo declarado do cancelamento — não existe no dado.
- Custo de frete reverso/reposição — não existe no dado.
- Qualquer afirmação sobre pedidos abandonados no carrinho — não existe no dado.
- Se o cancelamento foi iniciativa do cliente ou correção do próprio varejista —
  não distinguível.

**Resolvido nesta fase** (estava "a decidir" no template): cancelamento parcial de
pedido de múltiplas linhas não é mais uma decisão pendente — a unidade linha
(seção 3) trata cada linha individualmente, então a pergunta "conta o pedido
inteiro ou só as linhas" não se aplica mais.

## 8. Critério de sucesso

O projeto é válido mesmo que H1–H4 sejam refutadas e reste apenas o veredito de H5
(composição/seleção em vez de causa direta de Quantity/Country). Isso ainda é
descoberta acionável: a alavanca certa passa a ser segmentação de cliente
(recorrência, perfil de revendedor), não política de quantidade mínima por
pedido — e será registrado como achado válido, nunca como fracasso do projeto.
Da mesma forma, se H3 (rebaixada a exploratória) não se sustentar na checagem de
Control, isso é achado metodológico legítimo sobre os limites de um único ano de
dados, não uma falha a esconder.

## Tollgate DEFINE

| Critério | Veredito |
|---|---|
| Meta do Charter com origem citada ou marcada como proposta interna | **OK** — benchmark genérico descartado por não ser comparável; meta declarada como proposta interna a calcular na 2B |
| Hipóteses datadas e versionadas antes de qualquer teste | **OK** — `docs/pre-registro-hipoteses.md`, datado 2026-09-20, commitado nesta sessão |
| H5 marcada para ser testada antes de H1/H2 | **OK** — seção 5 do pré-registro e Analyze (P2-P original) já ordenam isso |
| Granularidade (pedido vs. linha) fechada | **OK** — linha, decisão fechada na seção 3, com métrica de enquadramento por pedido como secundária |

**Veredito da fase**: **APROVADO**. Ressalva herdada da Fase 0 (granularidade) foi
fechada nesta fase. Nova ressalva registrada e absorvida no desenho (H3 rebaixada
a exploratória pré-Control) — não é pendência, é ajuste declarado do escopo
confirmatório.
