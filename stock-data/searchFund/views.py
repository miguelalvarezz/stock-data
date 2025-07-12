from django.shortcuts import render
from django.http import HttpResponse, Http404
from apiControl.control import perform_api_call
#from apiControl.control import DataCoordinator
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import mplfinance as mpf
import plotly.graph_objs as go
import plotly.io as pio

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from .utils import search_fund_data, get_recommended_funds_by_sector

def get_fund_sector(symbol):
    """
    Función auxiliar para obtener el sector de un fondo de manera consistente
    """
    try:
        sector_data = perform_api_call("compare", symbol, "categorySector")
        if sector_data:
            # Manejar el sector de manera consistente con compare
            if isinstance(sector_data, dict):
                # Si es un diccionario (como devuelve FMP), usar 'category'
                return sector_data.get('category')
            else:
                # Si es un string directo (como devuelve YFinance), usarlo tal cual
                return sector_data
        else:
            return None
    except Exception as e:
        print(f"Error obteniendo sector para {symbol}: {str(e)}")
        return None

def search_view(request):
    context = {
        'query': None,
        'results': None,
        'error': None,
        'info': None,  # Nuevo campo para mensajes informativos
        'recommended_funds': None  # Nuevo campo para fondos recomendados
    }
    
    if request.method == 'GET':
        query = request.GET.get('query', '').strip()
        if query:
            try:
                results = search_fund_data(query)
                
                if results:
                    # Asegurarse de que results sea una lista
                    if not isinstance(results, list):
                        results = [results]
                    
                    # Filtrar resultados None o vacíos
                    results = [r for r in results if r]
                    
                    if results:
                        # Limitar a 5 resultados máximo
                        results = results[:5]

                        # Obtener sector para cada fondo
                        for result in results:
                            try:
                                symbol = result.get('symbol')
                                if symbol:
                                    sector = get_fund_sector(symbol)
                                    if sector:
                                        result['sector'] = sector
                                    else:
                                        result['sector'] = None
                            except Exception as e:
                                print(f"Error obteniendo sector para {symbol}: {str(e)}")
                                result['sector'] = None
                        
                        # Si los resultados vienen de la búsqueda por nombre, mostrar mensaje informativo
                        if all('price' not in r and 'change_percent' not in r and 'volume' not in r for r in results):
                            context['info'] = 'Símbolo no encontrado, se muestran resultados por nombre.'
                        
                        print(f"Resultados encontrados para '{query}':")
                        for idx, result in enumerate(results, 1):
                            print(f"\nResultado {idx}:")
                            for key, value in result.items():
                                print(f"  {key}: {value}")
                        
                        context['results'] = results
                        context['query'] = query
                        
                        # Obtener fondos recomendados del mismo sector
                        if results and len(results) > 0:
                            main_result = results[0]  # Tomar el primer resultado como principal
                            sector = main_result.get('sector') or main_result.get('category') or main_result.get('benchmark')
                            
                            if sector:
                                print(f"[DEBUG] Buscando fondos recomendados para sector: {sector}")
                                recommended_funds = get_recommended_funds_by_sector(
                                    sector=sector, 
                                    exclude_symbol=main_result.get('symbol'),
                                    max_results=5
                                )
                                context['recommended_funds'] = recommended_funds
                                print(f"[DEBUG] Fondos recomendados encontrados: {len(recommended_funds)}")
                            else:
                                print(f"[DEBUG] No se encontró información de sector para {query}")
                    else:
                        context['error'] = 'No se encontraron resultados válidos para la búsqueda.'
                else:
                    context['error'] = 'Ninguna API fue capaz de realizar la búsqueda para ese fondo.'
            except Exception as e:
                print(f"Error en la búsqueda: {str(e)}")
                context['error'] = f'Error al realizar la búsqueda: {str(e)}'
        else:
            context['error'] = 'Por favor, introduce un término de búsqueda.'
    
    return render(request, 'searchFund/search.html', context)

def fund_details_view(request, symbol):
    details = perform_api_call("search", symbol)
    if isinstance(details, list):
        details = details[0] if details else {}

    # Obtener sector del fondo
    sector = get_fund_sector(symbol)

    hist_data = perform_api_call("compare", symbol, "historicalProfit")
    df = None
    candlestick_data = None
    line_data = None
    growth_last_year = None
    growth_5y_avg = None

    if hist_data and 'dates' in hist_data and 'prices' in hist_data:
        df = pd.DataFrame({
            'Fecha': pd.to_datetime(hist_data['dates']),
            'Precio': hist_data['prices']
        })
        df = df.sort_values('Fecha')
        df['Fecha'] = df['Fecha'].dt.tz_localize(None)  # Eliminar zona horaria
        # Preparar datos para plotly.js en el frontend
        line_data = {
            'dates': df['Fecha'].dt.strftime('%Y-%m-%d').tolist(),
            'prices': df['Precio'].tolist(),
        }

        # Preparar datos OHLCV para plotly.js en el frontend
        if all(k in hist_data for k in ['open', 'high', 'low', 'close', 'volumes']):
            candlestick_data = {
                'dates': pd.to_datetime(hist_data['dates']).strftime('%Y-%m-%d').tolist(),
                'open': hist_data['open'],
                'high': hist_data['high'],
                'low': hist_data['low'],
                'close': hist_data['close'],
                'volume': hist_data['volumes'],
            }

        # Calcular crecimiento del último año
        now = pd.Timestamp(datetime.now())
        one_year_ago = now - pd.DateOffset(years=1)
        df['diff'] = (df['Fecha'] - one_year_ago).abs()
        row_last_year = df.loc[df['diff'].idxmin()]
        price_last_year = row_last_year['Precio']
        price_now = df.iloc[-1]['Precio']
        if price_last_year != 0:
            growth_last_year = ((price_now / price_last_year)-1) * 100
        else:
            growth_last_year = None

        # Calcular crecimiento medio anual de los últimos 5 años (CAGR)
        five_years_ago = now - pd.DateOffset(years=5)
        df['diff_5y'] = (df['Fecha'] - five_years_ago).abs()
        row_5y_ago = df.loc[df['diff_5y'].idxmin()]
        price_5y_ago = row_5y_ago['Precio']
        if price_5y_ago != 0 and len(df) > 1:
            n_years = (df.iloc[-1]['Fecha'] - row_5y_ago['Fecha']).days / 365.25
            if n_years > 0:
                growth_5y_avg = ((price_now / price_5y_ago) ** (1/n_years) - 1) * 100
            else:
                growth_5y_avg = None
        else:
            growth_5y_avg = None

    context = {
        'symbol': symbol,
        'details': details,
        'sector': sector,  # Agregar el sector al contexto
        'df': df,
        'line_data': line_data,
        'candlestick_data': candlestick_data,
        'growth_last_year': growth_last_year,
        'growth_5y_avg': growth_5y_avg,
    }
    return render(request, 'searchFund/fund_details.html', context)