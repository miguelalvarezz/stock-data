from .services.yfinance_service import YFinanceService
from .services.fmp_service import FMPService
from .services.eodhd_service import EODHDService
from .services.alphavantage_service import AlphaVantageService
from .exceptions.apiException import APIError



API_MAPPING = {
    "search": {
        "primary": YFinanceService.getSearchData,
        #"backup": lambda symbol: EODHDService().getSearchData(symbol),
    },

    "compare": {
        "historicalProfit": {
            "primary": YFinanceService.getHistoricalProfit,
            "backup": AlphaVantageService.getHistoricalProfit,
        },
        "anualVolatility": {
            "primary": YFinanceService.getAnualVolatility,
            "backup": FMPService.getAnualVolatility,
        },
        "commissions": {
            "primary": lambda symbol: FMPService().getCommissions(symbol),
        },
        "categorySector": {
            "primary": lambda symbol: FMPService().getCategorySector(symbol),
            "backup": YFinanceService.getCategorySector,
        },
        #"rating": {
            # Añadir en caso de que exista una API que devuelva el rating
            # Actualmente se realiza un ranking propio basado en rentabilidad/riesgo
        #},
    }
}

def perform_api_call(action, params, field=None):
    """
    Llama al método correspondiente dentro de la API (como .compare()).
    Si 'field' está presente, selecciona el API mapping por campo específico.
    """
    try:
        config = (
            API_MAPPING[action].get(field)
            if field
            else API_MAPPING[action]
        )

        if not config:
            raise APIError(f"No hay configuración para action='{action}', field='{field}'")

        primary_service = config.get("primary")

        try:
            return primary_service(params)
        except Exception as e:
            print(f"[API] Error en primaria para action='{action}', field='{field}': {e}")
            backup_service = config.get("backup")
            if backup_service:
                return backup_service(params)
            else:
                raise APIError(f"Error en API primaria y sin backup para action='{action}', field='{field}'")

    except KeyError:
        raise APIError(f"Acción o campo inválido: action='{action}', field='{field}'")


    

