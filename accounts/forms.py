from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User, DriverDocument

class UserRegisterForm(UserCreationForm):
    """
    Formulário para registro de usuários passageiros.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label=_('Nome'))
    last_name = forms.CharField(required=True, label=_('Sobrenome'))
    phone = forms.CharField(required=True, label=_('Telefone'))
    profile_picture = forms.ImageField(required=False, label=_('Foto de Perfil'))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 
                  'profile_picture', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        
        if commit:
            user.save()
        return user

class DriverRegisterForm(UserCreationForm):
    """
    Formulário para registro de usuários motoristas.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label=_('Nome'))
    last_name = forms.CharField(required=True, label=_('Sobrenome'))
    phone = forms.CharField(required=True, label=_('Telefone'))
    profile_picture = forms.ImageField(required=False, label=_('Foto de Perfil'))
    bio = forms.CharField(widget=forms.Textarea, required=False, label=_('Biografia'))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 
                  'profile_picture', 'bio', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.bio = self.cleaned_data['bio']
        
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    """
    Formulário para edição de perfil de usuário.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_picture']
        if User.user_type == 'driver':
            fields.append('bio')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user_type == 'driver':
            self.fields['bio'] = forms.CharField(widget=forms.Textarea, required=False, label=_('Biografia'))

class DriverDocumentForm(forms.ModelForm):
    """
    Formulário para upload de documentos de motorista.
    """
    class Meta:
        model = DriverDocument
        fields = ['document_type', 'document_file']
