"""Fase 4 - IMPROVE - segmentos de risco, simulacao de ganho com ponto de indiferenca,
desenho de experimento. Reusa o dataset congelado da Analyze (janela de exploracao,
holdout nunca tocado).
"""
import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportion_confint
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

df = pd.read_parquet("docs/analyze_dataset_exploracao.parquet")
print(f"Dataset carregado: {len(df)} linhas (janela de exploracao, identico ao Analyze/baseline congelado).")

def section(t):
    print("\n" + "=" * 100)
    print(t)
    print("=" * 100)

# ===========================================================================
section("2. TABELA DE SEGMENTOS DE RISCO (Country_group x Quantity_quartil x Recorrencia)")
seg = df.groupby(["country_group", "qty_quartil", "segmento_cliente"], observed=True).agg(
    n=("defect", "size"), d=("defect", "sum"), receita_total=("revenue", "sum")
).reset_index()
seg["rate"] = seg["d"] / seg["n"]
seg["receita_media_linha"] = seg["receita_total"] / seg["n"]
ci = seg.apply(lambda r: proportion_confint(r["d"], r["n"], method="wilson"), axis=1)
seg["ci_low"] = [c[0] for c in ci]
seg["ci_high"] = [c[1] for c in ci]
seg = seg.sort_values("rate", ascending=False)
print(seg.to_string(index=False))

overall_rate = df["defect"].mean()
LIMIAR_TAXA = overall_rate * 1.5   # 1.5x a taxa geral
LIMIAR_N = 500
seg["sinalizado"] = (seg["rate"] >= LIMIAR_TAXA) & (seg["n"] >= LIMIAR_N)
print(f"\nRegra de decisao: sinalizar celula se taxa >= {LIMIAR_TAXA*100:.3f}% (1.5x a taxa geral de {overall_rate*100:.3f}%) E n >= {LIMIAR_N}.")
print("\nCelulas SINALIZADAS para verificacao previa:")
flagged = seg[seg["sinalizado"]].copy()
print(flagged.to_string(index=False))
print(f"\nCelulas com taxa alta mas n insuficiente (nao sinalizadas por falta de confianca estatistica):")
print(seg[(seg["rate"] >= LIMIAR_TAXA) & (seg["n"] < LIMIAR_N)].to_string(index=False))

# ===========================================================================
section("3. SIMULACAO DE GANHO")

df["is_flagged_segment"] = df.set_index(["country_group", "qty_quartil", "segmento_cliente"]).index.isin(
    flagged.set_index(["country_group", "qty_quartil", "segmento_cliente"]).index
)
seg_orders = df[df["is_flagged_segment"]]
n_seg_total = len(seg_orders)
d_seg_total = seg_orders["defect"].sum()
n_seg_legit = n_seg_total - d_seg_total
avg_rev_defect = seg_orders.loc[seg_orders["defect"] == 1, "revenue"].mean()
avg_rev_all = seg_orders["revenue"].mean()

print(f"Pedidos nos segmentos sinalizados: {n_seg_total} (defeitos: {d_seg_total}, legitimos: {n_seg_legit})")
print(f"Receita media por linha CANCELADA nesses segmentos: £{avg_rev_defect:.2f}")
print(f"Receita media por linha (qualquer) nesses segmentos: £{avg_rev_all:.2f}")

cenarios = {
    "conservador": {"f_evitado": 0.20, "a_abandono": 0.02},
    "central":     {"f_evitado": 0.40, "a_abandono": 0.02},
    "otimista":    {"f_evitado": 0.60, "a_abandono": 0.02},
}

print("\nCONTA VISIVEL (por cenario, mesma taxa de abandono assumida de 2% para comparabilidade):")
resultados = {}
for nome, c in cenarios.items():
    f = c["f_evitado"]
    a = c["a_abandono"]
    linhas_evitadas = f * d_seg_total
    receita_preservada = linhas_evitadas * avg_rev_defect
    pedidos_abandonados = a * n_seg_legit
    receita_perdida = pedidos_abandonados * avg_rev_all
    ganho_liquido = receita_preservada - receita_perdida
    resultados[nome] = dict(f=f, a=a, linhas_evitadas=linhas_evitadas, receita_preservada=receita_preservada,
                             pedidos_abandonados=pedidos_abandonados, receita_perdida=receita_perdida, ganho_liquido=ganho_liquido)
    print(f"\n[{nome.upper()}] premissa: verificacao evita {f*100:.0f}% dos cancelamentos do segmento; "
          f"abandono induzido assumido de {a*100:.0f}% dos pedidos legitimos")
    print(f"  Linhas de cancelamento evitadas (estimado): {f} x {d_seg_total} = {linhas_evitadas:.1f}")
    print(f"  Receita preservada: {linhas_evitadas:.1f} x £{avg_rev_defect:.2f} = £{receita_preservada:,.2f}")
    print(f"  Pedidos legitimos abandonados (estimado): {a} x {n_seg_legit} = {pedidos_abandonados:.1f}")
    print(f"  Receita perdida por abandono: {pedidos_abandonados:.1f} x £{avg_rev_all:.2f} = £{receita_perdida:,.2f}")
    print(f"  GANHO LIQUIDO ESTIMADO: £{receita_preservada:,.2f} - £{receita_perdida:,.2f} = £{ganho_liquido:,.2f}")

