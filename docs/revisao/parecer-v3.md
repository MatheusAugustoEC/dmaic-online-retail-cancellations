# Parecer da banca — Cancelamentos e Devoluções, Online Retail (UCI) — V3 (arquivo local)

2026-09-22 · revisão nova e completa (V3) · arquivo local `C:\Users\Augusto\Desktop\Projetos\TEST IA\docs\index.html`, capturado via `file:///C:/Users/Augusto/Desktop/Projetos/TEST%20IA/docs/index.html` (não o site publicado) · nível 2 (repositório local, mesmo diretório de trabalho) · revisão visual: **realizada** (captura via Playwright — Painel, Dashboard, Relatório, Slides; Simples e Técnica; desktop, celular e escuro) **mais testes de interação dedicados** (automação de arrastar e Ctrl+roda nos gráficos com zoom, feitos à parte da captura padrão da skill, para investigar a observação 2 do responsável) · mesma lacuna já registrada nas rodadas anteriores: celular e escuro não cobriram o registro Técnica, e a captura de texto do registro Técnico dos Slides não percorreu os 9 slides.

Esta é uma revisão nova pelos quatro roteiros inteiros, não uma conferência de achados anteriores. As rodadas 1 e 2 (`parecer-banca-dmaic.md`, `parecer-r2.md`) permanecem intactas; esta revisão não as leu antes de revisar de novo (a leitura fria começou do zero na página capturada agora).

## Observações do responsável

Quatro pontos trazidos por quem abriu o arquivo, avaliados com evidência antes do resto da revisão.

### 1. Matriz "País e tamanho do pedido, cruzados" — células "n insuf." difíceis de ler

**Achado confirmado.** Onde: Dashboard, matriz País × Tamanho do pedido, nos dois registros (a palavra some no registro Técnico, virando "n<50" — ver abaixo). Evidência: `graficos/desktop__simples__dashboard__03.png` e a versão em celular e escuro — sete células (Finland/Q1, Sweden/Q1, Austria/Q1, Denmark/Q1, Denmark/Q2, Poland/Q1, Japan/Q2, Japan/Q3) mostram o texto "n insuf." em cinza, com borda tracejada, dentro de células do mesmo tamanho das que mostram números como "3,7" ou "14,2". O texto "n insuf." tem 8 caracteres contra 3–4 dos números — quebra o ritmo de leitura de uma matriz pensada para ser escaneada como números, e num relance rápido (o teste "reunião de trabalho") se parece mais com um erro de carregamento do que com uma célula deliberadamente sem dado. O registro Técnico usa "n<50" (mais curto, mas ainda destoa visualmente dos números da matriz e exige que o leitor saiba o que "n" significa).
O que corrigir: um tratamento visual mais discreto e consistente — por exemplo, um traço simples ("—") dentro da célula tracejada (o padrão comum em tabelas/dashboards para "sem dado suficiente"), com o "n<50"/a explicação completa reservada ao hover/tooltip e à legenda already existente ("poucos itens (não colorida)"). Isso mantém a transparência (a legenda já explica o corte) sem quebrar o escaneamento visual da matriz.
Erro ou preferência: PREFERÊNCIA de legibilidade — a solução atual é honesta e correta (não esconde a limitação, ao contrário do defeito original I2 que este mesmo achado motivou na rodada 1), mas o texto por extenso dentro da célula compromete a leitura rápida que o resto da matriz permite.
Gravidade: **MENOR**.

### 2. Dashboard, "Volume contra frequência, por produto" — bolhas não aparecem

