# Dossiê DMAIC — online_retail.csv

## P0-P · Contexto mestre

```
# CONTEXTO MESTRE — Cancelamentos e Devoluções no Online Retail (UCI)

Você é meu parceiro metodológico e técnico num projeto de análise conduzido por
DMAIC (Lean Seis Sigma), na modalidade portfólio.

## A situação
Não tenho cliente nem pergunta dada. Escolhi este dataset por interesse e a ordem
natural está invertida: os dados vieram antes do problema. Objetivo duplo:
produzir análise defensável e demonstrar método a quem avaliar.

## Regras permanentes
1. Fases na ordem: Fase 0 → Define → Measure → Analyze → Improve → Control. Ao fim
   de cada uma, TOLLGATE: OK / RESSALVA / FALHA por critério, e veredito APROVADO
   ou REPROVADO com o que falta.
2. SEPARAÇÃO ESTRUTURA/RELAÇÃO: nas fases 0 e Measure olhamos estrutura,
   procedência e qualidade. Relações entre variáveis só no Analyze. Se eu pedir
   correlação ou cruzamento antes disso, recuse e me lembre da regra.
3. ANTI-GARIMPO: hipótese só é testada depois de escrita e datada, com origem
   rastreável. Hipótese nascida de olhar os dados é legítima, mas vale menos como
   evidência causal, e isso fica escrito.
4. Rotule: [DADO] / [INFERÊNCIA] com confiança e base / [PREMISSA].
5. Nunca invente número. Faltou dado, pare e peça.
6. Antes de explicar variação, classifique: causa comum ou causa especial.
7. Correlação não é causalidade.
8. A análise mais simples que responde à pergunta. Se eu propuser complexidade que
   não muda decisão nenhuma, me diga.
9. HONESTIDADE DE PORTFÓLIO: não me deixe apresentar premissa como fato,
   stakeholder simulado como real, nem achado exploratório como confirmatório.

## REGRA ESPECÍFICA DESTE PROJETO — Vazamento por ausência de chave de ligação entre pedido e cancelamento
Este dataset não tem uma coluna que ligue um InvoiceNo de cancelamento (prefixo
"C") ao InvoiceNo original que ele cancela. Essa ligação vai precisar ser inferida
por CustomerID + StockCode + proximidade de InvoiceDate — e isso é uma construção
minha, não um fato do dado. Regras:
- Se eu pedir para "prever cancelamento" usando qualquer coluna que só existe na
  própria linha de cancelamento (Quantity negativo, o próprio InvoiceNo com "C"),
  me pare: isso é circular, o cancelamento está definindo a si mesmo.
- Todo preditor de cancelamento tem que vir do pedido ORIGINAL, no momento da
  compra — não da linha de devolução.
- Se eu quiser pular direto para "quais produtos cancelam mais" sem antes
  confirmar que a lógica de pareamento pedido↔cancelamento está registrada e
  validada (Fase 0, item 3), recuse.
- StockCode tem códigos que não são produto (ex.: "POST", "D", "M", "BANK
  CHARGES", "C2", "DOT", "CRUK", cartão-presente) — se eu tratar essas linhas como
  produto num Pareto ou numa contagem de defeito, me avise e proponha excluir ou
  segregar.
- Granularidade: uma linha é item-dentro-de-pedido (InvoiceNo × StockCode), não um
  pedido. Se eu misturar contagem de linhas com contagem de pedidos sem dizer qual
  estou usando, pare e peça que eu decida.

## Contrato de trabalho no repositório
Você tem autonomia sobre a organização deste projeto: crie, nomeie e reorganize
pastas e arquivos, refatore, extraia módulos, escreva testes — do jeito que fizer
mais sentido para este problema. Não me peça permissão a cada passo; prefiro que
proponha e execute. Ao mexer na estrutura, diga em uma linha o que mudou e por quê.

Três artefatos fogem dessa liberdade, porque são prova e não organização. Você
decide onde ficam e como se chamam, mas uma vez criados são IMUTÁVEIS:
  - o pré-registro datado das hipóteses
  - o baseline congelado
  - a quarentena do holdout
Correção neles é adendo datado ao final do arquivo, nunca edição silenciosa. Se
algum estiver errado, pare e me avise — não corrija por conta própria.

## Regra do holdout
Eixo temporal: InvoiceDate. Confirme primeiro o intervalo exato no profiling da
Fase 0 (minha inferência não verificada é dez/2010 a dez/2011 — cerca de 12
meses, um único ciclo sazonal completo, o que já é uma limitação: não dá para
isolar um ciclo sazonal inteiro dentro do holdout sem também tirá-lo do
treino). Corte proposto: os últimos ~2 meses da série (a partir de outubro ou
novembro, conforme a data máxima confirmada) viram quarentena de holdout; o
resto é janela de exploração. Declare no README que, com um único ano de dados,
a confirmação de estabilidade sazonal é estruturalmente mais fraca do que com
múltiplos anos — não force o contrário.
Este recorte está proibido até a fase Control. Não leia, não carregue, não
inspecione, não use "só para conferir". Se um script tocar esse caminho antes da
fase Control, isso é um defeito do projeto: recuse e me avise.

## Rastro
Ao passar cada tollgate, registre o veredito e faça commit. O commit datado do
pré-registro é a minha prova de que as hipóteses vieram antes da análise — é
artefato de evidência, não burocracia.

## Ficha
- Dataset: online_retail.csv — UCI Machine Learning Repository, "Online Retail"
  (Chen, Sain & Guo, 2012). [INFERÊNCIA, confiança alta pelo formato exato de
  colunas e contagem de linhas — confirmar fonte e licença antes de citar]
- Procedência: real. Transações de um varejista online do Reino Unido
  especializado em presentes/utilidades, muitos clientes parecem ser
  revendedores (quantidades por linha frequentemente altas). [INFERÊNCIA a
  confirmar no profiling — não é dado sintético, então a fase Measure é MSA
  real de procedência, não auditoria de placeholder]
- Escopo: 541.909 linhas (contagem de arquivo, sem header). Período aproximado
  dez/2010–dez/2011 [INFERÊNCIA, confirmar min/max de InvoiceDate na Fase 0].
- Granularidade: uma linha = um item de produto dentro de uma fatura
  (InvoiceNo × StockCode). NÃO é um pedido nem um cliente — decisão de
  granularidade do defeito fica para o Define (ver P2-P).
- Colunas:
  - Identificadores: InvoiceNo (prefixo "C" = cancelamento), StockCode,
    CustomerID
  - Temporal: InvoiceDate
  - Dimensões: Description, Country
  - Medidas: Quantity, UnitPrice
  - Candidata a desfecho: InvoiceNo com prefixo "C" + Quantity negativo
    (cancelamento/devolução)
- Stack: Python 3 — pandas, numpy, scipy, statsmodels, matplotlib/seaborn
- Tempo disponível: <preencha>
- Objetivo: peça central de portfólio
- Domínio prévio: não tenho experiência real em varejo/e-commerce B2B de
  giftware. A reconstrução de processo na Fase 0 é inferência minha e da IA,
  não conhecimento de setor — vou buscar referências externas (ver item GEMBA
  DOCUMENTAL da Fase 0) em vez de assumir que está certa.
```

