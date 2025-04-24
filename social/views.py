from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.db import transaction

from .models import SocialShare, SocialAccount, SocialPost, SocialReferral
from routes.models import Route
from bookings.models import Booking
from reviews.models import Review
from .forms import SocialShareForm, SocialAccountConnectForm, SocialPostForm

import json
import uuid
import requests
from urllib.parse import quote

# Configurações de redes sociais (em produção, use variáveis de ambiente)
FACEBOOK_APP_ID = getattr(settings, 'FACEBOOK_APP_ID', '123456789')
FACEBOOK_APP_SECRET = getattr(settings, 'FACEBOOK_APP_SECRET', 'app_secret')
TWITTER_API_KEY = getattr(settings, 'TWITTER_API_KEY', 'api_key')
TWITTER_API_SECRET = getattr(settings, 'TWITTER_API_SECRET', 'api_secret')

@login_required
def social_accounts_list(request):
    """
    Lista as contas de redes sociais vinculadas do usuário.
    """
    social_accounts = SocialAccount.objects.filter(user=request.user)
    
    return render(request, 'social/social_accounts_list.html', {
        'social_accounts': social_accounts
    })

@login_required
def social_account_connect(request, provider):
    """
    Conecta uma conta de rede social.
    """
    if provider not in [choice[0] for choice in SocialAccount.PROVIDER_CHOICES]:
        messages.error(request, "Provedor de rede social inválido.")
        return redirect('social:social_accounts_list')
    
    if request.method == 'POST':
        form = SocialAccountConnectForm(request.POST)
        if form.is_valid():
            # Em produção, use OAuth para autenticação segura
            # Aqui estamos simulando a conexão
            
            social_account = SocialAccount(
                user=request.user,
                provider=provider,
                provider_id=f"id_{uuid.uuid4().hex[:10]}",
                provider_username=form.cleaned_data.get('username'),
                access_token=f"token_{uuid.uuid4().hex}",
                token_expires_at=timezone.now() + timezone.timedelta(days=60)
            )
            social_account.save()
            
            messages.success(request, f"Conta {social_account.get_provider_display()} conectada com sucesso!")
            return redirect('social:social_accounts_list')
    else:
        form = SocialAccountConnectForm()
    
    return render(request, 'social/social_account_connect.html', {
        'form': form,
        'provider': provider,
        'provider_display': dict(SocialAccount.PROVIDER_CHOICES)[provider]
    })

@login_required
def social_account_disconnect(request, account_id):
    """
    Desconecta uma conta de rede social.
    """
    social_account = get_object_or_404(SocialAccount, id=account_id, user=request.user)
    
    if request.method == 'POST':
        # Em produção, revogue o token de acesso na API do provedor
        social_account.delete()
        messages.success(request, f"Conta {social_account.get_provider_display()} desconectada com sucesso!")
        return redirect('social:social_accounts_list')
    
    return render(request, 'social/social_account_disconnect.html', {
        'social_account': social_account
    })

@login_required
def share_route(request, route_id):
    """
    Compartilha uma rota em redes sociais.
    """
    route = get_object_or_404(Route, id=route_id)
    
    if request.method == 'POST':
        form = SocialShareForm(request.POST)
        if form.is_valid():
            platform = form.cleaned_data.get('platform')
            
            # Criar registro de compartilhamento
            share = SocialShare(
                user=request.user,
                platform=platform,
                content_type='route',
                content_id=route.id
            )
            
            # Gerar URL de compartilhamento
            route_url = request.build_absolute_uri(reverse('routes:detail', args=[route.id]))
            share_text = f"Confira esta rota incrível de {route.origin} para {route.destination} com a VanGo! #VanGo #Turismo"
            
            if platform == 'facebook':
                share.share_url = f"https://www.facebook.com/sharer/sharer.php?u={quote(route_url)}&quote={quote(share_text)}"
            elif platform == 'twitter':
                share.share_url = f"https://twitter.com/intent/tweet?url={quote(route_url)}&text={quote(share_text)}"
            elif platform == 'whatsapp':
                share.share_url = f"https://api.whatsapp.com/send?text={quote(share_text + ' ' + route_url)}"
            elif platform == 'telegram':
                share.share_url = f"https://t.me/share/url?url={quote(route_url)}&text={quote(share_text)}"
            elif platform == 'linkedin':
                share.share_url = f"https://www.linkedin.com/sharing/share-offsite/?url={quote(route_url)}"
            elif platform == 'email':
                share.share_url = f"mailto:?subject={quote('Confira esta rota turística!')}&body={quote(share_text + ' ' + route_url)}"
            
            share.save()
            
            # Retornar URL de compartilhamento
            return JsonResponse({
                'success': True,
                'share_url': share.share_url
            })
    else:
        form = SocialShareForm()
    
    return render(request, 'social/share_route.html', {
        'form': form,
        'route': route
    })

