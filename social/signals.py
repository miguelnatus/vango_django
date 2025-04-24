from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import SocialReferral, SocialPost

User = get_user_model()

@receiver(post_save, sender=SocialPost)
def publish_scheduled_post(sender, instance, created, **kwargs):
    """
    Publica posts agendados quando chegar o momento.
    Em um ambiente de produção, isso seria feito por um job agendado.
    """
    if not created:
        return
    
    # Se o post estiver agendado e o horário já passou, publicar
    if instance.status == 'pending' and instance.scheduled_for and instance.scheduled_for <= timezone.now():
        instance.publish()

@receiver(post_save, sender=User)
def check_referral_code(sender, instance, created, **kwargs):
    """
    Verifica se o usuário tem um código de referência.
    """
    if not created:
        return
    
    # Verificar se o usuário já tem um código de referência
    if not SocialReferral.objects.filter(user=instance).exists():
        # Criar um novo código de referência
        referral_code = SocialReferral.generate_referral_code(instance)
        
        # Criar uma nova referência
        SocialReferral.objects.create(
            user=instance,
            platform='other',
            referral_code=referral_code
        )
