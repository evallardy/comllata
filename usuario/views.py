from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Permission
from django.http import JsonResponse
from django.contrib.auth.views import LoginView

from usuario.models import Usuario
from .forms import UsuarioForm, UsuarioFormEdit, CambiaContrasenaForm, RegistrarseForm
from core.views import BaseAdministracionMixin

class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        if user.is_cliente:
            return '/'  # Redirige a dashboard de cliente
        elif user.is_staff or user.is_taller:
            return '/administracion/'  # Redirige a dashboard de admin o taller
        return '/'  # Redirige a home o login si no cumple nada

def custom_logout_view(request):
    if request.user.is_authenticated:
        if request.user.is_cliente:
            logout(request)
            return redirect('login_cliente')
        elif request.user.is_staff or request.user.is_taller:
            logout(request)
            return redirect('login_admin')
    logout(request)
    return redirect('/')

class usuarios(BaseAdministracionMixin, LoginRequiredMixin, ListView):
    model = Usuario
    template_name = 'usuario/usuarios.html'
    context_object_name = 'usuarios'
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = Usuario.objects.exclude(username='iagevm').exclude(username='jcamarillo').exclude(username='evallardy')
        # Puedes realizar filtros o manipulaciones adicionales en el queryset si es necesario
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuarios_perm'] = self.request.user.has_perm('core.usuarios')
        context['crea_usuario_perm'] = self.request.user.has_perm('core.crea_usuario')
        context['modifica_usuario_perm'] = self.request.user.has_perm('core.modifica_usuario')
        context['total_usuarios'] = Usuario.objects.exclude(username='iagevm').exclude(username='jcamarillo').exclude(username='evallardy').count()
        return context

class UserUpdateView(BaseAdministracionMixin, LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioFormEdit
    template_name = 'usuario/usuario.html'
    success_url = reverse_lazy('usuarios')  # URL de éxito después de guardar

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk', '0')
        usuario_sel = Usuario.objects.filter(id=pk).first()
        usuario = usuario_sel.username
        context['modifica_usuario_perm'] = self.request.user.has_perm('core.modifica_usuario')
        context['usuario'] = usuario
        return context

    def post(self, request, *args, **kwargs):
        # Intentar obtener el usuario a actualizar
        user = self.get_object()  # Obtén el usuario a actualizar

        # Obtener los datos del formulario manualmente
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.celular = request.POST.get('celular')
        user.email = request.POST.get('email')
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_cliente = request.POST.get('is_cliente') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_taller = request.POST.get('is_taller') == 'on'
        user.empresa_id = request.POST.get('empresa')

        password = request.POST.get('password')
        # Actualizar la contraseña solo si se proporciona un nuevo valor
        if password:
            user.set_password(password)  # Establece la nueva contraseña
            update_session_auth_hash(request, user)  # Mantiene la sesión activa

        user.save()  # Guarda el usuario para que se aplique la nueva contraseña

        return HttpResponseRedirect(reverse('usuarios'))

#login_required
#def registro(request):
#    data = {
#        'form': UsuarioForm
#    }
#    if request.method == 'POST':
#        formulario = UsuarioForm(data=request.POST)
#        if formulario.is_valid():
#            formulario.save()
#            return redirect(to="usuarios")
#        data["form"] = formulario
#    return render(request, 'usuario/registro.html', data)

class RegistroUsuarioView(BaseAdministracionMixin, LoginRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = "usuario/registro.html"
    success_url = reverse_lazy("usuarios")  # Redirige al listado de usuarios

    # Opcional: agregar contexto extra si quieres
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Registrar Usuario"
        return context

class Cambiar_contrasena(BaseAdministracionMixin, LoginRequiredMixin, View):
    template_name = 'usuario/cambiar_contrasena.html'
    form_class = CambiaContrasenaForm
    success_url = reverse_lazy("index")

    def get(self, request, *args, **kwargs ):
        return render(request, self.template_name, {'form': self.form_class})
    
    def post(self, request, *args, **kwargs ):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = Usuario.objects.filter(id=request.user.id)
            if user.exists(): 
                user = user.first()
                user.set_password(form.cleaned_data.get('password1'))
                user.save()
                return redirect(self.success_url)
            return redirect(self.success_url)
        else:
            form = self.form_class(request.POST)
            return render(request, self.template_name, {'form': form})

class Permisos_usuario(BaseAdministracionMixin, LoginRequiredMixin, View):
    template_name = 'usuario/permisos_usuario.html'
    def get(self, request):
        # Obtener todos los usuarios y permisos
        users = Usuario.objects.filter(is_active=1).exclude(username=self.request.user.username) \
            .exclude(username='iagevm').exclude(username='jcamarillo').exclude(cliente=1)
        # Renderizar el formulario con los datos necesarios
        context = {
            'users': users,
        }
        context['accesos_perm'] = self.request.user.has_perm('core.accesos')
        context['accesos_modificar_perm'] = self.request.user.has_perm('core.accesos_modificar')
        return render(request, self.template_name, context)
    def post(self, request):
        # Obtener el ID del usuario seleccionado y los permisos asignados
        user_id = request.POST.get('usuario', None)
        if user_id is None or user_id == '0':
            pass
        else:
            permissions = request.POST.getlist('permissions', [])

            # Actualizar los permisos del usuario seleccionado
            if user_id:
                try:
                    user = Usuario.objects.get(id=user_id)
                    user.user_permissions.set(permissions)
                except User.DoesNotExist:
                    pass
        # Redirigir a la página de éxito o a alguna otra página
        return HttpResponseRedirect(reverse('accesos'))

@login_required
def todos_permisos(request, id):
    user = Usuario.objects.get(id=id)
    usuario_permisos = set(user.user_permissions.values_list('id', flat=True))
    contable_permissions = Permission.objects.filter(content_type__model='usuario').exclude(codename__startswith='Can ').order_by('codename')
    permisos = list(Permission.objects.filter(content_type__model='usuario').exclude(name__startswith='Can ').values().order_by('name'))
    data = {
        'permisos': permisos,
        'usuario_permisos': list(usuario_permisos),
    }
    return JsonResponse(data)

def registrarse(request):
    data = {
        'form': RegistrarseForm
    }
    if request.method == 'POST':
        formulario = UsuarioForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="home")
        data["form"] = formulario
    return render(request, 'usuario/registrarse.html', data)
