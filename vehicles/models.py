from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User

class Vehicle(models.Model):
    """
    Modelo para armazenar informações sobre os veículos (vans).
    """
    VEHICLE_TYPE_CHOICES = (
        ('van', _('Van')),
        ('minibus', _('Micro-ônibus')),
        ('executive', _('Van Executiva')),
    )
    
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vehicles',
        verbose_name=_('Motorista')
    )
    vehicle_type = models.CharField(
        max_length=10,
        choices=VEHICLE_TYPE_CHOICES,
        default='van',
        verbose_name=_('Tipo de Veículo')
    )
    model = models.CharField(max_length=100, verbose_name=_('Modelo'))
    year = models.PositiveIntegerField(verbose_name=_('Ano'))
    license_plate = models.CharField(max_length=10, verbose_name=_('Placa'))
    capacity = models.PositiveIntegerField(verbose_name=_('Capacidade de Passageiros'))
    
    # Características do veículo
    has_air_conditioning = models.BooleanField(default=True, verbose_name=_('Ar Condicionado'))
    has_wifi = models.BooleanField(default=False, verbose_name=_('Wi-Fi'))
    has_usb_ports = models.BooleanField(default=False, verbose_name=_('Portas USB'))
    has_tv = models.BooleanField(default=False, verbose_name=_('TV'))
    has_accessibility = models.BooleanField(default=False, verbose_name=_('Acessibilidade'))
    
    # Verificação e status
    is_verified = models.BooleanField(default=False, verbose_name=_('Verificado'))
    is_active = models.BooleanField(default=True, verbose_name=_('Ativo'))
    
    # Imagens
    main_image = models.ImageField(
        upload_to='vehicle_images/',
        blank=True,
        null=True,
        verbose_name=_('Imagem Principal')
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criado em'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizado em'))
    
    class Meta:
        verbose_name = _('Veículo')
        verbose_name_plural = _('Veículos')
    
    def __str__(self):
        return f"{self.model} ({self.license_plate}) - {self.driver.get_full_name()}"


class VehicleImage(models.Model):
    """
    Modelo para armazenar imagens adicionais dos veículos.
    """
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Veículo')
    )
    image = models.ImageField(
        upload_to='vehicle_images/',
        verbose_name=_('Imagem')
    )
    caption = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Legenda')
    )
    
    class Meta:
        verbose_name = _('Imagem do Veículo')
        verbose_name_plural = _('Imagens do Veículo')
    
    def __str__(self):
        return f"Imagem de {self.vehicle}"
