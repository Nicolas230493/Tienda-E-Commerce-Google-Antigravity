from django import forms
from catalog.models import Product, ProductVariant

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        label="Cantidad",
        widget=forms.NumberInput(attrs={'class': 'w-20 px-3 py-2 border rounded-lg'})
    )
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )
    variant_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        variant_id = cleaned_data.get('variant_id')

        if self.product:
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(id=variant_id, product=self.product)
                    if quantity > variant.stock:
                        raise forms.ValidationError(f"Solo hay {variant.stock} unidades disponibles de esta variante.")
                except ProductVariant.DoesNotExist:
                    raise forms.ValidationError("Variante no válida.")
            else:
                if quantity > self.product.stock:
                    raise forms.ValidationError(f"Solo hay {self.product.stock} unidades disponibles.")
        
        return cleaned_data
