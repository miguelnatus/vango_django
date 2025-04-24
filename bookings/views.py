from django.shortcuts import render

# Implementações básicas das views para evitar erros
def booking_list_view(request):
    return render(request, 'bookings/list.html', {})

def booking_detail_view(request, booking_id):
    return render(request, 'bookings/detail.html', {})

def booking_create_view(request, route_id):
    return render(request, 'bookings/create.html', {})

def booking_cancel_view(request, booking_id):
    return render(request, 'bookings/cancel.html', {})

def booking_update_status_view(request, booking_id):
    return render(request, 'bookings/update_status.html', {})

def driver_booking_list_view(request):
    return render(request, 'bookings/driver_list.html', {})
