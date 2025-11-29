from django.db import models
try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField

class Musteri(models.Model):
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")
    ekstra_bilgiler = JSONField(default=dict, blank=True, verbose_name="Müşteri Bilgileri")

    class Meta:
        verbose_name = "Müşteri"
        verbose_name_plural = "Müşteriler"

    def __str__(self):
        veriler = self.ekstra_bilgiler
        if not veriler:
            return f"Müşteri #{self.pk}"
        
        # 1. Öncelik: 'Adı' veya 'Ad Soyad' gibi bir anahtar var mı bak
        for key in veriler.keys():
            if 'ad' in key.lower() or 'isim' in key.lower() or 'name' in key.lower():
                return f"{veriler[key]}"
        
        # 2. Öncelik: Yoksa ilk bulduğun değeri göster
        return list(veriler.values())[0]