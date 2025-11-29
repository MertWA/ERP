from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.db.models.signals import post_save
from django.dispatch import receiver
# Input Tipleri
INPUT_CHOICES = (
    ('CharField', 'Metin Kutusu (Kısa)'),
    ('TextField', 'Metin Kutusu (Uzun)'),
    ('IntegerField', 'Sayı'),
    ('DateField', 'Tarih'),
    ('BooleanField', 'Onay Kutusu (Evet/Hayır)'),
)

class FormYapilandirma(models.Model):
    class Meta:
        verbose_name = "Müşteri Form Yapılandırması"
        verbose_name_plural = "Müşteri Form Yapılandırması"

    def __str__(self):
        return "Genel Müşteri Form Ayarları"

    def save(self, *args, **kwargs):
        if not self.pk and FormYapilandirma.objects.exists():
            return
        return super(FormYapilandirma, self).save(*args, **kwargs)


class AlanTanim(models.Model):
    form_yapilandirma = models.ForeignKey(FormYapilandirma, related_name='alanlar', on_delete=models.CASCADE)
    baslik = models.CharField(max_length=100, verbose_name="Alan Adı (Etiket)")
    input_type = models.CharField(max_length=20, choices=INPUT_CHOICES, default='CharField', verbose_name="Veri Tipi")
    zorunlu = models.BooleanField(default=False, verbose_name="Zorunlu mu?")
    sira = models.PositiveSmallIntegerField(default=0, verbose_name="Sıralama")
    
    # Listeleme Ayarları
    listede_goster = models.BooleanField(default=False, verbose_name="Listede Göster")
    
    # YENİ EKLENEN ARAMA AYARI
    arama_varmi = models.BooleanField(default=True, verbose_name="Arama Yapılsın mı?")

    class Meta:
        verbose_name = "Form Alanı"
        verbose_name_plural = "Form Alanları"
        ordering = ['sira']

    def __str__(self):
        return self.baslik

class PdfAyarlari(models.Model):
    firma_adi = models.CharField(max_length=200, verbose_name="Firma Ünvanı")
    logo = models.ImageField(upload_to='logolar/', blank=True, null=True, verbose_name="Firma Logosu")
    adres = models.TextField(verbose_name="Firma Adresi", blank=True)
    telefon = models.CharField(max_length=50, verbose_name="Telefon", blank=True)
    eposta = models.EmailField(verbose_name="E-Posta", blank=True)
    web_site = models.URLField(verbose_name="Web Sitesi", blank=True)
    
    banka_bilgileri = models.TextField(verbose_name="Banka Bilgileri (Alt Bilgi)", blank=True, help_text="PDF'in en altında görünecek IBAN vb. bilgiler")

    class Meta:
        verbose_name = "PDF & Firma Ayarları"
        verbose_name_plural = "PDF & Firma Ayarları"

    def __str__(self):
        return self.firma_adi

    def save(self, *args, **kwargs):
        # Singleton (Sadece 1 kayıt olsun)
        if not self.pk and PdfAyarlari.objects.exists():
            return
        return super(PdfAyarlari, self).save(*args, **kwargs)

class SartMaddesi(models.Model):
    icerik = models.TextField(verbose_name="Madde İçeriği", help_text="Örn: Ödeme %50 peşin, %50 teslimdedir.")
    
    class Meta:
        verbose_name = "Standart Şart Maddesi"
        verbose_name_plural = "Standart Şart Maddeleri"

    def __str__(self):
        return self.icerik[:100]

class SartSablonu(models.Model):
    baslik = models.CharField(max_length=100, verbose_name="Şablon Adı", help_text="Örn: Standart Hizmet Sözleşmesi")
    maddeler = models.ManyToManyField(SartMaddesi, verbose_name="İçerdiği Maddeler")

    class Meta:
        verbose_name = "Şart Şablonu"
        verbose_name_plural = "Şart Şablonları"

    def __str__(self):
        return self.baslik
    
class DovizKuru(models.Model):
    kod = models.CharField(max_length=10, unique=True, verbose_name="Para Birimi Kodu", help_text="Örn: USD, EUR, TRY")
    ad = models.CharField(max_length=50, verbose_name="Para Birimi Adı")
    alis = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000, verbose_name="Alış Kuru")
    satis = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000, verbose_name="Satış Kuru")
    son_guncelleme = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")

    class Meta:
        verbose_name = "Döviz Kuru"
        verbose_name_plural = "Döviz Kurları"

    def __str__(self):
        return f"{self.kod}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile', verbose_name="Kullanıcı")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Profil Resmi")
    
    # İstersen buraya Telefon, Departman vb. de ekleyebilirsin
    
    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"

    def __str__(self):
        return f"{self.user.username} Profili"

# SİNYALLER (Otomatik Oluşturma)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Kullanıcı kaydedilince profili de kaydet (varsa)
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

def get_user_avatar(self):
    """
    Kullanıcının resmi varsa onu, yoksa varsayılan statik resmi döndürür.
    """
    if hasattr(self, 'userprofile') and self.userprofile.avatar:
        return self.userprofile.avatar.url
    
    # Resim yoksa statik klasöründeki varsayılanı döndür
    return static('img/default_avatar.png')

# Standart User modeline bu fonksiyonu "monte" ediyoruz
# (Eğer daha önce eklediysen bu satır zaten vardır, tekrar yazmana gerek yok)
User.add_to_class("get_avatar", get_user_avatar)