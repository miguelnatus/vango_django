from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.utils import timezone
from .models import Route, RouteImage, RouteStop
from .forms import RouteForm, RouteImageForm, RouteStopForm
from vehicles.models import Vehicle
from bookings.models import Booking
import json

def route_list_view(request):
    """
    Lista todas as rotas ativas.
    """
    routes = Route.objects.filter(is_active=True, status='active')
    
    # Filtros
    origin = request.GET.get('origin', '')
    destination = request.GET.get('destination', '')
    date = request.GET.get('date', '')
    
    if origin:
        routes = routes.filter(origin_name__icontains=origin)
    
    if destination:
        routes = routes.filter(destination_name__icontains=destination)
    
    if date:
        # Converter data para dia da semana (0-6)
        try:
            date_obj = timezone.datetime.strptime(date, '%Y-%m-%d')
            day_of_week = date_obj.weekday()
            
            # Filtrar rotas disponíveis nesse dia
            routes = [route for route in routes if day_of_week in route.available_days]
        except ValueError:
            pass
    
    context = {
        'routes': routes,
        'origin': origin,
        'destination': destination,
        'date': date,
    }
    
    return render(request, 'routes/list.html', context)

def route_detail_view(request, route_id):
    """
    Exibe detalhes de uma rota específica.
    """
    route = get_object_or_404(Route, id=route_id, is_active=True)
    
    # Obter avaliações
    from reviews.models import Review
    reviews = Review.objects.filter(route=route).order_by('-created_at')[:5]
    
    # Obter paradas
    stops = RouteStop.objects.filter(route=route).order_by('order')
    
    # Obter imagens
    images = RouteImage.objects.filter(route=route).order_by('order')
    
    # Dados para o mapa
    map_data = route.get_map_data()
    
    # Adicionar paradas ao mapa
    map_data['stops'] = [
        {
            'name': stop.name,
            'description': stop.description,
            'lat': float(stop.latitude),
            'lng': float(stop.longitude),
            'duration': stop.duration_minutes
        } for stop in stops
    ]
    
    context = {
        'route': route,
        'reviews': reviews,
        'stops': stops,
        'images': images,
        'map_data': json.dumps(map_data),
        'api_key': 'YOUR_GOOGLE_MAPS_API_KEY',  # Substituir pela chave real
    }
    
    return render(request, 'routes/detail.html', context)

def route_search_view(request):
    """
    Pesquisa de rotas com filtros avançados.
    """
    routes = Route.objects.filter(is_active=True, status='active')
    
    # Filtros básicos
    origin = request.GET.get('origin', '')
    destination = request.GET.get('destination', '')
    date = request.GET.get('date', '')
    
    # Filtros avançados
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    departure_time = request.GET.get('departure_time', '')
    has_wifi = request.GET.get('has_wifi', '')
    has_air_conditioning = request.GET.get('has_air_conditioning', '')
    is_accessible = request.GET.get('is_accessible', '')
    
    if origin:
        routes = routes.filter(origin_name__icontains=origin)
    
    if destination:
        routes = routes.filter(destination_name__icontains=destination)
    
    if date:
        try:
            date_obj = timezone.datetime.strptime(date, '%Y-%m-%d')
            day_of_week = date_obj.weekday()
            routes = [route for route in routes if day_of_week in route.available_days]
        except ValueError:
            pass
    
    if min_price:
        routes = routes.filter(price__gte=min_price)
    
    if max_price:
        routes = routes.filter(price__lte=max_price)
    
    if departure_time:
        # Implementação futura: filtrar por horário de partida
        pass
    
    if has_wifi:
        routes = routes.filter(has_wifi=True)
    
    if has_air_conditioning:
        routes = routes.filter(has_air_conditioning=True)
    
    if is_accessible:
        routes = routes.filter(is_accessible=True)
    
    context = {
        'routes': routes,
        'origin': origin,
        'destination': destination,
        'date': date,
        'min_price': min_price,
        'max_price': max_price,
        'departure_time': departure_time,
        'has_wifi': has_wifi,
        'has_air_conditioning': has_air_conditioning,
        'is_accessible': is_accessible,
    }
    
    return render(request, 'routes/search.html', context)

