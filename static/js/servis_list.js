document.addEventListener('DOMContentLoaded', function() {
    const $ = django.jQuery;

    // --- CSRF TOKEN ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // --- MODAL HTML ŞABLONLARI (HEPSİ BURADA) ---
    const modalsHTML = `
    <div class="modal fade" id="checklistModal" tabindex="-1" role="dialog" style="z-index: 1050;">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header bg-info text-white">
            <h5 class="modal-title"><i class="fas fa-tasks"></i> Yapılan İşlemler</h5>
            <button type="button" class="close text-white" data-dismiss="modal"><span>&times;</span></button>
          </div>
          <div class="modal-body">
            <div id="checklistContent" class="list-group"></div>
            <div class="text-muted mt-3 small">* İşlemleri tamamladıkça kutucukları işaretleyiniz.</div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="imzaModal" tabindex="-1" role="dialog" style="z-index: 1060;">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header bg-warning text-dark">
            <h5 class="modal-title"><i class="fas fa-file-signature"></i> Müşteri Onay İmzası</h5>
            <button type="button" class="close" data-dismiss="modal"><span>&times;</span></button>
          </div>
          <div class="modal-body text-center">
            
            <div class="form-group text-left" id="imzaNameArea" style="margin-bottom:15px;">
                <label>İmzalayan Adı Soyadı:</label>
                <input type="text" id="imzaAtanKisi" class="form-control" placeholder="Teslim alan kişi...">
            </div>

            <div id="imzaPadArea">
                <p>Lütfen aşağıdaki alana imza atınız:</p>
                <canvas id="popupSignaturePad" width="450" height="200" style="border:2px dashed #ccc; cursor:crosshair; touch-action: none;"></canvas>
                <div class="mt-2">
                    <button class="btn btn-sm btn-danger" id="btnTemizle">Temizle</button>
                    <button class="btn btn-sm btn-success" id="btnKaydet">Kaydet</button>
                </div>
            </div>
            <div id="imzaImageArea" style="display:none;">
                <img id="imzaResmi" src="" style="max-width:100%; border:1px solid #ddd; padding:5px;">
                <p class="text-success mt-2"><strong><i class="fas fa-check-circle"></i> İmzalanmış</strong></p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="imzaPreviewModal" tabindex="-1" role="dialog" style="z-index: 1090;">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Müşteri İmzası</h5>
            <button type="button" class="close" data-dismiss="modal"><span>&times;</span></button>
          </div>
          <div class="modal-body text-center">
            <img id="previewImzaImg" src="" style="max-width:100%; border:1px solid #ccc; padding:10px; margin-bottom:10px;">
            <h5 id="previewImzaAd" style="font-weight:bold; color:#333;"></h5>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="mailSecimModal" tabindex="-1" role="dialog" style="z-index: 1070;">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">📧 Servis Formu Gönder</h5>
            <button type="button" class="close" data-dismiss="modal"><span>&times;</span></button>
          </div>
          <div class="modal-body">
            <p>Lütfen gönderim yapılacak adresleri seçiniz:</p>
            <form id="mailSecimForm"><div id="mailListesiDiv"></div></form>
            <div id="secimUyari" class="alert alert-danger mt-2" style="display:none;">Lütfen seçim yapınız.</div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-dismiss="modal">İptal</button>
            <button type="button" class="btn btn-primary" id="btnMailGonderOnay">🚀 Gönder</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="pdfLangModal" tabindex="-1" role="dialog" style="z-index: 1080;">
      <div class="modal-dialog modal-sm" role="document">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title">Dil Seçimi</h5><button type="button" class="close" data-dismiss="modal"><span>&times;</span></button></div>
          <div class="modal-body text-center">
            <button class="btn btn-primary btn-block pdf-generate-action" data-lang="tr">🇹🇷 Türkçe</button>
            <button class="btn btn-secondary btn-block pdf-generate-action" data-lang="en">🇬🇧 English</button>
          </div>
        </div>
      </div>
    </div>`;

    // Modalları sayfaya ekle
    if ($('#checklistModal').length === 0) $('body').append(modalsHTML);


    // --- DEĞİŞKENLER ---
    let signaturePad = null;
    let currentServisId = null;
    let currentPdfBaseUrl = "";

    // ===============================================
    // 1. CHECKLIST İŞLEMLERİ
    // ===============================================
    $(document).on('click', '.btn-checklist', function(e) {
        e.preventDefault();
        const id = $(this).data('id');
        $.ajax({
            url: '/api/servis-detay/' + id + '/',
            success: function(data) {
                let html = '';
                if(data.islemler.length === 0) {
                    html = '<div class="alert alert-warning">Bu servis için tanımlı işlem yok.</div>';
                } else {
                    data.islemler.forEach(function(item) {
                        const checked = item.tamamlandi ? 'checked' : '';
                        const strike = item.tamamlandi ? 'text-decoration:line-through; color:#ccc;' : '';
                        html += `<label class="list-group-item d-flex justify-content-between align-items-center" style="cursor:pointer;">
                            <span style="${strike}" id="text-${item.id}">${item.aciklama}</span>
                            <input type="checkbox" class="islem-check" data-id="${item.id}" ${checked} style="width:20px; height:20px;">
                        </label>`;
                    });
                }
                $('#checklistContent').html(html);
                $('#checklistModal').addClass('show').css('display', 'block');
                $('body').addClass('modal-open');
            }
        });
    });

    $(document).on('change', '.islem-check', function() {
        const id = $(this).data('id');
        const status = $(this).is(':checked');
        const textSpan = $('#text-' + id);
        if(status) textSpan.css({'text-decoration': 'line-through', 'color': '#ccc'});
        else textSpan.css({'text-decoration': 'none', 'color': '#333'});
        $.ajax({
            url: '/api/islem-toggle/', type: 'POST', headers: {'X-CSRFToken': csrftoken},
            data: JSON.stringify({'islem_id': id, 'durum': status}), contentType: 'application/json'
        });
    });

    // ===============================================
    // 2. İMZA ALMA İŞLEMLERİ
    // ===============================================
    $(document).on('click', '.btn-imza', function(e) {
        e.preventDefault();
        currentServisId = $(this).data('id');
        
        const canvas = document.getElementById('popupSignaturePad');
        if(!signaturePad) signaturePad = new SignaturePad(canvas, { backgroundColor: 'rgba(255, 255, 255, 0)' });
        signaturePad.clear();
        $('#imzaAtanKisi').val(''); // İsmi temizle

        $.ajax({
            url: '/api/servis-detay/' + currentServisId + '/',
            success: function(data) {
                if (data.imza_var_mi) {
                    $('#imzaPadArea').hide(); $('#imzaNameArea').hide();
                    $('#imzaImageArea').show();
                    $('#imzaResmi').attr('src', ''); 
                    $('#imzaImageArea').html('<div class="alert alert-success">Bu servis zaten imzalanmış.</div>');
                } else {
                    $('#imzaImageArea').hide(); 
                    $('#imzaPadArea').show(); $('#imzaNameArea').show();
                    signaturePad.on();
                }
                $('#imzaModal').addClass('show').css('display', 'block');
                $('body').addClass('modal-open');
            }
        });
    });

    $(document).on('click', '#btnTemizle', function() { signaturePad.clear(); });
    
    $(document).on('click', '#btnKaydet', function() {
        if (signaturePad.isEmpty()) { alert("Lütfen imza atınız."); return; }
        
        const dataURL = signaturePad.toDataURL();
        const imzaAdi = $('#imzaAtanKisi').val(); 
        if(!imzaAdi) { alert("Lütfen imzalayan kişinin adını yazınız."); return; }

        const btn = $(this);
        btn.prop('disabled', true).text('Kaydediliyor...');

        $.ajax({
            url: '/api/servis-imza/' + currentServisId + '/', type: 'POST', headers: {'X-CSRFToken': csrftoken},
            data: JSON.stringify({'imza': dataURL, 'imza_atan': imzaAdi}),
            contentType: 'application/json',
            success: function() {
                closeAllModals();
                location.reload(); 
            },
            error: function() { alert("Hata."); btn.prop('disabled', false).text('Kaydet'); }
        });
    });

    // ===============================================
    // 3. İMZA ÖNİZLEME (LİSTEDEN TIKLAYINCA)
    // ===============================================
    $(document).on('click', '.imza-popup-trigger', function() {
        const src = $(this).attr('src');
        const ad = $(this).data('ad');
        $('#previewImzaImg').attr('src', src);
        $('#previewImzaAd').text(ad ? ad : "İsim Belirtilmemiş");
        $('#imzaPreviewModal').addClass('show').css('display', 'block');
        $('body').addClass('modal-open');
    });

    // ===============================================
    // 4. PDF & MAIL İŞLEMLERİ (SERVİS ÖZEL)
    // ===============================================
    $(document).on('click', '.pdf-modal-btn', function(e) {
        e.preventDefault(); currentPdfBaseUrl = $(this).data('url');
        $('#pdfLangModal').addClass('show').css('display', 'block');
        $('body').addClass('modal-open');
    });

    $(document).on('click', '.pdf-generate-action', function() {
        const lang = $(this).data('lang');
        const finalUrl = currentPdfBaseUrl + '?lang=' + lang;
        closeAllModals();
        window.open(finalUrl, '_blank');
    });

    $(document).on('click', '.mail-gonder-btn', function(e) {
        e.preventDefault();
        const btn = $(this);
        const postUrl = btn.attr('data-url'); // /servis/mail/5/
        
        // URL'den ID'yi al
        const parts = postUrl.split('/');
        const servisId = parts[parts.length - 2] || parts[parts.length - 1]; 
        const getUrl = '/api/servis-emails/' + servisId + '/';

        btn.css('opacity', '0.5');

        $.ajax({
            url: getUrl,
            success: function(data) {
                btn.css('opacity', '1');
                if (!data.found) { alert("⚠️ UYARI: Müşteri kartında mail adresi bulunamadı."); } 
                else {
                    let html = '';
                    data.emails.forEach(function(item, index) {
                        html += `<div class="form-group form-check"><input type="checkbox" class="form-check-input mail-checkbox" value="${item.value}" checked><label class="form-check-label"><strong>${item.value}</strong> (${item.key})</label></div>`;
                    });
                    $('#mailListesiDiv').html(html); $('#secimUyari').hide();
                    
                    $('#mailSecimModal').addClass('show').css('display', 'block');
                    $('body').addClass('modal-open');
                    
                    $('#btnMailGonderOnay').off('click').on('click', function() {
                        const secilenler = [];
                        $('.mail-checkbox:checked').each(function() { secilenler.push($(this).val()); });
                        if(secilenler.length === 0) { $('#secimUyari').show(); return; }
                        
                        $(this).text('Gönderiliyor...').prop('disabled', true);
                        $.ajax({
                            url: postUrl, type: 'POST', headers: {'X-CSRFToken': csrftoken},
                            data: JSON.stringify({'emails': secilenler}), contentType: 'application/json',
                            success: function() { location.reload(); },
                            error: function() { alert('Hata!'); }
                        });
                    });
                }
            },
            error: function() { alert("Veri çekilemedi."); btn.css('opacity', '1'); }
        });
    });

    // ===============================================
    // 5. GLOBAL MODAL KAPATMA FONKSİYONLARI
    // ===============================================
    function closeAllModals() {
        $('.modal').removeClass('show').css('display', 'none');
        $('.modal-backdrop').remove();
        $('body').removeClass('modal-open');
    }

    $(document).on('click', '[data-dismiss="modal"], .close', function(e) {
        e.preventDefault();
        closeAllModals();
    });

    $(document).on('click', '.modal', function(e) {
        if ($(e.target).hasClass('modal')) {
            closeAllModals();
        }
    });
    
    $(document).on('keydown', function(e) {
        if (e.key === "Escape") closeAllModals();
    });

    // ===============================================
    // 6. BİLGİLENDİRME REHBERİ (SERVİS ÖZEL)
    // ===============================================
    
    const helpModalHTML = `
    <div class="modal fade" id="helpModal" tabindex="-1" role="dialog" style="z-index: 1090;">
      <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">
          <div class="modal-header bg-info text-white">
            <h5 class="modal-title"><i class="fas fa-wrench"></i> Servis Yönetim Rehberi</h5>
            <button type="button" class="close text-white" data-dismiss="modal"><span>&times;</span></button>
          </div>
          <div class="modal-body">
            <style>
                .rehber-kutusu { background-color: #fff; }
                .rehber-satir { display: flex; align-items: flex-start; padding: 12px 0; border-bottom: 1px solid #f1f3f5; }
                .rehber-satir:last-child { border-bottom: none; }
                .rehber-etiket { flex: 0 0 160px; margin-right: 20px; font-weight: 700; color: #495057; }
                .rehber-badge { display: inline-block; background-color: #e9ecef; color: #495057; padding: 4px 8px; border-radius: 4px; font-size: 12px; border: 1px solid #dee2e6; width: 100%; text-align: center; }
                .rehber-aciklama { flex: 1; font-size: 13px; color: #212529; line-height: 1.6; }
                .section-header { margin-top: 20px; margin-bottom: 10px; font-size: 14px; font-weight: bold; color: #17a2b8; border-bottom: 2px solid #17a2b8; padding-bottom: 5px; text-transform: uppercase; }
                .section-header:first-child { margin-top: 0; }
            </style>

            <div class="rehber-kutusu">
                
                <div class="section-header">1. Servis Künyesi</div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Fiş No</span></div>
                    <div class="rehber-aciklama">Sistem tarafından otomatik üretilir (SRV-XXXX). Takip numarasıdır.</div>
                </div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Durum</span></div>
                    <div class="rehber-aciklama">Servisin aşamalarını belirtir. 'Tamamlandı' seçildiğinde <b>PDF</b> ve <b>Mail</b> butonları aktif olur.</div>
                </div>

                <div class="section-header">2. Görevlendirme & Ürünler</div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Teknisyenler</span></div>
                    <div class="rehber-aciklama">Bu servise gidecek personelleri seçip sağ kutuya atayınız.</div>
                </div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Ürünler</span></div>
                    <div class="rehber-aciklama">Bakım veya onarım yapılacak cihazları buradan ekleyiniz. Tekliften oluşturulduysa otomatik gelir.</div>
                </div>

                <div class="section-header">3. Onay & Kapanış</div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Checklist</span></div>
                    <div class="rehber-aciklama">Yapılacak İşlemler listesindeki maddeleri tamamlandıkça işaretleyiniz.</div>
                </div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">İmza</span></div>
                    <div class="rehber-aciklama">Müşteriden tablet veya mouse ile dijital imza alabilirsiniz. İmza alındığında durum otomatik <b>'Tamamlandı'</b> olur.</div>
                </div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Otomatik Bakım</span></div>
                    <div class="rehber-aciklama">Servis tamamlandığında, eğer ürünün <b>Bakım Periyodu</b> varsa, sistem otomatik olarak ileri tarihli bir 'Yaklaşan Bakım' kaydı oluşturur.</div>
                </div>

            </div>
          </div>
          <div class="modal-footer bg-light">
            <button type="button" class="btn btn-secondary" data-dismiss="modal">Kapat</button>
          </div>
        </div>
      </div>
    </div>`;

    if ($('#helpModal').length === 0) $('body').append(helpModalHTML);

    // Butona Tıklama Olayı
    $(document).on('click', '#btnHelpModal', function(e) {
        e.preventDefault();
        try { 
            $('#helpModal').modal('show'); 
        } catch(err) { 
            // Fallback
            $('#helpModal').show().addClass('show').css('display', 'block');
            $('body').addClass('modal-open');
            if ($('.modal-backdrop').length === 0) {
                $('<div class="modal-backdrop fade show"></div>').appendTo(document.body);
            }
        }
    });
});