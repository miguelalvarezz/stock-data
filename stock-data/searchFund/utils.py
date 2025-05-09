import yfinance as yf

# API FMP (financial modeling prep) -> ratios de riesgo  y rentabilidad anual
# API EODHD -> comisiones detalladas, dividendos y rendimientos
# API Alpha Vantage -> precios historicos (backup si falla yf) e informacion volatilidad


def search_fund_data(symbol):
    try:
        fund = yf.Ticker(symbol)
        info = fund.info
        return {
            'symbol': info.get('symbol'),
            'name': info.get('longName'),
            'sector': info.get('sector'),
            'return1y': info.get('52WeekChange'),
            'fees': info.get('annualReportExpenseRatio'),
            'benchmark': info.get('category'),
        }
    except:
        return None
