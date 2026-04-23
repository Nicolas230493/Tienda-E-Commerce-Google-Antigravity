from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from catalog.models import Product
from .cart import Cart
from .forms import CartAddProductForm

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        variant_id = cd.get('variant_id')
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override'],
            variant_id=variant_id
        )
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    # Para eliminar variante especifica, necesitariamos pasar el variant_id en la URL o POST
    # Por simplicidad ahora, si recibimos un parametro GET o POST variant_id lo usamos
    variant_id = request.POST.get('variant_id') or request.GET.get('variant_id')
    # Validar que product_id exista
    product = get_object_or_404(Product, id=product_id) 
    
    # El cart remove espera product object, pero usa el ID internamente
    # Modificamos cart.remove para aceptar product_id directamente en el paso anterior
    # pero revisando cart.py, usa `cart.remove(product_id, variant_id)` logicamente.
    # En la implementacion anterior cart.py -> remove(self, product, ...) -> product.id
    # En la nueva implementacion cart.py -> remove(self, product_id, variant_id)
    
    cart.remove(product_id, variant_id)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True,
            'variant_id': item['variant_id']
        })
    return render(request, 'cart/detail.html', {'cart': cart})
