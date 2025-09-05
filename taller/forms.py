from django import forms
from .models import Taller

class TallerForm(forms.ModelForm):
    class Meta:
        model = Taller
        fields = '__all__'
        widgets = {
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'imagen':  # todos menos imagen
                field.widget.attrs.update({'class': 'form-control'})