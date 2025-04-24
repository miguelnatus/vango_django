from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('register/driver/', views.register_driver_view, name='register_driver'),
    
    # Perfil
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
    
    # Dashboards
    path('dashboard/passenger/', views.passenger_dashboard_view, name='passenger_dashboard'),
    path('dashboard/driver/', views.driver_dashboard_view, name='driver_dashboard'),
    
    # Documentos de motorista
    path('driver/documents/', views.driver_documents_view, name='driver_documents'),
    path('driver/documents/add/', views.driver_document_add_view, name='driver_document_add'),
    path('driver/documents/<int:document_id>/delete/', views.driver_document_delete_view, name='driver_document_delete'),
    
    # Novas funcionalidades
    path('verify-email/send/', views.email_verification_send, name='email_verification_send'),
    path('verify-email/<str:token>/', views.email_verification_confirm, name='email_verification_confirm'),
    path('notifications/', views.user_notifications, name='notifications'),
    path('notifications/settings/', views.notification_settings, name='notification_settings'),
]
