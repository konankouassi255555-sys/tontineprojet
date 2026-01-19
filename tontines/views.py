from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from .models import Tontine, TontineMember, BeneficiaryAllocation
from .models import Contribution, Wallet, Vault, Transaction
from .forms import TontineCreationForm
from django.contrib.auth import get_user_model
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import models  # Pour utiliser models.Q
from django.utils import timezone
from django.urls import reverse
@login_required
def tontine_create_view(request):
    if request.method == 'POST':
        form = TontineCreationForm(request.POST)
        if form.is_valid():
            try:
                tontine = form.save(commit=False)
                tontine.manager = request.user
                tontine.status = 'draft'
                tontine.save()

                TontineMember.objects.create(
                    tontine=tontine,
                    user=request.user,
                    status='active',
                    role='president'
                )

                messages.success(request, f'La tontine "{tontine.name}" a été créée avec succès!')
                return redirect('tontine_detail', tontine_id=tontine.id)
            except Exception as e:
                messages.error(request, f'Une erreur est survenue: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = TontineCreationForm()

    return render(request, 'tontines/create.html', {'form': form})

@login_required
def tontine_list_view(request):
    # Tontines où l'utilisateur est membre
    user_tontines = Tontine.objects.filter(members__user=request.user).distinct()
    
    # Tontines gérées par l'utilisateur
    managed_tontines = Tontine.objects.filter(manager=request.user)
    
    # Statistiques
    stats = {
        'total_tontines': user_tontines.count(),
        'active_tontines': user_tontines.filter(status='active').count(),
        'total_contributed': TontineMember.objects.filter(
            user=request.user, status='active'
        ).aggregate(total=Sum('total_contributed'))['total'] or 0,
    }
    
    context = {
        'user_tontines': user_tontines,
        'managed_tontines': managed_tontines,
        'stats': stats,
    }
    return render(request, 'tontines/list.html', context)

@login_required
def tontine_detail_view(request, tontine_id):
    tontine = get_object_or_404(Tontine, id=tontine_id)
    
    # Vérifier si l'utilisateur a accès à cette tontine
    if not (request.user == tontine.manager or 
            tontine.members.filter(user=request.user).exists()):
        messages.error(request, "Vous n'avez pas accès à cette tontine.")
        return redirect('tontine_list')
    
    # Obtenir les membres
    members = tontine.members.all().select_related('user')
    
    # Statistiques de la tontine
    stats = {
        'total_members': members.count(),
        'active_members': members.filter(status='active').count(),
        'total_collected': members.aggregate(total=Sum('total_contributed'))['total'] or 0,
    }
    
    # Dernières contributions
    recent_contributions = tontine.contributions.select_related('member__user').order_by('-created_at')[:8]

    # Wallet utilisateur (s'il existe)
    user_wallet = None
    try:
        user_wallet = request.user.wallet
    except Exception:
        user_wallet = None

    context = {
        'tontine': tontine,
        'members': members,
        'stats': stats,
        'is_manager': request.user == tontine.manager,
        'recent_contributions': recent_contributions,
        'user_wallet': user_wallet,
    }
    return render(request, 'tontines/detail.html', context)

@login_required
def tontine_activate_view(request, tontine_id):
    tontine = get_object_or_404(Tontine, id=tontine_id)
    
    # Vérifier que l'utilisateur est le gestionnaire
    if request.user != tontine.manager:
        messages.error(request, "Seul le gestionnaire peut activer la tontine.")
        return redirect('tontine_detail', tontine_id=tontine.id)
    
    # Vérifier que la tontine est en brouillon
    if tontine.status != 'draft':
        messages.error(request, "Seules les tontines en brouillon peuvent être activées.")
        return redirect('tontine_detail', tontine_id=tontine.id)
    
    if request.method == 'POST':
        tontine.status = 'active'
        tontine.save()
        messages.success(request, f'La tontine "{tontine.name}" a été activée avec succès!')
        return redirect('tontine_detail', tontine_id=tontine.id)
    
    # Si c'est une requête GET, afficher une page de confirmation
    return render(request, 'tontines/activate.html', {'tontine': tontine})


@login_required
def tontine_manage_view(request, tontine_id):
    tontine = get_object_or_404(Tontine, id=tontine_id)
    
    # Vérifier que l'utilisateur est le gestionnaire
    if request.user != tontine.manager:
        messages.error(request, "Accès refusé. Seul le gestionnaire peut gérer cette tontine.")
        return redirect('tontine_detail', tontine_id=tontine.id)
    
    # Récupérer les membres
    members = tontine.members.all().select_related('user')

    # Statistiques basiques pour la gestion
    stats = {
        'total_members': members.count(),
        'active_members': members.filter(status='active').count(),
        'total_collected': members.aggregate(total=Sum('total_contributed'))['total'] or 0,
    }

    context = {
        'tontine': tontine,
        'members': members,
        'stats': stats,
    }
    return render(request, 'tontines/manage.html', context)


@login_required
def tontine_edit_view(request, tontine_id):
    tontine = get_object_or_404(Tontine, id=tontine_id)
    
    # Vérifier que l'utilisateur est le gestionnaire
    if request.user != tontine.manager:
        messages.error(request, "Seul le gestionnaire peut modifier la tontine.")
        return redirect('tontine_detail', tontine_id=tontine.id)
    
    # Seules les tontines en brouillon peuvent être modifiées
    if tontine.status != 'draft':
        messages.error(request, "Seules les tontines en brouillon peuvent être modifiées.")
        return redirect('tontine_detail', tontine_id=tontine.id)
    
    if request.method == 'POST':
        form = TontineCreationForm(request.POST, instance=tontine)
        if form.is_valid():
            form.save()
            messages.success(request, 'La tontine a été mise à jour avec succès!')
            return redirect('tontine_detail', tontine_id=tontine.id)
    else:
        form = TontineCreationForm(instance=tontine)
    
    context = {
        'form': form,
        'tontine': tontine,
        'is_edit': True,
    }
    return render(request, 'tontines/create.html', context)


@login_required
def tontine_join_view(request):
    """
    Permettre à un utilisateur de rejoindre une tontine via son code.
    Crée une TontineMember en statut 'pending' (le gestionnaire doit approuver).
    """
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        if not code:
            messages.error(request, 'Veuillez fournir un code de tontine.')
            return redirect('tontine_list')

        try:
            tontine = Tontine.objects.get(code=code)

            # N'autoriser que les tontines actives
            if tontine.status != 'active':
                messages.error(request, "Vous ne pouvez rejoindre qu'une tontine active.")
                return redirect('tontine_list')

            # Vérifier si l'utilisateur est déjà membre
            if TontineMember.objects.filter(tontine=tontine, user=request.user).exists():
                messages.warning(request, 'Vous êtes déjà membre de cette tontine.')
                return redirect('tontine_detail', tontine_id=tontine.id)

            # Créer la demande d'adhésion en attente
            TontineMember.objects.create(
                tontine=tontine,
                user=request.user,
                role='member',
                status='pending'
            )
            messages.success(request, "Demande d'adhésion envoyée au gestionnaire.")
            return redirect('tontine_list')

        except Tontine.DoesNotExist:
            messages.error(request, 'Tontine introuvable pour ce code.')
            return redirect('tontine_list')

    return redirect('tontine_list')

@login_required
@require_POST
@csrf_exempt
def tontine_contribute_view(request, tontine_id):
    """Enregistrer une contribution pour l'utilisateur connecté.
    Si requête AJAX, renvoie JSON, sinon redirige vers la page détail.
    """
    try:
        tontine = Tontine.objects.get(id=tontine_id)
        # Vérifier que la tontine est active
        if tontine.status != 'active':
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Tontine inactive.'})
            messages.error(request, "La tontine n'est pas active.")
            return redirect('tontine_detail', tontine_id=tontine.id)

        # Récupérer l'enregistrement du membre
        try:
            member = TontineMember.objects.get(tontine=tontine, user=request.user)
        except TontineMember.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': "Vous n'êtes pas membre."})
            messages.error(request, "Vous n'êtes pas membre de cette tontine.")
            return redirect('tontine_list')

        # Montant: par défaut montant de la tontine
        amount = tontine.contribution_amount
        # Créer la contribution
        contribution = Contribution.objects.create(
            tontine=tontine,
            member=member,
            amount=amount
        )

        # Mettre à jour totaux
        member.total_contributed = (member.total_contributed or 0) + amount
        member.save()
        tontine.total_pot = (tontine.total_pot or 0) + amount
        tontine.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Contribution enregistrée.'})

        messages.success(request, 'Contribution enregistrée avec succès.')
        return redirect('tontine_detail', tontine_id=tontine.id)

    except Tontine.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Tontine non trouvée.'})
        messages.error(request, 'Tontine non trouvée.')
        return redirect('tontine_list')
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, f'Erreur: {str(e)}')
        return redirect('tontine_detail', tontine_id=tontine_id)

