from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from teklif import views as teklif_views 
from servis import views as servis_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('api/proforma-emails/<int:pk>/', teklif_views.get_proforma_emails, name='api_proforma_emails'),
    path('api/urun-fiyat/<int:urun_id>/', teklif_views.get_urun_fiyat, name='api_urun_fiyat'),
    path('teklif/pdf/<int:pk>/', teklif_views.proforma_pdf, name='proforma_pdf'),
    path('teklif/mail/<int:pk>/', teklif_views.proforma_mail, name='proforma_mail'),
    path('api/sart-sablonlari/', teklif_views.get_sart_sablonlari, name='api_sart_sablonlari'),
    path('api/sablon-detay/<int:pk>/', teklif_views.get_sablon_detay, name='api_sablon_detay'),
    path('teklif/preview/<int:pk>/', teklif_views.get_proforma_preview, name='proforma_preview'),
    path('api/servis-detay/<int:pk>/', servis_views.get_servis_details, name='api_servis_detay'),
    path('api/islem-toggle/', servis_views.toggle_islem_durumu, name='api_islem_toggle'),
    path('api/servis-imza/<int:pk>/', servis_views.save_servis_imza, name='api_servis_imza'),
    path('servis/pdf/<int:pk>/', servis_views.servis_pdf, name='servis_pdf'),
    path('servis/mail/<int:pk>/', servis_views.servis_mail, name='servis_mail'),
    path('teklif/create-service/<int:pk>/', teklif_views.create_service_from_proforma, name='create_service_from_proforma'),
    path('api/servis-emails/<int:pk>/', servis_views.get_servis_emails, name='api_servis_emails'),
    path('servis/pdf/<int:pk>/', servis_views.servis_pdf, name='servis_pdf'),
    path('servis/mail/<int:pk>/', servis_views.servis_mail, name='servis_mail'),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

