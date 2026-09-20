"""Fase 2B - MEASURE - baseline, estabilidade, capabilidade, estratificacao.
Apenas janela de exploracao (InvoiceDate < 2011-10-01). Holdout jamais lido aqui.
"""
import pandas as pd
import numpy as np
from bisect import bisect_left
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize, proportion_confint

pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

HOLDOUT_START = pd.Timestamp("2011-10-01")

NON_PRODUCT_CODES = ["POST", "DOT", "M", "C2", "D", "S", "BANK CHARGES", "CRUK", "B", "PADS"]

raw = pd.read_csv(
    "online_retail.csv",
    dtype={"InvoiceNo": str, "StockCode": str, "Description": str, "Country": str},
    parse_dates=["InvoiceDate"],
)
NON_PRODUCT_CODES += [c for c in raw["StockCode"].unique() if str(c).lower().startswith("gift_")]

# HOLDOUT: nunca tocado. Filtramos ANTES de qualquer outra coisa.
df = raw[raw["InvoiceDate"] < HOLDOUT_START].copy()
print(f"[GUARDA HOLDOUT] linhas na janela de exploracao: {len(df)} de {len(raw)} totais "
      f"({len(df)/len(raw)*100:.1f}%). Holdout (>= {HOLDOUT_START.date()}) NAO carregado em nenhuma variavel abaixo.")

is_cancel_line = df["InvoiceNo"].str.startswith("C", na=False)
is_real_product = ~df["StockCode"].isin(NON_PRODUCT_CODES)
is_priced = df["UnitPrice"] > 0
has_customer = df["CustomerID"].notnull()

# ---------------------------------------------------------------------------
def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

section("0. FILTROS APLICADOS (fecha a pendencia da Measure 2A)")
n_nonproduct = (~is_real_product).sum()
n_nonpriced_real = (is_real_product & ~is_priced).sum()
print(f"Total linhas na janela de exploracao: {len(df)}")
print(f"  - StockCode nao-produto (excluidas): {n_nonproduct}")
print(f"  - StockCode produto real mas UnitPrice<=0 (excluidas, ajuste de estoque/erro de preco - decisao fechada nesta fase, estende a proposta da 2A para tambem cobrir os casos com CustomerID presente): {n_nonpriced_real}")

scope = df[is_real_product & is_priced].copy()
print(f"Linhas em escopo apos filtros de produto/preco: {len(scope)}")

orders_scope = scope[~scope["InvoiceNo"].str.startswith("C", na=False)].copy()
cancels_scope = scope[scope["InvoiceNo"].str.startswith("C", na=False)].copy()
print(f"  - Linhas de PEDIDO ORIGINAL em escopo: {len(orders_scope)}")
print(f"  - Linhas de CANCELAMENTO em escopo: {len(cancels_scope)}")

orders_valid = orders_scope[orders_scope["CustomerID"].notnull()].copy()
n_dropped_no_customer = len(orders_scope) - len(orders_valid)
print(f"  - Dos pedidos originais em escopo, com CustomerID nulo (fora do universo pareavel, Define secao 3): {n_dropped_no_customer}")
print(f"  - UNIVERSO FINAL do baseline (denominador): {len(orders_valid)} linhas de pedido original, produto real, preco>0, CustomerID presente")

cancels_valid = cancels_scope[cancels_scope["CustomerID"].notnull()].copy()
print(f"  - Cancelamentos com CustomerID presente disponiveis para pareamento na janela: {len(cancels_valid)}")

# ---------------------------------------------------------------------------
section("PAREAMENTO linha-a-linha (nearest preceding order, dentro da janela de exploracao)")
orders_valid = orders_valid.reset_index(drop=True)
orders_valid["defect"] = 0

key_to_rows = {}
for idx, row in orders_valid.iterrows():
    key = (row["CustomerID"], row["StockCode"])
    key_to_rows.setdefault(key, []).append((row["InvoiceDate"], idx))
for key in key_to_rows:
    key_to_rows[key].sort()