User = get_user_model()

@login_required
def tontine_invite_view(request, tontine_id):
    tontine = get_object_or_404(Tontine, id=tontine_id)
    
    # Vérifier que l'utilisateur est le gestionnaire
    if request.user != tontine.manager:
        messages.error(request, "Seul le gestionnaire peut inviter des membres.")
        return redirect('tontine_detail', tontine_id=tontine.id)
    
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        role = request.POST.get('role', 'member')
        
        # Chercher l'utilisateur
        try:
            user = User.objects.get(
                models.Q(username=username_or_email) | 
                models.Q(email=username_or_email)
            )
            
            # Vérifier si l'utilisateur est déjà membre
            if TontineMember.objects.filter(tontine=tontine, user=user).exists():
                messages.warning(request, f"{user.get_full_name()} est déjà membre de cette tontine.")
            else:
                # Créer l'invitation
                TontineMember.objects.create(
                    tontine=tontine,
                    user=user,
                    role=role,
                    status='pending'
                )
                messages.success(request, f'Invitation envoyée à {user.get_full_name()}')
                
        except User.DoesNotExist:
            messages.error(request, f'Utilisateur "{username_or_email}" non trouvé.')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
    
    return redirect('tontine_manage', tontine_id=tontine.id)


@login_required
@csrf_exempt
def wallet_deposit_view(request):
    """
    Page qui reçoit POSTs de top-up. Supporte méthodes simulées via 'method' POST param.
    Si GET: affiche la page de sélection du moyen de paiement (top-up).
    """
    if request.method == 'GET':
        # Render top-up selection page
        from django.shortcuts import render
        return render(request, 'tontines/wallet_topup.html')

    # POST processing
    amount = request.POST.get('amount')
    method = request.POST.get('method', 'manual')
    try:
        from decimal import Decimal
        amt = Decimal(amount)
        if amt <= 0:
            raise ValueError('Montant doit être positif')
    except Exception:
        messages.error(request, 'Montant invalide.')
        return redirect('wallet_topup')

    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    # Simuler intégration fournisseur : marquer dépôt comme réussi immédiatement
    # In production, ici on redirigerait vers l'API du fournisseur et on gérerait le callback.
    wallet.balance = (wallet.balance or 0) + amt
    wallet.save()

    Transaction.objects.create(user=request.user, wallet=wallet, amount=amt, type='deposit', note=f'Dépôt via {method}')
    messages.success(request, f'Dépôt de {amt} FCFA effectué via {method}.')
    # Redirect to wallet overview
    return redirect('wallet_overview')


