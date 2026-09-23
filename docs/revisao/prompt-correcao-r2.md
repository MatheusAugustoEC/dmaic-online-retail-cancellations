# CORREÇÕES DA BANCA — RODADA 2 — Cancelamentos e Devoluções, Online Retail (UCI)

Uma banca de revisores independentes conferiu, numa segunda rodada, as
correções aplicadas depois do primeiro parecer da página publicada
(https://matheusaugustoec.github.io/dmaic-online-retail-cancellations/,
2026-09-22). Os dois achados críticos e os oito achados importantes da
primeira rodada foram todos corrigidos e verificados — não precisam de nada
aqui. Restam só três pontos pequenos, nenhum deles muda número ou decisão.
Faça um por vez, na ordem.

Se eu tiver apagado algum bloco, é porque decidi não corrigir aquele ponto —
não o reintroduza.

## Regras
- Nenhuma correção abaixo muda um número da análise — são ajustes de texto e
  de posicionamento visual.
- Um número mudou? Não deveria, mas se mudar por engano, atualize-o nos
  quatro modos e nos dois registros de linguagem.
- Ao terminar: rode de nova a auditoria visual (captura de tela) para
  confirmar que os rótulos não se sobrepõem mais, e me diga, em uma linha
  por ID, o que mudou.

---

## [M1] Rótulo "limite do normal" ainda sobre a linha do limite
Crítica: o rótulo "limite do normal" da carta de controle (Painel e
Relatório) foi reposicionado na correção anterior, mas o traço pontilhado do
limite superior ainda passa por trás das letras — mais visível no tema
escuro, onde o contraste deixa o cruzamento óbvio.
Onde: Painel e Relatório, carta de controle (gráfico "chart-p" / "rep-carta"),
nos dois registros de linguagem, confirmado em desktop, celular e escuro.
O que fazer:
  1. Em vez de reancorar o rótulo ao longo da própria linha do limite (que
     sempre tem alguma chance de coincidir com um pico da curva), mover o
     rótulo para fora da área do gráfico (por exemplo, para a margem
     direita, alinhado com a legenda) ou para um espaço em branco fixo que
     não dependa do formato da curva.
  2. Testar em claro, escuro e celular, nos dois registros de linguagem.
Pronto quando: uma nova checagem de sobreposição não mostra nenhuma
ocorrência de "texto sobre linha" para o rótulo "limite do normal"/"UCL
(Laney)", em nenhum modo, tema ou dispositivo testado.
Muda junto: nada além da posição do próprio rótulo.
Fase de origem: Entrega · pós-hoc · cosmético

---

## [M2] "poka-yoke" ainda aparece duas vezes no Relatório em modo Simples
Crítica: a correção anterior tirou "poka-yoke" da tabela do plano de
controle no Painel, mas o Relatório (modo Simples), na seção "Onde o
dinheiro se perde", ainda usa o termo duas vezes: "Se a ação é uma
conferência extra na separação (poka-yoke), o custo é por produto tratado"
e "Uso o de impacto para priorizar a lista de produtos do poka-yoke".
Onde: Relatório, seção "Onde o dinheiro se perde" (modo Simples).
O que fazer:
  1. Trocar as duas ocorrências de "poka-yoke" por "conferência dupla" no
     texto do modo Simples dessa seção.
  2. Confirmar que o modo Técnico da mesma seção mantém "poka-yoke" (ali o
     termo é apropriado).
Pronto quando: uma busca por "poka-yoke" no texto capturado do Relatório em
modo Simples não encontra nenhuma ocorrência.
Muda junto: nada além do texto dessas duas frases.
Fase de origem: Entrega · pós-hoc · cosmético

---

## [M4] Rótulos do eixo Y tocam bolhas próximas no gráfico de dispersão (achado novo)
Crítica: ao corrigir a sobreposição dos nomes de produto no gráfico "Volume
contra frequência, por produto" (Dashboard), as bolhas foram reposicionadas
para não colidirem entre si — e algumas ficaram próximas o bastante do eixo
Y para tocar os rótulos de porcentagem do eixo (2,4%, 4,9%, 7,3%). É bem
mais leve que o problema original (não impede identificar nenhum produto),
mas ainda é uma sobreposição real.
Onde: Dashboard, "Volume contra frequência, por produto", desktop e tema
escuro.
O que fazer:
  1. Afastar levemente os rótulos de porcentagem do eixo Y das bolhas mais
     próximas da borda esquerda do gráfico (por exemplo, deslocando o
     rótulo do eixo para fora da área de plotagem, ou reduzindo o raio de
     colisão considerado).
  2. Testar em desktop, celular e escuro.
Pronto quando: uma nova checagem de sobreposição não mostra ocorrências de
"texto sobre marca" entre os rótulos do eixo Y e as bolhas do gráfico.
Muda junto: nada além da posição dos rótulos do eixo.
Fase de origem: Entrega · pós-hoc · cosmético