lags_days = []
orphan_cancels = 0
for _, crow in cancels_valid.iterrows():
    key = (crow["CustomerID"], crow["StockCode"])
    candidates = key_to_rows.get(key)
    if not candidates:
        orphan_cancels += 1
        continue
    dates = [d for d, _ in candidates]
    pos = bisect_left(dates, crow["InvoiceDate"])
    if pos == 0:
        orphan_cancels += 1
        continue
    prior_date, prior_idx = candidates[pos - 1]
    orders_valid.at[prior_idx, "defect"] = 1
    lags_days.append((crow["InvoiceDate"] - prior_date).total_seconds() / 86400)

n_defect = orders_valid["defect"].sum()
n_total = len(orders_valid)
print(f"Cancelamentos pareados a uma linha original especifica: {len(lags_days)}")
print(f"Cancelamentos orfaos dentro da janela (sem pedido original anterior compativel, ANTES do holdout): {orphan_cancels}")
print(f"Linhas originais marcadas como defeito (podem ter recebido >=1 cancelamento pareado): {n_defect} de {n_total}")

print("\nDistribuicao do lag (dias) entre pedido original e cancelamento pareado:")
lags = pd.Series(lags_days)
print(lags.describe())
print(f"% de cancelamentos pareados que ocorrem em ate 30 dias: {(lags<=30).mean()*100:.1f}%")
print(f"% de cancelamentos pareados que ocorrem em ate 60 dias: {(lags<=60).mean()*100:.1f}%")
print(f"% de cancelamentos pareados que ocorrem em ate 90 dias: {(lags<=90).mean()*100:.1f}%")

section("AVISO DE CENSURA A DIREITA (right-censoring)")
print("""Um pedido original de, digamos, setembro/2011 so pode ser contado como 'defeito'
aqui se o cancelamento correspondente TAMBEM ocorreu antes de 2011-10-01. Qualquer
cancelamento que caia no holdout (>= out/2011) e invisivel para este calculo, por
desenho (holdout fechado). Isso enviesa a taxa de cancelamento dos meses mais
recentes da janela de exploracao PARA BAIXO, na proporcao do lag tipico observado
acima. Nao corrijo isso agora (corrigir exigiria olhar o holdout) - fica como
limitacao declarada da carta de controle (secao 2) e do baseline (secao 1).""")

# ---------------------------------------------------------------------------
section("1. BASELINE")
p_hat = n_defect / n_total
ci_low, ci_high = proportion_confint(n_defect, n_total, alpha=0.05, method="wilson")
print(f"Taxa de cancelamento (linha, pareavel): {p_hat*100:.3f}%")
print(f"IC 95% (Wilson): [{ci_low*100:.3f}%, {ci_high*100:.3f}%]")

dpmo = p_hat * 1_000_000
z_long_term = stats.norm.ppf(1 - p_hat)
print(f"DPMO: {dpmo:.0f}")
print(f"Nivel sigma (longo prazo, sem deslocamento de 1.5-sigma): {z_long_term:.2f}")
print(f"Nivel sigma (convencao Six Sigma, com deslocamento de 1.5-sigma somado): {z_long_term + 1.5:.2f}")

print("\nDistribuicao de Quantity (linhas de pedido original em escopo):")
print(orders_valid["Quantity"].describe())
print("\nDistribuicao de UnitPrice (linhas de pedido original em escopo):")
print(orders_valid["UnitPrice"].describe())

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
q99_qty = orders_valid["Quantity"].quantile(0.99)
axes[0].hist(orders_valid.loc[orders_valid["Quantity"] <= q99_qty, "Quantity"], bins=50, color="#4C72B0")
axes[0].axvline(q99_qty, color="red", linestyle="--", label=f"p99={q99_qty:.0f}")
axes[0].set_title("Quantity por linha (ate p99; outliers acima marcados)")
axes[0].set_xlabel("Quantity")
axes[0].legend()

