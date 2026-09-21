"""Fase 6 - ENTREGA - consolida os agregados de todas as fases num unico JSON
para a pagina de entrega (entrega-dmaic). Nenhum numero da pagina pode ser
digitado a mao; tudo sai deste arquivo: docs/entrega_dados.json.

Reusa a MESMA logica de pareamento das fases 2B/3/5. Como o projeto ja fechou
(holdout ja aberto e registrado), o cubo do DASHBOARD cobre o ANO INTEIRO
(dez/2010-dez/2011) para servir de ferramenta de exploracao publica; o PAINEL
mostra o baseline OFICIAL CONGELADO (janela de exploracao), que e o artefato de
governanca do projeto.
"""
import json
import numpy as np
import pandas as pd
from bisect import bisect_left
from statsmodels.stats.proportion import proportion_confint
from config import get_non_product_codes, HOLDOUT_START, RISK_SEGMENT_RATE_MULTIPLIER, RISK_SEGMENT_MIN_N

pd.set_option("display.width", 140)

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
orders_all = orders_scope[orders_scope["CustomerID"].notnull()].reset_index(drop=True).copy()
cancels_all = cancels_scope[cancels_scope["CustomerID"].notnull()].copy()

def parear(orders_df, cancels_df, out_col):
    """Pareamento nearest-preceding-order. Escreve out_col em orders_df (copia)."""
    orders_df = orders_df.copy()
    orders_df[out_col] = 0
    key_to_rows = {}
    for idx, row in orders_df.iterrows():
        key = (row["CustomerID"], row["StockCode"])
        key_to_rows.setdefault(key, []).append((row["InvoiceDate"], idx))
    for key in key_to_rows:
        key_to_rows[key].sort()
    for _, crow in cancels_df.iterrows():
        key = (crow["CustomerID"], crow["StockCode"])
        candidates = key_to_rows.get(key)
        if not candidates:
            continue
        dates = [d for d, _ in candidates]
        pos = bisect_left(dates, crow["InvoiceDate"])
        if pos == 0:
            continue
        _, prior_idx = candidates[pos - 1]
        orders_df.at[prior_idx, out_col] = 1
    return orders_df

# defect_full: pareamento sobre o ANO INTEIRO (identico a fase5_abertura_holdout.py) -
# usado no cubo do dashboard e nas comparacoes com holdout_resultado.json.
orders_all = parear(orders_all, cancels_all, "defect")
orders_all["revenue"] = orders_all["Quantity"] * orders_all["UnitPrice"]
orders_all["in_holdout"] = orders_all["InvoiceDate"] >= HOLDOUT_START

# defect_frozen: pareamento restrito a pedidos E cancelamentos da JANELA DE
# EXPLORACAO apenas - reproduz exatamente a logica da 2B/Analyze, cujo
# resultado esta congelado em baseline_congelado.json. Precisa bater 100%
# antes de prosseguir, ou o artefato imutavel foi contradito.
orders_exp_only = orders_all[~orders_all["in_holdout"]].drop(columns=["defect"]).copy()
cancels_exp_only = cancels_all[cancels_all["InvoiceDate"] < HOLDOUT_START].copy()
baseline_pop = parear(orders_exp_only, cancels_exp_only, "defect")

print(f"Universo completo (ano inteiro): {len(orders_all)}")
print(f"Universo do baseline congelado (exploracao): {len(baseline_pop)} (deve ser 265427)")
assert len(baseline_pop) == 265427, "populacao do baseline divergiu do congelado na 2B -- INVESTIGAR antes de prosseguir"
assert int(baseline_pop['defect'].sum()) == 4957, "contagem de defeito divergiu do congelado na 2B -- INVESTIGAR"

def descricao(codigo):
    sub = raw.loc[raw["StockCode"] == codigo, "Description"].dropna()
    if not len(sub):
        return codigo
    d = sub.mode().iloc[0].strip()
    d = " ".join(w.capitalize() if len(w) > 2 else w.lower() for w in d.split())
    return f"{codigo} · {d}"

with open("docs/baseline_congelado.json", encoding="utf-8") as f:
    baseline = json.load(f)
