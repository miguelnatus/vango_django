from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    path('', views.vehicle_list_view, name='list'),
    path('<int:vehicle_id>/', views.vehicle_detail_view, name='detail'),
    path('create/', views.vehicle_create_view, name='create'),
    path('<int:vehicle_id>/edit/', views.vehicle_edit_view, name='edit'),
    path('<int:vehicle_id>/delete/', views.vehicle_delete_view, name='delete'),
]