@login_required
@require_POST
@csrf_exempt
def tontine_pay_from_wallet(request, tontine_id):
    """Payer la contribution depuis le wallet de l'utilisateur.
    Vérifie solde et effectue la contribution (création d'un Contribution).
    """
    try:
        tontine = Tontine.objects.get(id=tontine_id)
    except Tontine.DoesNotExist:
        messages.error(request, 'Tontine introuvable.')
        return redirect('tontine_list')

    try:
        wallet = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        messages.error(request, 'Porte-monnaie introuvable. Faites un dépôt.')
        return redirect('tontine_detail', tontine_id=tontine.id)

    amount = tontine.contribution_amount
    from decimal import Decimal
    amt = Decimal(amount)

    if wallet.balance < amt:
        messages.error(request, 'Solde insuffisant sur le porte-monnaie.')
        return redirect('tontine_detail', tontine_id=tontine.id)

    # Vérifier que l'utilisateur est membre actif
    try:
        member = TontineMember.objects.get(tontine=tontine, user=request.user)
        if member.status != 'active':
            messages.error(request, "Votre adhésion n'est pas active. Le gestionnaire doit d'abord vous accepter.")
            return redirect('tontine_detail', tontine_id=tontine.id)
    except TontineMember.DoesNotExist:
        messages.error(request, "Vous n'êtes pas membre de cette tontine.")
        return redirect('tontine_list')

    # Débiter wallet
    wallet.balance = wallet.balance - amt
    wallet.save()
    Transaction.objects.create(user=request.user, wallet=wallet, amount=amt, type='payment', note=f'Paiement contribution tontine {tontine.id}')

    # Créer contribution
    Contribution.objects.create(tontine=tontine, member=member, amount=amt)
    member.total_contributed = (member.total_contributed or 0) + amt
    member.save()
    tontine.total_pot = (tontine.total_pot or 0) + amt
    tontine.save()

    messages.success(request, 'Paiement effectué depuis votre porte-monnaie.')
    return redirect('tontine_detail', tontine_id=tontine.id)


