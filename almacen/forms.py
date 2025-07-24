from django import forms
from .models import Inventario

class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = '__all__'
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'producto_clave': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'existencia': forms.NumberInput(attrs={'class': 'form-control'}),
            'ancho': forms.NumberInput(attrs={'class': 'form-control'}),
            'alto': forms.NumberInput(attrs={'class': 'form-control'}),
            'rin': forms.NumberInput(attrs={'class': 'form-control'}),
            'estatus': forms.Select(attrs={'class': 'form-select'}),
            'actualizado': forms.Select(attrs={'class': 'form-select'}),
            'talleres': forms.Select(attrs={'class': 'form-select'}),
            'llantas': forms.Select(attrs={'class': 'form-select'}),
        }
