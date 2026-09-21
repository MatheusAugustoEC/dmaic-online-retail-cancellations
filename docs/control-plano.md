# FASE 5 — CONTROL

Data: 2026-09-20.

## Parte A — Plano de controle como especificação

### 1. Tabela de controle

| Métrica | Definição operacional | Fonte | Frequência | Limite | Responsável | Ação ao sair do limite |
|---|---|---|---|---|---|---|
| Taxa de cancelamento por segmento de risco (**primária**) | Linhas pareadas defeito/total, por célula Country×Quantity×Recorrência (Improve) | Pipeline mensal, mesma lógica de pareamento de `src/fase2b_baseline.py` | Mensal | Carta p por segmento, 3σ | Gerente de Operações/Atendimento (persona do Define) | 2 meses seguidos fora do limite OU regra de Nelson disparada → revisão do plano de segmentação (não ação imediata sobre 1 mês isolado) |
| Volume total de pedidos (guardrail) | Contagem de InvoiceNo únicos | Mesmo pipeline | Mensal | Queda >10% mês a mês atribuível ao segmento sob fricção | Mesmo responsável | Pausar a verificação prévia naquele segmento e investigar |
| Receita bruta (guardrail) | Σ Quantity×UnitPrice de linhas não-canceladas | Mesmo pipeline | Mensal | Queda >10% mês a mês atribuível ao segmento sob fricção | Mesmo responsável | Mesma ação acima |
| Taxa de abandono de checkout (guardrail) | % de sessões com fricção que não completam o pedido | Sistema de checkout — **fora do escopo deste dataset**, só medível depois do deploy real ou do experimento do Improve | Semanal durante rollout | Acima do ponto de indiferença calculado no Improve (2,01% no cenário central) | Mesmo responsável | Reverter a fricção imediatamente para o segmento afetado |
| Taxa de defeito por StockCode sinalizado (H4) | Linhas pareadas defeito/total por StockCode, n≥50 | Mesmo pipeline | Mensal | Novo StockCode cruza o limiar de 2x a taxa geral | Time de qualidade/estoque | Adicionar à lista de poka-yoke de conferência dupla |

### 2. Carta p de acompanhamento e gatilho

Herdada da Measure 2B (`src/fase2b_baseline.py`, seção "2. ESTABILIDADE"),
agora recalculada mês a mês incluindo os meses do holdout à medida que passam.
**Gatilho de alerta**: dois meses consecutivos fora dos limites de 3σ, **ou**
qualquer regra de Nelson disparada (a mesma lista já aplicada na 2B) →
aciona revisão do plano de controle, não ação automática sobre um único mês
(a 2B já mostrou que, com este volume mensal, os limites são estreitos o
suficiente para gerar falsos alarmes isolados).

### 3. O que invalidaria esta análise

- Mudança de plataforma de checkout (o processo de registro de cancelamento
  pode deixar de gerar InvoiceNo "C" da mesma forma, quebrando toda a lógica
  de pareamento).
- Mudança relevante no mix de países ou categorias de produto vendidos (a
  auditoria de H2/H5 e os segmentos do Improve foram calibrados sobre a
  composição observada; um mix diferente pode inverter conclusões, como já
  vimos acontecer entre UK e Resto dentro dos próprios dados).
- Qualquer evento que altere a composição de clientes revendedores vs.
  consumidor final (a análise inteira depende dessa composição — Quantity alta
  como sinal de revenda é uma leitura específica desta base).
- **Quando refazer**: revisão trimestral agendada, OU imediatamente no
  primeiro sinal de causa especial confirmada na carta (não em qualquer ponto
  fora de 3σ isolado — ver seção 2).

## Parte B — Controle do meu pipeline

### 4. Testes automáticos de qualidade

`tests/test_data_quality.py` — 11 testes cobrindo exatamente a auditoria da
2A (schema, volume, `Quantity=0`, completude de `CustomerID`/`Description`,
duplicatas exatas, presença dos StockCodes não-produto conhecidos, consistência
`UnitPrice<=0`/produto real, consistência prefixo "C"/`Quantity` negativo,
integridade do corte de holdout). Rodam com `pytest tests/` — 11/11 passando
sobre o dado atual.

### 5. Checklist de reprodutibilidade