@login_required
def wallet_overview(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    vaults = Vault.objects.filter(owner=request.user)
    transactions = request.user.transactions.order_by('-created_at')[:20]
    return render(request, 'tontines/wallet_overview.html', {
        'wallet': wallet,
        'vaults': vaults,
        'transactions': transactions,
    })


@login_required
def vaults_overview(request):
    vaults = Vault.objects.filter(owner=request.user).order_by('-id')
    return render(request, 'tontines/vaults_overview.html', {'vaults': vaults})


@login_required
@require_POST
@csrf_exempt
def vault_create_view(request):
    """Créer un coffre et (optionnel) déposer un montant depuis le wallet.
    Champs POST: name, locked_until (YYYY-MM-DD), amount (optionnel)
    """
    name = request.POST.get('name')
    locked_until = request.POST.get('locked_until')
    amount = request.POST.get('amount')
    from decimal import Decimal

    if not name:
        messages.error(request, 'Nom du coffre requis.')
        return redirect('tontine_list')

    vault = Vault.objects.create(owner=request.user, name=name)
    if locked_until:
        try:
            from datetime import datetime
            vault.locked_until = datetime.strptime(locked_until, '%Y-%m-%d').date()
            vault.save()
        except Exception:
            pass

    if amount:
        try:
            amt = Decimal(amount)
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            if wallet.balance >= amt:
                wallet.balance = wallet.balance - amt
                wallet.save()
                vault.balance = (vault.balance or 0) + amt
                vault.save()
                Transaction.objects.create(user=request.user, wallet=wallet, vault=vault, amount=amt, type='transfer', note='Dépot vers coffre')
            else:
                messages.warning(request, 'Solde insuffisant pour alimenter le coffre.')
        except Exception:
            messages.error(request, 'Montant invalide pour le dépôt.')

    messages.success(request, 'Coffre créé.')
    return redirect('vaults_overview')






# ============================================
# VUES API POUR LA GESTION DES MEMBRES
# ============================================

@login_required
@require_POST
@csrf_exempt
def tontine_change_member_role(request, tontine_id, member_id):
    """
    API pour changer le rôle d'un membre
    Utilisée via JavaScript dans manage.html
    """
    try:
        # Récupérer la tontine
        tontine = Tontine.objects.get(id=tontine_id)
        
        # Vérifier que l'utilisateur est le gestionnaire
        if request.user != tontine.manager:
            return JsonResponse({
                'success': False, 
                'error': 'Permission refusée. Seul le gestionnaire peut modifier les rôles.'
            })
        
        # Récupérer le membre
        member = TontineMember.objects.get(id=member_id, tontine=tontine)
        
        # Charger les données JSON
        data = json.loads(request.body)
        new_role = data.get('role')
        
        # Vérifier si le rôle est valide
        valid_roles = [choice[0] for choice in member.ROLE_CHOICES]
        if new_role not in valid_roles:
            return JsonResponse({
                'success': False, 
                'error': f'Rôle invalide. Rôles valides: {", ".join(valid_roles)}'
            })
        
        # Changer le rôle
        old_role = member.role
        member.role = new_role
        member.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Rôle changé de {old_role} à {new_role}',
            'new_role': new_role,
            'new_role_display': member.get_role_display()
        })
        
    except Tontine.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tontine non trouvée'})
    except TontineMember.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Membre non trouvé'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Données JSON invalides'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
@csrf_exempt
def tontine_change_member_status(request, tontine_id, member_id):
    """
    API pour changer le statut d'un membre
    Utilisée via JavaScript dans manage.html
    """
    try:
        # Récupérer la tontine
        tontine = Tontine.objects.get(id=tontine_id)
        
        # Vérifier que l'utilisateur est le gestionnaire
        if request.user != tontine.manager:
            return JsonResponse({
                'success': False, 
                'error': 'Permission refusée. Seul le gestionnaire peut modifier les statuts.'
            })
        
        # Récupérer le membre
        member = TontineMember.objects.get(id=member_id, tontine=tontine)
        
        # Charger les données JSON
        data = json.loads(request.body)
        new_status = data.get('status')
        
        # Vérifier si le statut est valide
        valid_statuses = ['pending', 'active', 'suspended']
        if new_status not in valid_statuses:
            return JsonResponse({
                'success': False, 
                'error': f'Statut invalide. Statuts valides: {", ".join(valid_statuses)}'
            })
        
        # Changer le statut
        old_status = member.status
        member.status = new_status
        member.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Statut changé de {old_status} à {new_status}',
            'new_status': new_status,
            'new_status_display': member.get_status_display()
        })
        
    except Tontine.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tontine non trouvée'})
    except TontineMember.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Membre non trouvé'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
