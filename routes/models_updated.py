from django.db import models
from django.contrib.auth.models import User
from accounts.models import User

class Route(models.Model):
    """
    Modelo para rotas turísticas.
    """
    STATUS_CHOICES = (
        ('active', 'Ativa'),
        ('inactive', 'Inativa'),
        ('cancelled', 'Cancelada'),
    )
    
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routes')
    title = models.CharField(max_length=100)
    description = models.TextField()
    origin_name = models.CharField(max_length=100)
    origin_address = models.CharField(max_length=200)
    origin_latitude = models.DecimalField(max_digits=10, decimal_places=7)
    origin_longitude = models.DecimalField(max_digits=10, decimal_places=7)
    destination_name = models.CharField(max_length=100)
    destination_address = models.CharField(max_length=200)
    destination_latitude = models.DecimalField(max_digits=10, decimal_places=7)
    destination_longitude = models.DecimalField(max_digits=10, decimal_places=7)
    
    # Waypoints para o mapa (pontos intermediários da rota)
    waypoints = models.JSONField(blank=True, null=True)
    
    # Informações da rota
    distance_km = models.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    max_passengers = models.IntegerField()
    
    # Dias e horários disponíveis
    available_days = models.JSONField()  # Lista de dias da semana (0-6)
    departure_time = models.TimeField()
    return_time = models.TimeField(blank=True, null=True)  # Para rotas de ida e volta
    
    # Status e datas
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Atributos da rota
    has_wifi = models.BooleanField(default=False)
    has_air_conditioning = models.BooleanField(default=False)
    has_bathroom = models.BooleanField(default=False)
    has_usb_outlets = models.BooleanField(default=False)
    is_accessible = models.BooleanField(default=False)
    allows_pets = models.BooleanField(default=False)
    
    # Imagens da rota
    cover_image = models.ImageField(upload_to='route_images/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.origin_name} → {self.destination_name})"
    
    @property
    def average_rating(self):
        from reviews.models import Review
        reviews = Review.objects.filter(route=self)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    
    @property
    def reviews_count(self):
        from reviews.models import Review
        return Review.objects.filter(route=self).count()
    
    @property
    def available_seats(self):
        from bookings.models import Booking
        # Implementação futura: calcular assentos disponíveis por data
        return self.max_passengers
    
    def get_map_data(self):
        """
        Retorna os dados necessários para exibir a rota no mapa.
        """
        return {
            'origin': {
                'name': self.origin_name,
                'address': self.origin_address,
                'lat': float(self.origin_latitude),
                'lng': float(self.origin_longitude)
            },
            'destination': {
                'name': self.destination_name,
                'address': self.destination_address,
                'lat': float(self.destination_latitude),
                'lng': float(self.destination_longitude)
            },
            'waypoints': self.waypoints or [],
            'distance_km': float(self.distance_km),
            'duration_minutes': self.duration_minutes
        }

class RouteImage(models.Model):
    """
    Modelo para imagens adicionais da rota.
    """
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='route_images/')
    caption = models.CharField(max_length=100, blank=True, null=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Imagem {self.order} - {self.route.title}"

class RouteStop(models.Model):
    """
    Modelo para paradas da rota (pontos turísticos, paradas para refeições, etc.).
    """
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    duration_minutes = models.IntegerField(default=0)  # Tempo de parada
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name} - {self.route.title}"