@login_required
def route_create_view(request):
    """
    Cria uma nova rota.
    """
    if not request.user.is_driver:
        messages.error(request, 'Apenas motoristas podem criar rotas.')
        return redirect('accounts:passenger_dashboard')
    
    # Verificar se o motorista tem veículos cadastrados
    vehicles = Vehicle.objects.filter(driver=request.user)
    if not vehicles.exists():
        messages.error(request, 'Você precisa cadastrar um veículo antes de criar uma rota.')
        return redirect('vehicles:create')
    
    if request.method == 'POST':
        form = RouteForm(request.POST, request.FILES)
        if form.is_valid():
            route = form.save(commit=False)
            route.driver = request.user
            
            # Processar waypoints do mapa
            waypoints_json = request.POST.get('waypoints_json', '[]')
            try:
                route.waypoints = json.loads(waypoints_json)
            except json.JSONDecodeError:
                route.waypoints = []
            
            route.save()
            messages.success(request, 'Rota criada com sucesso!')
            return redirect('routes:detail', route_id=route.id)
    else:
        form = RouteForm()
    
    context = {
        'form': form,
        'vehicles': vehicles,
        'api_key': 'YOUR_GOOGLE_MAPS_API_KEY',  # Substituir pela chave real
    }
    
    return render(request, 'routes/create.html', context)

@login_required
def route_edit_view(request, route_id):
    """
    Edita uma rota existente.
    """
    route = get_object_or_404(Route, id=route_id, driver=request.user)
    
    if request.method == 'POST':
        form = RouteForm(request.POST, request.FILES, instance=route)
        if form.is_valid():
            route = form.save(commit=False)
            
            # Processar waypoints do mapa
            waypoints_json = request.POST.get('waypoints_json', '[]')
            try:
                route.waypoints = json.loads(waypoints_json)
            except json.JSONDecodeError:
                route.waypoints = []
            
            route.save()
            messages.success(request, 'Rota atualizada com sucesso!')
            return redirect('routes:detail', route_id=route.id)
    else:
        form = RouteForm(instance=route)
    
    # Obter paradas
    stops = RouteStop.objects.filter(route=route).order_by('order')
    
    # Dados para o mapa
    map_data = route.get_map_data()
    
    # Adicionar paradas ao mapa
    map_data['stops'] = [
        {
            'name': stop.name,
            'description': stop.description,
            'lat': float(stop.latitude),
            'lng': float(stop.longitude),
            'duration': stop.duration_minutes
        } for stop in stops
    ]
    
    context = {
        'form': form,
        'route': route,
        'stops': stops,
        'map_data': json.dumps(map_data),
        'api_key': 'YOUR_GOOGLE_MAPS_API_KEY',  # Substituir pela chave real
    }
    
    return render(request, 'routes/edit.html', context)

@login_required
def driver_routes_view(request):
    """
    Lista as rotas do motorista.
    """
    if not request.user.is_driver:
        return redirect('accounts:passenger_dashboard')
    
    routes = Route.objects.filter(driver=request.user)
    
    # Filtrar por status
    status = request.GET.get('status', '')
    if status:
        routes = routes.filter(status=status)
    
    context = {
        'routes': routes,
        'status': status,
    }
    
    return render(request, 'routes/driver_routes.html', context)

