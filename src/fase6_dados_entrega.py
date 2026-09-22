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

# [C1] mesmo ajuste do baseline_pop (ver bloco abaixo), aplicado tambem ao
# dataset do ano inteiro que alimenta o cubo do Dashboard - a mesma linha
# outlier (23166/541431) tambem distorceria o "onde esta o dinheiro" e a
# selecao de produtos nomeados no Dashboard se nao fosse ajustada aqui.
_OUTLIER_C1_FULL = (orders_all["InvoiceNo"] == "541431") & (orders_all["StockCode"] == "23166")
orders_all["revenue_pareto"] = orders_all["revenue"]
orders_all.loc[_OUTLIER_C1_FULL & (orders_all["defect"] == 1), "revenue_pareto"] = 0.0

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

# ---------------------------------------------------------------------------
# [C1] CORRECAO POS-BANCA (2026-09-22): a linha de cancelamento StockCode
# 23166 / InvoiceNo 541431 (74.215 unidades, £77.183,60 - 99,5% do estorno
# atribuido ao produto) e uma transacao isolada de um so dia, mesmo padrao
# de anomalia ja tratado para o StockCode 23843 (excluido por nao passar do
# corte de n>=50). Aqui o produto 23166 tem 137 linhas legitimas e permanece
# na base normalmente; so a RECEITA desta linha especifica e zerada para fins
# de RANKING DE IMPACTO (Pareto por produto) - ela continua contando como
# defeito real para taxa/contagem (n, d), que a banca nao questionou. Nao
# mexe na taxa geral do baseline (1,868%/2,05%), nos guardrails nem no DPMO -
# escopo estritamente o Pareto de impacto por produto, como pedido.
_OUTLIER_C1 = (baseline_pop["InvoiceNo"] == "541431") & (baseline_pop["StockCode"] == "23166")
assert _OUTLIER_C1.sum() == 1, "linha outlier do C1 nao encontrada como esperado - verificar antes de prosseguir"
baseline_pop["revenue_pareto"] = baseline_pop["revenue"]
baseline_pop.loc[_OUTLIER_C1 & (baseline_pop["defect"] == 1), "revenue_pareto"] = 0.0
print(f"[C1] Linha outlier (23166/541431) zerada apenas em revenue_pareto (Pareto de impacto); "
      f"segue contando normalmente em n/d/taxa e na receita estornada geral do Painel.")

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
# [C1] usa revenue_pareto (linha 23166/541431 zerada) - nao "revenue" cru
sc["es"] = baseline_pop[baseline_pop["defect"] == 1].groupby("StockCode")["revenue_pareto"].sum()
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

# [I4] CORRECAO POS-BANCA (2026-09-22): o corte original (taxa PONTUAL >=2x a
# media, n>=50) nao controla falso positivo - com n=50 e a taxa media da base,
# um produto sem nenhum problema real tem ~1/4 de chance de bater "2x a media"
# so por acaso. Corrigido para usar o LIMITE INFERIOR do IC de Wilson da taxa
# (mesmo tipo de intervalo ja usado nos exemplos 21232/21231 do Relatorio) -
# criterio mais conservador, reduz de 198 para os produtos abaixo.
sc_valid["ci_lo"] = sc_valid.apply(lambda r: proportion_confint(r["d"], r["n"], method="wilson")[0], axis=1)
sc_valid["rate_ratio_ic_lo"] = sc_valid["ci_lo"] / overall_rate
h4_flagged = sc_valid[sc_valid["rate_ratio_ic_lo"] >= 2].sort_values("taxa", ascending=False)
h4_flagged_old_criterio = sc_valid[sc_valid["rate_ratio"] >= 2]
out["h4"] = {
    "n_produtos_avaliados": int(len(sc_valid)),
    "n_sinalizados": int(len(h4_flagged)),
    "n_sinalizados_criterio_antigo": int(len(h4_flagged_old_criterio)),
    "criterio": "limite inferior do IC de Wilson >= 2x a taxa media (corrigido de taxa pontual em 2026-09-22, ver I4)",
    "top10": [
        {"stockcode": idx, "label": descricao(idx), "taxa": round(float(r["taxa"]) * 100, 2), "n": int(r["n"]),
         "vezes_media": round(float(r["rate_ratio"]), 1), "vezes_media_ic_lo": round(float(r["rate_ratio_ic_lo"]), 1)}
        for idx, r in h4_flagged.head(10).iterrows()
    ],
}
h4_flagged_codes = set(h4_flagged.index)

