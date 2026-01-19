from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm,CustomUserChangeForm
from .models import CustomUser
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, f'Bienvenue {user.first_name} ! Votre compte a été créé avec succès.')
                
                # Redirection selon le type d'utilisateur
                if user.user_type == 'child':
                    messages.info(request, 'Bienvenue dans les tontines scolaires !')
                    return redirect('education:children_dashboard')
                elif user.user_type == 'rural_woman':
                    messages.info(request, 'Accédez à nos ressources spéciales pour les femmes rurales.')
                    return redirect('social:womens_dashboard')
                else:
                    return redirect('dashboard')
                    
            except Exception as e:
                messages.error(request, f'Une erreur est survenue: {str(e)}')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'user_types_with_desc': {
            'woman': 'Femme - Pour les tontines générales',
            'man': 'Homme - Pour les tontines générales',
            'child': 'Enfant - Pour les tontines scolaires',
            'rural_woman': 'Femme Rurale - Accès aux ressources spécifiques',
            'student': 'Étudiant - Tarifs préférentiels',
            'community': 'Association - Gestion de groupe',
            'manager': 'Gestionnaire - Administration de tontines',
        }
    }
    return render(request, 'accounts/register.html', context)

@login_required
def profile_view(request):
    # Calculer l'âge si non défini
    if request.user.date_of_birth and not request.user.age:
        from datetime import date
        today = date.today()
        request.user.age = today.year - request.user.date_of_birth.year - (
            (today.month, today.day) < (request.user.date_of_birth.month, request.user.date_of_birth.day)
        )
        request.user.save()
    
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def profile_edit_view(request):
    user = request.user
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = CustomUserChangeForm(instance=user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form, 'user': user})

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('password_change_done')
    
    def form_valid(self, form):
        messages.success(self.request, 'Votre mot de passe a été changé avec succès!')
        return super().form_valid(form)

class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'accounts/change_password_done.html'