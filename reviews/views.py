from django.shortcuts import render

# Implementações básicas das views para evitar erros
def review_create_view(request, booking_id):
    return render(request, 'reviews/create.html', {})

def review_detail_view(request, review_id):
    return render(request, 'reviews/detail.html', {})

def review_edit_view(request, review_id):
    return render(request, 'reviews/edit.html', {})
