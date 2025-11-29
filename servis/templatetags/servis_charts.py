from django import template
from django.db.models import Count
from django.utils import timezone
from servis.models import BakimPlani
import json
import datetime

register = template.Library()

@register.simple_tag
def get_servis_dashboard_data():
    bugun = timezone.now().date()
    
    # 1. GRAFİK: Bakım Durumu
    # Tarihi geçenler
    gecikmis = BakimPlani.objects.filter(gelecek_bakim_tarihi__lt=bugun).count()
    # Önümüzdeki 30 gün içinde olanlar
    yaklasan = BakimPlani.objects.filter(
        gelecek_bakim_tarihi__gte=bugun, 
        gelecek_bakim_tarihi__lte=bugun + datetime.timedelta(days=30)
    ).count()
    # Daha ileri tarihliler
    normal = BakimPlani.objects.filter(
        gelecek_bakim_tarihi__gt=bugun + datetime.timedelta(days=30)
    ).count()
    
    pie_data = [
        {'value': gecikmis, 'name': 'Gecikmiş Bakımlar', 'itemStyle': {'color': '#dc3545'}},
        {'value': yaklasan, 'name': 'Yaklaşan (30 Gün)', 'itemStyle': {'color': '#ffc107'}},
        {'value': normal, 'name': 'İleri Tarihli', 'itemStyle': {'color': '#28a745'}}
    ]

    # 2. GRAFİK: Gelecek 6 Ayın Bakım Yükü
    months = []
    counts = []
    
    for i in range(6):
        start_date = bugun + datetime.timedelta(days=i*30) # Kabaca aylık periyot
        end_date = start_date + datetime.timedelta(days=30)
        
        # O ay içindeki bakım sayısı
        count = BakimPlani.objects.filter(
            gelecek_bakim_tarihi__gte=start_date, 
            gelecek_bakim_tarihi__lt=end_date
        ).count()
        
        months.append(start_date.strftime('%Y-%m'))
        counts.append(count)

    return json.dumps({
        'pie_data': pie_data,
        'bar_months': months,
        'bar_counts': counts
    })