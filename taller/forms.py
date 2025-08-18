from django import forms
from .models import Taller

class TallerForm(forms.ModelForm):
    class Meta:
        model = Taller
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TallerForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})