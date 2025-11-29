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

    // ===============================================
    // MODAL HTML ŞABLONLARI (HEPSİ BURADA)
    // ===============================================

    // 1. BİLGİLENDİRME (REHBER) MODALI
    const helpModalHTML = `
    <div class="modal fade" id="helpModal" tabindex="-1" role="dialog" style="z-index: 9999;">
      <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">
          <div class="modal-header bg-info text-white">
            <h5 class="modal-title"><i class="fas fa-book-reader"></i> Teklif Oluşturma Rehberi</h5>
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
                <div class="section-header">1. Genel Bilgiler</div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Teklif Durumu</span></div>
                    <div class="rehber-aciklama">Yeni teklifler <b>'Hazırlık'</b> durumunda başlar. 'Onaylandı' olunca <b>Servis Oluştur</b> butonu açılır.</div>
                </div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Şart Şablonu</span></div>
                    <div class="rehber-aciklama">Sözleşme maddelerini hızlıca eklemek için kullanılır. Seçim yapınca 'Teklif Şartları' otomatik dolar.</div>
                </div>
                <div class="section-header">2. Ürün & Hizmetler</div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Otomatik Fiyat</span></div>
                    <div class="rehber-aciklama">Ürün seçince <b>Fiyat</b> ve <b>Kur</b> otomatik gelir.</div>
                </div>
                <div class="section-header">3. Notlar & İletişim</div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Notlar</span></div>
                    <div class="rehber-aciklama">PDF'te en altta görünür.</div>
                </div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Firma İçi Not</span></div>
                    <div class="rehber-aciklama" style="color:#c0392b;">Gizlidir, müşteriye gitmez.</div>
                </div>
            </div>
          </div>
          <div class="modal-footer bg-light">
            <button type="button" class="btn btn-secondary" data-dismiss="modal">Kapat</button>
          </div>
        </div>
      </div>
    </div>`;

    // 2. MAİL MODALI
    const mailModalHTML = `
    <div class="modal fade" id="mailSecimModal" tabindex="-1" role="dialog" style="z-index: 1050;">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">📧 Mail Gönderimi</h5>
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
    </div>`;

    // 3. PDF DİL MODALI
    const pdfLangModalHTML = `
    <div class="modal fade" id="pdfLangModal" tabindex="-1" role="dialog" style="z-index: 1060;">
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
    
    // 4. PREVIEW MODALI
    const previewModalHTML = `
    <div class="modal fade" id="previewModal" tabindex="-1" role="dialog" style="z-index: 1090;">
      <div class="modal-dialog modal-lg modal-dialog-scrollable" role="document"> 
        <div class="modal-content" style="border:none; border-radius:10px;">
          <div class="modal-body" id="previewContent" style="padding:0;">
            <div class="text-center p-5"><i class="fas fa-spinner fa-spin fa-3x"></i><br>Yükleniyor...</div>
          </div>
        </div>
      </div>
    </div>`;

    // Modalları sayfaya ekle (Varsa ekleme)
    if ($('#helpModal').length === 0) $('body').append(helpModalHTML);
    if ($('#mailSecimModal').length === 0) $('body').append(mailModalHTML);
    if ($('#pdfLangModal').length === 0) $('body').append(pdfLangModalHTML);
    if ($('#previewModal').length === 0) $('body').append(previewModalHTML);


    // ===============================================
    // EVENTS (TIKLAMA OLAYLARI)
    // ===============================================

    // 1. BİLGİLENDİRME BUTONU (REHBER)
    $(document).on('click', '#btnHelpModal', function(e) {
        e.preventDefault();
        try { 
            $('#helpModal').modal('show'); 
        } catch(err) { 
            // Fallback
            $('#helpModal').show().addClass('show').css('display', 'block');
            $('body').addClass('modal-open');
            $('<div class="modal-backdrop fade show"></div>').appendTo(document.body);
        }
    });

    // 2. MAIL BUTONU
    $(document).on('click', '.mail-gonder-btn', function(e) {
        e.preventDefault();
        const btn = $(this);
        const postUrl = btn.attr('data-url'); 
        const parts = postUrl.split('/');
        const proformaId = parts[parts.length - 2] || parts[parts.length - 1]; 
        const getUrl = '/api/proforma-emails/' + proformaId + '/';

        btn.css('opacity', '0.5');

        $.ajax({
            url: getUrl,
            success: function(data) {
                btn.css('opacity', '1');
                if (!data.found) {
                    alert("⚠️ UYARI: Müşteri kartında mail bilgisi bulunamadı.");
                } else {
                    let htmlContent = '';
                    data.emails.forEach(function(item, index) {
                        htmlContent += `
                        <div class="form-group form-check" style="padding-left: 20px;">
                            <input type="checkbox" class="form-check-input mail-checkbox" id="mailCheck${index}" value="${item.value}" checked>
                            <label class="form-check-label" for="mailCheck${index}">
                                <strong>${item.value}</strong> <span class="text-muted">(${item.key})</span>
                            </label>
                        </div>`;
                    });
                    $('#mailListesiDiv').html(htmlContent);
                    $('#secimUyari').hide();
                    try { $('#mailSecimModal').modal('show'); } catch(err) { $('#mailSecimModal').show().addClass('show'); }
                    
                    $('#btnMailGonderOnay').off('click').on('click', function() {
                        const secilenler = [];
                        $('.mail-checkbox:checked').each(function() { secilenler.push($(this).val()); });
                        if(secilenler.length === 0) { $('#secimUyari').slideDown(); return; }
                        
                        const modalBtn = $(this);
                        modalBtn.text('Gönderiliyor...').prop('disabled', true);
                        
                        $.ajax({
                            url: postUrl,
                            type: 'POST',
                            headers: {'X-CSRFToken': csrftoken},
                            data: JSON.stringify({'emails': secilenler}),
                            contentType: 'application/json',
                            success: function(response) { location.reload(); },
                            error: function() { 
                                alert('Gönderim hatası!'); 
                                modalBtn.text('🚀 Gönder').prop('disabled', false); 
                            }
                        });
                    });
                }
            },
            error: function() { alert("Veri çekilemedi."); btn.css('opacity', '1'); }
        });
    });

    // 3. PDF BUTONU
    let currentPdfBaseUrl = "";
    $(document).on('click', '.pdf-modal-btn', function(e) {
        e.preventDefault();
        currentPdfBaseUrl = $(this).data('url');
        try { $('#pdfLangModal').modal('show'); } catch(err) { $('#pdfLangModal').show().addClass('show'); }
    });

    $(document).on('click', '.pdf-generate-action', function() {
        const lang = $(this).data('lang');
        const finalUrl = currentPdfBaseUrl + '?lang=' + lang;
        $('#pdfLangModal').removeClass('show').hide();
        window.open(finalUrl, '_blank');
    });

    // 4. PREVIEW BUTONU
    $(document).on('click', '.preview-modal-btn', function(e) {
        e.preventDefault();
        const url = $(this).data('url');
        try { $('#previewModal').modal('show'); } catch(err) { $('#previewModal').show().addClass('show'); }
        
        $('#previewContent').html('<div class="text-center p-5"><i class="fas fa-spinner fa-spin fa-3x"></i><br>Yükleniyor...</div>');
        $.ajax({
            url: url,
            success: function(html) { $('#previewContent').html(html); },
            error: function() { $('#previewContent').html('<div class="alert alert-danger m-3">Hata oluştu.</div>'); }
        });
    });

    // 5. GENEL KAPATMA (Dışarı Tıklama & X Butonu)
    $(document).on('click', '[data-dismiss="modal"], .close', function(e) {
        $('.modal').removeClass('show').hide();
        $('.modal-backdrop').remove();
        $('body').removeClass('modal-open');
    });

    $(document).on('click', '.modal', function(e) {
        if ($(e.target).hasClass('modal')) {
            $('.modal').removeClass('show').hide();
            $('.modal-backdrop').remove();
            $('body').removeClass('modal-open');
        }
    });

});