# ---------------------------------------------------------------------------
# RELATORIO - numeros herdados dos memorandos de fase (copiados aqui como
# valores fixos calculados alhures no pipeline, nao recalculados)
# ---------------------------------------------------------------------------
# [I4] quantificacao recomputada direto dos dados (nao mais hardcoded) para
# refletir o novo conjunto do H4 (limite inferior do IC, nao taxa pontual).
_defects = baseline_pop[baseline_pop["defect"] == 1].copy()
_total_defeitos = len(_defects)
_total_receita = _defects["revenue"].sum()
_flag_h1 = _defects["qty_quartil"] == "Q4"
_flag_h2 = _defects["country_group"] == "Resto"
_flag_h4 = _defects["StockCode"].isin(h4_flagged_codes)
_uniao = _flag_h1 | _flag_h2 | _flag_h4
_sem_explicacao = ~_uniao

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
        "total_defeitos": int(_total_defeitos),
        "total_receita": round(float(_total_receita), 2),
        "h1_pct": round(float(_flag_h1.mean() * 100), 1), "h1_receita": round(float(_defects.loc[_flag_h1, "revenue"].sum()), 2),
        "h2_pct": round(float(_flag_h2.mean() * 100), 1), "h2_receita": round(float(_defects.loc[_flag_h2, "revenue"].sum()), 2),
        "h4_pct": round(float(_flag_h4.mean() * 100), 1), "h4_receita": round(float(_defects.loc[_flag_h4, "revenue_pareto"].sum()), 2),
        "uniao_pct": round(float(_uniao.mean() * 100), 1), "uniao_receita": round(float(_defects.loc[_uniao, "revenue"].sum()), 2),
        "sem_explicacao_pct": round(float(_sem_explicacao.mean() * 100), 1), "sem_explicacao_receita": round(float(_defects.loc[_sem_explicacao, "revenue"].sum()), 2),
    },
}
print(f"[I4] H4 corrigido (IC Wilson >=2x): {len(h4_flagged_codes)} produtos (era {len(h4_flagged_old_criterio)} pelo criterio antigo)")
print(f"[I4] quantificacao: H4={out['analyze']['quantificacao']['h4_pct']}%% uniao={out['analyze']['quantificacao']['uniao_pct']}%% sem_explicacao={out['analyze']['quantificacao']['sem_explicacao_pct']}%%")

# ---------------------------------------------------------------------------
# [C2] CORRECAO POS-BANCA (2026-09-22): a conta do Improve usava contagem de
# LINHAS (InvoiceNo x StockCode) como se fosse contagem de PEDIDOS. Abandono
# de checkout e um evento por FATURA, nao por linha de produto - recalculado
# abaixo direto dos dados (nada hardcoded), usando fatura (InvoiceNo) como
# unidade para o lado do abandono. A receita preservada (que depende de
# quantas LINHAS de cancelamento a verificacao evitaria) continua em linhas,
# como pedido pela banca ("a receita total preservada, em soma, nao precisa
# mudar - so a base de pedidos legitimos").
FLAGGED_SEGMENTS = [("UK", "Q4", "Recorrente"), ("Resto", "Q2", "Recorrente"), ("Resto", "Q1", "Recorrente")]
_seg_mask = pd.Series(False, index=baseline_pop.index)
for _g, _f, _s in FLAGGED_SEGMENTS:
    _seg_mask |= (baseline_pop["country_group"] == _g) & (baseline_pop["qty_quartil"] == _f) & (baseline_pop["segmento_cliente"] == _s)
seg_pop = baseline_pop[_seg_mask].copy()

segmento_total_n = int(len(seg_pop))                       # linhas (para a receita preservada)
segmento_total_d = int(seg_pop["defect"].sum())             # linhas canceladas
receita_media_cancelada = float(seg_pop.loc[seg_pop["defect"] == 1, "revenue"].mean())

inv_defect = seg_pop.groupby("InvoiceNo")["defect"].max()
faturas_total = int(inv_defect.shape[0])
faturas_com_cancelamento = int((inv_defect == 1).sum())
faturas_legit_idx = inv_defect[inv_defect == 0].index
faturas_legitimas = int(len(faturas_legit_idx))
receita_media_fatura_legit = float(seg_pop[seg_pop["InvoiceNo"].isin(faturas_legit_idx)].groupby("InvoiceNo")["revenue"].sum().mean())

_a_abandono = 0.02
cenarios = {}
for nome, f in [("conservador", 0.20), ("central", 0.40), ("otimista", 0.60)]:
    linhas_evitadas = segmento_total_d * f
    receita_preservada = linhas_evitadas * receita_media_cancelada
    faturas_abandonadas = _a_abandono * faturas_legitimas
    receita_perdida = faturas_abandonadas * receita_media_fatura_legit
    ganho = receita_preservada - receita_perdida
    indiferenca = receita_preservada / (faturas_legitimas * receita_media_fatura_legit) * 100
    cenarios[nome] = {"f": int(f * 100), "ganho": round(ganho, 2), "indiferenca": round(indiferenca, 3)}

_taxa_base_fatura = faturas_com_cancelamento / faturas_total
_efeito_detectar = _taxa_base_fatura * 0.40  # reducao relativa de 40%, mesma premissa central
from statsmodels.stats.power import NormalIndPower as _NIP
from statsmodels.stats.proportion import proportion_effectsize as _pe
_h = _pe(_taxa_base_fatura - _efeito_detectar, _taxa_base_fatura)
_n_por_braco = _NIP().solve_power(effect_size=_h, alpha=0.05, power=0.8, ratio=1.0)
_faturas_mes_segmento = faturas_total / 10  # janela madura ~10 meses de exploracao

out["improve"] = {
    "unidade_abandono": "fatura (InvoiceNo) - corrigido de linha para fatura em 2026-09-22, ver C2",
    "segmento_total_n": segmento_total_n,
    "segmento_total_d": segmento_total_d,
    "receita_media_cancelada": round(receita_media_cancelada, 2),
    "faturas_total": faturas_total,
    "faturas_com_cancelamento": faturas_com_cancelamento,
    "faturas_legitimas": faturas_legitimas,
    "faturas_legitimas_pct": round(faturas_legitimas / faturas_total * 100, 1),
    "receita_media_fatura_legit": round(receita_media_fatura_legit, 2),
    "cenarios": cenarios,
    "experimento": {
        "baseline_segmento_fatura_pct": round(_taxa_base_fatura * 100, 3),
        "efeito_detectar_pp": round((_taxa_base_fatura - _efeito_detectar) * 100, 3),
        "n_por_braco": int(round(_n_por_braco)),
        "faturas_mes_segmento": round(_faturas_mes_segmento, 1),
        "meses_para_n": round(_n_por_braco * 2 / _faturas_mes_segmento, 2),
    },
    "fmea": [
        {"modo": "Fricção afasta revendedores de alto volume", "sev": 9, "oco": 6, "det": 4, "npr": 216},
        {"modo": "Regra de Quantity aplicada fora do UK por engano", "sev": 8, "oco": 3, "det": 5, "npr": 120},
        {"modo": "Regra de segmento desatualiza com mudança de mix", "sev": 6, "oco": 5, "det": 3, "npr": 90},
    ],
}
print(f"[C2] faturas_total={faturas_total} faturas_com_cancelamento={faturas_com_cancelamento} "
      f"faturas_legitimas={faturas_legitimas} ({faturas_legitimas/faturas_total*100:.1f}%%)")
print(f"[C2] cenarios: {cenarios}")
print(f"[C2] experimento: n_por_braco={_n_por_braco:.1f} taxa_base_fatura={_taxa_base_fatura*100:.3f}%%")

