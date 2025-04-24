from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Avg, Count, Sum
from .models import User, DriverDocument
from bookings.models import Booking
from routes.models import Route
from vehicles.models import Vehicle
from reviews.models import Review
from .forms import UserRegisterForm, UserProfileForm, DriverRegisterForm, DriverDocumentForm

def login_view(request):
    """
    View para login de usuários.
    """
    if request.user.is_authenticated:
        if request.user.is_driver:
            return redirect('accounts:driver_dashboard')
        else:
            return redirect('accounts:passenger_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            
            # Redirecionar para a página apropriada
            next_page = request.GET.get('next', None)
            if next_page:
                return redirect(next_page)
            elif user.is_driver:
                return redirect('accounts:driver_dashboard')
            else:
                return redirect('accounts:passenger_dashboard')
        else:
            messages.error(request, 'Nome de usuário ou senha incorretos.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    """
    View para logout de usuários.
    """
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('core:home')

def register_view(request):
    """
    View para registro de passageiros.
    """
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'passenger'
            user.save()
            
            # Fazer login automático após o registro
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            
            messages.success(request, 'Conta criada com sucesso! Bem-vindo ao VanGo.')
            return redirect('accounts:passenger_dashboard')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def register_driver_view(request):
    """
    View para registro de motoristas.
    """
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = DriverRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'driver'
            user.save()
            
            # Fazer login automático após o registro
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            
            messages.success(request, 'Conta de motorista criada com sucesso! Complete seu perfil para começar a oferecer rotas.')
            return redirect('accounts:driver_dashboard')
    else:
        form = DriverRegisterForm()
    
    return render(request, 'accounts/register_driver.html', {'form': form})

@login_required
def profile_view(request):
    """
    View para visualização do perfil do usuário.
    """
    user = request.user
    context = {
        'user': user,
    }
    
    # Adicionar informações específicas para motoristas
    if user.is_driver:
        # Obter estatísticas do motorista
        routes_count = Route.objects.filter(driver=user).count()
        vehicles_count = Vehicle.objects.filter(driver=user).count()
        reviews = Review.objects.filter(driver=user)
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        reviews_count = reviews.count()
        
        context.update({
            'routes_count': routes_count,
            'vehicles_count': vehicles_count,
            'avg_rating': avg_rating,
            'reviews_count': reviews_count,
        })
    else:
        # Obter estatísticas do passageiro
        bookings_count = Booking.objects.filter(passenger=user).count()
        completed_bookings = Booking.objects.filter(passenger=user, status='completed').count()
        
        context.update({
            'bookings_count': bookings_count,
            'completed_bookings': completed_bookings,
        })
    
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_edit_view(request):
    """
    View para edição do perfil do usuário.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})

@login_required
def change_password_view(request):
    """
    View para alteração de senha.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Manter o usuário logado após a alteração da senha
            update_session_auth_hash(request, user)
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def passenger_dashboard_view(request):
    """
    Dashboard para passageiros.
    """
    if request.user.is_driver:
        return redirect('accounts:driver_dashboard')
    
    # Obter reservas do passageiro
    upcoming_bookings = Booking.objects.filter(
        passenger=request.user,
        status__in=['pending', 'confirmed'],
        booking_date__gte=timezone.now().date()
    ).order_by('booking_date')[:5]
    
    past_bookings = Booking.objects.filter(
        passenger=request.user,
        status__in=['completed', 'cancelled']
    ).order_by('-booking_date')[:5]
    
    # Obter rotas populares
    popular_routes = Route.objects.filter(
        is_active=True
    ).annotate(
        bookings_count=Count('bookings')
    ).order_by('-bookings_count')[:3]
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'popular_routes': popular_routes,
    }
    
    return render(request, 'accounts/passenger_dashboard.html', context)

@login_required
def driver_dashboard_view(request):
    """
    Dashboard para motoristas.
    """
    if not request.user.is_driver:
        return redirect('accounts:passenger_dashboard')
    
    # Obter rotas do motorista
    routes = Route.objects.filter(driver=request.user)
    
    # Obter próximas viagens
    upcoming_bookings = Booking.objects.filter(
        route__driver=request.user,
        status='confirmed',
        booking_date__gte=timezone.now().date()
    ).order_by('booking_date')[:5]
    
    # Obter estatísticas
    total_bookings = Booking.objects.filter(route__driver=request.user).count()
    completed_bookings = Booking.objects.filter(route__driver=request.user, status='completed').count()
    
    # Calcular faturamento
    revenue = Booking.objects.filter(
        route__driver=request.user,
        status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Obter avaliações recentes
    recent_reviews = Review.objects.filter(driver=request.user).order_by('-created_at')[:3]
    
    context = {
        'routes': routes,
        'upcoming_bookings': upcoming_bookings,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'revenue': revenue,
        'recent_reviews': recent_reviews,
        'is_verified': request.user.is_verified,
    }
    
    return render(request, 'accounts/driver_dashboard.html', context)

@login_required
def driver_documents_view(request):
    """
    View para gerenciamento de documentos do motorista.
    """
    if not request.user.is_driver:
        return redirect('accounts:passenger_dashboard')
    
    documents = DriverDocument.objects.filter(driver=request.user)
    
    return render(request, 'accounts/driver_documents.html', {
        'documents': documents
    })

@login_required
def driver_document_add_view(request):
    """
    View para adicionar documento de motorista.
    """
    if not request.user.is_driver:
        return redirect('accounts:passenger_dashboard')
    
    if request.method == 'POST':
        form = DriverDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.driver = request.user
            document.save()
            messages.success(request, 'Documento enviado com sucesso! Aguarde a verificação.')
            return redirect('accounts:driver_documents')
    else:
        form = DriverDocumentForm()
    
    return render(request, 'accounts/driver_document_add.html', {
        'form': form
    })

@login_required
def driver_document_delete_view(request, document_id):
    """
    View para excluir documento de motorista.
    """
    if not request.user.is_driver:
        return redirect('accounts:passenger_dashboard')
    
    document = get_object_or_404(DriverDocument, id=document_id, driver=request.user)
    
    # Não permitir excluir documentos já verificados
    if document.is_verified:
        messages.error(request, 'Não é possível excluir documentos já verificados.')
        return redirect('accounts:driver_documents')
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Documento excluído com sucesso!')
        return redirect('accounts:driver_documents')
    
    return render(request, 'accounts/driver_document_delete.html', {
        'document': document
    })

# Novas funcionalidades

@login_required
def email_verification_send(request):
    """
    Envia e-mail de verificação para o usuário.
    """
    user = request.user
    
    # Implementação futura: gerar token e enviar e-mail
    
    messages.success(request, 'E-mail de verificação enviado com sucesso! Verifique sua caixa de entrada.')
    return redirect('accounts:profile')

@login_required
def email_verification_confirm(request, token):
    """
    Confirma o e-mail do usuário através do token.
    """
    # Implementação futura: verificar token e confirmar e-mail
    
    messages.success(request, 'E-mail verificado com sucesso!')
    return redirect('accounts:profile')

@login_required
def notification_settings(request):
    """
    Configurações de notificações do usuário.
    """
    # Implementação futura: configurações de notificações
    
    return render(request, 'accounts/notification_settings.html')

@login_required
def user_notifications(request):
    """
    Lista de notificações do usuário.
    """
    # Implementação futura: listar notificações
    
    return render(request, 'accounts/notifications.html')
