from django.db import models
from django.contrib.auth.models import User
from musteri.models import Musteri
from stok.models import Urun
from teklif.models import Proforma
from django.utils.html import mark_safe
from django_ckeditor_5.fields import CKEditor5Field
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from simple_history.models import HistoricalRecords
import datetime

# --- GÜNCELLENEN DURUM LİSTESİ (Kapandı Kalktı) ---
DURUM_SECENEKLERI = (
    ('bekliyor', 'Bekliyor / Atandı'),
    ('islemde', 'İşlemde'),
    ('parca_bekleniyor', 'Yedek Parça Bekleniyor'),
    ('imza_bekleniyor', 'İşlem Bitti (İmza Bekleniyor)'),
    ('tamamlandi', 'Tamamlandı'), 
    ('iptal', 'İptal'),
)

class TeknisyenUser(User):
    class Meta:
        proxy = True
        verbose_name = "Teknisyen"
        verbose_name_plural = "Teknisyenler"
    def __str__(self):
        full_name = self.get_full_name()
        return full_name if full_name else self.username

class ServisKaydi(models.Model):
    musteri = models.ForeignKey(Musteri, on_delete=models.CASCADE, verbose_name="Müşteri")
    ilgili_proforma = models.ForeignKey(Proforma, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Bağlı Teklif/Proforma")
    teknisyenler = models.ManyToManyField(TeknisyenUser, verbose_name="Görevli Teknisyenler")
    
    fis_no = models.CharField(max_length=20, unique=True, editable=False, verbose_name="Servis Fiş No")
    konu = models.CharField(max_length=200, verbose_name="Servis Konusu / Arıza")
    aciklama = CKEditor5Field('Teknisyen Notları / Arıza Detayı', config_name='default', blank=True)
    firma_ici_not = models.TextField(verbose_name="Firma İçi Not (Gizli)", blank=True)

    planlanan_tarih = models.DateTimeField(verbose_name="Planlanan Randevu")
    tamamlanma_tarihi = models.DateTimeField(null=True, blank=True, verbose_name="Tamamlanma Tarihi")
    
    durum = models.CharField(max_length=20, choices=DURUM_SECENEKLERI, default='bekliyor', verbose_name="Durum")
    musteri_imzasi = models.TextField(blank=True, null=True, verbose_name="Müşteri İmzası (Data)")
    imza_atan_kisi = models.CharField(max_length=100, blank=True, null=True, verbose_name="İmzalayan Kişi")

    mail_gonderim_tarihi = models.DateTimeField(null=True, blank=True, verbose_name="Son Mail Tarihi")
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    class Meta:
        verbose_name = "Servis Kaydı"
        verbose_name_plural = "Servis Kayıtları"
        ordering = ['-planlanan_tarih']

    def __str__(self): return f"{self.fis_no} - {self.musteri}"

    def save(self, *args, **kwargs):
        if not self.fis_no:
            import uuid
            self.fis_no = f"SRV-{str(uuid.uuid4())[:8].upper()}"
        # Sadece tamamlandi durumunda tarih basıyoruz
        if self.durum == 'tamamlandi' and not self.tamamlanma_tarihi:
            self.tamamlanma_tarihi = timezone.now()
        super().save(*args, **kwargs)

    def imza_goster(self):
        if self.musteri_imzasi:
            return mark_safe(f'<img src="{self.musteri_imzasi}" class="imza-popup-trigger" data-ad="{self.imza_atan_kisi or ""}" style="height:30px; border:1px solid #ccc; background:#fff; cursor:zoom-in;">')
        return "-"
    imza_goster.short_description = "İmza"

class ServisMailLog(models.Model):
    servis = models.ForeignKey(ServisKaydi, related_name='mail_logs', on_delete=models.CASCADE)
    gonderilen_adres = models.EmailField(verbose_name="Gönderilen Adres")
    gonderim_zamani = models.DateTimeField(auto_now_add=True, verbose_name="Gönderim Zamanı")
    class Meta:
        verbose_name = "Mail Kaydı"
        verbose_name_plural = "Mail Gönderim Geçmişi"
        ordering = ['-gonderim_zamani']

class ServisUrunleri(models.Model):
    servis = models.ForeignKey(ServisKaydi, related_name='urunler', on_delete=models.CASCADE)
    urun = models.ForeignKey(Urun, on_delete=models.PROTECT, verbose_name="Ürün")
    seri_no = models.CharField(max_length=100, blank=True, verbose_name="Seri No / Açıklama")
    adet = models.PositiveIntegerField(default=1)
    class Meta: verbose_name, verbose_name_plural = "Servis Ürünü", "Servis Ürünleri"

class YapilanIslem(models.Model):
    servis = models.ForeignKey(ServisKaydi, related_name='islemler', on_delete=models.CASCADE)
    aciklama = models.CharField(max_length=255, verbose_name="Yapılan İşlem")
    tamamlandi = models.BooleanField(default=False, verbose_name="Tamamlandı")
    class Meta: verbose_name, verbose_name_plural = "Yapılan İşlem", "Yapılan İşlemler (Checklist)"

class BakimPlani(models.Model):
    musteri = models.ForeignKey(Musteri, on_delete=models.CASCADE, verbose_name="Müşteri")
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE, verbose_name="Ürün")
    son_servis = models.ForeignKey(ServisKaydi, on_delete=models.SET_NULL, null=True, verbose_name="Son Yapılan Servis")
    son_bakim_tarihi = models.DateField(verbose_name="Son Bakım Tarihi")
    gelecek_bakim_tarihi = models.DateField(verbose_name="Gelecek Bakım Tarihi")
    aciklama = models.CharField(max_length=200, blank=True, verbose_name="Not")

    class Meta:
        verbose_name = "Yaklaşan Bakım"
        verbose_name_plural = "Yaklaşan Bakımlar"
        ordering = ['gelecek_bakim_tarihi']

    def __str__(self): return f"{self.musteri} - {self.urun}"
    def kalan_gun(self): return (self.gelecek_bakim_tarihi - timezone.now().date()).days

