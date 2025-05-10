import yfinance as yf
import pandas as pd
import requests


def search_fund_data(symbol):
    try:
        fund = yf.Ticker(symbol)
        info = fund.info

        # LOGICA CALCULO RENTABILIDAD ANUAL DURANTE 10 AÑOS
        symbol = info.get('symbol')
        years = 10

        # API Alpha Vantage -> precios historicos (backup si falla yf) e informacion volatilidad
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={symbol}&apikey=TSZP1J022SY5DL5D'
        response = requests.get(url)
        data = response.json()

        if 'Monthly Adjusted Time Series' not in data:
            print("Error al obtener datos. Verifica el símbolo o tu clave API.")
            exit()

        # === 2. CONVERTIR A DATAFRAME ===
        monthly_data = data['Monthly Adjusted Time Series']
        df = pd.DataFrame.from_dict(monthly_data, orient='index')
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        df = df[['5. adjusted close']].astype(float)
        df.rename(columns={'5. adjusted close': 'Adj Close'}, inplace=True)

        # === 3. FILTRAR FECHAS ===
        end_date = df.index.max()
        start_date = end_date.replace(year=end_date.year - years)

        # Asegurarse de que haya datos en el mes exacto
        if start_date not in df.index:
            # Buscar el primer mes disponible después de la fecha objetivo
            start_date = df[df.index >= start_date].index[0]

        start_price = df.loc[start_date, 'Adj Close']
        end_price = df.loc[end_date, 'Adj Close']

        # === 4. CALCULAR CAGR ===
        cagr = (end_price / start_price) ** (1 / years) - 1








        return {
            'symbol': info.get('symbol'),
            'name': info.get('longName'),
            'sector': info.get('sector'),
            #'return1y': info.get('52WeekChange'),
            'return1y': cagr * 100,
            'fees': info.get('annualReportExpenseRatio'),
            'benchmark': info.get('category'),
        }
    except:
        return None
