from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

class SocialShare(models.Model):
    """
    Modelo para rastrear compartilhamentos em redes sociais.
    """
    PLATFORM_CHOICES = (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('email', 'Email'),
        ('other', 'Outro'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_shares')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    content_type = models.CharField(max_length=20, choices=(
        ('route', 'Rota'),
        ('booking', 'Reserva'),
        ('review', 'Avaliação'),
        ('profile', 'Perfil'),
    ))
    content_id = models.PositiveIntegerField()
    shared_at = models.DateTimeField(auto_now_add=True)
    share_url = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Compartilhamento Social'
        verbose_name_plural = 'Compartilhamentos Sociais'
        ordering = ['-shared_at']
    
    def __str__(self):
        return f"{self.get_platform_display()} - {self.get_content_type_display()} #{self.content_id}"

class SocialAccount(models.Model):
    """
    Modelo para armazenar contas de redes sociais vinculadas.
    """
    PROVIDER_CHOICES = (
        ('facebook', 'Facebook'),
        ('google', 'Google'),
        ('twitter', 'Twitter'),
        ('apple', 'Apple'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_accounts')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_id = models.CharField(max_length=255)
    provider_username = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Conta Social'
        verbose_name_plural = 'Contas Sociais'
        unique_together = ('provider', 'provider_id')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_provider_display()} - {self.provider_username or self.provider_id}"
    
    @property
    def is_token_expired(self):
        if not self.token_expires_at:
            return True
        return self.token_expires_at <= timezone.now()

class SocialPost(models.Model):
    """
    Modelo para armazenar posts em redes sociais.
    """
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('published', 'Publicado'),
        ('failed', 'Falhou'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_posts')
    social_account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='social_posts/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    post_id = models.CharField(max_length=255, blank=True, null=True)
    post_url = models.URLField(blank=True, null=True)
    scheduled_for = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Post Social'
        verbose_name_plural = 'Posts Sociais'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.social_account.get_provider_display()} - {self.content[:50]}"
    
    def publish(self):
        """
        Publica o post na rede social.
        """
        # Implementação depende da API de cada rede social
        # Aqui seria chamada a função específica para cada provedor
        
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()
        
        return True

class SocialReferral(models.Model):
    """
    Modelo para rastrear referências de redes sociais.
    """
    PLATFORM_CHOICES = (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('email', 'Email'),
        ('other', 'Outro'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referred_by')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    referral_code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    converted_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Referência Social'
        verbose_name_plural = 'Referências Sociais'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} -> {self.referred_user.get_full_name()} via {self.get_platform_display()}"
    
    def convert(self):
        """
        Marca a referência como convertida.
        """
        self.converted_at = timezone.now()
        self.save()
        
        return True
    
    @classmethod
    def generate_referral_code(cls, user):
        """
        Gera um código de referência único para o usuário.
        """
        import random
        import string
        
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not cls.objects.filter(referral_code=code).exists():
                return code
