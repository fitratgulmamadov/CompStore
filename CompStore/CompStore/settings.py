from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-hqsf)i_vivvq6@2rqy)+a21mmm@kl&@h3k%y@e6%bjsa!xn+ut'
)

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

_hosts = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in _hosts.split(',') if h.strip()]


INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
]

UNFOLD = {
    "SITE_TITLE": "CompStore",
    "SITE_HEADER": "CompStore",
    "SITE_URL": "/",
    "SITE_SYMBOL": "memory",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "DASHBOARD_CALLBACK": "store.admin.dashboard_callback",
    "COLORS": {
        "font": {
            "subtle-light": "107 114 128",
            "subtle-dark":  "156 163 175",
            "default-light": "75 85 99",
            "default-dark":  "209 213 219",
            "important-light": "17 24 39",
            "important-dark":  "243 244 246",
        },
        "primary": {
            "50":  "255 242 242",
            "100": "255 220 220",
            "200": "255 180 180",
            "300": "255 130 130",
            "400": "255 70 70",
            "500": "229 0 26",
            "600": "200 0 20",
            "700": "170 0 15",
            "800": "130 0 10",
            "900": "90 0 7",
            "950": "60 0 5",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Магазин",
                "items": [
                    {"title": "Товары",         "icon": "memory",        "link": "/admin/store/product/"},
                    {"title": "Категории",      "icon": "category",      "link": "/admin/store/category/"},
                    {"title": "Готовые сборки", "icon": "desktop_windows","link": "/admin/store/prebuiltpc/"},
                    {"title": "Уровни сборок",  "icon": "bar_chart",     "link": "/admin/store/prebuiltlevel/"},
                ],
            },
            {
                "title": "Заказы",
                "items": [
                    {"title": "Заказы",  "icon": "shopping_bag", "link": "/admin/store/order/"},
                    {"title": "Корзины", "icon": "shopping_cart", "link": "/admin/store/cart/"},
                ],
            },
            {
                "title": "Аналитика",
                "items": [
                    {"title": "Посещаемость", "icon": "analytics", "link": "/admin/store/pagevisit/"},
                ],
            },
            {
                "title": "Система",
                "items": [
                    {"title": "Пользователи", "icon": "person",  "link": "/admin/auth/user/"},
                    {"title": "Группы",       "icon": "group",   "link": "/admin/auth/group/"},
                ],
            },
        ],
    },
}


X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'store.middleware.VisitTrackingMiddleware',
]

ROOT_URLCONF = 'CompStore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.cart_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'CompStore.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Доверять заголовкам от Nginx-прокси
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SITE_NAME = 'CompStore'

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Production: trust requests forwarded by Nginx
_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if _origins:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _origins.split(',') if o.strip()]
