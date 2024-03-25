from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Category, Location, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'slug',
                    'is_published', 'created_at',)
    list_editable = ('is_published',)
    list_display_links = ('title', 'slug',)
    search_fields = ('title', 'description',)
    list_filter = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at',)
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'post_image',
                    'pub_date', 'author', 'location',
                    'category', 'is_published', 'created_at',)
    list_editable = ('is_published',)
    search_fields = ('title', 'text',)
    list_filter = ('title', 'text',)

    def post_image(self, obj):
        if obj.image:
            img_url = obj.image.url
            return mark_safe(f'<img src={img_url} width="80" height="60">')
        return 'отсутствует'


@admin.register(Comment)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('text', 'post', 'is_published', 'created_at', 'author',)
    list_editable = ('is_published',)
    search_fields = ('text',)
    list_filter = ('text',)
