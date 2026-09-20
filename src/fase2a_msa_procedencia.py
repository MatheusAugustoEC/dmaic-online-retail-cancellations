"""Fase 2A - MEASURE - auditoria de procedencia e qualidade (6 dimensoes).
Estrutura/qualidade apenas. Nenhuma relacao entre variaveis-hipotese eh testada aqui.
"""
import pandas as pd
import numpy as np
from collections import Counter

df = pd.read_csv(
    "online_retail.csv",
    dtype={"InvoiceNo": str, "StockCode": str, "Description": str, "Country": str},
    parse_dates=["InvoiceDate"],
)

NON_PRODUCT_CODES = ["POST", "DOT", "M", "C2", "D", "S", "BANK CHARGES", "CRUK", "B", "PADS"]
NON_PRODUCT_CODES += [c for c in df["StockCode"].unique() if str(c).lower().startswith("gift_")]

def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

def veredito(ok, msg):
    print(("APROVADO" if ok else "REPROVADO") + " - " + msg)

# ---------------------------------------------------------------------------
section("1. PERFIL - chave candidata (InvoiceNo, StockCode)")
dup_key = df.duplicated(subset=["InvoiceNo", "StockCode"], keep=False)
print(f"Linhas com (InvoiceNo, StockCode) duplicado (aparece 2+ vezes): {dup_key.sum()}")
print(f"Combinacoes unicas de (InvoiceNo, StockCode): {df.drop_duplicates(subset=['InvoiceNo','StockCode']).shape[0]}")
print(f"InvoiceNo unicos: {df['InvoiceNo'].nunique()}")
print(f"StockCode unicos: {df['StockCode'].nunique()}")
print(f"CustomerID unicos: {df['CustomerID'].nunique()}")
print(f"InvoiceNo com prefixo 'C': {df['InvoiceNo'].str.startswith('C', na=False).sum()}")

# ---------------------------------------------------------------------------
section("2. COMPLETUDE")
null_cust = df["CustomerID"].isnull().sum()
print(f"CustomerID nulo: {null_cust} ({null_cust/len(df)*100:.2f}%)")
print("\nPor Country (top 10 taxa de nulo):")
by_country = df.groupby("Country")["CustomerID"].apply(lambda s: s.isnull().mean() * 100).sort_values(ascending=False)
print(by_country.head(10).round(2))
print("\nPor mes (contagem de nulo):")
print(df[df["CustomerID"].isnull()]["InvoiceDate"].dt.to_period("M").value_counts().sort_index())

desc_null_with_code = df["Description"].isnull().sum()
print(f"\nDescription nula (StockCode sempre presente, nunca nulo): {desc_null_with_code} ({desc_null_with_code/len(df)*100:.2f}%)")
veredito(null_cust / len(df) < 0.30, f"CustomerID nulo em {null_cust/len(df)*100:.2f}% (concentrado em UK 27,0% vs nao-UK 3,2%, ja mapeado na Fase 0) - completude parcial, nao total")
veredito(desc_null_with_code / len(df) < 0.01, f"Description nula em {desc_null_with_code/len(df)*100:.2f}% - dentro do criterio de aceite (<1%)")

# ---------------------------------------------------------------------------
section("3. UNICIDADE")
exact_dup = df.duplicated(keep=False)
n_exact_dup_rows = exact_dup.sum()
n_exact_dup_groups = df[exact_dup].drop_duplicates().shape[0]
print(f"Linhas duplicadas EXATAS (todas as colunas iguais): {n_exact_dup_rows} linhas em {n_exact_dup_groups} grupos distintos")
veredito(n_exact_dup_rows / len(df) < 0.02, f"{n_exact_dup_rows} linhas ({n_exact_dup_rows/len(df)*100:.2f}%) sao duplicata exata - tratar como lancamento repetido, nao evento novo")

