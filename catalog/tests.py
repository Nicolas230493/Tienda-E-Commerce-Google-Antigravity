from django.test import TestCase
from catalog.models import Category, Product

class CatalogModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            category=self.category,
            name='Smartphone',
            slug='smartphone',
            price=999.99,
            stock=10,
            sku='PHONE123'
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Smartphone')
        self.assertEqual(self.product.category.name, 'Electronics')
        self.assertTrue(self.product.active)

    def test_absolute_url(self):
        url = self.product.get_absolute_url()
        self.assertEqual(url, f'/shop/product/{self.product.id}/{self.product.slug}/')