**Achado confirmado, com causa raiz provável identificada.** Nas capturas estáticas desta revisão (carregamento normal da página, sem interação), as bolhas aparecem normalmente — ver `graficos/desktop__simples__dashboard__06.png`, e as versões em celular e escuro, todas com os 6-7 produtos nomeados e a bolha "Outros produtos" visíveis. Não reproduzi "zero bolhas" só carregando a página.
Mas testei a interação de zoom que a legenda do próprio gráfico anuncia ("Arraste sobre o gráfico para ampliar · Ctrl + roda do mouse aproxima e afasta") com automação de navegador, e **confirmei um defeito real**: nenhuma das duas formas de zoom funciona neste gráfico.
- Arrastar sobre a área do gráfico não aciona nenhum zoom — em vez disso, dispara a seleção de texto nativa do navegador (a página inteira abaixo do ponto de arraste fica destacada em azul, como ao selecionar um parágrafo) — ver `svgzoom2_after_crop.png`.
- Ctrl + roda do mouse sobre o gráfico não muda nada nos eixos (testado com scroll equivalente a ~13 "cliques" de roda) — ver `scatter_wheel_after_crop.png`.
Por comparação, testei a mesma interação na carta de controle do Painel (que anuncia a mesma legenda) e ela **funciona**: arrastar de fato restringe o eixo de datas e faz aparecer um botão "Ver tudo" — ver `ctrlzoom_after_crop.png`.
Isto é uma explicação plausível e testável para "não vejo as bolhas": se o leitor tentar usar a interação de zoom anunciada — a reação natural diante de um gráfico com poucos itens nomeados e um "Outros produtos" grande — o gráfico não reage, e dependendo do navegador a seleção de texto nativa pode alterar visualmente a região (texto destacado sobre as bolhas, ou o usuário rolando/clicando repetidamente tentando fazer o zoom funcionar) a ponto de a pessoa relatar "não vejo bolha nenhuma". Não consegui reproduzir um estado de "zero bolhas" literal nesta bateria de testes — registro isso como limite desta verificação, não como o achado em si.
O que corrigir: implementar de fato o zoom por arraste e Ctrl+roda no gráfico de dispersão do Dashboard (mesma biblioteca/mecanismo já usado com sucesso na carta de controle do Painel), ou, se o gráfico de bolhas não for candidato a zoom, remover a legenda "Arraste sobre o gráfico para ampliar · Ctrl + roda do mouse aproxima e afasta" que aparece embaixo dele — uma instrução de uso que não funciona é pior do que nenhuma instrução.
Erro ou preferência: ERRO — a legenda promete uma interação que não existe neste gráfico.
Gravidade: **IMPORTANTE** (não muda nenhum número ou conclusão, mas é uma funcionalidade anunciada e ausente, verificável e reproduzível, que pode ter causado exatamente o sintoma relatado).

### 3. Painel, cartão "Abandono no checkout" — "n/d"

**Achado confirmado.** Onde: Painel, linha de quatro cartões (Faturamento, Pedidos, Clientes ativos, Abandono no checkout). Evidência: `capturas/desktop__simples__painel.png` — o quarto cartão mostra "n/d" em negrito, do mesmo tamanho e peso visual que "£ 5.786.872", "13.081" e "3.613" nos outros três, com a legenda menor "não mensurável com este dado" abaixo. Há uma frase logo abaixo da linha de cartões que contextualiza ("O quarto — quanto isso afasta cliente no checkout — esta base não registra; só um teste real mediria"), mas essa explicação depende de o leitor continuar lendo depois do cartão — no cartão em si, "n/d" ao lado de três números reais tem a mesma aparência de um dado que falhou ao carregar, não de uma lacuna declarada de propósito.
O que corrigir: diferenciar visualmente o cartão "n/d" dos outros três — por exemplo, com um estilo mais discreto (texto acinzentado em vez do mesmo negrito/cor dos números reais) e uma nota curta diretamente associada ao cartão (não só no parágrafo abaixo), do tipo "não medido por desenho — ver Relatório, seção 11", para que o "n/d" se leia como uma decisão declarada, não como uma métrica ausente.
Erro ou preferência: PREFERÊNCIA — o dado está correto e a lacuna é genuína e já declarada no texto; o problema é só de hierarquia visual.
Gravidade: **MENOR**.

### 4. Dashboard, cartão "Diferença da média" — "+0,00 pontos percentuais"

**Achado confirmado.** Onde: Dashboard, linha de quatro cartões (Itens, Voltam, Devolvido, Diferença da média). Evidência: `capturas/desktop__simples__dashboard.png` — no estado padrão da página (nenhum filtro aplicado), o cartão mostra "+0,00 pontos percentuais". Isso é matematicamente correto e até previsível — sem filtro, o recorte é a base inteira, então a diferença para a própria média da base é sempre zero por definição — mas nenhum texto ao lado do cartão explica isso. O parágrafo acima da linha de filtros diz "Nenhum filtro — mostrando tudo", o que dá uma pista indireta, mas não conecta explicitamente esse fato a "por isso a diferença é 0,00". Um leitor que veja só a linha de cartões pode interpretar "+0,00" como um indicador quebrado, do mesmo jeito que o "n/d" do Painel.
O que corrigir: adicionar uma nota curta junto ao cartão (ou no texto de estado "Nenhum filtro") explicando que a diferença é sempre 0,00 sem filtro ativo, e passa a mostrar a distância real assim que um filtro (país, produto, etc.) for aplicado — convidando o leitor a interagir, em vez de deixá-lo achando que o cartão não funciona.
Erro ou preferência: PREFERÊNCIA — o número está correto; falta uma frase de contexto.
Gravidade: **MENOR**.

