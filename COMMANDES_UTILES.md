#!/bin/bash
# ============================================================================
# Commandes Utiles pour GetMiPay Integration
# ============================================================================

echo "🚀 GetMiPay Integration - Commandes Utiles"
echo "=========================================="

# ============================================================================
# 1. CONFIGURATION INITIALE
# ============================================================================

echo ""
echo "1️⃣  CONFIGURATION INITIALE"
echo "─────────────────────────────────"
echo "# Configuration interactive des clés GetMiPay:"
echo "python setup_getmipay.py"
echo ""
echo "# Tester la connexion GetMiPay:"
echo "python setup_getmipay.py --test"
echo ""

# ============================================================================
# 2. DÉMARRAGE DU SERVEUR
# ============================================================================

echo "2️⃣  DÉMARRAGE DU SERVEUR"
echo "─────────────────────────────────"
echo "# Démarrer le serveur en développement:"
echo "python manage.py runserver"
echo ""
echo "# Démarrer sur un port spécifique:"
echo "python manage.py runserver 0.0.0.0:8080"
echo ""
echo "# Accéder à l'app:"
echo "http://localhost:8000"
echo ""

# ============================================================================
# 3. TESTS ET VALIDATION
# ============================================================================

echo "3️⃣  TESTS ET VALIDATION"
echo "─────────────────────────────────"
echo "# Lancer tous les tests GetMiPay:"
echo "python manage.py test tontines.tests_getmipay -v 2"
echo ""
echo "# Tests de dépôt:"
echo "python manage.py test tontines.tests_getmipay.GetMiPayDepositTestCase -v 2"
echo ""
echo "# Tests de retrait:"
echo "python manage.py test tontines.tests_getmipay.GetMiPayWithdrawalTestCase -v 2"
echo ""
echo "# Tests webhook:"
echo "python manage.py test tontines.tests_getmipay.GetMiPayWebhookTestCase -v 2"
echo ""
echo "# Tests d'intégration:"
echo "python manage.py test tontines.tests_getmipay.GetMiPayIntegrationTestCase -v 2"
echo ""

# ============================================================================
# 4. MIGRATION ET DATABASE
# ============================================================================

echo "4️⃣  MIGRATIONS ET DATABASE"
echo "─────────────────────────────────"
echo "# Créer les migrations (si nouvelles modifications):"
echo "python manage.py makemigrations"
echo ""
echo "# Appliquer les migrations:"
echo "python manage.py migrate"
echo ""
echo "# Voir l'état des migrations:"
echo "python manage.py showmigrations"
echo ""

# ============================================================================
# 5. GESTION D'UTILISATEURS
# ============================================================================

echo "5️⃣  GESTION D'UTILISATEURS"
echo "─────────────────────────────────"
echo "# Créer un superuser (admin):"
echo "python manage.py createsuperuser"
echo ""
echo "# Shell Django interactif:"
echo "python manage.py shell"
echo ""
echo "# Exemples de commandes shell:"
echo "  from django.contrib.auth import get_user_model"
echo "  User = get_user_model()"
echo "  user = User.objects.first()"
echo "  print(user.wallet.balance)"
echo "  exit()"
echo ""

# ============================================================================
# 6. CONSOLE D'ADMINISTRATION
# ============================================================================

echo "6️⃣  CONSOLE D'ADMINISTRATION"
echo "─────────────────────────────────"
echo "# Accéder à l'admin Django:"
echo "http://localhost:8000/admin/"
echo ""
echo "# View transactions:"
echo "http://localhost:8000/admin/tontines/transaction/"
echo ""
echo "# View wallets:"
echo "http://localhost:8000/admin/tontines/wallet/"
echo ""

# ============================================================================
# 7. PAGES CLÉS DE L'APP
# ============================================================================

echo "7️⃣  PAGES CLÉS DE L'APP"
echo "─────────────────────────────────"
echo "# Accueil / Dashboard:"
echo "http://localhost:8000/accueil/"
echo ""
echo "# Porte-monnaie:"
echo "http://localhost:8000/wallet/"
echo ""
echo "# Recharger le porte-monnaie:"
echo "http://localhost:8000/wallet/topup/"
echo ""
echo "# Retirer de l'argent:"
echo "http://localhost:8000/wallet/withdraw/"
echo ""
echo "# Coffres-forts:"
echo "http://localhost:8000/vaults/"
echo ""

# ============================================================================
# 8. DEBUGGING
# ============================================================================

