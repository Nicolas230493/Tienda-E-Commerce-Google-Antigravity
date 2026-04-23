from django.contrib import admin
from .models import Order, OrderItem
from django.utils.safestring import mark_safe

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product', 'variant']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_info', 'shipping_method_display', 'total_display', 'paid_status', 'status', 'created']
    list_filter = ['status', 'paid', 'shipping_method', 'created']
    list_editable = ['status']
    search_fields = ['id', 'first_name', 'last_name', 'email', 'payment_id']
    inlines = [OrderItemInline]
    readonly_fields = ['created', 'updated', 'total_amount', 'tax_amount']
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('user', ('first_name', 'last_name'), 'email')
        }),
        ('Detalles de Envío', {
            'fields': ('address', ('postal_code', 'city'), ('shipping_method', 'shipping_cost'), 'tracking_number')
        }),
        ('Estado y Pago', {
            'fields': (('status', 'paid'), ('payment_status', 'payment_id'))
        }),
        ('Cifras Finales', {
            'fields': (('tax_amount', 'total_amount'),),
        }),
    )

    @admin.display(description='Cliente')
    def user_info(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description='Total')
    def total_display(self, obj):
        return mark_safe(f"<strong style='color: #0891b2;'>${obj.get_total_cost()}</strong>")

    @admin.display(description='Logística')
    def shipping_method_display(self, obj):
        icon = "🚲" if obj.shipping_method == 'bicycle' else "🛵"
        return f"{icon} {obj.get_shipping_method_display()}"

    @admin.display(description='Pagado', boolean=True)
    def paid_status(self, obj):
        return obj.paid
