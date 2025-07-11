from .services.yfinance_service import YFinanceService
from .services.fmp_service import FMPService
from .services.eodhd_service import EODHDService
from .services.alphavantage_service import AlphaVantageService
from .exceptions.apiException import APIError


def generic_search(query):
    # Primero intenta buscar por símbolo con YFinance
    try:
        result = YFinanceService.getSearchData(query)
        if result:
            return result
    except Exception:
        pass
    # Si falla, intenta buscar por nombre con EODHD
    try:
        eodhd = EODHDService()
        api_result = eodhd.getSearchData(query)
        if api_result and api_result.get('quotes'):
            return api_result['quotes']
    except Exception:
        pass
    return None

API_MAPPING = {
    "search": {
        "primary": generic_search,
        #"backup": lambda symbol: EODHDService().getSearchData(symbol),
    },

    "compare": {
        "historicalProfit": {
            "primary": YFinanceService.getHistoricalProfit,
        #    "backup": AlphaVantageService.getHistoricalProfit,
        },
        "anualVolatility": {
            "primary": YFinanceService.getAnualVolatility,
            #"backup": FMPService.getAnualVolatility,
        },
        "commissions": {
            "primary": lambda symbol: FMPService().getCommissions(symbol),
        },
        "categorySector": {
            "primary": lambda symbol: FMPService().getCategorySector(symbol),           # ACTUALMENTE NO FUNCIONA
            "backup": YFinanceService.getCategorySector,                                # ACTUALMENTE FUNCIONA ESTA
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
