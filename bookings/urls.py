from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list_view, name='list'),
    path('<int:booking_id>/', views.booking_detail_view, name='detail'),
    path('create/<int:route_id>/', views.booking_create_view, name='create'),
    path('<int:booking_id>/cancel/', views.booking_cancel_view, name='cancel'),
    path('<int:booking_id>/update-status/', views.booking_update_status_view, name='update_status'),
    path('driver/', views.driver_booking_list_view, name='driver_list'),
]
