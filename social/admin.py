from django.contrib import admin
from .models import SocialShare, SocialAccount, SocialPost, SocialReferral

@admin.register(SocialShare)
class SocialShareAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'content_type', 'content_id', 'shared_at')
    list_filter = ('platform', 'content_type', 'shared_at')
    search_fields = ('user__username', 'user__email', 'content_id')
    date_hierarchy = 'shared_at'

@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'provider_username', 'created_at', 'is_token_expired')
    list_filter = ('provider', 'created_at')
    search_fields = ('user__username', 'user__email', 'provider_username', 'provider_id')
    readonly_fields = ('created_at', 'updated_at')
    
    def is_token_expired(self, obj):
        return obj.is_token_expired
    is_token_expired.boolean = True
    is_token_expired.short_description = 'Token Expirado'

@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'social_account', 'status', 'scheduled_for', 'published_at', 'created_at')
    list_filter = ('status', 'social_account__provider', 'created_at', 'published_at')
    search_fields = ('user__username', 'user__email', 'content')
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    actions = ['publish_posts']
    
    def publish_posts(self, request, queryset):
        for post in queryset.filter(status='pending'):
            post.publish()
        self.message_user(request, f"{queryset.count()} posts foram publicados com sucesso.")
    publish_posts.short_description = "Publicar posts selecionados"

@admin.register(SocialReferral)
class SocialReferralAdmin(admin.ModelAdmin):
    list_display = ('user', 'referred_user', 'platform', 'referral_code', 'created_at', 'is_converted')
    list_filter = ('platform', 'created_at', 'converted_at')
    search_fields = ('user__username', 'user__email', 'referred_user__username', 'referred_user__email', 'referral_code')
    readonly_fields = ('created_at', 'converted_at')
    
    def is_converted(self, obj):
        return obj.converted_at is not None
    is_converted.boolean = True
    is_converted.short_description = 'Convertido'