| Item | Status |
|---|---|
| Parâmetros extraídos para configuração (`src/config.py`) | **OK** — StockCodes não-produto, corte de holdout, limiares de segmento de risco, efeitos mínimos pré-registrados |
| Scripts reexecutáveis do zero, mesma saída | **OK** — reexecutei `fase2b`, `fase3`, `fase4` após o refactor de config e os números bateram exatamente com o documentado |
| Seed de aleatoriedade fixada | **N/A** — nenhum passo usa aleatoriedade (sem bootstrap, sem split aleatório; holdout é temporal, determinístico) |
| Versão de bibliotecas registrada | **FALHA** — não há `requirements.txt` nem lockfile neste projeto. Registrado aqui como pendência real, não escondida. |
| Dados brutos versionados ou hash registrado | **FALHA PARCIAL** — `online_retail.csv` está no `.gitignore` (prática correta para arquivo grande), mas não há hash/checksum registrado do arquivo usado. Sem isso, "reprodutível do zero" depende de o mesmo CSV estar presente. |
| Cada fase documentada com tollgate e commit correspondente | **OK** — `git log` mostra um commit por fase, com o veredito no corpo da mensagem |

Onde ainda falha: falta `requirements.txt` e hash do dataset bruto — ambos
apontados aqui como dívida técnica real do projeto, não resolvidos nesta
sessão por não terem sido pedidos, mas registrados para não esconder.

### 6. Verificação do ganho contra o baseline congelado

`docs/baseline_congelado.json` (2B): taxa 1,868% (IC95% [1,817%; 1,920%]).
Reexecutando `fase2b_baseline.py` após o refactor de configuração (seção 4
acima), os números saíram idênticos — `git diff` no JSON não mostrou
alteração. O baseline permanece válido e não foi silenciosamente alterado.

### 7. Abertura do holdout — feita uma única vez

Script: `src/fase5_abertura_holdout.py`. Resultado congelado em
`docs/holdout_resultado.json` (**artefato imutável a partir de agora**).

**Taxa de cancelamento no holdout**: 1,179% (IC95% [1,122%; 1,239%]), n=130.910,
defeitos=1.543 — **abaixo** do intervalo projetado a partir da exploração
madura ([2,089%; 2,255%]). **A taxa NÃO se sustentou dentro da projeção.**

**Isso não é descartado nem maquiado — é achado metodológico legítimo,
registrado como tal**: a quebra mensal do próprio holdout mostra um padrão
que aponta para censura à direita, não para uma queda real do processo:

| Mês | Taxa | Dias de visibilidade dentro dos dados (aprox.) |
|---|---|---|
| out/2011 | 1,74% | até ~70 dias (mais próximo do padrão da exploração) |
| nov/2011 | 0,99% | até ~39 dias |
| dez/2011 | 0,27% | até ~9 dias |

A taxa cai monotonicamente à medida que a janela de visibilidade dentro do
próprio arquivo (que termina em 2011-12-09) encolhe — exatamente o padrão que
o artefato de censura documentado na 2B e no Analyze previa, agora em escala
maior porque o holdout inteiro é mais curto que qualquer mês individual da
exploração. **Não afirmo que é 100% censura e 0% efeito real** (não há como
isolar isso sem dados após 2011-12-09, que não existem) — mas a evidência
disponível não sustenta concluir "o processo melhorou no holdout"; sustenta
"a métrica de taxa pooled do holdout é estruturalmente subestimada pelo mesmo
mecanismo já documentado, e mais gravemente aqui".

**Os segmentos de risco identificados no Improve SE SUSTENTARAM**: as 3
células sinalizadas (UK×Q4×Recorrente, Resto×Q2×Recorrente,
Resto×Q1×Recorrente) continuam entre as de maior taxa no holdout, usando a
mesma regra de decisão recalculada sobre a taxa geral do holdout — nenhuma
delas caiu da lista. Novas células apareceram (todas envolvendo
"Primeira_compra" em Resto/UK-Q4), o que é compatível com a época do ano
(fim de ano atrai mais compradores de presente de primeira vez) — não
testado formalmente, fica como observação para o próximo ciclo.

**H4 (StockCodes problemáticos) se sustentou com folga**: dos 195 produtos
sinalizados na exploração, 174 têm dado suficiente no holdout, com taxa média
de 3,63% contra 1,18% da taxa geral do holdout (**3,1x**, muito próximo do
critério de 2x usado para sinalizar) — a causa mais robusta do Analyze
continua sendo a mais robusta no holdout.

**Conclusão da abertura do holdout**: a taxa geral não se sustentou dentro da
projeção (achado metodológico sobre os limites de medir cancelamento perto da
borda dos dados, não sobre o processo de negócio), mas a estrutura de risco
(segmentos do Improve e produtos do H4) se sustentou integralmente. Isso
reforça, e não enfraquece, a recomendação de priorizar H4 e os segmentos
condicionados por H5 sobre qualquer meta agregada de taxa mensal.

## Tollgate CONTROL

| Critério | Veredito |
|---|---|
| Holdout aberto uma única vez, resultado registrado independente do veredito | **OK** — `docs/holdout_resultado.json`, taxa geral fora da projeção registrada sem suavização |
| README declara o que o dado não permite concluir | Ver `README.md` |

**Veredito da fase**: **APROVADO**.