@login_required
def route_stop_add_view(request, route_id):
    """
    Adiciona uma parada a uma rota.
    """
    route = get_object_or_404(Route, id=route_id, driver=request.user)
    
    if request.method == 'POST':
        form = RouteStopForm(request.POST)
        if form.is_valid():
            stop = form.save(commit=False)
            stop.route = route
            
            # Definir ordem
            last_stop = RouteStop.objects.filter(route=route).order_by('-order').first()
            stop.order = (last_stop.order + 1) if last_stop else 1
            
            stop.save()
            messages.success(request, 'Parada adicionada com sucesso!')
            return redirect('routes:edit', route_id=route.id)
    else:
        form = RouteStopForm()
    
    context = {
        'form': form,
        'route': route,
        'api_key': 'YOUR_GOOGLE_MAPS_API_KEY',  # Substituir pela chave real
    }
    
    return render(request, 'routes/stop_add.html', context)

@login_required
def route_stop_edit_view(request, stop_id):
    """
    Edita uma parada de uma rota.
    """
    stop = get_object_or_404(RouteStop, id=stop_id, route__driver=request.user)
    
    if request.method == 'POST':
        form = RouteStopForm(request.POST, instance=stop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Parada atualizada com sucesso!')
            return redirect('routes:edit', route_id=stop.route.id)
    else:
        form = RouteStopForm(instance=stop)
    
    context = {
        'form': form,
        'stop': stop,
        'route': stop.route,
        'api_key': 'YOUR_GOOGLE_MAPS_API_KEY',  # Substituir pela chave real
    }
    
    return render(request, 'routes/stop_edit.html', context)

@login_required
def route_stop_delete_view(request, stop_id):
    """
    Exclui uma parada de uma rota.
    """
    stop = get_object_or_404(RouteStop, id=stop_id, route__driver=request.user)
    route_id = stop.route.id
    
    if request.method == 'POST':
        stop.delete()
        messages.success(request, 'Parada excluída com sucesso!')
        return redirect('routes:edit', route_id=route_id)
    
    context = {
        'stop': stop,
        'route': stop.route,
    }
    
    return render(request, 'routes/stop_delete.html', context)

@login_required
def route_image_add_view(request, route_id):
    """
    Adiciona uma imagem a uma rota.
    """
    route = get_object_or_404(Route, id=route_id, driver=request.user)
    
    if request.method == 'POST':
        form = RouteImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.route = route
            
            # Definir ordem
            last_image = RouteImage.objects.filter(route=route).order_by('-order').first()
            image.order = (last_image.order + 1) if last_image else 1
            
            image.save()
            messages.success(request, 'Imagem adicionada com sucesso!')
            return redirect('routes:edit', route_id=route.id)
    else:
        form = RouteImageForm()
    
    context = {
        'form': form,
        'route': route,
    }
    
    return render(request, 'routes/image_add.html', context)

@login_required
def route_image_delete_view(request, image_id):
    """
    Exclui uma imagem de uma rota.
    """
    image = get_object_or_404(RouteImage, id=image_id, route__driver=request.user)
    route_id = image.route.id
    
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Imagem excluída com sucesso!')
        return redirect('routes:edit', route_id=route_id)
    
    context = {
        'image': image,
        'route': image.route,
    }
    
    return render(request, 'routes/image_delete.html', context)

def route_map_view(request, route_id):
    """
    Exibe o mapa de uma rota específica.
    """
    route = get_object_or_404(Route, id=route_id, is_active=True)
    
    # Obter paradas
    stops = RouteStop.objects.filter(route=route).order_by('order')
    
    # Dados para o mapa
    map_data = route.get_map_data()
    
    # Adicionar paradas ao mapa
    map_data['stops'] = [
        {
            'name': stop.name,
            'description': stop.description,
            'lat': float(stop.latitude),
            'lng': float(stop.longitude),
            'duration': stop.duration_minutes
        } for stop in stops
    ]
    
    context = {
        'route': route,
        'stops': stops,
        'map_data': json.dumps(map_data),
        'api_key': 'YOUR_GOOGLE_MAPS_API_KEY',  # Substituir pela chave real
    }
    
    return render(request, 'routes/map.html', context)
