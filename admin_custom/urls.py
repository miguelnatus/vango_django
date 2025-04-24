from django.urls import path
from . import views

app_name = 'admin_custom'

urlpatterns = [
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    path('users/', views.AdminUsersView.as_view(), name='users'),
    path('routes/', views.AdminRoutesView.as_view(), name='routes'),
    path('bookings/', views.AdminBookingsView.as_view(), name='bookings'),
    path('payments/', views.AdminPaymentsView.as_view(), name='payments'),
    path('reviews/', views.AdminReviewsView.as_view(), name='reviews'),
    path('documents/', views.AdminDocumentsView.as_view(), name='documents'),
    path('coupons/', views.AdminCouponsView.as_view(), name='coupons'),
]
