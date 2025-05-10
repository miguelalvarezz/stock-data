import yfinance as yf
import pandas as pd
from searchFund.utils import search_fund_data

# API FMP (financial modeling prep) -> ratios de riesgo  y rentabilidad anual
# API EODHD -> comisiones detalladas, dividendos y rendimientos
# API Alpha Vantage -> precios historicos (backup si falla yf) e informacion volatilidad



def compare_funds_data(f1, f2):
    d1 = search_fund_data(f1)
    d2 = search_fund_data(f2)
    if not d1 or not d2:
        return pd.DataFrame()
    d1['volatility'] = 0.1  # Simulado
    d2['volatility'] = 0.2
    df = pd.DataFrame([d1, d2], index=[f1, f2])
    df.fillna("N/A", inplace=True)
    return df