@login_required
def share_booking(request, booking_id):
    """
    Compartilha uma reserva em redes sociais.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        form = SocialShareForm(request.POST)
        if form.is_valid():
            platform = form.cleaned_data.get('platform')
            
            # Criar registro de compartilhamento
            share = SocialShare(
                user=request.user,
                platform=platform,
                content_type='booking',
                content_id=booking.id
            )
            
            # Gerar URL de compartilhamento
            route_url = request.build_absolute_uri(reverse('routes:detail', args=[booking.route.id]))
            share_text = f"Acabei de reservar uma viagem de {booking.route.origin} para {booking.route.destination} com a VanGo! #VanGo #Turismo"
            
            if platform == 'facebook':
                share.share_url = f"https://www.facebook.com/sharer/sharer.php?u={quote(route_url)}&quote={quote(share_text)}"
            elif platform == 'twitter':
                share.share_url = f"https://twitter.com/intent/tweet?url={quote(route_url)}&text={quote(share_text)}"
            elif platform == 'whatsapp':
                share.share_url = f"https://api.whatsapp.com/send?text={quote(share_text + ' ' + route_url)}"
            elif platform == 'telegram':
                share.share_url = f"https://t.me/share/url?url={quote(route_url)}&text={quote(share_text)}"
            elif platform == 'linkedin':
                share.share_url = f"https://www.linkedin.com/sharing/share-offsite/?url={quote(route_url)}"
            elif platform == 'email':
                share.share_url = f"mailto:?subject={quote('Minha viagem com VanGo!')}&body={quote(share_text + ' ' + route_url)}"
            
            share.save()
            
            # Retornar URL de compartilhamento
            return JsonResponse({
                'success': True,
                'share_url': share.share_url
            })
    else:
        form = SocialShareForm()
    
    return render(request, 'social/share_booking.html', {
        'form': form,
        'booking': booking
    })

@login_required
def share_review(request, review_id):
    """
    Compartilha uma avaliação em redes sociais.
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = SocialShareForm(request.POST)
        if form.is_valid():
            platform = form.cleaned_data.get('platform')
            
            # Criar registro de compartilhamento
            share = SocialShare(
                user=request.user,
                platform=platform,
                content_type='review',
                content_id=review.id
            )
            
            # Gerar URL de compartilhamento
            route_url = request.build_absolute_uri(reverse('routes:detail', args=[review.booking.route.id]))
            share_text = f"Dei {review.rating} estrelas para minha viagem de {review.booking.route.origin} para {review.booking.route.destination} com a VanGo! #VanGo #Turismo"
            
            if platform == 'facebook':
                share.share_url = f"https://www.facebook.com/sharer/sharer.php?u={quote(route_url)}&quote={quote(share_text)}"
            elif platform == 'twitter':
                share.share_url = f"https://twitter.com/intent/tweet?url={quote(route_url)}&text={quote(share_text)}"
            elif platform == 'whatsapp':
                share.share_url = f"https://api.whatsapp.com/send?text={quote(share_text + ' ' + route_url)}"
            elif platform == 'telegram':
                share.share_url = f"https://t.me/share/url?url={quote(route_url)}&text={quote(share_text)}"
            elif platform == 'linkedin':
                share.share_url = f"https://www.linkedin.com/sharing/share-offsite/?url={quote(route_url)}"
            elif platform == 'email':
                share.share_url = f"mailto:?subject={quote('Minha avaliação da viagem com VanGo!')}&body={quote(share_text + ' ' + route_url)}"
            
            share.save()
            
            # Retornar URL de compartilhamento
            return JsonResponse({
                'success': True,
                'share_url': share.share_url
            })
    else:
        form = SocialShareForm()
    
    return render(request, 'social/share_review.html', {
        'form': form,
        'review': review
    })

