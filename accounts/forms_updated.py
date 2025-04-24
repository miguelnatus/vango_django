from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, DriverDocument

class UserRegisterForm(UserCreationForm):
    """
    Formulário para registro de passageiros.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=True)
    profile_picture = forms.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 
                  'profile_picture', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Remover caracteres não numéricos
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) < 10:
            raise forms.ValidationError('Número de telefone inválido. Deve ter pelo menos 10 dígitos.')
        return phone

class DriverRegisterForm(UserRegisterForm):
    """
    Formulário para registro de motoristas.
    """
    cnh = forms.CharField(max_length=20, required=True, label='CNH')
    cnh_expiration = forms.DateField(required=True, label='Data de Validade da CNH',
                                    widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta(UserRegisterForm.Meta):
        fields = UserRegisterForm.Meta.fields + ['cnh', 'cnh_expiration']
    
    def clean_cnh(self):
        cnh = self.cleaned_data.get('cnh')
        # Remover caracteres não numéricos
        cnh = ''.join(filter(str.isdigit, cnh))
        if len(cnh) != 11:
            raise forms.ValidationError('CNH inválida. Deve ter 11 dígitos.')
        return cnh

class UserProfileForm(forms.ModelForm):
    """
    Formulário para edição de perfil de usuário.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_picture', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email

class DriverDocumentForm(forms.ModelForm):
    """
    Formulário para upload de documentos de motorista.
    """
    class Meta:
        model = DriverDocument
        fields = ['document_type', 'document_file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_document_file(self):
        document_file = self.cleaned_data.get('document_file')
        # Verificar tamanho do arquivo (máximo 5MB)
        if document_file and document_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('O arquivo é muito grande. O tamanho máximo é 5MB.')
        
        # Verificar extensão do arquivo
        valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        import os
        ext = os.path.splitext(document_file.name)[1]
        if ext.lower() not in valid_extensions:
            raise forms.ValidationError('Formato de arquivo não suportado. Use PDF, JPG ou PNG.')
        
        return document_file

# Novos formulários

class NotificationSettingsForm(forms.ModelForm):
    """
    Formulário para configurações de notificações.
    """
    class Meta:
        model = User
        fields = ['email_notifications', 'sms_notifications', 'push_notifications']
        labels = {
            'email_notifications': 'Receber notificações por e-mail',
            'sms_notifications': 'Receber notificações por SMS',
            'push_notifications': 'Receber notificações push',
        }

class EmailVerificationForm(forms.Form):
    """
    Formulário para reenvio de verificação de e-mail.
    """
    email = forms.EmailField(required=True)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail não está registrado.')
        return email
