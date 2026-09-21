# Cancelamentos e Devoluções — Online Retail (UCI)

Projeto de portfólio conduzido por DMAIC (Lean Seis Sigma), aplicado a um
dataset onde os dados vieram antes da pergunta. Todas as fases, tollgates e
decisões estão versionadas neste repositório, fase por fase, com commit
correspondente.

## Que pergunta este projeto responde

Onde e por que os pedidos deste varejista são cancelados/devolvidos, e qual
mudança (em segmento de cliente, produto, país ou faixa de quantidade)
reduziria a taxa de cancelamento sem sacrificar o volume de vendas atendido.

## A resposta em uma frase

A causa mais robusta e acionável é **produto específico** (um conjunto fechado
de ~195 StockCodes com taxa de cancelamento 2x a 11x a média geral, validado
também no holdout com 3,1x a taxa geral); **quantidade alta do pedido só é
fator de risco dentro do Reino Unido** — fora dele o padrão se inverte — e as
duas hipóteses mais óbvias isoladamente (quantidade alta, país estrangeiro)
são estatisticamente detectáveis mas **abaixo do efeito mínimo prático
pré-registrado**, portanto não entram como recomendação isolada.

## Como rodar do zero

```bash
pip install pandas numpy scipy statsmodels matplotlib pytest pyarrow
python src/fase0_profiling.py
python src/fase0_timeline_e_pareamento.py
python src/fase2a_msa_procedencia.py
python src/fase2b_baseline.py
python src/fase3_analyze.py
python src/fase4_improve.py
python src/fase5_abertura_holdout.py   # NAO RODAR MAIS DE UMA VEZ EM UM PROJETO NOVO — aqui já foi aberto
pytest tests/
```

`online_retail.csv` (UCI Online Retail) precisa estar na raiz do projeto —
não está versionado (`.gitignore`). **Faltando neste checklist**: não há
`requirements.txt`/lockfile de versões nem hash do CSV original — dívida
técnica declarada no Control (`docs/control-plano.md`, item 5).

## Origem e natureza dos dados

UCI Machine Learning Repository, "Online Retail" (Chen, Sain & Guo, 2012),
licença CC BY 4.0. Dado **real** de um varejista britânico de giftware,
dez/2010 a dez/2011 (12 meses e 9 dias — um único ciclo sazonal, não
múltiplos anos). 541.909 linhas, granularidade item-dentro-de-fatura.

**O que o dado NÃO registra, e o que isso proíbe concluir**:
- Motivo declarado do cancelamento → nenhuma causa aqui é "por que o cliente
  cancelou" no sentido de motivo relatado; são todas correlações estruturais.
- Custo de frete reverso/reposição → a simulação de ganho no Improve não
  calcula ROI líquido real, só receita bruta preservada menos fricção
  estimada; por isso o **ponto de indiferença**, não o ganho bruto, é o
  número central da recomendação.
- Se o cancelamento foi iniciativa do cliente ou correção do próprio
  varejista → nenhuma hipótese depende dessa distinção, mas ela limita
  qualquer leitura de "culpa".
- Carrinhos abandonados e tentativas de compra rejeitadas → a "taxa de
  cancelamento" aqui é sobre pedidos que existiram, não sobre conversão.
- Identificador de operador → nenhuma causa de erro humano específico é
  testável.
- Categoria de produto formal → `Description` é texto livre com 16,4% de
  inconsistência por StockCode (Measure 2A); nenhuma categoria foi inventada.

## Decisões metodológicas e por quê

- **Granularidade: linha** (InvoiceNo × StockCode), não pedido — decidido no
  Define. Resolve de graça o caso de cancelamento parcial e é a granularidade
  nativa do dado; métrica por-pedido fica só como leitura secundária.
- **Regra de pareamento cancelamento↔pedido original**: como não existe chave
  de ligação entre uma fatura "C" e o pedido que ela cancela, a ligação foi
  **inferida** por (CustomerID, StockCode, pedido original mais próximo no
  passado). Isso é uma construção do projeto, não um fato do dado, e está
  declarado como tal em toda fase que depende dela.
- **Holdout**: últimos ~2,3 meses (`InvoiceDate >= 2011-10-01`), 31,6% do
  volume (desproporcional ao tempo porque captura o pico de novembro) —
  escolha deliberada de priorizar integridade temporal sobre um split 80/20
  "bonito". Consequência aceita: H3 (sazonalidade) foi rebaixada a
  exploratória porque o único pico real da base cai inteiro no holdout.

## Veredito da armadilha de vazamento por ausência de chave de ligação

Testado na Fase 0 e reconfirmado na Measure 2A/2B/Analyze: **81,8%–85,3%** dos
cancelamentos históricos pareiam a um pedido original sob a regra acima
(a variação entre fases vem de diferentes filtros de escopo aplicados antes
de contar). **Toda conclusão de causa deste projeto vale só para esse
subconjunto pareável — não para o total de cancelamentos observados.** Isso
está repetido no cabeçalho de cada teste do Analyze, não só aqui.

## Premissas do stakeholder simulado

Persona de decisão: Gerente de Operações/Atendimento ao Cliente, decidindo
semanalmente se adiciona verificação prévia a segmentos de risco. **Este
stakeholder é simulado; as premissas sobre sua alçada e seus incentivos estão
registradas no Define (`docs/define-charter.md`), não confirmadas com
nenhuma pessoa real.**

## Resumo por fase (tollgates)

| Fase | Documento | Veredito |
|---|---|---|
| 0 — Reconhecimento | (memorando na conversa, script `src/fase0_*.py`) | Aprovado com ressalva (granularidade fechada no Define) |
| Define | `docs/define-charter.md`, `docs/pre-registro-hipoteses.md` (imutável) | Aprovado |
| Measure 2A | `docs/measure-2a-procedencia.md` | Aprovado com ressalva (fechada na 2B) |
| Measure 2B | `docs/measure-2b-baseline.md`, `docs/baseline_congelado.json` (imutável) | Aprovado com ressalva (leituras de causa comum/artefato documentadas) |
| Analyze | `docs/analyze-causa-raiz.md` | Aprovado |
| Improve | `docs/improve-recomendacao.md` | Aprovado |
| Control | `docs/control-plano.md`, `docs/holdout_resultado.json` (imutável) | Aprovado |

## O que eu faria com acesso ao sistema real de checkout e a dados de motivo de devolução

- Testar a fricção condicionada (UK × Quantity alta) como experimento real
  (desenho já pronto no Improve, seção 4), medindo abandono de checkout de
  verdade em vez de assumir uma taxa.
- Usar o motivo declarado da devolução para separar defeito de produto (frágil,
  descrição errada) de arrependimento de compra — H4 hoje mistura os dois
  porque a base não distingue.
- Confirmar com o time de operações se os StockCodes "M"/"D"/"B" (ajustes
  manuais/estoque) realmente correspondem a baixa de estoque, não a
  cancelamento de cliente mal registrado — a inferência da Measure 2A é forte
  mas não confirmada por ninguém do processo real.
- Medir custo de frete reverso por produto, para transformar "receita
  preservada" em ROI líquido de verdade no Improve.

Ver também `docs/retrospectiva-kaizen.md` para o que é reutilizável no
próximo projeto e a retrospectiva dos oito desperdícios.
