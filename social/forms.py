from django import forms
from .models import SocialAccount, SocialPost

class SocialShareForm(forms.Form):
    """
    Formulário para compartilhar conteúdo em redes sociais.
    """
    PLATFORM_CHOICES = (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('linkedin', 'LinkedIn'),
        ('email', 'Email'),
    )
    
    platform = forms.ChoiceField(
        label='Plataforma',
        choices=PLATFORM_CHOICES,
        widget=forms.RadioSelect
    )
    
    custom_message = forms.CharField(
        label='Mensagem personalizada (opcional)',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Adicione uma mensagem personalizada ao compartilhar...'})
    )

class SocialAccountConnectForm(forms.Form):
    """
    Formulário para conectar conta de rede social.
    """
    username = forms.CharField(
        label='Nome de usuário',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Seu nome de usuário na rede social'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Em um ambiente real, você seria redirecionado para a página de autenticação da rede social.'

class SocialPostForm(forms.ModelForm):
    """
    Formulário para criar post em rede social.
    """
    social_account = forms.ModelChoiceField(
        label='Conta',
        queryset=SocialAccount.objects.none(),
        empty_label=None
    )
    
    class Meta:
        model = SocialPost
        fields = ['social_account', 'content', 'image', 'url', 'scheduled_for']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'O que você está pensando?'}),
            'url': forms.URLInput(attrs={'placeholder': 'https://exemplo.com'}),
            'scheduled_for': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = 'Imagem (opcional)'
        self.fields['url'].label = 'URL (opcional)'
        self.fields['scheduled_for'].label = 'Agendar para (opcional)'
        self.fields['content'].label = 'Conteúdo'
        
        # Campos opcionais
        self.fields['image'].required = False
        self.fields['url'].required = False
        self.fields['scheduled_for'].required = False
