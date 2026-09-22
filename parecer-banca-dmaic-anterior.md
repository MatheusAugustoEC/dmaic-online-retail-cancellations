# Parecer da banca — Cancelamentos e Devoluções, Online Retail (UCI)

2026-09-21 · rodada 1 (completa a rodada iniciada nesta mesma data) · https://matheusaugustoec.github.io/dmaic-online-retail-cancellations/ · nível 2 (repositório público consultado para confirmar suspeitas do nível 1) · revisão visual: **realizada** (captura via Playwright — Painel, Dashboard, Relatório, Slides; Simples e Técnica; desktop, celular e escuro)

Esta rodada substitui a tentativa anterior registrada neste mesmo arquivo, que
não pôde rodar a captura de tela e por isso não tinha veredito fechado. Os
achados I1–I4 daquela tentativa foram revisitados abaixo (I1 fica resolvido;
I2 e I3 se confirmam; I4 é reformulado com mais evidência).

## Veredito

**REPROVADO** — um achado crítico muda um número que a própria página chama de
"o número que decide" (o ponto de indiferença de abandono no checkout). É
reversível: é um erro de rótulo/unidade em uma conta, não um problema de
desenho do projeto — a auditoria de qualidade, o controle estatístico e o
desenho experimental por trás da recomendação continuam sólidos.

## A banca

- **Gestor** — Diretor de Operações de um atacadista/varejista online de
  presentes e utilidades, Reino Unido. Responde pela margem e pelo custo
  operacional.
- **Especialista do domínio** — Gerente de fulfillment/expedição (picking,
  packing e conferência de pedidos), com experiência em logística reversa.
- **Cientista de dados sênior** — especializado em controle estatístico de
  processos (CEP) e desenho de experimentos/inferência causal.
- **Recrutador de dados** — calibrado para vaga de Analista/Cientista de
  Dados pleno-sênior (o projeto é peça de portfólio).

(Cartões aprovados pelo usuário no início desta revisão.)

## A voz de cada revisor

**Gestor:** Eu quase aprovava isso. O ponto de indiferença é o tipo de número
que eu preciso para decidir — direto, sem inflar o ganho — e o cenário
conservador dando prejuízo já mostrado sem disfarce me deixa confortável para
confiar no resto. Mas quando fui checar a conta de perto, os "34.257 pedidos"
do segmento não batem com os "13.081 pedidos" que o próprio Painel mostra
para a janela inteira — é fisicamente impossível um subconjunto ter quase
3x mais pedidos que o total. Enquanto essa conta não for refeita com a
unidade certa, eu não assino embaixo do 2,01% como "o número que decide". E
ninguém me disse quanto custa nem quanto rende a ação que vocês chamam de
"mais robusta" (a auditoria dos 198 produtos) — só a segunda ação tem número.

**Especialista do domínio:** O raciocínio de causa é bom — testar a hipótese
rival (país) antes da principal é exatamente o tipo de disciplina que separa
uma análise séria de um garimpo de correlação, e a divergência dos dois
Paretos é real, eu já vi isso em outro varejista. Mas a trava recomendada para
"pedido grande do Reino Unido" é uma confirmação no checkout — do lado do
cliente — enquanto a causa suspeita que vocês mesmos escreveram no
pré-registro é erro de separação em lote grande, que é do lado do meu galpão.
Se o problema nasce na expedição, por que a trava está no carrinho de compras?
Isso también é, coincidentemente, a própria fricção que a simulação de ganho
diz que pode zerar o resultado. E o alarme de "faturamento caiu 10%" vai
disparar todo janeiro, depois do Natal, em qualquer varejo de presente — isso
precisa de uma correção sazonal antes de ir para produção.

**Cientista de dados sênior:** Metodologicamente, isto está bem acima da
média de um projeto de portfólio: hipótese rival pré-registrada e testada
antes das principais, efeito mínimo definido antes de olhar o dado, carta p′
de Laney no lugar certo (a carta mensal simples realmente sinalizaria alarme
falso), holdout aberto uma única vez com o resultado divergente registrado e
explicado por censura à direita em vez de maquiado como melhora. O que me
impede de aprovar sem ressalva é um erro de unidade que encontrei ao cruzar
`docs/pre-registro-hipoteses.md` (que define a unidade do defeito como
**linha**, não pedido) com `src/fase4_improve.py` (que conta linhas) e com o
texto do Relatório e do Improve, que chamam essas linhas de "pedidos" na
simulação do ganho. Não é um erro sutil de estilo: o abandono no checkout é
um evento por pedido, não por linha de produto, então a base sobre a qual o
2,01% foi calculado pode estar inflada pelo número médio de linhas por
pedido. Há também uma célula de 65,5% dominando sozinha a escala de cor de
toda a matriz Dashboard, e um gráfico de bolhas com quatro rótulos
sobrepostos a ponto de ficarem ilegíveis.

