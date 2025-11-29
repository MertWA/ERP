document.addEventListener("DOMContentLoaded", function() {
    // Footer Linkini Düzenle
    const copyright = document.querySelector('.main-footer strong');
    if (copyright) {
        copyright.innerHTML = `Copyright &copy; 2025 <a href="https://asmeyazilim.com" target="_blank">ASME Yazılım</a>. Tüm hakları saklıdır.`;
    }
});