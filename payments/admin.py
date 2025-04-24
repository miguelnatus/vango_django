from django.contrib import admin
from .models import Payment, PaymentMethod, Coupon, CouponUsage

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'booking', 'amount', 'status', 'payment_method', 'payment_date', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__username', 'user__email', 'booking__id', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'booking', 'amount', 'status', 'payment_method')
        }),
        ('Detalhes da Transação', {
            'fields': ('transaction_id', 'gateway_response', 'payment_date')
        }),
        ('Informações de Cartão', {
            'fields': ('card_last_digits', 'card_brand'),
            'classes': ('collapse',),
        }),
        ('Informações de Boleto', {
            'fields': ('bank_slip_url', 'bank_slip_expiration'),
            'classes': ('collapse',),
        }),
        ('Informações de PIX', {
            'fields': ('pix_qr_code', 'pix_expiration'),
            'classes': ('collapse',),
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    actions = ['approve_payments', 'decline_payments', 'refund_payments']
    
    def approve_payments(self, request, queryset):
        for payment in queryset.filter(status__in=['pending', 'processing']):
            payment.approve()
        self.message_user(request, f"{queryset.count()} pagamentos foram aprovados com sucesso.")
    approve_payments.short_description = "Aprovar pagamentos selecionados"
    
    def decline_payments(self, request, queryset):
        for payment in queryset.filter(status__in=['pending', 'processing']):
            payment.decline()
        self.message_user(request, f"{queryset.count()} pagamentos foram recusados.")
    decline_payments.short_description = "Recusar pagamentos selecionados"
    
    def refund_payments(self, request, queryset):
        for payment in queryset.filter(status='approved'):
            payment.refund()
        self.message_user(request, f"{queryset.count()} pagamentos foram reembolsados.")
    refund_payments.short_description = "Reembolsar pagamentos selecionados"

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'type', 'get_display_name', 'is_default', 'created_at')
    list_filter = ('type', 'is_default', 'created_at')
    search_fields = ('user__username', 'user__email', 'card_last_digits', 'card_holder_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'type', 'is_default')
        }),
        ('Informações de Cartão', {
            'fields': ('card_token', 'card_last_digits', 'card_brand', 'card_holder_name', 'card_expiry_month', 'card_expiry_year'),
            'classes': ('collapse',),
        }),
        ('Informações de Conta Bancária', {
            'fields': ('bank_name', 'bank_account_number', 'bank_branch_number'),
            'classes': ('collapse',),
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_display_name(self, obj):
        return str(obj)
    get_display_name.short_description = 'Descrição'

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'type', 'value', 'valid_from', 'valid_until', 'usage_count', 'usage_limit', 'is_valid')
    list_filter = ('type', 'is_first_purchase_only', 'valid_from', 'valid_until')
    search_fields = ('code', 'description')
    readonly_fields = ('usage_count', 'created_at', 'updated_at')
    filter_horizontal = ('applicable_routes',)
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('code', 'description', 'type', 'value')
        }),
        ('Restrições', {
            'fields': ('min_purchase', 'max_discount', 'valid_from', 'valid_until', 'usage_limit', 'usage_count')
        }),
        ('Restrições de Usuário', {
            'fields': ('is_first_purchase_only',)
        }),
        ('Restrições de Rota', {
            'fields': ('applicable_routes',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    actions = ['duplicate_coupons']
    
    def duplicate_coupons(self, request, queryset):
        for coupon in queryset:
            new_coupon = coupon
            new_coupon.pk = None
            new_coupon.code = f"{coupon.code}_COPY"
            new_coupon.usage_count = 0
            new_coupon.save()
            
            # Copiar rotas aplicáveis
            for route in coupon.applicable_routes.all():
                new_coupon.applicable_routes.add(route)
        
        self.message_user(request, f"{queryset.count()} cupons foram duplicados com sucesso.")
    duplicate_coupons.short_description = "Duplicar cupons selecionados"

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('id', 'coupon', 'user', 'booking', 'discount_amount', 'used_at')
    list_filter = ('used_at',)
    search_fields = ('coupon__code', 'user__username', 'user__email', 'booking__id')
    readonly_fields = ('used_at',)