## Veredito

**APROVADO COM RESSALVAS** — nenhum achado desta rodada muda um número, uma conclusão ou uma decisão do projeto. O mais sério (o zoom do gráfico de dispersão) é uma funcionalidade de interface anunciada e não implementada, com evidência reproduzível — real e a ser corrigida, mas não compromete a análise, a auditoria de qualidade, o controle estatístico nem o desenho causal, que continuam sólidos e foram reconferidos nesta rodada. Os quatro pontos trazidos pelo responsável são achados reais, na maioria PREFERÊNCIA de apresentação, não ERRO de conteúdo.

## A banca

- **Gestor** — Gerente de Operações de um atacadista/varejista online de presentes e utilidades, Reino Unido, ~12 anos no setor.
- **Especialista do domínio** — Gerente de fulfillment/separação de pedidos e logística reversa, atacado online B2B, Reino Unido.
- **Cientista de dados sênior** — controle estatístico de processo, teste de hipótese com efeito mínimo pré-registrado, desenho de experimentos.
- **Recrutador de dados** — vaga de analista de dados júnior, generalista, mercado brasileiro.

(Cartões aprovados pelo usuário no início desta revisão, sem ajuste — mesmo domínio das rodadas anteriores.)

## A voz de cada revisor

**Gestor:** Isto continua parecendo um trabalho sério — a conta do ganho agora está em faturas, não em linhas, o critério de H4 ficou mais rigoroso, e o alarme de faturamento não vai mais disparar sozinho em fevereiro. O que me incomoda nesta passada é mais sutil: um cartão de "Abandono no checkout" com "n/d" bem no meio da primeira tela é o tipo de coisa que, numa reunião de verdade, alguém aponta e pergunta "isso quebrou?" antes mesmo de eu explicar que é proposital. E a linha "Erro de separação em pedido grande do Reino Unido | a definir (sem dado de linha-base)" no plano de controle — eu entendo por que está "a definir", mas um plano de controle com uma linha sem limite definido não é bem um plano de controle ainda; é uma promessa de que um dia vai ser.

**Especialista do domínio:** A trava dupla (separação e checkout, com a separação como primeira linha) continua sendo a decisão certa — reconhece que a causa é de armazém sem abrir mão do reforço no checkout só onde o risco é condicionado. Não achei nada de novo na minha área que mude essa leitura.

**Cientista de dados sênior:** Reconferi os números críticos da rodada anterior e continuam batendo — 6.902 faturas, 9,04% de taxa no nível de fatura, 66 produtos pelo critério do limite inferior do IC. O que essa rodada me trouxe de novo é um problema de interação, não de estatística: testei o zoom que o gráfico de dispersão anuncia e ele simplesmente não funciona — nem arrastar, nem Ctrl+roda —, enquanto o mesmo recurso funciona perfeitamente na carta de controle. Isso não muda um número, mas é o tipo de coisa que, se eu estivesse numa demonstração ao vivo e tentasse mostrar esse gráfico interativamente, me deixaria sem explicação na hora.

**Recrutador de dados:** A troca de idioma e a auditoria de qualidade continuam sendo o diferencial real deste projeto. Mas um recrutador júnior generalista, sem paciência para ler o Relatório inteiro, vai passar o olho pelo Painel e pelo Dashboard primeiro — e é exatamente ali que os dois cartões "quebrados na aparência" (n/d, +0,00) e o gráfico de bolhas com zoom morto estão. Não é o tipo de coisa que me faz rejeitar o candidato, mas é o tipo de coisa que me faz notar, e numa entrevista eu perguntaria "você testou clicar em tudo antes de publicar?".

## Achados importantes

