from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Modelo de usuário personalizado para o VanGo.
    Estende o modelo de usuário padrão do Django.
    """
    USER_TYPE_CHOICES = (
        ('passenger', _('Passageiro')),
        ('driver', _('Motorista')),
        ('admin', _('Administrador')),
    )
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='passenger',
        verbose_name=_('Tipo de Usuário')
    )
    phone = models.CharField(max_length=15, blank=True, verbose_name=_('Telefone'))
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name=_('Foto de Perfil')
    )
    
    # Campos específicos para motoristas
    is_verified = models.BooleanField(default=False, verbose_name=_('Verificado'))
    bio = models.TextField(blank=True, verbose_name=_('Biografia'))
    
    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    @property
    def is_driver(self):
        return self.user_type == 'driver'
    
    @property
    def is_passenger(self):
        return self.user_type == 'passenger'
    
    @property
    def average_rating(self):
        """Retorna a avaliação média do usuário."""
        if self.is_driver:
            from reviews.models import Review
            reviews = Review.objects.filter(driver=self)
            if reviews.exists():
                return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return None


class DriverDocument(models.Model):
    """
    Modelo para armazenar documentos de motoristas.
    """
    DOCUMENT_TYPE_CHOICES = (
        ('cnh', _('CNH')),
        ('vehicle_registration', _('Documento do Veículo')),
        ('tourism_credential', _('Credencial de Turismo')),
        ('insurance', _('Seguro')),
        ('other', _('Outro')),
    )
    
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Motorista')
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name=_('Tipo de Documento')
    )
    document_file = models.FileField(
        upload_to='driver_documents/',
        verbose_name=_('Arquivo')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Verificado')
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Data de Upload')
    )
    
    class Meta:
        verbose_name = _('Documento do Motorista')
        verbose_name_plural = _('Documentos do Motorista')
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.driver.get_full_name()}"
