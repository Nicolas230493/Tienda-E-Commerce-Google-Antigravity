from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# --- Managers y QuerySets para Optimización ORM ---

class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def with_prefetched_variants(self):
        """
        Optimización N+1: Carga variantes y sus atributos en una sola consulta.
        """
        return self.prefetch_related(
            'variants__attribute_values__attribute',
            'images'
        )

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def with_prefetched_variants(self):
        return self.get_queryset().with_prefetched_variants()


# --- Modelos del Catálogo ---

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descripción")
    active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_list_by_category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name="Categoría", db_index=True)
    name = models.CharField(max_length=255, verbose_name="Nombre", db_index=True)
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Precio con descuento")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU")
    active = models.BooleanField(default=True, verbose_name="Activo", db_index=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Eliminado", db_index=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name="Imagen Principal")
    
    # Inventario
    allow_backorder = models.BooleanField(default=False, verbose_name="Permitir reservas sin stock")
    low_stock_threshold = models.PositiveIntegerField(default=5, verbose_name="Umbral de stock bajo")
    
    # SEO
    meta_title = models.CharField(max_length=255, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta Description")
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Asignar Manager personalizado
    objects = ProductManager()

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-created']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.id, self.slug])
        
    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/%Y/%m/%d')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Imagen de Producto"
        verbose_name_plural = "Imágenes de Producto"


class Attribute(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nombre del Atributo (ej. Talla, Color)")

    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, related_name='values', on_delete=models.CASCADE)
    value = models.CharField(max_length=50, verbose_name="Valor (ej. S, Rojo)")

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    attribute_values = models.ManyToManyField(AttributeValue, related_name='variants')
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="SKU Variante")
    price_override = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Precio específico")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock Variante")

    def __str__(self):
        return f"{self.product.name} - " + ", ".join([str(v) for v in self.attribute_values.all()])

    @property
    def price(self):
        return self.price_override if self.price_override is not None else self.product.current_price


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Puntuación")
    title = models.CharField(max_length=100, verbose_name="Título")
    comment = models.TextField(verbose_name="Comentario")
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False, verbose_name="Aprobado")

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ['-created']


class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='wishlist', on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='wishlisted_by', blank=True)

    def __str__(self):
        return f"Wishlist de {self.user.username}"
