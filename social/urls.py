from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    # Contas de redes sociais
    path('accounts/', views.social_accounts_list, name='social_accounts_list'),
    path('accounts/connect/<str:provider>/', views.social_account_connect, name='social_account_connect'),
    path('accounts/disconnect/<int:account_id>/', views.social_account_disconnect, name='social_account_disconnect'),
    
    # Compartilhamento
    path('share/route/<int:route_id>/', views.share_route, name='share_route'),
    path('share/booking/<int:booking_id>/', views.share_booking, name='share_booking'),
    path('share/review/<int:review_id>/', views.share_review, name='share_review'),
    
    # Posts
    path('posts/', views.social_posts_list, name='social_posts_list'),
    path('posts/create/', views.create_social_post, name='create_social_post'),
    path('posts/<int:post_id>/', views.social_post_detail, name='social_post_detail'),
    path('posts/<int:post_id>/delete/', views.social_post_delete, name='social_post_delete'),
    
    # Programa de indicação
    path('referral/', views.referral_program, name='referral_program'),
]
