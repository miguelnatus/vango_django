from django import forms
from .models import PaymentMethod

class PaymentMethodForm(forms.ModelForm):
    """
    Formulário para adicionar um novo método de pagamento.
    """
    # Campos para cartão de crédito/débito (não serão salvos no banco de dados)
    card_number = forms.CharField(
        label='Número do Cartão',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '•••• •••• •••• ••••'})
    )
    card_holder = forms.CharField(
        label='Nome no Cartão',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nome como aparece no cartão'})
    )
    card_expiry_month = forms.ChoiceField(
        label='Mês de Expiração',
        required=False,
        choices=[(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 13)]
    )
    card_expiry_year = forms.ChoiceField(
        label='Ano de Expiração',
        required=False,
        choices=[(str(i), str(i)) for i in range(2023, 2036)]
    )
    card_cvv = forms.CharField(
        label='Código de Segurança (CVV)',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '•••'})
    )
    
    class Meta:
        model = PaymentMethod
        fields = ['type', 'is_default']
        widgets = {
            'type': forms.RadioSelect(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].label = 'Tipo de Método de Pagamento'
        self.fields['is_default'].label = 'Definir como método padrão'
    
    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('type')
        
        if payment_type in ['credit_card', 'debit_card']:
            card_number = cleaned_data.get('card_number')
            card_holder = cleaned_data.get('card_holder')
            card_expiry_month = cleaned_data.get('card_expiry_month')
            card_expiry_year = cleaned_data.get('card_expiry_year')
            card_cvv = cleaned_data.get('card_cvv')
            
            if not card_number:
                self.add_error('card_number', 'Este campo é obrigatório.')
            elif not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
                self.add_error('card_number', 'Número de cartão inválido.')
            
            if not card_holder:
                self.add_error('card_holder', 'Este campo é obrigatório.')
            
            if not card_expiry_month:
                self.add_error('card_expiry_month', 'Este campo é obrigatório.')
            
            if not card_expiry_year:
                self.add_error('card_expiry_year', 'Este campo é obrigatório.')
            
            if not card_cvv:
                self.add_error('card_cvv', 'Este campo é obrigatório.')
            elif not card_cvv.isdigit() or len(card_cvv) < 3 or len(card_cvv) > 4:
                self.add_error('card_cvv', 'Código de segurança inválido.')
        
        return cleaned_data

class CreditCardPaymentForm(forms.Form):
    """
    Formulário para pagamento com cartão de crédito.
    """
    card_number = forms.CharField(
        label='Número do Cartão',
        widget=forms.TextInput(attrs={'placeholder': '•••• •••• •••• ••••'})
    )
    card_holder = forms.CharField(
        label='Nome no Cartão',
        widget=forms.TextInput(attrs={'placeholder': 'Nome como aparece no cartão'})
    )
    card_expiry_month = forms.ChoiceField(
        label='Mês de Expiração',
        choices=[(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 13)]
    )
    card_expiry_year = forms.ChoiceField(
        label='Ano de Expiração',
        choices=[(str(i), str(i)) for i in range(2023, 2036)]
    )
    card_cvv = forms.CharField(
        label='Código de Segurança (CVV)',
        widget=forms.TextInput(attrs={'placeholder': '•••'})
    )
    save_card = forms.BooleanField(
        label='Salvar cartão para futuras compras',
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        card_number = cleaned_data.get('card_number')
        card_cvv = cleaned_data.get('card_cvv')
        
        if card_number and (not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19):
            self.add_error('card_number', 'Número de cartão inválido.')
        
        if card_cvv and (not card_cvv.isdigit() or len(card_cvv) < 3 or len(card_cvv) > 4):
            self.add_error('card_cvv', 'Código de segurança inválido.')
        
        return cleaned_data

class PixPaymentForm(forms.Form):
    """
    Formulário para pagamento com PIX.
    """
    # Não precisa de campos adicionais, apenas confirmação
    confirm = forms.BooleanField(
        label='Confirmo que pagarei via PIX',
        required=True
    )

class BankSlipPaymentForm(forms.Form):
    """
    Formulário para pagamento com boleto bancário.
    """
    # Não precisa de campos adicionais, apenas confirmação
    confirm = forms.BooleanField(
        label='Confirmo que pagarei via boleto bancário',
        required=True
    )
    
    # Opcionalmente, pode incluir campos para CPF/CNPJ
    document = forms.CharField(
        label='CPF/CNPJ',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Apenas números'})
    )
    
    def clean_document(self):
        document = self.cleaned_data.get('document')
        
        if document:
            # Remover caracteres não numéricos
            document = ''.join(filter(str.isdigit, document))
            
            # Validar CPF/CNPJ
            if len(document) != 11 and len(document) != 14:
                raise forms.ValidationError('CPF/CNPJ inválido.')
        
        return document
