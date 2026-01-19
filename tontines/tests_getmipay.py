"""
Tests pour l'intégration GetMiPay
Tests unitaires pour vérifier le flux de paiement complet
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from decimal import Decimal
from unittest.mock import patch, MagicMock
from tontines.models import Wallet, Transaction
from tontines.getmipay_service import getmipay_service
import json
import hmac
import hashlib

User = get_user_model()


class GetMiPayDepositTestCase(TestCase):
    """Tests pour les dépôts via GetMiPay"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.wallet, _ = Wallet.objects.get_or_create(user=self.user)
        self.client = Client()
        self.client.login(username='testuser', password='password123')
    
    def test_wallet_topup_page_loads(self):
        """Tester que la page de recharge se charge"""
        response = self.client.get('/wallet/topup/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tontines/wallet_topup.html')
    
    def test_wallet_topup_form_required_fields(self):
        """Tester que les champs requis sont validés"""
        # Montant manquant
        response = self.client.post('/wallet/topup/', {
            'phone_number': '+226XXXXXXXXX',
            'method': 'wave'
        })
        self.assertEqual(response.status_code, 302)  # Redirect on error
        
        # Numéro manquant
        response = self.client.post('/wallet/topup/', {
            'amount': 5000,
            'method': 'wave'
        })
        self.assertEqual(response.status_code, 302)
    
    @patch('tontines.getmipay_service.requests.post')
    def test_initiate_deposit_success(self, mock_post):
        """Tester l'initiation réussie d'un dépôt"""
        # Mock la réponse GetMiPay
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'success': True,
            'transaction_id': 'TXN123456',
            'payment_url': 'https://getmipay.com/payment/TXN123456'
        }
        mock_post.return_value = mock_response
        
        # Appeler le service
        result = getmipay_service.initiate_deposit(
            user=self.user,
            amount=Decimal('5000'),
            phone_number='+226XXXXXXXXX',
            method='wave'
        )
        
        # Vérifier le résultat
        self.assertTrue(result['success'])
        self.assertEqual(result['transaction_id'], 'TXN123456')
        self.assertIn('payment_url', result)
        
        # Vérifier que la Transaction a été créée
        transaction = Transaction.objects.filter(
            user=self.user,
            type='deposit'
        ).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.amount, Decimal('5000'))
    
    @patch('tontines.getmipay_service.requests.post')
    def test_initiate_deposit_failure(self, mock_post):
        """Tester l'échec d'un dépôt"""
        # Mock une erreur GetMiPay
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'success': False,
            'error': 'Invalid phone number'
        }
        mock_post.return_value = mock_response
        
        # Appeler le service
        result = getmipay_service.initiate_deposit(
            user=self.user,
            amount=Decimal('5000'),
            phone_number='invalid',
            method='wave'
        )
        
        # Vérifier l'erreur
        self.assertFalse(result['success'])
        self.assertIn('error', result)


