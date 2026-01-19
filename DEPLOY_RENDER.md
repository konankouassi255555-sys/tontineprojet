# 🚀 Guide de Déploiement TontinePro sur Render

## 📋 Table des matières

- [Prérequis](#prérequis)
- [Préparation du projet](#préparation-du-projet)
- [Création du compte Render](#création-du-compte-render)
- [Configuration sur Render](#configuration-sur-render)
- [Déploiement](#déploiement)
- [Post-déploiement](#post-déploiement)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## 🔍 Prérequis

Avant de commencer, assurez-vous d'avoir:

- ✅ Un compte **GitHub** (pour versionner le code)
- ✅ Un compte **Render** (https://render.com)
- ✅ Django configuré correctement localement
- ✅ Git installé et configuré
- ✅ PostgreSQL (optionnel mais recommandé pour production)

---

## 📦 Préparation du projet

### 1. Créer le fichier `requirements.txt`

```bash
pip freeze > requirements.txt
```

Vérifiez que le fichier contient au minimum:

```
Django==6.0.1
Pillow==10.0.0
gunicorn==21.0.0
whitenoise==6.5.0
psycopg2-binary==2.9.7
python-dotenv==1.0.0
```

### 2. Créer un fichier `.env` pour les variables d'environnement

```bash
touch .env
```

Remplissez-le avec:

```
DEBUG=False
SECRET_KEY=your-secret-key-here-generate-a-long-random-string
ALLOWED_HOSTS=your-app.onrender.com,localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### 3. Créer un fichier `runtime.txt` pour spécifier la version Python

```bash
echo "python-3.13.1" > runtime.txt
```

### 4. Créer un fichier `render.yaml` pour l'infrastructure

```yaml
services:
  - type: web
    name: tontinepro
    env: python
    plan: free
    buildCommand: "pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput"
    startCommand: "gunicorn config.wsgi:application"
    envVars:
      - key: DEBUG
        value: false
      - key: PYTHON_VERSION
        value: 3.13.1

databases:
  - name: tontinepro_db
    databaseName: tontinepro_db
    user: tontinepro_user
    plan: free
```

### 5. Mettre à jour `settings.py` pour production

Modifiez `config/settings.py`:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-fallback')

# Debug
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Allowed hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'db.sqlite3'),
        'USER': os.getenv('DB_USER', 'user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Use SQLite if DATABASE_URL not set (development)
if not os.getenv('DATABASE_URL'):
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CSRF & Security
CSRF_TRUSTED_ORIGINS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Installed apps (ajouter whitenoise)
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Ajouter ici
    'django.middleware.security.SecurityMiddleware',
    # ... rest of middleware
]
```

### 6. Créer un fichier `Procfile` (optionnel mais recommandé)

```
web: gunicorn config.wsgi:application
```

### 7. Créer un fichier `.gitignore` pour éviter les fichiers sensibles

```
.env
.env.local
*.pyc
__pycache__/
*.sqlite3
media/
staticfiles/
venv/
.DS_Store
*.log
```

### 8. Pusher le code sur GitHub

```bash
git init
git add .
git commit -m "Initial commit: TontinePro v2.0"
git remote add origin https://github.com/votre-username/tontine_projet.git
git branch -M main
git push -u origin main
```

---

## 🌐 Création du compte Render

1. Accédez à https://render.com
2. Cliquez sur **"Sign Up"**
3. Connectez-vous avec GitHub (recommandé)
4. Autorisez Render à accéder à vos repositories
5. Confirmez votre email

---

## ⚙️ Configuration sur Render

### Étape 1: Créer une nouvelle application Web

1. Dashboard Render → **"New"** → **"Web Service"**
2. Sélectionnez votre repository `tontine_projet`
3. Remplissez les détails:

| Champ | Valeur |
|-------|--------|
| Name | `tontinepro` |
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput` |
| Start Command | `gunicorn config.wsgi:application` |
| Plan | Free (ou Starter) |

### Étape 2: Configurer les variables d'environnement

Dans **"Environment"**, ajoutez:

```
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-generate-here
ALLOWED_HOSTS=tontinepro.onrender.com,localhost
PYTHON_VERSION=3.13.1
```

**Pour générer une SECRET_KEY sécurisée:**

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Étape 3: Créer une base de données PostgreSQL (optionnel mais recommandé)

1. Dashboard Render → **"New"** → **"PostgreSQL"**
2. Configurez:
   - Name: `tontinepro-db`
   - Database: `tontinepro_db`
   - User: `tontinepro_user`
   - Plan: Free
3. Copier l'**Internal Database URL**
4. Ajouter à l'app Web comme variable d'env: `DATABASE_URL`

### Étape 4: Lier la base de données à l'app Web

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

---

## 🚀 Déploiement

### Déploiement automatique (recommandé)

1. Le déploiement est **automatique** à chaque push sur `main`
2. Consultez les **"Logs"** pour vérifier la progression
3. Attendez le message **"Deploy live"**

### Déploiement manuel (si nécessaire)

```bash
git push origin main
```

Render détectera le changement et redéploiera automatiquement.

---

## ✅ Post-déploiement

### 1. Créer un superutilisateur

Dans **"Shell"** du service Render:

```bash
python manage.py createsuperuser
```

Ou via command pendant le build:

```bash
python manage.py createsuperuser --noinput --username admin --email admin@tontinepro.com
```

### 2. Vérifier l'application

- Accédez à votre URL: `https://tontinepro.onrender.com`
- Admin: `https://tontinepro.onrender.com/admin`

### 3. Collecter les fichiers statiques

Automatique via le build command, mais si nécessaire:

```bash
python manage.py collectstatic --noinput
```

### 4. Migrer les données

Si modifications du modèle:

```bash
python manage.py migrate
```

---

## 🔧 Troubleshooting

### ❌ Erreur: "Application failed to start"

**Solution:**

1. Vérifiez les logs: Dashboard → **"Logs"**
2. Vérifiez `requirements.txt` - toutes les dépendances?
3. Vérifiez `settings.py` - DEBUG=False?
4. Vérifiez `ALLOWED_HOSTS` - domaine Render inclus?

### ❌ Erreur: "Port already in use"

**Solution:**

Render assigne automatiquement le port. Utilisez la variable d'env `$PORT`:

Dans `settings.py`:

```python
import os
PORT = os.environ.get('PORT', 8000)
```

### ❌ Erreur: "Database connection error"

**Solution:**

1. Vérifiez `DATABASE_URL` est bien configurée
2. Vérifiez les credentials PostgreSQL
3. Relancez le service

### ❌ Fichiers statiques non chargés

**Solution:**

1. Vérifiez `STATIC_ROOT` est configuré
2. Exécutez: `python manage.py collectstatic --noinput`
3. Vérifiez `whitenoise` est dans `MIDDLEWARE`

### ❌ Media files non accessible

**Solution:**

Pour les fichiers uploadés, utilisez un service cloud:

- **AWS S3** (boto3)
- **Google Cloud Storage**
- **Render Disks** (limité)

Configuration avec S3:

```python
# settings.py
if not DEBUG:
    AWS_STORAGE_BUCKET_NAME = 'your-bucket'
    AWS_S3_REGION_NAME = 'us-east-1'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

---

## 🔐 Sécurité

### Checklist sécurité avant production:

- ✅ `DEBUG=False` en production
- ✅ `SECRET_KEY` long et aléatoire
- ✅ `ALLOWED_HOSTS` configuré correctement
- ✅ `CSRF_TRUSTED_ORIGINS` défini
- ✅ HTTPS forcé (`SECURE_SSL_REDIRECT=True`)
- ✅ Cookies sécurisés (`SESSION_COOKIE_SECURE=True`)
- ✅ Base de données PostgreSQL (pas SQLite)
- ✅ Backups configurés
- ✅ Secrets non commitées dans Git

---

## 🛠️ Maintenance

### Mettre à jour le code

```bash
# Développement local
git add .
git commit -m "Update features"
git push origin main

# Render redéploiera automatiquement
```

### Mettre à jour les dépendances

```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

### Consulter les logs

Dashboard Render → Service → **"Logs"**

### Redémarrer l'application

Dashboard Render → Service → **"Manual Deploy"** → **"Deploy latest commit"**

### Monitorer les performances

- Accédez à **"Metrics"** dans le dashboard
- Consultez CPU, RAM, requêtes
- Considérez un plan payant si dépassement

---

## 📊 Monitoring et Alertes

### Activer les alertes

1. Dashboard Render → Service → **"Alerts"**
2. Configurez:
   - CPU > 80%
   - Memory > 80%
   - Service down

### Vérifier la santé

```bash
curl https://tontinepro.onrender.com/health/
```

---

## 💾 Backups

### Base de données PostgreSQL

Render gère automatiquement les backups (plan payant)

Pour exporter manuellement:

```bash
python manage.py dumpdata > backup.json
```

### Media files

Considérez S3 ou Google Cloud Storage pour persistance.

---

## 🎯 Optimisations performance

### 1. Utiliser PostgreSQL au lieu de SQLite
### 2. Activer le compression avec WhiteNoise
### 3. Configurer le caching
### 4. Ajouter un CDN (CloudFlare)
### 5. Optimiser les images (Pillow)

---

## 📞 Support et Ressources

- **Render Docs:** https://render.com/docs
- **Django Deployment:** https://docs.djangoproject.com/en/6.0/howto/deployment/
- **WhiteNoise:** https://whitenoise.evans.io/
- **Gunicorn:** https://gunicorn.org/

---

## ✅ Checklist Déploiement Final

- [ ] `requirements.txt` créé et à jour
- [ ] `.env` configuré localement
- [ ] `runtime.txt` spécifie Python 3.13
- [ ] `settings.py` modifié pour production
- [ ] `Procfile` créé
- [ ] `.gitignore` inclut les fichiers sensibles
- [ ] Code pushé sur GitHub
- [ ] Compte Render créé
- [ ] Variables d'environnement configurées
- [ ] Base de données PostgreSQL liée (optionnel)
- [ ] Déploiement réussi
- [ ] Superutilisateur créé
- [ ] Application accessible et fonctionnelle
- [ ] Logs vérifiés pour erreurs
- [ ] Fichiers statiques chargent correctement

---

## 🎉 Résumé

Votre **TontinePro** est maintenant **live** sur Render! 🚀

- **URL:** https://tontinepro.onrender.com
- **Admin:** https://tontinepro.onrender.com/admin
- **Logs:** Dashboard Render → Logs
- **Monitoring:** Dashboard Render → Metrics

---

**Version:** 1.0 | **Date:** Janvier 2026 | **Plateforme:** Render

Pour questions ou issues, consultez la documentation officielle de Render ou Django.
