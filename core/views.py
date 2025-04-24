from django.shortcuts import render
from django.views.generic import TemplateView
from .models import CoreSettings, FAQ

def home(request):
    """
    View para a página inicial do site.
    """
    settings = CoreSettings.get_settings()
    return render(request, 'core/home.html', {
        'settings': settings,
    })

def about(request):
    """
    View para a página Sobre Nós.
    """
    settings = CoreSettings.get_settings()
    return render(request, 'core/about.html', {
        'settings': settings,
    })

def contact(request):
    """
    View para a página de Contato.
    """
    settings = CoreSettings.get_settings()
    return render(request, 'core/contact.html', {
        'settings': settings,
    })

def faq(request):
    """
    View para a página de Perguntas Frequentes.
    """
    settings = CoreSettings.get_settings()
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')
    
    # Agrupar FAQs por categoria
    faq_categories = {}
    for faq in faqs:
        category = faq.get_category_display()
        if category not in faq_categories:
            faq_categories[category] = []
        faq_categories[category].append(faq)
    
    return render(request, 'core/faq.html', {
        'settings': settings,
        'faq_categories': faq_categories,
    })

def terms(request):
    """
    View para a página de Termos e Condições.
    """
    settings = CoreSettings.get_settings()
    return render(request, 'core/terms.html', {
        'settings': settings,
    })

def privacy(request):
    """
    View para a página de Política de Privacidade.
    """
    settings = CoreSettings.get_settings()
    return render(request, 'core/privacy.html', {
        'settings': settings,
    })
