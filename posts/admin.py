from django.contrib import admin
from .models import Post, PostVote


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'community', 'vote_status', 'number_of_comments', 'created_at']
    list_filter = ['created_at', 'community']
    search_fields = ['title', 'body', 'creator__email']
    readonly_fields = ['created_at', 'edited_at']


@admin.register(PostVote)
class PostVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'vote_value', 'created_at']
    list_filter = ['vote_value', 'created_at']
    search_fields = ['user__email', 'post__title']
    readonly_fields = ['created_at', 'updated_at']
