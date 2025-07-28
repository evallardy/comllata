from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from .models import Inventario
from .forms import InventarioForm
from core.views import BaseAdministracionMixin

class InventarioListView(BaseAdministracionMixin, TemplateView):
    model = Inventario
    template_name = 'almacen/inventario_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventarios = Inventario.objects.all()  # puedes cambiar el orden
        paginator = Paginator(inventarios, 100)  # 10 por página

        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['inventarios'] = page_obj.object_list  # Para compatibilidad si ya usas {{ inventarios }}
        return context

class InventarioCreateView(BaseAdministracionMixin, CreateView):
    model = Inventario
    form_class = InventarioForm
    template_name = 'almacen/inventario_form.html'
    success_url = reverse_lazy('inventario_list')

class InventarioUpdateView(BaseAdministracionMixin, UpdateView):
    model = Inventario
    form_class = InventarioForm
    template_name = 'almacen/inventario_form.html'
    success_url = reverse_lazy('inventario_list')

class InventarioDeleteView(BaseAdministracionMixin, DeleteView):
    model = Inventario
    template_name = 'almacen/inventario_confirm_delete.html'
    success_url = reverse_lazy('inventario_list')
