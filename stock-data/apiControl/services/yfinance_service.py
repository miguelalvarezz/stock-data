# apiManager/services/yfinance_service.py
import yfinance as yf
import pandas as pd
from typing import Dict, Optional, Any, List
from datetime import datetime

class YFinanceService:
    def __init__(self):
        # Configuración inicial si es necesaria
        pass

    @staticmethod
    def getSearchData(symbol: str) -> List[Dict[str, Any]]:
        try:
            # Obtener datos usando yfinance
            fund = yf.Ticker(symbol)
            
            # Convertir la información a DataFrame
            info_df = pd.DataFrame([fund.info])
            
            # Definir las columnas que queremos y sus valores por defecto
            columns_mapping = {
                'symbol': 'symbol',
                'longName': 'name',
                'sector': 'sector',
                '52WeekChange': 'return1y',
                'expenseRatio': 'fees',
                'category': 'benchmark',
                'regularMarketPrice': 'price',
                'regularMarketChangePercent': 'change_percent',
                'regularMarketVolume': 'volume'
            }
            
            # Crear un DataFrame con las columnas que existen
            available_columns = [col for col in columns_mapping.keys() if col in info_df.columns]
            result_df = info_df[available_columns].copy()
            
            # Renombrar las columnas disponibles
            rename_dict = {col: columns_mapping[col] for col in available_columns}
            result_df = result_df.rename(columns=rename_dict)
            
            # Convertir a diccionario y limpiar valores nulos
            result = result_df.to_dict('records')[0]
            result = {k: v for k, v in result.items() if pd.notna(v)}
            
            print("Datos procesados con pandas:")
            print(pd.DataFrame([result]).to_string())
            
            return [result] if result else []
            
        except ValueError as ve:
            print(f"Error de validación: {str(ve)}")
            raise  # Re-lanzamos la excepción para manejarla en la vista
        except Exception as e:
            print(f"Error en búsqueda YFinance: {str(e)}")
            raise  # Re-lanzamos la excepción para manejarla en la vista

    @staticmethod
    def getHistoricalProfit(symbol: str) -> Optional[Dict[str, Any]]:
        print(f"[DEBUG] getHistoricalProfit llamado para: {symbol}")
        # Asignamos un timeframe por defecto (se probará con 10 y con 5 años)
        timeframes = ["10y", "5y"]

        for timeframe in timeframes:
            try:
                fund = yf.Ticker(symbol)
                hist = fund.history(period=timeframe)
                # print(f"[DEBUG] getHistoricalProfit: timeframe={timeframe}, datos={len(hist)} filas")
                # Verificar que tenemos datos
                if not hist.empty:
                    return {
                        'dates': hist.index.tolist(),
                        'prices': hist['Close'].tolist(),
                        'open': hist['Open'].tolist(),
                        'high': hist['High'].tolist(),
                        'low': hist['Low'].tolist(),
                        'close': hist['Close'].tolist(),
                        'volumes': hist['Volume'].tolist()
                    }
            except Exception as e:
                print(f"Error al obtener datos con timeframe {timeframe}: {str(e)}")
                continue
        print(f"No se pudieron obtener datos para {symbol} con ninguno de los timeframes: {timeframes}")
        return None
        
    @staticmethod
    def calculateAnnualReturns(historical_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[DEBUG] calculateAnnualReturns llamado")
        print(f"[DEBUG] calculateAnnualReturns recibió: {type(historical_data)}")
        if historical_data:
            print(f"[DEBUG] calculateAnnualReturns keys: {list(historical_data.keys()) if isinstance(historical_data, dict) else 'No es dict'}")
        try:
            if not historical_data or 'dates' not in historical_data or 'prices' not in historical_data:
                print("[DEBUG] calculateAnnualReturns: datos históricos vacíos o incompletos")
                return None
            
            # Crear DataFrame con los datos históricos
            df = pd.DataFrame({
                'date': pd.to_datetime(historical_data['dates']),
                'price': historical_data['prices']
            })
            
            # Ordenar por fecha
            df = df.sort_values('date')
            
            # Calcular rentabilidades anuales
            annual_returns = {}
            
            # Agrupar por año
            df['year'] = df['date'].dt.year
            years = df['year'].unique()
            
            for year in years:
                year_data = df[df['year'] == year]
                if len(year_data) > 0:
                    start_price = year_data.iloc[0]['price']
                    end_price = year_data.iloc[-1]['price']
                    
                    # Verificar que los precios son válidos
                    if start_price > 0 and end_price > 0:
                        annual_return = ((end_price / start_price) - 1) * 100
                        annual_returns[year] = {
                            'return': round(annual_return, 2),
                            'start_price': round(start_price, 2),
                            'end_price': round(end_price, 2),
                            'data_points': len(year_data)
                        }
                        print(f"[DEBUG] Año {year}: start={start_price}, end={end_price}, return={annual_returns[year]['return']}%")
            
            # Calcular CAGR de todo el período
            if len(df) >= 2:
                start_price = df.iloc[0]['price']
                end_price = df.iloc[-1]['price']
                
                if start_price > 0 and end_price > 0:
                    # Calcular años exactos entre el primer y último dato
                    days_between = (df.iloc[-1]['date'] - df.iloc[0]['date']).days
                    exact_years = days_between / 365.25
                    
                    if exact_years > 0:
                        cagr = ((end_price / start_price) ** (1/exact_years) - 1) * 100
                    else:
                        cagr = None
                else:
                    cagr = None
            else:
                cagr = None
            print(f"[DEBUG] CAGR calculado: {round(cagr,2) if cagr is not None else None}%")
            return {
                'annual_returns': annual_returns,
                'cagr': round(cagr, 2) if cagr is not None else None,
                'period_years': len(annual_returns),
                'total_data_points': len(df),
                'date_range': {
                    'start': df.iloc[0]['date'].strftime('%Y-%m-%d'),
                    'end': df.iloc[-1]['date'].strftime('%Y-%m-%d')
                }
            }
            
        except Exception as e:
            print(f"Error al calcular rentabilidades anuales: {str(e)}")
            return None
        
    @staticmethod
    def getAnualVolatility(symbol: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la volatilidad del fondo durante el último año
        """
        try:
            fund = yf.Ticker(symbol)
            
            # Obtener datos históricos del último año
            hist = fund.history(period="1y")
            
            if hist.empty:
                return None
            
            # Calcular retornos diarios
            hist['Returns'] = hist['Close'].pct_change()
            
            # Calcular volatilidad anual (desviación estándar de retornos * sqrt(252))
            # 252 es el número aproximado de días de trading en un año
            daily_volatility = hist['Returns'].std()
            annual_volatility = daily_volatility * (252 ** 0.5)
            
            # Convertir a porcentaje
            annual_volatility_percent = annual_volatility * 100
            
            return {
                'volatility': annual_volatility_percent,
                'daily_volatility': daily_volatility * 100,
                'period': '1y',
                'data_points': len(hist)
            }
            
        except Exception as e:
            print(f"Error al calcular volatilidad para {symbol}: {str(e)}")
            return None

    @staticmethod
    def getCategorySector(symbol: str) -> Optional[Dict[str, str]]:
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            '''
            # Determinar si es ETF o acción
            #is_etf = info.get('quoteType', '').lower() == 'etf'
            category = info.get('category')
            industry = info.get('industry')
            
            # Usar category si existe, sino usar industry
            classification = category if category else industry

            
            result = {
                'symbol': symbol,
                'type': 'ETF' if is_etf else 'Stock',
                'sector': classification,
                #'long_name': info.get('longName', ''),
                #'sector': info.get('sector'),
                #'industry': info.get('industry'),
                #'fund_family': info.get('fundFamily'),
                #'category': info.get('category'),
                #'summary': info.get('longBusinessSummary', '')[:200] + '...'  # Resumen recortado
            }
            
            # Limpieza de valores None
            result = {k: v for k, v in result.items() if v is not None}

            return result if result else None
            '''
            
            info_df = pd.DataFrame([info])
            # Intentar obtener category primero, si no existe o es nulo, usar industry
            classification = info_df['category'].iloc[0] if 'category' in info_df.columns and pd.notna(info_df['category'].iloc[0]) else info_df['industry'].iloc[0]
            
            return classification if pd.notna(classification) else None
            
        except Exception as e:
            print(f"Error al obtener categoría para {symbol}: {str(e)}")
            return None

    @staticmethod
    def getMarketCap(symbol: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la capitalización de mercado del fondo/empresa
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            market_cap = info.get('marketCap')
            
            if market_cap is None:
                return None
            
            # Formatear el market cap para mejor legibilidad
            if market_cap >= 1e12:  # Trillones
                formatted_cap = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:  # Billones
                formatted_cap = f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:  # Millones
                formatted_cap = f"${market_cap/1e6:.2f}M"
            else:
                formatted_cap = f"${market_cap:,.0f}"
            
            return {
                'market_cap': market_cap,
                'formatted_market_cap': formatted_cap,
                'symbol': symbol
            }
            
        except Exception as e:
            print(f"Error al obtener market cap para {symbol}: {str(e)}")
            return None