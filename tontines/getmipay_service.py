"""
Service d'intégration GetMiPay pour les paiements mobiles et les retraits.
GetMiPay est un agrégateur de paiements qui supporte Wave, Orange Money, Moov, MTN, et Visa.
"""

import requests
import json
import hashlib
import hmac
from django.conf import settings
from django.utils import timezone
from .models import Transaction, Wallet
import logging

logger = logging.getLogger(__name__)


class GetMiPayService:
    """Service pour gérer les transactions GetMiPay"""
    
    def __init__(self):
        self.api_key = settings.GETMIPAY_API_KEY
        self.secret_key = settings.GETMIPAY_SECRET_KEY
        self.api_url = settings.GETMIPAY_API_URL
        self.webhook_secret = settings.GETMIPAY_WEBHOOK_SECRET
    
    def _generate_signature(self, data):
        """Générer une signature HMAC pour sécuriser les requêtes"""
        message = json.dumps(data, sort_keys=True)
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_headers(self):
        """Retourner les headers pour les requêtes GetMiPay"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'TontinePro/1.0'
        }
    
    def initiate_deposit(self, user, amount, phone_number, method='wave'):
        """
        Initier un dépôt (recharge porte-monnaie).
        
        Args:
            user: Utilisateur effectuant le dépôt
            amount: Montant en FCFA
            phone_number: Numéro de téléphone
            method: Méthode de paiement (wave, orange_money, moov_money, mtn_money, visa)
        
        Returns:
            dict avec transaction_id et payment_url
        """
        try:
            payload = {
                'api_key': self.api_key,
                'amount': float(amount),
                'currency': 'XOF',
                'phone_number': phone_number,
                'method': method,
                'reference': f'DEPOSIT-{user.id}-{timezone.now().timestamp()}',
                'callback_url': f'https://yourdomain.com/callback/getmipay/',
                'return_url': f'https://yourdomain.com/wallet/deposit-callback/',
                'description': f'Dépôt porte-monnaie - {user.email}',
            }
            
            signature = self._generate_signature(payload)
            payload['signature'] = signature
            
            response = requests.post(
                f'{self.api_url}/v1/payments/initiate',
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                # Enregistrer une transaction en attente
                wallet, _ = Wallet.objects.get_or_create(user=user)
                transaction = Transaction.objects.create(
                    user=user,
                    wallet=wallet,
                    amount=float(amount),
                    type='deposit',
                    note=f'Dépôt initialisé via {method} - {data.get("transaction_id")}'
                )
                
                logger.info(f"Dépôt initié pour {user.email}: {amount} FCFA")
                return {
                    'success': True,
                    'transaction_id': data.get('transaction_id'),
                    'payment_url': data.get('payment_url'),
                    'db_transaction_id': transaction.id
                }
            else:
                logger.error(f"Erreur GetMiPay: {data.get('message')}")
                return {
                    'success': False,
                    'error': data.get('message', 'Erreur inconnue')
                }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur réseau GetMiPay: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur de connexion: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Erreur initiate_deposit: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur serveur: {str(e)}'
            }
    
    def initiate_withdrawal(self, user, amount, phone_number, method='wave'):
        """
        Initier un retrait (depuis le porte-monnaie).
        
        Args:
            user: Utilisateur effectuant le retrait
            amount: Montant en FCFA
            phone_number: Numéro de téléphone
            method: Méthode de paiement
        
        Returns:
            dict avec transaction_id
        """
        try:
            wallet = Wallet.objects.get(user=user)
            
            if wallet.balance < float(amount):
                return {
                    'success': False,
                    'error': 'Solde insuffisant'
                }
            
            payload = {
                'api_key': self.api_key,
                'amount': float(amount),
                'currency': 'XOF',
                'phone_number': phone_number,
                'method': method,
                'reference': f'WITHDRAWAL-{user.id}-{timezone.now().timestamp()}',
                'callback_url': f'https://yourdomain.com/callback/getmipay/',
                'description': f'Retrait porte-monnaie - {user.email}',
            }
            
            signature = self._generate_signature(payload)
            payload['signature'] = signature
            
            response = requests.post(
                f'{self.api_url}/v1/payouts/initiate',
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                # Débiter immédiatement le wallet (sera crédité si le retrait échoue)
                wallet.balance -= float(amount)
                wallet.save()
                
                transaction = Transaction.objects.create(
                    user=user,
                    wallet=wallet,
                    amount=float(amount),
                    type='withdraw',
                    note=f'Retrait initié via {method} - {data.get("transaction_id")}'
                )
                
                logger.info(f"Retrait initié pour {user.email}: {amount} FCFA")
                return {
                    'success': True,
                    'transaction_id': data.get('transaction_id'),
                    'db_transaction_id': transaction.id
                }
            else:
                logger.error(f"Erreur GetMiPay retrait: {data.get('message')}")
                return {
                    'success': False,
                    'error': data.get('message', 'Erreur inconnue')
                }
        
        except Wallet.DoesNotExist:
            return {
                'success': False,
                'error': 'Porte-monnaie non trouvé'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur réseau GetMiPay retrait: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur de connexion: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Erreur initiate_withdrawal: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur serveur: {str(e)}'
            }
    
    def verify_webhook(self, signature, data):
        """Vérifier la signature du webhook GetMiPay"""
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            json.dumps(data, sort_keys=True).encode(),
            hashlib.sha256
        ).hexdigest()
        return signature == expected_signature
    
    def process_webhook(self, event_type, data):
        """
        Traiter un webhook GetMiPay.
        
        Types d'événements:
        - payment.completed: Dépôt complété
        - payment.failed: Dépôt échoué
        - payout.completed: Retrait complété
        - payout.failed: Retrait échoué
        """
        try:
            transaction_id = data.get('transaction_id')
            status = data.get('status')
            amount = float(data.get('amount', 0))
            
            if event_type == 'payment.completed' and status == 'success':
                # Créditer le wallet
                transaction = Transaction.objects.get(id=transaction_id)
                wallet = transaction.wallet
                wallet.balance += amount
                wallet.save()
                transaction.note = f'{transaction.note} - COMPLÉTÉ'
                transaction.save()
                logger.info(f"Dépôt complété: {transaction_id}")
                return True
            
            elif event_type == 'payment.failed':
                # Marquer comme échoué
                transaction = Transaction.objects.get(id=transaction_id)
                transaction.note = f'{transaction.note} - ÉCHOUÉ'
                transaction.save()
                logger.warning(f"Dépôt échoué: {transaction_id}")
                return True
            
            elif event_type == 'payout.completed' and status == 'success':
                # Retrait complété, wallet déjà débité
                transaction = Transaction.objects.get(id=transaction_id)
                transaction.note = f'{transaction.note} - COMPLÉTÉ'
                transaction.save()
                logger.info(f"Retrait complété: {transaction_id}")
                return True
            
            elif event_type == 'payout.failed':
                # Retrait échoué, créditer le wallet
                transaction = Transaction.objects.get(id=transaction_id)
                wallet = transaction.wallet
                wallet.balance += amount
                wallet.save()
                transaction.note = f'{transaction.note} - ÉCHOUÉ, Remboursé'
                transaction.save()
                logger.warning(f"Retrait échoué: {transaction_id}, remboursé")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Erreur process_webhook: {str(e)}")
            return False


# Singleton
getmipay_service = GetMiPayService()