---

## P1-P · Fase 0 · Arqueologia do processo

Rode este logo após o P0-P, com o dado já carregado.

```
# FASE 0 — RECONHECIMENTO · Arqueologia do processo

REGRA: aqui olhamos estrutura e procedência. Nada de correlação, cruzamento ou
importância de variável. Se eu pedir, recuse — isso é Analyze.

## Insumo
Rode e cole aqui:
- shape, dtypes, e contagem de nulos por coluna (InvoiceNo, StockCode,
  Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country)
- min/max de InvoiceDate, e contagem de InvoiceDate por mês (para eu ver a
  cobertura real antes de fixar o corte de holdout do P0-P)
- contagem de valores únicos de InvoiceNo, StockCode, CustomerID, Country
- quantas linhas têm InvoiceNo começando com "C"; quantas têm Quantity < 0;
  a diferença entre esses dois conjuntos (linhas com Quantity<0 mas sem "C",
  e vice-versa)
- top 20 valores de StockCode por frequência, para eu ver quantos são código
  de produto real e quantos são "POST"/"D"/"M"/"BANK CHARGES"/"C2"/"DOT" etc.
- distribuição de Country (contagem de linhas por país)

## Tarefas
1. SIPOC REVERSO — reconstrua o processo real que teria gerado cada coluna.
   Marque cada etapa [EVIDENTE NO DADO] ou [INFERIDA]. Aponte as etapas que o
   dataset não registra: confirmação de pagamento, separação/embalagem do
   pedido, motivo declarado do cancelamento, custo de frete de devolução,
   contato do cliente antes de cancelar.

2. LINHA DO TEMPO DE UMA UNIDADE — narre o ciclo de vida de um pedido dizendo
   quando cada coluna é preenchida. Depois responda:
   a coluna InvoiceDate da fatura de cancelamento é preenchida necessariamente
   DEPOIS da InvoiceDate da fatura original que ela cancela — isso é sempre
   verdade neste dado, ou existe caso de cancelamento com data igual/anterior
   (o que sinalizaria erro de relógio ou reuso de InvoiceNo)? Description é
   preenchida uma vez por StockCode ou varia entre linhas com o mesmo
   StockCode (indício de erro de digitação/normalização)? UnitPrice de um
   mesmo StockCode varia entre faturas (promoção, negociação, ou erro)?

3. TESTE DE ARMADILHA PRIORITÁRIA — este é o item mais importante da fase.
   Não existe coluna que ligue uma fatura de cancelamento ("C...") à fatura
   original que ela cancela. Proponha e teste uma lógica de pareamento por
   CustomerID + StockCode + janela de tempo (ex.: cancelamento casado com o
   pedido do mesmo cliente/produto mais próximo no passado). Rode nos dados:
   quantas linhas de cancelamento conseguem achar um pedido original candidato
   sob essa regra? Quantas ficam órfãs (cliente nulo, ou nenhum pedido anterior
   compatível)? Se a taxa de pareamento for baixa, diga sem suavizar que a
   análise de causa de cancelamento vai ter que trabalhar com uma amostra
   enviesada (só os casos pareáveis) e que isso entra nas limitações.

4. ATORES E INCENTIVOS — que papéis tocam este processo (atendente que lança o
   pedido, cliente que compra ou devolve, operador de estoque que separa),
   quem preenche o quê, onde há incentivo para registrar errado, tarde ou não
   registrar (ex.: CustomerID nulo em check-out sem cadastro, quantidade
   negativa lançada como ajuste manual de estoque em vez de devolução real
   — StockCode "M" ou "D" são candidatos a isso, confirme na contagem do
   Insumo).

5. DEFEITO — desenvolva a definição operacional de "pedido cancelado/devolvido":
   o que conta (fatura com InvoiceNo "C" pareada a um pedido original), o que
   não conta (linhas de ajuste sem StockCode de produto real, ex. "BANK
   CHARGES", "POSTAGE"), casos de borda (cancelamento parcial — só algumas
   linhas do pedido original voltam; CustomerID nulo no pedido original,
   impossibilitando o pareamento), e a decisão de unidade: defeito é por
   PEDIDO (InvoiceNo) ou por LINHA (InvoiceNo × StockCode)? Argumente os dois
   lados — pedido é a unidade de decisão comercial, linha é a unidade de
   estoque/produto.

6. CTQ — que características o cliente final deste processo valorizaria
   (entrega correta, preço estável, disponibilidade), e quais são mensuráveis
   aqui? Inclua a tensão central: reduzir cancelamento pode significar mais
   fricção no checkout (verificação, confirmação), o que reduz conversão —
   essas duas grandezas competem.

7. GEMBA DOCUMENTAL — busque: "UK e-commerce return rate benchmark",
   "online retail order cancellation rate industry average", "B2B wholesale
   giftware return rate", "UCI Online Retail dataset Chen 2012 paper" (para
   confirmar a fonte e o que os autores originais documentaram sobre coleta).

8. O QUE O DADO NÃO REGISTRA — motivo do cancelamento, custo de devolução/frete
   reverso, se o cliente foi recontatado, pedidos abandonados no carrinho
   (nunca viram InvoiceNo), clientes que desistiram de comprar de novo depois
   de um cancelamento ruim. Diga o efeito de cada ausência sobre o que se pode
   concluir — em especial sobre a fase Improve, que vai precisar de ponto de
   indiferença em vez de ganho bruto por causa disso.

## Saída
Memorando de 1 página + três perguntas candidatas com decisor nomeado + o
veredito do teste de pareamento cancelamento↔pedido original (item 3), que
determina se o projeto segue em nível de pedido, linha, ou precisa ser
reposicionado para "taxa de devolução por produto/país" sem tentar rastrear o
pedido original.

## Tollgate 0
- Taxa de pareamento cancelamento↔pedido original está medida e registrada,
  não estimada de cabeça.
- A distinção StockCode-produto vs StockCode-não-produto está decidida e
  documentada, com a lista de códigos excluídos.
- A granularidade do defeito (pedido vs linha) está decidida, não em aberto.
- As três perguntas candidatas têm decisor nomeado, não genérico ("o negócio").
```

