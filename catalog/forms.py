from django import forms
from .models import Product, Review

class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar estilos de Impulso Shop a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-4 py-3 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 outline-none transition-all placeholder-slate-500'
            })

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'sku', 'price', 'discount_price', 
            'stock', 'image', 'active', 'low_stock_threshold', 
            'description', 'meta_title', 'meta_description'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'active': forms.CheckboxInput(attrs={'class': 'w-6 h-6 rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-cyan-500'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-4 py-3 focus:border-cyan-400 outline-none'}),
            'title': forms.TextInput(attrs={'class': 'w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-4 py-3 focus:border-cyan-400 outline-none'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-4 py-3 focus:border-cyan-400 outline-none'}),
        }
