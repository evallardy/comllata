from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import PasswordInput

from .models import Usuario

class UsuarioForm(UserCreationForm):
    is_active = forms.BooleanField(widget=forms.CheckboxInput)
    is_staff = forms.BooleanField(widget=forms.CheckboxInput)
    is_taller = forms.BooleanField(widget=forms.CheckboxInput)
    is_cliente = forms.BooleanField(widget=forms.CheckboxInput)
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmación', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'is_staff', 'is_taller', 'is_cliente', 'is_active', 'first_name', 'last_name',
                   'materno', 'celular', 'taller', 'email', 'password1', 'password2']
        labels = {
            'username': 'Usuario',
            'is_staff': 'Staff',
            'is_taller': 'Taller',
            'is_cliente': 'Cliente',
            'is_active': 'Activo',
            'first_name': 'Nombre',
            'last_name': 'Paterno',
            'materno': 'Materno',
            'celular': 'Celular',
            'taller': 'Taller',
            'email': 'Correo',
            'password1': 'Contraseña',
            'password2': 'Confirmación'
            }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['materno'].required = False
        self.fields['is_staff'].required = False
        self.fields['is_taller'].required = False
        self.fields['is_cliente'].required = False
        self.fields['is_active'].required = False
        self.fields['celular'].required = True
        self.fields['taller'].required = False
        self.fields['email'].required = True
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['username'].widget.attrs['autocomplete'] = 'off'
        self.fields['password1'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['password2'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['is_active'].initial = True

        for nombre, campo in self.fields.items():
            if nombre in ['is_staff', 'is_taller', 'is_cliente', 'is_active']:
                campo.widget.attrs.update({
                    'class': 'form-check-input',
                })
            else:
                campo.widget.attrs.update({
                    'class': 'form-control'
                })


class UsuarioFormEdit(forms.ModelForm):
    is_staff = forms.BooleanField(widget=forms.CheckboxInput, label='')
    is_active = forms.BooleanField(widget=forms.CheckboxInput, label='')
    is_taller = forms.BooleanField(widget=forms.CheckboxInput, label='')
    is_cliente = forms.BooleanField(widget=forms.CheckboxInput, label='')
    password = forms.CharField(
        widget=PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=False,
        label='Nueva Contraseña'
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'materno', 'is_staff', 'is_taller', 'is_cliente', 'celular', 'taller', 'email', 'is_active', 'password']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Paterno',
            'materno': 'Materno',
            'is_staff': 'Staff',
            'is_taller': 'Taller',
            'is_cliente': 'Cliente',
            'taller': 'Taller',
            'celular': 'Celular',
            'email': 'Correo',
            'is_active': 'Activo',
            'password': 'Contraseña',
            }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['materno'].required = False
        self.fields['is_staff'].required = False
        self.fields['is_taller'].required = False
        self.fields['is_cliente'].required = False
        self.fields['celular'].required = True
        self.fields['taller'].required = False
        self.fields['email'].required = True
        self.fields['is_active'].required = False
        self.fields['password'].required = False
        
        for form in self.visible_fields():
            if not (form.name == 'is_staff' or form.name == 'is_active' or form.name == 'is_taller' or form.name == 'is_cliente'):
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

class RegistrarseForm(UserCreationForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmación', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'is_cliente', 'is_active', 'first_name', 'last_name',
                  'materno', 'celular', 'email', 'password1', 'password2']
        labels = {
            'username': 'Usuario',
            'is_cliente': 'Cliente',
            'is_active': 'Activo',
            'first_name': 'Nombre',
            'last_name': 'Paterno',
            'materno': 'Materno',
            'celular': 'Celular',
            'email': 'Correo',
            'password1': 'Contraseña',
            'password2': 'Confirmación'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Reemplazar el campo username por un EmailField
        self.fields['username'] = forms.EmailField(
            label='Usuario (Correo)',
            required=True,
            widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'off'})
        )

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['materno'].required = False
        self.fields['is_cliente'].required = False
        self.fields['is_active'].required = False
        self.fields['celular'].required = True
        self.fields['email'].required = True
        self.fields['password1'].required = True
        self.fields['password2'].required = True
        self.fields['is_active'].initial = True
        self.fields['username'].widget.attrs['autocomplete'] = 'off'
        self.fields['password1'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['password2'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['is_active'].initial = True

        for nombre, campo in self.fields.items():
            if nombre in ['is_cliente', 'is_active']:
                campo.widget.attrs.update({
                    'class': 'form-check-input',
                })
            elif nombre not in ['username']:  # username ya tiene clase aplicada arriba
                campo.widget.attrs.update({
                    'class': 'form-control'
                })