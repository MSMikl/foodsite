from django.contrib import admin
from .models import User, Order, Type, Menu, Allergy, Recipe, RecipeShow, Referer


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'email', 'is_active', 'is_staff']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_tag', 'calories']
    readonly_fields = ['image_tag']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'price', 'finish_time']


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'price']


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    pass


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    pass


@admin.register(RecipeShow)
class RecipeShowAdmin(admin.ModelAdmin):
    pass

@admin.register(Referer)
class RefererAdmin(admin.ModelAdmin):
    pass