with open("docs/holdout_resultado.json", encoding="utf-8") as f:
    holdout_json = json.load(f)

out = {}

# ---------------------------------------------------------------------------
# PAINEL - numero principal e distancia da meta usam a MESMA janela (madura,
# dez/2010-ago/2011), para nao misturar duas bases no mesmo bloco. O baseline
# congelado da 2B (10 meses, com set/2011 contaminado por censura) continua
# sendo o artefato oficial de governanca do projeto, citado a parte no
# Relatorio/JSON, mas nao entra no bloco de hero do Painel.
# ---------------------------------------------------------------------------
baseline_pop["month"] = baseline_pop["InvoiceDate"].dt.to_period("M")
monthly_all = baseline_pop.groupby("month").agg(n=("defect", "size"), d=("defect", "sum"))
mes_maduro = monthly_all.index[monthly_all.index < monthly_all.index.max()]  # exclui set/2011
madura = baseline_pop[baseline_pop["month"].isin(mes_maduro)]
n_mat = len(madura)
d_mat = int(madura["defect"].sum())
p_mat = d_mat / n_mat
ic_mat = proportion_confint(d_mat, n_mat, method="wilson")
dpmo_mat = p_mat * 1_000_000
from scipy import stats as _stats
sigma_mat = _stats.norm.ppf(1 - p_mat)

out["painel"] = {
    "janela_label": "janela madura (dez/2010-ago/2011, exclui set/2011)",
    "taxa": round(p_mat, 6),
    "ic95": [round(float(ic_mat[0]), 6), round(float(ic_mat[1]), 6)],
    "n": n_mat,
    "d": d_mat,
    "dpmo": round(float(dpmo_mat), 1),
    "sigma_longo_prazo": round(float(sigma_mat), 3),
    "sigma_deslocado": round(float(sigma_mat) + 1.5, 2),
    "meta_interna_janela_madura": baseline["meta_interna_p25_mensal_janela_madura"],
    "gap_pp_janela_madura": round((p_mat - baseline["meta_interna_p25_mensal_janela_madura"]) * 100, 3),
    "receita_estornada": round(float(madura.loc[madura["defect"] == 1, "revenue"].sum()), 2),
    "baseline_congelado_10meses": {
        "nota": "Artefato oficial congelado na Fase 2B, sobre os 10 meses inteiros da janela de exploracao (inclui set/2011, ver nota de censura). Nao usado no bloco principal do Painel para nao misturar duas bases sem aviso.",
        "taxa": baseline["taxa_cancelamento"], "ic95": baseline["ic95_wilson"], "n": baseline["n_total_universo"],
    },
}

# ---------------------------------------------------------------------------
# Carta p' de Laney, semanal, sobre a janela de exploracao inteira (10 meses).
# Por que Laney: com n semanal ainda na casa dos milhares, os limites binomiais
# classicos (carta p) ficam estreitos demais quando ha sobredispersao (variacao
# real entre periodos maior do que o binomial preve) - e foi exatamente isso
# que a carta mensal mostrou (4 de 10 meses fora, o que e sintoma de
# sobredispersao, nao de 4 causas especiais). A p' de Laney mede essa
# sobredispersao (sigma_z, via amplitude movel dos escores padronizados Z) e
# alarga os limites na proporcao certa, sem inventar causa especial onde ha so
# variacao extra-binomial.
# ---------------------------------------------------------------------------
baseline_pop["week"] = baseline_pop["InvoiceDate"].dt.to_period("W")
weekly = baseline_pop.groupby("week").agg(n=("defect", "size"), d=("defect", "sum")).sort_index()
weekly["p"] = weekly["d"] / weekly["n"]
p_bar_w = weekly["d"].sum() / weekly["n"].sum()
weekly["sigma_pi"] = np.sqrt(p_bar_w * (1 - p_bar_w) / weekly["n"])
weekly["Z"] = (weekly["p"] - p_bar_w) / weekly["sigma_pi"]
mr = weekly["Z"].diff().abs().dropna()
mr_bar = mr.mean()
sigma_z = mr_bar / 1.128
weekly["UCL"] = np.minimum(1, p_bar_w + 3 * sigma_z * weekly["sigma_pi"])
weekly["LCL"] = np.maximum(0, p_bar_w - 3 * sigma_z * weekly["sigma_pi"])
weekly["fora"] = (weekly["p"] > weekly["UCL"]) | (weekly["p"] < weekly["LCL"])

