from django import template
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from teklif.models import Proforma
import json

register = template.Library()

@register.simple_tag
def get_teklif_dashboard_data():
    # --- GRAFİK 1: AYLIK DURUM BAZLI HACİM (STACKED BAR) ---
    son_12_ay = timezone.now() - timezone.timedelta(days=365)
    
    veriler = Proforma.objects.filter(created_at__gte=son_12_ay)\
        .annotate(month=TruncMonth('created_at'))
        
    # Matris Hesaplama
    matrix = {}
    tum_aylar = set()
    
    for p in veriler:
        ay_str = p.created_at.strftime('%Y-%m')
        tum_aylar.add(ay_str)
        
        toplam = 0
        for k in p.kalemler.all():
            # DÜZELTME BURADA: Üründen fiyat alınıyor
            if k.urun:
                toplam += k.miktar * k.urun.satis_fiyati
        
        if ay_str not in matrix: matrix[ay_str] = {}
        
        durum_key = p.durum 
        if durum_key not in matrix[ay_str]: matrix[ay_str][durum_key] = 0
        
        matrix[ay_str][durum_key] += float(toplam)

    sorted_months = sorted(list(tum_aylar))
    
    durum_tipleri = ['hazirlik', 'gonderildi', 'onaylandi', 'reddedildi', 'iptal']
    durum_labels = {'hazirlik': 'Hazırlık', 'gonderildi': 'Gönderildi', 'onaylandi': 'Onaylandı', 'reddedildi': 'Reddedildi', 'iptal': 'İptal'}
    durum_colors = {'hazirlik': '#6c757d', 'gonderildi': '#ffc107', 'onaylandi': '#28a745', 'reddedildi': '#dc3545', 'iptal': '#343a40'}
    
    series_data = []
    for d in durum_tipleri:
        data_points = []
        for ay in sorted_months:
            data_points.append(matrix.get(ay, {}).get(d, 0))
        
        series_data.append({
            'name': durum_labels[d],
            'type': 'bar',
            'stack': 'total',
            'emphasis': {'focus': 'series'},
            'itemStyle': {'color': durum_colors[d]},
            'data': data_points
        })

    # --- GRAFİK 2: EN ÇOK TEKLİF VERİLEN MÜŞTERİLER ---
    top_customers = {}
    for p in veriler:
        musteri_adi = str(p.musteri)
        toplam = 0
        for k in p.kalemler.all():
            # DÜZELTME BURADA: Üründen fiyat alınıyor
            if k.urun:
                toplam += k.miktar * k.urun.satis_fiyati
        
        if musteri_adi in top_customers: top_customers[musteri_adi] += float(toplam)
        else: top_customers[musteri_adi] = float(toplam)
    
    sorted_cust = sorted(top_customers.items(), key=lambda x: x[1], reverse=True)[:5]
    cust_names = [x[0] for x in sorted_cust]
    cust_values = [x[1] for x in sorted_cust]

    return json.dumps({
        'months': sorted_months,
        'series': series_data,
        'top_cust_names': cust_names,
        'top_cust_values': cust_values
    })