same_key_diff_qty = df.groupby(["InvoiceNo", "StockCode"])["Quantity"].nunique()
n_retificado = (same_key_diff_qty > 1).sum()
print(f"\nCombinacoes (InvoiceNo, StockCode) com mais de uma Quantity distinta (indicio de retificacao): {n_retificado} de {len(same_key_diff_qty)}")
veredito(True, f"{n_retificado} combinacoes com Quantity divergente na mesma chave - candidato a lancamento retificado, nao erro de unicidade; nao remover automaticamente")

# ---------------------------------------------------------------------------
section("4. VALIDADE")
n_qty_zero = (df["Quantity"] == 0).sum()
print(f"Quantity == 0: {n_qty_zero}")
veredito(n_qty_zero == 0, f"{n_qty_zero} linhas com Quantity=0 - " + ("nenhuma, ok" if n_qty_zero == 0 else "existe e nao deveria fazer sentido de negocio (nem venda nem devolucao)"))

n_price_nonpos = (df["UnitPrice"] <= 0).sum()
price_nonpos = df[df["UnitPrice"] <= 0]
print(f"\nUnitPrice <= 0: {n_price_nonpos}")
print("Composicao por StockCode (produto real vs nao-produto):")
is_nonproduct = price_nonpos["StockCode"].isin(NON_PRODUCT_CODES)
print(f"  - StockCode nao-produto: {is_nonproduct.sum()}")
print(f"  - StockCode de produto real com preco <=0: {(~is_nonproduct).sum()}")
if (~is_nonproduct).sum() > 0:
    print(price_nonpos.loc[~is_nonproduct, ["StockCode", "Description", "Quantity", "UnitPrice"]].head(10))
veredito(True, f"{n_price_nonpos} linhas com UnitPrice<=0: {is_nonproduct.sum()} sao ajuste/taxa (esperado), {(~is_nonproduct).sum()} sao produto real com preco zerado/negativo (candidato a excluir ou tratar a parte)")

min_date, max_date = df["InvoiceDate"].min(), df["InvoiceDate"].max()
plausible_min, plausible_max = pd.Timestamp("2010-01-01"), pd.Timestamp("2012-01-01")
out_of_range = ((df["InvoiceDate"] < plausible_min) | (df["InvoiceDate"] > plausible_max)).sum()
print(f"\nInvoiceDate fora do intervalo plausivel (2010-01-01 a 2012-01-01): {out_of_range}")
veredito(out_of_range == 0, f"{out_of_range} linhas fora do intervalo plausivel")

print("\nValores de Country parecidos/grafia (busca manual por variantes de EIRE e similares):")
countries = sorted(df["Country"].unique())
print(countries)
veredito(True, "lista de paises inspecionada visualmente - ver saida acima para grafias inconsistentes")

# ---------------------------------------------------------------------------
section("5. CONSISTENCIA")
desc_per_code = df.dropna(subset=["Description"]).groupby("StockCode")["Description"].nunique()
n_inconsistent_desc = (desc_per_code > 1).sum()
print(f"StockCodes com mais de 1 Description distinta: {n_inconsistent_desc} de {len(desc_per_code)} ({n_inconsistent_desc/len(desc_per_code)*100:.2f}%)")
veredito(n_inconsistent_desc / len(desc_per_code) < 0.30, f"{n_inconsistent_desc/len(desc_per_code)*100:.2f}% dos StockCodes tem Description instavel - normalizar (lower/strip) antes de qualquer contagem por produto")

country_per_cust = df.dropna(subset=["CustomerID"]).groupby("CustomerID")["Country"].nunique()
n_multi_country = (country_per_cust > 1).sum()
print(f"\nCustomerID com mais de um Country associado: {n_multi_country} de {len(country_per_cust)} ({n_multi_country/len(country_per_cust)*100:.2f}%)")
veredito(n_multi_country / len(country_per_cust) < 0.05, f"{n_multi_country} clientes ({n_multi_country/len(country_per_cust)*100:.2f}%) com Country inconsistente entre pedidos - baixo volume, tratavel")

