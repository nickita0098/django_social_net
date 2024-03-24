from django.contrib import admin

from .models import Category, Location, Post


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
    list_display = ('title', 'text', 'pub_date', 'author', 'location',
                    'category', 'is_published', 'created_at',)
    list_editable = ('is_published',)
    search_fields = ('title', 'text',)
    list_filter = ('title', 'text',)