---

## P2-P · Define · Charter e pré-registro

```
# FASE 1 — DEFINE · Charter e pré-registro

Vou fechar a pergunta antes de olhar relações. Este documento será datado e
versionado como prova de que não garimpei resultado.

## Insumo
Memorando da Fase 0 + veredito do teste de pareamento cancelamento↔pedido +
lista de StockCodes não-produto excluídos.

## Pergunta escolhida
Onde e por que os pedidos deste varejista são cancelados/devolvidos, e qual
mudança (em segmento de cliente, produto, país ou faixa de quantidade)
reduziria a taxa de cancelamento sem sacrificar o volume de vendas atendido.

## Tarefas
1. PERSONA DE DECISÃO — declare, não finja: Gerente de Operações/Atendimento
   ao Cliente (persona derivada da alavanca: quem decide adicionar fricção de
   verificação — ex. confirmação por e-mail/telefone antes de despachar —
   para segmentos de risco, ou manter checkout sem fricção). Decide
   semanalmente, sobre o volume de pedidos da semana, e faria diferente
   conforme o resultado: se a taxa de cancelamento de um segmento (país,
   faixa de quantidade, categoria de produto) estiver estruturalmente acima
   da meta, adiciona verificação prévia para aquele segmento; se estiver
   dentro, mantém frictionless. Tudo como [PREMISSA DECLARADA]. Escreva a
   frase de honestidade do README: "Este stakeholder é simulado; as premissas
   sobre sua alçada e seus incentivos estão registradas neste Define, não
   confirmadas com nenhuma pessoa real."
   Avalie também a persona alternativa antes de descartá-la: Gerente
   Comercial decidindo termos de conta para clientes de alto volume
   (possíveis revendedores) com alta taxa de cancelamento — diga por que
   escolheu uma e não a outra, ou se cabem as duas em fases diferentes.

2. PROBLEMA EM UMA FRASE:
   "Em <escopo: pedidos de dez/2010 a dez/2011, unidade decidida na Fase 0>,
   a taxa de cancelamento/devolução está em <a medir na Fase 2B> quando a
   meta é <valor + origem>, representando <impacto em receita perdida ou
   linhas afetadas> por <período>."
   Meta: busque benchmark externo (ver GEMBA DOCUMENTAL da Fase 0) com fonte
   citável. Não achando um comparável (setor de giftware B2B é nicho), use
   meta interna — por exemplo o melhor quartil histórico entre países ou
   entre meses — e declare explicitamente que é proposta, não referência de
   mercado.

3. DEFINIÇÃO OPERACIONAL do defeito e da métrica primária: unidade decidida
   na Fase 0 (pedido ou linha); o que conta como cancelado (fatura "C" pareada
   a um pedido original sob a regra de pareamento validada); o que não conta
   (ajustes de estoque, taxas, postagem); janela (por mês de InvoiceDate do
   pedido original); casos de borda: cancelamento parcial de um pedido de
   múltiplas linhas, CustomerID nulo impedindo pareamento, cancelamento sem
   par original encontrado. Liste as ambiguidades remanescentes.

4. MÉTRICAS SECUNDÁRIAS E GUARDRAILS — a armadilha de otimização local aqui:
   é possível "melhorar" a taxa de cancelamento simplesmente dificultando o
   checkout ao ponto de afastar clientes legítimos, o que reduziria pedidos
   totais sem reduzir a insatisfação real. Guardrail: acompanhar volume total
   de pedidos e receita bruta junto com a taxa de cancelamento — uma
   recomendação que reduz cancelamento mas derruba volume não passa.

5. HIPÓTESES PRÉ-REGISTRADAS — direcionais, com origem rotulada, teste
   planejado e efeito mínimo acionável:
   H1 [INSPEÇÃO ESTRUTURAL] Pedidos com Quantity total alta (típico de
      compra por revendedor) têm taxa de cancelamento maior que pedidos de
      quantidade baixa, por erro de picking/estoque em lotes grandes.
      Teste: comparação de taxa por quartil de Quantity agregada por
      InvoiceNo. Efeito mínimo: diferença de taxa ≥ 3 p.p. entre quartil
      superior e inferior.
   H2 [INSPEÇÃO ESTRUTURAL] Pedidos de Country fora do Reino Unido têm taxa
      de cancelamento maior que UK, por custo/tempo de frete e alfândega.
      Teste: comparação de proporções UK vs não-UK, com atenção a n por país
      (a maioria dos países terá poucos pedidos — declarar quais não
      sustentam teste individual e agrupar em "UK" vs "resto").
      Efeito mínimo: diferença de taxa ≥ 5 p.p.
   H3 [TEORIA DE DOMÍNIO] Pedidos feitos no pico sazonal (novembro–dezembro)
      têm taxa de cancelamento maior que no resto do ano, por erro
      operacional sob alta carga de separação/embalagem.
      Teste: taxa mensal, carta p ou I-MR conforme decidido na Fase 2B.
      Efeito mínimo: diferença de taxa ≥ 2 p.p. entre pico e não-pico.
   H4 [INSPEÇÃO ESTRUTURAL] Certos StockCodes concentram taxa de
      cancelamento muito acima da média do catálogo (produto
      problemático — frágil, descrição enganosa, etc).
      Teste: Pareto de taxa de cancelamento por StockCode, com corte mínimo
      de n por produto para entrar no ranking.
      Efeito mínimo: produtos no top do Pareto com taxa ≥ 2x a média geral.
   H5 — RIVAL ESTRUTURAL de H1 e H2 [INSPEÇÃO ESTRUTURAL] O efeito
      "quantidade alta → mais cancelamento" (H1) é artefato de composição:
      pedidos de quantidade alta se concentram em poucos CustomerID
      (grandes revendedores) e/ou em países específicos que já têm taxa de
      cancelamento estruturalmente maior por outro motivo (ex.: são clientes
      novos testando o fornecedor, não o volume em si). Alternativa de
      seleção: clientes em sua primeira compra registrada cancelam mais,
      independente de quantidade, e quantidade alta correlaciona com
      primeira compra.
      Teste: efeito de Quantity dentro de estratos de CustomerID (cliente
      recorrente vs primeira compra) e de Country. Se o efeito de H1 sumir
      ou inverter dentro dos estratos, é composição/seleção, não causa.
      Esta hipótese é testada ANTES de H1, não depois.

6. ANTI-GARIMPO — holdout: últimos ~2 meses de InvoiceDate (corte exato a
   confirmar com o intervalo real levantado na Fase 0), isolados até Control,
   nunca inspecionados antes. Correção para múltiplos testes: 5 hipóteses
   pré-registradas + eventuais subtestes de estratificação em H5 → aplicar
   Bonferroni ou Holm sobre o conjunto de testes confirmatórios (não sobre
   explorações posteriores, que ficam rotuladas como exploratórias).

7. ESCOPO — DENTRO: cancelamento/devolução de pedidos com CustomerID
   presente e StockCode de produto real. FORA (já inviável pela Fase 0):
   motivo declarado do cancelamento (não existe no dado), custo de frete
   reverso (não existe), qualquer afirmação sobre pedidos abandonados no
   carrinho (não existe no dado). A DECIDIR: se cancelamento parcial de
   pedido conta como defeito do pedido inteiro ou só das linhas afetadas.

8. CRITÉRIO DE SUCESSO — o projeto vale mesmo se H1 a H4 forem refutadas e
   restar só a conclusão de H5 (composição/seleção em vez de causa): isso
   ainda é uma descoberta acionável — significa que a alavanca certa é
   segmentação de cliente, não política de quantidade mínima por pedido — e
   deve ser registrada como tal, não como fracasso do projeto.

## Tollgate DEFINE
- Meta do Charter tem origem citada (benchmark externo) ou está marcada como
  proposta interna, nunca apresentada como referência de mercado sem ser.
- As 5 hipóteses estão datadas e versionadas antes de qualquer teste.
- H5 (rival) está marcada para ser testada antes de H1/H2, não depois.
- A decisão de granularidade (pedido vs linha) está fechada, sem "decidir
  depois".
```

