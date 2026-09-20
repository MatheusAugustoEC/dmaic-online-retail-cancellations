"""Fase 0 - item 2 (linha do tempo) e item 3 (teste de pareamento cancelamento<->pedido original)."""
import pandas as pd
import numpy as np

df = pd.read_csv(
    "online_retail.csv",
    dtype={"InvoiceNo": str, "StockCode": str, "Description": str, "Country": str},
    parse_dates=["InvoiceDate"],
)

def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

is_cancel = df["InvoiceNo"].str.startswith("C", na=False)
cancels = df[is_cancel].copy()
orders = df[~is_cancel].copy()

section("2a. Description varia dentro do mesmo StockCode?")
desc_per_code = df.dropna(subset=["Description"]).groupby("StockCode")["Description"].nunique()
print("StockCodes com mais de 1 Description distinta:", (desc_per_code > 1).sum(), "de", len(desc_per_code))
print(desc_per_code[desc_per_code > 1].sort_values(ascending=False).head(10))

section("2b. UnitPrice varia entre faturas para o mesmo StockCode?")
price_stats = df.groupby("StockCode")["UnitPrice"].agg(["nunique", "min", "max", "std"])
print("StockCodes com mais de 1 UnitPrice distinto:", (price_stats["nunique"] > 1).sum(), "de", len(price_stats))
print(price_stats.sort_values("std", ascending=False).head(10))

section("3. TESTE DE PAREAMENTO cancelamento <-> pedido original (CustomerID + StockCode + data anterior mais proxima)")

cancels_valid_cust = cancels.dropna(subset=["CustomerID"]).copy()
orders_valid_cust = orders.dropna(subset=["CustomerID"]).copy()

print(f"Total linhas de cancelamento: {len(cancels)}")
print(f"Cancelamentos com CustomerID nulo (ja orfaos, sem tentativa de pareamento): {cancels['CustomerID'].isnull().sum()}")
print(f"Cancelamentos com CustomerID presente (candidatos a pareamento): {len(cancels_valid_cust)}")

orders_idx = orders_valid_cust.groupby(["CustomerID", "StockCode"])["InvoiceDate"].apply(list).to_dict()

matched = 0
orphan_no_prior_order = 0

for _, row in cancels_valid_cust.iterrows():
    key = (row["CustomerID"], row["StockCode"])
    candidate_dates = orders_idx.get(key)
    if candidate_dates:
        prior_dates = [d for d in candidate_dates if d < row["InvoiceDate"]]
        if prior_dates:
            matched += 1
        else:
            orphan_no_prior_order += 1
    else:
        orphan_no_prior_order += 1

total_cancel_lines = len(cancels)
orphan_null_customer = cancels["CustomerID"].isnull().sum()

print(f"\nPareados (existe pedido original do mesmo CustomerID+StockCode ANTES da data do cancelamento): {matched}")
print(f"Orfaos (CustomerID presente, mas nenhum pedido original compativel antes): {orphan_no_prior_order}")
print(f"Orfaos (CustomerID nulo, pareamento impossivel por definicao): {orphan_null_customer}")
print(f"\nTaxa de pareamento sobre TOTAL de linhas de cancelamento: {matched/total_cancel_lines*100:.2f}%")
print(f"Taxa de pareamento sobre cancelamentos COM CustomerID: {matched/len(cancels_valid_cust)*100:.2f}%")

section("3b. Casos de data igual/anterior (cancelamento com timestamp <= pedido candidato mais proximo, ja excluido do match)")
same_or_before = 0
for _, row in cancels_valid_cust.iterrows():
    key = (row["CustomerID"], row["StockCode"])
    candidate_dates = orders_idx.get(key)
    if candidate_dates:
        same_or_after_cancel = [d for d in candidate_dates if d >= row["InvoiceDate"]]
        if same_or_after_cancel and not [d for d in candidate_dates if d < row["InvoiceDate"]]:
            same_or_before += 1
print(f"Cancelamentos cujo(s) unico(s) candidato(s) por chave tem InvoiceDate >= data do cancelamento (nao pareavel por ordem temporal): {same_or_before}")

section("4. CustomerID nulo: concentra em algum Country ou periodo?")
null_cust = df[df["CustomerID"].isnull()]
print("Distribuicao por Country (top 10) das linhas com CustomerID nulo:")
print(null_cust["Country"].value_counts().head(10))
print("\nDistribuicao por mes das linhas com CustomerID nulo:")
print(null_cust["InvoiceDate"].dt.to_period("M").value_counts().sort_index())
