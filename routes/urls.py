from django.urls import path
from . import views

app_name = 'routes'

urlpatterns = [
    path('', views.route_list_view, name='list'),
    path('search/', views.route_search_view, name='search'),
    path('<int:route_id>/', views.route_detail_view, name='detail'),
    path('create/', views.route_create_view, name='create'),
    path('<int:route_id>/edit/', views.route_edit_view, name='edit'),
    path('driver/', views.driver_routes_view, name='driver_routes'),
]
