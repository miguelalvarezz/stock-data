from django.shortcuts import render

from django.shortcuts import render
from .utils import compare_funds_data

# Create your views here.
#from django.http import HttpResponse



def compare_view(request):
    f1 = request.GET.get('fund1')
    f2 = request.GET.get('fund2')
    comparison_table = None
    if f1 and f2:
        comparison_table = compare_funds_data(f1, f2).to_html(classes="table table-bordered")
    return render(request, 'compareFund/compare.html', {
        'fund1': f1,
        'fund2': f2,
        'comparison_table': comparison_table
    })