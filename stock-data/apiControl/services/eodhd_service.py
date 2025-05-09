# apiManager/services/eodhd_service.py
import requests
from typing import Dict, Any
from django.conf import settings

class EODHDService:
    def __init__(self):
        self.api_key = settings.EODHD_API_KEY
        self.base_url = "https://eodhd.com/api"

    def search_funds(self, query: str) -> Dict[str, Any]:
        """
        Búsqueda de fondos (backup)
        """
        try:
            url = f"{self.base_url}/search/{query}?api_token={self.api_key}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Log del error
            return {}

    def get_detailed_fees(self, symbol: str) -> Dict[str, Any]:
        """
        Obtiene comisiones detalladas
        """
        try:
            url = f"{self.base_url}/fund/{symbol}?api_token={self.api_key}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Log del error
            return {}