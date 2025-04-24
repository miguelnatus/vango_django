from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class User(AbstractUser):
    """
    Modelo de usuário personalizado com campos adicionais.
    """
    USER_TYPE_CHOICES = (
        ('passenger', 'Passageiro'),
        ('driver', 'Motorista'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='passenger')
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Campos específicos para motoristas
    cnh = models.CharField(max_length=20, blank=True, null=True)
    cnh_expiration = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Campos para verificação de e-mail
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)
    
    # Campos para notificações
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    # Campos para segurança
    login_attempts = models.IntegerField(default=0)
    last_login_attempt = models.DateTimeField(blank=True, null=True)
    account_locked_until = models.DateTimeField(blank=True, null=True)
    
    @property
    def is_driver(self):
        return self.user_type == 'driver'
    
    @property
    def is_passenger(self):
        return self.user_type == 'passenger'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def account_locked(self):
        if self.account_locked_until and self.account_locked_until > timezone.now():
            return True
        return False
    
    def lock_account(self, minutes=30):
        """
        Bloqueia a conta do usuário por um período de tempo.
        """
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=minutes)
        self.save()
    
    def unlock_account(self):
        """
        Desbloqueia a conta do usuário.
        """
        self.account_locked_until = None
        self.login_attempts = 0
        self.save()
    
    def increment_login_attempts(self):
        """
        Incrementa o contador de tentativas de login.
        """
        self.login_attempts += 1
        self.last_login_attempt = timezone.now()
        
        # Bloquear conta após 5 tentativas falhas
        if self.login_attempts >= 5:
            self.lock_account()
        
        self.save()
    
    def reset_login_attempts(self):
        """
        Reseta o contador de tentativas de login.
        """
        self.login_attempts = 0
        self.save()
    
    def generate_email_verification_token(self):
        """
        Gera um token para verificação de e-mail.
        """
        import uuid
        self.email_verification_token = str(uuid.uuid4())
        self.email_verification_sent_at = timezone.now()
        self.save()
        return self.email_verification_token
    
    def verify_email(self):
        """
        Marca o e-mail como verificado.
        """
        self.email_verified = True
        self.email_verification_token = None
        self.save()

class DriverDocument(models.Model):
    """
    Modelo para documentos de motorista.
    """
    DOCUMENT_TYPE_CHOICES = (
        ('cnh', 'Carteira Nacional de Habilitação'),
        ('vehicle_registration', 'Documento do Veículo'),
        ('insurance', 'Seguro'),
        ('criminal_record', 'Certidão de Antecedentes Criminais'),
        ('other', 'Outro'),
    )
    
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    document_file = models.FileField(upload_to='driver_documents/')
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    rejection_reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.driver.username}"
    
    def verify(self, verified_by):
        """
        Marca o documento como verificado.
        """
        self.is_verified = True
        self.verified_at = timezone.now()
        self.verified_by = verified_by
        self.rejection_reason = None
        self.save()
    
    def reject(self, reason):
        """
        Rejeita o documento com um motivo.
        """
        self.is_verified = False
        self.rejection_reason = reason
        self.save()

class Notification(models.Model):
    """
    Modelo para notificações de usuário.
    """
    NOTIFICATION_TYPE_CHOICES = (
        ('booking_created', 'Nova Reserva'),
        ('booking_confirmed', 'Reserva Confirmada'),
        ('booking_cancelled', 'Reserva Cancelada'),
        ('route_created', 'Nova Rota'),
        ('document_verified', 'Documento Verificado'),
        ('document_rejected', 'Documento Rejeitado'),
        ('review_received', 'Nova Avaliação'),
        ('system', 'Notificação do Sistema'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    related_object_id = models.IntegerField(blank=True, null=True)
    related_object_type = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """
        Marca a notificação como lida.
        """
        self.read = True
        self.read_at = timezone.now()
        self.save()
    
    @classmethod
    def create_notification(cls, user, notification_type, title, message, related_object=None, related_object_type=None):
        """
        Cria uma nova notificação.
        """
        notification = cls(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message
        )
        
        if related_object:
            notification.related_object_id = related_object.id
            notification.related_object_type = related_object_type or related_object.__class__.__name__
        
        notification.save()
        return notification
