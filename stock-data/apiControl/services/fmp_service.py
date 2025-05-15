# apiManager/services/fmp_service.py
import requests
from typing import Dict, List, Any
from django.conf import settings
from apiControl.exceptions.apiException import APIError

class FMPService:
    def __init__(self):
        self.api_key = settings.FMP_API_KEY
        self.base_url = "https://financialmodelingprep.com/api/v3"
    

    def getAnualVolatility(self, symbol: str) -> Dict[str, Any]:
        # TODO: Implementar
        return None
    

    def getCommissions(self, symbol: str) -> Dict[str, Any]:
        url = f"https://financialmodelingprep.com/api/v3/etf-info/{symbol}?apikey={self.api_key}"
    
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                fund_data = data[0]
                return {
                    'expense_ratio': fund_data.get('expenseRatio'),
                    'total_assets': fund_data.get('totalAssets'),
                    'ytd_return': fund_data.get('ytd'),
                    'inception_date': fund_data.get('inceptionDate'),
                    'fund_family': fund_data.get('fundFamily')
                }
            return None
        except Exception as e:
            print(f"Error al obtener comisiones: {e}")
            return None

    def getCategorySector(self, symbol: str) -> Dict[str, Any]:
        try:

            url = f"https://financialmodelingprep.com/api/v3/etf-info?symbol={symbol}&apikey={self.api_key}"
            response = requests.get(url)
            data = response.json()

            if not data or "category" not in data[0]:
                raise APIError("No se encontró categoría/sector en la respuesta de FMP")

            return {
                "symbol": symbol,
                "category": data[0]["category"]
            }

        except Exception as e:
            raise APIError(f"Error al obtener categoría/sector desde FMP: {e}")

    '''
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
    '''
    