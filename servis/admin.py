from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ServisKaydi, YapilanIslem, ServisUrunleri, BakimPlani, ServisMailLog, BakimGecmisi
from teklif.models import Proforma
from simple_history.admin import SimpleHistoryAdmin

# ... (Inline'lar AYNI: YapilanIslemInline, ServisUrunleriInline, ServisMailLogInline) ...
class YapilanIslemInline(admin.TabularInline):
    model = YapilanIslem
    extra = 1
    verbose_name = "İşlem"
    verbose_name_plural = "Yapılacak İşlemler Listesi"
    fields = ('aciklama', 'tamamlandi')

class ServisUrunleriInline(admin.TabularInline):
    model = ServisUrunleri
    extra = 1
    verbose_name = "Ürün"
    verbose_name_plural = "Servis Yapılacak Ürünler"
    autocomplete_fields = ['urun']

class ServisMailLogInline(admin.TabularInline):
    model = ServisMailLog
    extra = 0
    readonly_fields = ('gonderilen_adres', 'gonderim_zamani')
    can_delete = False
    verbose_name = "Mail Gönderim Geçmişi"
    verbose_name_plural = "Mail Gönderim Geçmişi"
    def has_add_permission(self, request, obj=None): return False

@admin.register(ServisKaydi)
class ServisKaydiAdmin(admin.ModelAdmin):
    list_display = ('fis_no', 'musteri', 'teknisyen_listesi', 'durum', 'planlanan_tarih', 'imza_goster', 'hizli_islemler')
    list_filter = ('durum', 'planlanan_tarih')
    search_fields = ('fis_no', 'musteri__ad_soyad', 'konu')
    
    list_editable = ('durum',)
    
    autocomplete_fields = ['musteri', 'ilgili_proforma']
    
    inlines = [ServisUrunleriInline, YapilanIslemInline, ServisMailLogInline]
    
    readonly_fields = ('fis_no', 'imza_goster')
    filter_horizontal = ('teknisyenler',) 

    fieldsets = (
        ('Servis Künyesi', {
            'fields': (
                'fis_no', 
                'ilgili_proforma', 
                'durum',
                'musteri', 
                'planlanan_tarih'
            )
        }),
        ('Görevlendirme', {
            'fields': ('teknisyenler',)
        }),
        ('Arıza & Detay', {
            'fields': ('konu', 'aciklama', 'firma_ici_not')
        }),
        ('İmza', { 
            'fields': ('imza_atan_kisi', 'musteri_imzasi') 
        }),
    )

    class Media:
        js = (
            'https://cdn.jsdelivr.net/npm/signature_pad@4.0.0/dist/signature_pad.umd.min.js',
            'js/servis_list.js',
        )
        css = {'all': ('css/admin_custom.css',)}

    # --- YENİ EKLENEN METOT: READONLY MANTIĞI ---
    def get_readonly_fields(self, request, obj=None):
        # Mevcut readonly alanları al (fis_no, imza_goster)
        ro_fields = list(self.readonly_fields)
        
        if obj: # Eğer düzenleme sayfasındaysak (Kayıt varsa)
            # Ve eğer bu servisin bağlı bir proforması varsa
            if obj.ilgili_proforma:
                ro_fields.append('ilgili_proforma') # Değiştirilemez yap
                
            # Ayrıca Müşteri de değiştirilmemeli bence (Mantık bütünlüğü için)
            # İstersen aşağıdaki satırı silebilirsin
            ro_fields.append('musteri') 
            
        return ro_fields

    def teknisyen_listesi(self, obj):
        tek_list = [t.get_full_name() or t.username for t in obj.teknisyenler.all()]
        if not tek_list: return "-"
        return format_html("<br>".join(tek_list))
    teknisyen_listesi.short_description = "Teknisyenler"

    def imza_goster(self, obj):
        if obj.musteri_imzasi:
            return format_html(f'<img src="{obj.musteri_imzasi}" class="imza-popup-trigger" data-ad="{obj.imza_atan_kisi or ""}" style="height:30px; border:1px solid #ccc; background:#fff; cursor:zoom-in;">')
        return "-"
    imza_goster.short_description = "İmza"

    def hizli_islemler(self, obj):
        imza_renk = "btn-success" if obj.musteri_imzasi else "btn-secondary"
        imza_ikon = "fas fa-check-double" if obj.musteri_imzasi else "fas fa-signature"
        
        html_content = f'''
            <div style="white-space:nowrap;">
                <button type="button" class="btn btn-info btn-sm btn-checklist" data-id="{obj.pk}" title="İşlemler"><i class="fas fa-tasks"></i></button>
                <button type="button" class="btn {imza_renk} btn-sm btn-imza" data-id="{obj.pk}" title="İmza"><i class="{imza_ikon}"></i></button>
        '''

        if obj.durum in ['tamamlandi']:
            pdf_url = reverse('servis_pdf', args=[obj.pk])
            mail_url = reverse('servis_mail', args=[obj.pk])
            
            btn_mail_cls = "btn-dark" if obj.mail_gonderim_tarihi else "btn-warning"
            btn_mail_text = "Tekrar" if obj.mail_gonderim_tarihi else "Gönder"
            btn_mail_style = "color:white !important;" if obj.mail_gonderim_tarihi else "color:#333; font-weight:bold;"

            html_content += f'''
                <button type="button" class="btn btn-secondary btn-sm pdf-modal-btn" data-url="{pdf_url}" title="Form Yazdır"><i class="fas fa-print"></i></button>
                <button type="button" class="btn {btn_mail_cls} btn-sm mail-gonder-btn" data-url="{mail_url}" style="{btn_mail_style}"><i class="fas fa-paper-plane"></i> {btn_mail_text}</button>
            '''

        html_content += '</div>'
        return format_html(html_content)

    hizli_islemler.short_description = "Hızlı İşlemler"
    change_form_template = 'admin/servis/serviskaydi/change_form.html'
    
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        proforma_id = request.GET.get('proforma_id')
        if proforma_id:
            try:
                proforma = Proforma.objects.get(pk=proforma_id)
                initial['ilgili_proforma'] = proforma
                initial['musteri'] = proforma.musteri
                initial['konu'] = f"{proforma.kod} referanslı servis kaydı"
            except: pass
        return initial