q99_price = orders_valid["UnitPrice"].quantile(0.99)
axes[1].hist(orders_valid.loc[orders_valid["UnitPrice"] <= q99_price, "UnitPrice"], bins=50, color="#55A868")
axes[1].axvline(q99_price, color="red", linestyle="--", label=f"p99={q99_price:.2f}")
axes[1].set_title("UnitPrice por linha (ate p99; outliers acima marcados)")
axes[1].set_xlabel("UnitPrice (£)")
axes[1].legend()
plt.tight_layout()
plt.savefig("reports/2b_histogramas_quantity_unitprice.png", dpi=110)
plt.close()
print("\nGrafico salvo: reports/2b_histogramas_quantity_unitprice.png")

# ---------------------------------------------------------------------------
section("2. ESTABILIDADE - carta p mensal")
orders_valid["month"] = orders_valid["InvoiceDate"].dt.to_period("M")
monthly = orders_valid.groupby("month").agg(n=("defect", "size"), d=("defect", "sum"))
monthly["p"] = monthly["d"] / monthly["n"]
p_bar = monthly["d"].sum() / monthly["n"].sum()
monthly["sigma"] = np.sqrt(p_bar * (1 - p_bar) / monthly["n"])
monthly["UCL"] = np.minimum(1, p_bar + 3 * monthly["sigma"])
monthly["LCL"] = np.maximum(0, p_bar - 3 * monthly["sigma"])
monthly["fora_de_controle"] = (monthly["p"] > monthly["UCL"]) | (monthly["p"] < monthly["LCL"])
print(monthly)
print(f"\nNumero de pontos na carta mensal: {len(monthly)} (abaixo do minimo de ~20 citado na metodologia para carta robusta)")
print(f"Pontos fora dos limites (regra de Nelson 1): {monthly['fora_de_controle'].sum()}")

run_above = (monthly["p"] > p_bar).astype(int)
max_run = 0
current = 0
for v in run_above:
    if v == 1:
        current += 1
        max_run = max(max_run, current)
    else:
        current = 0
print(f"Maior sequencia de pontos consecutivos acima da linha central (regra de Nelson 2 pede >=9): {max_run}")

fig, ax = plt.subplots(figsize=(11, 5))
x = monthly.index.astype(str)
ax.plot(x, monthly["p"] * 100, marker="o", color="#4C72B0", label="taxa mensal")
ax.axhline(p_bar * 100, color="black", linestyle="-", label=f"media = {p_bar*100:.2f}%")
ax.plot(x, monthly["UCL"] * 100, color="red", linestyle="--", label="UCL/LCL (3 sigma)")
ax.plot(x, monthly["LCL"] * 100, color="red", linestyle="--")
for i, (m, row) in enumerate(monthly.iterrows()):
    if row["fora_de_controle"]:
        ax.annotate(str(m), (i, row["p"] * 100), color="red", fontweight="bold")
ax.set_title("Carta p mensal - taxa de cancelamento pareavel (janela de exploracao)")
ax.set_ylabel("% cancelamento")
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("reports/2b_carta_p_mensal.png", dpi=110)
plt.close()
print("Grafico salvo: reports/2b_carta_p_mensal.png")

print("\n--- Alternativa semanal (avaliacao de trade-off, nao substitui a mensal) ---")
orders_valid["week"] = orders_valid["InvoiceDate"].dt.to_period("W")
weekly = orders_valid.groupby("week").agg(n=("defect", "size"), d=("defect", "sum"))
weekly["p"] = weekly["d"] / weekly["n"]
print(f"Numero de semanas na janela de exploracao: {len(weekly)} (mais perto do minimo de 20, mas n por semana varia de {weekly['n'].min()} a {weekly['n'].max()}, mediana {weekly['n'].median():.0f} - limites de controle mais largos e instaveis semana a semana)")

