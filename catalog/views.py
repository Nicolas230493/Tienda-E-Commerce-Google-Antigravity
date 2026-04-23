from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Category, Product, Review
from .forms import ReviewForm
from cart.forms import CartAddProductForm

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