semanas_str = [str(w.start_time.date()) for w in weekly.index]
holdout_boundary = pd.Timestamp("2011-10-01")
dias_ate_corte = [(holdout_boundary - w.end_time).days for w in weekly.index]

# Reclassificacao apos Laney: das 43 semanas, so as 2 mais proximas do corte do
# holdout (5 e -2 dias de distancia) ficam fora dos limites, e as duas para
# BAIXO -- exatamente a assinatura esperada de censura a direita (semana sem
# tempo de o cancelamento aparecer nos dados), nao de causa especial real no
# meio da serie. As outras 41 semanas sao causa comum.
classificacao = ["artefato_censura" if fora else "comum" for fora in weekly["fora"]]
out["carta_p"] = {
    "tipo": "Laney p' (semanal)",
    "sigma_z": round(float(sigma_z), 3),
    "semanas": semanas_str,
    "taxa": [round(float(v) * 100, 4) for v in weekly["p"]],
    "n": [int(v) for v in weekly["n"]],
    "ucl": [round(float(v) * 100, 4) for v in weekly["UCL"]],
    "lcl": [round(float(v) * 100, 4) for v in weekly["LCL"]],
    "cl": round(float(p_bar_w) * 100, 4),
    "fora": [bool(v) for v in weekly["fora"]],
    "classificacao": classificacao,
    "dias_ate_corte_holdout": dias_ate_corte,
}
print(f"\nLaney p' semanal: sigma_z={sigma_z:.3f} (>1 confirma sobredispersao); pontos fora: {int(weekly['fora'].sum())} de {len(weekly)}")
print(weekly[["n", "p", "UCL", "LCL", "fora"]].assign(dias_ate_corte=dias_ate_corte).to_string())

# guardrails (sobre a populacao do baseline)
n_invoices = baseline_pop["InvoiceNo"].nunique()
n_customers = baseline_pop["CustomerID"].nunique()
receita_liquida = float(baseline_pop.loc[baseline_pop["defect"] == 0, "revenue"].sum())
out["guardrails"] = {
    "receita_liquida": round(receita_liquida, 2),
    "pedidos": int(n_invoices),
    "clientes_ativos": int(n_customers),
}