echo "8️⃣  DEBUGGING"
echo "─────────────────────────────────"
echo "# Voir les logs en live:"
echo "tail -f logs/django.log"
echo ""
echo "# Chercher les erreurs GetMiPay:"
echo "grep -i getmipay logs/django.log"
echo ""
echo "# Chercher les erreurs de webhook:"
echo "grep -i webhook logs/django.log"
echo ""
echo "# Tester une requête HTTP:"
echo "curl -X POST http://localhost:8000/webhook/getmipay/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"event\":\"payment.completed\"}'"
echo ""

# ============================================================================
# 9. DÉVELOPPEMENT
# ============================================================================

echo "9️⃣  DÉVELOPPEMENT"
echo "─────────────────────────────────"
echo "# Format le code Python:"
echo "black tontines/"
echo ""
echo "# Lint le code:"
echo "flake8 tontines/"
echo ""
echo "# Vérifier les imports:"
echo "isort tontines/"
echo ""

# ============================================================================
# 10. DÉPLOIEMENT
# ============================================================================

echo "🔟 DÉPLOIEMENT"
echo "─────────────────────────────────"
echo "# Collecter les fichiers statiques:"
echo "python manage.py collectstatic --no-input"
echo ""
echo "# Créer une sauvegarde de la base de données:"
echo "cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)"
echo ""
echo "# Vérifier les problèmes de déploiement:"
echo "python manage.py check --deploy"
echo ""

# ============================================================================
# 11. FICHIERS IMPORTANTS
# ============================================================================

echo "1️⃣1️⃣ FICHIERS IMPORTANTS"
echo "─────────────────────────────────"
echo "# Documentation:"
echo "cat GETMIPAY_INTEGRATION.md"
echo "cat QUICKSTART_GETMIPAY.md"
echo "cat CHANGELOG_GETMIPAY.md"
echo "cat IMPLEMENTATION_SUMMARY.md"
echo "cat ARCHITECTURE_DIAGRAM.md"
echo ""
echo "# Code source:"
echo "cat tontines/getmipay_service.py"
echo "cat tontines/views.py"
echo "cat config/urls.py"
echo "cat config/settings.py"
echo ""

# ============================================================================
# 12. VARIABLES D'ENVIRONNEMENT
# ============================================================================

echo "1️⃣2️⃣ VARIABLES D'ENVIRONNEMENT (optionnel)"
echo "─────────────────────────────────"
echo "# Exporter pour la session (Linux/Mac):"
echo "export DJANGO_SETTINGS_MODULE=config.settings"
echo "export GETMIPAY_API_KEY=pk_test_..."
echo "export GETMIPAY_SECRET_KEY=sk_test_..."
echo ""
echo "# Sur Windows PowerShell:"
echo "\$env:DJANGO_SETTINGS_MODULE = 'config.settings'"
echo "\$env:GETMIPAY_API_KEY = 'pk_test_...'"
echo ""

# ============================================================================
# 13. CRÉATION DE DONNÉES DE TEST
# ============================================================================

echo "1️⃣3️⃣ CRÉATION DE DONNÉES DE TEST"
echo "─────────────────────────────────"
echo "# Python shell:"
echo "python manage.py shell << EOF"
echo "from django.contrib.auth import get_user_model"
echo "from tontines.models import Wallet, Tontine, TontineMember"
echo ""
echo "User = get_user_model()"
echo "user = User.objects.create_user("
echo "    username='testuser',"
echo "    email='test@example.com',"
echo "    password='password123'"
echo ")"
echo "wallet = Wallet.objects.create(user=user, balance=10000)"
echo "print(f'User {user.username} created with wallet: {wallet.balance} FCFA')"
echo "EOF"
echo ""

# ============================================================================
# 14. RÉSUMÉ RAPIDE
# ============================================================================

echo ""
echo "═" | awk '{for(i=1;i<=80;i++)printf "═"} END {print ""}'
echo "✨ RÉSUMÉ RAPIDE"
echo "═" | awk '{for(i=1;i<=80;i++)printf "═"} END {print ""}'
echo ""
echo "1. Configuration      : python setup_getmipay.py"
echo "2. Démarrer           : python manage.py runserver"
echo "3. Tester             : python manage.py test tontines.tests_getmipay"
echo "4. Accéder            : http://localhost:8000/"
echo "5. Admin              : http://localhost:8000/admin/"
echo "6. Recharger          : http://localhost:8000/wallet/topup/"
echo ""
echo "📚 Documentation      : Lire les fichiers .md"
echo "🐛 Debugging          : tail -f logs/django.log"
echo "✅ Vérifier           : python setup_getmipay.py --test"
echo ""
echo "═" | awk '{for(i=1;i<=80;i++)printf "═"} END {print ""}'