**Recrutador de dados:** Em 30 segundos no Painel eu entendo o problema, o
tamanho, e a limitação central — isso é raro, a maioria dos projetos de
portfólio enterra a limitação na seção 15. A troca de idioma técnico/simples é
um diferencial real que não vi em outros projetos com este mesmo dataset. Mas
não há nome, GitHub, LinkedIn ou contato em lugar nenhum da página — nem no
topo, nem no rodapé de nenhum dos quatro modos. Para uma peça de portfólio,
isso é o tipo de coisa que me faz fechar a aba antes de saber quem fez o
trabalho. E "poka-yoke" aparece escrito no modo Simples duas vezes — pequeno,
mas é exatamente o tipo de vazamento que eu uso para saber se a pessoa testou
a própria interface nos dois registros.

## Achados críticos

**C1 · CRÍTICO · Unidade "pedidos" usada para o que são linhas — o ponto de indiferença pode estar errado — Cientista de dados sênior, Gestor**
- Onde: Relatório (seção "A conta do ganho, passo a passo" / seção 10 técnica), Painel (plano de controle), `docs/improve-recomendacao.md`.
- Evidência: `docs/pre-registro-hipoteses.md` declara explicitamente "Unidade do defeito: **linha** (InvoiceNo × StockCode)". `src/fase4_improve.py:25` agrega com `n=("defect", "size")` sobre o dataset de linhas — ou seja, `n` conta linhas, não faturas distintas. Ainda assim, `docs/improve-recomendacao.md` e o Relatório escrevem "34.257 **pedidos**, 1.052 defeitos, 33.205 'legítimos'" e, na mesma seção, "33.205 dos 34.257 **pedidos** do segmento". Isso é aritmeticamente incompatível com o próprio Painel, que mostra `PEDIDOS: 13.081` (faturas distintas) para a janela madura inteira (9 meses) — um subconjunto de 3 segmentos não pode ter 2,6x mais pedidos que o total de pedidos da janela usada de referência.
- O que corrigir: Renomear a unidade para "linhas" em toda a seção 3/10 (Relatório, Painel, Improve), **ou** recalcular a simulação agregando por `InvoiceNo` real antes de aplicar a taxa de abandono de 2% — abandono no checkout é um evento por pedido, não por linha de produto, e um pedido grande (Q4, o segmento dominante da conta) tem várias linhas. Verificável recontando `df.groupby("InvoiceNo").ngroups` nos 3 segmentos sinalizados, em vez de `len(df)`.
- Erro ou preferência: ERRO.
- Fase de origem: Improve (pós-hoc — muda um número que o próprio projeto chama de principal na fase Control).

## Achados importantes

