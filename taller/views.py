from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy

from .models import Taller
from .forms import TallerForm
from core.views import BaseAdministracionMixin

@method_decorator(staff_member_required(login_url='/administracion/'), name='dispatch')
class TallerListView(BaseAdministracionMixin, TemplateView):
    model = Taller
    template_name = "taller/taller_list.html"
    context_object_name = "talleres"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        talleres = Taller.objects.all().order_by('id')  # puedes cambiar el orden
        total_talleres = talleres.count()
        context['total_talleres'] = total_talleres
        context['talleres'] = talleres  # Para compatibilidad si ya usas {{ inventarios }}
        return context

@method_decorator(staff_member_required(login_url='/administracion/'), name='dispatch')
class TallerCreateView(BaseAdministracionMixin, CreateView):
    model = Taller
    form_class = TallerForm
    template_name = "taller/taller_form.html"
    success_url = reverse_lazy("taller_list")

@method_decorator(staff_member_required(login_url='/administracion/'), name='dispatch')
class TallerUpdateView(BaseAdministracionMixin, UpdateView):
    model = Taller
    form_class = TallerForm
    template_name = "taller/taller_form.html"
    success_url = reverse_lazy("taller_list")

@method_decorator(staff_member_required(login_url='/administracion/'), name='dispatch')
class TallerDeleteView(BaseAdministracionMixin, DeleteView):
    model = Taller
    template_name = "taller/taller_confirm_delete.html"
    success_url = reverse_lazy("taller_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.estatus = 0  # baja lógica
        self.object.save()
        return super().form_valid(self.get_form())
