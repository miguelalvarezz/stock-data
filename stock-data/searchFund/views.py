from django.shortcuts import render
from apiControl.services.control import DataCoordinator

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
                coordinator = DataCoordinator()
                results = coordinator.search_fund(query)
                
                if results:
                    context['results'] = results
                    context['query'] = query
                else:
                    context['error'] = 'Ninguna API fue capaz de realizar la búsqueda para ese fondo.'
            except Exception as e:
                context['error'] = f'Error al realizar la búsqueda: {str(e)}'
        else:
            context['error'] = 'Por favor, introduce un término de búsqueda.'
    
    return render(request, 'searchFund/search.html', context)