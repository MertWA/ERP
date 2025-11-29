from django import template
from django.db.models import F
from stok.models import Urun, Kategori
import json

register = template.Library()

@register.simple_tag
def get_stok_dashboard_data():
    """
    Stok dashboard'u için gerekli verileri JSON formatında hazırlar.
    """
    
    # 1. GRAFİK VERİSİ: Kritik Stok Altındaki Ürünler
    # Stoğu, kritik seviyenin altında veya eşit olanları filtrele
    kritik_urunler = Urun.objects.filter(stok_miktari__lte=F('kritik_stok_seviyesi')).order_by('stok_miktari')
    
    kritik_data = {
        'names': [u.ad for u in kritik_urunler],
        'values': [u.stok_miktari for u in kritik_urunler],
        'limits': [u.kritik_stok_seviyesi for u in kritik_urunler]
    }

    # 2. GRAFİK VERİSİ: Kategori Bazlı Stok Dağılımı (TreeMap)
    # Kategori -> Ürünler hiyerarşisi
    kategoriler = Kategori.objects.all()
    treemap_data = []

    for kat in kategoriler:
        urunler = Urun.objects.filter(kategori=kat)
        # Eğer kategoride ürün varsa ekle
        if urunler.exists():
            children = []
            toplam_stok = 0
            for u in urunler:
                children.append({
                    'name': u.ad,
                    'value': u.stok_miktari
                })
                toplam_stok += u.stok_miktari
            
            treemap_data.append({
                'name': kat.ad,
                'value': toplam_stok, # Kategorinin toplam büyüklüğü
                'children': children
            })

    return json.dumps({
        'kritik': kritik_data,
        'treemap': treemap_data
    })