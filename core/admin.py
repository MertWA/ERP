from django.contrib import admin
from django.utils.safestring import mark_safe 
from .models import FormYapilandirma, AlanTanim, PdfAyarlari, SartMaddesi, SartSablonu,DovizKuru,UserProfile
from .services import tcmb_kur_guncelle
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django.urls import path
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class AlanTanimInline(admin.TabularInline):
    model = AlanTanim
    extra = 1
    fields = ('baslik', 'input_type', 'zorunlu', 'listede_goster', 'arama_varmi', 'sira')

@admin.register(FormYapilandirma)
class FormYapilandirmaAdmin(admin.ModelAdmin):
    inlines = [AlanTanimInline]
    list_display = ('__str__',)
    
    fieldsets = (
        ('Genel', {'fields': ('kullanim_kilavuzu',)}),
    )
    readonly_fields = ('kullanim_kilavuzu',)

    def kullanim_kilavuzu(self, instance):
        return mark_safe(
            """
            <style>
                /* Ana Kutu Stili */
                .rehber-kutusu {
                    background-color: #fff;
                    border: 1px solid #dee2e6;
                    border-left: 5px solid #6c757d; /* Sol şerit */
                    border-radius: 4px;
                    padding: 0; /* İç boşluğu kaldırdık, satırlara vereceğiz */
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }
                
                /* Başlık Kısmı */
                .rehber-baslik {
                    background-color: #f8f9fa;
                    padding: 15px 20px;
                    border-bottom: 1px solid #dee2e6;
                    margin: 0;
                    font-size: 16px;
                    font-weight: 600;
                    color: #343a40;
                }

                /* Liste Yapısı */
                .rehber-liste {
                    list-style: none;
                    margin: 0;
                    padding: 0;
                }

                /* Her Bir Satır (Flexbox ile Hizalama) */
                .rehber-satir {
                    display: flex; /* Yan yana diz */
                    align-items: flex-start; /* Üstten hizala */
                    padding: 12px 20px;
                    border-bottom: 1px solid #f1f3f5;
                }
                .rehber-satir:last-child {
                    border-bottom: none;
                }

                /* Sol Taraftaki Etiket (Badge) */
                .rehber-etiket {
                    flex: 0 0 140px; /* Genişliği 140px'e sabitle */
                    margin-right: 20px;
                }
                .badge-gri {
                    display: block;
                    background-color: #e9ecef;
                    color: #495057;
                    padding: 6px 10px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 700;
                    text-align: center;
                    border: 1px solid #dee2e6;
                }

                /* Sağ Taraftaki Açıklama */
                .rehber-aciklama {
                    flex: 1; /* Kalan boşluğu doldur */
                    font-size: 13px;
                    color: #212529;
                    line-height: 1.6;
                    padding-top: 4px; /* Badge ile hizalamak için ufak boşluk */
                }

                /* Veri Tipi Alt Listesi */
                .alt-liste {
                    margin-top: 5px;
                    padding-left: 0;
                    list-style: none;
                    font-size: 12px;
                    color: #6c757d;
                }
                .alt-liste li {
                    margin-bottom: 2px;
                }
                .alt-liste strong {
                    color: #495057;
                }
            </style>

            <div class="rehber-kutusu">
                <h3 class="rehber-baslik"><i class="fas fa-info-circle"></i> Form Yapılandırma Rehberi</h3>
                <ul class="rehber-liste">
                    
                    <li class="rehber-satir">
                        <div class="rehber-etiket"><span class="badge-gri">Alan Adı</span></div>
                        <div class="rehber-aciklama">
                            Kullanıcının formu doldururken göreceği isimdir (Örn: "Vergi Numarası", "TC Kimlik").
                        </div>
                    </li>

                    <li class="rehber-satir">
                        <div class="rehber-etiket"><span class="badge-gri">Veri Tipi</span></div>
                        <div class="rehber-aciklama">
                            Girilecek verinin formatını ve kutucuk tipini belirler.
                            <ul class="alt-liste">
                                <li>• <strong>Metin Kutusu:</strong> İsim, Adres, Unvan vb.</li>
                                <li>• <strong>Sayı:</strong> Telefon, TC, Adet, Stok Miktarı vb.</li>
                                <li>• <strong>Tarih:</strong> Doğum günü, Kayıt tarihi, Vade tarihi vb.</li>
                                <li>• <strong>Onay Kutusu:</strong> Evet/Hayır seçenekleri için.</li>
                            </ul>
                        </div>
                    </li>

                    <li class="rehber-satir">
                        <div class="rehber-etiket"><span class="badge-gri">Zorunlu mu?</span></div>
                        <div class="rehber-aciklama">
                            İşaretlenirse, müşteri eklerken bu alan boş bırakılamaz. Sistem uyarı verir.
                        </div>
                    </li>

                    <li class="rehber-satir">
                        <div class="rehber-etiket"><span class="badge-gri">Listede Göster</span></div>
                        <div class="rehber-aciklama">
                            İşaretlenirse, "Müşteriler" ana sayfasındaki tabloda bu bilgi ayrı bir sütun olarak eklenir (Hızlı Bakış).
                        </div>
                    </li>

                    <li class="rehber-satir">
                        <div class="rehber-etiket"><span class="badge-gri">Arama Yapılsın mı?</span></div>
                        <div class="rehber-aciklama">
                            İşaretlenirse, müşteri arama kutusuna yazılan kelime bu alanın içinde de aranır.
                        </div>
                    </li>

                    <li class="rehber-satir">
                        <div class="rehber-etiket"><span class="badge-gri">Sıralama</span></div>
                        <div class="rehber-aciklama">
                            Kutucukların formda ve listede hangi sırayla (0, 1, 2...) duracağını belirler. Küçük sayılar en üstte görünür.
                        </div>
                    </li>

                </ul>
            </div>
            """
        )
    
    kullanim_kilavuzu.short_description = " "

    def has_add_permission(self, request):
        return not FormYapilandirma.objects.exists()

