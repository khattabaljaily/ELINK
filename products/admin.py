from django.contrib import admin

from .models import Category, Product, ProductImage, Variant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active', 'total_stock')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, VariantInline]