class GetMiPayWithdrawalTestCase(TestCase):
    """Tests pour les retraits via GetMiPay"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.wallet, _ = Wallet.objects.get_or_create(user=self.user)
        self.wallet.balance = Decimal('10000')
        self.wallet.save()
        self.client = Client()
        self.client.login(username='testuser', password='password123')
    
    def test_wallet_withdraw_page_loads(self):
        """Tester que la page de retrait se charge"""
        response = self.client.get('/wallet/withdraw/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tontines/wallet_withdraw.html')
    
    def test_withdraw_insufficient_balance(self):
        """Tester un retrait avec solde insuffisant"""
        self.wallet.balance = Decimal('500')
        self.wallet.save()
        
        response = self.client.post('/wallet/withdraw/', {
            'amount': 1000,
            'phone_number': '+226XXXXXXXXX',
            'method': 'wave'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect on error
    
    @patch('tontines.getmipay_service.requests.post')
    def test_initiate_withdrawal_success(self, mock_post):
        """Tester l'initiation réussie d'un retrait"""
        # Mock la réponse GetMiPay
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'success': True,
            'payout_id': 'PAYOUT123456'
        }
        mock_post.return_value = mock_response
        
        initial_balance = self.wallet.balance
        
        # Appeler le service
        result = getmipay_service.initiate_withdrawal(
            user=self.user,
            amount=Decimal('2000'),
            phone_number='+226XXXXXXXXX',
            method='wave'
        )
        
        # Vérifier le résultat
        self.assertTrue(result['success'])
        
        # Vérifier que le porte-monnaie a été débité
        self.wallet.refresh_from_db()
        expected_balance = initial_balance - Decimal('2000')
        self.assertEqual(self.wallet.balance, expected_balance)
        
        # Vérifier que la Transaction a été créée
        transaction = Transaction.objects.filter(
            user=self.user,
            type='withdraw'
        ).first()
        self.assertIsNotNone(transaction)


class GetMiPayWebhookTestCase(TestCase):
    """Tests pour les webhooks GetMiPay"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.wallet, _ = Wallet.objects.get_or_create(user=self.user)
        self.wallet.balance = Decimal('1000')
        self.wallet.save()
        self.client = Client()
    
    def test_webhook_signature_verification(self):
        """Tester la vérification de signature du webhook"""
        from django.conf import settings
        
        webhook_data = {
            'event': 'payment.completed',
            'transaction_id': 'TXN123456',
            'user_id': self.user.id
        }
        
        # Générer la signature correcte
        message = json.dumps(webhook_data, sort_keys=True)
        correct_signature = hmac.new(
            settings.GETMIPAY_WEBHOOK_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Tester la vérification
        result = getmipay_service.verify_webhook(correct_signature, webhook_data)
        self.assertTrue(result)
        
        # Tester avec une mauvaise signature
        wrong_signature = 'wrong_signature_123'
        result = getmipay_service.verify_webhook(wrong_signature, webhook_data)
        self.assertFalse(result)
    
    def test_webhook_payment_completed(self):
        """Tester le traitement d'un webhook payment.completed"""
        # Créer une Transaction en attente
        transaction = Transaction.objects.create(
            user=self.user,
            wallet=self.wallet,
            amount=Decimal('5000'),
            type='deposit',
            note='Dépôt en attente'
        )
        
        webhook_data = {
            'event': 'payment.completed',
            'transaction_id': str(transaction.id),
            'user_id': self.user.id
        }
        
        # Traiter le webhook
        result = getmipay_service.process_webhook('payment.completed', webhook_data)
        
        # Vérifier que le porte-monnaie a été crédité
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('6000'))
        
        # Vérifier que la Transaction est marquée comme complétée
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, 'completed')
    
    def test_webhook_payment_failed(self):
        """Tester le traitement d'un webhook payment.failed"""
        initial_balance = self.wallet.balance
        
        # Créer une Transaction en attente
        transaction = Transaction.objects.create(
            user=self.user,
            wallet=self.wallet,
            amount=Decimal('5000'),
            type='deposit',
            note='Dépôt en attente'
        )
        
        webhook_data = {
            'event': 'payment.failed',
            'transaction_id': str(transaction.id),
            'error': 'Payment declined'
        }
        
        # Traiter le webhook
        result = getmipay_service.process_webhook('payment.failed', webhook_data)
        
        # Vérifier que le porte-monnaie n'a pas changé
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, initial_balance)
        
        # Vérifier que la Transaction est marquée comme échouée
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, 'failed')


class GetMiPayIntegrationTestCase(TestCase):
    """Tests d'intégration complets"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.wallet, _ = Wallet.objects.get_or_create(user=self.user)
        self.wallet.balance = Decimal('0')
        self.wallet.save()
        self.client = Client()
        self.client.login(username='testuser', password='password123')
    
    @patch('tontines.getmipay_service.requests.post')
    def test_complete_deposit_flow(self, mock_post):
        """Tester le flux complet de dépôt"""
        # Mock la réponse GetMiPay
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'success': True,
            'transaction_id': 'TXN123456',
            'payment_url': 'https://getmipay.com/payment/TXN123456'
        }
        mock_post.return_value = mock_response
        
        # Accéder à la page de recharge
        response = self.client.get('/wallet/topup/')
        self.assertEqual(response.status_code, 200)
        
        # Soumettre le formulaire
        response = self.client.post('/wallet/topup/', {
            'amount': 5000,
            'phone_number': '+226XXXXXXXXX',
            'method': 'wave'
        })
        
        # Vérifier la redirection vers GetMiPay
        self.assertEqual(response.status_code, 302)
        self.assertIn('getmipay.com', response.url)
        
        # Vérifier que la Transaction a été créée
        transaction = Transaction.objects.filter(
            user=self.user,
            type='deposit'
        ).first()
        self.assertIsNotNone(transaction)