@login_required
def create_social_post(request):
    """
    Cria um post para publicar em redes sociais.
    """
    social_accounts = SocialAccount.objects.filter(user=request.user)
    
    if not social_accounts.exists():
        messages.warning(request, "Você precisa conectar pelo menos uma conta de rede social para criar posts.")
        return redirect('social:social_accounts_list')
    
    if request.method == 'POST':
        form = SocialPostForm(request.POST, request.FILES)
        if form.is_valid():
            social_account_id = form.cleaned_data.get('social_account')
            social_account = get_object_or_404(SocialAccount, id=social_account_id, user=request.user)
            
            post = SocialPost(
                user=request.user,
                social_account=social_account,
                content=form.cleaned_data.get('content'),
                url=form.cleaned_data.get('url'),
                scheduled_for=form.cleaned_data.get('scheduled_for')
            )
            
            if 'image' in request.FILES:
                post.image = request.FILES['image']
            
            post.save()
            
            # Se não estiver agendado, publicar imediatamente
            if not post.scheduled_for:
                post.publish()
                messages.success(request, "Post publicado com sucesso!")
            else:
                messages.success(request, f"Post agendado para {post.scheduled_for.strftime('%d/%m/%Y %H:%M')}!")
            
            return redirect('social:social_posts_list')
    else:
        form = SocialPostForm()
        form.fields['social_account'].queryset = social_accounts
    
    return render(request, 'social/create_social_post.html', {
        'form': form,
        'social_accounts': social_accounts
    })

@login_required
def social_posts_list(request):
    """
    Lista os posts em redes sociais do usuário.
    """
    social_posts = SocialPost.objects.filter(user=request.user)
    
    return render(request, 'social/social_posts_list.html', {
        'social_posts': social_posts
    })

@login_required
def social_post_detail(request, post_id):
    """
    Detalhes de um post em rede social.
    """
    post = get_object_or_404(SocialPost, id=post_id, user=request.user)
    
    return render(request, 'social/social_post_detail.html', {
        'post': post
    })

@login_required
def social_post_delete(request, post_id):
    """
    Exclui um post em rede social.
    """
    post = get_object_or_404(SocialPost, id=post_id, user=request.user)
    
    if request.method == 'POST':
        # Em produção, se o post já foi publicado, tente excluí-lo na API do provedor
        post.delete()
        messages.success(request, "Post excluído com sucesso!")
        return redirect('social:social_posts_list')
    
    return render(request, 'social/social_post_delete.html', {
        'post': post
    })