| ID | Achado | Evidência | O que corrigir | Fase de origem |
|---|---|---|---|---|
| I1 | Ação mais robusta (H4, ~198 produtos) não tem conta de ganho/custo | Relatório, seção "A conta do ganho": "A simulação abaixo é sobre os 3 segmentos de risco... não sobre os produtos do H4, que exigiriam um teste operacional diferente" — a causa que mais explica o prejuízo (40,4% de cobertura) fica sem número de retorno | Estimar ao menos uma ordem de grandeza do custo da auditoria física e do ganho esperado, ou declarar explicitamente que a decisão sobre H4 não pode ser tomada só com este relatório | Improve (pós-hoc) |
| I2 | Poka-yoke recomendado atua no checkout (cliente); a causa suspeita (H1) é erro de separação/picking em lote grande (armazém) | `docs/pre-registro-hipoteses.md:24-27` atribui H1 a "erro de picking/estoque em lotes grandes"; `docs/improve-recomendacao.md` lista "Elimina a causa" como SOP de separação em duas etapas, mas o item marcado como **Poka-yoke** (e o único que vira ação no Relatório/Painel) é "confirmação obrigatória... no checkout" — a trava fica no lado oposto de onde a causa nasce, e é justamente essa fricção que a própria simulação de ganho (C1) modela como risco de abandono | Confirmar com o time de fulfillment se uma checagem na separação (mais perto da causa) não é operacionalmente melhor que fricção no checkout do cliente; se o checkout for mantido, declarar explicitamente essa troca (menos risco de erro físico vs. mais risco de abandono de cliente) | Improve (pós-hoc — pode mudar a recomendação) |
| I3 | Alarme de "faturamento/pedidos caem >10%" no plano de controle não tem ajuste sazonal | `docs/control-plano.md` e Painel: alarme é "queda >10%, mensal", sem menção a sazonalidade; o próprio Relatório reconhece "um único pico de fim de ano" (seção "O que eu não sei") | Testar a variação mês a mês de faturamento/pedidos nos dados já existentes (dez/2010→jan/2011 e nov/2011→dez/2011 vs. jan seguinte) e, se a queda pós-pico ultrapassar 10% normalmente, trocar o alarme por comparação ano contra ano ou por desvio da sazonalidade esperada, não do mês anterior | Control (pós-hoc) |
| I4 | Jargão técnico ("poka-yoke") aparece no modo Simples | `docs/index.html:315` (célula do plano de controle sem `span.sim`/`span.tec` separados) e `docs/index.html:516` dentro de um `<p class="sim">`: "conferência extra na separação (poka-yoke)" — confirmado também no texto capturado do Relatório em modo Simples | Substituir por linguagem simples ("conferência dupla") no texto e na célula compartilhada da tabela, reservando "poka-yoke" ao modo Técnico | Entrega (pós-hoc, cosmético) |
| I5 | Nenhuma atribuição de autoria em nenhum modo da página | Capturas de tela completas (topo e rodapé) de Painel e Relatório, desktop e celular: sem nome, GitHub, LinkedIn ou contato em nenhum dos dois | Adicionar nome, link do repositório e/ou LinkedIn no cabeçalho ou rodapé — peça de portfólio sem identificação de autor não cumpre a função de portfólio para o Recrutador | Entrega (pós-hoc) |
| I6 | Gráfico de dispersão (Dashboard) com rótulos ilegíveis por sobreposição | `sobreposicao.md`: "d-scatter · texto sobre texto: 4 ocorrências" e "texto sobre marca: 6 ocorrências" no desktop e no escuro; confirmado visualmente em `graficos/desktop__simples__dashboard__06.png` — os rótulos de 23166, 22501 e outros dois produtos ficam ilegíveis, sobrepostos em um bloco único de texto | Espalhar os rótulos (leader lines) ou mostrar só no hover para bolhas próximas; ocorre em desktop, celular e escuro nos dois registros de linguagem | Entrega (pós-hoc) |
| I7 | Célula de 65,5% domina sozinha a escala de cor da matriz País × Quantidade | `graficos/desktop__simples__dashboard__03.png`: célula "Australia / Q1 (menor)" mostra 65,5%, ordens de grandeza acima de todas as outras células (a maioria entre 0% e 10%), tornando as demais visualmente indistinguíveis entre si | Declarar o n da célula (suspeita: n muito pequeno, poucas unidades vendidas para a Austrália no quartil menor) e considerar excluir células com n abaixo de um piso mínimo do mapa de cor, ou usar escala truncada/log com nota | Entrega (pós-hoc) — **hipótese a verificar**: confirmar o n real da célula Australia×Q1 no dado agregado |

## Achados menores

- **M1** — Rótulo "limite do normal" sobreposto à própria linha pontilhada do limite superior, na carta de controle (Painel e Relatório). Confirmado em `sobreposicao.md` ("texto sobre linha: 1 ocorrência") e visualmente em todos os modos/temas/dispositivos testados. Corrigir com leve deslocamento vertical do rótulo. (Entrega, cosmético.)

## O que está sólido

**Gestor**
- O ponto de indiferença é apresentado como "o número que decide", não o ganho bruto — e o cenário conservador (ganho negativo, −£21.002) é mostrado sem suavização, mesmo isto tendo o problema de unidade do achado C1.
- O stakeholder ("Ger. Operações") é declarado explicitamente como persona simulada, sem fingir aprovação real.

**Especialista do domínio**
- As contramedidas seguem a hierarquia correta (elimina causa → reduz variação → poka-yoke → apenas detecta), e a trava por quantidade nunca é aplicada fora do critério condicionado a H5.
- O FMEA aponta como maior risco (NPR 216) exatamente o segmento de clientes recorrentes de alto volume sendo o mais penalizado pela própria recomendação — reconhece o ponto fraco em vez de escondê-lo.