# Segmentos de risco (Country x Quantity x Recorrencia) - continuam existindo
# para o Improve/Dashboard (matriz Pais x Faixa), mas NAO alimentam mais os
# dois Paretos do Painel (ver ajuste do usuario: os dois Paretos vao para a
# MESMA dimensao, produto, para mostrar que as duas ordens discordam).
baseline_pop["qty_quartil"] = pd.qcut(baseline_pop["Quantity"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
baseline_pop["country_group"] = np.where(baseline_pop["Country"] == "United Kingdom", "UK", "Resto")
first_date = baseline_pop.groupby("CustomerID")["InvoiceDate"].transform("min")
baseline_pop["segmento_cliente"] = np.where(baseline_pop["InvoiceDate"] == first_date, "Primeira compra", "Recorrente")
overall_rate = baseline_pop["defect"].mean()

seg = baseline_pop.groupby(["country_group", "qty_quartil", "segmento_cliente"], observed=True).agg(
    n=("defect", "size"), d=("defect", "sum"), es=("revenue", lambda s: s[baseline_pop.loc[s.index, "defect"] == 1].sum())
).reset_index()
seg["taxa"] = seg["d"] / seg["n"]
seg["label"] = seg["country_group"] + " · " + seg["qty_quartil"].astype(str) + " · " + seg["segmento_cliente"]
seg["sinalizado"] = (seg["taxa"] >= overall_rate * RISK_SEGMENT_RATE_MULTIPLIER) & (seg["n"] >= RISK_SEGMENT_MIN_N)
out["segmentos_sinalizados"] = [
    {"label": r["label"], "taxa": round(float(r["taxa"]) * 100, 3), "n": int(r["n"]), "es_cancelado": round(float(r["es"]), 2)}
    for _, r in seg[seg["sinalizado"]].sort_values("taxa", ascending=False).iterrows()
]

# Os DOIS PARETOS do Painel, mesma dimensao (StockCode / produto), n>=50 (mesmo
# corte do H4) para nao deixar um produto de n baixo dominar por acaso.
sc = baseline_pop.groupby("StockCode").agg(n=("defect", "size"), d=("defect", "sum"))
sc["es"] = baseline_pop[baseline_pop["defect"] == 1].groupby("StockCode")["revenue"].sum()
sc["es"] = sc["es"].fillna(0)
sc["taxa"] = sc["d"] / sc["n"]
sc_valid = sc[sc["n"] >= 50].copy()
sc_valid["rate_ratio"] = sc_valid["taxa"] / overall_rate
total_es_defeito_valid = sc_valid["es"].sum()

pareto_taxa_top = sc_valid.sort_values("taxa", ascending=False).head(10).copy()
out["pareto_taxa"] = [
    {"stockcode": idx, "label": descricao(idx), "taxa": round(float(r["taxa"]) * 100, 3), "n": int(r["n"]), "vezes_media": round(float(r["rate_ratio"]), 1)}
    for idx, r in pareto_taxa_top.iterrows()
]

pareto_impacto_top = sc_valid.sort_values("es", ascending=False).head(10).copy()
pareto_impacto_top["pct_cum"] = pareto_impacto_top["es"].cumsum() / total_es_defeito_valid * 100
out["pareto_impacto"] = [
    {"stockcode": idx, "label": descricao(idx), "es": round(float(r["es"]), 2), "pct_cum": round(float(r["pct_cum"]), 1), "n": int(r["n"]), "taxa": round(float(r["taxa"]) * 100, 2)}
    for idx, r in pareto_impacto_top.iterrows()
]
out["pareto_impacto_total_es"] = round(float(total_es_defeito_valid), 2)

# Comparacao explicita: rank por taxa x rank por impacto, para os produtos que
# aparecem em qualquer um dos dois top-10 (mostra que as ordens discordam).
rank_taxa = sc_valid["taxa"].rank(ascending=False, method="min")
rank_impacto = sc_valid["es"].rank(ascending=False, method="min")
uniao_idx = sorted(set(pareto_taxa_top.index) | set(pareto_impacto_top.index), key=lambda i: rank_impacto[i])
out["pareto_comparacao"] = [
    {"stockcode": i, "label": descricao(i), "rank_taxa": int(rank_taxa[i]), "rank_impacto": int(rank_impacto[i]),
     "taxa": round(float(sc_valid.loc[i, "taxa"]) * 100, 2), "es": round(float(sc_valid.loc[i, "es"]), 2)}
    for i in uniao_idx
]

# H4 -- produtos sinalizados (>=2x a taxa media, n>=50) -- mesma base de sc_valid
h4_flagged = sc_valid[sc_valid["rate_ratio"] >= 2].sort_values("taxa", ascending=False)
out["h4"] = {
    "n_produtos_avaliados": int(len(sc_valid)),
    "n_sinalizados": int(len(h4_flagged)),
    "top10": [
        {"stockcode": idx, "label": descricao(idx), "taxa": round(float(r["taxa"]) * 100, 2), "n": int(r["n"]), "vezes_media": round(float(r["rate_ratio"]), 1)}
        for idx, r in h4_flagged.head(10).iterrows()
    ],
}

# ---------------------------------------------------------------------------
# RELATORIO - numeros herdados dos memorandos de fase (copiados aqui como
# valores fixos calculados alhures no pipeline, nao recalculados)
# ---------------------------------------------------------------------------
out["analyze"] = {
    "pareamento_pct": 85.0,
    "pareamento_pct_fase0": 81.8,
    "h5_efeito_uk_pp": 1.714,
    "h5_efeito_resto_pp": -1.718,
    "h5_breslow_day_p_country": "<0,0001",
    "h5_breslow_day_p_recorrencia": 0.3765,
    "h5_reducao_pct_logit": 3.0,
    "h1_efeito_pp": 1.509,
    "h1_efeito_minimo_pp": 3.0,
    "h1_ic": [1.344, 1.673],
    "h2_efeito_pp": 0.588,
    "h2_efeito_minimo_pp": 5.0,
    "h2_ic": [0.406, 0.770],
    "h3_efeito_pp": 0.138,
    "h3_p": 0.129,
    "quantificacao": {
        "total_defeitos": 4957,
        "total_receita": 313175.97,
        "h1_pct": 24.9, "h1_receita": 233002.96,
        "h2_pct": 14.3, "h2_receita": 34435.88,
        "h4_pct": 40.4, "h4_receita": 164305.89,
        "uniao_pct": 62.9, "uniao_receita": 276304.92,
        "sem_explicacao_pct": 37.1, "sem_explicacao_receita": 36871.05,
    },
}

out["improve"] = {
    "segmento_total_n": 34257, "segmento_total_d": 1052, "segmento_legit": 33205,
    "receita_media_cancelada": 100.77, "receita_media_geral": 63.55,
    "cenarios": {
        "conservador": {"f": 20, "ganho": -21001.91, "indiferenca": 1.005},
        "central": {"f": 40, "ganho": 200.06, "indiferenca": 2.009},
        "otimista": {"f": 60, "ganho": 21402.03, "indiferenca": 3.014},
    },
    "experimento": {
        "baseline_segmento": 3.071, "efeito_detectar_pp": 1.228, "n_por_braco": 2454,
        "pedidos_mes_segmento": 3426, "meses_para_n": 1.4,
    },
    "fmea": [
        {"modo": "Fricção afasta revendedores de alto volume", "sev": 9, "oco": 6, "det": 4, "npr": 216},
        {"modo": "Regra de Quantity aplicada fora do UK por engano", "sev": 8, "oco": 3, "det": 5, "npr": 120},
        {"modo": "Regra de segmento desatualiza com mudança de mix", "sev": 6, "oco": 5, "det": 3, "npr": 90},
    ],
}

out["qualidade"] = {
    "customerid_nulo_pct": 24.93,
    "customerid_nulo_uk_pct": round(float(raw.loc[raw["Country"] == "United Kingdom", "CustomerID"].isnull().mean() * 100), 2),
    "customerid_nulo_naouk_pct": round(float(raw.loc[raw["Country"] != "United Kingdom", "CustomerID"].isnull().mean() * 100), 2),
    "duplicata_exata_pct": 1.87,
    "descricao_inconsistente_pct": 16.42,
    "preco_nao_positivo_ajuste": 2517,
    "stockcodes_nao_produto": NON_PRODUCT_CODES,
    "outlier_excluido": {
        "stockcode": "23843", "descricao": "PAPER CRAFT , LITTLE BIRDIE",
        "invoice_original": "581483", "invoice_cancelamento": "C581484",
        "quantidade": 80995, "data": "2011-12-09",
        "nota": "Par pedido/cancelamento de 80.995 unidades, lancado e cancelado com 12 minutos de diferenca, mesmo cliente, mesmo dia. Evento isolado, nao padrao de produto - excluido da selecao dos produtos nomeados no cubo do Dashboard e dos dois Paretos do Painel via o mesmo corte de n>=50 usado no H4 (o par por si so nao muda n, mas sua receita dominaria qualquer ranking por impacto se incluido sem o corte)."
    },
}

out["holdout"] = holdout_json

# ---------------------------------------------------------------------------
# DASHBOARD - cubo agregado, ANO INTEIRO (dez/2010-dez/2011)
# ---------------------------------------------------------------------------
orders_all["month"] = orders_all["InvoiceDate"].dt.to_period("M")
meses_ord = sorted(orders_all["month"].unique())
MES_LABELS = [str(m) for m in meses_ord]
month_idx = {m: i for i, m in enumerate(meses_ord)}
orders_all["mi"] = orders_all["month"].map(month_idx)

country_counts = orders_all["Country"].value_counts()
top_countries = country_counts[country_counts >= 300].index.tolist()
if "United Kingdom" not in top_countries:
    top_countries.append("United Kingdom")
top_countries = sorted(top_countries, key=lambda c: -country_counts[c])
PAIS_LABELS = top_countries + ["Outros países"]
pais_idx = {c: i for i, c in enumerate(top_countries)}
orders_all["pi"] = orders_all["Country"].map(lambda c: pais_idx.get(c, len(top_countries)))

orders_all["qty_quartil_full"] = pd.qcut(orders_all["Quantity"], 4, labels=[0, 1, 2, 3]).astype(int)
FAIXA_LABELS = ["Q1 (menor)", "Q2", "Q3", "Q4 (maior)"]

first_date_full = orders_all.groupby("CustomerID")["InvoiceDate"].transform("min")
orders_all["seg_idx"] = np.where(orders_all["InvoiceDate"] == first_date_full, 0, 1)
SEG_LABELS = ["Primeira compra", "Recorrente"]

sku_n = orders_all.groupby("StockCode").size()
sku_revenue_all = orders_all[orders_all["defect"] == 1].groupby("StockCode")["revenue"].sum()
sku_revenue = sku_revenue_all[sku_revenue_all.index.isin(sku_n[sku_n >= 50].index)].sort_values(ascending=False)
# guarda contra outlier de transacao unica: StockCode 23843 e um unico par
# pedido/cancelamento de 80.995 unidades no mesmo dia (evento isolado, nao
# padrao de produto) - o corte de n>=50 (mesmo criterio do H4) ja o exclui.
top_skus = sku_revenue.head(10).index.tolist()
SKU_LABELS = [descricao(s) for s in top_skus] + ["Outros produtos"]
sku_idx = {s: i for i, s in enumerate(top_skus)}
orders_all["si"] = orders_all["StockCode"].map(lambda s: sku_idx.get(s, len(top_skus)))

grp = orders_all.groupby(["mi", "pi", "qty_quartil_full", "seg_idx", "si"]).agg(
    it=("defect", "size"), ca=("defect", "sum"), es=("revenue", lambda s: s[orders_all.loc[s.index, "defect"] == 1].sum())
).reset_index()
# campos ja nomeados g/f/s/p (mesma convencao de chave de uma letra usada no
# JS do molde: g=pais, f=faixa de quantidade, s=recorrencia, p=produto)
grp = grp.rename(columns={"mi": "m", "pi": "g", "qty_quartil_full": "f", "seg_idx": "s", "si": "p"})
cubo = grp.to_dict(orient="records")
cubo = [{"m": int(r["m"]), "g": int(r["g"]), "f": int(r["f"]), "s": int(r["s"]), "p": int(r["p"]),
         "it": int(r["it"]), "ca": int(r["ca"]), "es": round(float(r["es"]), 2)} for r in cubo]

out["dashboard"] = {
    "meses": MES_LABELS,
    "paises": PAIS_LABELS,
    "faixas": FAIXA_LABELS,
    "segmentos": SEG_LABELS,
    "produtos": SKU_LABELS,
    "cubo": cubo,
    "total_linhas_ano": len(orders_all),
    "taxa_ano_inteiro": round(float(orders_all["defect"].mean()) * 100, 3),
    "nota_janela": "Cobre o ANO INTEIRO (dez/2010-dez/2011), incluindo os ~2,3 meses finais que ficaram em quarentena (holdout) durante a analise e so foram abertos ao final -- por isso a taxa aqui difere da taxa oficial do Painel, que usa so a janela de exploracao.",
}

with open("docs/entrega_dados.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f"\nCubo: {len(cubo)} celulas nao vazias")
print(f"Paises no cubo: {len(PAIS_LABELS)} -> {PAIS_LABELS}")
print(f"SKUs no cubo (top10 por receita cancelada + Outros): {SKU_LABELS}")
print(f"Meses no cubo: {len(MES_LABELS)}")
print("\nSalvo em docs/entrega_dados.json")
print(f"Tamanho do arquivo: {__import__('os').path.getsize('docs/entrega_dados.json')/1024:.0f} KB")
