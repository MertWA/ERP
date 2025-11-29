from django import forms
from core.models import FormYapilandirma
from .models import Musteri

class MusteriDinamikForm(forms.ModelForm):
    class Meta:
        model = Musteri
        fields = '__all__'
        exclude = ('ekstra_bilgiler',)

    def __init__(self, *args, **kwargs):
        super(MusteriDinamikForm, self).__init__(*args, **kwargs)
        
        # 1. ADIM: ÖNCE ALANLARI OLUŞTUR (Core Ayarlarından)
        ayarlar = FormYapilandirma.objects.first()
        if ayarlar:
            for alan in ayarlar.alanlar.all().order_by('sira'):
                field_args = {
                    'label': alan.baslik,
                    'required': alan.zorunlu,
                }
                
                # Input tipine göre alanı yarat
                if alan.input_type == 'CharField':
                    self.fields[alan.baslik] = forms.CharField(**field_args)
                elif alan.input_type == 'TextField':
                    self.fields[alan.baslik] = forms.CharField(widget=forms.Textarea, **field_args)
                elif alan.input_type == 'IntegerField':
                    self.fields[alan.baslik] = forms.IntegerField(**field_args)
                elif alan.input_type == 'DateField':
                    self.fields[alan.baslik] = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), **field_args)
                else:
                    self.fields[alan.baslik] = forms.CharField(**field_args)

        # 2. ADIM: SONRA VERİYİ YÜKLE (Eğer düzenleme modundaysak)
        if self.instance.pk and self.instance.ekstra_bilgiler:
            for key, value in self.instance.ekstra_bilgiler.items():
                # JSON'daki anahtar bizim formda yarattığımız alanla eşleşiyor mu?
                if key in self.fields:
                    self.fields[key].initial = value

    def save(self, commit=True):
        instance = super(MusteriDinamikForm, self).save(commit=False)
        
        ayarlar = FormYapilandirma.objects.first()
        if ayarlar:
            dinamik_veri = {}
            for alan in ayarlar.alanlar.all():
                if alan.baslik in self.cleaned_data:
                    deger = self.cleaned_data[alan.baslik]
                    # Tarih verisini string formatına çevir
                    if hasattr(deger, 'isoformat'):
                        deger = deger.isoformat()
                    dinamik_veri[alan.baslik] = deger
            
            instance.ekstra_bilgiler = dinamik_veri

        if commit:
            instance.save()
        return instance