# apiManager/services/fmp_service.py
import requests
from typing import Dict, List, Any
from django.conf import settings

class FMPService:
    def __init__(self):
        self.api_key = settings.FMP_API_KEY
        self.base_url = "https://financialmodelingprep.com/api/v3"

    def search_funds(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca fondos por nombre o símbolo
        """
        try:
            url = f"{self.base_url}/search?query={query}&apikey={self.api_key}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Log del error
            return []

    def get_risk_ratios(self, symbol: str) -> Dict[str, Any]:
        """
        Obtiene ratios de riesgo del fondo
        """
        try:
            url = f"{self.base_url}/ratios/{symbol}?apikey={self.api_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and data:
                return data[0]  # Tomar el más reciente
            elif isinstance(data, dict):
                return data
            else:
                return {}
        except Exception as e:
            # Log del error
            return {}