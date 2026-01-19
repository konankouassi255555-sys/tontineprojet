# Integration GetMiPay - Guide de Configuration et Utilisation

## Vue d'ensemble

GetMiPay est un agrégateur de paiements mobiles et cartes bancaires qui permet aux utilisateurs de :
- **Recharger** leur porte-monnaie via Wave, Orange Money, Moov Money, MTN Money, ou Visa
- **Retirer** des fonds depuis leur porte-monnaie vers leurs comptes mobiles
- **Payer** les contributions de tontine directement avec le porte-monnaie GetMiPay

## Architecture de l'Intégration

### Fichiers créés/modifiés :

1. **`tontines/getmipay_service.py`** - Service complet d'intégration
   - `initiate_deposit()` - Initier un recharge porte-monnaie
   - `initiate_withdrawal()` - Initier un retrait
   - `verify_webhook()` - Vérifier les webhooks GetMiPay
   - `process_webhook()` - Traiter les événements payment.completed, payment.failed, etc.

2. **`config/settings.py`** - Configuration GetMiPay
   - GETMIPAY_API_KEY
   - GETMIPAY_SECRET_KEY
   - GETMIPAY_API_URL
   - GETMIPAY_WEBHOOK_SECRET
   - PAYMENT_METHODS dict

3. **`tontines/views.py`** - Vues pour les opérations
   - `wallet_deposit_view()` - GET affiche formulaire, POST initie dépôt
   - `wallet_withdraw_view()` - GET affiche formulaire, POST initie retrait
   - `getmipay_webhook_view()` - Webhook endpoint pour GetMiPay callbacks

4. **`config/urls.py`** - Routes
   - `/wallet/topup/` - Page de recharge
   - `/wallet/withdraw/` - Page de retrait
   - `/webhook/getmipay/` - Endpoint webhook

5. **Templates**
   - `templates/tontines/wallet_topup.html` - Formulaire de recharge
   - `templates/tontines/wallet_withdraw.html` - Formulaire de retrait
   - `templates/tontines/wallet_overview.html` - Aperçu du porte-monnaie amélioré

## Flux de Paiement

### Dépôt (Recharge porte-monnaie)

```
1. Utilisateur accède à /wallet/topup/
2. Remplit le formulaire : montant, numéro téléphone, méthode
3. Clique "Payer"
4. wallet_deposit_view() appelle getmipay_service.initiate_deposit()
5. Service crée une Transaction (status: pending) en base
6. Service appelle l'API GetMiPay /v1/payments/initiate
7. Utilisateur est redirigé vers la page de paiement GetMiPay
8. Utilisateur complète le paiement (Wave, Orange Money, etc.)
9. GetMiPay envoie webhook à /webhook/getmipay/ avec event: payment.completed
10. Webhook met à jour la Transaction et crédite le porte-monnaie
```

### Retrait

```
1. Utilisateur accède à /wallet/withdraw/
2. Remplit le formulaire : montant, numéro téléphone, méthode
3. Clique "Retirer"
4. wallet_withdraw_view() appelle getmipay_service.initiate_withdrawal()
5. Service vérifie le solde
6. Service débite immédiatement le porte-monnaie (optimistic debit)
7. Service crée une Transaction (status: pending) en base
8. Service appelle l'API GetMiPay /v1/payouts/initiate
9. Utilisateur reçoit l'argent sur son compte mobile
10. GetMiPay envoie webhook payout.completed
11. Webhook marque la Transaction comme completed
12. Si payout.failed, webhook peut créditer le porte-monnaie
```

## Configuration

### 1. Obtenir les clés GetMiPay

- Allez sur https://dashboard.getmipay.com
- Créez un compte développeur
- Récupérez :
  - API Key
  - Secret Key
  - Configurez le Webhook Secret

### 2. Mettre à jour `config/settings.py`

```python
# GetMiPay Configuration
GETMIPAY_API_KEY = 'your_api_key_here'
GETMIPAY_SECRET_KEY = 'your_secret_key_here'
GETMIPAY_API_URL = 'https://api.sandbox.getmipay.com'  # sandbox
# ou en production: 'https://api.getmipay.com'
GETMIPAY_WEBHOOK_SECRET = 'your_webhook_secret_here'
```

### 3. Configurer l'URL du Webhook

