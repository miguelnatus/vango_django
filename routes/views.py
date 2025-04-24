from django.urls import path
from . import views

app_name = 'routes'

# Implementações básicas das views para evitar erros
def route_list_view(request):
    return render(request, 'routes/list.html', {})

def route_search_view(request):
    return render(request, 'routes/search.html', {})

def route_detail_view(request, route_id):
    return render(request, 'routes/detail.html', {})

def route_create_view(request):
    return render(request, 'routes/create.html', {})

def route_edit_view(request, route_id):
    return render(request, 'routes/edit.html', {})

def driver_routes_view(request):
    return render(request, 'routes/driver_routes.html', {})
