from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import PasswordInput

from .models import Usuario

class UsuarioForm(UserCreationForm):
    cliente = forms.BooleanField(widget=forms.CheckboxInput)

    class Meta:
        model = Usuario
        fields = ['username', 'cliente', 'first_name', 'last_name', 'celular', 'email', 'password1', 'password2']
        labels = {
            'username': 'Usuario',
            'Cliente': 'Cliente',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'celular': 'Celular',
            'email': 'Correo',
            'password1': 'Contraseña',
            'password2': 'Confirmación'
            }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['cliente'].required = False
        self.fields['celular'].required = True
        self.fields['email'].required = True
        self.fields['password1'].required = False
        self.fields['password2'].required = False

class UsuarioFormEdit(forms.ModelForm):
    cliente = forms.BooleanField(widget=forms.CheckboxInput, label='')
    is_active = forms.BooleanField(widget=forms.CheckboxInput, label='')
    password = forms.CharField(
        widget=PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=False,
        label='Nueva Contraseña'
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'cliente', 'celular', 'email', 'is_active', 'password']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'cliente': 'Cliente',
            'celular': 'Celular',
            'email': 'Correo',
            'is_active': 'Activo',
            }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['cliente'].required = False
        self.fields['celular'].required = True
        self.fields['email'].required = True
        self.fields['is_active'].required = False
        
        for form in self.visible_fields():
            if not (form.name == 'cliente' or form.name == 'is_active'):
                form.field.widget.attrs['class'] = 'form-control'


class CambiaContrasenaForm(forms.Form):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs = {
                'class': 'form-control',
                'placeholder': 'Ingrese su nueva contraseña...',
                'id':'password1',
                'required': 'required',
            }
        )
    )   
    password2 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs = {
                'class': 'form-control',
                'placeholder': 'Confirme nueva contraseña...',
                'id':'password2',
                'required': 'required',
            }
        )
    )
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Contraseñas no coinciden !')
        return password2