- Dans le dashboard GetMiPay, enregistrez l'URL du webhook :
  - Développement: `http://localhost:8000/webhook/getmipay/`
  - Production: `https://yourdomain.com/webhook/getmipay/`

### 4. Migrations (si nécessaire)

```bash
python manage.py makemigrations
python manage.py migrate
```

## Tests Sandbox

### Tester un dépôt réussi :

1. Accédez à `http://localhost:8000/wallet/topup/`
2. Remplissez :
   - Montant: 5000 FCFA
   - Numéro: +226XXXXXXXXXX
   - Méthode: Wave
3. Cliquez "Payer"
4. Vous êtes redirigé à GetMiPay
5. Utilisez les identifiants sandbox Wave :
   - Numéro: +226 70 00 00 00 (exemple)
   - PIN: 0000
6. Confirmez le paiement
7. Vous êtes redirigé à l'app
8. Le porte-monnaie est crédité

### Tester un retrait :

1. Accédez à `http://localhost:8000/wallet/withdraw/`
2. Remplissez :
   - Montant: 2000 FCFA
   - Numéro: +226XXXXXXXXXX
   - Méthode: Orange Money
3. Cliquez "Retirer"
4. Le porte-monnaie est débité immédiatement
5. L'argent est envoyé au numéro (en sandbox, c'est simulé)

## Codes d'Erreur Courants

| Code | Signification | Solution |
|------|---------------|----------|
| 400 | Requête invalide | Vérifiez les paramètres (montant, numéro) |
| 401 | Authentification échouée | Vérifiez API_KEY et SECRET_KEY |
| 403 | Accès refusé | Vérifiez les permissions dans le dashboard |
| 429 | Trop de requêtes | Attendez avant de renvoyer |
| 500 | Erreur serveur | Contactez le support GetMiPay |

## Monitorer les Transactions

### Vue d'ensemble des transactions :

- Accédez à `/wallet/` pour voir l'historique
- Chaque transaction affiche : Date, Type (Dépôt/Retrait), Montant, Note
- Les transactions en attente sont visibles dans les logs Django

### Logs :

```bash
# Voir les logs GetMiPay
tail -f logs/django.log | grep GetMiPay
```

## Sécurité

### Points importants :

1. **Signature HMAC** - Tous les webhooks sont signés avec HMAC-SHA256
2. **HTTPS obligatoire** en production
3. **Pas de stockage** de numéros de carte ou PIN
4. **Transactions atomiques** - Débit/crédit en une seule opération
5. **Timeouts** - Configuré à 30 secondes pour les appels API

### Vérification de la signature webhook :

```python
def verify_webhook(signature, data):
    expected_sig = hmac.new(
        WEBHOOK_SECRET.encode(),
        json.dumps(data, sort_keys=True).encode(),
        hashlib.sha256
    ).hexdigest()
    return signature == expected_sig
```

## Troubleshooting

### Le webhook n'est pas appelé

1. Vérifiez l'URL webhook dans le dashboard GetMiPay
2. Vérifiez que votre serveur est accessible de l'extérieur
3. Vérifiez les logs GetMiPay (dashboard)
4. Test manuel : `curl -X POST http://localhost:8000/webhook/getmipay/ -H "Content-Type: application/json" -d '{"event":"payment.completed", "transaction_id":"123"}'`

### Le paiement s'affiche en sandbox mais pas en production

1. Vérifiez les clés API (pas de mélange sandbox/production)
2. Confirmez les URLs de redirection
3. Vérifiez les logs de l'API GetMiPay
4. Testez d'abord avec une petite transaction (1 FCFA)

### Erreur "Signature invalide"

1. Vérifiez le WEBHOOK_SECRET en base de données
2. Vérifiez que la signature dans les headers est correcte
3. Vérifiez le contenu du body (ne pas ajouter d'espaces)

## Fonctionnalités Futures

- [ ] Support des paiements récurrents
- [ ] Split payments (partage automatique aux membres)
- [ ] Rapports détaillés GetMiPay
- [ ] Intégration USSD pour feature phones
- [ ] Notifications SMS des transactions
- [ ] Cashback/Rewards program

## Contactez le Support

- GetMiPay: https://support.getmipay.com
- Tontine Pro: [email de support]
