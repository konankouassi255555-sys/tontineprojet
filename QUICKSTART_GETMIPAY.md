# 🚀 Quick Start - GetMiPay Integration

## 5 minutes pour mettre en place GetMiPay

### Étape 1: Obtenir les clés (2 min)

1. Allez sur https://dashboard.getmipay.com
2. Créez un compte développeur
3. Confirmez votre email
4. Allez à "API Keys" et créez une clé
5. Copiez:
   - API Key
   - Secret Key
   - Webhook Secret

### Étape 2: Configurer (1 min)

Exécutez le script de configuration :

```bash
cd c:\Users\Utilisateur\tontine_projet
python setup_getmipay.py
```

Le script va :
- Vous demander les clés
- Mettre à jour settings.py automatiquement
- Afficher les instructions suivantes

### Étape 3: Enregistrer le Webhook (1 min)

1. Dashboard GetMiPay → Webhooks
2. Cliquez "Add Webhook"
3. URL: `https://yourdomain.com/webhook/getmipay/`
4. Événements:
   - ✅ payment.completed
   - ✅ payment.failed
   - ✅ payout.completed
   - ✅ payout.failed
5. Cliquez "Create"

### Étape 4: Démarrer le serveur (1 min)

```bash
cd c:\Users\Utilisateur\tontine_projet
C:/Users/Utilisateur/tontine_projet/venv/Scripts/python.exe manage.py runserver
```

### Étape 5: Tester (1 min)

1. Allez à http://localhost:8000
2. Créez un compte ou connectez-vous
3. Allez à http://localhost:8000/wallet/topup/
4. Remplissez:
   - Montant: 5000 FCFA
   - Numéro: +226XXXXXXXXXX
   - Méthode: Wave
5. Cliquez "Payer"
6. Utilisez les identifiants de test GetMiPay
7. Vérifiez que le porte-monnaie est crédité ✓

---

## 🎯 Fonctionnalités Disponibles

✅ **Recharger le porte-monnaie**
- URL: `/wallet/topup/`
- Montants personnalisés
- 5 méthodes de paiement
- Redirection sécurisée

✅ **Retirer des fonds**
- URL: `/wallet/withdraw/`
- Vérification du solde
- Débit immédiat
- Envoi direct au numéro

✅ **Historique des transactions**
- Voir tous les dépôts/retraits
- Dates et montants détaillés
- Statuts de transaction

✅ **Webhooks sécurisés**
- Signature HMAC-SHA256
- 4 événements traités
- Mise à jour en temps réel

---

## 📞 Commandes Utiles

```bash
# Démarrer le serveur
python manage.py runserver

# Lancer les tests
python manage.py test tontines.tests_getmipay

# Tester la connexion API
python setup_getmipay.py --test

# Créer un superuser
python manage.py createsuperuser

# Accéder à l'admin
# Allez à http://localhost:8000/admin/
```

---

## 🔑 Exemple de Configuration

Après exécution de `setup_getmipay.py`, votre `config/settings.py` contiendra:

```python
GETMIPAY_API_KEY = 'pk_test_abc123...'
GETMIPAY_SECRET_KEY = 'sk_test_xyz789...'
GETMIPAY_API_URL = 'https://api.sandbox.getmipay.com'
GETMIPAY_WEBHOOK_SECRET = 'wh_secret_...'

PAYMENT_METHODS = {
    'wave': {'name': 'Wave', 'enabled': True},
    'orange_money': {'name': 'Orange Money', 'enabled': True},
    'moov_money': {'name': 'Moov Money', 'enabled': True},
    'mtn_money': {'name': 'MTN Money', 'enabled': True},
    'visa': {'name': 'Visa Card', 'enabled': True},
}
```

---

## 🧪 Test Scenarios

### Scénario 1: Dépôt réussi
- Montant: 5000 FCFA
- Attendu: Porte-monnaie crédité, Transaction marquée "complétée"

### Scénario 2: Retrait réussi
- Montant: 2000 FCFA
- Attendu: Porte-monnaie débité, Fonds envoyés

### Scénario 3: Dépôt échoué
- Utiliser identifiants invalides
- Attendu: Erreur affichée, Porte-monnaie non modifié

### Scénario 4: Retrait solde insuffisant
- Montant: supérieur au solde
- Attendu: Erreur "Solde insuffisant"

---

## 📚 Documentation Complète

Pour plus de détails, consultez:

- **[GETMIPAY_INTEGRATION.md](GETMIPAY_INTEGRATION.md)** - Guide complet (300+ lignes)
- **[CHANGELOG_GETMIPAY.md](CHANGELOG_GETMIPAY.md)** - Tous les changements
- **[tontines/tests_getmipay.py](tontines/tests_getmipay.py)** - Exemples de test

---

## ✅ Checklist

- [ ] Clés API obtenues de GetMiPay
- [ ] Script setup_getmipay.py exécuté
- [ ] Webhook configuré dans GetMiPay
- [ ] Serveur démarre sans erreur
- [ ] Page /wallet/topup/ s'affiche
- [ ] Page /wallet/withdraw/ s'affiche
- [ ] Test de dépôt réussi
- [ ] Test de retrait réussi
- [ ] Historique montre les transactions

---

## 🆘 Support Rapide

| Problème | Solution |
|----------|----------|
| "Connexion API refusée" | Vérifier API_KEY dans settings.py |
| "Module requests not found" | `pip install requests` |
| "Page blanche" | Vérifier logs: `tail -f logs/django.log` |
| "Webhook ne s'appelle pas" | Vérifier URL webhook dans dashboard GetMiPay |
| "Signature invalide" | Vérifier WEBHOOK_SECRET |

---

**Prêt ? Commencez par `python setup_getmipay.py` ! 🎉**