---

## Measure 2A · MSA / auditoria de procedência

```
# FASE 2A — MEASURE · Procedência e qualidade do dado

Não há acesso a quem gera o dado (sistema de e-commerce do varejista original)
— isto é auditoria de procedência, não MSA clássico com operador/instrumento
reais. Trate como tal: as seis dimensões avaliam a base como registro
histórico fixo, não um sistema de medição vivo que eu possa recalibrar.

## Insumo
Resultado bruto de cada teste abaixo, código incluído — não a descrição do
teste, o resultado rodado.

## Tarefas
1. PERFIL — confirme: chave candidata é (InvoiceNo, StockCode)? Existe
   duplicata exata dessa combinação (mesma fatura, mesmo produto, duas
   linhas)? Contagem de InvoiceNo únicos, StockCode únicos, CustomerID únicos,
   e quantos InvoiceNo têm prefixo "C".

2. AUDITORIA DAS SEIS DIMENSÕES, cada uma com teste e critério de aceite.
   Gere o código que imprime aprovado/reprovado e o volume afetado:
   - Completude — CustomerID nulo (quanto, e se concentra em algum Country ou
     período); Description nula quando StockCode existe.
   - Unicidade — linhas duplicadas exatas (todas as colunas iguais); mesma
     (InvoiceNo, StockCode) aparecendo mais de uma vez com Quantity
     diferente (indício de lançamento retificado, não de erro).
   - Validade — Quantity = 0 (deveria existir?); UnitPrice <= 0 e o que essas
     linhas representam (StockCode "M"/"D"/"BANK CHARGES" etc. vs produto
     real com preço zerado); InvoiceDate fora do intervalo plausível do
     dataset; Country com valores inconsistentes de grafia (ex. "EIRE" vs
     variações).
   - Consistência — um mesmo StockCode deveria ter uma Description estável;
     meça quantas descrições distintas por StockCode existem e se isso é
     erro de digitação ou produto reaproveitado com nome diferente; um mesmo
     CustomerID deveria ter um único Country predominante — quantos têm mais
     de um?
   - Acurácia — não há como verificar contra fonte externa linha a linha;
     declare isso em vez de simular um teste que não existe.
   - Pontualidade — meça a cobertura de InvoiceDate por mês (há meses com
     poucas linhas, sugerindo corte de coleta?); registros fora de ordem
     cronológica dentro do mesmo InvoiceNo.

3. TESTE DE ARTIFICIALIDADE — não é a suspeita principal aqui (o formato e a
   sujeira do dado — descrições inconsistentes, StockCodes não-produto,
   quantidades negativas irregulares — são assinatura de dado real, não
   sintético), mas rode mesmo assim como checagem barata: Quantity e
   UnitPrice têm cauda longa e outliers reais, ou são discretos demais? Lei
   de Benford no primeiro dígito de UnitPrice*Quantity. Se tudo vier "limpo
   demais", reabra a suspeita.

4. VIESES — seleção: só pedidos efetivamente registrados aparecem, não
   carrinhos abandonados nem tentativas de compra rejeitadas (cartão
   recusado etc.) — não existe no dado. Sobrevivência: um CustomerID só
   existe se fez ao menos uma compra completa; clientes que desistiram antes
   da primeira compra são invisíveis. Vazamento: reforce o teste de
   pareamento cancelamento↔pedido original feito na Fase 0 — confirme que
   nenhuma feature usada como preditor no Analyze vem de depois do momento
   do pedido original.

5. ERRO INDETECTÁVEL — não dá para saber, só com estas colunas, se um
   cancelamento foi iniciativa do cliente ou anulação por erro do próprio
   varejista (ex. pedido duplicado por engano), nem se um UnitPrice de fato
   cobrado difere do registrado (desconto verbal, erro de sistema). Vai para
   as limitações do README.

6. VEREDITO FIT-FOR-PURPOSE — a base sustenta bem "onde e para quem a taxa
   de cancelamento é maior" (descritivo/estratificado); não sustenta "por
   que o cliente cancelou" no nível de motivo declarado, nem "quanto custou
   cada devolução" (sem custo de frete reverso/reposição). Diga isso com
   todas as letras e proponha registrar como limitação declarada no README,
   não como falha do projeto — a base ainda sustenta a pergunta de
   priorização de segmento, só não a pergunta de causa individual fina.

## Tollgate
- As seis dimensões foram rodadas com código, não estimadas.
- A taxa de pareamento cancelamento↔pedido original (herdada da Fase 0) está
  confirmada como estável o suficiente para sustentar o Analyze, ou o projeto
  foi formalmente reposicionado para nível agregado (produto/país/mês) sem
  tentar rastrear pedido individual.
- Lista de StockCodes não-produto excluídos está fechada e documentada.
```

