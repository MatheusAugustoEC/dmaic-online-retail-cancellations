# FASE 4 — IMPROVE · Recomendação que não vou implementar

Data: 2026-09-20. Código: `src/fase4_improve.py`, sobre
`docs/analyze_dataset_exploracao.parquet` (janela de exploração, holdout nunca
tocado). Toda conclusão herda a ressalva do Analyze: vale só para o subconjunto
pareável de cancelamentos.

## 1. Contramedidas por causa raiz validada

### Causa 1 — H4: StockCodes específicos com taxa ≥2x a média (causa confirmada, estatística e praticamente)

| Tipo | Contramedida |
|---|---|
| Elimina a causa | Auditoria física dos ~198 StockCodes sinalizados — a base não diz POR QUE eles falham mais (produto frágil, descrição enganosa, foto errada), então "eliminar" aqui é uma investigação qualitativa fora do dado, não uma ação data-driven direta. Declarado como próximo passo, não como algo que os dados resolvem sozinhos. |
| Reduz variação | Procedimento de embalagem padronizado especificamente para a lista fechada de StockCodes sinalizados (não para o catálogo inteiro). |
| **Poka-yoke** | Conferência dupla obrigatória (scan de código de barras + segunda pessoa) no momento da separação, **gatilhada automaticamente pelo próprio StockCode** quando ele está na lista de risco — o erro é barrado no ponto de origem, não descoberto depois pelo cliente. |
| Apenas detecta | Monitoramento mensal da taxa por StockCode (já desenhado no Control) para flagar novos entrantes na lista de risco. |

### Causa 2 — H5-condicionada: Quantity alta como risco, mas só dentro do UK

| Tipo | Contramedida |
|---|---|
| Elimina a causa | Revisar o processo de separação para pedidos grandes DENTRO DO UK (ex.: trocar picking único por conferência em duas etapas acima de um limiar de Quantity) — ataca o mecanismo suposto (erro de picking em lote grande), não só o sintoma. |
| Reduz variação | SOP específico de separação para pedidos UK acima do limiar de Quantity que definiu Q4. |
| **Poka-yoke** | Passo de confirmação obrigatória (checkbox ou e-mail) no checkout **apenas quando Country=UK E Quantity do carrinho ultrapassa o limiar de risco** — condicionado explicitamente ao veredito de H5, nunca aplicado fora do UK, onde o padrão se inverte. |
| Apenas detecta | Revisão manual pré-despacho de pedidos UK de alto volume (detecção, não prevenção). |

**Nenhuma contramedida usa Country ou Quantity isoladamente como gatilho** —
H1 e H2 foram estatisticamente confirmadas mas praticamente refutadas no
Analyze (efeito abaixo do mínimo pré-registrado); só a combinação
condicionada por H5 entra como base do poka-yoke.

## 2. Entregável concreto — tabela de segmentos de risco

Cruzamento Country_group × faixa de Quantity (quartil) × Recorrência, 16
células. **Regra de decisão**: sinalizar célula se taxa ≥ 1,5× a taxa geral
(1,868% → limiar 2,801%) **E** n ≥ 500 (evita marcar célula pequena dominada
por poucos casos).

| Country | Quantity | Cliente | n | Taxa | IC95% (Wilson) |
|---|---|---|---|---|---|
| **Resto** | **Q1 (menor)** | **Recorrente** | **1.812** | **5,57%** | **[4,61%; 6,73%]** |
| **UK** | **Q4 (maior)** | **Recorrente** | **27.642** | **2,94%** | **[2,75%; 3,15%]** |
| **Resto** | **Q2** | **Recorrente** | **4.803** | **2,85%** | **[2,42%; 3,36%]** |

Nenhuma outra célula ultrapassou os dois critérios simultaneamente. Note que a
primeira célula sinalizada (Resto, Q1, Recorrente) é **exatamente o padrão
invertido que H5 encontrou** — quantidade baixa, não alta, é o risco fora do
UK. O cruzamento data-driven confirma isso sem eu precisar presumir direção:
a tabela não foi construída assumindo "Quantity alta = risco em todo lugar".

