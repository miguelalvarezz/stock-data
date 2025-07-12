import yfinance as yf
import pandas as pd
from apiControl.control import perform_api_call
import requests
from .models import Fund


def is_basic_fund_info(fund):
    # Ajusta los campos según lo que devuelva EODHD
    basic_keys = {'symbol', 'shortname', 'longname', 'exchange', 'type', 'score'}
    return set(fund.keys()).issubset(basic_keys)

def get_recommended_funds_by_sector(sector, exclude_symbol=None, max_results=5):
    """
    Obtiene fondos recomendados del mismo sector
    """
    if not sector:
        return []
    
    try:
        print(f"[DEBUG] Buscando fondos recomendados para sector: {sector}")
        
        # Lista de fondos populares por sector (esto se puede expandir)
        sector_funds = {
            'Technology': ['QQQ', 'XLK', 'VGT', 'SMH', 'SOXX', 'IGV', 'XSW'],
            'Healthcare': ['XLV', 'VHT', 'IHI', 'IHF', 'XHE', 'IHV', 'XHS'],
            'Financial': ['XLF', 'VFH', 'IYF', 'KBE', 'KRE', 'XLFS', 'VFH'],
            'Energy': ['XLE', 'VDE', 'IXC', 'XOP', 'OIH', 'XES', 'XME'],
            'Consumer Discretionary': ['XLY', 'VCR', 'IYC', 'XRT', 'FDIS', 'XHB'],
            'Consumer Staples': ['XLP', 'VDC', 'IYK', 'XLP', 'KXI', 'XHS'],
            'Industrials': ['XLI', 'VIS', 'IYJ', 'XAR', 'ITA', 'XHB'],
            'Materials': ['XLB', 'VAW', 'IYM', 'XME', 'PICK', 'XES'],
            'Real Estate': ['XLRE', 'VNQ', 'IYR', 'SCHH', 'RWR', 'XHB'],
            'Utilities': ['XLU', 'VPU', 'IDU', 'XLU', 'JXI', 'XHS'],
            'Communication Services': ['XLC', 'VOX', 'IYZ', 'XTL', 'FCOM', 'XSW'],
            'Internet Retail': ['AMZN', 'BABA', 'JD', 'PDD', 'MELI', 'ETSY', 'SHOP', 'BIDU'],
            'Auto Manufacturers': ['TSLA', 'TM', 'F', 'GM', 'HMC', 'NSANY', 'RACE', 'NIO', 'XPEV', 'LI'],
            'ETF': ['SPY', 'VOO', 'IVV', 'QQQ', 'VTI', 'DIA', 'IWM'],
            'Index': ['SPY', 'VOO', 'IVV', 'QQQ', 'VTI', 'DIA', 'IWM'],
            'Equity': ['SPY', 'VOO', 'IVV', 'QQQ', 'VTI', 'DIA', 'IWM'],
            'Mutual Fund': ['VFINX', 'VTSMX', 'VWELX', 'VWINX', 'VWNDX'],
            'S&P 500': ['SPY', 'VOO', 'IVV', 'SPLG', 'SPLG'],
            'NASDAQ': ['QQQ', 'TQQQ', 'SQQQ', 'QLD', 'QID'],
            'Dow Jones': ['DIA', 'UDOW', 'SDOW', 'DDM', 'DXD'],
            'Russell 2000': ['IWM', 'TNA', 'TZA', 'UWM', 'SAA']
        }
        
        # Mapeo de sectores similares
        sector_mapping = {
            'tech': 'Technology',
            'technology': 'Technology',
            'health': 'Healthcare',
            'healthcare': 'Healthcare',
            'medical': 'Healthcare',
            'finance': 'Financial',
            'financial': 'Financial',
            'banking': 'Financial',
            'oil': 'Energy',
            'energy': 'Energy',
            'consumer': 'Consumer Discretionary',
            'retail': 'Consumer Discretionary',
            'industrial': 'Industrials',
            'manufacturing': 'Industrials',
            'material': 'Materials',
            'real estate': 'Real Estate',
            'reit': 'Real Estate',
            'utility': 'Utilities',
            'telecom': 'Communication Services',
            'communication': 'Communication Services',
            'internet retail': 'Internet Retail',
            'ecommerce': 'Internet Retail',
            'online retail': 'Internet Retail',
            'auto': 'Auto Manufacturers',
            'automotive': 'Auto Manufacturers',
            'automobile': 'Auto Manufacturers',
            'cars': 'Auto Manufacturers',
            'vehicles': 'Auto Manufacturers',
            'etf': 'ETF',
            'index': 'Index',
            'equity': 'Equity',
            'mutual': 'Mutual Fund',
            's&p': 'S&P 500',
            'sp500': 'S&P 500',
            'nasdaq': 'NASDAQ',
            'dow': 'Dow Jones',
            'russell': 'Russell 2000'
        }
        
        # Buscar fondos del sector específico
        sector_key = None
        sector_lower = sector.lower()
        
        # Primero intentar mapeo directo
        if sector_lower in sector_mapping:
            sector_key = sector_mapping[sector_lower]
        else:
            # Buscar coincidencias parciales
            for key in sector_funds.keys():
                if key.lower() in sector_lower or sector_lower in key.lower():
                    sector_key = key
                    break
        
        if not sector_key:
            # Si no encontramos el sector exacto, buscar fondos similares
            print(f"[DEBUG] Sector '{sector}' no encontrado en la lista, buscando fondos generales")
            # Usar fondos generales como fallback
            sector_key = 'ETF'
        
        recommended_symbols = sector_funds[sector_key]
        
        # Excluir el símbolo actual si se proporciona
        if exclude_symbol:
            recommended_symbols = [s for s in recommended_symbols if s.upper() != exclude_symbol.upper()]
        
        # Obtener datos de los fondos recomendados
        recommended_funds = []
        for symbol in recommended_symbols[:max_results]:
            try:
                fund_data = perform_api_call("search", symbol)
                if fund_data:
                    if isinstance(fund_data, list):
                        fund_data = fund_data[0] if fund_data else None
                    
                    if fund_data and isinstance(fund_data, dict):
                        # Añadir información adicional
                        fund_data['is_recommended'] = True
                        fund_data['recommendation_reason'] = f"Fondo del sector {sector}"
                        recommended_funds.append(fund_data)
                        
            except Exception as e:
                print(f"[DEBUG] Error obteniendo datos para {symbol}: {str(e)}")
                continue
        
        print(f"[DEBUG] Fondos recomendados encontrados: {len(recommended_funds)}")
        return recommended_funds
        
    except Exception as e:
        print(f"[DEBUG] Error obteniendo fondos recomendados: {str(e)}")
        return []