---

## Measure 2B · Baseline, estabilidade e capabilidade

```
# FASE 2B — MEASURE · Baseline, estabilidade e capabilidade

Trabalhe apenas na janela de exploração (exclui os últimos ~2 meses de
InvoiceDate reservados como holdout no Define). O holdout permanece fechado.

## Tarefas
1. BASELINE — taxa de cancelamento (na unidade decidida no Define — pedido ou
   linha) com intervalo de confiança. Como o defeito é binário, complemente
   com DPMO e nível sigma. Peça também a distribuição de Quantity e UnitPrice
   por linha (forma, não só média) — são as duas medidas contínuas centrais
   deste processo.

2. ESTABILIDADE — carta p (proporção de cancelamento por período, já que a
   unidade é atributo binário e o tamanho de amostra por período varia mês a
   mês); justifique contra I-MR (que seria a escolha se o foco fosse
   Quantity/UnitPrice, não taxa de defeito). Agregação recomendada: mensal
   (dá entre 12 e 14 pontos na janela de exploração — perto do mínimo de 20
   citado na metodologia; diga isso e considere agregação semanal como
   alternativa para ganhar pontos, avaliando o trade-off de instabilidade de
   n por semana). Regras de Nelson sobre a carta. Consequência prática: se a
   variação mês a mês for causa comum, a resposta não é cobrar meta mensal de
   cancelamento da operação, é mudar política estrutural (ex. checkout,
   política de devolução).

3. CAPABILIDADE — taxa de cancelamento observada contra a meta do Charter
   (benchmark externo ou meta interna declarada). Traduza em uma frase de
   negócio: quantos pedidos a mais por mês seriam "conformes" se a meta fosse
   atingida.

4. ESTRATIFICAÇÃO E PARETO — dimensões: Country, faixa de Quantity (quartil),
   StockCode/categoria de produto, CustomerID novo-vs-recorrente. Dois
   Paretos obrigatórios: um por TAXA de cancelamento (aponta segmento de
   maior risco proporcional) e um por IMPACTO ABSOLUTO (linhas/receita
   cancelada, aponta onde o volume dói mais). Diga explicitamente se são o
   mesmo segmento ou não, e qual dos dois orienta a recomendação da Improve.

5. TAMANHO DE AMOSTRA — poder disponível para os efeitos mínimos
   pré-registrados em H1–H4. A maioria dos ~38 países terá poucas linhas —
   liste quais países não sustentam teste individual (n insuficiente) e
   precisam ser agrupados em "UK" vs "resto" ou descartados do teste por
   país.

6. CÓDIGO — gere tudo, com gráficos: carta p com limites e pontos fora de
   controle rotulados por mês; os dois Paretos com o corte de 80% marcado;
   histograma de Quantity e UnitPrice com outliers marcados.

7. CONGELAMENTO — bloco de baseline para versionar: taxa de cancelamento,
   intervalo de confiança, janela de exploração usada, filtros aplicados
   (StockCodes excluídos, linhas com CustomerID nulo tratadas como),
   data.

## Tollgate
- Carta de controle rodada com agregação declarada e justificada, ponto de
  atenção sobre o número de pontos citado explicitamente.
- Os dois Paretos (taxa e impacto) apontam segmentos comparados lado a lado,
  não só um dos dois.
- Baseline congelado como artefato imutável, com todos os filtros listados.
```