section("PONTO DE INDIFERENCA (o numero principal desta fase)")
for nome, r in resultados.items():
    a_indiferenca = r["receita_preservada"] / (n_seg_legit * avg_rev_all)
    print(f"[{nome.upper()}] Taxa de abandono de checkout que ANULARIA o ganho: {a_indiferenca*100:.3f}% "
          f"dos pedidos legitimos do segmento (assumindo f_evitado={r['f']*100:.0f}%)")
print(f"""
LEITURA EM DESTAQUE: mesmo no cenario CENTRAL (evita 40% dos cancelamentos do
segmento), basta que a fricção afaste pouco mais de {resultados['central']['receita_preservada']/(n_seg_legit*avg_rev_all)*100:.2f}% dos
pedidos legítimos do segmento para zerar o ganho estimado. Como {n_seg_legit} dos
{n_seg_total} pedidos do segmento sinalizado sao legitimos (nao teriam cancelado
de qualquer forma), a recomendação e FRAGIL por natureza: a base nao registra
nenhum contrafactual real de abandono, entao esse numero e o que decide se a
recomendacao vale a pena, nao o ganho bruto.
""")

print("O QUE A SIMULACAO NAO CAPTURA:")
print("""- Efeito reputacional de friccao extra em clientes legitimos de alto volume
  (revendedores recorrentes, provavelmente os clientes mais valiosos - Fase 0
  ja apontava isso).
- Efeito de medio prazo sobre recompra (cliente irritado com friccao pode nao
  voltar, mesmo sem abandonar o checkout na hora).
- Custo operacional de implementar e manter a verificacao (nao modelado).
""")

# ===========================================================================
section("4. DESENHO DO EXPERIMENTO")
seg_rate = d_seg_total / n_seg_total
analysis = NormalIndPower()
print(f"Taxa de cancelamento do segmento sinalizado (baseline do experimento): {seg_rate*100:.3f}%")
print("NOTA: o efeito minimo absoluto de 3 p.p. pre-registrado em H1 foi calibrado sobre a taxa geral (~1.9%) -")
print("aplicado literalmente aqui (baseline de 3.07%) exigiria derrubar a taxa quase a zero, o que nao e um alvo")
print("realista de experimento. Uso em vez disso a reducao RELATIVA da premissa central da simulacao (40%) como")
print("efeito a detectar - e mais compativel com o que a intervencao realisticamente promete.")
effect_central = seg_rate * cenarios["central"]["f_evitado"]
h = proportion_effectsize(seg_rate - effect_central, seg_rate)
n_per_arm = analysis.solve_power(effect_size=h, alpha=0.05, power=0.8, ratio=1.0)
print(f"Efeito a detectar (reducao relativa de 40% da taxa do segmento): {seg_rate*100:.3f}% -> {(seg_rate-effect_central)*100:.3f}% "
      f"(diferenca absoluta {effect_central*100:.3f} p.p.)")
print(f"n necessario por braco (alfa=0.05, poder=80%): {n_per_arm:.0f}")
print(f"Pedidos elegiveis disponiveis por mes nesse segmento (media da janela de exploracao): {n_seg_total/10:.0f}")
print(f"Tempo estimado para acumular {n_per_arm*2:.0f} pedidos (2 bracos): "
      f"{n_per_arm*2/(n_seg_total/10):.1f} meses de trafego no segmento sinalizado")