@login_required
def referral_program(request):
    """
    Programa de indicação.
    """
    # Gerar código de referência se o usuário ainda não tiver
    referral_code = None
    referrals = SocialReferral.objects.filter(user=request.user)
    
    # Verificar se o usuário já tem referências
    if not referrals.exists():
        referral_code = SocialReferral.generate_referral_code(request.user)
    else:
        # Usar o código da primeira referência
        referral_code = referrals.first().referral_code
    
    # Contar referências convertidas
    converted_referrals = referrals.filter(converted_at__isnull=False).count()
    
    # Gerar URLs de compartilhamento
    base_url = request.build_absolute_uri(reverse('accounts:register'))
    referral_url = f"{base_url}?ref={referral_code}"
    
    share_urls = {
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={quote(referral_url)}&quote={quote('Junte-se a mim no VanGo e ganhe um desconto na sua primeira viagem!')}",
        'twitter': f"https://twitter.com/intent/tweet?url={quote(referral_url)}&text={quote('Junte-se a mim no VanGo e ganhe um desconto na sua primeira viagem!')}",
        'whatsapp': f"https://api.whatsapp.com/send?text={quote('Junte-se a mim no VanGo e ganhe um desconto na sua primeira viagem! ' + referral_url)}",
        'telegram': f"https://t.me/share/url?url={quote(referral_url)}&text={quote('Junte-se a mim no VanGo e ganhe um desconto na sua primeira viagem!')}",
        'email': f"mailto:?subject={quote('Convite para o VanGo')}&body={quote('Olá! Estou usando o VanGo para minhas viagens turísticas e acho que você também vai gostar. Use meu código de indicação para ganhar um desconto na sua primeira viagem: ' + referral_code + '. Registre-se aqui: ' + referral_url)}"
    }
    
    return render(request, 'social/referral_program.html', {
        'referral_code': referral_code,
        'referral_url': referral_url,
        'share_urls': share_urls,
        'referrals': referrals,
        'converted_referrals': converted_referrals
    })

def process_referral(request):
    """
    Processa um código de indicação.
    """
    referral_code = request.GET.get('ref')
    
    if not referral_code:
        return None
    
    try:
        # Verificar se o código existe
        referral = SocialReferral.objects.get(referral_code=referral_code)
        
        # Armazenar na sessão para uso posterior
        request.session['referral_code'] = referral_code
        
        return referral
    except SocialReferral.DoesNotExist:
        return None

def register_with_referral(request, user):
    """
    Registra um usuário com código de indicação.
    """
    referral_code = request.session.get('referral_code')
    
    if not referral_code:
        return False
    
    try:
        # Verificar se o código existe
        referral = SocialReferral.objects.get(referral_code=referral_code)
        
        # Verificar se o usuário não está se auto-referenciando
        if referral.user == user:
            return False
        
        # Atualizar a referência
        referral.referred_user = user
        referral.convert()
        
        # Limpar da sessão
        del request.session['referral_code']
        
        return True
    except SocialReferral.DoesNotExist:
        return False

# Funções auxiliares

def get_share_buttons(request, content_type, content_id):
    """
    Gera botões de compartilhamento para um conteúdo.
    """
    url = request.build_absolute_uri()
    
    if content_type == 'route':
        route = get_object_or_404(Route, id=content_id)
        text = f"Confira esta rota incrível de {route.origin} para {route.destination} com a VanGo! #VanGo #Turismo"
    elif content_type == 'booking':
        booking = get_object_or_404(Booking, id=content_id)
        text = f"Acabei de reservar uma viagem de {booking.route.origin} para {booking.route.destination} com a VanGo! #VanGo #Turismo"
    elif content_type == 'review':
        review = get_object_or_404(Review, id=content_id)
        text = f"Dei {review.rating} estrelas para minha viagem de {review.booking.route.origin} para {review.booking.route.destination} com a VanGo! #VanGo #Turismo"
    else:
        text = "Confira o VanGo, o melhor aplicativo para rotas turísticas! #VanGo #Turismo"
    
    share_urls = {
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={quote(url)}&quote={quote(text)}",
        'twitter': f"https://twitter.com/intent/tweet?url={quote(url)}&text={quote(text)}",
        'whatsapp': f"https://api.whatsapp.com/send?text={quote(text + ' ' + url)}",
        'telegram': f"https://t.me/share/url?url={quote(url)}&text={quote(text)}",
        'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url={quote(url)}",
        'email': f"mailto:?subject={quote('Confira isto no VanGo!')}&body={quote(text + ' ' + url)}"
    }
    
    return share_urls
