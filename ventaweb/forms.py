from django import forms
from django.utils import timezone
from .models import ReglasComision
from almacen.models import Inventario
from decimal import Decimal

class ReglasComisionForm(forms.ModelForm):
    class Meta:
        model = ReglasComision
        fields = '__all__'
        widgets = {
            "fecha_inicial": forms.DateInput(format='%Y-%m-%d', attrs={"type": "date", "class": "form-control"}),
            "fecha_final": forms.DateInput(format='%Y-%m-%d', attrs={"type": "date", "class": "form-control"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- Campos dinámicos ---
        # Marcas únicas
        marcas = (
            Inventario.objects.exclude(marca__isnull=True)
            .exclude(marca__exact="")
            .values_list("marca", flat=True)
            .distinct()
            .order_by("marca")
        )
        self.fields["marca"] = forms.ChoiceField(
            choices=[("", "---------")] + [(m, m) for m in marcas],
            required=False,
            widget=forms.Select(attrs={"class": "form-select"})
        )

        # Rines únicos
        rines = (
            Inventario.objects.exclude(rin__isnull=True)
            .values_list("rin", flat=True)
            .distinct()
            .order_by("rin")
        )
        self.fields["rin"] = forms.TypedChoiceField(
            choices=[(None, "---------")] + [(str(r), str(r)) for r in rines if r is not None],
            required=False,
            coerce=lambda x: Decimal(x) if x not in (None, "", "None") else None,
            empty_value=None,
            widget=forms.Select(attrs={"class": "form-select"})
        )

        # Otros campos
        self.fields["talleres"].widget = forms.CheckboxInput(attrs={"class": "form-check-input"})
        self.fields["empresa"].widget.attrs.update({"class": "form-select"})
        self.fields["tipo"].widget.attrs.update({"class": "form-select"})
        self.fields["estatus"].widget.attrs.update({"class": "form-select"})

        # --- Iniciales de fecha después de construir los campos ---
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
        talleres = cleaned_data.get("talleres")
        empresa = cleaned_data.get("empresa")
        rin = cleaned_data.get("rin")
        marca = cleaned_data.get("marca")
        cantidad = cleaned_data.get("cantidad")

        if talleres:
            if empresa or rin or marca:
                self.add_error(None, "Selecciona talleres o un taller (marca o rin)")
        else:
            if empresa or rin or marca:
                if not empresa:
                    self.add_error('empresa', "Selecciona un taller para la marca o rin")
            else:
                self.add_error(None, "Selecciona talleres o un taller (marca o rin)")

        if cantidad is not None and cantidad <= 0:
            self.add_error('cantidad', "La cantidad debe ser mayor a 0")


        if fecha_inicial and fecha_final:
            if fecha_final < fecha_inicial:
                self.add_error('fecha_final', "La fecha final debe ser mayor o igual a la inicial.")
            if fecha_final < hoy:
                self.add_error('fecha_inicial', "La fecha inicial debe ser mayor o igual a hoy.")
        else:
            self.add_error(None, "Falta fecha inicial o fecha final.")
        return cleaned_data
