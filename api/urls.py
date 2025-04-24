from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'vehicles', views.VehicleViewSet)
router.register(r'routes', views.RouteViewSet)
router.register(r'bookings', views.BookingViewSet)
router.register(r'reviews', views.ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    # Endpoints personalizados
    path('routes/search/', views.RouteSearchAPIView.as_view(), name='route-search'),
    path('routes/<int:route_id>/schedules/', views.RouteScheduleListAPIView.as_view(), name='route-schedules'),
    path('routes/<int:route_id>/reviews/', views.RouteReviewsAPIView.as_view(), name='route-reviews'),
    path('drivers/<int:driver_id>/routes/', views.DriverRoutesAPIView.as_view(), name='driver-routes'),
    path('drivers/<int:driver_id>/reviews/', views.DriverReviewsAPIView.as_view(), name='driver-reviews'),
    path('passengers/<int:passenger_id>/bookings/', views.PassengerBookingsAPIView.as_view(), name='passenger-bookings'),
]
