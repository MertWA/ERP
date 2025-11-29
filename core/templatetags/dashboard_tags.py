from django import template
from django.utils import timezone
from django.contrib.admin.models import LogEntry
from django.db.models import Count, Q, Sum, F
from django.db.models.functions import TruncMonth
from django.utils.html import mark_safe
# YENİ IMPORT: App Config'e erişmek için
from django.apps import apps 
from django.db import models
from stok.models import Urun
from servis.models import ServisKaydi
from teklif.models import Proforma, ProformaKalemi
import json
import datetime

register = template.Library()

@register.simple_tag(takes_context=True)
def get_admin_dashboard_data(context):
    request = context['request']
    period = request.GET.get('period', 'today')
    
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 1. LOG FİLTRELEME
    if period == 'week':
        date_limit = now - datetime.timedelta(days=7)
        filter_kwargs = {'action_time__gte': date_limit}
    elif period == 'month':
        date_limit = now - datetime.timedelta(days=30)
        filter_kwargs = {'action_time__gte': date_limit}
    else: # today
        filter_kwargs = {'action_time__gte': today_start}

    logs = LogEntry.objects.filter(**filter_kwargs).select_related('user', 'content_type').order_by('-action_time')[:100]
    
    # 2. FİNANSAL GRAFİK
    six_months_ago = now - datetime.timedelta(days=180)
    monthly_financials = ProformaKalemi.objects.filter(proforma__created_at__gte=six_months_ago) \
        .annotate(month=TruncMonth('proforma__created_at')) \
        .values('month') \
        .annotate(total_amount=Sum(F('miktar') * F('urun__satis_fiyati'))) \
        .order_by('month')

    fin_months = []
    fin_totals = []
    for entry in monthly_financials:
        if entry['month']:
            fin_months.append(entry['month'].strftime('%Y-%m'))
            fin_totals.append(float(entry['total_amount'] or 0))

    financial_chart_data = json.dumps({'months': fin_months, 'totals': fin_totals})

    # 3. STOK UYARILARI
    out_of_stock = Urun.objects.filter(stok_miktari__lte=0, aktif=True)
    critical_stock = Urun.objects.filter(stok_miktari__gt=0, stok_miktari__lte=F('kritik_stok_seviyesi'), aktif=True)
    
    # 4. SERVİS UYARILARI
    urgent_services = ServisKaydi.objects.filter(
        Q(planlanan_tarih__lt=now) | Q(planlanan_tarih__date=today_start.date()),
        durum__in=['bekliyor', 'islemde', 'parca_bekleniyor', 'imza_bekleniyor']
    ).order_by('planlanan_tarih')

    # 5. STOK GRAFİK VERİSİ
    total_products = Urun.objects.filter(aktif=True).count()
    safe_stock = total_products - out_of_stock.count() - critical_stock.count()
    
    stock_pie_data = json.dumps([
        {'value': safe_stock, 'name': 'Güvenli', 'itemStyle': {'color': '#28a745'}},
        {'value': critical_stock.count(), 'name': 'Kritik', 'itemStyle': {'color': '#ffc107'}},
        {'value': out_of_stock.count(), 'name': 'Tükendi', 'itemStyle': {'color': '#dc3545'}}
    ])

    return {
        'logs': logs,
        'period': period,
        'financial_chart_data': financial_chart_data,
        'out_of_stock': out_of_stock,
        'critical_stock': critical_stock,
        'urgent_services': urgent_services,
        'stock_pie_data': stock_pie_data,
        'service_count': urgent_services.count()
    }

# --- YENİ EKLENEN FİLTRE: APP VERBOSE NAME ---
@register.filter
def get_app_name(content_type):
    """
    ContentType objesini alır (örn: 'core' uygulamasının bir modeli)
    ve o uygulamanın verbose_name'ini (örn: 'Ayarlar') döndürür.
    """
    if not content_type:
        return ""
    try:
        # App Config'i çağır ve verbose_name'i al
        app_config = apps.get_app_config(content_type.app_label)
        return app_config.verbose_name
    except:
        # Hata olursa (veya app bulunamazsa) teknik adını döndür
        return content_type.app_label