## 3. Simulação do ganho

Universo dos 3 segmentos sinalizados: 34.257 pedidos, 1.052 defeitos, 33.205
"legítimos" (não cancelariam de qualquer forma). Receita média por linha
cancelada nesses segmentos: £100,77 (puxada para cima pela célula UK-Q4, onde
o pedido médio cancelado vale £74,31 — revendedores).

| Cenário | Fração de cancelamentos evitada | Receita preservada | Abandono assumido (2%) | Receita perdida | **Ganho líquido** |
|---|---|---|---|---|---|
| Conservador | 20% | £21.202 | 2% dos legítimos | £42.204 | **−£21.002** |
| Central | 40% | £42.404 | 2% dos legítimos | £42.204 | **£200** |
| Otimista | 60% | £63.606 | 2% dos legítimos | £42.204 | **£21.402** |

**No cenário conservador o ganho é NEGATIVO** — a fricção custaria mais do que
economiza, mesmo com uma taxa de abandono baixa (2%). Só a partir do cenário
central o resultado vira positivo, e por uma margem pequena.

### Ponto de indiferença (o número em destaque)

Taxa de abandono de checkout que zeraria o ganho, por cenário:
- Conservador (20% evitado): **1,01%**
- **Central (40% evitado): 2,01%**
- Otimista (60% evitado): 3,01%

**Isto é frágil por desenho**: 33.205 dos 34.257 pedidos do segmento
sinalizado (97%) são legítimos e não cancelariam de qualquer forma. Mesmo no
cenário central, basta a fricção afastar **pouco mais de 2%** desses clientes
legítimos para o ganho inteiro desaparecer. Como esta base não registra nenhum
contrafactual real de abandono (nenhum "quase-cancelamento evitado" está
marcado), **este ponto de indiferença — não o ganho bruto de £42.404 do
cenário central — é o número que decide se a recomendação vale a pena**. Uma
recomendação cujo ganho evapora com 2 em cada 100 clientes legítimos incomodados
não é uma recomendação robusta; é uma aposta que só o experimento (seção 4)
pode validar de verdade.

### O que a simulação não captura
- Efeito reputacional de fricção extra em revendedores recorrentes de alto
  volume — provavelmente os clientes mais valiosos da base (já apontado na
  Fase 0).
- Efeito de médio prazo sobre recompra (cliente incomodado pode não voltar,
  mesmo sem abandonar o checkout na hora).
- Custo operacional de implementar/manter a verificação.

## 4. Desenho do experimento

- **Baseline do segmento**: 3,071% de cancelamento.
- **Efeito a detectar**: em vez do mínimo absoluto de 3 p.p. herdado de H1
  (que aplicado literalmente aqui exigiria derrubar a taxa quase a zero — alvo
  irreal), uso a redução relativa de 40% da premissa central da simulação
  (3,071% → 1,843%, diferença de 1,228 p.p.).
- **n necessário**: 2.454 pedidos por braço (α=0,05, poder=80%).
- **Tempo estimado**: ~3.426 pedidos elegíveis/mês no segmento → **~1,4 meses**
  de tráfego para os dois braços.

**Unidade de aleatorização**: recomendo **CustomerID**, não sessão de
checkout. Motivo: o segmento de maior peso (UK-Q4-Recorrente, revendedores) é
justamente o mais sensível a fricção repetida — expor o mesmo cliente a braços
diferentes em compras diferentes (risco da unidade "sessão") é mais grave aqui
do que o custo de diluir o n (clientes recorrentes contribuem vários pedidos
ao mesmo braço).

