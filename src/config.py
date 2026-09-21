"""Configuracao central do projeto - parametros que antes estavam hardcoded
espalhados pelos scripts das Fases 0-4. Qualquer mudanca aqui e uma mudanca de
decisao do projeto, nao um detalhe de implementacao - deve ser revisada como tal.
"""
import pandas as pd

# Decidido na Fase 0/2A - lista fechada de StockCodes que nao representam produto
NON_PRODUCT_CODES_BASE = ["POST", "DOT", "M", "C2", "D", "S", "BANK CHARGES", "CRUK", "B", "PADS"]
# gift_0001_* (vales-presente) sao detectados dinamicamente por prefixo, nao hardcoded aqui

def get_non_product_codes(stockcode_series):
    codes = list(NON_PRODUCT_CODES_BASE)
    codes += [c for c in stockcode_series.unique() if str(c).lower().startswith("gift_")]
    return codes

# Decidido no Define, Fase 1 - corte de holdout (InvoiceDate >= este valor fica trancado ate o Control)
HOLDOUT_START = pd.Timestamp("2011-10-01")

# Decidido na Measure 2B/2A - exclusao de linhas de produto real sem preco valido (ajuste de estoque)
MIN_UNIT_PRICE = 0.0  # UnitPrice deve ser estritamente > este valor para contar como pedido valido

# Decidido no Improve, Fase 4 - regra de sinalizacao de segmento de risco
RISK_SEGMENT_RATE_MULTIPLIER = 1.5   # sinaliza se taxa >= 1.5x a taxa geral
RISK_SEGMENT_MIN_N = 500             # e n >= 500

# Decidido no Define, Fase 1 - efeitos minimos praticos pre-registrados (docs/pre-registro-hipoteses.md)
EFEITO_MINIMO_H1_PP = 0.03   # 3 p.p., Quantity Q4 vs Q1
EFEITO_MINIMO_H2_PP = 0.05   # 5 p.p., UK vs Resto
EFEITO_MINIMO_H3_PP = 0.02   # 2 p.p., sazonalidade (exploratoria)
EFEITO_MINIMO_H4_RATIO = 2.0  # 2x a taxa media, StockCode

# Limiares de qualidade estruturais (Fase 2A) - usados como guarda em tests/test_data_quality.py
QUALIDADE_LIMITES = {
    "n_linhas_min": 400_000,
    "n_linhas_max": 700_000,
    "customerid_nulo_pct_min": 0.10,
    "customerid_nulo_pct_max": 0.40,
    "description_nulo_pct_max": 0.02,
    "duplicata_exata_pct_max": 0.05,
    "unitprice_nao_positivo_pct_max": 0.02,
}