---

## Analyze · Causa raiz

```
# FASE 3 — ANALYZE · Causa raiz

Ainda na janela de exploração. Holdout fechado.
Regra: nenhuma causa entra na lista final sem evidência quantitativa.

## Tarefas
1. ISHIKAWA adaptado — categorias deste processo (não as 6M industriais):
   Cliente (novo vs recorrente, país, porte da compra), Produto (categoria,
   preço, StockCode específico), Operação (época do ano/carga de pedidos,
   possível erro de picking em lotes grandes), Sistema de registro (StockCode
   não-produto misturado, CustomerID nulo). Para cada causa: é testável aqui?
   Marque como impossível de testar: motivo declarado do cliente, erro
   humano específico do operador (não identificado individualmente na base)
   — vão para limitações.

2. HIPÓTESE RIVAL ESTRUTURAL PRIMEIRO (H5 do Define). É a quantidade do
   pedido que causa cancelamento, ou é a composição de clientes/países que
   compram em grande quantidade que já cancela mais por outro motivo? Peça:
   efeito bruto de Quantity sobre taxa de cancelamento versus efeito dentro
   de estratos de CustomerID (novo vs recorrente) e de Country; verificação
   de Simpson entre agregado e estratificado; se a base não permitir separar
   os dois efeitos com confiança (ex. poucos clientes recorrentes de alto
   volume para comparar), exigir que isso seja dito e que o custo em força da
   conclusão de H1 seja declarado.

3. HIPÓTESE PRINCIPAL — teste de H1 (Quantity) e H2 (Country) e H3
   (sazonalidade) e H4 (StockCode) na ordem do pré-registro, cada um com o
   formato de saída que vai alimentar a recomendação da Improve: qual
   segmento concreto (ex. "pedidos de Quantity total acima do 3º quartil
   originados de clientes na primeira compra") entra na lista de segmentos
   de risco.

4. RETOMADA DA ARMADILHA PRIORITÁRIA — se a taxa de pareamento
   cancelamento↔pedido original (Fase 0/2A) ficou baixa, ajuste a redação de
   toda conclusão sobre "causa" de cancelamento para deixar claro que ela
   vale só para o subconjunto pareável, não para o total de cancelamentos
   observados. Não deixe nenhum gráfico apresentar essa amostra parcial como
   se fosse o universo completo de cancelamentos.

5. TESTES — H0/H1 para cada hipótese, teste e justificativa (proporção,
   qui-quadrado ou regressão logística conforme o número de fatores),
   premissas e verificação, alfa ajustado pela correção pré-registrada no
   Define, poder, n por segmento, efeito mínimo prático herdado do Define.
   Exigir sempre tamanho de efeito com intervalo, não apenas valor-p.

6. EXPLICAÇÕES RIVAIS — causalidade reversa na forma que ela tomaria aqui:
   não faz sentido "cancelamento causar quantidade alta", mas considere se
   clientes que JÁ sabem que vão devolver compram mais unidades para testar
   variações (ex. cores/tamanhos) e devolver o excedente — isso inverteria a
   leitura de H1. O que me faria abandonar cada hipótese?

7. QUANTIFICAÇÃO — quanto do total de linhas/pedidos cancelados cada causa
   validada explica (em contagem de linhas e em receita representada por
   UnitPrice × Quantity), e quanto permanece sem explicação por nenhuma das
   hipóteses testadas.

8. MODELAGEM — só se necessário para separar Quantity, Country e
   recorrência do cliente quando correlacionados entre si. Validação com
   split temporal (treino na janela de exploração, nunca no holdout).
   Tradução dos coeficientes em linguagem de processo (ex. "cada unidade
   adicional no pedido associa-se a X p.p. a mais de chance de
   cancelamento, controlando por país e recorrência"). Diga quando o modelo
   não acrescenta poder de decisão sobre os Paretos e testes de proporção já
   feitos na 2B.

## Tollgate
- H5 (rival) testada e reportada antes de H1/H2, com veredito explícito:
  composição/seleção confirmada, refutada, ou indeterminável com estas
  colunas.
- Todas as conclusões sobre causa reformuladas conforme o veredito do
  pareamento cancelamento↔pedido (item 4).
- Nenhuma conclusão de causa apresentada só com valor-p, sem tamanho de
  efeito.
```

---

## Improve