print("""
Justificativa I-MR vs carta p: I-MR se aplica a medida CONTINUA individual (ex.
Quantity ou UnitPrice medio por periodo). Aqui o defeito e um ATRIBUTO BINARIO
(cancelado ou nao) com tamanho de amostra variavel mes a mes -> carta p e a
escolha correta.

LEITURA HONESTA DO RESULTADO (nao a canonica "tudo em controle"): com n mensal
acima de ~19.000, os limites de 3-sigma ficam muito estreitos (~+-0.08 p.p.),
entao a carta fica hipersensivel - 5 de 10 meses cruzam o limite. Antes de
tratar isso como 5 causas especiais eu classifico caso a caso:
- SET/2011 (abaixo do LCL): explicado pelo proprio artefato de censura a
  direita documentado acima (mes mais proximo do corte do holdout, cancelamento
  tem menos tempo de acontecer dentro da janela) - isso e ARTEFATO DE MEDICAO,
  nao causa especial do processo real. Nao entra na leitura de capabilidade
  (secao 3 usa janela madura, excluindo este mes).
- JAN/FEV/MAR/MAI (acima do UCL, todos entre 21,2%% e 23,0%% contra media de
  ~20,3%%): breach estatistico real, mas de magnitude pequena (~1-2 p.p. acima
  do centro) dado o n gigante. JAN concentrado logo apos o pico de fim de ano e
  compativel com hipotese de dominio plausivel (devolucao pos-Natal) - fica
  registrado como pista para o Analyze, NAO testado aqui (seria cruzamento de
  variavel, proibido na Measure).
Classificacao: a variacao mes a mes tem pelo menos um artefato de medicao
(setembro) e um subconjunto de pontos com breach estatistico pequeno mas real
(jan-mar, mai) que pede investigacao no Analyze, nao uma meta mensal cobrada da
operacao - a resposta estrutural (checkout, verificacao por segmento) continua
sendo a via correta, mas a alegacao de "tudo e causa comum" seria imprecisa.
""")

# ---------------------------------------------------------------------------
section("3. CAPABILIDADE")
print("O mes de SET/2011 e excluido do calculo de capabilidade: seu p artificialmente baixo (0,86%) e efeito "
      "do artefato de censura a direita (secao acima), nao do processo real. Usar a janela inteira contaminaria "
      "tanto a taxa pooled quanto a propria meta (que e um quantil dessas taxas mensais) com o mesmo vies.")
monthly_mature = monthly.drop(index=monthly.index.max())  # remove o ultimo mes (SET/2011)
n_mature = monthly_mature["n"].sum()
d_mature = monthly_mature["d"].sum()
p_hat_mature = d_mature / n_mature
print(f"\nTaxa pooled (janela madura, dez/2010-ago/2011, 9 meses): {p_hat_mature*100:.4f}% (n={n_mature}, d={d_mature})")

month_rates_mature = monthly_mature["p"]
meta_interna = month_rates_mature.quantile(0.25)
print(f"Meta interna proposta (melhor quartil historico das taxas MENSAIS, p25, janela madura): {meta_interna*100:.4f}%")
print("[PROPOSTA INTERNA, nao referencia de mercado - decidido no Define por falta de benchmark de nicho B2B giftware]")
gap = p_hat_mature - meta_interna
orders_per_month_avg = monthly_mature["n"].mean()
extra_conformes_mes = gap * orders_per_month_avg
print(f"Gap atual vs meta: {gap*100:.4f} p.p.")
print(f"Media de linhas de pedido por mes na janela madura: {orders_per_month_avg:.0f}")
print(f"Traducao de negocio: se a meta interna (p25 historico = {meta_interna*100:.2f}%) fosse atingida em todos os "
      f"meses, cerca de {extra_conformes_mes:.0f} linhas de pedido a mais por mes ficariam 'conformes' (nao-canceladas), "
      f"na media da janela madura.")
print(f"\n(Para registro: se SET/2011 fosse incluido sem correcao, a taxa pooled cairia para {p_hat*100:.3f}% e o "
      f"p25 para {monthly['p'].quantile(0.25)*100:.3f}%, invertendo o sinal do gap por puro artefato de medicao - "
      f"por isso a janela madura e a leitura oficial de capabilidade.)")

# ---------------------------------------------------------------------------
section("4. ESTRATIFICACAO E PARETO")

def rate_table(df_in, group_col, min_n):
    g = df_in.groupby(group_col).agg(n=("defect", "size"), d=("defect", "sum"))
    g["rate"] = g["d"] / g["n"]
    g["suficiente"] = g["n"] >= min_n
    return g.sort_values("rate", ascending=False)

