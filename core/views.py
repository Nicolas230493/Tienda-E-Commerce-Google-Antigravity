from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from catalog.models import Product
from orders.models import Order

def home(request):
    recent_products = Product.objects.filter(active=True).order_by('-created')[:8]
    return render(request, 'core/home.html', {'recent_products': recent_products})

@staff_member_required
def dashboard(request):
    # Metricas simples
    total_sales = Order.objects.filter(paid=True).aggregate(Sum('total_amount'))['total_amount__sum']
    total_orders_count = Order.objects.count()
    active_products_count = Product.objects.filter(active=True).count()
    recent_orders = Order.objects.order_by('-created')[:5]

    return render(request, 'core/dashboard.html', {
        'total_sales': total_sales,
        'total_orders_count': total_orders_count,
        'active_products_count': active_products_count,
        'recent_orders': recent_orders
    })
