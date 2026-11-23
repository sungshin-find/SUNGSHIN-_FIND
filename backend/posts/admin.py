from django.contrib import admin

from .models import Match, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'post_type', 'title', 'category', 'color', 'location', 'event_date', 'status', 'author']
    list_filter = ['post_type', 'status', 'category', 'location']
    search_fields = ['title', 'description']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'lost', 'found', 'score', 'created_at']
    ordering = ['-score']
