from parler.admin import TranslatableAdmin

from django.http import HttpRequest
from django.contrib import admin

from .models import Category, Product

# Register your models here.
@admin.register(Category)
class ProfileAdmin(TranslatableAdmin):
    list_display = ('name', 'slug')
    # prepopulated_fields = {'slug': ('name',)}

    def get_prepopulated_fields(self, request: HttpRequest, obj: Category = None) -> dict:
        return {'slug': ('name',)}


@admin.register(Product)
class ProfileAdmin(TranslatableAdmin):
    list_display = ('name', 'slug', 'price', 'available', 'created', 'updated')
    list_filter = ('available', 'created', 'updated')
    list_editable = ('price', 'available')
    # prepopulated_fields = {'slug': ('name',)}

    def get_prepopulated_fields(self, request: HttpRequest, obj: Category = None) -> dict:
        return {'slug': ('name',)}