print("""
UNIDADE DE ALEATORIZACAO:
- CustomerID: evita que o mesmo cliente caia em bracos diferentes em compras
  diferentes (contaminacao), mas dilui o n disponivel (clientes recorrentes
  contribuem varios pedidos para o MESMO braco, reduzindo a informacao
  estatistica por pedido) e atrasa o experimento se a base de clientes unicos
  do segmento for menor que o n de PEDIDOS calculado acima.
- Sessao de checkout: mais proxima do ponto de decisao real (a friccao e
  aplicada por pedido, nao por cliente), atinge o n calculado mais rapido, mas
  um mesmo cliente pode cair em bracos diferentes em compras diferentes -
  ameaca de contaminacao/efeito de aprendizado (cliente que ja viu a
  verificacao uma vez pode reagir diferente na proxima).
RECOMENDACAO: CustomerID como unidade primaria, por ser o segmento de maior
valor (revendedores recorrentes) o mais sensivel a friccao repetida - o risco
de contaminacao de sessao e mais grave aqui do que o custo de diluir o n.

ELEGIBILIDADE: pedidos nos segmentos sinalizados pela tabela da secao 2.
DURACAO: minimo de 1 mes fora do pico sazonal para atingir o n calculado; se
o n nao for atingido a tempo, estender para cobrir uma fatia do pico
(nov-dez), sabendo que H3 (exploratoria) sugere que sazonalidade pode alterar
o comportamento de cancelamento - resultado do braco no pico deve ser
analisado separado do resultado fora do pico, nao pooled sem checar.
METRICA DE DECISAO: taxa de cancelamento pareavel do braco tratado vs. controle.
GUARDRAILS: taxa de abandono de checkout do braco tratado (medida real, nao
premissa - o experimento e a unica forma de medir isso de verdade), volume
total de pedidos do segmento, receita bruta do segmento.
CRITERIO DE PARADA: guardrail de abandono ou volume violado antes de atingir o
n calculado -> para o experimento e reporta como achado (a fricção e cara demais
para esse segmento), nao insiste ate o n.

AMEACAS A VALIDADE:
- Sazonalidade nao coberta pela janela do teste (mitigada pela duracao acima).
- Contaminacao por CustomerID exposto a ambos os bracos em compras diferentes
  (mitigada pela escolha de unidade de aleatorizacao).
- Regressao a media: segmentos sinalizados pela MAIOR taxa observada no
  Analyze podem regredir naturalmente no periodo do experimento mesmo sem
  intervencao - o braco controle serve exatamente para isolar isso, mas vale
  registrar a ameaça explicitamente.
""")

# ===========================================================================
section("5. FMEA DA RECOMENDACAO")
fmea = pd.DataFrame([
    {"modo_falha": "Friccao afasta revendedores de alto volume (UK, Quantity alta, recorrentes)",
     "severidade": 9, "ocorrencia": 6, "deteccao": 4, "obs": "deteccao via queda de volume por segmento (guardrail do experimento e do Control)"},
    {"modo_falha": "Regra de segmento fica desatualizada com mudanca de mix de produtos/paises",
     "severidade": 6, "ocorrencia": 5, "deteccao": 3, "obs": "deteccao via monitoramento do plano de controle (Fase 5)"},
    {"modo_falha": "Regra de Quantity aplicada FORA do UK por engano (H5 mostrou inversao de sinal em Resto)",
     "severidade": 8, "ocorrencia": 3, "deteccao": 5, "obs": "deteccao via auditoria de configuracao do segmento antes de cada deploy"},
])
fmea["RPN"] = fmea["severidade"] * fmea["ocorrencia"] * fmea["deteccao"]
print(fmea.to_string(index=False))

# ===========================================================================
section("6. O CONTRA")
print("""
O PARAGRAFO MAIS FORTE DE UM CETICO:
"A taxa de cancelamento associada a Quantity alta pode ser so efeito de poucos
clientes grandes com comportamento idiossincratico, e aplicar friccao para todo
o segmento penaliza clientes bons por causa de poucos casos."

RESPOSTA ANCORADA NO VEREDITO REAL DE H5 (nao generica):
O ceptismo esta PARCIALMENTE certo, e o proprio Analyze ja incorporou isso: H5
nao foi refutada de forma limpa - a regressao ajustada mostrou que o efeito de
Quantity sobrevive quase intacto (reducao de so 3% ao controlar por pais e
recorrencia) DENTRO do UK, mas o teste de Breslow-Day encontrou que esse mesmo
efeito SE INVERTE fora do UK. Isso significa que o ceptico tem razao sobre uma
coisa muito especifica: NAO EXISTE uma regra universal "quantidade alta = risco"
que valha para toda a base - e por isso a recomendacao aqui NUNCA propos isso.
A tabela de segmentos (secao 2) so sinaliza celulas onde a taxa observada e
alta E o n sustenta confianca estatistica (>=500) - isso ja filtra boa parte
do "poucos casos idiossincraticos" que o ceptico teme, porque celulas de n
baixo com taxa alta foram explicitamente EXCLUIDAS da lista de segmentos
sinalizados (ver a tabela de celulas descartadas por n insuficiente, secao 2).
O que a resposta NAO resolve: mesmo com n>=500, uma celula ainda pode ser
dominada por poucos CustomerID com muitos pedidos cada (nao verificado aqui) -
esse e um teste adicional que o experimento da secao 4 (aleatorizado por
CustomerID, nao por pedido) resolve na pratica, e que a simulacao da secao 3
nao consegue resolver sozinha com dado historico.
""")
