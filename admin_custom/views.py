from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from django.contrib import messages

from accounts.models import User, PassengerProfile, DriverProfile, DriverDocument
from routes.models import Route
from bookings.models import Booking
from vehicles.models import Vehicle
from reviews.models import Review
from payments.models import Payment, PaymentMethod, Coupon

class AdminDashboardView(View):
    """
    View para o dashboard administrativo personalizado
    """
    template_name = 'admin_custom/dashboard.html'
    
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Estatísticas gerais
        total_users = User.objects.count()
        total_passengers = PassengerProfile.objects.count()
        total_drivers = DriverProfile.objects.count()
        total_routes = Route.objects.count()
        total_bookings = Booking.objects.count()
        total_vehicles = Vehicle.objects.count()
        
        # Estatísticas financeiras
        total_revenue = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        avg_booking_value = Payment.objects.filter(status='completed').aggregate(Avg('amount'))['amount__avg'] or 0
        
        # Estatísticas de crescimento
        new_users_today = User.objects.filter(date_joined__date=timezone.now().date()).count()
        new_bookings_today = Booking.objects.filter(created_at__date=timezone.now().date()).count()
        
        # Rotas mais populares
        popular_routes = Route.objects.annotate(
            booking_count=Count('booking')
        ).order_by('-booking_count')[:5]
        
        # Motoristas mais ativos
        active_drivers = DriverProfile.objects.annotate(
            route_count=Count('user__route')
        ).order_by('-route_count')[:5]
        
        # Avaliações recentes
        recent_reviews = Review.objects.order_by('-created_at')[:5]
        
        # Documentos pendentes de aprovação
        pending_documents = DriverDocument.objects.filter(status='pending').order_by('created_at')
        
        context = {
            'total_users': total_users,
            'total_passengers': total_passengers,
            'total_drivers': total_drivers,
            'total_routes': total_routes,
            'total_bookings': total_bookings,
            'total_vehicles': total_vehicles,
            'total_revenue': total_revenue,
            'avg_booking_value': avg_booking_value,
            'new_users_today': new_users_today,
            'new_bookings_today': new_bookings_today,
            'popular_routes': popular_routes,
            'active_drivers': active_drivers,
            'recent_reviews': recent_reviews,
            'pending_documents': pending_documents,
        }
        
        return render(request, self.template_name, context)

class AdminUsersView(View):
    """
    View para gerenciamento de usuários
    """
    template_name = 'admin_custom/users.html'
    
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Filtrar usuários
        user_type = request.GET.get('user_type', 'all')
        status = request.GET.get('status', 'all')
        search = request.GET.get('search', '')
        
        users = User.objects.all()
        
        if user_type == 'passenger':
            users = users.filter(passengerprofile__isnull=False)
        elif user_type == 'driver':
            users = users.filter(driverprofile__isnull=False)
        elif user_type == 'staff':
            users = users.filter(is_staff=True)
        
        if status == 'active':
            users = users.filter(is_active=True)
        elif status == 'inactive':
            users = users.filter(is_active=False)
        
        if search:
            users = users.filter(
                first_name__icontains=search
            ) | users.filter(
                last_name__icontains=search
            ) | users.filter(
                email__icontains=search
            ) | users.filter(
                username__icontains=search
            )
        
        context = {
            'users': users.order_by('-date_joined'),
            'user_type': user_type,
            'status': status,
            'search': search,
        }
        
        return render(request, self.template_name, context)

class AdminRoutesView(View):
    """
    View para gerenciamento de rotas
    """
    template_name = 'admin_custom/routes.html'
    
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Filtrar rotas
        status = request.GET.get('status', 'all')
        search = request.GET.get('search', '')
        
        routes = Route.objects.all()
        
        if status == 'active':
            routes = routes.filter(is_active=True)
        elif status == 'inactive':
            routes = routes.filter(is_active=False)
        
        if search:
            routes = routes.filter(
                title__icontains=search
            ) | routes.filter(
                origin__icontains=search
            ) | routes.filter(
                destination__icontains=search
            )
        
        context = {
            'routes': routes.order_by('-created_at'),
            'status': status,
            'search': search,
        }
        
        return render(request, self.template_name, context)

class AdminBookingsView(View):
    """
    View para gerenciamento de reservas
    """
    template_name = 'admin_custom/bookings.html'
    
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Filtrar reservas
        status = request.GET.get('status', 'all')
        search = request.GET.get('search', '')
        
        bookings = Booking.objects.all()
        
        if status != 'all':
            bookings = bookings.filter(status=status)
        
        if search:
            bookings = bookings.filter(
                booking_code__icontains=search
            ) | bookings.filter(
                passenger__first_name__icontains=search
            ) | bookings.filter(
                passenger__last_name__icontains=search
            ) | bookings.filter(
                route__title__icontains=search
            )
        
        context = {
            'bookings': bookings.order_by('-created_at'),
            'status': status,
            'search': search,
        }
        
        return render(request, self.template_name, context)

