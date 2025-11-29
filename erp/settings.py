from pathlib import Path
from decouple import config
import os
import os

# GTK3 Kütüphanesini Windows'a Tanıtma
# (Eğer GTK3'ü standart konuma kurduysan burası çalışır)
if os.name == 'nt':
    GTK_FOLDER = r'C:\Program Files\GTK3-Runtime Win64\bin'
    if os.path.exists(GTK_FOLDER):
        try:
            os.add_dll_directory(GTK_FOLDER)
        except AttributeError:
            # Python 3.8 öncesi için
            os.environ['PATH'] = GTK_FOLDER + ';' + os.environ['PATH']
            
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'simple_history',
    'django_ckeditor_5',
    'core',
    'musteri',
    'teklif',
    'stok',
    'servis',    
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'erp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'erp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # Bütün kritik bilgileri .env dosyasından çekiyoruz
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'tr'

TIME_ZONE = 'Europe/Istanbul'

USE_I18N = True

USE_L10N = True # Formatlama (Virgül/Nokta) için önemli

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'

# Dosyaların bilgisayarda fiziksel olarak saklanacağı klasör
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CKEditor 5 Ayarları
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|', 
            'bold', 'italic', 'underline', 'strikethrough', 'code', '|', 
            'bulletedList', 'numberedList', '|',
            'outdent', 'indent', '|',
            'blockQuote', 'insertTable', 'undo', 'redo'
        ],
        'language': 'tr',  # Türkçe dil desteği
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells' ]
        },
    }
}

# ==========================================
# JAZZMIN AYARLARI (MODERN ERP ARAYÜZÜ)
# ==========================================

# ==========================================
# 1. JAZZMIN AYARLARI (MANTIK VE İÇERİK)
# ==========================================
# Burası menü sıralaması, ikonlar ve başlıkları yönetir.
X_FRAME_OPTIONS = 'SAMEORIGIN'
JAZZMIN_SETTINGS = {
    # --- GENEL BAŞLIKLAR ---
    "site_title": "Medikal ERP",
    "site_header": "Medikal ERP",
    "site_brand": "Medikal Tim",
    "welcome_sign": "Yönetim Paneline Hoşgeldiniz",
    "copyright": "ASME Yazılım Ltd. Şti.",
    "search_model": "musteri.Musteri",
    "user_avatar": "get_avatar",
    # --- MENÜ DAVRANIŞI ---
    # Tweak ayarlarında da False yaptığın için burayı da False tutuyoruz.
    # Menüler kapalı gelir, tıklayınca aşağı açılır.
    "show_sidebar": True,
    "navigation_expanded": False,
    "custom_css": "css/admin_custom.css",
    "custom_js": "js/admin_global.js",
    # --- MENÜ SIRALAMASI ---
    "order_with_respect_to": [
        "teklif",
        'servis',
        "stok",
        "musteri",        
        "auth",
        "core",
    ],
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Teklifler", "url": "/admin/teklif/", "new_window": False, "icon": "fas fa-file-invoice-dollar"},
        {"name": "Servis", "url": "/admin/servis/", "new_window": False, "icon": "fas fa-boxes"},
        {"name": "Stok", "url": "/admin/stok/", "new_window": False, "icon": "fas fa-boxes"},
        {"name": "Müşteriler", "url": "/admin/musteri/", "new_window": False, "icon": "fas fa-users"},        
    ],
    # --- İKONLAR (FontAwesome 5) ---
    "icons": {
        # Auth
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        
        # Müşteri App
        "musteri": "fas fa-address-book",
        "musteri.Musteri": "fas fa-user-tie",
        
        # Stok App
        "stok": "fas fa-boxes",
        "stok.Urun": "fas fa-box-open",
        "stok.Kategori": "fas fa-tags",
        
        # Teklif App
        "teklif": "fas fa-file-signature",
        "teklif.Proforma": "fas fa-file-invoice-dollar",
        "teklif.MailLog": "fas fa-envelope-open-text",
        
        # Core (Ayarlar) App
        "core": "fas fa-cogs",
        "core.FormYapilandirma": "fas fa-sliders-h",
        "core.PdfAyarlari": "fas fa-file-pdf",
        "core.DovizKuru": "fas fa-money-bill-wave",
        "core.SartSablonu": "fas fa-clipboard-list",
        "core.SartMaddesi": "fas fa-list-ol",

        # Servis App
        "servis": "fas fa-tools",
        "servis.ServisKaydi": "fas fa-clipboard-check",
        "servis.BakimPlani": "fas fa-calendar-check",
    },

    
    "default_icon_parents": "fas fa-circle",
    "default_icon_children": "fas fa-dot-circle",
    
    "related_modal_active": True,
    
    "usermenu_links": [
        {"model": "auth.user"}
    ],
    "hide_models": ["teklif.MailLog", "servis.YapilanIslem", "servis.ServisUrunleri", "servis.ServisMailLog"],
    # UI Builder'ı açık bırakalım, ince ayar yapmak istersen kullanırsın
    "show_ui_builder": True,
}

# ==========================================
# 2. JAZZMIN UI TWEAKS (GÖRSEL TASARIM)
# ==========================================
# Senin gönderdiğin Pulse temalı ve özel ayarlı yapı:

JAZZMIN_UI_TWEAKS = {
    # --- METİN BOYUTLARI ---
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    
    # --- RENKLER VE TEMA ---
    "theme": "pulse",  # Seçtiğin tema
    "dark_mode_theme": None,
    "accent": "accent-primary",
    
    # --- ÜST BAR (NAVBAR) ---
    "navbar": "navbar-light",
    "brand_colour": "navbar-success", # Sol üst köşe (Logo alanı) Sarı/Turuncu
    "no_navbar_border": False,
    "navbar_fixed": False,
    "actions_sticky_top": False,
    
    # --- SOL MENÜ (SIDEBAR) ---
    "sidebar": "sidebar-light-success", # Beyaz zemin, Yeşil vurgu
    "sidebar_nav_small_text": True,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,   # Alt menüler içeriden başlar (Daha okunaklı)
    "sidebar_nav_compact_style": True,  # Daha sıkışık, az yer kaplayan yapı
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,     # Modern düz görünüm
    "sidebar_fixed": True,              # Menü sabit, içerik kayar
    
    # --- YERLEŞİM ---
    "layout_boxed": False,
    "footer_fixed": True,
    "navigation_expanded": False, # Menüler kapalı başlar
    
    # --- BUTON STİLLERİ (Outline Tercihin) ---
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-warning", # Uyarı butonları dolu kalsın (Daha dikkat çekici)
        "danger": "btn-danger",   # Silme butonları dolu kalsın
        "success": "btn-success"  # Kaydet butonları dolu kalsın
    }
}