'''
def is_result_useful(result):
    campos_clave = [
        'symbol', 'name', 'price', 'change_percent', 'volume', 'risk_ratios', 'fees'
    ]
    return any(
        result.get(campo) not in [None, '', 'N/A', 'null', {}] for campo in campos_clave
    )

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
        all_results = []
        try:
            # Primero intentamos con FMP (búsqueda principal)
            fmp_results = self.fmp.search_funds(query)
            if fmp_results:
                all_results.extend(fmp_results)

            # Luego intentamos con YFinance SOLO si no hay resultados de FMP
            if not all_results:
                try:
                    yf_data = self.yfinance.get_fund_data(query)
                    if yf_data:
                        all_results.append(yf_data)
                except Exception as e:
                    print(f"Error en búsqueda YFinance: {str(e)}")

            # Si no hay resultados, intentamos con EODHD (backup)
            if not all_results:
                eod_results = self.eodhd.search_funds(query)
                if eod_results:
                    all_results.extend(eod_results)

            # Enriquecer los resultados con datos adicionales
            for result in all_results:
                if 'symbol' in result:
                    additional_data = self.get_fund_data(result['symbol'])
                    result.update(additional_data)

            # Filtrar resultados útiles
            all_results = [r for r in all_results if is_result_useful(r)]

            return all_results if all_results else None

        except Exception as e:
            # Log del error
            print(f"Error en la búsqueda de fondos: {str(e)}")
            return None

    def get_fund_comparison_data(self, symbol):
        """
        Funcionalidad 2: Comparación de fondos        
        """
        data = {}

        # Rentabilidad historica -> yfinance y av backup
        try:
            historical_data = self.yfinance.get_historical_performance(symbol)
            data.update({
                    'performance_10y': historical_data.get('10y'),
                    'performance_5y': historical_data.get('5y'),
                    'performance_3y': historical_data.get('3y')
                })
        except Exception as e:
            # Backup con Alpha Vantage
            try:
                historical_data = self.alpha_vantage.get_historical_performance(symbol)
                data.update({
                    'performance_10y': historical_data.get('10y'),
                    'performance_5y': historical_data.get('5y'),
                    'performance_3y': historical_data.get('3y')
                })
            except Exception as e:
                return None
            
        # Volatilidad anual -> yfinance y fmp backup
        try:
            volatility_data = self.fmp.get_volatility(symbol)
            data['volatility'] = volatility_data
        except Exception as e:
            try:
                volatility_data = self.alpha_vantage.get_volatility(symbol)
                data['volatility'] = volatility_data
            except Exception as e:
                return None
            
        # Comisiones y gastos -> fmp
        try:
            fees_data = self.fmp.get_fund_fees(symbol)
            data['fees'] = fees_data
        except Exception as e:
            return None
        
        # Categoria/sector -> fmp y eodhd como backup
        try:
            category_data = self.fmp.get_fund_category(symbol)
            data['category'] = category_data
        except Exception as e:
            try:
                category_data = self.alpha_vantage.get_fund_category(symbol)
                data['category'] = category_data
            except Exception as e:
                print(f"Error obteniendo categoría de Alpha Vantage: {str(e)}")
        
        # Rating/calificación -> calculo basado en rentabilidad/riesgo
        try:
            rating_data = self._calculate_fund_rating(data)
            data['rating'] = rating_data
        except Exception as e:
            print(f"Error calculando rating del fondo: {str(e)}")

        return data
    

    def _calculate_fund_rating(self, fund_data):
        """
        Basado en la rentabilidad y el riesgo
        """
        try:
            # Obtener datos necesarios
            performance_3y = fund_data.get('performance_3y', 0)
            volatility = fund_data.get('volatility', 0)
            
            if volatility == 0:
                return 'N/A'
            
            # Calcular ratio de Sharpe simplificado
            sharpe_ratio = performance_3y / volatility
            
            # Asignar estrellas basado en el ratio
            if sharpe_ratio > 2.0:
                return '★★★★★'
            elif sharpe_ratio > 1.5:
                return '★★★★☆'
            elif sharpe_ratio > 1.0:
                return '★★★☆☆'
            elif sharpe_ratio > 0.5:
                return '★★☆☆☆'
            else:
                return '★☆☆☆☆'
        except Exception as e:
            return 'N/A'


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

    def get_fund_data(self, symbol):
        """
        Recupera datos detallados combinados de todas las fuentes
        """
        data = {}
        risk_ratios = {}
        fees = {}

        # 1. Intentar obtener datos básicos de YFinance
        try:
            yf_data = self.yfinance.get_fund_data(symbol)
            print(f"[LOG] YFinance data for {symbol}: {yf_data}")
            if yf_data:
                data.update(yf_data)
                # Extraer comisión si existe
                if yf_data.get('fees') not in [None, '', 'null', 'N/A']:
                    fees['annualReportExpenseRatio'] = yf_data['fees']
        except Exception as e:
            print(f"Error getting YFinance data: {str(e)}")

        # 2. Si faltan datos básicos, intentar con FMP (search_funds)
        try:
            if not data.get('name') or not data.get('symbol'):
                fmp_search = self.fmp.search_funds(symbol)
                print(f"[LOG] FMP search_funds for {symbol}: {fmp_search}")
                if isinstance(fmp_search, list) and fmp_search:
                    for key, value in fmp_search[0].items():
                        if key not in data or data[key] in [None, '', 'null']:
                            data[key] = value
                else:
                    print(f"[LOG] FMP tampoco encontró información básica para {symbol}.")
        except Exception as e:
            print(f"Error getting FMP search_funds data: {str(e)}")

        # 3. Ratios de riesgo de FMP
        try:
            fmp_data = self.fmp.get_risk_ratios(symbol)
            print(f"[LOG] FMP risk ratios for {symbol}: {fmp_data}")
            # Seleccionar solo los ratios de riesgo más relevantes
            risk_keys = [
                'currentRatio', 'quickRatio', 'debtEquityRatio', 'grossProfitMargin',
                'netProfitMargin', 'returnOnAssets', 'returnOnEquity', 'priceEarningsRatio',
                'priceToBookRatio', 'priceToSalesRatio', 'interestCoverage', 'cashRatio'
            ]
            for key in risk_keys:
                if key in fmp_data and fmp_data[key] not in [None, '', 'null', 'N/A']:
                    risk_ratios[key] = fmp_data[key]
        except Exception as e:
            print(f"Error getting FMP data: {str(e)}")

        # 4. Comisiones detalladas de EODHD
        try:
            eod_data = self.eodhd.get_detailed_fees(symbol)
            print(f"[LOG] EODHD detailed fees for {symbol}: {eod_data}")
            # Buscar posibles campos de comisiones
            fee_keys = ['managementFee', 'expenseRatio', 'totalExpenseRatio']
            for key in fee_keys:
                if key in eod_data and eod_data[key] not in [None, '', 'null', 'N/A']:
                    fees[key] = eod_data[key]
        except Exception as e:
            print(f"Error getting EODHD data: {str(e)}")

        if risk_ratios:
            data['risk_ratios'] = risk_ratios
        if fees:
            data['fees'] = fees

        print(f"[LOG] Datos combinados finales para {symbol}: {data}")
        return data
'''