| ID | Achado | Evidência | O que corrigir | Fase de origem |
|---|---|---|---|---|
| V2 | Zoom (arrastar e Ctrl+roda) não funciona no gráfico de dispersão do Dashboard, apesar de anunciado na legenda; funciona corretamente na carta de controle do Painel | `svgzoom2_after_crop.png` (arraste vira seleção de texto), `scatter_wheel_after_crop.png` (Ctrl+roda não muda eixos), `ctrlzoom_after_crop.png` (comparação: funciona na carta de controle) | Implementar o zoom no gráfico de dispersão com o mesmo mecanismo da carta de controle, ou remover a legenda que anuncia a interação | Entrega |

## Achados menores

- **V1** — Células "n insuf."/"n<50" na matriz do Dashboard quebram o escaneamento visual por serem texto longo dentro de células de números curtos; trocar por um símbolo mais discreto (ex.: "—"), mantendo a explicação completa na legenda/hover. (Entrega.)
- **V3** — Cartão "Abandono no checkout" (Painel) mostra "n/d" com o mesmo peso visual dos cartões com número real; diferenciar visualmente e anexar a explicação diretamente ao cartão. (Entrega.)
- **V4** — Cartão "Diferença da média" (Dashboard) mostra "+0,00" sem filtro ativo, sem nota explicando que isso é esperado por definição; adicionar uma frase curta de contexto. (Entrega.)
- **V5** — Linha "Erro de separação em pedido grande do Reino Unido" no plano de controle (Painel) tem o campo "Alarme em" preenchido com "a definir (sem dado de linha-base)" — correto e honesto, mas uma linha de plano de controle sem limite definido, apresentada com a mesma formatação das linhas que têm limite, pode ser lida como um controle já ativo; considerar marcar essa linha visualmente como "pendente" até que o limite seja definido. (Control.)

## O que corrigir, passo a passo

### [V2] · Zoom não funciona no gráfico de dispersão do Dashboard — prioridade 1
O problema, em linguagem simples: o gráfico "Volume contra frequência, por produto" (Dashboard) diz, na legenda abaixo dele, que dá para arrastar ou usar Ctrl+roda do mouse para ampliar — mas nenhuma das duas coisas faz efeito nenhum quando testadas. Arrastar apenas seleciona o texto da página, como se você tivesse arrastado sobre um parágrafo. Ctrl+roda não muda nada.
Por que importa: é uma instrução de uso publicada que não corresponde ao que a página faz. Isso é o tipo de coisa que mina a confiança de quem está testando o projeto — e é uma explicação plausível para relatos de "não consigo ver as bolhas direito", porque tentar usar uma interação que não responde é frustrante e pode levar a cliques/arrastos repetidos que bagunçam a seleção de texto da tela.
Onde está: Dashboard, gráfico "Volume contra frequência, por produto", legenda "Arraste sobre o gráfico para ampliar · Ctrl + roda do mouse aproxima e afasta" (Simples) / "Arraste para ampliar · Ctrl + roda: zoom · duplo clique: ver tudo" (Técnico), abaixo do gráfico, nos dois registros de linguagem.
O que fazer:
  1. Localizar o componente de gráfico de dispersão (bolhas) no código-fonte e verificar se o mecanismo de zoom por arraste/Ctrl+roda está de fato conectado a ele (na carta de controle do Painel, o mesmo tipo de interação funciona — usar essa implementação como referência).
  2. Implementar (ou reconectar) o zoom no gráfico de dispersão com o mesmo comportamento da carta de controle: arrastar restringe os eixos à área selecionada; Ctrl+roda aproxima/afasta; um botão "Ver tudo" (ou duplo clique) reseta a visão.
  3. Se, por alguma razão de design, o gráfico de dispersão não for zoomável (por exemplo, poucos pontos não justificarem zoom), remover a legenda de instrução de zoom desse gráfico específico nos dois registros de linguagem, em vez de deixá-la publicada sem função.
  4. Testar em desktop, celular (gesto de pinça, se aplicável) e tema escuro, nos dois registros.
Como saber que ficou certo: arrastar sobre a área de plotagem do gráfico de dispersão restringe visivelmente os eixos (ou a legenda de zoom foi removida, se a decisão for não implementar); Ctrl+roda muda a escala dos eixos; nenhum arraste sobre o gráfico aciona seleção de texto nativa do navegador.
O que pode mudar junto: nada além do comportamento deste gráfico — nenhum número da análise depende desta correção.
Fase de origem: Entrega · não é pós-hoc de análise (é um defeito de interface, não de conteúdo).

