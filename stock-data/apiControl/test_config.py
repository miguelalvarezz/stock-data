"""
Configuración para tests de apiControl

Este archivo contiene configuraciones y utilidades para los tests
"""

import os
from unittest.mock import patch, MagicMock
from django.test import TestCase

# Configuración de variables de entorno para tests
os.environ.setdefault('FMP_API_KEY', 'test_fmp_key')
os.environ.setdefault('EODHD_API_KEY', 'test_eodhd_key')
os.environ.setdefault('ALPHAVANTAGE_API_KEY', 'test_alphavantage_key')


class MockAPITestCase(TestCase):
    """Clase base para tests que necesitan mocks de APIs"""
    
    def setUp(self):
        """Configuración inicial para todos los tests"""
        super().setUp()
        
        # Configurar mocks globales para APIs externas
        self.yfinance_patcher = patch('apiControl.services.yfinance_service.yf.Ticker')
        self.requests_patcher = patch('apiControl.services.fmp_service.requests.get')
        self.eodhd_requests_patcher = patch('apiControl.services.eodhd_service.requests.get')
        
        self.mock_yfinance = self.yfinance_patcher.start()
        self.mock_requests = self.requests_patcher.start()
        self.mock_eodhd_requests = self.eodhd_requests_patcher.start()
    
    def tearDown(self):
        """Limpieza después de cada test"""
        self.yfinance_patcher.stop()
        self.requests_patcher.stop()
        self.eodhd_requests_patcher.stop()
        super().tearDown()
    
    def setup_yfinance_mock(self, symbol, info_data=None, history_data=None):
        """Configurar mock de YFinance para un símbolo específico"""
        mock_ticker = MagicMock()
        
        if info_data is not None:
            mock_ticker.info = info_data
        
        if history_data is not None:
            mock_ticker.history.return_value = history_data
        
        self.mock_yfinance.return_value = mock_ticker
        return mock_ticker
    
    def setup_fmp_mock(self, response_data, status_code=200):
        """Configurar mock de FMP para respuestas específicas"""
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = status_code
        
        self.mock_requests.return_value = mock_response
        return mock_response
    
    def setup_eodhd_mock(self, response_data, status_code=200):
        """Configurar mock de EODHD para respuestas específicas"""
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = status_code
        
        self.mock_eodhd_requests.return_value = mock_response
        return mock_response


# Datos de ejemplo para tests
SAMPLE_YFINANCE_INFO = {
    'symbol': 'AAPL',
    'longName': 'Apple Inc.',
    'sector': 'Technology',
    '52WeekChange': 0.15,
    'expenseRatio': 0.02,
    'category': 'Technology',
    'regularMarketPrice': 150.0,
    'regularMarketChangePercent': 0.05,
    'regularMarketVolume': 1000000
}

SAMPLE_FMP_RESPONSE = [{
    'expenseRatio': 0.02,
    'totalAssets': 1000000000,
    'ytd': 0.15,
    'inceptionDate': '2020-01-01',
    'fundFamily': 'Vanguard',
    'category': 'Technology'
}]

SAMPLE_EODHD_RESPONSE = [
    {
        'Code': 'AAPL',
        'Name': 'Apple Inc.',
        'Exchange': 'NASDAQ',
        'Type': 'Common Stock',
        'Score': 0.95
    }
]

SAMPLE_HISTORICAL_DATA = {
    'dates': ['2023-01-01', '2023-01-02', '2023-01-03'],
    'prices': [100.0, 101.0, 102.0],
    'open': [99.0, 100.5, 101.5],
    'high': [102.0, 103.0, 104.0],
    'low': [98.0, 99.5, 100.5],
    'close': [100.0, 101.0, 102.0],
    'volumes': [1000000, 1100000, 1200000]
}


def create_mock_dataframe(data_dict):
    """Crear un DataFrame mock para tests"""
    import pandas as pd
    return pd.DataFrame([data_dict])


def create_mock_historical_dataframe():
    """Crear un DataFrame mock para datos históricos"""
    import pandas as pd
    from datetime import datetime, timedelta
    
    dates = pd.date_range('2023-01-01', periods=10, freq='D')
    data = {
        'Open': [100 + i for i in range(10)],
        'High': [105 + i for i in range(10)],
        'Low': [95 + i for i in range(10)],
        'Close': [102 + i for i in range(10)],
        'Volume': [1000000 + i * 100000 for i in range(10)]
    }
    
    return pd.DataFrame(data, index=dates) 