class BakimGecmisiInline(admin.TabularInline):
    model = BakimGecmisi
    extra = 0
    readonly_fields = ('servis', 'tarih', 'olusturulan_sonraki_tarih')
    can_delete = False
    verbose_name = "Bakım Geçmişi"
    verbose_name_plural = "Bakım Geçmişi"
    def has_add_permission(self, request, obj=None): return False

@admin.register(BakimPlani)
class BakimPlaniAdmin(admin.ModelAdmin):
    list_display = ('musteri', 'urun', 'son_bakim_tarihi', 'durum_cubugu', 'gelecek_bakim_tarihi', 'kalan_gun_goster')
    list_filter = ('gelecek_bakim_tarihi', 'urun')
    search_fields = ('musteri__ad_soyad', 'urun__ad')
    
    # Inline Eklendi
    inlines = [BakimGecmisiInline]

    def kalan_gun_goster(self, obj):
        kalan = obj.kalan_gun()
        if kalan < 0: return format_html(f'<span style="color:red; font-weight:bold;">{abs(kalan)} Gün Gecikti!</span>')
        elif kalan <= 30: return format_html(f'<span style="color:orange; font-weight:bold;">{kalan} Gün Kaldı</span>')
        return f"{kalan} Gün"
    kalan_gun_goster.short_description = "Durum"

    def durum_cubugu(self, obj):
        kalan = obj.kalan_gun()
        periyot = obj.urun.bakim_periyodu * 30 
        if periyot == 0: periyot = 365
        gecen = periyot - kalan
        yuzde = (gecen / periyot) * 100
        if yuzde > 100: yuzde = 100
        if yuzde < 0: yuzde = 0
        renk = "success"
        if kalan < 30: renk = "warning"
        if kalan < 0: renk = "danger"
        return format_html(f'<div class="progress" style="height: 20px; width:100px; background:#e9ecef;"><div class="progress-bar bg-{renk}" role="progressbar" style="width: {yuzde}%"></div></div>')
    durum_cubugu.short_description = "Periyot"