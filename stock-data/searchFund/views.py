from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from .utils import search_fund_data

def search_view(request):
    query = request.GET.get('query')
    fund_data = None
    if query:
        fund_data = search_fund_data(query)
    return render(request, 'searchFund/search.html', {
        'query': query,
        'fund_data': fund_data
    })