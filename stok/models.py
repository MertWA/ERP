from django.db import models
from core.models import DovizKuru
from simple_history.models import HistoricalRecords
class Kategori(models.Model):
    ad = models.CharField(max_length=100, verbose_name="Kategori Adı")
    class Meta:
        verbose_name = "Ürün Kategorisi"
        verbose_name_plural = "Ürün Kategorileri"
    def __str__(self): return self.ad

class Urun(models.Model):
    kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kategori")
    kod = models.CharField(max_length=50, unique=True, verbose_name="Ürün Kodu / SKU")
    ad = models.CharField(max_length=200, verbose_name="Ürün Adı")
    para_birimi = models.ForeignKey(DovizKuru, on_delete=models.PROTECT, default=1, verbose_name="Para Birimi")
    satis_fiyati = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Satış Fiyatı")
    stok_miktari = models.IntegerField(default=0, verbose_name="Mevcut Stok")
    kritik_stok_seviyesi = models.IntegerField(default=10, verbose_name="Kritik Stok Uyarısı")
    aktif = models.BooleanField(default=True, verbose_name="Satışta mı?")
    history = HistoricalRecords()
    # YENİ ALAN: Bakım Periyodu
    bakim_periyodu = models.PositiveIntegerField(
        default=0, 
        verbose_name="Bakım Periyodu (Ay)", 
        help_text="0: Bakım gerektirmez. Örn: 6 yazarsanız, her 6 ayda bir bakım uyarısı verir."
    )

    class Meta:
        verbose_name = "Ürün / Hizmet"
        verbose_name_plural = "Ürünler / Hizmetler"

    def __str__(self):
        return f"{self.kod} - {self.ad}"

    def stok_durumu_html(self):
        if self.stok_miktari <= 0: return "stok_yok"
        elif self.stok_miktari <= self.kritik_stok_seviyesi: return "kritik"
        return "normal"