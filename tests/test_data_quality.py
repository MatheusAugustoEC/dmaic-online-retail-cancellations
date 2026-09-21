"""Converte a auditoria da Fase 2A em testes automaticos. Rodar com: pytest tests/
Objetivo: falhar se um novo lote de dados mudar de forma, dominio ou volume de
forma que invalidaria as decisoes tomadas nas Fases 0-4 (ver Control, Parte B).
Nao repete o teste de causa (isso e Analyze) - so estrutura e qualidade.
"""
import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from config import get_non_product_codes, QUALIDADE_LIMITES, HOLDOUT_START

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "online_retail.csv")

REQUIRED_COLUMNS = ["InvoiceNo", "StockCode", "Description", "Quantity",
                    "InvoiceDate", "UnitPrice", "CustomerID", "Country"]


@pytest.fixture(scope="module")
def df():
    return pd.read_csv(
        DATA_PATH,
        dtype={"InvoiceNo": str, "StockCode": str, "Description": str, "Country": str},
        parse_dates=["InvoiceDate"],
    )


def test_colunas_esperadas_presentes(df):
    faltando = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    assert not faltando, f"Colunas ausentes: {faltando} - schema do dado mudou, revisar todo o pipeline antes de prosseguir"


def test_volume_de_linhas_dentro_do_esperado(df):
    n = len(df)
    lim = QUALIDADE_LIMITES
    assert lim["n_linhas_min"] <= n <= lim["n_linhas_max"], (
        f"Volume de linhas ({n}) fora da faixa esperada [{lim['n_linhas_min']}, {lim['n_linhas_max']}] - "
        f"baseline congelado na 2B pode nao ser mais comparavel"
    )


def test_quantity_nunca_zero(df):
    n_zero = (df["Quantity"] == 0).sum()
    assert n_zero == 0, f"{n_zero} linhas com Quantity=0 - Fase 2A esperava 0, investigar antes de prosseguir"


def test_invoicedate_sem_valores_futuros_absurdos(df):
    assert df["InvoiceDate"].max() < pd.Timestamp.now(), "InvoiceDate no futuro - erro de parsing ou de origem"


def test_completude_customerid_dentro_da_faixa_historica(df):
    pct_nulo = df["CustomerID"].isnull().mean()
    lim = QUALIDADE_LIMITES
    assert lim["customerid_nulo_pct_min"] <= pct_nulo <= lim["customerid_nulo_pct_max"], (
        f"CustomerID nulo em {pct_nulo*100:.1f}% - fora da faixa historica "
        f"[{lim['customerid_nulo_pct_min']*100:.0f}%, {lim['customerid_nulo_pct_max']*100:.0f}%] observada na 2A. "
        f"Se caiu muito, a taxa de pareamento pode ter mudado - revalidar Fase 0 item 3 antes de recongelar baseline."
    )


def test_completude_description_dentro_do_esperado(df):
    pct_nulo = df["Description"].isnull().mean()
    assert pct_nulo <= QUALIDADE_LIMITES["description_nulo_pct_max"], (
        f"Description nula em {pct_nulo*100:.2f}% - acima do limite historico de "
        f"{QUALIDADE_LIMITES['description_nulo_pct_max']*100:.0f}%"
    )


def test_duplicatas_exatas_dentro_do_esperado(df):
    pct_dup = df.duplicated(keep=False).mean()
    assert pct_dup <= QUALIDADE_LIMITES["duplicata_exata_pct_max"], (
        f"{pct_dup*100:.2f}% de linhas duplicadas exatas - acima do limite historico de "
        f"{QUALIDADE_LIMITES['duplicata_exata_pct_max']*100:.0f}%, revisar antes de contar como pedido valido"
    )


def test_stockcodes_nao_produto_ainda_cobrem_o_esperado(df):
    non_product = get_non_product_codes(df["StockCode"])
    faltando = [c for c in ["POST", "M", "D", "BANK CHARGES"] if c not in df["StockCode"].unique()]
    assert not faltando, (
        f"Codigos nao-produto esperados sumiram do dado: {faltando} - pode indicar mudanca de "
        f"plataforma/processo de checkout (ver Control Parte A, item 3, condicao de invalidacao)"
    )


def test_unitprice_nao_positivo_em_produto_real_dentro_do_esperado(df):
    non_product = get_non_product_codes(df["StockCode"])
    real_product = ~df["StockCode"].isin(non_product)
    pct = (df.loc[real_product, "UnitPrice"] <= 0).mean()
    assert pct <= QUALIDADE_LIMITES["unitprice_nao_positivo_pct_max"], (
        f"{pct*100:.2f}% das linhas de produto real tem UnitPrice<=0 - acima do limite historico de "
        f"{QUALIDADE_LIMITES['unitprice_nao_positivo_pct_max']*100:.0f}%, revisar filtro do baseline (Measure 2B, secao 0)"
    )


def test_taxa_de_cancelamento_c_consistente_com_quantity_negativo(df):
    is_c = df["InvoiceNo"].str.startswith("C", na=False)
    is_neg = df["Quantity"] < 0
    inconsistentes = (is_c & ~is_neg).sum()
    assert inconsistentes == 0, (
        f"{inconsistentes} InvoiceNo com prefixo 'C' e Quantity>=0 - viola a premissa usada em todo o "
        f"pipeline (Fase 0: 100% dos 'C' tinham Quantity<0)"
    )


def test_holdout_ainda_e_o_intervalo_mais_recente(df):
    assert df["InvoiceDate"].max() >= HOLDOUT_START, (
        "Data maxima do dado ficou abaixo do corte de holdout configurado - o holdout precisa ser "
        "redefinido (config.py) antes de qualquer nova rodada de Control"
    )