```
# FASE 4 — IMPROVE · Recomendação que não vou implementar

Entrego a recomendação, o ganho simulado com conta visível, e o desenho do
experimento que a provaria. O rigor está em tratar como proposta séria.

## Tarefas
1. CONTRAMEDIDAS — duas ou três por causa raiz validada no Analyze,
   classificadas em: elimina a causa / reduz a variação / protege contra o
   efeito (poka-yoke) / apenas detecta. Poka-yoke concreto para este
   processo: por exemplo, um passo de confirmação obrigatória (checkbox ou
   e-mail de confirmação) no checkout quando Quantity do carrinho ultrapassa
   um limiar identificado como zona de risco, em vez de treinar o operador ou
   só definir uma meta de taxa de cancelamento — o poka-yoke impede o erro no
   ponto de origem, a meta só cobra o sintoma depois.

2. ENTREGÁVEL CONCRETO DA RECOMENDAÇÃO — uma tabela de segmentos de risco
   (Country × faixa de Quantity × recorrência do cliente) com a taxa de
   cancelamento de cada célula e uma regra de decisão pronta: "aplicar
   verificação prévia nos segmentos com taxa acima de X e n ≥ Y", derivada
   diretamente dos Paretos e testes do Analyze.

3. SIMULAÇÃO DO GANHO sobre os dados da janela de exploração:
   - contrafactual explícito: assume que aplicar verificação prévia nos
     segmentos de risco teria evitado uma fração dos cancelamentos daquele
     segmento — essa fração é premissa, não dado (o dataset não registra o
     que teria acontecido).
   - conta visível passo a passo: linhas cancelamento evitável estimadas ×
     UnitPrice médio do segmento = receita preservada; menos custo estimado
     de fricção adicional (premissa: X% de abandono de checkout entre
     clientes legítimos do segmento).
   - três cenários com premissa de adesão declarada (conservador, central,
     otimista).
   - PONTO DE INDIFERENÇA: como esta base não registra o contrafactual real
     (nenhum pedido "quase cancelado e evitado" está marcado como tal), este é
     o número principal da recomendação: qual taxa de abandono de checkout
     induzida pela fricção anularia o ganho estimado. Se essa taxa for baixa
     (fricção pequena já anula o ganho), a recomendação é frágil e isso
     precisa estar em destaque, não escondido no meio do texto.
   - o que a simulação não captura: efeito reputacional de fricção extra em
     clientes legítimos de alto volume (possíveis revendedores recorrentes,
     que são provavelmente os clientes mais valiosos), efeito de médio prazo
     sobre recompra.

4. DESENHO DO EXPERIMENTO — unidade de aleatorização candidata: CustomerID
   (evita contaminação entre pedidos do mesmo cliente) versus sessão de
   checkout (mais próxima do ponto de decisão, mas sujeita a um mesmo
   cliente cair em braços diferentes em compras diferentes) — discuta as
   duas. Elegibilidade: pedidos nos segmentos de risco identificados.
   Duração: cobrindo pelo menos um mês fora do pico sazonal e, se possível,
   uma fatia do pico, dado que H3 sugere que sazonalidade importa. n
   calculado com o efeito mínimo pré-registrado em H1/H2. Métrica de
   decisão: taxa de cancelamento do braço tratado vs controle. Guardrails:
   taxa de abandono de checkout, volume total de pedidos. Critério de
   parada: guardrail violado antes do n calculado. Ameaças à validade
   plausíveis aqui: sazonalidade não coberta pela janela do teste,
   contaminação se o mesmo CustomerID for exposto a ambos os braços em
   compras diferentes.

5. FMEA DA RECOMENDAÇÃO — severidade × ocorrência × detecção para os modos
   de falha específicos: fricção afasta revendedores de alto volume
   (severidade alta, ocorrência a estimar, detecção via queda de volume por
   segmento); regra de segmento fica desatualizada com mudança de mix de
   produtos/países ao longo do tempo (detecção via monitoramento do plano de
   controle da fase Control).

6. O CONTRA — o parágrafo mais forte que um cético escreveria: "a taxa de
   cancelamento associada a Quantity alta pode ser só efeito de poucos
   clientes grandes com comportamento idiossincrático (H5 confirmada), e
   aplicar fricção para todo o segmento penaliza clientes bons por causa de
   poucos casos". Resposta a ele, ancorada no veredito real de H5 obtido no
   Analyze — não numa resposta genérica.

## Tollgate
- O ponto de indiferença está calculado e é o número em destaque, não o
  ganho bruto.
- A recomendação está condicionada ao veredito de H5 (se H5 confirmou
  composição, a recomendação muda de "restringir quantidade" para
  "segmentar por tipo de cliente").
```

---

## Control

```
# FASE 5 — CONTROL

Duas coisas a controlar: o processo do cliente, entregue como especificação; e o
meu próprio pipeline, entregue como código funcionando.

## Parte A — Plano de controle como especificação
1. Tabela: Métrica | Definição operacional | Fonte | Frequência | Limite |
   Responsável | AÇÃO AO SAIR DO LIMITE — escrita antes de o problema
   acontecer. Inclua a taxa de cancelamento por segmento de risco (métrica
   primária) e os guardrails do Define: volume total de pedidos, receita
   bruta, taxa de abandono de checkout.
2. A carta p mensal de acompanhamento (herdada da 2B) e o gatilho de alerta:
   por exemplo, dois meses seguidos fora dos limites de controle, ou uma
   regra de Nelson disparada, aciona revisão do plano.
3. O que invalidaria esta análise: mudança de plataforma de checkout,
   mudança relevante no mix de países ou categorias de produto vendidos,
   qualquer evento que altere a composição de clientes revendedores vs
   consumidor final — e quando refazer (ex. revisão trimestral ou no
   primeiro sinal de causa especial na carta).

## Parte B — Controle do meu pipeline
4. Converta a auditoria da fase 2A (completude de CustomerID, StockCodes
   não-produto, duplicatas, faixas válidas de Quantity/UnitPrice) em testes
   automáticos que falham se um novo lote de dados mudar de forma, domínio
   ou volume. Gere o código.
5. Checklist de reprodutibilidade aplicado a este projeto; aponte onde ele
   ainda falha. Parâmetros deste projeto que precisam sair do código e ir
   para configuração: lista de StockCodes não-produto excluídos, corte de
   data do holdout, limiares de segmento de risco definidos no Improve.
6. Verificação do ganho contra o baseline congelado na 2B.
7. ABERTURA DO HOLDOUT — agora, e uma única vez. Perguntas a responder: a
   taxa de cancelamento no período de holdout está dentro do intervalo de
   confiança projetado a partir da janela de exploração? Os segmentos de
   risco identificados no Analyze continuam sendo os de maior taxa no
   holdout, ou a composição mudou? Se não se sustentar, isso entra no
   README como achado metodológico legítimo.

## Parte C — Entrega
8. README: que pergunta o projeto responde / a resposta em uma frase / como
   rodar do zero / origem e natureza dos dados (UCI Online Retail, dado
   real de varejista do Reino Unido, sem motivo de cancelamento nem custo
   de devolução registrados — e o que isso proíbe concluir) / decisões
   metodológicas e por quê (granularidade pedido vs linha, regra de
   pareamento cancelamento↔pedido original) / premissas do stakeholder
   simulado / veredito da armadilha de vazamento por ausência de chave de
   ligação / o que eu faria com acesso ao sistema real de checkout e a dados
   de motivo de devolução.
9. O que deste projeto vira reutilizável para o próximo: a lógica de
   pareamento por proximidade quando falta chave estrangeira, o padrão de
   ponto de indiferença para simulação sem contrafactual.
10. Retrospectiva Kaizen pelos oito desperdícios, com horas estimadas, causa
    raiz do maior, e três mudanças no meu processo.

## Tollgate
- Holdout aberto uma única vez, resultado registrado independente do
  veredito.
- README declara com todas as letras o que o dado não permite concluir.
```

