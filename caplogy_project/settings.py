import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'votre-clé-secrète-à-remplacer')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Configuration ALLOWED_HOSTS
allowed_hosts_from_env = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else []
ALLOWED_HOSTS = allowed_hosts_from_env + [
    'localhost',
    '127.0.0.1',
    'intranet.caplogy.com',
    # Ajoutez d'autres domaines si nécessaire
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'caplogy_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'caplogy_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'caplogy_app' / 'templates'],
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

WSGI_APPLICATION = 'caplogy_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'caplogy_app' / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# URL vers laquelle @login_required redirige
LOGIN_URL = '/login/'

# (facultatif) où rediriger après une connexion réussie
LOGIN_REDIRECT_URL = '/'

# (facultatif) où rediriger après la déconnexion
LOGOUT_REDIRECT_URL = '/login/'

# LDAP / Active Directory configuration
AD_SERVER = os.getenv('AD_SERVER', 'ldaps://10.3.0.107')
AD_DOMAIN = os.getenv('AD_DOMAIN', 'CAPLOGY')
AD_SEARCH_BASE = os.getenv('AD_SEARCH_BASE', 'DC=CAPLOGY,DC=LOCAL')

# Configuration LDAP avancée
LDAP_BIND_DN = os.getenv('LDAP_BIND_DN', '')  # DN complet pour la connexion service
LDAP_BIND_PASSWORD = os.getenv('LDAP_BIND_PASSWORD', '')  # Mot de passe pour la connexion service
LDAP_USER_SEARCH_BASE = os.getenv('LDAP_USER_SEARCH_BASE', 'OU=Utilisateurs Caplogy,DC=CAPLOGY,DC=LOCAL')

# Configuration SSL/TLS pour LDAPS
LDAP_USE_SSL = True
LDAP_SSL_VERIFY = False  # Mettre à True en production avec certificat valide
