# Retrospectiva — o que fica para o próximo projeto

Data: 2026-09-20.

## 9. O que deste projeto vira reutilizável

**Pareamento por proximidade quando falta chave estrangeira.** Padrão geral:
quando um evento de "reversão" (cancelamento, estorno, devolução) não carrega
a chave do evento original que reverte, construir o pareamento por
(identificador do agente + identificador do item + data anterior mais
próxima), implementado com um índice `dict` de listas ordenadas de datas por
chave + busca binária (`bisect_left`) — O(n log n), não O(n²). Usado três
vezes neste projeto (Fase 0, Measure 2B, abertura do holdout) com a mesma
lógica; deveria ter sido uma função só (ver item 10, causa raiz do maior
desperdício).

**Ponto de indiferença para simulação sem contrafactual.** Sempre que uma
simulação de ganho depende de uma premissa não observável no dado (aqui:
"fração de cancelamentos que a intervenção evitaria"), a métrica de saída não
deve ser o ganho no cenário mais provável — deve ser o valor do parâmetro
adverso (aqui: taxa de abandono de checkout) que zera o ganho. Isso transforma
uma simulação especulativa em um número testável e não-inflado. Reaplicável a
qualquer recomendação Improve construída sobre dado histórico sem A/B real.

**Teste de rival estrutural via estratificação + Breslow-Day antes de aceitar
um efeito agregado.** A regressão ajustada sozinha (redução de 3% no log-odds)
teria me feito concluir "H5 refutada". Só a estratificação por país com teste
de homogeneidade revelou a inversão de sinal fora do UK. Padrão a repetir:
nunca aceitar "o modelo ajustado não mudou muito o coeficiente" como prova de
ausência de efeito de composição — sempre também estratificar e testar
homogeneidade por dimensão candidata antes de descartar.

## 10. Retrospectiva Kaizen — oito desperdícios (aplicado ao meu próprio processo de análise, não ao processo do varejista)

| Desperdício | Onde apareceu neste projeto | Horas estimadas |
|---|---|---|
| **Defeitos** | Escrevi texto interpretativo (veredito da carta p na 2B, veredito de H5 na Analyze) **dentro do script, antes de rodar o código** — presumindo resultado "sem causa especial" e "sem paradoxo de Simpson". Os dois presumiram errado: a carta mostrou 5/10 meses fora de controle, e Breslow-Day encontrou heterogeneidade real por país. Tive que reescrever a interpretação depois de ver o resultado real. | ~0,4h |
| Superprocessamento / retrabalho | A mesma lógica de pareamento (dict de datas ordenadas + bisect) foi reimplementada do zero três vezes (Fase 0, Measure 2B, abertura do holdout) em vez de extraída para uma função compartilhada — risco de drift entre cópias (verifiquei manualmente que não houve, mas foi verificação extra, não prevenção). | ~0,2h |
| Movimento | Rodei `fase5_abertura_holdout.py` de dentro de `src/` por hábito e o script falhou por não achar o CSV (path relativo à raiz do projeto) — um erro de diretório de execução bobo, mas que interrompeu o fluxo. | ~0,05h |
| Espera | Instalação de `pytest` no meio da Fase 5 porque não estava no ambiente — poderia ter sido verificado/instalado no início do projeto. | ~0,05h |
| Inventário | Nenhum arquivo intermediário abandonado ou não utilizado — os `.parquet`/`.json` de cada fase são todos referenciados pela fase seguinte. | 0h |
| Superprodução | Nenhuma saída gerada além do que cada tollgate pedia. | 0h |
| Espera (do leitor) | Nenhuma — cada fase entregou memorando fechado antes de avançar. | 0h |
| Potencial não utilizado | Não usei nenhuma ferramenta de visualização interativa (ex. dashboard) para os gráficos — ficaram como PNG estático; para um portfólio, um artefato interativo dos Paretos/carta p teria mais impacto de apresentação, mas não foi pedido nesta sessão. | — (oportunidade, não desperdício medido) |

### Causa raiz do maior desperdício (Defeitos)

Escrevi conclusões qualitativas como parte do *código* (dentro de `print()`)
no mesmo momento em que escrevia a lógica de cálculo — antes de rodar e ver o
número real. Isso é exatamente o tipo de garimpo invertido que o contexto
mestre deste projeto pede para eu vigiar no usuário (regra 3, ANTI-GARIMPO) e
eu cometi a versão simétrica: escrever a interpretação antes da evidência, só
que dentro do meu próprio código em vez de numa hipótese pré-registrada. A
diferença que salvou o projeto: eu sempre rodei o script e conferi a saída
bruta antes de publicar o memorando, então o erro nunca chegou ao documento
final — mas o retrabalho aconteceu, e um processo melhor não dependeria de eu
notar a divergência toda vez.

### Três mudanças no meu processo, a partir de agora

1. **Nunca escrever texto de veredito/interpretação dentro de `print()` antes
   de rodar o script.** Prints de código ficam neutros (números, tabelas); a
   interpretação só é redigida no memorando `.md`, depois de ver a saída real.
2. **Extrair a lógica de pareamento repetida para uma função única**
   (ex. `src/pareamento.py::parear_cancelamentos(orders, cancels)`), usada
   pelas três fases que precisam dela, em vez de reimplementar.
3. **Documentar no topo de cada script "rodar a partir da raiz do projeto"**
   (ou tornar os caminhos relativos ao próprio arquivo do script) para
   eliminar o erro de diretório de execução.
