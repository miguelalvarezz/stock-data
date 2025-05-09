# apiManager/services/yfinance_service.py
import yfinance as yf
from typing import Dict, Optional, Any

class YFinanceService:
    def __init__(self):
        # Configuración inicial si es necesaria
        pass

    def get_fund_data(self, symbol: str) -> Dict[str, Any]:
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
            # Log del error
            return None

    def get_historical_prices(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Obtiene precios históricos del fondo
        """
        try:
            fund = yf.Ticker(symbol)
            hist = fund.history(period=timeframe)
            return {
                'dates': hist.index.tolist(),
                'prices': hist['Close'].tolist(),
                'volumes': hist['Volume'].tolist()
            }
        except Exception as e:
            # Log del error
            return None