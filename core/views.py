from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from tontines.models import Tontine, TontineMember
from datetime import datetime, timedelta
from tontines.models import Contribution
from tontines.models import Tontine, Wallet, Vault

# Create your views here.

def home(request):
    return render(request, 'home.html')


@login_required
def accueil_view(request):
    """Vue d'accueil avec tableau de bord financier complet"""
    user_tontines = Tontine.objects.filter(members__user=request.user).distinct()
    
    # KPIs et statistiques
    total_tontines_count = user_tontines.count()
    active_tontines_count = user_tontines.filter(status='active').count()
    draft_count = user_tontines.filter(status='draft').count()
    completed_count = user_tontines.filter(status='completed').count()
    
    # Total des contributions
    total_contributed = TontineMember.objects.filter(
        user=request.user, status='active'
    ).aggregate(total=Sum('total_contributed'))['total'] or 0
    
    # Total du pot (somme des tontines)
    total_pot = Tontine.objects.filter(members__user=request.user).aggregate(
        total=Sum('total_pot')
    )['total'] or 0
    
    # Nombre total de membres actifs dans les tontines de l'utilisateur
    total_active_members = TontineMember.objects.filter(
        tontine__in=user_tontines, status='active'
    ).values('user').distinct().count()
    
    # Nombre total de contributions
    total_contributions = Contribution.objects.filter(
        tontine__in=user_tontines
    ).count()
    
    # Montant moyen par tontine
    average_pot = total_pot // max(total_tontines_count, 1)
    
    # Données pour les graphiques
    tontine_names = []
    tontine_totals = []
    for t in user_tontines[:10]:
        tontine_names.append(f'"{t.name}"')
        tontine_totals.append(t.total_pot or 0)
    
    # Taux de participation (%)
    if total_tontines_count > 0:
        participation_rate = min(100, (active_tontines_count * 100) // total_tontines_count)
    else:
        participation_rate = 0
    
    # Taux de contribution (%)
    if total_pot > 0:
        contribution_rate = min(100, (total_contributed * 100) // total_pot) if total_pot > 0 else 0
    else:
        contribution_rate = 0
    
    # Taux d'utilisation (%)
    if total_contributions > 0:
        utilization_rate = min(100, (active_tontines_count * 100) // max(total_tontines_count, 1))
    else:
        utilization_rate = 0
    
    # Santé globale (moyenne des trois taux)
    health_rate = (participation_rate + contribution_rate + utilization_rate) // 3
    
    # Portefeuille et coffres
    try:
        wallet = request.user.wallet
        wallet_balance = wallet.balance or 0
    except:
        wallet_balance = 0
    
    vaults_total = Vault.objects.filter(owner=request.user).aggregate(
        total=Sum('balance')
    )['total'] or 0
    
    # Prochaine échéance
    next_due_label = 'Aucune'
    try:
        active_tontines = user_tontines.filter(status='active')
        soon_days = None
        for t in active_tontines:
            start = t.start_date
            if not start:
                continue
            today = datetime.utcnow().date()
            if today < start:
                diff = (start - today).days
            else:
                days_since = (today - start).days
                cycle_days = t.cycle_duration or 30
                cycles_passed = days_since // cycle_days
                next_cycle = start + timedelta(days=(cycles_passed + 1) * cycle_days)
                diff = (next_cycle - today).days
            
            if soon_days is None or diff < soon_days:
                soon_days = diff
        
        if soon_days is not None:
            if soon_days <= 1:
                next_due_label = 'Bientôt'
            else:
                next_due_label = f'dans {soon_days}j'
    except Exception:
        next_due_label = 'N/A'
    
    context = {
        'user_tontines': user_tontines,
        'total_tontines_count': total_tontines_count,
        'active_tontines_count': active_tontines_count,
        'draft_count': draft_count,
        'completed_count': completed_count,
        'total_contributed': total_contributed,
        'total_pot': total_pot,
        'total_active_members': total_active_members,
        'total_contributions': total_contributions,
        'average_pot': average_pot,
        'participation_rate': participation_rate,
        'contribution_rate': contribution_rate,
        'utilization_rate': utilization_rate,
        'health_rate': health_rate,
        'wallet_balance': wallet_balance,
        'vaults_total': vaults_total,
        'next_due_label': next_due_label,
        'tontine_names': '[' + ', '.join(tontine_names) + ']',
        'tontine_totals': '[' + ', '.join(str(t) for t in tontine_totals) + ']',
        'active_count': active_tontines_count,
    }
    return render(request, 'accueil.html', context)


@login_required
def dashboard(request):
    # Nombre de tontines dont l'utilisateur est membre
    user_tontines_count = Tontine.objects.filter(members__user=request.user).distinct().count()

    # Total contribué par l'utilisateur
    total_contributed = TontineMember.objects.filter(user=request.user, status='active').aggregate(total=Sum('total_contributed'))['total'] or 0

    # Calculer prochaine échéance parmi les tontines actives de l'utilisateur
    next_due_label = 'Aucune'
    try:
        active_tontines = Tontine.objects.filter(members__user=request.user, status='active').distinct()
        soon_days = None
        for t in active_tontines:
            start = t.start_date
            if not start:
                continue
            today = datetime.utcnow().date()
            if today < start:
                diff = (start - today).days
            else:
                days_since = (today - start).days
                cycle_days = t.cycle_duration or 30
                cycles_passed = days_since // cycle_days
                next_cycle = start + timedelta(days=(cycles_passed + 1) * cycle_days)
                diff = (next_cycle - today).days

            if soon_days is None or diff < soon_days:
                soon_days = diff

        if soon_days is not None:
            if soon_days <= 1:
                next_due_label = 'bientôt'
            else:
                next_due_label = f'dans {soon_days} jours'
    except Exception:
        next_due_label = 'Aucune'

    context = {
        'user': request.user,
        'user_tontines_count': user_tontines_count,
        'total_contributed': total_contributed,
        'next_due_label': next_due_label,
        'recent_contributions': Contribution.objects.filter(tontine__members__user=request.user).select_related('member__user','tontine').order_by('-created_at')[:6],
    }
    return render(request, 'dashboard.html', context)


@login_required
def calendar_view(request):
    from tontines.models import Tontine
    upcoming = []
    try:
        active_tontines = Tontine.objects.filter(members__user=request.user, status='active').distinct()
        today = datetime.utcnow().date()
        for t in active_tontines:
            if not t.start_date:
                continue
            days_since = (today - t.start_date).days if today >= t.start_date else (t.start_date - today).days
            cycle_days = t.cycle_duration or 30
            if today < t.start_date:
                next_date = t.start_date
            else:
                cycles_passed = max(0, days_since // cycle_days)
                next_date = t.start_date + timedelta(days=(cycles_passed + 1) * cycle_days)
            days = (next_date - today).days
            upcoming.append((t, next_date, days))
        # sort by days
        upcoming.sort(key=lambda x: x[2])
    except Exception:
        upcoming = []

    return render(request, 'calendar.html', {'upcoming': upcoming})