# 🚀 Déploiement Rapide TontinePro sur Render

## 5 étapes pour déployer en 10 minutes

### 1️⃣ Préparer le projet (2 min)

```bash
# Cloner ou naviguer vers le projet
cd tontine_projet

# Créer requirements.txt
pip freeze > requirements.txt

# Ajouter les fichiers de configuration
# ✅ runtime.txt (déjà créé)
# ✅ Procfile (déjà créé)
# ✅ render.yaml (déjà créé)
# ✅ .env.example (déjà créé)

# Commit et push
git add .
git commit -m "Add Render deployment config"
git push origin main
```

### 2️⃣ Créer un compte Render (3 min)

```
1. Accédez à https://render.com
2. Cliquez "Sign up"
3. Connectez-vous avec GitHub
4. Autorisez Render
5. Confirmez votre email
```

### 3️⃣ Créer l'app Web sur Render (2 min)

```
1. Dashboard → "New" → "Web Service"
2. Sélectionnez: tontine_projet
3. Settings:
   - Name: tontinepro
   - Build: pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   - Start: gunicorn config.wsgi:application
   - Plan: Free
4. Cliquez "Create Web Service"
```

### 4️⃣ Configurer les variables d'environnement (2 min)

```
Dans Render → Service → Environment, ajoutez:

DEBUG=False
SECRET_KEY=<générer une clé sécurisée>
ALLOWED_HOSTS=tontinepro.onrender.com,localhost
PYTHON_VERSION=3.13.1
```

### 5️⃣ Déployer! (1 min)

```
1. Render détecte automatiquement les changements
2. Consultez les "Logs"
3. Attendez "Deploy live" ✅
4. Accédez à https://tontinepro.onrender.com
```

---

## 🎉 C'est fait!

Votre TontinePro est maintenant **LIVE** sur Render!

**URL:** https://tontinepro.onrender.com

---

## 📚 Ressources utiles

- 📖 [Guide complet](./DEPLOY_RENDER.md)
- 🔒 [Documentation Render](https://render.com/docs)
- 🐍 [Django Deployment](https://docs.djangoproject.com/en/6.0/howto/deployment/)

---

## 🆘 Problèmes courants

| Erreur | Solution |
|--------|----------|
| "Application failed to start" | Vérifiez les logs, vérifiez requirements.txt |
| "Database connection error" | Configurez DATABASE_URL |
| "Files statiques non chargés" | Vérifiez STATIC_ROOT et whitenoise |
| "Erreur 500" | Vérifiez DEBUG=False, ALLOWED_HOSTS |

---

**Besoin d'aide?** Consultez [DEPLOY_RENDER.md](./DEPLOY_RENDER.md) pour le guide complet!
