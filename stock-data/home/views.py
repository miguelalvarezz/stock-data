import requests
import pandas as pd
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import ClientUser


def get_market_trends():
    api_key = settings.FMP_API_KEY
    base_url = 'https://financialmodelingprep.com/api/v3/stock/'
    endpoints = {
        'most_active': f'{base_url}actives?apikey={api_key}',
        'gainers': f'{base_url}gainers?apikey={api_key}',
        'losers': f'{base_url}losers?apikey={api_key}',
    }
    data = {}
    for key, url in endpoints.items():
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data[key] = resp.json().get('mostActiveStock', resp.json())
            else:
                data[key] = []
        except Exception as e:
            data[key] = []
    return data


def home_view(request):
    market_trends = get_market_trends()
    sort = request.GET.get('sort')
    order = request.GET.get('order')
    tab = request.GET.get('tab', 'most_active')

    # Solo ordena si el usuario ha hecho clic en un encabezado (hay sort y order)
    if sort and order and tab in market_trends:
        items = market_trends[tab]
        if items and isinstance(items, list):
            df = pd.DataFrame(items)
            column_map = {
                'price': 'price',
                'changes': 'changes',
                'changesPercentage': 'changesPercentage',
            }
            sort_col = column_map.get(sort, sort)
            if sort_col in df.columns:
                ascending = (order == 'asc')
                if sort_col == 'changesPercentage':
                    df[sort_col] = df[sort_col].str.replace('%','').str.replace('+','').str.replace(',','.').astype(float)
                elif sort_col == 'price' or sort_col == 'changes':
                    df[sort_col] = pd.to_numeric(df[sort_col], errors='coerce')
                df = df.sort_values(by=sort_col, ascending=ascending)
                if sort_col == 'changesPercentage':
                    def format_change(val):
                        if pd.isna(val):
                            return "N/A"
                        sign = "+" if val >= 0 else ""
                        return f"{sign}{val:.2f}%"
                    df[sort_col] = df[sort_col].apply(format_change)
                market_trends[tab] = df.to_dict(orient='records')

    return render(request, 'home/home.html', {
        'market_trends': market_trends,
        'sort': sort,
        'order': order,
        'tab': tab,
    })

def register_view(request):
    """
    Vista para el registro de nuevos usuarios
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a StockData.')
            return redirect('home')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'home/register.html', {'form': form})

def login_view(request):
    """
    Vista para el inicio de sesión
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de vuelta, {user.get_full_name()}!')
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'home/login.html', {'form': form})

def logout_view(request):
    """
    Vista para cerrar sesión
    """
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('home')

@login_required
def profile_view(request):
    """
    Vista para ver y editar el perfil del usuario
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'home/profile.html', {'form': form})