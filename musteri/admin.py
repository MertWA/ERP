from django.contrib import admin
from django.db.models import Q
from .models import Musteri
from .forms import MusteriDinamikForm
from core.models import FormYapilandirma

@admin.register(Musteri)
class MusteriAdmin(admin.ModelAdmin):
    form = MusteriDinamikForm
    exclude = ('ekstra_bilgiler',)
    
    # Varsayılan arama çubuğunu aktif etmek için en az bir alan şart.
    # Biz ID'yi koyuyoruz, dinamik olanları aşağıda kodla ekleyeceğiz.
    search_fields = ['id'] 

    def get_search_results(self, request, queryset, search_term):
        """
        Standart aramayı JSON verilerini de kapsayacak şekilde genişletiyoruz.
        """
        # 1. Önce standart aramayı (ID araması) yap
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        if not search_term:
            return queryset, use_distinct

        # 2. Core ayarlarından "Arama Yapılsın mı?" seçili alanları bul
        try:
            ayarlar = FormYapilandirma.objects.first()
        except:
            return queryset, use_distinct

        if ayarlar:
            arama_aktif_alanlar = ayarlar.alanlar.filter(arama_varmi=True)
            
            if arama_aktif_alanlar.exists():
                # Dinamik bir sorgu (OR mantığı ile) oluşturuyoruz
                q_objects = Q()
                
                for alan in arama_aktif_alanlar:
                    # JSON içinde arama syntax'ı: ekstra_bilgiler__Anahtar__icontains
                    lookup_key = f"ekstra_bilgiler__{alan.baslik}__icontains"
                    
                    # Sorguya ekle (OR | operatörü ile)
                    q_objects |= Q(**{lookup_key: search_term})
                
                # Mevcut sonuçlarla (ID araması) birleştiriyoruz
                # Yani: (ID içinde bul) VEYA (JSON içinde bul)
                queryset |= self.model.objects.filter(q_objects)

        return queryset, use_distinct

    # --- ÖNCEKİ KODLARIN AYNISI (Listeleme ve Form) ---

    def get_list_display(self, request):
        standart_bas = ['__str__']
        standart_son = ['olusturulma_tarihi']
        dinamik_sutun_isimleri = []

        try:
            ayarlar = FormYapilandirma.objects.first()
        except:
            ayarlar = None

        if ayarlar:
            aktif_alanlar = ayarlar.alanlar.filter(listede_goster=True).order_by('sira')
            for alan in aktif_alanlar:
                func_name = f"col_{alan.id}"
                def getter(obj, k=alan.baslik):
                    return obj.ekstra_bilgiler.get(k, "-")
                
                getter.short_description = alan.baslik
                getter.admin_order_field = None
                setattr(self, func_name, getter)
                dinamik_sutun_isimleri.append(func_name)
        
        return standart_bas + dinamik_sutun_isimleri + standart_son

    def get_form(self, request, obj=None, **kwargs):
        kwargs['fields'] = None
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        dinamik_alanlar = []
        ayarlar = FormYapilandirma.objects.first()
        if ayarlar:
            for alan in ayarlar.alanlar.all().order_by('sira'):
                dinamik_alanlar.append(alan.baslik)
        
        if not dinamik_alanlar:
            return super().get_fieldsets(request, obj)

        return [('Müşteri Bilgileri', {'fields': dinamik_alanlar})]