### [V1] · Células "n insuf." difíceis de escanear na matriz do Dashboard — prioridade 2
O problema, em linguagem simples: a matriz País × Tamanho do pedido mostra "n insuf." (Simples) ou "n<50" (Técnico) por extenso dentro das células sem dado suficiente — texto bem mais longo que os números de 3-4 caracteres nas outras células, o que quebra o ritmo de leitura de quem está escaneando a matriz rapidamente.
Por que importa: numa leitura rápida (o teste "isto seria apresentado assim numa reunião?"), texto longo dentro de uma célula de matriz numérica chama atenção desproporcional e pode parecer um erro de carregamento, não uma decisão de design.
Onde está: Dashboard, matriz "País e tamanho do pedido, cruzados", células de países com poucos itens no quartil (Finland, Sweden, Austria, Denmark, Poland, Japan — nas faixas com n<50), nos dois registros de linguagem.
O que fazer:
  1. Trocar o texto "n insuf."/"n<50" dentro da célula por um símbolo mais curto e discreto, como um traço ("—"), mantendo a borda tracejada e a cor neutra já usadas.
  2. Manter a explicação completa ("poucos itens (não colorida)") na legenda abaixo da matriz, e considerar adicionar o "n" exato num tooltip/hover para quem quiser o detalhe.
Como saber que ficou certo: as células sem dado suficiente usam um símbolo curto, do mesmo comprimento visual aproximado dos números nas outras células da matriz.
O que pode mudar junto: nada além da formatação dessas células.
Fase de origem: Entrega.

### [V3] · Cartão "n/d" do Painel sem destaque visual — prioridade 3
O problema, em linguagem simples: o cartão "Abandono no checkout" mostra "n/d" com o mesmo tamanho e peso dos três cartões vizinhos que têm números reais (Faturamento, Pedidos, Clientes ativos) — a explicação de por que está em branco só aparece num parágrafo depois, não junto ao cartão.
Por que importa: um leitor que só bate o olho na linha de cartões (o padrão de leitura de um Painel executivo) vê um "n/d" solto entre três números reais e pode interpretar como dado ausente por falha, não por desenho.
Onde está: Painel, linha de quatro cartões, cartão "Abandono no checkout", nos dois registros de linguagem.
O que fazer:
  1. Aplicar um estilo visualmente mais discreto ao cartão "n/d" (por exemplo, texto acinzentado em vez da mesma cor/peso dos números reais).
  2. Adicionar uma nota curta diretamente sob o "n/d" (não só no parágrafo abaixo da linha de cartões) — algo como "não medido por desenho — ver seção 11".
Como saber que ficou certo: o cartão "n/d" é visualmente distinguível dos outros três à primeira vista, e tem uma explicação de uma linha grudada nele, sem depender do parágrafo seguinte.
O que pode mudar junto: nada além do estilo e do texto deste cartão.
Fase de origem: Entrega.

### [V4] · Cartão "+0,00" do Dashboard sem contexto — prioridade 4
O problema, em linguagem simples: o cartão "Diferença da média" mostra "+0,00 pontos percentuais" quando nenhum filtro está aplicado — correto (comparar a base inteira com ela mesma dá zero), mas nada perto do cartão explica isso.
Por que importa: é o mesmo problema de aparência do achado V3 — um número que parece quebrado mas é, na verdade, um resultado trivial e esperado do estado padrão da página.
Onde está: Dashboard, linha de quatro cartões, cartão "Diferença da média", estado sem filtro, nos dois registros de linguagem.
O que fazer:
  1. Adicionar uma frase curta junto ao cartão, ou ao texto "Nenhum filtro — mostrando tudo", explicando que a diferença é sempre 0,00 sem filtro ativo e passa a refletir o recorte assim que um filtro for aplicado.
Como saber que ficou certo: o cartão "Diferença da média", no estado padrão da página, tem uma explicação de uma linha visível perto dele sobre por que mostra zero.
O que pode mudar junto: nada além do texto de contexto.
Fase de origem: Entrega.

### Acabamento
- **[V5]** Linha "Erro de separação em pedido grande do Reino Unido" no plano de controle do Painel tem "Alarme em: a definir (sem dado de linha-base)" — considerar um destaque visual de "pendente" para essa linha específica, distinguindo-a das linhas com limite já definido.