class AdminPaymentsView(View):
    """
    View para gerenciamento de pagamentos
    """
    template_name = 'admin_custom/payments.html'
    
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Filtrar pagamentos
        status = request.GET.get('status', 'all')
        search = request.GET.get('search', '')
        
        payments = Payment.objects.all()
        
        if status != 'all':
            payments = payments.filter(status=status)
        
        if search:
            payments = payments.filter(
                payment_code__icontains=search
            ) | payments.filter(
                user__first_name__icontains=search
            ) | payments.filter(
                user__last_name__icontains=search
            ) | payments.filter(
                booking__booking_code__icontains=search
            )
        
        context = {
            'payments': payments.order_by('-created_at'),
            'status': status,
            'search': search,
        }
        
        return render(request, self.template_name, context)

class AdminReviewsView(View):
    """
    View para gerenciamento de avaliações
    """
    template_name = 'admin_custom/reviews.html'
    
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Filtrar avaliações
        rating = request.GET.get('rating', 'all')
        search = request.GET.get('search', '')
        
        reviews = Review.objects.all()
        
        if rating != 'all':
            reviews = reviews.filter(rating=rating)
        
        if search:
            reviews = reviews.filter(
                user__first_name__icontains=search
            ) | reviews.filter(
                user__last_name__icontains=search
            ) | reviews.filter(
                route__title__icontains=search
            ) | reviews.filter(
                comment__icontains=search
            )
        
        context = {
            'reviews': reviews.order_by('-created_at'),
            'rating': rating,
            'search': search,
        }
        
        return render(request, self.template_name, context)

class AdminDocumentsView(View):
    """
    View para gerenciamento de documentos de motoristas
    """
    template_name = 'admin_custom/documents.html'
    
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Filtrar documentos
        status = request.GET.get('status', 'all')
        search = request.GET.get('search', '')
        
        documents = DriverDocument.objects.all()
        
        if status != 'all':
            documents = documents.filter(status=status)
        
        if search:
            documents = documents.filter(
                driver__user__first_name__icontains=search
            ) | documents.filter(
                driver__user__last_name__icontains=search
            ) | documents.filter(
                document_type__icontains=search
            )
        
        context = {
            'documents': documents.order_by('-created_at'),
            'status': status,
            'search': search,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        document_id = request.POST.get('document_id')
        action = request.POST.get('action')
        
        if document_id and action:
            document = DriverDocument.objects.get(id=document_id)
            
            if action == 'approve':
                document.status = 'approved'
                document.reviewed_at = timezone.now()
                document.reviewed_by = request.user
                document.save()
                messages.success(request, f'Documento {document.document_type} aprovado com sucesso.')
            
            elif action == 'reject':
                document.status = 'rejected'
                document.reviewed_at = timezone.now()
                document.reviewed_by = request.user
                document.rejection_reason = request.POST.get('rejection_reason', '')
                document.save()
                messages.success(request, f'Documento {document.document_type} rejeitado com sucesso.')
        
        return redirect('admin_custom:documents')

class AdminCouponsView(View):
    """
    View para gerenciamento de cupons de desconto
    """
    template_name = 'admin_custom/coupons.html'
    
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Filtrar cupons
        status = request.GET.get('status', 'all')
        search = request.GET.get('search', '')
        
        coupons = Coupon.objects.all()
        
        if status == 'active':
            coupons = coupons.filter(is_active=True)
        elif status == 'inactive':
            coupons = coupons.filter(is_active=False)
        
        if search:
            coupons = coupons.filter(
                code__icontains=search
            ) | coupons.filter(
                description__icontains=search
            )
        
        context = {
            'coupons': coupons.order_by('-created_at'),
            'status': status,
            'search': search,
        }
        
        return render(request, self.template_name, context)

# URLs para o painel administrativo personalizado
app_name = 'admin_custom'

urlpatterns = [
    path('', AdminDashboardView.as_view(), name='dashboard'),
    path('users/', AdminUsersView.as_view(), name='users'),
    path('routes/', AdminRoutesView.as_view(), name='routes'),
    path('bookings/', AdminBookingsView.as_view(), name='bookings'),
    path('payments/', AdminPaymentsView.as_view(), name='payments'),
    path('reviews/', AdminReviewsView.as_view(), name='reviews'),
    path('documents/', AdminDocumentsView.as_view(), name='documents'),
    path('coupons/', AdminCouponsView.as_view(), name='coupons'),
]
