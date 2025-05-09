import yfinance as yf

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