@admin.register(PdfAyarlari)
class PdfAyarlariAdmin(admin.ModelAdmin):
    list_display = ('firma_adi', 'telefon', 'logo_onizleme')
    
    def logo_onizleme(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" height="30" />')
        return "-"
    logo_onizleme.short_description = "Logo"

    def has_add_permission(self, request):
        return not PdfAyarlari.objects.exists()

@admin.register(SartMaddesi)
class SartMaddesiAdmin(admin.ModelAdmin):
    list_display = ('icerik_kisalt',)
    search_fields = ('icerik',)

    def icerik_kisalt(self, obj):
        return obj.icerik[:100] + "..." if len(obj.icerik) > 100 else obj.icerik
    icerik_kisalt.short_description = "Madde"

@admin.register(SartSablonu)
class SartSablonuAdmin(admin.ModelAdmin):
    list_display = ('baslik',)
    filter_horizontal = ('maddeler',) # Maddeleri sağa sola atarak seçme arayüzü

@admin.register(DovizKuru)
class DovizKuruAdmin(admin.ModelAdmin):
    list_display = ('kod', 'ad', 'alis', 'satis', 'son_guncelleme')
    readonly_fields = ('son_guncelleme',)
    change_list_template = "admin/core/dovizkuru_change_list.html" # Özel şablon

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('guncelle/', self.admin_site.admin_view(self.kur_guncelle_view), name='kur_guncelle'),
        ]
        return my_urls + urls

    def kur_guncelle_view(self, request):
        # 1. Kontrol: Bugün zaten çekilmiş mi?
        # USD'ye bakarak anlarız (TRY hep 1 olduğu için değişmez)
        usd = DovizKuru.objects.filter(kod='USD').first()
        bugun = timezone.now().date()
        
        # Eğer USD varsa VE son güncelleme bugüne aitse
        if usd and usd.son_guncelleme.date() == bugun:
            self.message_user(request, "⚠️ Kurlar zaten bugün güncellenmiş! Tekrar çekilmedi.", level=messages.WARNING)
        else:
            # Güncelleme işlemini başlat
            basari, mesaj = tcmb_kur_guncelle()
            if basari:
                self.message_user(request, f"✅ {mesaj}", level=messages.SUCCESS)
            else:
                self.message_user(request, f"❌ {mesaj}", level=messages.ERROR)
        
        return HttpResponseRedirect("../")

# Profil Resmini Kullanıcı Sayfasına Gömme (Inline)
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil Resmi & Detaylar'
    fk_name = 'user'

# Standart UserAdmin'i Özelleştirme
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, )
    
    # Listede Avatarı Göstermek İstersen (Opsiyonel)
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

# Eski User admini kaldırıp yenisini kaydediyoruz
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)