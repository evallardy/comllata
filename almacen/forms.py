from django import forms
from .models import Inventario

class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['descripcion', 'producto_clave', 'precio', 'existencia', 'ancho',
                  'alto', 'rin','estatus', 'imagen', 'empresa']

        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'producto_clave': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'existencia': forms.NumberInput(attrs={'class': 'form-control'}),
            'ancho': forms.NumberInput(attrs={'class': 'form-control'}),
            'alto': forms.NumberInput(attrs={'class': 'form-control'}),
            'rin': forms.NumberInput(attrs={'class': 'form-control'}),
            'estatus': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(InventarioForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        self.fields["empresa"].widget.attrs.update({"class": "form-select"})
        self.fields["estatus"].widget.attrs.update({"class": "form-select"})