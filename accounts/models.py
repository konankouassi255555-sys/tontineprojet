from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Types d'utilisateurs mis à jour
    USER_TYPES = (
        ('admin', 'Administrateur'),
        ('woman', 'Femme'),
        ('man', 'Homme'),
        ('child', 'Enfant'),
        ('rural_woman', 'Femme Rurale'),
        ('student', 'Étudiant'),
        ('community', 'Association Communautaire'),
        ('manager', 'Gestionnaire de Tontine'),
    )
    
    # Genres
    GENDER_CHOICES = (
        ('F', 'Féminin'),
        ('M', 'Masculin'),
        ('O', 'Autre'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='woman')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='F')
    phone_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Calculer l'âge si date de naissance est fournie
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            self.age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"