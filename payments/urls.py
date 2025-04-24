from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Métodos de pagamento
    path('methods/', views.payment_methods_list, name='payment_methods_list'),
    path('methods/add/', views.payment_method_add, name='payment_method_add'),
    path('methods/<int:method_id>/delete/', views.payment_method_delete, name='payment_method_delete'),
    path('methods/<int:method_id>/set-default/', views.payment_method_set_default, name='payment_method_set_default'),
    
    # Checkout e pagamento
    path('checkout/<int:booking_id>/', views.checkout, name='checkout'),
    path('apply-coupon/<int:booking_id>/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/<int:booking_id>/', views.remove_coupon, name='remove_coupon'),
    path('confirmation/<int:payment_id>/', views.payment_confirmation, name='payment_confirmation'),
    
    # Histórico e detalhes
    path('history/', views.payment_history, name='payment_history'),
    path('detail/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    
    # Webhook
    path('webhook/', views.payment_webhook, name='payment_webhook'),
]
