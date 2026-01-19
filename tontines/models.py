from django.db import models
from django.conf import settings

# Create your models here.

class Tontine(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Brouillon'),
        ('active', 'Active'),
        ('paused', 'En pause'),
        ('completed', 'Terminée'),
    )
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField()
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    contribution_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_pot = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    meeting_schedule = models.CharField(max_length=100, blank=True, verbose_name="Calendrier des réunions")
    meeting_location = models.CharField(max_length=200, blank=True, verbose_name="Lieu des réunions")
    cycle_duration = models.IntegerField(default=30, help_text="Durée du cycle en jours")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class TontineMember(models.Model):
    ROLE_CHOICES = (
        ('member', 'Membre'),
        ('treasurer', 'Trésorier'),
        ('secretary', 'Secrétaire'),
        ('vice_president', 'Vice-Président'),
        ('president', 'Président'),
    )
    tontine = models.ForeignKey(Tontine, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'En attente'),
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
    ], default='pending')
    total_contributed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['tontine', 'user']
    
    def __str__(self):
        return f"{self.user} dans {self.tontine}"


class Contribution(models.Model):
    tontine = models.ForeignKey(Tontine, on_delete=models.CASCADE, related_name='contributions')
    member = models.ForeignKey(TontineMember, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} par {self.member.user} pour {self.tontine} le {self.created_at}"


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"Wallet de {self.user} - {self.balance}"


class Vault(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vaults')
    name = models.CharField(max_length=200)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    locked_until = models.DateField(null=True, blank=True)

    def is_locked(self):
        if not self.locked_until:
            return False
        from django.utils import timezone
        return timezone.localdate() < self.locked_until

    def __str__(self):
        return f"Coffre {self.name} ({self.owner}) - {self.balance}"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Dépôt'),
        ('withdraw', 'Retrait'),
        ('payment', 'Paiement'),
        ('transfer', 'Transfert'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    vault = models.ForeignKey(Vault, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.get_type_display()} {self.amount} - {self.user} on {self.created_at}"


class BeneficiaryAllocation(models.Model):
    """
    Modèle pour tracker qui reçoit la tontine et gérer les cycles de distribution.
    Empêche quelqu'un de recevoir deux fois avant que tout le monde en ait reçu une.
    """
    tontine = models.ForeignKey(Tontine, on_delete=models.CASCADE, related_name='allocations')
    member = models.ForeignKey(TontineMember, on_delete=models.CASCADE, related_name='allocations')
    cycle_number = models.IntegerField(default=1, help_text="Numéro du cycle (1ère distribution, 2ème, etc.)")
    allocated_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Montant de la tontine reçu")
    
    class Meta:
        unique_together = ['tontine', 'member', 'cycle_number']
    
    def __str__(self):
        return f"{self.member.user} - Cycle {self.cycle_number} - {self.tontine}"