def search_fund_data(symbol):
    print(f"[DEBUG] Iniciando búsqueda de {symbol}")
    result = perform_api_call("search", symbol)
    if result:
        # Si el resultado es una lista de fondos básicos, haz la búsqueda detallada
        if isinstance(result, list) and all(is_basic_fund_info(f) for f in result if isinstance(f, dict)):
            print("[DEBUG] Resultado contiene solo información básica, se realizará búsqueda detallada por símbolo")
            detailed_results = []
            for fund in result:
                symbol_key = (fund.get('symbol') or fund.get('Code') or '').strip()
                print(f"[DEBUG] Buscando detalles para símbolo: '{symbol_key}'")
                if symbol_key:
                    try:
                        details = perform_api_call("search", symbol_key)
                        print(f"[DEBUG] Resultado de búsqueda detallada para '{symbol_key}': {details}")
                        if details:
                            if isinstance(details, list):
                                for d in details:
                                    if isinstance(d, dict):
                                        detailed_results.append(d)
                            elif isinstance(details, dict):
                                detailed_results.append(details)
                        else:
                            print(f"[DEBUG] No se encontró información detallada para {symbol_key}")
                    except Exception as e_detail:
                        print(f"[DEBUG] Error buscando detalles para {symbol_key}: {e_detail}")
                else:
                    print(f"[DEBUG] Fondo sin símbolo válido: {fund}")
            print(f"[DEBUG] Resultados detallados finales: {detailed_results}")
            return detailed_results if detailed_results else result
        else:
            return result
    else:
        print("[DEBUG] No se encontraron resultados para la búsqueda.")
        return None


'''
def search_fund_data(symbol):
    try:
        fund = yf.Ticker(symbol)
        info = fund.info

        # LOGICA CALCULO RENTABILIDAD ANUAL DURANTE 10 AÑOS
        symbol = info.get('symbol')
        years = 10

        # API Alpha Vantage -> precios historicos (backup si falla yf) e informacion volatilidad
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={symbol}&apikey=TSZP1J022SY5DL5D'
        response = requests.get(url)
        data = response.json()

        if 'Monthly Adjusted Time Series' not in data:
            print("Error al obtener datos. Verifica el símbolo o tu clave API.")
            exit()

        # === 2. CONVERTIR A DATAFRAME ===
        monthly_data = data['Monthly Adjusted Time Series']
        df = pd.DataFrame.from_dict(monthly_data, orient='index')
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        df = df[['5. adjusted close']].astype(float)
        df.rename(columns={'5. adjusted close': 'Adj Close'}, inplace=True)

        # === 3. FILTRAR FECHAS ===
        end_date = df.index.max()
        start_date = end_date.replace(year=end_date.year - years)

        # Asegurarse de que haya datos en el mes exacto
        if start_date not in df.index:
            # Buscar el primer mes disponible después de la fecha objetivo
            start_date = df[df.index >= start_date].index[0]

        start_price = df.loc[start_date, 'Adj Close']
        end_price = df.loc[end_date, 'Adj Close']

        # === 4. CALCULAR CAGR ===
        cagr = ((end_price / start_price) ** (1 / years) - 1) * 100

        return {
            'symbol': info.get('symbol'),
            'name': info.get('longName'),
            'sector': info.get('sector'),
            #'return1y': info.get('52WeekChange'),
            'return1y': cagr,
            'fees': info.get('annualReportExpenseRatio'),
            'benchmark': info.get('category'),
        }
    except:
        return None
'''