"""Fase 5 - CONTROL - ABERTURA DO HOLDOUT. RODAR UMA UNICA VEZ.
Este script le InvoiceDate >= 2011-10-01 pela primeira vez em todo o projeto.
O resultado vai para docs/holdout_resultado.json, que a partir da execucao
deste script vira ARTEFATO IMUTAVEL junto com o pre-registro e o baseline.
"""
import json
import numpy as np
import pandas as pd
from bisect import bisect_left
from statsmodels.stats.proportion import proportion_confint
from config import get_non_product_codes, HOLDOUT_START, RISK_SEGMENT_RATE_MULTIPLIER, RISK_SEGMENT_MIN_N

pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

def section(t):
    print("\n" + "=" * 100)
    print(t)
    print("=" * 100)

print("!" * 100)
print("ABERTURA DO HOLDOUT - primeira e unica leitura de InvoiceDate >= 2011-10-01 neste projeto.")
print("!" * 100)

raw = pd.read_csv(
    "online_retail.csv",
    dtype={"InvoiceNo": str, "StockCode": str, "Description": str, "Country": str},
    parse_dates=["InvoiceDate"],
)
NON_PRODUCT_CODES = get_non_product_codes(raw["StockCode"])

is_real_product = ~raw["StockCode"].isin(NON_PRODUCT_CODES)
is_priced = raw["UnitPrice"] > 0
scope = raw[is_real_product & is_priced].copy()
orders_scope = scope[~scope["InvoiceNo"].str.startswith("C", na=False)].copy()
cancels_scope = scope[scope["InvoiceNo"].str.startswith("C", na=False)].copy()
orders_valid = orders_scope[orders_scope["CustomerID"].notnull()].reset_index(drop=True).copy()
cancels_valid = cancels_scope[cancels_scope["CustomerID"].notnull()].copy()

# pareamento identico ao usado na 2B/Analyze, agora sobre o dataset INTEIRO
# (uma cancelamento de out/2011 pode ter como par mais proximo um pedido de set/2011 -
# isso e correto: o pedido original nao muda de mes so porque agora podemos ver o cancelamento)
orders_valid["defect"] = 0
key_to_rows = {}
for idx, row in orders_valid.iterrows():
    key = (row["CustomerID"], row["StockCode"])
    key_to_rows.setdefault(key, []).append((row["InvoiceDate"], idx))
for key in key_to_rows:
    key_to_rows[key].sort()

for _, crow in cancels_valid.iterrows():
    key = (crow["CustomerID"], crow["StockCode"])
    candidates = key_to_rows.get(key)
    if not candidates:
        continue
    dates = [d for d, _ in candidates]
    pos = bisect_left(dates, crow["InvoiceDate"])
    if pos == 0:
        continue
    _, prior_idx = candidates[pos - 1]
    orders_valid.at[prior_idx, "defect"] = 1

orders_valid["in_holdout"] = orders_valid["InvoiceDate"] >= HOLDOUT_START
holdout = orders_valid[orders_valid["in_holdout"]].copy()
exploracao = orders_valid[~orders_valid["in_holdout"]].copy()

section("1. TAXA DE CANCELAMENTO NO HOLDOUT vs. PROJECAO DA EXPLORACAO")
n_h, d_h = len(holdout), int(holdout["defect"].sum())
p_h = d_h / n_h
ci_h = proportion_confint(d_h, n_h, method="wilson")
print(f"Holdout (out-dez/2011): n={n_h}, defeitos={d_h}, taxa={p_h*100:.3f}%, IC95% Wilson [{ci_h[0]*100:.3f}%, {ci_h[1]*100:.3f}%]")

# projecao a partir da janela de exploracao MADURA (dez/2010-ago/2011), igual usado na capabilidade da 2B
exploracao["month"] = exploracao["InvoiceDate"].dt.to_period("M")
monthly_exp = exploracao.groupby("month").agg(n=("defect", "size"), d=("defect", "sum"))
monthly_exp["p"] = monthly_exp["d"] / monthly_exp["n"]
monthly_mature = monthly_exp.drop(index=monthly_exp.index.max())  # exclui set/2011, contaminado por censura
mean_rate = monthly_mature["p"].mean()
std_rate = monthly_mature["p"].std(ddof=1)
n_meses = len(monthly_mature)
se_mean = std_rate / np.sqrt(n_meses)
proj_lo = mean_rate - 1.96 * se_mean
proj_hi = mean_rate + 1.96 * se_mean
print(f"\nProjecao a partir da media dos {n_meses} meses maduros da exploracao: media={mean_rate*100:.3f}%, "
      f"desvio entre meses={std_rate*100:.3f} p.p.")
print(f"Intervalo projetado (media +/- 1.96*erro-padrao-da-media): [{proj_lo*100:.3f}%, {proj_hi*100:.3f}%]")
print(f"\nTaxa observada no holdout: {p_h*100:.3f}%")
dentro_projecao = proj_lo <= p_h <= proj_hi
print(f"VEREDITO: taxa do holdout {'ESTA' if dentro_projecao else 'NAO ESTA'} dentro do intervalo projetado.")

print("\nNota honesta: o holdout tambem sofre censura a direita no proprio limite dos dados (max=2011-12-09) -")
print("pedidos de outubro tem ~2 meses para cancelar dentro dos dados, pedidos de dezembro tem poucos dias.")
holdout["month"] = holdout["InvoiceDate"].dt.to_period("M")
print(holdout.groupby("month").agg(n=("defect", "size"), d=("defect", "sum")).assign(p=lambda x: x["d"]/x["n"]))

