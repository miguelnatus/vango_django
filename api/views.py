from rest_framework import viewsets, generics, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from accounts.models import User
from vehicles.models import Vehicle
from routes.models import Route, RouteSchedule
from bookings.models import Booking
from reviews.models import Review
from .serializers import (
    UserSerializer, VehicleSerializer, RouteSerializer, 
    RouteScheduleSerializer, BookingSerializer, ReviewSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user_type', 'is_verified']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['vehicle_type', 'is_verified', 'is_active', 'driver']
    search_fields = ['model', 'license_plate']

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['route_type', 'is_active', 'is_featured', 'driver', 'vehicle']
    search_fields = ['title', 'description', 'origin', 'destination']

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'passenger', 'route', 'booking_date']
    search_fields = ['booking_reference']

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['passenger', 'driver', 'route', 'rating']

# Views personalizadas
class RouteSearchAPIView(generics.ListAPIView):
    """
    API para busca avançada de rotas com filtros específicos.
    """
    serializer_class = RouteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    def get_queryset(self):
        queryset = Route.objects.filter(is_active=True)
        
        origin = self.request.query_params.get('origin', None)
        destination = self.request.query_params.get('destination', None)
        date = self.request.query_params.get('date', None)
        passengers = self.request.query_params.get('passengers', None)
        
        if origin:
            queryset = queryset.filter(origin__icontains=origin)
        if destination:
            queryset = queryset.filter(destination__icontains=destination)
        if passengers:
            queryset = queryset.filter(vehicle__capacity__gte=int(passengers))
            
        # Filtrar por disponibilidade na data
        if date:
            # Lógica para verificar disponibilidade na data específica
            pass
            
        return queryset

class RouteScheduleListAPIView(generics.ListAPIView):
    """
    API para listar horários disponíveis para uma rota específica.
    """
    serializer_class = RouteScheduleSerializer
    
    def get_queryset(self):
        route_id = self.kwargs['route_id']
        return RouteSchedule.objects.filter(route_id=route_id)

class RouteReviewsAPIView(generics.ListAPIView):
    """
    API para listar avaliações de uma rota específica.
    """
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        route_id = self.kwargs['route_id']
        return Review.objects.filter(route_id=route_id)

class DriverRoutesAPIView(generics.ListAPIView):
    """
    API para listar rotas de um motorista específico.
    """
    serializer_class = RouteSerializer
    
    def get_queryset(self):
        driver_id = self.kwargs['driver_id']
        return Route.objects.filter(driver_id=driver_id, is_active=True)

class DriverReviewsAPIView(generics.ListAPIView):
    """
    API para listar avaliações de um motorista específico.
    """
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        driver_id = self.kwargs['driver_id']
        return Review.objects.filter(driver_id=driver_id)

class PassengerBookingsAPIView(generics.ListAPIView):
    """
    API para listar reservas de um passageiro específico.
    """
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        passenger_id = self.kwargs['passenger_id']
        return Booking.objects.filter(passenger_id=passenger_id)
