from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from routes.models import Route
from bookings.models import Booking

class Review(models.Model):
    """
    Modelo para armazenar avaliações de rotas e motoristas.
    """
    RATING_CHOICES = (
        (1, '1 - Péssimo'),
        (2, '2 - Ruim'),
        (3, '3 - Regular'),
        (4, '4 - Bom'),
        (5, '5 - Excelente'),
    )
    
    passenger = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        verbose_name=_('Passageiro')
    )
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_received',
        verbose_name=_('Motorista')
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Rota')
    )
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name=_('Reserva')
    )
    
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        verbose_name=_('Avaliação')
    )
    comment = models.TextField(
        blank=True,
        verbose_name=_('Comentário')
    )
    
    # Avaliações específicas
    punctuality_rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        verbose_name=_('Pontualidade')
    )
    vehicle_rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        verbose_name=_('Veículo')
    )
    driver_rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        verbose_name=_('Motorista')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Criada em')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Atualizada em')
    )
    
    class Meta:
        verbose_name = _('Avaliação')
        verbose_name_plural = _('Avaliações')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Avaliação de {self.passenger.get_full_name()} para {self.driver.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Calcular a avaliação geral com base nas avaliações específicas
        if not self.rating:
            self.rating = round((self.punctuality_rating + self.vehicle_rating + self.driver_rating) / 3)
        super().save(*args, **kwargs)
