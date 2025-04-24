from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from routes.models import Route, RouteSchedule

class Booking(models.Model):
    """
    Modelo para armazenar reservas de rotas feitas pelos passageiros.
    """
    STATUS_CHOICES = (
        ('pending', _('Pendente')),
        ('confirmed', _('Confirmada')),
        ('cancelled', _('Cancelada')),
        ('completed', _('Concluída')),
    )
    
    passenger = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('Passageiro')
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('Rota')
    )
    schedule = models.ForeignKey(
        RouteSchedule,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('Horário')
    )
    
    # Detalhes da reserva
    booking_date = models.DateField(verbose_name=_('Data da Viagem'))
    num_passengers = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Número de Passageiros')
    )
    total_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_('Preço Total (R$)')
    )
    
    # Status e rastreamento
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    booking_reference = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_('Referência da Reserva')
    )
    
    # Informações adicionais
    special_requests = models.TextField(
        blank=True,
        verbose_name=_('Solicitações Especiais')
    )
    pickup_location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Local de Embarque')
    )
    dropoff_location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Local de Desembarque')
    )
    
    # Datas de controle
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Criada em')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Atualizada em')
    )
    
    class Meta:
        verbose_name = _('Reserva')
        verbose_name_plural = _('Reservas')
        ordering = ['-booking_date', '-created_at']
    
    def __str__(self):
        return f"Reserva {self.booking_reference} - {self.passenger.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Gerar referência de reserva se não existir
        if not self.booking_reference:
            import random
            import string
            chars = string.ascii_uppercase + string.digits
            self.booking_reference = ''.join(random.choice(chars) for _ in range(8))
        
        # Calcular preço total se não definido
        if not self.total_price:
            self.total_price = self.route.price * self.num_passengers
            
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Modelo para armazenar informações de pagamento das reservas.
    """
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', _('Cartão de Crédito')),
        ('debit_card', _('Cartão de Débito')),
        ('pix', _('PIX')),
        ('bank_transfer', _('Transferência Bancária')),
        ('cash', _('Dinheiro')),
    )
    
    STATUS_CHOICES = (
        ('pending', _('Pendente')),
        ('processing', _('Processando')),
        ('completed', _('Concluído')),
        ('failed', _('Falhou')),
        ('refunded', _('Reembolsado')),
    )
    
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name=_('Reserva')
    )
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_('Valor (R$)')
    )
    payment_method = models.CharField(
        max_length=15,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name=_('Método de Pagamento')
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    # Informações de transação
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('ID da Transação')
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Data do Pagamento')
    )
    
    # Datas de controle
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Criado em')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Atualizado em')
    )
    
    class Meta:
        verbose_name = _('Pagamento')
        verbose_name_plural = _('Pagamentos')
    
    def __str__(self):
        return f"Pagamento {self.id} - Reserva {self.booking.booking_reference}"
