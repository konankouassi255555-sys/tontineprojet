from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
import datetime

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPES, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    gender = forms.ChoiceField(
        choices=CustomUser.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        help_text="Format: JJ/MM/AAAA"
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'user_type', 'gender',
                  'first_name', 'last_name', 'date_of_birth', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter des classes Bootstrap à tous les champs
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Validation basique du numéro de téléphone
        if not phone_number.startswith('+'):
            # Ajouter l'indicatif sénégalais par défaut
            if phone_number.startswith('0'):
                phone_number = '+221' + phone_number[1:]
            elif phone_number.startswith('7'):
                phone_number = '+221' + phone_number
        return phone_number
    
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth:
            if date_of_birth > datetime.date.today():
                raise forms.ValidationError("La date de naissance ne peut pas être dans le futur.")
        return date_of_birth
    
# Ajoutez cette classe après CustomUserCreationForm
class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number', 
                  'user_type', 'gender', 'date_of_birth', 'profile_picture')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre user_type en lecture seule pour les utilisateurs non-admin
        if 'instance' in kwargs:
            user = kwargs['instance']
            if not user.is_staff:
                self.fields['user_type'].widget.attrs['readonly'] = True
                self.fields['user_type'].widget.attrs['class'] += ' bg-light'    