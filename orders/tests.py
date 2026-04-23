from django.test import TestCase, Client
from django.urls import reverse
from catalog.models import Category, Product
from accounts.models import User

class OrderViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        
    def test_order_create_view_redirects_if_empty_cart(self):
        # Si el carrito esta vacio, muestra la pagina igual (la logica actual solo muestra 'carrito vacio' en el checkout o template)
        # En nuestra vista detail.html si esta vacio muestra alerta.
        # En la vista order_create, renderiza el form.
        response = self.client.get(reverse('orders:order_create'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart:cart_detail'))

    def test_user_orders_requires_login(self):
        response = self.client.get(reverse('orders:user_orders'))
        self.assertNotEqual(response.status_code, 200)
        # Deberia redirigir al login
        self.assertTrue(response.status_code == 302)
        
    def test_user_orders_accessible_logged_in(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('orders:user_orders'))
        self.assertEqual(response.status_code, 200)
