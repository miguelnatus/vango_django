from django import forms
from .models import Route, RouteImage, RouteStop

class RouteForm(forms.ModelForm):
    """
    Formulário para criação e edição de rotas.
    """
    class Meta:
        model = Route
        fields = [
            'title', 'description', 
            'origin_name', 'origin_address', 'origin_latitude', 'origin_longitude',
            'destination_name', 'destination_address', 'destination_latitude', 'destination_longitude',
            'distance_km', 'duration_minutes', 'price', 'max_passengers',
            'available_days', 'departure_time', 'return_time',
            'has_wifi', 'has_air_conditioning', 'has_bathroom', 'has_usb_outlets', 'is_accessible', 'allows_pets',
            'cover_image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'origin_latitude': forms.HiddenInput(),
            'origin_longitude': forms.HiddenInput(),
            'destination_latitude': forms.HiddenInput(),
            'destination_longitude': forms.HiddenInput(),
            'available_days': forms.CheckboxSelectMultiple(),
            'departure_time': forms.TimeInput(attrs={'type': 'time'}),
            'return_time': forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {
            'title': 'Título da Rota',
            'description': 'Descrição',
            'origin_name': 'Nome do Local de Origem',
            'origin_address': 'Endereço de Origem',
            'destination_name': 'Nome do Local de Destino',
            'destination_address': 'Endereço de Destino',
            'distance_km': 'Distância (km)',
            'duration_minutes': 'Duração (minutos)',
            'price': 'Preço (R$)',
            'max_passengers': 'Número Máximo de Passageiros',
            'available_days': 'Dias Disponíveis',
            'departure_time': 'Horário de Partida',
            'return_time': 'Horário de Retorno (opcional)',
            'has_wifi': 'Wi-Fi',
            'has_air_conditioning': 'Ar Condicionado',
            'has_bathroom': 'Banheiro',
            'has_usb_outlets': 'Tomadas USB',
            'is_accessible': 'Acessível para Cadeirantes',
            'allows_pets': 'Permite Animais de Estimação',
            'cover_image': 'Imagem de Capa'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Verificar se as coordenadas foram fornecidas
        origin_lat = cleaned_data.get('origin_latitude')
        origin_lng = cleaned_data.get('origin_longitude')
        dest_lat = cleaned_data.get('destination_latitude')
        dest_lng = cleaned_data.get('destination_longitude')
        
        if not origin_lat or not origin_lng:
            self.add_error('origin_address', 'Selecione um local de origem válido no mapa.')
        
        if not dest_lat or not dest_lng:
            self.add_error('destination_address', 'Selecione um local de destino válido no mapa.')
        
        return cleaned_data

class RouteImageForm(forms.ModelForm):
    """
    Formulário para upload de imagens da rota.
    """
    class Meta:
        model = RouteImage
        fields = ['image', 'caption']
        labels = {
            'image': 'Imagem',
            'caption': 'Legenda (opcional)'
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        # Verificar tamanho da imagem (máximo 5MB)
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError('A imagem é muito grande. O tamanho máximo é 5MB.')
        
        # Verificar extensão da imagem
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        import os
        ext = os.path.splitext(image.name)[1]
        if ext.lower() not in valid_extensions:
            raise forms.ValidationError('Formato de imagem não suportado. Use JPG, PNG ou WebP.')
        
        return image

class RouteStopForm(forms.ModelForm):
    """
    Formulário para adicionar paradas na rota.
    """
    class Meta:
        model = RouteStop
        fields = ['name', 'description', 'address', 'latitude', 'longitude', 'duration_minutes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
        labels = {
            'name': 'Nome da Parada',
            'description': 'Descrição',
            'address': 'Endereço',
            'duration_minutes': 'Duração da Parada (minutos)'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Verificar se as coordenadas foram fornecidas
        lat = cleaned_data.get('latitude')
        lng = cleaned_data.get('longitude')
        
        if not lat or not lng:
            self.add_error('address', 'Selecione um local válido no mapa.')
        
        return cleaned_data

class RouteSearchForm(forms.Form):
    """
    Formulário para pesquisa de rotas.
    """
    origin = forms.CharField(max_length=100, required=False, label='Origem')
    destination = forms.CharField(max_length=100, required=False, label='Destino')
    date = forms.DateField(required=False, label='Data', widget=forms.DateInput(attrs={'type': 'date'}))
    min_price = forms.DecimalField(required=False, label='Preço Mínimo')
    max_price = forms.DecimalField(required=False, label='Preço Máximo')
    departure_time = forms.TimeField(required=False, label='Horário de Partida', widget=forms.TimeInput(attrs={'type': 'time'}))
    has_wifi = forms.BooleanField(required=False, label='Wi-Fi')
    has_air_conditioning = forms.BooleanField(required=False, label='Ar Condicionado')
    is_accessible = forms.BooleanField(required=False, label='Acessível para Cadeirantes')
