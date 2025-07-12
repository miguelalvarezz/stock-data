from django.shortcuts import render
from .utils import compare_fund
from apiControl.services.yfinance_service import YFinanceService



def compare_view(request):
    f1 = request.GET.get('fund1', '').strip().upper()
    f2 = request.GET.get('fund2', '').strip().upper()
    
    print(f"[DEBUG] Fondos recibidos: fund1={f1}, fund2={f2}")
    
    context = {
        'fund1': f1,
        'fund2': f2,
        'comparison_table': None,
        'error': None
    }
    
    if not f1 and not f2:
        return render(request, 'compareFund/compare.html', context)
    
    try:
        # Verificar que ambos fondos existen
        fund1_data = YFinanceService.getSearchData(f1)
        fund2_data = YFinanceService.getSearchData(f2)
        
        if not fund1_data:
            context['error'] = f"No se encontró el fondo: {f1}"
            return render(request, 'compareFund/compare.html', context)
            
        if not fund2_data:
            context['error'] = f"No se encontró el fondo: {f2}"
            return render(request, 'compareFund/compare.html', context)
        
        # Si ambos fondos existen, proceder con la comparación
        print(f"[DEBUG] Intentando comparar fondos: {f1} vs {f2}")
        df, price_series, annual_returns_series, growth_last_year, growth_5y_avg = compare_fund(f1, f2)
        
        if not df.empty:
            comparison_table = df.to_html(classes="table table-bordered table-striped")
            context['comparison_table'] = comparison_table
            context['price_series'] = price_series
            context['annual_returns_series'] = annual_returns_series
            context['growth_last_year'] = growth_last_year
            context['growth_5y_avg'] = growth_5y_avg
            # Pasar valores simples para el template
            context['growth_last_year_fund1'] = growth_last_year.get(f1)
            context['growth_last_year_fund2'] = growth_last_year.get(f2)
            context['growth_5y_avg_fund1'] = growth_5y_avg.get(f1)
            context['growth_5y_avg_fund2'] = growth_5y_avg.get(f2)
            print(f"[DEBUG] Tabla HTML generada: {comparison_table[:100]}...")
        else:
            context['error'] = "No se pudieron obtener datos para la comparación"
            print("[DEBUG] DataFrame vacío")
            
    except Exception as e:
        print(f"[DEBUG] Error en la comparación: {str(e)}")
        context['error'] = f"Error al realizar la comparación: {str(e)}"
    
    return render(request, 'compareFund/compare.html', context)