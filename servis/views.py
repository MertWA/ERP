from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_exempt
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
import json
import os

from .models import ServisKaydi, YapilanIslem
from core.models import PdfAyarlari

try:
    from weasyprint import HTML
except ImportError:
    pass

# ... (Eski API'ler: get_servis_details, toggle_islem_durumu, save_servis_imza AYNI KALSIN) ...
@staff_member_required
def get_servis_details(request, pk):
    servis = get_object_or_404(ServisKaydi, pk=pk)
    islemler = list(servis.islemler.all().values('id', 'aciklama', 'tamamlandi'))
    return JsonResponse({'fis_no': servis.fis_no, 'musteri': str(servis.musteri), 'islemler': islemler, 'imza_var_mi': bool(servis.musteri_imzasi)})

@staff_member_required
@require_POST
def toggle_islem_durumu(request):
    try:
        data = json.loads(request.body)
        islem = get_object_or_404(YapilanIslem, pk=data.get('islem_id'))
        islem.tamamlandi = data.get('durum')
        islem.save()
        return JsonResponse({'status': 'success'})
    except: return JsonResponse({'status': 'error'}, status=400)

@staff_member_required
@require_POST
def save_servis_imza(request, pk):
    servis = get_object_or_404(ServisKaydi, pk=pk)
    try:
        data = json.loads(request.body)
        imza_data = data.get('imza')
        imza_atan = data.get('imza_atan') # YENİ ALAN
        
        if imza_data:
            servis.musteri_imzasi = imza_data
            
            # İsim geldiyse kaydet
            if imza_atan:
                servis.imza_atan_kisi = imza_atan

            if servis.durum not in ['kapandi', 'iptal']:
                servis.durum = 'tamamlandi'
            servis.save()
            return JsonResponse({'status': 'success'})
    except:
        pass
    return JsonResponse({'status': 'error'}, status=400)

@staff_member_required
@xframe_options_exempt
def servis_pdf(request, pk):
    servis = get_object_or_404(ServisKaydi, pk=pk)
    lang = request.GET.get('lang', 'tr')
    
    labels = {
        'tr': {'title': 'SERVİS FORMU', 'ticket_no': 'Fiş No', 'customer': 'Müşteri', 'date': 'Tarih', 'subject': 'Konu', 'technician': 'Teknisyen', 'products': 'Ürünler', 'actions': 'Yapılan İşlemler', 'notes': 'Notlar', 'signature': 'Müşteri İmzası'},
        'en': {'title': 'SERVICE REPORT', 'ticket_no': 'Ticket No', 'customer': 'Customer', 'date': 'Date', 'subject': 'Subject', 'technician': 'Technician', 'products': 'Products', 'actions': 'Actions Taken', 'notes': 'Notes', 'signature': 'Customer Signature'}
    }
    L = labels[lang]
    firma = PdfAyarlari.objects.first()

    logo_path = None
    if firma and firma.logo:
        logo_path = firma.logo.path
        if os.name == 'nt': logo_path = f"file:///{logo_path.replace(os.sep, '/')}"

    teknisyenler = ", ".join([u.get_full_name() or u.username for u in servis.teknisyenler.all()])
    
    context = {
        's': servis, 'firma': firma, 'L': L, 'logo_url': logo_path,
        'teknisyenler': teknisyenler,
        'urunler': servis.urunler.all(),
        'islemler': servis.islemler.all()
    }

    html_string = render_to_string('servis/pdf.html', context)
    base_url = request.build_absolute_uri()
    if os.name == 'nt': base_url = base_url.replace('\\', '/')
    
    html = HTML(string=html_string, base_url=base_url)
    pdf_file = html.write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{servis.fis_no}.pdf"'
    return response

# --- GÜNCELLENEN MAİL FONKSİYONU (SERVİSE ÖZEL) ---
@staff_member_required
@require_POST
def servis_mail(request, pk):
    servis = get_object_or_404(ServisKaydi, pk=pk)
    try:
        data = json.loads(request.body)
        secilen_mailler = data.get('emails', [])
        if not secilen_mailler: return JsonResponse({'status': 'error', 'message': 'Mail seçilmedi'}, status=400)
        
        # 1. Logları Kaydet
        for mail in secilen_mailler:
            ServisMailLog.objects.create(
                servis=servis,
                gonderilen_adres=mail
            )

        # 2. Güncelle (Sadece tarih)
        servis.mail_gonderim_tarihi = timezone.now()
        # DÜZELTME: Durumu değiştirmiyoruz, zaten tamamlandı ki butonu görüyor
        servis.save()
        
        messages.success(request, f"Servis formu gönderildi.")
        return JsonResponse({'status': 'success'})
    except: return JsonResponse({'status': 'error'}, status=400)

# --- YENİ EKLENEN: SERVİS MAİLLERİNİ BULMA API ---
@staff_member_required
def get_servis_emails(request, pk):
    servis = get_object_or_404(ServisKaydi, pk=pk)
    musteri_verileri = servis.musteri.ekstra_bilgiler or {}
    
    bulunan_mailler = []
    for key, value in musteri_verileri.items():
        if isinstance(value, str) and "@" in value:
            bulunan_mailler.append({'key': key, 'value': value})
            
    return JsonResponse({
        'found': len(bulunan_mailler) > 0,
        'emails': bulunan_mailler
    })

# --- YENİ EKLENEN: KAYDI MANUEL KAPATMA ---
@staff_member_required
def servis_kapat(request, pk):
    servis = get_object_or_404(ServisKaydi, pk=pk)
    servis.durum = 'kapandi'
    servis.save()
    messages.success(request, f"{servis.fis_no} başarıyla kapatıldı.")
    return redirect(request.META.get('HTTP_REFERER', 'admin:servis_serviskaydi_changelist'))