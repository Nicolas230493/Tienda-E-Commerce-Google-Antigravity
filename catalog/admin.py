from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Category, Product, ProductImage, ProductVariant, Attribute, AttributeValue

# --- Inlines ---

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    # filter_horizontal solo funciona en ModelAdmin por defecto, pero podemos usarlo en inlines 
    # si definimos el widget o usamos un truco de admin.
    filter_horizontal = ('attribute_values',)
    fields = ('sku', 'attribute_values', 'price_override', 'stock')
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('attribute_values__attribute')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

# --- Admin Classes ---

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'active']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['active']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # 3. Optimización de la Lista (CRUD - Read)
    list_display = ['get_thumbnail', 'name', 'category', 'total_stock', 'active_toggle']
    list_display_links = ['name']
    list_filter = ['active', 'category', 'created', 'allow_backorder']
    search_fields = ['name', 'sku', 'description']
    list_select_related = ('category',) # Optimización N+1
    
    # 4. Mejora del Formulario (CRUD - Create/Update)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        (_('Información Básica'), {
            'fields': ('category', 'name', 'slug', 'sku', 'description')
        }),
        (_('Información de Precios y SEO'), {
            'fields': (
                ('price', 'discount_price'),
                ('stock', 'active'),
                ('meta_title', 'meta_description')
            )
        }),
        (_('Configuración de Inventario'), {
            'classes': ('collapse',),
            'fields': ('allow_backorder', 'low_stock_threshold', 'image')
        }),
    )

    # --- Métodos de visualización ---

    @admin.display(description=_('Miniatura'))
    def get_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 8px; object-fit: cover;" />', obj.image.url)
        return format_html('<div style="width: 50px; height: 50px; background: #eee; border-radius: 8px; display: flex; align-items: center; justify-content: center;"><i class="fas fa-image" style="color: #ccc;"></i></div>')

    @admin.display(description=_('Stock Total'))
    def total_stock(self, obj):
        # Muestra el stock base y resalta si es bajo
        color = "red" if obj.stock <= obj.low_stock_threshold else "inherit"
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.stock)

    @admin.display(boolean=True, description=_('Estado'))
    def active_toggle(self, obj):
        return obj.active

    # --- Acciones Masivas (CRUD - Delete/Update) ---

    actions = ['mark_as_on_sale', 'mark_out_of_stock']

    @admin.action(description=_("Marcar seleccionados como 'En Oferta'"))
    def mark_as_on_sale(self, request, queryset):
        # Ejemplo: Aplicar un 10% de descuento si no tiene uno
        count = 0
        for product in queryset:
            if not product.discount_price:
                product.discount_price = product.price * 0.9
                product.save()
                count += 1
        self.message_user(request, f"Se ha aplicado oferta a {count} productos.")

    @admin.action(description=_("Marcar seleccionados 'Sin Stock'"))
    def mark_out_of_stock(self, request, queryset):
        updated = queryset.update(stock=0, active=False)
        self.message_user(request, f"{updated} productos marcados sin stock e inactivos.")

# --- Atributos ---

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute', 'value']
    list_filter = ['attribute']
