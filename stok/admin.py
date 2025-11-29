from django.contrib import admin
from django.utils.html import format_html
from .models import Urun, Kategori
from simple_history.admin import SimpleHistoryAdmin

@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('ad',)

@admin.register(Urun)
class UrunAdmin(SimpleHistoryAdmin):
    # 'para_birimi' alanını listeye ekledik
    list_display = ('kod', 'ad', 'kategori', 'satis_fiyati', 'para_birimi', 'stok_miktari', 'bakim_periyodu', 'stok_gorsel', 'aktif')
    
    list_filter = ('kategori', 'aktif', 'para_birimi') # Filtreye de ekledik
    search_fields = ('kod', 'ad')
    list_editable = ('stok_miktari', 'satis_fiyati')

    fieldsets = (
        ('Ürün Bilgileri', {
            'fields': ('kategori', 'kod', 'ad', 'para_birimi', 'satis_fiyati', 'aktif')
        }),
        ('Stok & Servis', {
            'fields': ('stok_miktari', 'kritik_stok_seviyesi', 'bakim_periyodu'),
            'classes': ('collapse',),
        }),
    )
    change_form_template = 'admin/stok/urun/change_form.html'

    class Media:
        js = ('js/stok_admin.js',) # Yeni JS dosyası
        css = {'all': ('css/admin_custom.css',)}
    class Media:
        js = ('js/stok_admin.js',) # Yeni JS dosyası
        css = {'all': ('css/admin_custom.css',)} # Ortak stil
    def stok_gorsel(self, obj):
        durum = obj.stok_durumu_html()
        if durum == "stok_yok":
            renk, mesaj, ikon = "red", "TÜKENDİ", "❌"
        elif durum == "kritik":
            renk, mesaj, ikon = "orange", "KRİTİK", "⚠️"
        else:
            renk, mesaj, ikon = "green", "OK", "✅"
        return format_html(f'<span style="color: {renk}; font-weight: bold;">{ikon} {mesaj}</span>')
    stok_gorsel.short_description = "Durum"