# --- YENİ MODEL: BAKIM GEÇMİŞİ (INLINE İÇİN) ---
class BakimGecmisi(models.Model):
    plan = models.ForeignKey(BakimPlani, related_name='gecmis', on_delete=models.CASCADE)
    servis = models.ForeignKey(ServisKaydi, on_delete=models.CASCADE, verbose_name="Yapılan Servis")
    tarih = models.DateField(verbose_name="İşlem Tarihi")
    olusturulan_sonraki_tarih = models.DateField(verbose_name="Oluşturulan Sonraki Bakım Tarihi")

    class Meta:
        verbose_name = "Bakım Geçmişi"
        verbose_name_plural = "Bakım Geçmişi"
        ordering = ['-tarih']

# --- OTOMASYON ---
@receiver(post_save, sender=ServisKaydi)
def update_bakim_plani(sender, instance, **kwargs):
    # Sadece 'tamamlandi' durumunda çalış
    if instance.durum == 'tamamlandi' and instance.tamamlanma_tarihi:
        for servis_urunu in instance.urunler.all():
            urun = servis_urunu.urun
            if urun.bakim_periyodu > 0:
                gun_sayisi = urun.bakim_periyodu * 30
                gelecek_tarih = instance.tamamlanma_tarihi.date() + datetime.timedelta(days=gun_sayisi)
                
                # Planı bul veya oluştur
                plan, created = BakimPlani.objects.get_or_create(
                    musteri=instance.musteri, urun=urun,
                    defaults={
                        'son_servis': instance,
                        'son_bakim_tarihi': instance.tamamlanma_tarihi.date(),
                        'gelecek_bakim_tarihi': gelecek_tarih
                    }
                )
                
                # Geçmiş Kaydı Oluştur (Mükerrer olmasın diye get_or_create)
                BakimGecmisi.objects.get_or_create(
                    plan=plan,
                    servis=instance,
                    defaults={
                        'tarih': instance.tamamlanma_tarihi.date(),
                        'olusturulan_sonraki_tarih': gelecek_tarih
                    }
                )

                # Ana Planı Güncelle
                plan.son_servis = instance
                plan.son_bakim_tarihi = instance.tamamlanma_tarihi.date()
                plan.gelecek_bakim_tarihi = gelecek_tarih
                plan.save()