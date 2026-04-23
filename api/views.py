from rest_framework import generics
from catalog.models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer
    lookup_field = 'id'

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(active=True)
    serializer_class = CategorySerializer