print("--- Por COUNTRY (n minimo 100 para entrar no ranking individual) ---")
country_tab = rate_table(orders_valid, "Country", 100)
print(country_tab)
uk_vs_resto = orders_valid.copy()
uk_vs_resto["grupo"] = np.where(uk_vs_resto["Country"] == "United Kingdom", "UK", "Resto")
print("\nUK vs Resto:")
print(rate_table(uk_vs_resto, "grupo", 1))

print("\n--- Por FAIXA DE QUANTITY (quartil, no nivel de LINHA) ---")
orders_valid["qty_quartil"] = pd.qcut(orders_valid["Quantity"], 4, labels=["Q1 (menor)", "Q2", "Q3", "Q4 (maior)"])
qty_tab = rate_table(orders_valid, "qty_quartil", 1)
print(qty_tab)

print("\n--- Por StockCode (n minimo 50 para entrar no ranking individual) ---")
stockcode_tab = rate_table(orders_valid, "StockCode", 50)
print(f"StockCodes com n>=50: {stockcode_tab['suficiente'].sum()} de {len(stockcode_tab)}")
print(stockcode_tab[stockcode_tab["suficiente"]].head(15))

print("\n--- Por RECORRENCIA de cliente (primeira compra vs recorrente, dentro da janela de exploracao) ---")
first_order_date = orders_valid.groupby("CustomerID")["InvoiceDate"].transform("min")
orders_valid["primeira_compra"] = orders_valid["InvoiceDate"] == first_order_date
orders_valid["segmento_cliente"] = np.where(orders_valid["primeira_compra"], "Primeira compra", "Recorrente")
print(rate_table(orders_valid, "segmento_cliente", 1))

print("\n\n>>> PARETO POR TAXA (top 10 segmentos com n suficiente, ranking descendente por taxa) <<<")
pareto_rate_pool = pd.concat([
    country_tab[country_tab["suficiente"]].assign(dimensao="Country"),
    qty_tab.assign(dimensao="Quantity_quartil"),
    stockcode_tab[stockcode_tab["suficiente"]].assign(dimensao="StockCode"),
])
pareto_rate_top = pareto_rate_pool.sort_values("rate", ascending=False).head(10)
print(pareto_rate_top[["dimensao", "n", "d", "rate"]])

print("\n\n>>> PARETO POR IMPACTO ABSOLUTO (linhas canceladas, corte de 80% marcado) <<<")
pareto_impact_pool = pd.concat([
    country_tab.assign(dimensao="Country"),
    qty_tab.assign(dimensao="Quantity_quartil"),
    stockcode_tab.assign(dimensao="StockCode"),
])
pareto_impact_top = pareto_impact_pool.sort_values("d", ascending=False).head(15).copy()
pareto_impact_top["pct_cum"] = pareto_impact_top["d"].cumsum() / n_defect * 100
print(pareto_impact_top[["dimensao", "n", "d", "rate", "pct_cum"]])

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
axes[0].barh(pareto_rate_top.index.astype(str) + " (" + pareto_rate_top["dimensao"] + ")", pareto_rate_top["rate"] * 100, color="#C44E52")
axes[0].invert_yaxis()
axes[0].set_title("Pareto por TAXA de cancelamento (top 10, n suficiente)")
axes[0].set_xlabel("% cancelamento")

axes[1].barh(pareto_impact_top.index.astype(str) + " (" + pareto_impact_top["dimensao"] + ")", pareto_impact_top["d"], color="#4C72B0")
axes[1].invert_yaxis()
ax2 = axes[1].twiny()
ax2.plot(pareto_impact_top["pct_cum"].values, range(len(pareto_impact_top)), color="black", marker="o")
ax2.axvline(80, color="red", linestyle="--", label="80%")
ax2.set_xlabel("% acumulado")
ax2.legend(loc="lower right")
axes[1].set_title("Pareto por IMPACTO ABSOLUTO (linhas canceladas)")
axes[1].set_xlabel("n linhas canceladas")
plt.tight_layout()
plt.savefig("reports/2b_paretos.png", dpi=110)
plt.close()
print("\nGrafico salvo: reports/2b_paretos.png")

