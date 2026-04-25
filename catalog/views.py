from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Sum
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Category, Product, Review
from .forms import ReviewForm, ProductForm
from cart.forms import CartAddProductForm
from orders.models import Order

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.filter(active=True)
    products = Product.objects.active().with_prefetched_variants()

    # 1. Filtro por Categoria
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # 2. Busqueda (Search)
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    # 3. Filtros Avanzados (Precio)
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    return render(request, 'catalog/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

def product_detail(request, id, slug):
    product = get_object_or_404(
        Product.objects.with_prefetched_variants(), 
        id=id, 
        slug=slug, 
        active=True
    )
    
    # Formulario de Carrito
    cart_product_form = CartAddProductForm()

    # Reseñas
    reviews = product.reviews.filter(active=True)
    new_review = None

    if request.method == 'POST':
        # Manejo de Reseñas
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.product = product
            new_review.user = request.user
            new_review.save()
            return redirect(product.get_absolute_url())
    else:
        review_form = ReviewForm()

    # Variantes (Simple: solo listar para visualizacion o seleccion basica en form de carrito)
    variants = product.variants.filter(stock__gt=0)
    
    # Recently Viewed (Session)
    # ---------------------------
    # Guardamos IDs en sesion
    recently_viewed = request.session.get('recently_viewed', [])
    if id not in recently_viewed:
        recently_viewed.insert(0, id)
        if len(recently_viewed) > 5:
            recently_viewed.pop()
        request.session['recently_viewed'] = recently_viewed
        request.session.modified = True

    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'cart_product_form': cart_product_form,
        'reviews': reviews,
        'review_form': review_form,
        'variants': variants
    })

# --- Staff Dashboard Views ---

@staff_member_required
def dashboard_products(request):
    products = Product.objects.all().select_related('category').order_by('-created')
    
    # Métricas
    stats = {
        'total_products': products.count(),
        'low_stock': products.filter(stock__lte=5).count(),
        'active_now': products.filter(active=True).count(),
        'monthly_sales': Order.objects.filter(paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    }
    
    return render(request, 'catalog/dashboard/product_list.html', {
        'products': products,
        'stats': stats
    })

@staff_member_required
def dashboard_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            from django.utils.text import slugify
            product.slug = slugify(product.name)
            product.save()
            messages.success(request, f'¡Producto "{product.name}" creado con éxito!')
            return redirect('catalog:dashboard_products')
    else:
        form = ProductForm()
    
    return render(request, 'catalog/dashboard/product_form.html', {
        'form': form,
        'title': 'Crear Nuevo Producto'
    })

@staff_member_required
def dashboard_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{product.name}" actualizado.')
            return redirect('catalog:dashboard_products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'catalog/dashboard/product_form.html', {
        'form': form,
        'product': product,
        'title': f'Editando: {product.name}'
    })

from django.db import transaction

@staff_member_required
def dashboard_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        # Implementación de Soft Delete
        product.is_deleted = True
        product.active = False
        product.save()
        messages.warning(request, f'Producto "{product.name}" marcado como eliminado (Soft Delete).')
        return redirect('catalog:dashboard_products')
    return render(request, 'catalog/dashboard/product_confirm_delete.html', {'product': product})

# Función auxiliar para manejo de stock seguro (Race Conditions)
@transaction.atomic
def update_product_stock_safe(product_id, quantity_to_reduce):
    """
    Bloquea la fila del producto en la DB hasta que se complete la transacción.
    Evita que dos procesos descuenten stock simultáneamente.
    """
    try:
        product = Product.objects.select_for_update().get(id=product_id)
        if product.stock >= quantity_to_reduce:
            product.stock -= quantity_to_reduce
            product.save()
            return True
        return False
    except Product.DoesNotExist:
        return False