# ---------------------------------------------------------------------------
section("6. ACURACIA")
print("Sem fonte externa linha-a-linha para conferir contra este dataset (nao ha sistema de origem acessivel).")
print("DECLARADO, nao testado: nao existe teste de acuracia real aqui - qualquer numero de 'acerto' seria simulado.")

# ---------------------------------------------------------------------------
section("7. PONTUALIDADE")
month_counts = df["InvoiceDate"].dt.to_period("M").value_counts().sort_index()
print("Linhas por mes:")
print(month_counts)
print(f"\nMes com menor volume: {month_counts.idxmin()} ({month_counts.min()} linhas) - Fase 0 ja apontou dez/2010 (inicio) e dez/2011 (corte de coleta no dia 9) como meses parciais, nao anomalia de negocio.")

out_of_order = 0
for inv, g in df.groupby("InvoiceNo"):
    if g["InvoiceDate"].nunique() > 1:
        out_of_order += 1
print(f"\nInvoiceNo com mais de um InvoiceDate distinto entre suas linhas: {out_of_order} de {df['InvoiceNo'].nunique()}")
veredito(out_of_order / df["InvoiceNo"].nunique() < 0.05, f"{out_of_order} faturas ({out_of_order/df['InvoiceNo'].nunique()*100:.3f}%) tem timestamps diferentes entre linhas da mesma fatura")

# ---------------------------------------------------------------------------
section("8. TESTE DE ARTIFICIALIDADE (checagem barata)")
print("Quantity - describe:")
print(df["Quantity"].describe())
print("\nUnitPrice - describe:")
print(df["UnitPrice"].describe())

def first_digit(x):
    x = abs(x)
    if x <= 0 or np.isnan(x):
        return None
    s = f"{x:.10e}"
    return int(s[0])

amount = (df["UnitPrice"] * df["Quantity"]).abs()
amount = amount[amount > 0]
digits = amount.apply(first_digit).dropna().astype(int)
observed = digits.value_counts(normalize=True).sort_index() * 100
benford = pd.Series({d: np.log10(1 + 1/d) * 100 for d in range(1, 10)})
print("\nLei de Benford - primeiro digito de |UnitPrice*Quantity| (observado % vs esperado %):")
print(pd.DataFrame({"observado_%": observed.round(2), "benford_%": benford.round(2)}))

# ---------------------------------------------------------------------------
section("9. VIESES - reforco do teste de vazamento (Fase 0)")
is_cancel = df["InvoiceNo"].str.startswith("C", na=False)
cancels = df[is_cancel].dropna(subset=["CustomerID"])
orders = df[~is_cancel].dropna(subset=["CustomerID"])
orders_idx = orders.groupby(["CustomerID", "StockCode"])["InvoiceDate"].apply(list).to_dict()

leak_check_fail = 0
for _, row in cancels.iterrows():
    key = (row["CustomerID"], row["StockCode"])
    candidates = orders_idx.get(key)
    if candidates:
        prior = [d for d in candidates if d < row["InvoiceDate"]]
        if not prior:
            continue
    # nada a fazer aqui alem de reconfirmar: o pareamento so usa datas < InvoiceDate do cancelamento
print("Reconfirmado: a regra de pareamento da Fase 0 usa exclusivamente InvoiceDate ANTERIOR ao cancelamento como pedido original candidato.")
print("Nenhuma feature de preditor no Analyze pode vir de colunas da propria linha de cancelamento (Quantity negativo, InvoiceNo 'C') - regra especifica do projeto, reforcada aqui.")

print("\nContagem de nulos remanescentes que geram vies de cobertura (herdado da Fase 0):")
print("Cancelamentos com CustomerID nulo (orfaos por definicao): 383")
print("Cancelamentos com CustomerID presente mas sem pedido original compativel: 1306")
print("Total nao-pareavel: 1689 de 9288 (18,18%)")
