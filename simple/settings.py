"""
Django settings for simple project.

Architecture:
  - Sharded PostgreSQL via ShardRouter (see manage.py)
  - Each shard has an async read replica
  - Django internals (auth, sessions, admin) stay on 'default'
  - Environment-driven: no secrets in source, no hardcoded hosts
"""

import os
from pathlib import Path

import dj_database_url

from manage import ShardRouter, build_databases, SHARD_COUNT

# ── Paths ─────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent


# ── Environment helpers ───────────────────────────────────────────────────────

def env(key: str, default: str | None = None, *, required: bool = False) -> str | None:
    """Fetch an env var, optionally raising if absent in production."""
    value = os.environ.get(key, default)
    if required and not value:
        raise ImproperlyConfigured(f"Required environment variable '{key}' is not set.")
    return value


# ── Security ──────────────────────────────────────────────────────────────────

SECRET_KEY = env("DJANGO_SECRET_KEY", required=True)

DEBUG = env("DJANGO_DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in env("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]

# Secure cookie / HTTPS settings — inactive in DEBUG, enforced in production
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG


# ── Applications ──────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    "feed",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "simple.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "simple.wsgi.application"


# ── Database — sharded + replicated ───────────────────────────────────────────
#
# build_databases() expands a single base config into:
#   default          — Django internals (auth, sessions, admin, contenttypes)
#   shard_0          — feed app data, primary (reads + writes)
#   shard_0_replica  — feed app data, replica (reads only, async lag possible)
#   shard_1 / shard_1_replica
#   shard_2 / shard_2_replica   (SHARD_COUNT controls how many pairs are built)
#
# To add a shard: bump DJANGO_SHARD_COUNT and export the new host env vars.
# No code changes required.
#
# Env vars expected per shard (shard_id = 0, 1, 2 ...):
#   DB_SHARD_{id}_HOST          primary hostname
#   DB_SHARD_{id}_REPLICA_HOST  replica hostname
#   DB_SHARD_{id}_NAME          database name (defaults to shard_{id})
#
# Connection pool tuning (optional):
#   DB_CONN_MAX_AGE    persistent connection lifetime in seconds (default 60)
#   DB_POOL_SIZE       max connections per process   (default 10)

_base_url = env("DATABASE_URL", required=True)
_conn_max_age = int(env("DB_CONN_MAX_AGE", "60"))

_base_config = dj_database_url.parse(
    _base_url,
    conn_max_age=_conn_max_age,
    conn_health_checks=True,
)

DATABASES = build_databases({"default": _base_config})

DATABASE_ROUTERS = ["manage.ShardRouter"]

# Shard health check — logged at startup, does not block boot
_SHARD_ALIASES = (
    ["default"]
    + [f"shard_{i}" for i in range(SHARD_COUNT)]
    + [f"shard_{i}_replica" for i in range(SHARD_COUNT)]
)


# ── Auth ──────────────────────────────────────────────────────────────────────

AUTH_USER_MODEL = "feed.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ── Internationalisation ──────────────────────────────────────────────────────

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ── Static files ──────────────────────────────────────────────────────────────

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


# ── Misc ──────────────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
