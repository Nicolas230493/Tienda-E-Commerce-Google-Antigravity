from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart

def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            
            # --- Lógica de Negocio (Impuestos) ---
            # El shipping_method ya viene del formulario validado
            if order.shipping_method == 'bicycle':
                order.shipping_cost = 5.00
            else:
                order.shipping_cost = 12.00
            
            # Calculo simple de impuestos (ej. 21% del subtotal)
            subtotal = cart.get_total_price()
            order.tax_amount = round(float(subtotal) * 0.21, 2)
            
            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    variant=item['variant'], # Ahora guardamos la variante
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Limpiar carrito
            cart.clear()
            
            # Guardar ID de orden en sesión para el proceso de pago
            request.session['order_id'] = order.id
            
            # Redirigir al proceso de pago
            return redirect('payment:process')
            
    else:
        # Pre-poblar form con datos del usuario y su dirección predeterminada
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
            address = request.user.get_default_address()
            if address:
                initial_data.update({
                    'address': address.street_address,
                    'city': address.city,
                    'postal_code': address.postal_code
                })
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'orders/create.html', {'cart': cart, 'form': form})

@login_required
def user_orders(request):
    orders = request.user.orders.all()
    return render(request, 'orders/list.html', {'orders': orders})
