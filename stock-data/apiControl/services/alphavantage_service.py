# apiManager/services/alpha_vantage_service.py
import requests
from typing import Dict, Any
from django.conf import settings

class AlphaVantageService:
    def __init__(self):
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        

    def getHistoricalProfit(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Obtiene datos históricos (backup de YFinance)
        """
        try:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.api_key
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Log del error
            return {}
        