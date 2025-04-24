from django.db import models
from django.utils import timezone
from accounts.models import User
from routes.models import Route

class Payment(models.Model):
    """
    Modelo para pagamentos.
    """
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('approved', 'Aprovado'),
        ('declined', 'Recusado'),
        ('refunded', 'Reembolsado'),
        ('cancelled', 'Cancelado'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('bank_slip', 'Boleto Bancário'),
        ('bank_transfer', 'Transferência Bancária'),
        ('wallet', 'Carteira Digital'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # Informações de pagamento
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_response = models.JSONField(blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    
    # Informações de cartão (armazenadas de forma segura)
    card_last_digits = models.CharField(max_length=4, blank=True, null=True)
    card_brand = models.CharField(max_length=20, blank=True, null=True)
    
    # Informações de boleto
    bank_slip_url = models.URLField(blank=True, null=True)
    bank_slip_expiration = models.DateTimeField(blank=True, null=True)
    
    # Informações de PIX
    pix_qr_code = models.TextField(blank=True, null=True)
    pix_expiration = models.DateTimeField(blank=True, null=True)
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pagamento {self.id} - {self.get_status_display()}"
    
    @property
    def is_paid(self):
        return self.status == 'approved'
    
    @property
    def is_pending(self):
        return self.status == 'pending' or self.status == 'processing'
    
    @property
    def is_failed(self):
        return self.status == 'declined' or self.status == 'cancelled'
    
    @property
    def is_refunded(self):
        return self.status == 'refunded'
    
    @property
    def is_expired(self):
        if self.payment_method == 'bank_slip' and self.bank_slip_expiration:
            return timezone.now() > self.bank_slip_expiration
        elif self.payment_method == 'pix' and self.pix_expiration:
            return timezone.now() > self.pix_expiration
        return False
    
    def approve(self, transaction_id=None, gateway_response=None):
        """
        Marca o pagamento como aprovado.
        """
        self.status = 'approved'
        self.payment_date = timezone.now()
        
        if transaction_id:
            self.transaction_id = transaction_id
        
        if gateway_response:
            self.gateway_response = gateway_response
        
        self.save()
        
        # Atualizar status da reserva
        self.booking.confirm()
    
    def decline(self, gateway_response=None):
        """
        Marca o pagamento como recusado.
        """
        self.status = 'declined'
        
        if gateway_response:
            self.gateway_response = gateway_response
        
        self.save()
    
    def refund(self, gateway_response=None):
        """
        Marca o pagamento como reembolsado.
        """
        self.status = 'refunded'
        
        if gateway_response:
            self.gateway_response = gateway_response
        
        self.save()
        
        # Atualizar status da reserva
        self.booking.cancel()
    
    def cancel(self):
        """
        Marca o pagamento como cancelado.
        """
        self.status = 'cancelled'
        self.save()
        
        # Atualizar status da reserva
        self.booking.cancel()

class PaymentMethod(models.Model):
    """
    Modelo para métodos de pagamento salvos pelo usuário.
    """
    TYPE_CHOICES = (
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('bank_account', 'Conta Bancária'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_default = models.BooleanField(default=False)
    
    # Informações de cartão (armazenadas de forma segura)
    card_token = models.CharField(max_length=100, blank=True, null=True)
    card_last_digits = models.CharField(max_length=4, blank=True, null=True)
    card_brand = models.CharField(max_length=20, blank=True, null=True)
    card_holder_name = models.CharField(max_length=100, blank=True, null=True)
    card_expiry_month = models.CharField(max_length=2, blank=True, null=True)
    card_expiry_year = models.CharField(max_length=4, blank=True, null=True)
    
    # Informações de conta bancária
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    bank_branch_number = models.CharField(max_length=10, blank=True, null=True)
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.type in ['credit_card', 'debit_card']:
            return f"{self.get_type_display()} - {self.card_brand} **** {self.card_last_digits}"
        else:
            return f"{self.get_type_display()} - {self.bank_name}"
    
    def save(self, *args, **kwargs):
        # Se este método de pagamento for definido como padrão,
        # remover o status de padrão de outros métodos do mesmo usuário
        if self.is_default:
            PaymentMethod.objects.filter(user=self.user, is_default=True).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        if self.type in ['credit_card', 'debit_card'] and self.card_expiry_month and self.card_expiry_year:
            now = timezone.now()
            expiry_date = timezone.datetime(
                year=int(self.card_expiry_year),
                month=int(self.card_expiry_month),
                day=1
            )
            # Cartão expira no último dia do mês
            if expiry_date.month == 12:
                expiry_date = expiry_date.replace(year=expiry_date.year + 1, month=1)
            else:
                expiry_date = expiry_date.replace(month=expiry_date.month + 1)
            expiry_date = expiry_date - timezone.timedelta(days=1)
            
            return now.date() > expiry_date.date()
        return False

class Coupon(models.Model):
    """
    Modelo para cupons de desconto.
    """
    TYPE_CHOICES = (
        ('percentage', 'Porcentagem'),
        ('fixed', 'Valor Fixo'),
    )
    
    code = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Restrições
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    usage_limit = models.IntegerField(blank=True, null=True)
    usage_count = models.IntegerField(default=0)
    
    # Restrições de usuário
    is_first_purchase_only = models.BooleanField(default=False)
    
    # Restrições de rota
    applicable_routes = models.ManyToManyField(Route, blank=True, related_name='coupons')
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-valid_until']
    
    def __str__(self):
        return f"{self.code} - {self.description}"
    
    @property
    def is_valid(self):
        now = timezone.now()
        
        if now < self.valid_from or now > self.valid_until:
            return False
        
        if self.usage_limit is not None and self.usage_count >= self.usage_limit:
            return False
        
        return True
    
    def calculate_discount(self, amount):
        """
        Calcula o valor do desconto para um determinado valor.
        """
        if not self.is_valid:
            return 0
        
        if amount < self.min_purchase:
            return 0
        
        if self.type == 'percentage':
            discount = amount * (self.value / 100)
        else:  # fixed
            discount = self.value
        
        # Limitar ao valor máximo de desconto, se definido
        if self.max_discount is not None and discount > self.max_discount:
            discount = self.max_discount
        
        # Não permitir desconto maior que o valor da compra
        if discount > amount:
            discount = amount
        
        return discount
    
    def use(self):
        """
        Incrementa o contador de uso do cupom.
        """
        self.usage_count += 1
        self.save()

class CouponUsage(models.Model):
    """
    Modelo para registrar o uso de cupons.
    """
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='coupon_usage')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('coupon', 'booking')
        ordering = ['-used_at']
    
    def __str__(self):
        return f"{self.coupon.code} usado por {self.user.username} em {self.used_at}"
