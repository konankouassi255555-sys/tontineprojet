#!/usr/bin/env python
"""
Script de configuration GetMiPay
Aide à configurer les clés API et les paramètres de webhook.
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au PATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings


def configure_getmipay():
    """Configurer les clés GetMiPay"""
    print("\n" + "="*60)
    print("Configuration GetMiPay - Tontine Pro")
    print("="*60 + "\n")
    
    print("Cette procédure va vous guider pour configurer les clés GetMiPay.\n")
    
    print("Étape 1: Obtenir vos clés API")
    print("-" * 40)
    print("1. Allez sur https://dashboard.getmipay.com")
    print("2. Créez un compte développeur")
    print("3. Acceptez l'invite d'email de confirmation")
    print("4. Dans le dashboard, allez à 'API Keys'")
    print("5. Créez une nouvelle clé API")
    print("6. Copiez: API Key, Secret Key, Webhook Secret\n")
    
    input("Appuyez sur Entrée une fois que vous avez les clés...")
    
    print("\nÉtape 2: Entrer vos clés")
    print("-" * 40)
    
    api_key = input("API Key: ").strip()
    secret_key = input("Secret Key: ").strip()
    webhook_secret = input("Webhook Secret: ").strip()
    
    # Déterminer l'environnement (sandbox ou production)
    env = input("\nEnvironnement (sandbox ou production) [sandbox]: ").strip().lower() or "sandbox"
    if env == "sandbox":
        api_url = "https://api.sandbox.getmipay.com"
    else:
        api_url = "https://api.getmipay.com"
    
    # Afficher le résumé
    print("\nÉtape 3: Résumé de la configuration")
    print("-" * 40)
    print(f"API Key: {api_key[:20]}...")
    print(f"Secret Key: {secret_key[:20]}...")
    print(f"Webhook Secret: {webhook_secret[:20]}...")
    print(f"API URL: {api_url}")
    print(f"Webhook URL: https://yourdomain.com/webhook/getmipay/")
    print()
    
    # Générer la configuration
    config_content = f"""
# GetMiPay Configuration
# Configuration API pour l'intégration des paiements mobiles

GETMIPAY_API_KEY = '{api_key}'
GETMIPAY_SECRET_KEY = '{secret_key}'
GETMIPAY_API_URL = '{api_url}'
GETMIPAY_WEBHOOK_SECRET = '{webhook_secret}'

# Méthodes de paiement supportées
PAYMENT_METHODS = {{
    'wave': {{'name': 'Wave', 'logo': 'wave.png', 'enabled': True}},
    'orange_money': {{'name': 'Orange Money', 'logo': 'orange.png', 'enabled': True}},
    'moov_money': {{'name': 'Moov Money', 'logo': 'moov.png', 'enabled': True}},
    'mtn_money': {{'name': 'MTN Money', 'logo': 'mtn.png', 'enabled': True}},
    'visa': {{'name': 'Visa Card', 'logo': 'visa.png', 'enabled': True}},
}}
"""
    
    # Afficher les instructions
    print("\nÉtape 4: Mise à jour de settings.py")
    print("-" * 40)
    print("Voici la configuration à ajouter à config/settings.py :\n")
    print(config_content)
    print("\nOu cliquez sur le lien ci-dessous pour mettre à jour automatiquement...")
    
    response = input("\nMettre à jour automatiquement (o/n) ? ").strip().lower()
    
    if response == 'o' or response == 'oui':
        settings_file = project_root / "config" / "settings.py"
        
        # Lire le contenu actuel
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si la configuration existe déjà
        if 'GETMIPAY_API_KEY' in content:
            print("\n⚠️  Configuration GetMiPay trouvée. Mise à jour en cours...\n")
            # Remplacer les clés existantes
            import re
            content = re.sub(
                r"GETMIPAY_API_KEY = '[^']*'",
                f"GETMIPAY_API_KEY = '{api_key}'",
                content
            )
            content = re.sub(
                r"GETMIPAY_SECRET_KEY = '[^']*'",
                f"GETMIPAY_SECRET_KEY = '{secret_key}'",
                content
            )
            content = re.sub(
                r"GETMIPAY_API_URL = '[^']*'",
                f"GETMIPAY_API_URL = '{api_url}'",
                content
            )
            content = re.sub(
                r"GETMIPAY_WEBHOOK_SECRET = '[^']*'",
                f"GETMIPAY_WEBHOOK_SECRET = '{webhook_secret}'",
                content
            )
        else:
            print("\n✓ Ajout de la configuration GetMiPay à settings.py...\n")
            # Ajouter la configuration à la fin du fichier
            content += config_content
        
        # Écrire le fichier
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ config/settings.py mis à jour avec succès !\n")
    
    # Étape 5: Configurer le webhook
    print("\nÉtape 5: Configuration du Webhook")
    print("-" * 40)
    print("1. Allez sur https://dashboard.getmipay.com")
    print("2. Allez à 'Webhooks'")
    print("3. Cliquez sur 'Ajouter un webhook'")
    print("4. Entrez l'URL: https://yourdomain.com/webhook/getmipay/")
    print("5. Sélectionnez les événements:")
    print("   - payment.completed")
    print("   - payment.failed")
    print("   - payout.completed")
    print("   - payout.failed")
    print("6. Cliquez sur 'Créer'\n")
    
    print("\nÉtape 6: Test de l'intégration")
    print("-" * 40)
    print("Pour tester l'intégration en sandbox :\n")
    print("1. Démarrez le serveur: python manage.py runserver")
    print("2. Allez à: http://localhost:8000/wallet/topup/")
    print("3. Remplissez le formulaire avec :")
    print("   - Montant: 5000")
    print("   - Numéro: +226XXXXXXXXXX")
    print("   - Méthode: Wave")
    print("4. Cliquez sur 'Payer'")
    print("5. Utilisez les identifiants de test GetMiPay")
    print("6. Confirmez le paiement")
    print("7. Vérifiez que le porte-monnaie est crédité\n")
    
    print("="*60)
    print("Configuration terminée avec succès !")
    print("="*60 + "\n")


def test_connection():
    """Tester la connexion à l'API GetMiPay"""
    print("\nTest de connexion à GetMiPay...")
    print("-" * 40)
    
    try:
        import requests
        from django.conf import settings
        
        api_key = settings.GETMIPAY_API_KEY
        api_url = settings.GETMIPAY_API_URL
        
        if api_key == 'your_api_key_here':
            print("⚠️  Les clés API ne sont pas configurées. Configurez-les d'abord.\n")
            return False
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Faire un test de requête (ping)
        response = requests.get(f'{api_url}/v1/health', headers=headers, timeout=5)
        
        if response.status_code == 200:
            print("✓ Connexion à GetMiPay réussie !")
            print(f"✓ Environnement: {api_url}")
            return True
        else:
            print(f"⚠️  Statut HTTP: {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Erreur de connexion. Vérifiez votre connexion Internet.")
        return False
    except requests.exceptions.Timeout:
        print("✗ Timeout. GetMiPay ne répond pas.")
        return False
    except Exception as e:
        print(f"✗ Erreur: {str(e)}")
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Configuration GetMiPay')
    parser.add_argument('--test', action='store_true', help='Tester la connexion')
    args = parser.parse_args()
    
    if args.test:
        test_connection()
    else:
        configure_getmipay()
