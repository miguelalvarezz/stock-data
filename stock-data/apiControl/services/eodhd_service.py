# apiManager/services/eodhd_service.py
import requests
from typing import Dict, Any
from django.conf import settings

class EODHDService:
    def __init__(self):
        self.api_key = settings.EODHD_API_KEY
        self.base_url = "https://eodhd.com/api"

    def getSearchData(self, query: str) -> Dict[str, Any]:
        """
        Búsqueda de fondos (backup)
        """
        try:
            url = f"{self.base_url}/search/{query}?api_token={self.api_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Convertimos la respuesta al mismo formato que YFinance
            formatted_results = []
            for item in data:
                formatted_item = {
                    'symbol': item.get('Code', ''),
                    'shortname': item.get('Name', ''),
                    'longname': item.get('Name', ''),
                    'exchange': item.get('Exchange', ''),
                    'type': item.get('Type', ''),
                    'score': item.get('Score', 0)
                }
                formatted_results.append(formatted_item)
            return {
                'quotes': formatted_results,
                'count': len(formatted_results)
            }
        except Exception as e:
            # Log del error
            return {'quotes': [], 'count': 0}
        
    def getCategorySector(self, symbol: str) -> Dict[str, Any]:
        # TODO: Implementar
        return None
    
    def compare_funds(self, symbol1: str, symbol2: str) -> Dict[str, Any]:
        """
        Comparación de fondos (backup)
        """
        try:
            url = f"{self.base_url}/compare/{symbol1},{symbol2}?api_token={self.api_key}"
            response = requests.get(url)
            response.raise_for_status()
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