# ---------------------------------------------------------------------------
# [I7] CORRECAO POS-BANCA (2026-09-22): o alarme "queda >10% vs. mes anterior"
# nao sobrevive a propria serie historica do projeto (fev/2011 e abr/2011 ja
# caem >20% mes a mes sem nenhum problema real). Testado: (a) limites I-MR
# sobre a serie de variacao % mes a mes - ficam tao largos (~-75% a -85%) que
# nunca disparariam, inuteis como alarme; (b) desvio vs. media movel dos 3
# meses anteriores - historicamente mais estavel (maior queda legitima,
# excluindo dez/2011 que e mes parcial conhecido, fica em -14,2% receita e
# -10,7% pedidos). Adotado (b): alarme por desvio da media movel de 3 meses,
# limiar de 20% (acima de qualquer queda legitima observada nesta unica
# janela). Limitacao declarada: um ano so de dado nao sustenta comparacao
# ano-contra-ano nem decomposicao formal de sazonalidade - o limiar aqui e
# calibrado nos proprios dados do projeto, nao em multiplos ciclos.
_g_ctrl = orders_all.copy()  # ano inteiro (holdout ja aberto, uso legitimo para calibrar limiar de alarme)
_g_ctrl["month"] = _g_ctrl["InvoiceDate"].dt.to_period("M")
_g_agg = _g_ctrl.groupby("month").agg(receita=("revenue", "sum"), pedidos=("InvoiceNo", "nunique"))
_g_agg["receita_ma3"] = _g_agg["receita"].rolling(3).mean().shift(1)
_g_agg["pedidos_ma3"] = _g_agg["pedidos"].rolling(3).mean().shift(1)
_g_agg["receita_dev_ma3"] = (_g_agg["receita"] / _g_agg["receita_ma3"] - 1) * 100
_g_agg["pedidos_dev_ma3"] = (_g_agg["pedidos"] / _g_agg["pedidos_ma3"] - 1) * 100
_dev_r_hist = _g_agg["receita_dev_ma3"].dropna().iloc[:-1]  # exclui dez/2011 (parcial, 9 dias)
_dev_p_hist = _g_agg["pedidos_dev_ma3"].dropna().iloc[:-1]
out["controle_alarme"] = {
    "limiar_antigo_pct": 10,
    "limiar_novo_pct": 20,
    "base_antiga": "mes anterior",
    "base_nova": "media movel dos 3 meses anteriores",
    "maior_queda_legitima_receita_pct": round(float(_dev_r_hist.min()), 1),
    "maior_queda_legitima_pedidos_pct": round(float(_dev_p_hist.min()), 1),
    "nota": "Limiar antigo (10% vs. mes anterior) disparava em meses legitimos da propria serie historica (fev e abr/2011). Novo limiar calibrado para nao disparar em nenhum mes legitimo observado nesta janela (maior queda legitima: receita -14,2%%, pedidos -10,7%%, excluindo dez/2011 que e mes parcial conhecido).",
}
print(f"[I7] maior queda legitima (media movel 3m): receita={out['controle_alarme']['maior_queda_legitima_receita_pct']}%% pedidos={out['controle_alarme']['maior_queda_legitima_pedidos_pct']}%%")

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
    "outlier_pareto_ajustado": {
        "stockcode": "23166", "descricao": descricao("23166"),
        "invoice_original": "541431", "invoice_cancelamento": "C541433",
        "quantidade": 74215, "unit_price": 1.04, "receita_linha": round(74215 * 1.04, 2),
        "data": "2011-01-18",
        "correcao": "C1 (revisao externa, 2026-09-22)",
        "nota": "Ao contrario de 23843, este produto tem 137 linhas legitimas e permanece na base normalmente (n, d e taxa inalterados). So a RECEITA desta linha especifica (£77.183,60 de £77.579,29 do produto, 99,5%) foi zerada em revenue_pareto - usada apenas nos dois Paretos do Painel e no ranking/legenda de produto do Dashboard. Nao afeta a taxa de cancelamento geral, o DPMO, a receita liquida dos guardrails nem a receita estornada do hero do Painel."
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
# [C1] revenue_pareto (nao "revenue" cru) tambem na selecao/exposicao do Dashboard
sku_revenue_all = orders_all[orders_all["defect"] == 1].groupby("StockCode")["revenue_pareto"].sum()
sku_revenue = sku_revenue_all[sku_revenue_all.index.isin(sku_n[sku_n >= 50].index)].sort_values(ascending=False)
# guarda contra outlier de transacao unica: StockCode 23843 e um unico par
# pedido/cancelamento de 80.995 unidades no mesmo dia (evento isolado, nao
# padrao de produto) - o corte de n>=50 (mesmo criterio do H4) ja o exclui.
# StockCode 23166/InvoiceNo 541431 (74.215 un., £77.183,60) e outro outlier de
# transacao unica, tratado em revenue_pareto (ver [C1] acima) - nao no corte
# de n, porque 23166 tem 137 linhas legitimas e continua no cubo normalmente.
top_skus = sku_revenue.head(10).index.tolist()
SKU_LABELS = [descricao(s) for s in top_skus] + ["Outros produtos"]
sku_idx = {s: i for i, s in enumerate(top_skus)}
orders_all["si"] = orders_all["StockCode"].map(lambda s: sku_idx.get(s, len(top_skus)))

grp = orders_all.groupby(["mi", "pi", "qty_quartil_full", "seg_idx", "si"]).agg(
    it=("defect", "size"), ca=("defect", "sum"), es=("revenue_pareto", lambda s: s[orders_all.loc[s.index, "defect"] == 1].sum())
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
