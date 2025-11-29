from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.views.decorators.clickjacking import xframe_options_exempt
from django.conf import settings
import json
from decimal import Decimal
import os

# Modeller
from .models import Proforma, MailLog
from stok.models import Urun
from core.models import PdfAyarlari, SartSablonu
from servis.models import ServisKaydi, ServisUrunleri
from django.urls import reverse

# WeasyPrint
try:
    from weasyprint import HTML, CSS
except ImportError:
    pass

# --- 1. API: ÜRÜN FİYATI GETİRME (JS İÇİN) ---
@staff_member_required
def get_urun_fiyat(request, urun_id):
    urun = get_object_or_404(Urun, pk=urun_id)
    # Para birimi ID'si gerekirse buradan döneriz ama artık JS'de kur kutusu olmadığı için sadece fiyat yeterli olabilir
    pb_id = urun.para_birimi.id if urun.para_birimi else 1
    return JsonResponse({
        'fiyat': urun.satis_fiyati,
        'para_birimi_id': pb_id 
    })

# --- 2. API: MÜŞTERİ MAİLLERİNİ BULMA ---
@staff_member_required
def get_proforma_emails(request, pk):
    proforma = get_object_or_404(Proforma, pk=pk)
    musteri_verileri = proforma.musteri.ekstra_bilgiler or {}
    bulunan_mailler = []
    for key, value in musteri_verileri.items():
        if isinstance(value, str) and "@" in value:
            bulunan_mailler.append({'key': key, 'value': value})
    return JsonResponse({'found': len(bulunan_mailler) > 0, 'emails': bulunan_mailler})

# --- 3. API: ŞABLON LİSTESİ ---
@staff_member_required
def get_sart_sablonlari(request):
    sablonlar = SartSablonu.objects.all().values('id', 'baslik')
    return JsonResponse(list(sablonlar), safe=False)

# --- 4. API: ŞABLON DETAYI ---
@staff_member_required
def get_sablon_detay(request, pk):
    sablon = get_object_or_404(SartSablonu, pk=pk)
    maddeler = list(sablon.maddeler.all().values_list('icerik', flat=True))
    return JsonResponse({'maddeler': maddeler})

# --- 5. PDF OLUŞTURMA (WEASYPRINT) ---
@staff_member_required
@xframe_options_exempt
def proforma_pdf(request, pk):
    proforma = get_object_or_404(Proforma, pk=pk)
    lang = request.GET.get('lang', 'tr')
    
    labels = {
        'tr': {'title': 'PROFORMA FATURA', 'bill_to': 'Sayın / Firma:', 'bill_from': 'Gönderen Firma:', 'invoice_no': 'Teklif No', 'date': 'Tarih', 'valid_until': 'Geçerlilik Tarihi', 'desc': 'Açıklama / Ürün', 'qty': 'Miktar', 'price': 'Birim Fiyat', 'total': 'Tutar', 'subtotal': 'Ara Toplam', 'tax': 'KDV', 'grand_total': 'Genel Toplam', 'terms': 'Şartlar ve Koşullar', 'page': 'Sayfa', 'of': '/'},
        'en': {'title': 'PROFORMA INVOICE', 'bill_to': 'Bill To:', 'bill_from': 'Bill From:', 'invoice_no': 'Invoice No', 'date': 'Date', 'valid_until': 'Valid Until', 'desc': 'Description', 'qty': 'Quantity', 'price': 'Unit Price', 'total': 'Line Total', 'subtotal': 'Subtotal', 'tax': 'VAT', 'grand_total': 'Grand Total', 'terms': 'Terms and Conditions', 'page': 'Page', 'of': 'of'}
    }
    L = labels[lang]
    firma = PdfAyarlari.objects.first()

    # Logo Yolu
    logo_path = None
    if firma and firma.logo:
        logo_path = firma.logo.path
        if os.name == 'nt':
            logo_path = f"file:///{logo_path.replace(os.sep, '/')}"

    kalemler = []
    ara_toplam = Decimal(0)
    toplam_kdv = Decimal(0)
    
    # Sembolü ilk ürünün kuruna göre belirleyelim (Varsayılan ₺)
    sembol = "₺"
    first_item = proforma.kalemler.first()
    if first_item and first_item.urun and first_item.urun.para_birimi:
        sembol = first_item.urun.para_birimi.kod

    for k in proforma.kalemler.all():
        # DÜZELTME: Fiyatı ve Kuru artık STOK KARTINDAN (k.urun) çekiyoruz
        if k.urun:
            guncel_fiyat = k.urun.satis_fiyati
            satir_sembol = k.urun.para_birimi.kod if k.urun.para_birimi else "₺"
        else:
            guncel_fiyat = Decimal(0)
            satir_sembol = "₺"

        tutar = Decimal(k.miktar) * guncel_fiyat
        kdv_tutar = tutar * (Decimal(k.kdv_orani) / Decimal(100))
        
        kalemler.append({
            'urun': k.urun.ad,
            'aciklama': k.aciklama,
            'miktar': k.miktar,
            'fiyat': f"{guncel_fiyat:,.2f} {satir_sembol}",
            'toplam': f"{tutar:,.2f} {satir_sembol}"
        })
        ara_toplam += tutar
        toplam_kdv += kdv_tutar

    genel_toplam = ara_toplam + toplam_kdv

    sartlar = []
    if proforma.sart_sablonu:
        sartlar = [m.icerik for m in proforma.sart_sablonu.maddeler.all()]

    context = {
        'p': proforma,
        'kalemler': kalemler,
        'firma': firma,
        'L': L,
        'ara_toplam': ara_toplam,
        'toplam_kdv': toplam_kdv,
        'genel_toplam': genel_toplam,
        'sartlar': sartlar,
        'sembol': sembol,
        'logo_url': logo_path,
    }

    html_string = render_to_string('teklif/pdf.html', context)
    
    base_url = request.build_absolute_uri()
    if os.name == 'nt':
        base_url = base_url.replace('\\', '/')

    html = HTML(string=html_string, base_url=base_url)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{proforma.kod}.pdf"'
    return response

