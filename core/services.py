import requests
import xml.etree.ElementTree as ET
from datetime import date
from django.utils import timezone
from .models import DovizKuru

def tcmb_kur_guncelle():
    """
    TCMB'den güncel kurları çeker ve veritabanını günceller.
    Sadece USD ve EUR alır. TRY yoksa ekler.
    """
    url = "http://www.tcmb.gov.tr/kurlar/today.xml"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            
            # 1. TRY'yi Garantiye Al (Base Currency)
            DovizKuru.objects.update_or_create(
                kod='TRY',
                defaults={'ad': 'Türk Lirası', 'alis': 1.0, 'satis': 1.0}
            )

            # 2. İstenen Kurlar
            hedefler = ['USD', 'EUR']
            
            # Bugün güncellendi mi kontrolü aslında view'da yapılacak ama burada işlem yapıyoruz
            updated_count = 0
            
            for currency in root.findall('Currency'):
                kod = currency.get('Kod')
                
                if kod in hedefler:
                    isim = currency.find('Isim').text
                    # ForexSelling (Efektif değil normal satış alıyoruz genelde)
                    # Virgülleri noktaya çevirip floata alıyoruz
                    alis = float(currency.find('ForexBuying').text or 0)
                    satis = float(currency.find('ForexSelling').text or 0)
                    
                    DovizKuru.objects.update_or_create(
                        kod=kod,
                        defaults={
                            'ad': isim,
                            'alis': alis,
                            'satis': satis,
                            'son_guncelleme': timezone.now()
                        }
                    )
                    updated_count += 1
            
            return True, f"{updated_count} adet kur güncellendi."
            
    except Exception as e:
        return False, f"Hata oluştu: {str(e)}"
    
    return False, "Bilinmeyen hata."