**Elegibilidade**: pedidos nas 3 células sinalizadas. **Duração**: mínimo 1
mês fora do pico para atingir o n; se necessário, estender para cobrir fatia
do pico (nov–dez) — resultado do braço no pico analisado separadamente, não
agrupado sem checar, dado que H3 (exploratória) sugere que sazonalidade pode
alterar o comportamento. **Métrica de decisão**: taxa de cancelamento pareável
tratado vs. controle. **Guardrails**: abandono de checkout real (medido, não
premissa — o experimento é a única forma de medir isso de verdade), volume
total, receita bruta do segmento. **Critério de parada**: guardrail violado
antes do n → para e reporta como achado, não insiste até o n calculado.

**Ameaças à validade**: sazonalidade não coberta (mitigada pela duração);
contaminação por CustomerID em ambos os braços (mitigada pela unidade
escolhida); **regressão à média** — os segmentos foram sinalizados pela MAIOR
taxa observada no Analyze, que pode regredir naturalmente mesmo sem
intervenção; o braço controle isola isso, mas fica registrado como ameaça
explícita, não escondida.

## 5. FMEA da recomendação

| Modo de falha | Severidade | Ocorrência | Detecção | RPN |
|---|---|---|---|---|
| Fricção afasta revendedores de alto volume (UK, Quantity alta, recorrentes) | 9 | 6 | 4 | **216** |
| Regra de Quantity aplicada fora do UK por engano (H5 mostrou inversão de sinal em Resto) | 8 | 3 | 5 | 120 |
| Regra de segmento fica desatualizada com mudança de mix de produtos/países | 6 | 5 | 3 | 90 |

O maior risco (RPN 216) é exatamente o segmento de maior valor da base
(revendedores recorrentes) sendo o mais penalizado — reforça por que o ponto
de indiferença da seção 3, não o ganho bruto, deve guiar a decisão de seguir
ou não.

## 6. O contra

**Parágrafo do cético**: "A taxa de cancelamento associada a Quantity alta
pode ser só efeito de poucos clientes grandes com comportamento
idiossincrático, e aplicar fricção para todo o segmento penaliza clientes bons
por causa de poucos casos."

**Resposta ancorada no veredito real de H5**: o ceticismo está PARCIALMENTE
certo, e o Analyze já incorporou isso — H5 não foi refutada de forma limpa. A
regressão ajustada mostrou que o efeito de Quantity sobrevive quase intacto
dentro do UK (redução de só 3% ao controlar por país e recorrência), mas o
teste de Breslow-Day encontrou que esse mesmo efeito **se inverte** fora do
UK. Por isso nenhuma contramedida aqui usa uma regra universal "quantidade
alta = risco" — a tabela de segmentos só sinaliza células com n≥500, o que já
filtra boa parte do "poucos casos idiossincráticos" que o cético teme (células
de n baixo com taxa alta foram explicitamente descartadas na seção 2). **O que
esta resposta NÃO resolve**: mesmo com n≥500, uma célula pode ainda ser
dominada por poucos CustomerID com muitos pedidos cada — isso não foi
verificado com o dado histórico; é exatamente o que o experimento aleatorizado
por CustomerID (seção 4) resolve na prática, e que a simulação sozinha não
pode.

## Tollgate IMPROVE

| Critério | Veredito |
|---|---|
| Ponto de indiferença calculado e em destaque, não o ganho bruto | **OK** — seção 3, com nota explícita de que o cenário conservador dá ganho negativo |
| Recomendação condicionada ao veredito de H5 | **OK** — nenhuma contramedida usa Country ou Quantity isoladamente; o poka-yoke da Causa 2 é explicitamente restrito a "Quantity alta E UK"; a tabela de segmentos sinalizou naturalmente a célula invertida (Resto-Q1-Recorrente) sem presumir direção |

**Veredito da fase**: **APROVADO**. A recomendação é honesta sobre sua própria
fragilidade: no cenário mais conservador o ganho é negativo, e mesmo no
cenário central um abandono de pouco mais de 2% já zera o resultado — a
decisão real só deve ser tomada depois do experimento (~1,4 meses de dados),
não a partir desta simulação.
