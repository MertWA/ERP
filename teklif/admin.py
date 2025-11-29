from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import TextInput, Select
from django.utils import timezone
from .models import Proforma, ProformaKalemi, MailLog
from .forms import ProformaForm, ProformaKalemiFormSet
from simple_history.admin import SimpleHistoryAdmin

class ProformaKalemiInline(admin.TabularInline):
    model = ProformaKalemi
    formset = ProformaKalemiFormSet
    extra = 1
    autocomplete_fields = ['urun']
    fields = ('urun', 'aciklama', 'miktar', 'kdv_orani', 'satir_toplami_goster')
    readonly_fields = ('satir_toplami_goster',)

    def satir_toplami_goster(self, obj):
        if obj.pk and obj.urun:
            guncel_fiyat = obj.urun.satis_fiyati
            sembol = obj.urun.para_birimi.kod if obj.urun.para_birimi else "TL"
            tutar = obj.miktar * guncel_fiyat
            return f"{tutar:,.2f} {sembol}"
        return "-"
    satir_toplami_goster.short_description = "Guncel Tutar"

class MailLogInline(admin.TabularInline):
    model = MailLog
    extra = 0
    readonly_fields = ('gonderilen_adres', 'gonderim_zamani')
    can_delete = False
    verbose_name = "Mail Gonderim Gecmisi"
    verbose_name_plural = "Mail Gonderim Gecmisi"
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Proforma)
class ProformaAdmin(SimpleHistoryAdmin):
    form = ProformaForm
    list_display = ('kod', 'musteri_link', 'tarih', 'durum', 'toplam_tutar_hesapla', 'mail_durumu', 'islemler')
    list_filter = ('tarih', 'durum')
    search_fields = ('kod', 'musteri__ad_soyad')
    list_editable = ("durum",)
    
    inlines = [ProformaKalemiInline, MailLogInline]
    autocomplete_fields = ['musteri']
    readonly_fields = ('kod_goster',)
    
    change_form_template = 'admin/teklif/proforma/change_form.html'

    fieldsets = (
        ('Genel Bilgiler', {
            'fields': (
                'kod_goster', 'durum', 'musteri', 'tarih', 'gecerlilik_tarihi', 'sablon_secimi'
            )
        }),
        ('Notlar', {
            'classes': ('collapse',),
            'fields': ('notlar', 'firma_ici_not')
        }),
    )

    class Media:
        js = ('js/teklif_admin.js',)
        css = {'all': ('css/admin_custom.css',)}

    def get_readonly_fields(self, request, obj=None):
        ro_fields = list(self.readonly_fields)
        if not obj: 
            ro_fields.append('durum') 
        return ro_fields

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['tarih'] = timezone.now().date()
        return initial

    def kod_goster(self, obj=None):
        if obj and obj.kod: return obj.kod
        return format_html('<span style="color:#999; font-style:italic;">(Otomatik Olusturulur)</span>')
    kod_goster.short_description = "Teklif No"

    def musteri_link(self, obj): return obj.musteri
    musteri_link.short_description = "Musteri"

    def toplam_tutar_hesapla(self, obj):
        toplam = 0
        sembol = "TL"
        kalemler = obj.kalemler.all()
        if kalemler.exists() and kalemler.first().urun and kalemler.first().urun.para_birimi:
            sembol = kalemler.first().urun.para_birimi.kod
            
        for kalem in kalemler:
            if kalem.urun:
                toplam += kalem.miktar * kalem.urun.satis_fiyati
        return f"{toplam:,.2f} {sembol}"
    toplam_tutar_hesapla.short_description = "Toplam"

    def mail_durumu(self, obj):
        sent_count = obj.mail_logs.values('gonderilen_adres').distinct().count()
        if sent_count > 0:
            return format_html('<span class="badge badge-success" style="font-size:11px;">Mail Iletildi</span>')
        return format_html('<span class="badge badge-secondary" style="font-size:11px;">Bekliyor</span>')
    mail_durumu.short_description = "Mail Durumu"

    def islemler(self, obj):
        pdf_url = reverse('proforma_pdf', args=[obj.pk])
        mail_url = reverse('proforma_mail', args=[obj.pk])
        preview_url = reverse('proforma_preview', args=[obj.pk])
        
        if obj.mail_gonderim_tarihi:
            btn_text, btn_cls = "Tekrar", "btn-outline-secondary"
        else:
            btn_text, btn_cls = "Gönder", "btn-warning"

        servis_html = ""
        if obj.durum == 'onaylandi':
            # BAĞLI SERVİS VAR MI KONTROLÜ
            # related_name kullanmadığımız için (ServisKaydi modelinde ilgili_proforma var)
            # ters ilişki: serviskaydi_set
            mevcut_servis = obj.serviskaydi_set.first()
            
            if mevcut_servis:
                # Servis varsa GÖRÜNTÜLE butonu (Mavi)
                servis_url = reverse('admin:servis_serviskaydi_change', args=[mevcut_servis.pk])
                servis_html = f'''<a class="btn btn-info btn-sm" href="{servis_url}" title="Servis Kaydına Git" style="border-radius:4px; box-shadow:0 2px 4px rgba(0,0,0,0.1);"><i class="fas fa-external-link-alt"></i> Servis</a>'''
            else:
                # Yoksa OLUŞTUR butonu (Yeşil)
                servis_create_url = reverse('create_service_from_proforma', args=[obj.pk])
                servis_html = f'''<a class="btn btn-success btn-sm" href="{servis_create_url}" title="Servis Oluştur" style="border-radius:4px; box-shadow:0 2px 4px rgba(0,0,0,0.1);"><i class="fas fa-tools"></i> Servis</a>'''

        common_style = "border-radius:4px; margin-right:4px; box-shadow:0 2px 4px rgba(0,0,0,0.1);"

        return format_html(
            '''
            <div style="display:flex; align-items:center;">
                <button type="button" class="btn btn-primary btn-sm preview-modal-btn" data-url="{preview_url}" title="Hızlı Önizleme" style="{style}"><i class="fas fa-eye"></i></button>
                <button type="button" class="btn btn-dark btn-sm pdf-modal-btn" data-url="{pdf_url}" title="PDF Oluştur" style="{style}"><i class="fas fa-file-pdf"></i></button>
                <button type="button" class="btn {btn_cls} btn-sm mail-gonder-btn" data-url="{mail_url}" title="Mail Gönder" style="{style} font-weight:600;"><i class="fas fa-paper-plane"></i> {btn_text}</button>
                {servis_btn}
            </div>
            ''',
            preview_url=preview_url, pdf_url=pdf_url, btn_cls=btn_cls, mail_url=mail_url, btn_text=btn_text, style=common_style, servis_btn=mark_safe(servis_html)
        )
    islemler.short_description = "Hızlı İşlemler"