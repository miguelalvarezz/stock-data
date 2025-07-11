import yfinance as yf
import pandas as pd
from apiControl.control import perform_api_call
from apiControl.exceptions.apiException import APIError
# LOS DATOS A MOSTRAR SON:
# - Rentabilidad HISTORICA 10 AÑOS, 5 AÑOS O 3  -> yfinance y av o eodhd como backup
# - Volatilidad anual -> yfinance y fmp backup
# - Comisiones y gastos -> fmp
# - Categoria/sector -> fmp o av y eodhd como backup
# - rating calificacion -> intentar con yfinance o crear un ranking propio basado en rentabilidad/riesgo

def calculate_fund_rating(data):

    rentabilidad = data.get("historicalProfit")
    volatilidad = data.get("anualVolatility")

    if rentabilidad is None or volatilidad is None:
        return "☆☆☆☆☆"
        #raise APIError("No se puede calcular rating sin rentabilidad y volatilidad")
        

    # mayor rentabilidad y menor riesgo = mejor rating
    score = (rentabilidad / volatilidad) * 100

    if score > 120:
        return "★★★★★"
    elif score > 100:
        return "★★★★☆"
    elif score > 80:
        return "★★★☆☆"
    elif score > 60:
        return "★★☆☆☆"
    elif score > 40:
        return "★☆☆☆☆"
    else:
        return "☆☆☆☆☆"
    