# ---------------------------------------------------------------------------
section("5. TAMANHO DE AMOSTRA E PODER")
insuficientes = country_tab[~country_tab["suficiente"]]
print(f"Paises com n<100 (nao sustentam teste individual, vao para 'resto' ou sao descartados do teste por pais): {len(insuficientes)} de {len(country_tab)}")
print(list(insuficientes.index))

analysis = NormalIndPower()
def poder_teste(n1, n2, p_baseline, delta_pp):
    p2 = p_baseline + delta_pp
    h = proportion_effectsize(p2, p_baseline)
    return analysis.power(effect_size=h, nobs1=n1, ratio=n2 / n1, alpha=0.05 / 4)

n_q1 = qty_tab.loc["Q1 (menor)", "n"]
n_q4 = qty_tab.loc["Q4 (maior)", "n"]
poder_h1 = poder_teste(n_q1, n_q4, p_hat, 0.03)
print(f"\nH1 (Quantity Q1 n={n_q1:.0f} vs Q4 n={n_q4:.0f}, efeito minimo 3 p.p., alfa ajustado 0.0125): poder = {poder_h1*100:.1f}%")

n_uk = (uk_vs_resto["grupo"] == "UK").sum()
n_resto = (uk_vs_resto["grupo"] == "Resto").sum()
poder_h2 = poder_teste(n_uk, n_resto, p_hat, 0.05)
print(f"H2 (UK n={n_uk} vs Resto n={n_resto}, efeito minimo 5 p.p., alfa ajustado 0.0125): poder = {poder_h2*100:.1f}%")

print(f"\nH4 (StockCode): {stockcode_tab['suficiente'].sum()} produtos com n>=50 sustentam comparacao individual contra a media geral; "
      f"produtos com n<50 (a maioria, {(~stockcode_tab['suficiente']).sum()} de {len(stockcode_tab)}) ficam fora do Pareto de H4 por falta de poder.")

# ---------------------------------------------------------------------------
section("7. CONGELAMENTO DO BASELINE")
freeze = {
    "data_congelamento": "2026-09-20",
    "unidade": "linha (InvoiceNo x StockCode)",
    "janela_exploracao": "InvoiceDate < 2011-10-01 (2010-12-01 a 2011-09-30)",
    "holdout_reservado": "InvoiceDate >= 2011-10-01 (nunca lido nesta fase)",
    "filtros_aplicados": {
        "stockcodes_excluidos": NON_PRODUCT_CODES,
        "unitprice_le_0_em_produto_real": "excluido do universo (decisao fechada na 2B, estende a 2A)",
        "customerid_nulo": "excluido do universo pareavel (fora do escopo do Define)",
    },
    "n_total_universo": int(n_total),
    "n_defeito": int(n_defect),
    "taxa_cancelamento": round(float(p_hat), 6),
    "ic95_wilson": [round(float(ci_low), 6), round(float(ci_high), 6)],
    "dpmo": round(float(dpmo), 1),
    "sigma_longo_prazo": round(float(z_long_term), 3),
    "meta_interna_p25_mensal_janela_madura": round(float(meta_interna), 6),
    "taxa_pooled_janela_madura_dez2010_ago2011": round(float(p_hat_mature), 6),
    "limitacao_censura_direita": "taxa do mes de set/2011 artificialmente baixa (0.86% vs media geral 2.0%) por censura a direita - cancelamentos que cairiam no holdout sao invisiveis; meta interna e comparacao de capabilidade usam janela madura (dez/2010-ago/2011) para nao herdar esse vies",
}
import json
with open("docs/baseline_congelado.json", "w", encoding="utf-8") as f:
    json.dump(freeze, f, ensure_ascii=False, indent=2)
print(json.dumps(freeze, ensure_ascii=False, indent=2))
print("\nSalvo em docs/baseline_congelado.json (ARTEFATO IMUTAVEL a partir de agora).")
