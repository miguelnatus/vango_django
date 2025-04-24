from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<int:booking_id>/', views.review_create_view, name='create'),
    path('<int:review_id>/', views.review_detail_view, name='detail'),
    path('<int:review_id>/edit/', views.review_edit_view, name='edit'),
]
