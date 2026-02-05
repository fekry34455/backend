from django.contrib import admin
from .models import Community, CommunityMember


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['id', 'creator', 'number_of_members', 'privacy_type', 'created_at']
    list_filter = ['privacy_type', 'created_at']
    search_fields = ['id', 'creator__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CommunityMember)
class CommunityMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'community', 'is_moderator', 'joined_at']
    list_filter = ['is_moderator', 'joined_at']
    search_fields = ['user__email', 'community__id']
    readonly_fields = ['joined_at']
