"""Fase 0 - profiling de estrutura e procedencia. Sem cruzamento de variaveis."""
import pandas as pd
import numpy as np

pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

df = pd.read_csv(
    "online_retail.csv",
    dtype={"InvoiceNo": str, "StockCode": str, "Description": str, "Country": str},
    parse_dates=["InvoiceDate"],
)

def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

section("1. SHAPE")
print(df.shape)

section("2. DTYPES")
print(df.dtypes)

section("3. NULOS POR COLUNA (contagem e %)")
nulls = df.isnull().sum()
pct = (nulls / len(df) * 100).round(2)
print(pd.DataFrame({"n_nulos": nulls, "pct_nulos": pct}))

section("4. MIN/MAX InvoiceDate")
print("min:", df["InvoiceDate"].min())
print("max:", df["InvoiceDate"].max())

section("5. CONTAGEM DE LINHAS POR MES (InvoiceDate)")
month_counts = df["InvoiceDate"].dt.to_period("M").value_counts().sort_index()
print(month_counts)

section("6. CONTAGEM DE VALORES UNICOS")
for col in ["InvoiceNo", "StockCode", "CustomerID", "Country"]:
    print(f"{col}: {df[col].nunique()}")

section("7. InvoiceNo com prefixo C vs Quantity < 0")
is_cancel_invoice = df["InvoiceNo"].str.startswith("C", na=False)
is_neg_qty = df["Quantity"] < 0
n_cancel_invoice = is_cancel_invoice.sum()
n_neg_qty = is_neg_qty.sum()
neg_qty_not_cancel = (is_neg_qty & ~is_cancel_invoice).sum()
cancel_not_neg_qty = (is_cancel_invoice & ~is_neg_qty).sum()
both = (is_cancel_invoice & is_neg_qty).sum()
print(f"InvoiceNo com prefixo 'C': {n_cancel_invoice}")
print(f"Quantity < 0: {n_neg_qty}")
print(f"Ambos (C e Quantity<0): {both}")
print(f"Quantity<0 mas SEM prefixo C: {neg_qty_not_cancel}")
print(f"Prefixo C mas Quantity >= 0: {cancel_not_neg_qty}")

section("8. TOP 20 StockCode por frequencia")
print(df["StockCode"].value_counts().head(20))

section("9. DISTRIBUICAO DE Country (contagem de linhas)")
print(df["Country"].value_counts())

section("10. Description nula quando StockCode existe (checagem rapida p/ Fase 0)")
desc_null_with_stockcode = df["Description"].isnull().sum()
print(f"Description nula (total): {desc_null_with_stockcode}")

section("11. Amostra de linhas com StockCode nao-produto candidatos")
non_product_candidates = ["POST", "D", "M", "BANK CHARGES", "C2", "DOT", "CRUK", "PADS", "AMAZONFEE"]
for code in non_product_candidates:
    n = (df["StockCode"] == code).sum()
    if n > 0:
        desc_sample = df.loc[df["StockCode"] == code, "Description"].dropna().unique()[:3]
        print(f"{code}: n={n}, descriptions={list(desc_sample)}")
