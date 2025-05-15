from django.shortcuts import render
from django.http import HttpResponse, Http404
from apiControl.control import perform_api_call
#from apiControl.control import DataCoordinator

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from .utils import search_fund_data

def search_view(request):
    context = {
        'query': None,
        'results': None,
        'error': None
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
                        print(f"Resultados encontrados para '{query}':")
                        for idx, result in enumerate(results, 1):
                            print(f"\nResultado {idx}:")
                            for key, value in result.items():
                                print(f"  {key}: {value}")
                        
                        context['results'] = results
                        context['query'] = query
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