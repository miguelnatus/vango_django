from django.db import models
from django.utils.translation import gettext_lazy as _

class CoreSettings(models.Model):
    """
    Modelo para armazenar configurações gerais do aplicativo.
    """
    site_name = models.CharField(max_length=100, default="VanGo", verbose_name=_('Nome do Site'))
    site_description = models.TextField(blank=True, verbose_name=_('Descrição do Site'))
    contact_email = models.EmailField(verbose_name=_('Email de Contato'))
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name=_('Telefone de Contato'))
    
    # Redes sociais
    facebook_url = models.URLField(blank=True, verbose_name=_('URL do Facebook'))
    instagram_url = models.URLField(blank=True, verbose_name=_('URL do Instagram'))
    twitter_url = models.URLField(blank=True, verbose_name=_('URL do Twitter'))
    
    # SEO
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name=_('Meta Keywords'))
    meta_description = models.TextField(blank=True, verbose_name=_('Meta Description'))
    
    # Configurações de comissão
    passenger_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        verbose_name=_('Percentual de Taxa para Passageiros (%)')
    )
    driver_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=15.00,
        verbose_name=_('Percentual de Taxa para Motoristas (%)')
    )
    
    # Configurações de cancelamento
    cancellation_policy = models.TextField(blank=True, verbose_name=_('Política de Cancelamento'))
    
    # Termos e políticas
    terms_and_conditions = models.TextField(blank=True, verbose_name=_('Termos e Condições'))
    privacy_policy = models.TextField(blank=True, verbose_name=_('Política de Privacidade'))
    
    # Logo e favicon
    logo = models.ImageField(
        upload_to='core/',
        blank=True,
        null=True,
        verbose_name=_('Logo')
    )
    favicon = models.ImageField(
        upload_to='core/',
        blank=True,
        null=True,
        verbose_name=_('Favicon')
    )
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizado em'))
    
    class Meta:
        verbose_name = _('Configuração do Sistema')
        verbose_name_plural = _('Configurações do Sistema')
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        # Garantir que só exista uma instância deste modelo
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Retorna a instância única de configurações ou cria uma nova se não existir."""
        settings, created = cls.objects.get_or_create(
            defaults={
                'site_name': 'VanGo',
                'contact_email': 'contato@vango.com.br',
            }
        )
        return settings


class FAQ(models.Model):
    """
    Modelo para armazenar perguntas frequentes.
    """
    CATEGORY_CHOICES = (
        ('general', _('Geral')),
        ('booking', _('Reservas')),
        ('payment', _('Pagamentos')),
        ('routes', _('Rotas')),
        ('drivers', _('Motoristas')),
    )
    
    question = models.CharField(max_length=255, verbose_name=_('Pergunta'))
    answer = models.TextField(verbose_name=_('Resposta'))
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        verbose_name=_('Categoria')
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Ordem'))
    is_active = models.BooleanField(default=True, verbose_name=_('Ativa'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criada em'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizada em'))
    
    class Meta:
        verbose_name = _('Pergunta Frequente')
        verbose_name_plural = _('Perguntas Frequentes')
        ordering = ['category', 'order']
    
    def __str__(self):
        return self.question
