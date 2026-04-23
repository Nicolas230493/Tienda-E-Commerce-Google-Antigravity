from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant, Attribute, AttributeValue

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'active']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['active']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    filter_horizontal = ['attribute_values']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'stock', 'active', 'created']
    list_filter = ['active', 'category', 'created']
    list_editable = ['price', 'stock', 'active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'sku', 'description']
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('category', 'name', 'slug', 'sku', 'description')
        }),
        ('Precios e Inventario', {
            'fields': (('price', 'discount_price'), ('stock', 'active'), ('allow_backorder', 'low_stock_threshold'))
        }),
        ('Multimedia', {
            'fields': ('image',)
        }),
        ('SEO y Marketing', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute', 'value']
    list_filter = ['attribute']
