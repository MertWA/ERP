from django import forms
from django.forms.models import BaseInlineFormSet # Gerekli import
from .models import Proforma
from core.models import SartSablonu

# --- YENİ EKLENEN FORMSET (VALIDASYON İÇİN) ---
class ProformaKalemiFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        
        # Eğer hata varsa veya silinecekse geç
        if any(self.errors):
            return

        # Geçerli (Dolu ve Silinmek üzere işaretlenmemiş) satırları say
        dolu_satir_sayisi = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                dolu_satir_sayisi += 1

        # Kural: En az 1 satır olmalı
        if dolu_satir_sayisi < 1:
            raise forms.ValidationError("Lütfen en az 1 ürün/hizmet kalemi ekleyiniz. Boş teklif oluşturulamaz.")

class ProformaForm(forms.ModelForm):
    sablon_secimi = forms.ModelChoiceField(
        queryset=SartSablonu.objects.all(),
        required=False,
        label="Hızlı Şart Şablonu Seç",
        help_text="Seçtiğinizde aşağıdaki şartlar otomatik dolar."
    )

    class Meta:
        model = Proforma
        fields = '__all__'