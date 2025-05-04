from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Recipe, Category
from django.utils.html import format_html

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'category_types')

    def category_types(self, obj):
        return format_html(
            ' '.join(
                f'<span style="background:#FF6B00;color:white;padding:2px 5px;border-radius:3px;margin:2px;display:inline-block;">{c.get_category_type_display()}</span>'
                for c in obj.categories.all()
            )
        )

    category_types.short_description = 'Типи'

admin.site.register(User, UserAdmin)
admin.site.register(Recipe)
admin.site.register(Category)