def compare_fund(symbol1, symbol2):
    """
    Comparación de fondos: devuelve tabla, series de precios y rentabilidad, y crecimiento del último año
    """
    print(f"[DEBUG] Iniciando comparación de {symbol1} vs {symbol2}")
    data1 = {}
    data2 = {}
    error = {}
    # Series para graficar
    price_series = {}
    profit_series = {}
    growth_last_year = {}
    growth_5y_avg = {}

    # Rentabilidad historica (serie de precios)
    try:
        print(f"[DEBUG] Obteniendo rentabilidad histórica para {symbol1}")
        hist1 = perform_api_call("compare", symbol1, "historicalProfit")
        print(f"[DEBUG] Obteniendo rentabilidad histórica para {symbol2}")
        hist2 = perform_api_call("compare", symbol2, "historicalProfit")
        if hist1 and 'dates' in hist1 and 'prices' in hist1:
            df1 = pd.DataFrame({
                'Fecha': pd.to_datetime(hist1['dates']),
                'Precio': hist1['prices']
            }).sort_values('Fecha')
            df1['Fecha'] = df1['Fecha'].dt.tz_localize(None)
            price_series[symbol1] = {
                'dates': df1['Fecha'].dt.strftime('%Y-%m-%d').tolist(),
                'prices': df1['Precio'].tolist(),
            }
            # Rentabilidad acumulada (desde el primer valor)
            base = df1['Precio'].iloc[0]
            df1['Rentabilidad'] = (df1['Precio'] / base - 1) * 100
            profit_series[symbol1] = {
                'dates': df1['Fecha'].dt.strftime('%Y-%m-%d').tolist(),
                'profit': df1['Rentabilidad'].tolist(),
            }
            # Crecimiento último año
            now = pd.Timestamp.now()
            one_year_ago = now - pd.DateOffset(years=1)
            df1['diff'] = (df1['Fecha'] - one_year_ago).abs()
            row_last_year = df1.loc[df1['diff'].idxmin()]
            price_last_year = row_last_year['Precio']
            price_now = df1.iloc[-1]['Precio']
            if price_last_year != 0:
                growth_last_year[symbol1] = ((price_now / price_last_year)-1) * 100
            else:
                growth_last_year[symbol1] = None
            # Crecimiento medio anual 5 años (CAGR)
            five_years_ago = now - pd.DateOffset(years=5)
            df1['diff_5y'] = (df1['Fecha'] - five_years_ago).abs()
            row_5y_ago = df1.loc[df1['diff_5y'].idxmin()]
            price_5y_ago = row_5y_ago['Precio']
            if price_5y_ago != 0 and len(df1) > 1:
                n_years = (df1.iloc[-1]['Fecha'] - row_5y_ago['Fecha']).days / 365.25
                if n_years > 0:
                    growth_5y_avg[symbol1] = ((price_now / price_5y_ago) ** (1/n_years) - 1) * 100
                else:
                    growth_5y_avg[symbol1] = None
            else:
                growth_5y_avg[symbol1] = None
        if hist2 and 'dates' in hist2 and 'prices' in hist2:
            df2 = pd.DataFrame({
                'Fecha': pd.to_datetime(hist2['dates']),
                'Precio': hist2['prices']
            }).sort_values('Fecha')
            df2['Fecha'] = df2['Fecha'].dt.tz_localize(None)
            price_series[symbol2] = {
                'dates': df2['Fecha'].dt.strftime('%Y-%m-%d').tolist(),
                'prices': df2['Precio'].tolist(),
            }
            base = df2['Precio'].iloc[0]
            df2['Rentabilidad'] = (df2['Precio'] / base - 1) * 100
            profit_series[symbol2] = {
                'dates': df2['Fecha'].dt.strftime('%Y-%m-%d').tolist(),
                'profit': df2['Rentabilidad'].tolist(),
            }
            now = pd.Timestamp.now()
            one_year_ago = now - pd.DateOffset(years=1)
            df2['diff'] = (df2['Fecha'] - one_year_ago).abs()
            row_last_year = df2.loc[df2['diff'].idxmin()]
            price_last_year = row_last_year['Precio']
            price_now = df2.iloc[-1]['Precio']
            if price_last_year != 0:
                growth_last_year[symbol2] = ((price_now / price_last_year)-1) * 100
            else:
                growth_last_year[symbol2] = None
            # Crecimiento medio anual 5 años (CAGR)
            five_years_ago = now - pd.DateOffset(years=5)
            df2['diff_5y'] = (df2['Fecha'] - five_years_ago).abs()
            row_5y_ago = df2.loc[df2['diff_5y'].idxmin()]
            price_5y_ago = row_5y_ago['Precio']
            if price_5y_ago != 0 and len(df2) > 1:
                n_years = (df2.iloc[-1]['Fecha'] - row_5y_ago['Fecha']).days / 365.25
                if n_years > 0:
                    growth_5y_avg[symbol2] = ((price_now / price_5y_ago) ** (1/n_years) - 1) * 100
                else:
                    growth_5y_avg[symbol2] = None
            else:
                growth_5y_avg[symbol2] = None
        data1['historicalProfit'] = hist1
        data2['historicalProfit'] = hist2
    except APIError as e:
        print(f"[ERROR] Error en rentabilidad histórica: {str(e)}")
        error["historicalProfit"] = str(e)

    # Volatilidad anual
    try:
        print(f"[DEBUG] Obteniendo volatilidad anual para {symbol1}")
        data1["anualVolatility"] = perform_api_call("compare", symbol1, "anualVolatility")
        print(f"[DEBUG] Obteniendo volatilidad anual para {symbol2}")
        data2["anualVolatility"] = perform_api_call("compare", symbol2, "anualVolatility")
    except APIError as e:
        print(f"[ERROR] Error en volatilidad anual: {str(e)}")
        error["anualVolatility"] = str(e)

    # Comisiones y gastos
    try:
        print(f"[DEBUG] Obteniendo comisiones para {symbol1}")
        data1["commissions"] = perform_api_call("compare", symbol1, "commissions")
        print(f"[DEBUG] Obteniendo comisiones para {symbol2}")
        data2["commissions"] = perform_api_call("compare", symbol2, "commissions")
    except APIError as e:
        print(f"[ERROR] Error en comisiones: {str(e)}")
        error["commissions"] = str(e)

    # Categoria/sector
    try:
        print(f"[DEBUG] Obteniendo categoría/sector para {symbol1}")
        data1["categorySector"] = perform_api_call("compare", symbol1, "categorySector")
        print(f"[DEBUG] Obteniendo categoría/sector para {symbol2}")
        data2["categorySector"] = perform_api_call("compare", symbol2, "categorySector")
    except APIError as e:
        print(f"[ERROR] Error en categoría/sector: {str(e)}")
        error["categorySector"] = str(e)

    # Rating/calificación -> Calculo basado en rentabilidad/riesgo
    try:
        print(f"[DEBUG] Calculando rating para {symbol1}")
        data1['rating'] = calculate_fund_rating(data1)
        print(f"[DEBUG] Calculando rating para {symbol2}")
        data2['rating'] = calculate_fund_rating(data2)
    except Exception as e:
        print(f"[ERROR] Error en cálculo de rating: {str(e)}")
        error["rating"] = str(e)
        data1['rating'] = None
        data2['rating'] = None

    print(f"[DEBUG] Datos finales para {symbol1}: {data1}")
    print(f"[DEBUG] Datos finales para {symbol2}: {data2}")
    print(f"[DEBUG] Errores encontrados: {error}")

    # Crear DataFrame con los resultados
    df = pd.DataFrame([data1, data2], index=[symbol1, symbol2])
    if 'historicalProfit' in df.columns:
        df = df.drop(columns=['historicalProfit'])
    df.fillna("N/A", inplace=True)
    print(f"[DEBUG] DataFrame final:\n{df}")
    return df, price_series, profit_series, growth_last_year, growth_5y_avg
