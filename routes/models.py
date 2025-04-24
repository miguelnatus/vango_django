from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from vehicles.models import Vehicle

class Route(models.Model):
    """
    Modelo para armazenar rotas turísticas oferecidas pelos motoristas.
    """
    ROUTE_TYPE_CHOICES = (
        ('airport_transfer', _('Transfer Aeroporto')),
        ('city_tour', _('City Tour')),
        ('intercity', _('Intermunicipal')),
        ('custom', _('Personalizada')),
    )
    
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='routes',
        verbose_name=_('Motorista')
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='routes',
        verbose_name=_('Veículo')
    )
    route_type = models.CharField(
        max_length=20,
        choices=ROUTE_TYPE_CHOICES,
        verbose_name=_('Tipo de Rota')
    )
    title = models.CharField(max_length=100, verbose_name=_('Título'))
    description = models.TextField(verbose_name=_('Descrição'))
    
    # Origem e destino
    origin = models.CharField(max_length=100, verbose_name=_('Origem'))
    destination = models.CharField(max_length=100, verbose_name=_('Destino'))
    
    # Coordenadas para mapa (opcional)
    origin_latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name=_('Latitude de Origem')
    )
    origin_longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name=_('Longitude de Origem')
    )
    destination_latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name=_('Latitude de Destino')
    )
    destination_longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name=_('Longitude de Destino')
    )
    
    # Detalhes da rota
    distance = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        verbose_name=_('Distância (km)')
    )
    duration = models.PositiveIntegerField(
        verbose_name=_('Duração (minutos)')
    )
    price = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name=_('Preço por pessoa (R$)')
    )
    
    # Status da rota
    is_active = models.BooleanField(default=True, verbose_name=_('Ativa'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Destacada'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criada em'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizada em'))
    
    class Meta:
        verbose_name = _('Rota')
        verbose_name_plural = _('Rotas')
    
    def __str__(self):
        return f"{self.title} ({self.origin} → {self.destination})"


class RouteSchedule(models.Model):
    """
    Modelo para armazenar horários disponíveis para cada rota.
    """
    WEEKDAY_CHOICES = (
        (0, _('Segunda-feira')),
        (1, _('Terça-feira')),
        (2, _('Quarta-feira')),
        (3, _('Quinta-feira')),
        (4, _('Sexta-feira')),
        (5, _('Sábado')),
        (6, _('Domingo')),
    )
    
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name=_('Rota')
    )
    weekday = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        verbose_name=_('Dia da Semana')
    )
    departure_time = models.TimeField(verbose_name=_('Horário de Partida'))
    
    class Meta:
        verbose_name = _('Horário de Rota')
        verbose_name_plural = _('Horários de Rota')
        ordering = ['weekday', 'departure_time']
        unique_together = ['route', 'weekday', 'departure_time']
    
    def __str__(self):
        return f"{self.route.title} - {self.get_weekday_display()} {self.departure_time}"


class RouteStop(models.Model):
    """
    Modelo para armazenar paradas intermediárias em uma rota.
    """
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='stops',
        verbose_name=_('Rota')
    )
    name = models.CharField(max_length=100, verbose_name=_('Nome'))
    description = models.TextField(blank=True, verbose_name=_('Descrição'))
    order = models.PositiveIntegerField(verbose_name=_('Ordem'))
    
    # Coordenadas para mapa (opcional)
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name=_('Latitude')
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name=_('Longitude')
    )
    
    # Duração da parada
    duration = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Duração (minutos)')
    )
    
    class Meta:
        verbose_name = _('Parada')
        verbose_name_plural = _('Paradas')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name} (Parada {self.order} de {self.route.title})"
