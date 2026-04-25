from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from catalog.models import Product, ProductVariant

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
    )

    SHIPPING_METHOD_CHOICES = (
        ('bicycle', 'Bicicleta'),
        ('motorcycle', 'Motocicleta'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='orders', 
        verbose_name="Usuario"
    )
    
    # Contact Info
    first_name = models.CharField(max_length=50, verbose_name="Nombre")
    last_name = models.CharField(max_length=50, verbose_name="Apellido")
    email = models.EmailField(verbose_name="Email")
    
    # Shipping Info
    address = models.CharField(max_length=250, verbose_name="Dirección")
    postal_code = models.CharField(max_length=20, verbose_name="Código Postal")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    
    # Restricción de Logística: Solo Bici o Moto
    shipping_method = models.CharField(
        max_length=20, 
        choices=SHIPPING_METHOD_CHOICES, 
        default='bicycle', 
        verbose_name="Método de Envío"
    )
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Costo de Envío")
    tracking_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de Seguimiento")
    
    # Financials
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Impuestos")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Pagado")
    
    # Payment
    payment_id = models.CharField(max_length=255, blank=True, verbose_name="ID Pago (Stripe)")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="Estado del Pago")
    
    created = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated = models.DateTimeField(auto_now=True, verbose_name="Actualizado")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado del Pedido")
    paid = models.BooleanField(default=False, verbose_name="Pagado")

    class Meta:
        ordering = ['-created']
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f'Pedido {self.id}'

    def clean(self):
        """
        Validación a nivel de modelo para asegurar que el método de envío sea válido.
        """
        valid_methods = [choice[0] for choice in self.SHIPPING_METHOD_CHOICES]
        if self.shipping_method not in valid_methods:
            raise ValidationError(
                {'shipping_method': f"El método de envío '{self.shipping_method}' no está permitido. Use Bicicleta o Motocicleta."}
            )

    def save(self, *args, **kwargs):
        self.full_clean() # Forzamos la ejecución de clean() antes de guardar
        super().save(*args, **kwargs)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all()) + self.shipping_cost + self.tax_amount

    def deduct_stock(self):
        """
        Descuenta el stock de los productos/variantes de forma atómica.
        """
        from django.db import transaction
        from django.db.models import F

        with transaction.atomic():
            for item in self.items.all():
                if item.variant:
                    # Bloqueamos la fila de la variante para evitar ventas simultáneas
                    variant = ProductVariant.objects.select_for_update().get(id=item.variant.id)
                    if variant.stock >= item.quantity:
                        variant.stock = F('stock') - item.quantity
                        variant.save()
                    else:
                        raise ValueError(f"Stock insuficiente para la variante {variant}")
                else:
                    # Bloqueamos la fila del producto
                    product = Product.objects.select_for_update().get(id=item.product.id)
                    if product.stock >= item.quantity:
                        product.stock = F('stock') - item.quantity
                        product.save()
                    else:
                        raise ValueError(f"Stock insuficiente para el producto {product}")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, related_name='order_items', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Item de Pedido"
        verbose_name_plural = "Items de Pedido"

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity
