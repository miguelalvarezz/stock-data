from .yfinance_service import YFinanceService
from .fmp_service import FMPService
from .eodhd_service import EODHDService
from .alphavantage_service import AlphaVantageService

class DataCoordinator:
    def __init__(self):
        self.yfinance = YFinanceService()
        self.fmp = FMPService()
        self.eodhd = EODHDService()
        self.alpha_vantage = AlphaVantageService()

    def search_fund(self, query):
        """
        Funcionalidad 1: Búsqueda de fondos
        """
        try:
            # Primero intentamos con FMP (búsqueda principal)
            results = self.fmp.search_funds(query)
            if results:
                return results

            # Si falla, intentamos con EODHD (backup)
            return self.eodhd.search_funds(query)
        except Exception as e:
            # Log del error
            return None

    def get_fund_comparison_data(self, symbol):
        """
        Funcionalidad 2: Comparación de fondos
        """
        data = {}
        try:
            # Datos principales de YFinance
            data.update(self.yfinance.get_fund_data(symbol))
            
            # Ratios de riesgo de FMP
            data.update(self.fmp.get_risk_ratios(symbol))
            
            # Comisiones detalladas de EODHD
            data.update(self.eodhd.get_detailed_fees(symbol))
        except Exception as e:
            # Si falla YFinance, intentamos con Alpha Vantage
            data.update(self.alpha_vantage.get_historical_data(symbol))
        
        return data

    def get_chart_data(self, symbol, timeframe):
        """
        Funcionalidad 4: Visualización de gráficos
        """
        try:
            # Precios históricos de YFinance
            price_data = self.yfinance.get_historical_prices(symbol, timeframe)
            
            # Datos de riesgo de FMP para gráfico radar
            risk_data = self.fmp.get_risk_data(symbol)
            
            # Métricas técnicas de Alpha Vantage
            technical_data = self.alpha_vantage.get_technical_metrics(symbol)
            
            return {
                'prices': price_data,
                'risk': risk_data,
                'technical': technical_data
            }
        except Exception as e:
            # Si falla YFinance, usamos Alpha Vantage como backup
            return self.alpha_vantage.get_historical_data(symbol)