section("2. OS SEGMENTOS DE RISCO DO IMPROVE CONTINUAM SENDO OS DE MAIOR TAXA?")
for d_ in (holdout, exploracao):
    d_["qty_quartil"] = pd.qcut(d_["Quantity"], 4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop")
    d_["country_group"] = np.where(d_["Country"] == "United Kingdom", "UK", "Resto")
    first_date = d_.groupby("CustomerID")["InvoiceDate"].transform("min")
    d_["segmento_cliente"] = np.where(d_["InvoiceDate"] == first_date, "Primeira_compra", "Recorrente")

def seg_table(data):
    g = data.groupby(["country_group", "qty_quartil", "segmento_cliente"], observed=True).agg(
        n=("defect", "size"), d=("defect", "sum")
    ).reset_index()
    g["rate"] = g["d"] / g["n"]
    return g.sort_values("rate", ascending=False)

seg_holdout = seg_table(holdout)
seg_exploracao = seg_table(exploracao)
overall_rate_holdout = holdout["defect"].mean()
limiar_holdout = overall_rate_holdout * RISK_SEGMENT_RATE_MULTIPLIER
seg_holdout["sinalizado_holdout"] = (seg_holdout["rate"] >= limiar_holdout) & (seg_holdout["n"] >= RISK_SEGMENT_MIN_N)

print("Segmentos sinalizados no IMPROVE (Analyze/exploracao):")
print("  UK / Q4 / Recorrente")
print("  Resto / Q2 / Recorrente")
print("  Resto / Q1 / Recorrente")

print(f"\nTabela completa no HOLDOUT (limiar recalculado sobre a taxa geral do holdout, {overall_rate_holdout*100:.3f}%):")
print(seg_holdout.to_string(index=False))

flagged_original = {("UK", "Q4", "Recorrente"), ("Resto", "Q2", "Recorrente"), ("Resto", "Q1", "Recorrente")}
sinalizados_holdout = set(seg_holdout[seg_holdout["sinalizado_holdout"]][["country_group", "qty_quartil", "segmento_cliente"]]
                           .apply(tuple, axis=1))
print(f"\nSinalizados no HOLDOUT com a mesma regra: {sinalizados_holdout}")
print(f"Sinalizados no IMPROVE (exploracao): {flagged_original}")
print(f"Interseccao: {flagged_original & sinalizados_holdout}")
print(f"So no Improve (nao se sustentaram no holdout): {flagged_original - sinalizados_holdout}")
print(f"So no holdout (novos, nao previstos): {sinalizados_holdout - flagged_original}")

section("2b. Persistencia dos StockCodes de H4 (produtos sinalizados)")
sc_exp = exploracao.groupby("StockCode").agg(n=("defect", "size"), d=("defect", "sum"))
sc_exp["rate"] = sc_exp["d"] / sc_exp["n"]
overall_exp = exploracao["defect"].mean()
top_h4_exp = set(sc_exp[(sc_exp["n"] >= 50) & (sc_exp["rate"] >= 2 * overall_exp)].index)

sc_hold = holdout.groupby("StockCode").agg(n=("defect", "size"), d=("defect", "sum"))
sc_hold["rate"] = sc_hold["d"] / sc_hold["n"]
sc_hold_avail = sc_hold[sc_hold.index.isin(top_h4_exp) & (sc_hold["n"] >= 10)]
print(f"Dos {len(top_h4_exp)} StockCodes sinalizados por H4 na exploracao, {len(sc_hold_avail)} aparecem no holdout com n>=10.")
print(f"Taxa media desses StockCodes no holdout: {sc_hold_avail['rate'].mean()*100:.2f}% vs. taxa geral do holdout {overall_rate_holdout*100:.2f}%")
print(sc_hold_avail.sort_values("rate", ascending=False).head(10))

# ===========================================================================
section("CONGELAMENTO DO RESULTADO DO HOLDOUT (artefato imutavel)")
resultado = {
    "data_abertura": "2026-09-20",
    "aviso": "Abertura UNICA do holdout. Nao repetir esta leitura. Correcao futura so como adendo datado.",
    "holdout_n": int(n_h),
    "holdout_defeitos": int(d_h),
    "holdout_taxa": round(float(p_h), 6),
    "holdout_ic95_wilson": [round(float(ci_h[0]), 6), round(float(ci_h[1]), 6)],
    "projecao_exploracao_madura": {
        "media_mensal": round(float(mean_rate), 6),
        "intervalo_projetado_95": [round(float(proj_lo), 6), round(float(proj_hi), 6)],
    },
    "taxa_holdout_dentro_da_projecao": bool(dentro_projecao),
    "segmentos_sinalizados_no_improve": sorted(list(flagged_original)),
    "segmentos_sinalizados_no_holdout_mesma_regra": sorted(list(sinalizados_holdout)),
    "segmentos_que_se_sustentaram": sorted(list(flagged_original & sinalizados_holdout)),
    "segmentos_que_nao_se_sustentaram": sorted(list(flagged_original - sinalizados_holdout)),
    "h4_stockcodes_sinalizados_exploracao": len(top_h4_exp),
    "h4_stockcodes_com_dado_suficiente_no_holdout": int(len(sc_hold_avail)),
    "h4_taxa_media_holdout_desses_produtos": round(float(sc_hold_avail["rate"].mean()), 6) if len(sc_hold_avail) else None,
    "h4_taxa_geral_holdout": round(float(overall_rate_holdout), 6),
}
with open("docs/holdout_resultado.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)
print(json.dumps(resultado, ensure_ascii=False, indent=2))
print("\nSalvo em docs/holdout_resultado.json -- ARTEFATO IMUTAVEL a partir de agora.")