**Cientista de dados sênior**
- H5 (hipótese rival) testada antes de H1/H2, com efeito mínimo pré-registrado e imutável — protocolo anti-garimpo real, não só declarado.
- Holdout aberto uma única vez; resultado fora da projeção (censura à direita) registrado e explicado com evidência (queda mensal monotônica out→dez dentro do próprio holdout), em vez de escondido atrás de "a taxa melhorou".
- A exclusão do outlier de 80.995 unidades (StockCode 23843) segue o mesmo critério de corte (n≥50) usado no H4, não é uma exclusão ad-hoc — confirmado em `src/fase6_dados_entrega.py`.

**Recrutador de dados**
- Autocrítica específica e recorrente ("O que eu não sei", "o que a simulação não captura") em vez de genérica.
- No modo Painel, em uma tela, aparecem o número principal, a distância da meta e a limitação central, sem precisar procurar no Relatório.

## Cobertura dos roteiros

| Revisor | Itens | OK | Achado | Não se aplica |
|---|---|---|---|---|
| Gestor | 8 (G1–G8) | 5 | 3 (I1, C1 via G4, I3 via G5) | 0 |
| Especialista do domínio | 8 (E1–E8) | 6 | 2 (I2 via E3, I3 via E7 parcial) | 0 |
| Cientista de dados sênior | 12 (T1–T12) | 8 | 4 (C1 via T1, I6/I7 via T4/T11, M1 via T11) | 1 (T9 — projeto não constrói modelo preditivo) |
| Recrutador de dados | 8 (R1–R8) | 6 | 2 (I5, I4 via R5) | 0 |

## Matriz de achados

| ID | Gravidade | Revisor | Fase de origem | Pós-hoc | Status |
|---|---|---|---|---|---|
| C1 | Crítico | Cientista de dados sênior, Gestor | Improve | Sim | aguardando decisão |
| I1 | Importante | Gestor | Improve | Sim | aguardando decisão |
| I2 | Importante | Especialista do domínio | Improve | Sim | aguardando decisão |
| I3 | Importante | Gestor, Especialista do domínio | Control | Sim | aguardando decisão |
| I4 | Importante | Recrutador de dados | Entrega | Sim (cosmético) | aguardando decisão |
| I5 | Importante | Recrutador de dados | Entrega | Sim (cosmético) | aguardando decisão |
| I6 | Importante | Cientista de dados sênior | Entrega | Sim (cosmético) | aguardando decisão |
| I7 | Importante | Cientista de dados sênior | Entrega | Sim | aguardando decisão |
| M1 | Menor | Cientista de dados sênior | Entrega | Sim (cosmético) | aguardando decisão |

## Limites desta revisão

- **Nível 2 parcial**: o repositório público (`MatheusAugustoEC/dmaic-online-retail-cancellations`) foi consultado só para confirmar as suspeitas nascidas na leitura fria da página (C1, I2, I4, I5, e a checagem do outlier de 80.995 unidades citada em "O que está sólido") — não foi feita uma auditoria independente de todo o código-fonte ou reexecução dos scripts.
- **C1 não foi recalculado por esta banca**: apontamos a inconsistência de unidade com evidência direta do código e do texto, mas não recontamos `InvoiceNo` distintos nos 3 segmentos para produzir o número corrigido — isso cabe à correção, não à revisão.
- **I7 (célula de 65,5%)** não teve o `n` da célula verificado nos dados brutos; é hipótese a verificar, não achado confirmado por número.
- O registro Técnica dos Slides só capturou o último slide (estado de navegação herdado da sessão anterior do script) — não foi possível confirmar se todos os 9 slides existem e renderizam corretamente em Técnica; Simples foi verificado por completo (9/9 slides).
- Esta revisão não teve acesso a nenhum profissional real do setor de varejo online; toda afirmação sobre prática de fulfillment, picking ou comportamento de abandono de checkout (I2, I3, I7) é conhecimento geral do revisor emulado — tratar como hipótese a confirmar (regra 3 da banca), não como fato do setor.
- Esta conversa não escreveu nenhum código deste projeto — é a primeira vez que ela vê a página e o repositório —, mas o diretório de trabalho local é o mesmo repositório do projeto (`origin` aponta para `MatheusAugustoEC/dmaic-online-retail-cancellations`). Isso permitiu o nível 2 sem precisar clonar nada; registra-se por transparência.
