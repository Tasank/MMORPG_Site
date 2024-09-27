from django.contrib import admin
from .models import Post, Response

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('category', 'title', 'created_ad')
    search_fields = ('title', 'text')
    list_filter = ('category',)
    date_hierarchy = 'created_ad'
    actions = ['approve_posts']

    def approve_posts(self, request, queryset):
        queryset.update(status=True)

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'status', 'created_ad')
    search_fields = ('text',)
    list_filter = ('status',)
    date_hierarchy = 'created_ad'
