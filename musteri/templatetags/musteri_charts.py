from django import template
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.utils import timezone
from musteri.models import Musteri
import json

register = template.Library()

@register.simple_tag
def get_musteri_dashboard_data():
    # Son 12 ay
    son_12_ay = timezone.now() - timezone.timedelta(days=365)
    
    veriler = Musteri.objects.filter(olusturulma_tarihi__gte=son_12_ay)\
        .annotate(month=TruncMonth('olusturulma_tarihi'))\
        .values('month')\
        .annotate(total=Count('id'))\
        .order_by('month')
    
    months = []
    new_counts = [] # Aylık yeni gelen
    cumulative_counts = [] # Toplam müşteri sayısı
    
    # Toplam müşteri sayısını baz alarak başlat (Önceki yıllardan gelenler)
    current_total = Musteri.objects.filter(olusturulma_tarihi__lt=son_12_ay).count()

    for v in veriler:
        months.append(v['month'].strftime('%Y-%m'))
        count = v['total']
        new_counts.append(count)
        
        current_total += count
        cumulative_counts.append(current_total)
        
    return json.dumps({
        'months': months,
        'new_counts': new_counts,
        'cumulative_counts': cumulative_counts
    })