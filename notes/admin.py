from django.contrib import admin
from .models import Category, Tag, Note

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name',)
    list_filter = ('user',)

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name',)
    list_filter = ('user',)

class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'created_at', 'updated_at', 'reminder')
    search_fields = ('title', 'content')
    list_filter = ('user', 'category', 'tags', 'created_at', 'updated_at')
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'

admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Note, NoteAdmin)
