from django import forms
from django.utils import timezone

from .models import Aviso

class AvisoForm(forms.ModelForm):
    class Meta:
        model = Aviso
        fields = ['tipo', 'aviso', 'icono', 'fecha_inicial', 'fecha_final']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'aviso': forms.TextInput(attrs={'class': 'form-control'}),
            'icono': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicial': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_final': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            if self.instance.fecha_inicial:
                self.fields['fecha_inicial'].initial = self.instance.fecha_inicial
            if self.instance.fecha_final:
                self.fields['fecha_final'].initial = self.instance.fecha_final

    def clean(self):    
        cleaned_data = super().clean()
        fecha_inicial = cleaned_data.get("fecha_inicial")
        fecha_final = cleaned_data.get("fecha_final")
        hoy = timezone.localdate()

        if fecha_inicial and fecha_final:
            if fecha_final < fecha_inicial:
                self.add_error('fecha_final', "La fecha final debe ser mayor o igual a la inicial.")
            if fecha_final < hoy:
                self.add_error('fecha_inicial', "La fecha inicial debe ser mayor o igual a hoy.")
        else:
            self.add_error(None, "Falta fecha inicial o fecha final.")
        return cleaned_data