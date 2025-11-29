document.addEventListener('DOMContentLoaded', function() {
    const $ = django.jQuery;

    // --- REHBER MODALI ---
    const helpModalHTML = `
    <div class="modal fade" id="stokHelpModal" tabindex="-1" role="dialog" style="z-index: 1090;">
      <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">
          <div class="modal-header bg-info text-white">
            <h5 class="modal-title"><i class="fas fa-boxes"></i> Stok Yönetim Rehberi</h5>
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
                
                <div class="section-header">1. Ürün Kimliği</div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Kod / SKU</span></div>
                    <div class="rehber-aciklama">Ürüne ait benzersiz stok kodudur (Örn: TST-001). Sistemde arama yaparken ve teklif oluştururken bu kod kullanılır.</div>
                </div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Kategori</span></div>
                    <div class="rehber-aciklama">Ürünleri gruplamak ve raporlarda (Örn: Dashboard Pasta Grafiği) analiz etmek için kullanılır.</div>
                </div>

                <div class="section-header">2. Fiyatlandırma</div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Satış Fiyatı</span></div>
                    <div class="rehber-aciklama">Ürünün birim satış fiyatıdır. Teklif oluştururken bu fiyat otomatik olarak gelir.</div>
                </div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Para Birimi</span></div>
                    <div class="rehber-aciklama">Fiyatın hangi döviz cinsinden olduğunu belirtir. Tekliflerde kur bilgisi buradan otomatik çekilir.</div>
                </div>

                <div class="section-header">3. Depo & Uyarılar</div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Mevcut Stok</span></div>
                    <div class="rehber-aciklama">Depodaki güncel adettir. Listede anlık olarak takip edilebilir.</div>
                </div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Kritik Stok</span></div>
                    <div class="rehber-aciklama">Stok bu sayının altına düştüğünde, Admin Dashboard'unda <b>"Kritik Stoklar"</b> uyarı listesine düşer ve kırmızı işaretlenir.</div>
                </div>

                <div class="section-header">4. Servis Entegrasyonu</div>
                <div class="rehber-satir">
                    <div class="rehber-etiket"><span class="rehber-badge">Bakım Periyodu</span></div>
                    <div class="rehber-aciklama">Bu ürünün kaç ayda bir bakıma girmesi gerektiğini belirtir (Örn: 6 Ay). <br>
                    <span style="color:#28a745; font-weight:bold;">Otomasyon:</span> Bu ürün servise girip "Tamamlandı" olduğunda, sistem otomatik olarak bir sonraki bakım tarihini hesaplar ve takvime işler.</div>
                </div>

            </div>

          </div>
          <div class="modal-footer bg-light">
            <button type="button" class="btn btn-secondary" data-dismiss="modal">Kapat</button>
          </div>
        </div>
      </div>
    </div>`;

    if ($('#stokHelpModal').length === 0) $('body').append(helpModalHTML);

    // Butona Tıklama Olayı
    $(document).on('click', '#btnStokHelp', function(e) {
        e.preventDefault();
        try { 
            $('#stokHelpModal').modal('show'); 
        } catch(err) { 
            // Fallback
            $('#stokHelpModal').show().addClass('show').css('display', 'block');
            $('body').addClass('modal-open');
            if ($('.modal-backdrop').length === 0) {
                $('<div class="modal-backdrop fade show"></div>').appendTo(document.body);
            }
        }
    });

    // Kapatma İşlemleri
    $(document).on('click', '[data-dismiss="modal"]', function(e) {
        $('#stokHelpModal').removeClass('show').hide();
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