# --- 6. MAİL GÖNDERME ---
@staff_member_required
@require_POST
def proforma_mail(request, pk):
    proforma = get_object_or_404(Proforma, pk=pk)
    try:
        data = json.loads(request.body)
        secilen_mailler = data.get('emails', [])
    except:
        return JsonResponse({'status': 'error', 'message': 'Veri hatası'}, status=400)
    
    if not secilen_mailler:
        return JsonResponse({'status': 'error', 'message': 'Mail seçilmedi'}, status=400)

    for mail in secilen_mailler:
        MailLog.objects.create(proforma=proforma, gonderilen_adres=mail)

    proforma.mail_gonderim_tarihi = timezone.now()
    proforma.save()
    
    messages.success(request, f"{len(secilen_mailler)} adrese mail gönderildi.")
    return JsonResponse({'status': 'success'})

# --- 7. ÖNİZLEME (PREVIEW) ---
@staff_member_required
def get_proforma_preview(request, pk):
    proforma = get_object_or_404(Proforma, pk=pk)
    
    kalemler = []
    ara_toplam = Decimal(0)
    toplam_kdv = Decimal(0)
    sembol = "₺"
    
    # İlk kalemin kurunu genel sembol yapalım
    first_item = proforma.kalemler.first()
    if first_item and first_item.urun and first_item.urun.para_birimi:
        sembol = first_item.urun.para_birimi.kod

    for k in proforma.kalemler.all():
        # DÜZELTME: Burada da 'k.birim_fiyat' yerine 'k.urun.satis_fiyati' kullanıyoruz
        if k.urun:
            guncel_fiyat = k.urun.satis_fiyati
            satir_sembol = k.urun.para_birimi.kod if k.urun.para_birimi else "₺"
        else:
            guncel_fiyat = Decimal(0)
            satir_sembol = "₺"

        tutar = Decimal(k.miktar) * guncel_fiyat
        kdv_tutar = tutar * (Decimal(k.kdv_orani) / Decimal(100))
        
        kalemler.append({
            'urun': k.urun.ad,
            'aciklama': k.aciklama,
            'miktar': k.miktar,
            'fiyat': guncel_fiyat,
            'toplam': tutar,
            'kur': satir_sembol
        })
        ara_toplam += tutar
        toplam_kdv += kdv_tutar

    genel_toplam = ara_toplam + toplam_kdv
    
    sartlar = []
    if proforma.sart_sablonu:
        sartlar = [m.icerik for m in proforma.sart_sablonu.maddeler.all()]

    context = {
        'p': proforma,
        'kalemler': kalemler,
        'ara_toplam': ara_toplam,
        'toplam_kdv': toplam_kdv,
        'genel_toplam': genel_toplam,
        'sembol': sembol,
        'sartlar': sartlar,
        'logs': proforma.mail_logs.all().order_by('-gonderim_zamani')
    }
    
    html = render_to_string('teklif/admin_preview.html', context)
    return HttpResponse(html)

# --- 8. OTOMATİK SERVİS OLUŞTURMA ---
@staff_member_required
def create_service_from_proforma(request, pk):
    proforma = get_object_or_404(Proforma, pk=pk)
    
    # 1. Kontrol: Zaten var mı?
    mevcut_servis = proforma.serviskaydi_set.first()
    if mevcut_servis:
        # Varsa direkt ona git
        messages.warning(request, f"Bu teklif için zaten bir servis kaydı mevcut: {mevcut_servis.fis_no}")
        return redirect(reverse('admin:servis_serviskaydi_change', args=[mevcut_servis.pk]))

    # 2. Yoksa Oluştur
    servis = ServisKaydi.objects.create(
        musteri=proforma.musteri,
        ilgili_proforma=proforma,
        konu=f"{proforma.kod} Teklifi Kaynaklı Servis",
        planlanan_tarih=timezone.now(),
        durum='bekliyor'
    )
    
    for kalem in proforma.kalemler.all():
        if kalem.urun:
            ServisUrunleri.objects.create(
                servis=servis,
                urun=kalem.urun,
                adet=kalem.miktar,
                seri_no=kalem.urun.kod
            )
        
    change_url = reverse('admin:servis_serviskaydi_change', args=[servis.pk])
    return redirect(change_url)