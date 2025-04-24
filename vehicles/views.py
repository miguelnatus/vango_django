from django.shortcuts import render

# Implementações básicas das views para evitar erros
def vehicle_list_view(request):
    return render(request, 'vehicles/list.html', {})

def vehicle_detail_view(request, vehicle_id):
    return render(request, 'vehicles/detail.html', {})

def vehicle_create_view(request):
    return render(request, 'vehicles/create.html', {})

def vehicle_edit_view(request, vehicle_id):
    return render(request, 'vehicles/edit.html', {})

def vehicle_delete_view(request, vehicle_id):
    return render(request, 'vehicles/delete.html', {})