@csrf_exempt
def tontine_remove_member(request, tontine_id, member_id):
    """
    Supprimer un membre de la tontine
    Version non-API (redirection normale)
    """
    try:
        # Récupérer la tontine
        tontine = Tontine.objects.get(id=tontine_id)

        # Vérifier que l'utilisateur est le gestionnaire
        if request.user != tontine.manager:
            # Si requête AJAX, renvoyer JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Permission refusée.'})
            messages.error(request, "Permission refusée.")
            return redirect('tontine_manage', tontine_id=tontine.id)

        # Récupérer le membre
        member = TontineMember.objects.get(id=member_id, tontine=tontine)
        member_name = member.user.get_full_name()

        # Ne pas permettre de supprimer le gestionnaire
        if member.user == tontine.manager:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': "Impossible de supprimer le gestionnaire."})
            messages.error(request, "Vous ne pouvez pas supprimer le gestionnaire de la tontine.")
        else:
            member.delete()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': f"{member_name} a été retiré de la tontine."})
            messages.success(request, f"{member_name} a été retiré de la tontine.")

        return redirect('tontine_manage', tontine_id=tontine.id)

    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, f"Erreur: {str(e)}")
        return redirect('tontine_manage', tontine_id=tontine_id)


# ============================================
# GESTION DES BÉNÉFICIAIRES (ALLOCATION)
# ============================================

def get_allocation_stats(tontine):
    """Retourne les statistiques d'allocation pour une tontine"""
    members = tontine.members.filter(status='active')
    current_cycle = BeneficiaryAllocation.objects.filter(tontine=tontine).aggregate(
        max_cycle=Count('id', distinct=True)
    ).get('max_cycle') or 0
    if current_cycle == 0:
        current_cycle = 1
    
    # Membres qui ont déjà reçu dans le cycle actuel
    received_members = BeneficiaryAllocation.objects.filter(
        tontine=tontine, 
        cycle_number=current_cycle
    ).values_list('member_id', flat=True)
    
    # Membres qui peuvent encore recevoir
    can_receive = members.exclude(id__in=received_members)
    already_received = members.filter(id__in=received_members)
    
    return {
        'current_cycle': current_cycle,
        'total_members': members.count(),
        'can_receive': list(can_receive),
        'already_received': list(already_received),
        'all_received': can_receive.count() == 0
    }


@login_required
def allocate_beneficiary_view(request, tontine_id):
    """Enregistrer un bénéficiaire pour la tontine"""
    tontine = get_object_or_404(Tontine, id=tontine_id)
    
    # Vérifier que l'utilisateur est gestionnaire
    if request.user != tontine.manager:
        messages.error(request, "Seul le gestionnaire peut allouer la tontine.")
        return redirect('tontine_detail', tontine_id=tontine.id)
    
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        try:
            member = TontineMember.objects.get(id=member_id, tontine=tontine, status='active')
        except TontineMember.DoesNotExist:
            messages.error(request, "Membre non trouvé ou inactif.")
            return redirect('tontine_manage', tontine_id=tontine.id)
        
        stats = get_allocation_stats(tontine)
        
        # Vérifier que le membre peut recevoir (n'a pas déjà reçu dans le cycle actuel)
        if member.id not in [m.id for m in stats['can_receive']]:
            messages.error(request, f"{member.user.get_full_name()} a déjà reçu la tontine ce cycle.")
            return redirect('tontine_manage', tontine_id=tontine.id)
        
        # Créer l'allocation
        try:
            allocation = BeneficiaryAllocation.objects.create(
                tontine=tontine,
                member=member,
                cycle_number=stats['current_cycle'],
                amount=tontine.total_pot
            )
            messages.success(request, f"{member.user.get_full_name()} a reçu {tontine.total_pot} FCFA de la tontine {tontine.name} (Cycle {stats['current_cycle']}).")
            return redirect('tontine_manage', tontine_id=tontine.id)
        except Exception as e:
            messages.error(request, f"Erreur lors de l'allocation: {str(e)}")
            return redirect('tontine_manage', tontine_id=tontine.id)
    
    # Afficher le formulaire
    stats = get_allocation_stats(tontine)
    context = {
        'tontine': tontine,
        'stats': stats,
        'can_receive_members': stats['can_receive'],
        'already_received': stats['already_received'],
    }
    return render(request, 'tontines/allocate_beneficiary.html', context)