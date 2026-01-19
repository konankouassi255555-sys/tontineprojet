from .settings import AUTH_USER_MODEL


def wallet_context(request):
    """Expose wallet and vault totals to templates when user is authenticated."""
    data = {}
    try:
        user = request.user
        if user and user.is_authenticated:
            # Import here to avoid import loops
            from tontines.models import Wallet, Vault
            try:
                wallet = user.wallet
                wallet_balance = wallet.balance
            except Exception:
                wallet_balance = 0
            try:
                vaults = Vault.objects.filter(owner=user)
                vaults_total = sum([v.balance or 0 for v in vaults])
            except Exception:
                vaults_total = 0
            data['wallet_balance'] = wallet_balance
            data['vaults_total'] = vaults_total
    except Exception:
        pass
    return data