## O que está sólido (reconfirmado nesta rodada, do zero)

**Gestor**
- A conta do ganho está consistente em faturas (não linhas) em todos os quatro modos e nos dois registros — reconferi 6.902 faturas, 91,0% legítimas, £6.761 de ganho central, sem nenhum leftover do número antigo (£200, 2,01%, 97%).
- O plano de controle não dispara mais em meses legítimos: o limiar de 20% vs. média móvel de 3 meses está documentado com a maior queda histórica observada (-14,2% receita, -10,7% pedidos).

**Especialista do domínio**
- A dupla trava (separação como primeira linha, checkout como reforço condicionado) está bem explicada nos dois registros, com a troca declarada explicitamente ("menos risco de erro físico vs. mais risco de abandono de cliente").

**Cientista de dados sênior**
- H5 pré-registrada e testada antes de H1/H2 continua com o mesmo rigor (Breslow-Day p<0,0001, correção de Holm).
- O critério de H4 (limite inferior do IC de Wilson ≥2x, não taxa pontual) está corretamente propagado nos quatro modos: 66 produtos, 23,4% de cobertura, sem nenhuma menção residual a "198" fora do contexto histórico da própria correção.
- Zero ocorrências de sobreposição de rótulos em toda a checagem automática desta rodada (`sobreposicao.md`), nos quatro modos, três temas e dois dispositivos — os achados M1 e M4 das rodadas anteriores (rótulo sobre a linha, rótulos de eixo sobre bolha) estão de fato resolvidos.

**Recrutador de dados**
- "Poka-yoke" não aparece mais em nenhum lugar do registro Simples (Painel e Relatório) — confirmado por busca no texto capturado; o achado M2 da rodada 2 está totalmente resolvido, não só parcialmente.
- Atribuição de autoria (GitHub) presente em todos os quatro modos, nos dois registros — confirmado nesta captura também.

## Cobertura dos roteiros

| Revisor | Itens | OK | Achado | Não se aplica |
|---|---|---|---|---|
| Gestor | 8 (G1–G8) | 6 | 2 (V3 via G1/G8, V5 via G5/G7) | 0 |
| Especialista do domínio | 8 (E1–E8) | 8 | 0 | 0 |
| Cientista de dados sênior | 12 (T1–T12) | 9 | 2 (V2 via T11, V1 via T4/T11) | 1 (T9 — projeto não constrói modelo preditivo comparado com baseline) |
| Recrutador de dados | 8 (R1–R8) | 7 | 1 (V4 via R2/R6) | 0 |

Notas de cobertura, item a item relevante:

- **G1** — "Consigo dizer em uma frase o que a página pede que eu faça, quem faz e quando?" OK: Painel, tabela "O que acompanhar" — cinco linhas com dono e frequência, mais a ação de separação (V5 registra a ressalva sobre a linha sem limite, mas a ação e o dono estão claros).
- **G2** — "A ação principal tem conta?" OK: a ação de segmento tem conta completa (seção 10); H4 tem a lacuna declarada explicitamente (não é omissão silenciosa) — já era achado I5 da rodada 1, resolvido, reconfirmado aqui.
- **G3** ▸ — diferença para a meta = +0,05pp; intervalo do número principal = 1,99%–2,10%; a meta está no limite inferior do intervalo — Painel e Relatório já reconhecem isso explicitamente ("a meta cai bem na borda da margem de erro"). OK, achado I1 da rodada 1 continua resolvido.
- **G4** — "O ganho sobrevive ao pior cenário plausível?" OK: cenário conservador mostra prejuízo (-£14.441), declarado sem suavização.
- **G5** — "O plano de controle funciona na rotina?" Achado V5 (linha sem limite definido) e reconfirmação de que o alarme de faturamento/pedidos não dispara mais por sazonalidade normal.
- **G6** — "Que risco para o negócio a página não mencionou?" OK: FMEA cobre fricção em cliente de alto volume, regra aplicada fora do UK, lista desatualizada — não achei risco relevante ausente nesta rodada.
- **G7** — "O que eu pediria na reunião antes de aprovar?" Achado V5 — a linha de alarme "a definir" é exatamente o tipo de pergunta que sobra para a reunião.
- **G8** — "Os títulos dos slides contam a história sozinhos?" OK: os 9 títulos, lidos isoladamente, descrevem a ação e a ressalva corretamente (conferi nos dois registros).
- **E1–E2, E4–E8** — OK, sem achado novo nesta rodada; processo, vocabulário, premissas e limitações seguem consistentes com o que já foi confirmado nas rodadas 1 e 2.
- **E3** — "A contramedida atua na etapa onde a causa nasce?" OK: a ação de separação (picking) ataca a causa suspeita diretamente; o checkout é declarado como camada adicional, não como a única trava — achado I6 da rodada 1 continua resolvido.
- **T1** — "Os números batem entre si?" OK: nenhum número desatualizado encontrado em nenhum dos oito arquivos de texto capturados (busca dedicada por 2,01%, £200, 97%, 198, 23166-como-1º — zero ocorrências fora de contexto histórico).
- **T2** ▸ — maior item do ranking de impacto agora é 22423, £17.632 ÷ £299.135 = 5,9% do total — bem abaixo do limiar de 20% que exigiria suspeita; achado C1 da rodada 1 continua resolvido.
- **T3** — OK, IC de Wilson calculado sobre o número principal, com a ressalva de que a meta cai na borda já declarada (ligado a G3/I1).
- **T4** — matriz mostra "n insuf." (achado V1, de legibilidade, não de honestidade — o piso de n está corretamente aplicado); gráfico de dispersão não mostra n explicitamente mas usa área proporcional à receita, critério já auditado nas rodadas anteriores.
- **T5** — OK: critério de H4 agora usa limite inferior do IC, controla falso positivo, reconfirmado.
- **T6** — OK: linguagem causal proporcional à evidência (H1/H2 "estatisticamente confirmadas, praticamente refutadas"; H4 "confirmada, estatística e praticamente").
- **T7** — OK: holdout, censura à direita explicada com evidência de queda monotônica.
- **T8** — OK: desenho experimental recalculado corretamente em nível de fatura (793/braço, taxa-base 9,04%).
- **T9** — NÃO SE APLICA: o projeto não constrói um modelo preditivo a ser comparado com um baseline simples; é análise de causa raiz e experimentação, não classificação/regressão.
- **T10** — OK: as duas exclusões de outlier (23843, 23166) documentadas lado a lado com o mesmo critério.
- **T11** — achados V1 e V2 (legibilidade da matriz; zoom quebrado no gráfico de dispersão); zero sobreposição de rótulos confirmada em todos os modos/temas/dispositivos capturados.
- **T12** — OK: nível 2 usado para confirmar V2 diretamente no comportamento da página (não no código-fonte da análise).
- **R1** — OK: GitHub no rodapé de todos os modos.
- **R2** — "Em 30 segundos, entendo o problema e o resultado sem rolar?" Achado V4 registra a ressalva sobre o cartão "+0,00" no Dashboard não ser a primeira tela relevante para essa pergunta (o Painel, que é a primeira tela, continua OK nesse critério).
- **R3–R5, R7–R8** — OK, sem achado novo.
- **R6** — "O essencial é acessível, e a profundidade é opcional?" OK, com a ressalva de V1/V3/V4 sobre alguns elementos "essenciais" (cartões, matriz) precisarem de contexto adicional para não parecerem quebrados.

## Matriz de achados

Ver `matriz-achados-v3.md`.

## Limites desta revisão

- Não consegui reproduzir literalmente "zero bolhas" no gráfico de dispersão nesta bateria de testes — encontrei e confirmei uma causa plausível (zoom não funcional) mas não o sintoma exato relatado. Se o problema persistir depois de corrigido o zoom, vale reproduzir com o navegador e os passos exatos usados originalmente.
- Não testei a interação de zoom em touch (celular) — os testes de arrastar/Ctrl+roda foram feitos com mouse simulado, em desktop.
- Mesma lacuna de cobertura das rodadas anteriores: celular e escuro não cobriram o registro Técnico; Slides em Técnico não teve os 9 slides percorridos na captura de texto (limitação do script/sessão do navegador).
- Nível 2 usado apenas para: (a) testar a interação de zoom diretamente na página (V2), e (b) conferir, por leitura de texto, que os números da rodada 2 se propagaram sem leftover — não houve nova auditoria de código de análise além do que já foi feito nas rodadas 1 e 2.
- Como nas rodadas anteriores, esta conversa tem acesso ao repositório local (mesmo diretório de trabalho), o que permitiu os testes de nível 2 sem clonar nada — registrado por transparência.
