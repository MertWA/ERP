from django.db import models
from musteri.models import Musteri
from django_ckeditor_5.fields import CKEditor5Field
from stok.models import Urun 
from core.models import SartSablonu
from simple_history.models import HistoricalRecords
DURUM_SECENEKLERI = (
    ('hazirlik', 'Hazırlık'),
    ('gonderildi', 'Gönderildi'),
    ('onaylandi', 'Onaylandı'),
    ('reddedildi', 'Reddedildi'),
    ('iptal', 'İptal'),
)

class Proforma(models.Model):
    musteri = models.ForeignKey(Musteri, on_delete=models.CASCADE, verbose_name="Müşteri")
    durum = models.CharField(max_length=20, choices=DURUM_SECENEKLERI, default='hazirlik', verbose_name="Teklif Durumu")
    sart_sablonu = models.ForeignKey(SartSablonu, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Şart Şablonu")
    
    tarih = models.DateField(verbose_name="Teklif Tarihi")
    gecerlilik_tarihi = models.DateField(verbose_name="Son Geçerlilik Tarihi", blank=True, null=True)
    kod = models.CharField(max_length=20, unique=True, editable=False, verbose_name="Teklif No")
    
    notlar = CKEditor5Field('Not', config_name='default', blank=True)
    firma_ici_not = models.TextField(verbose_name="Firma İçi Not (Gizli)", blank=True)
    
    mail_gonderim_tarihi = models.DateTimeField(null=True, blank=True, verbose_name="Son Mail Tarihi")
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    class Meta:
        verbose_name = "Proforma Teklif"
        verbose_name_plural = "Proforma Teklifler"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.kod} - {self.musteri}"
    
    def save(self, *args, **kwargs):
        if not self.kod:
            import uuid
            self.kod = f"PRF-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)

class MailLog(models.Model):
    proforma = models.ForeignKey(Proforma, related_name='mail_logs', on_delete=models.CASCADE)
    gonderilen_adres = models.EmailField(verbose_name="Gönderilen Adres")
    gonderim_zamani = models.DateTimeField(auto_now_add=True, verbose_name="Gönderim Zamanı")
    
    class Meta:
        verbose_name = "Mail Kaydı"
        verbose_name_plural = "Mail Gönderim Geçmişi"
        ordering = ['-gonderim_zamani']

class ProformaKalemi(models.Model):
    proforma = models.ForeignKey(Proforma, related_name='kalemler', on_delete=models.CASCADE)
    urun = models.ForeignKey(Urun, on_delete=models.PROTECT, verbose_name="Ürün Seçimi")
    
    # BİRİM FİYAT VE KUR ALANLARI SİLİNDİ
    
    aciklama = models.CharField(max_length=200, blank=True, verbose_name="Açıklama (Opsiyonel)")
    miktar = models.PositiveIntegerField(default=1, verbose_name="Miktar")
    kdv_orani = models.PositiveIntegerField(default=20, verbose_name="KDV %")

    class Meta:
        verbose_name = "Teklif Kalemi"
        verbose_name_plural = "Teklif Kalemleri"

    @property
    def satir_toplami(self):
        # Hesaplama artık anlık olarak ürün kartından çekiliyor
        if self.urun:
            return self.miktar * self.urun.satis_fiyati
        return 0