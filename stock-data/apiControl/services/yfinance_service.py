# apiManager/services/yfinance_service.py
import yfinance as yf
import pandas as pd
from typing import Dict, Optional, Any, List

class YFinanceService:
    def __init__(self):
        # Configuración inicial si es necesaria
        pass
    

    def getSearchData(symbol: str) -> List[Dict[str, Any]]:
        try:
            # Obtener datos usando yfinance
            fund = yf.Ticker(symbol)
            
            # Verificar si el símbolo existe
            if not fund.info or not fund.info.get('symbol'):
                raise ValueError(f"No se encontró el fondo con símbolo: {symbol}")
            
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



    '''
    def getSearchData(symbol: str) -> Dict[str, Any]:
        # Obtiene datos básicos del fondo (PREESTABLECIDOS POR NOSOTROS)

        try:
            fund = yf.Ticker(symbol)            
            info = fund.info
            return {
                'symbol': info.get('symbol'),
                'name': info.get('longName'),
                'sector': info.get('sector'),
                'return1y': info.get('52WeekChange'),
                'fees': info.get('expenseRatio'),
                'benchmark': info.get('category'),
                'price': info.get('regularMarketPrice'),
                'change_percent': info.get('regularMarketChangePercent'),
                'volume': info.get('regularMarketVolume'),
            }

        except Exception as e:
            print(f"Error en búsqueda YFinance {str(e)}")
            return None
    '''

    def getHistoricalProfit(symbol: str) -> Dict[str, Any]:
        """
        Obtiene precios históricos del fondo
        """
        # Asignamos un timeframe por defecto (se probará con 10 y con 5 años)
        timeframes = ["10y", "5y"]

        for timeframe in timeframes:
            try:
                fund = yf.Ticker(symbol)
                hist = fund.history(period=timeframe)
                
                # Verificar que tenemos datos
                if not hist.empty:
                    return {
                        'dates': hist.index.tolist(),
                        'prices': hist['Close'].tolist(),
                        'volumes': hist['Volume'].tolist()
                    }
                    
            except Exception as e:
                print(f"Error al obtener datos con timeframe {timeframe}: {str(e)}")
                continue
    
        # Si llegamos aquí, ambos timeframes fallaron
        print(f"No se pudieron obtener datos para {symbol} con ninguno de los timeframes: {timeframes}")
        return None
        
    def getAnualVolatility(symbol: str) -> Dict[str, Any]:
        """
        Obtiene la volatilidad anual del fondo
        """
        try:
            fund = yf.Ticker(symbol)
            return fund.info.get('annualVolatility')
        except Exception as e:
            # Log del error
            return None

    def getCategorySector(symbol: str) -> Optional[Dict[str, str]]:
        """
        Obtiene información de categoría y sector de un fondo o acción usando yfinance
        
        Args:
            symbol: Símbolo del activo (ej. 'VOO' para ETF o 'AAPL' para acción)
            
        Returns:
            Diccionario con:
            - 'category': Categoría del fondo (si es ETF)
            - 'sector': Sector principal (si es acción)
            - 'industry': Industria específica
            - 'fund_family': Familia de fondos (para ETFs)
            - 'type': Tipo de activo ('ETF' o 'Stock')
            None si hay error o no se encuentra el símbolo
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Determinar si es ETF o acción
            is_etf = info.get('quoteType', '').lower() == 'etf'
            
            result = {
                'symbol': symbol,
                'type': 'ETF' if is_etf else 'Stock',
                'long_name': info.get('longName', ''),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'fund_family': info.get('fundFamily'),
                'category': info.get('category'),
                'summary': info.get('longBusinessSummary', '')[:200] + '...'  # Resumen recortado
            }
            
            # Limpieza de valores None
            result = {k: v for k, v in result.items() if v is not None}
            
            return result if result else None
            
        except Exception as e:
            print(f"Error al obtener categoría para {symbol}: {str(e)}")
            return None