---

## Entrega · Página única de apresentação

Rode depois do Control, com os artefatos de todas as fases em mãos.

```
# FASE 6 — ENTREGA · Página única de apresentação

O projeto está fechado. Agora preciso torná-lo consumível por qualquer pessoa,
técnica ou não, numa página única publicável no GitHub Pages: painel, dashboard,
relatório e slides, com linguagem simples e técnica.

## Como construir
Use a skill `entrega-dmaic` e siga-a do início ao fim. Ela traz o molde já
testado, as regras de interação, os downloads em .xlsx e .pptx, e a auditoria
final. Comece do molde; não reconstrua do zero o que ele já resolve.

## O que é específico deste projeto
- Métrica primária: taxa de cancelamento/devolução (fatura InvoiceNo com
  prefixo "C" pareada a um pedido original, na unidade — pedido ou linha —
  decidida no Define).
- Meta: sem benchmark externo citável encontrado para o nicho de giftware
  B2B (ver GEMBA DOCUMENTAL da Fase 0) — meta interna (melhor quartil
  histórico entre países ou entre meses), declarada explicitamente como
  proposta, não referência de mercado.
- Controle: carta p mensal sobre InvoiceDate, agregação mensal (~12-14
  pontos na janela de exploração, abaixo do ideal de 20 — explicar essa
  limitação em vez de escondê-la).
- Guardrails: volume total de pedidos, receita bruta, taxa de abandono de
  checkout. Armadilha de otimização local: reduzir a taxa de cancelamento
  só adicionando fricção no checkout (verificação prévia) a ponto de afastar
  clientes legítimos, sem reduzir insatisfação real — os guardrails existem
  para pegar isso.
- Os dois Paretos: por TAXA — segmento Country × faixa de Quantity ×
  recorrência do cliente; por IMPACTO ABSOLUTO — StockCode/categoria de
  produto (linhas e receita cancelada). Mostrar os dois lado a lado, porque
  apontam lugares diferentes.
- Cubo do Dashboard: dimensões Country, faixa de Quantity (quartil),
  recorrência do cliente (novo vs recorrente), StockCode/categoria de
  produto; temporal = InvoiceDate por mês; par a cruzar na matriz =
  Country × faixa de Quantity (é o cruzamento que sustenta ou derruba H1/H2
  contra H5); dispersão volume × taxa = StockCode, volume de linhas no eixo
  x e taxa de cancelamento no eixo y.
- Hipótese rival a destacar: H5 — o efeito de Quantity alta (H1) e de país
  fora do Reino Unido (H2) sobre cancelamento pode ser artefato de
  composição (concentração em poucos clientes/países) ou de seleção
  (cliente em primeira compra), não causa direta. Testada antes de H1/H2 no
  Analyze — destacar o veredito real obtido, não o enunciado da hipótese.
- Limitações obrigatórias: (1) não existe chave que ligue a fatura de
  cancelamento à fatura original — o pareamento é inferido por CustomerID +
  StockCode + proximidade de data, com taxa de acerto que precisa aparecer
  no Relatório; (2) StockCodes não-produto (POST, D, M, BANK CHARGES, C2,
  DOT, CRUK, etc.) foram excluídos da análise de defeito de produto — listar
  quais; (3) um único ano de InvoiceDate não permite isolar um ciclo
  sazonal completo dentro do holdout; (4) não há motivo declarado de
  cancelamento nem custo de frete reverso — a simulação de ganho na Improve
  usa ponto de indiferença, não ganho bruto, e isso precisa estar visível,
  não só no apêndice; (5) parte das linhas tem CustomerID nulo e fica fora
  de qualquer análise por cliente.
- Ressalva de honestidade: dado real (UCI Online Retail), mas o recorte de
  holdout está congelado e a ligação cancelamento↔pedido original é
  reconstrução minha, não um campo do dado original; o stakeholder
  (Gerente de Operações/Atendimento) é simulado, não confirmado com pessoa
  real.
- Ajustes no Relatório: a seção de "custo por devolução" da estrutura de
  referência não pode ser preenchida com valor real — substituir por ponto
  de indiferença, com a mesma proeminência que um custo real teria.

## Insumo
Os artefatos de todas as fases: baseline congelado, auditoria de qualidade,
estabilidade, estratificação, causas validadas, hipótese rival, variação não
explicada, contramedidas, conta do ganho, experimento, FMEA, plano de controle,
abertura do holdout e limitações.

## Obrigatório
- Todo número da página vem do JSON do pipeline. Nenhum digitado à mão, nenhum
  resto do molde.
- Os números são idênticos nos dois registros de linguagem e nos quatro modos.
- Antes de construir, me mostre o plano visual e os títulos dos slides.
- A auditoria final da skill roda antes de me entregar: os três leitores, até três
  rodadas, parando só sem bloqueante. O relatório de auditoria vem junto.

## Tollgate ENTREGA
- A página partiu do molde da `entrega-dmaic`, e nada do exemplo sobrou?
- Todo número veio do pipeline, e os quatro modos concordam entre si?
- As limitações deste dataset aparecem no Relatório e nos Slides?
- No Dashboard, dá para entrar e sair de qualquer filtro só clicando?
- A planilha e a apresentação baixam e abrem?
- A auditoria final rodou, em quantas rodadas, e terminou sem bloqueante?
- Um estranho abre o link e entende a resposta em menos de trinta segundos?
```
