from decimal import Decimal
from django.conf import settings
from catalog.models import Product, ProductVariant
from .models import Cart as CartModel, CartItem

class Cart:
    def __init__(self, request):
        self.session = request.session
        self.user = request.user
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False, variant_id=None):
        # Generar ID único para el item en el carrito (Producto + Variante)
        product_id = str(product.id)
        cart_key = product_id
        if variant_id:
            cart_key = f"{product_id}_{variant_id}"

        if cart_key not in self.cart:
            price = str(product.current_price)
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(id=variant_id)
                    price = str(variant.price)
                except ProductVariant.DoesNotExist:
                    pass # Fallback to product price

            self.cart[cart_key] = {
                'quantity': 0, 
                'price': price,
                'product_id': product_id,
                'variant_id': variant_id
            }
        
        if override_quantity:
            self.cart[cart_key]['quantity'] = quantity
        else:
            self.cart[cart_key]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True
        if self.user.is_authenticated:
            self._sync_db()

    def _sync_db(self):
        # Aseguramos que el carrito base exista
        cart_model, created = CartModel.objects.get_or_create(user=self.user)
        
        # Obtenemos los IDs de los items que están actualmente en la sesión
        current_item_keys = []
        
        for item in self.cart.values():
            product_id = int(item['product_id'])
            # Nota: El modelo CartItem actual no soporta variantes en BD según la auditoría.
            # Implementamos el update_or_create sobre el product_id.
            cart_item, created = CartItem.objects.update_or_create(
                cart=cart_model,
                product_id=product_id,
                defaults={'quantity': item['quantity']}
            )
            current_item_keys.append(cart_item.id)
            
        # Limpiamos los items que ya no están en el carrito de la sesión
        CartItem.objects.filter(cart=cart_model).exclude(id__in=current_item_keys).delete()

    def remove(self, product_id, variant_id=None):
        cart_key = str(product_id)
        if variant_id:
             cart_key = f"{product_id}_{variant_id}"
             
        if cart_key in self.cart:
            del self.cart[cart_key]
            self.save()

    def __iter__(self):
        # Recolectar IDs
        product_ids = set()
        variant_ids = set()
        for item in self.cart.values():
            product_ids.add(int(item['product_id']))
            if item['variant_id']:
                variant_ids.add(int(item['variant_id']))

        products = Product.objects.filter(id__in=product_ids)
        variants = ProductVariant.objects.filter(id__in=variant_ids)
        
        cart = self.cart.copy()
        
        # Mapear objetos
        product_map = {p.id: p for p in products}
        variant_map = {v.id: v for v in variants}

        for key, item in cart.items():
            item['product'] = product_map.get(int(item['product_id']))
            item['variant'] = variant_map.get(int(item['variant_id'])) if item['variant_id'] else None
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            # Para uso en templates (formularios update)
            item['key'] = key 
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()
