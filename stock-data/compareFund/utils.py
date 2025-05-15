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
        raise APIError("No se puede calcular rating sin rentabilidad y volatilidad")

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
        Funcionalidad 2: Comparación de fondos        
        """
        print(f"[DEBUG] Iniciando comparación de {symbol1} vs {symbol2}")
        data1 = {}
        data2 = {}
        error = {}

        # Rentabilidad historica
        try:
            print(f"[DEBUG] Obteniendo rentabilidad histórica para {symbol1}")
            data1["historicalProfit"] = perform_api_call("compare", symbol1, "historicalProfit")
            print(f"[DEBUG] Obteniendo rentabilidad histórica para {symbol2}")
            data2["historicalProfit"] = perform_api_call("compare", symbol2, "historicalProfit")
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
        df.fillna("N/A", inplace=True)
        
        print(f"[DEBUG] DataFrame final:\n{df}")
        return df
