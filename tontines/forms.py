from django import forms
from .models import Tontine
from django.utils import timezone
import re

class TontineCreationForm(forms.ModelForm):
    class Meta:
        model = Tontine
        fields = ('name', 'code', 'description', 'contribution_amount', 
                  'start_date', 'end_date', 'meeting_schedule', 'meeting_location', 'cycle_duration')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Tontine des Femmes de Dakar'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: TFD2024'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description détaillée de la tontine...'
            }),
            'contribution_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant en FCFA',
                'min': '100'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'meeting_schedule': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Tous les samedis à 10h'
            }),
            'meeting_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Maison communautaire, Dakar'
            }),
            'cycle_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Durée en jours',
                'min': '1',
                'value': '30'
            }),
        }
        labels = {
            'cycle_duration': 'Durée du cycle (jours)',
            'meeting_schedule': 'Calendrier des réunions',
            'meeting_location': 'Lieu des réunions',
        }
        help_texts = {
            'cycle_duration': 'Durée entre chaque contribution (ex: 30 jours pour mensuel)',
            'code': 'Code unique (lettres majuscules et chiffres uniquement)',
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not re.match(r'^[A-Z0-9]{3,10}$', code):
            raise forms.ValidationError(
                'Le code doit contenir uniquement des lettres majuscules et chiffres (3-10 caractères).'
            )
        
        # Vérifier si le code existe déjà
        if Tontine.objects.filter(code=code).exists():
            raise forms.ValidationError('Ce code est déjà utilisé. Veuillez en choisir un autre.')
        
        return code
    
    def clean_contribution_amount(self):
        amount = self.cleaned_data.get('contribution_amount')
        if amount < 100:
            raise forms.ValidationError('Le montant minimum de contribution est de 100 FCFA.')
        return amount
    
    def clean_cycle_duration(self):
        duration = self.cleaned_data.get('cycle_duration')
        if duration < 1:
            raise forms.ValidationError('La durée du cycle doit être d\'au moins 1 jour.')
        return duration
    
    def clean_end_date(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        
        if end_date and start_date:
            if end_date <= start_date:
                raise forms.ValidationError('La date de fin doit être après la date de début.')
        
        return end_date