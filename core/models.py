from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid



# ============================================
# MODÈLE UTILISATEUR PERSONNALISÉ
# ============================================


class CustomUser(AbstractUser):
    """Utilisateur personnalisé avec champs étendus"""
    
    # Identifiants
    email = models.EmailField(unique=True, verbose_name="Email")
    phone_number = PhoneNumberField(blank=True, null=True, unique=True, verbose_name="Numéro de téléphone")
    
    # Vérifications
    email_verified = models.BooleanField(default=False, verbose_name="Email vérifié")
    phone_verified = models.BooleanField(default=False, verbose_name="Téléphone vérifié")
    
    # 2FA
    two_factor_enabled = models.BooleanField(default=False, verbose_name="2FA activé")
    two_factor_secret = models.CharField(max_length=100, blank=True, null=True)
    
    # Profil
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Préférences
    newsletter_subscribed = models.BooleanField(default=False)
    notifications_enabled = models.BooleanField(default=True)
    
    # Sécurité
    last_ip = models.GenericIPAddressField(blank=True, null=True)
    last_login_location = models.CharField(max_length=200, blank=True, null=True)
    account_locked = models.BooleanField(default=False)
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
    
    def __str__(self):
        return self.email



# ============================================
# LOGEMENT (ENRICHI)
# ============================================


class Logement(models.Model):
    TYPE_CHOICES = [
        ('appartement', 'Appartement'),
        ('maison', 'Maison'),
        ('studio', 'Studio'),
        ('chambre', 'Chambre'),
        ('autre', 'Autre'),
    ]
    
    ETAGE_CHOICES = [
        ('rdc', 'Rez-de-chaussée'),
        ('etage', 'Étage'),
        ('dernier', 'Dernier étage'),
    ]
    
    STATUT_CHOICES = [
        ('disponible', 'Disponible'),
        ('reclame', 'Réclamé (en attente)'),
        ('verifie', 'Vérifié (propriétaire confirmé)'),
    ]
    
    # Informations de base
    titre = models.CharField(max_length=200)
    adresse = models.CharField(max_length=300)
    code_postal = models.CharField(max_length=5, default='31000')
    latitude = models.FloatField()
    longitude = models.FloatField()
    prix = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix (loyer mensuel)")
    surface = models.FloatField(verbose_name="Surface (m²)")
    description = models.TextField(blank=True, null=True)
    type_logement = models.CharField(max_length=20, choices=TYPE_CHOICES, default='appartement')
    chambres = models.IntegerField(default=1)
    etage = models.CharField(max_length=20, choices=ETAGE_CHOICES, default='etage')
    
    # DVF (Données Valeurs Foncières)
    date_mutation = models.DateField(blank=True, null=True, verbose_name="Date de vente")
    valeur_fonciere = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Prix de vente")
    
    # Cadastre
    id_parcelle = models.CharField(max_length=20, blank=True, null=True, verbose_name="Référence cadastrale")
    
    # Propriété et statut
    proprietaire = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='biens_possedes',
        verbose_name="Propriétaire vérifié"
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='disponible')
    
    # Notes et avis
    note_moyenne = models.FloatField(default=0, verbose_name="Note moyenne")
    nombre_avis = models.IntegerField(default=0, verbose_name="Nombre d'avis")
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Logement"
        verbose_name_plural = "Logements"
        indexes = [
            models.Index(fields=['code_postal', 'type_logement']),
            models.Index(fields=['prix', 'surface']),
            models.Index(fields=['note_moyenne']),
        ]
    
    def __str__(self):
        return self.titre
    
    def recalculer_note_moyenne(self):
        """Recalcule la note moyenne à partir des avis"""
        avis = self.avis.filter(verifie=True)
        if avis.exists():
            self.note_moyenne = avis.aggregate(models.Avg('note'))['note__avg']
            self.nombre_avis = avis.count()
        else:
            self.note_moyenne = 0
            self.nombre_avis = 0
        self.save()



# ============================================
# RÉCLAMATION PROPRIÉTAIRE
# ============================================


class ReclamationProprietaire(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
    ]
    
    logement = models.ForeignKey(Logement, on_delete=models.CASCADE, related_name='reclamations')
    utilisateur = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mes_reclamations')
    
    # Justificatifs
    justificatif = models.FileField(upload_to='justificatifs/proprietaires/', verbose_name="Justificatif (taxe foncière, titre de propriété)")
    message = models.TextField(verbose_name="Message explicatif")
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_reclamation = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(blank=True, null=True)
    
    # Traitement admin
    commentaire_admin = models.TextField(blank=True, verbose_name="Commentaire administrateur")
    traite_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reclamations_traitees')
    
    class Meta:
        ordering = ['-date_reclamation']
        verbose_name = "Réclamation propriétaire"
        verbose_name_plural = "Réclamations propriétaires"
        unique_together = ('logement', 'utilisateur', 'statut')
    
    def __str__(self):
        return f"Réclamation de {self.utilisateur.email} pour {self.logement.titre}"
    
    def accepter(self, admin_user):
        """Accepte la réclamation et attribue le logement"""
        self.statut = 'accepte'
        self.date_traitement = timezone.now()
        self.traite_par = admin_user
        self.save()
        
        # Mettre à jour le logement
        self.logement.proprietaire = self.utilisateur
        self.logement.statut = 'verifie'
        self.logement.save()
        
        # Refuser les autres réclamations en attente pour ce logement
        ReclamationProprietaire.objects.filter(
            logement=self.logement,
            statut='en_attente'
        ).exclude(id=self.id).update(statut='refuse')
    
    def refuser(self, admin_user, raison):
        """Refuse la réclamation"""
        self.statut = 'refuse'
        self.date_traitement = timezone.now()
        self.traite_par = admin_user
        self.commentaire_admin = raison
        self.save()



# ============================================
# AVIS LOGEMENT
# ============================================


class AvisLogement(models.Model):
    logement = models.ForeignKey(Logement, on_delete=models.CASCADE, related_name='avis')
    locataire = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mes_avis')
    
    # Avis
    note = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Note (1 à 5 étoiles)"
    )
    titre = models.CharField(max_length=200, verbose_name="Titre de l'avis")
    commentaire = models.TextField(verbose_name="Commentaire détaillé")
    
    # Critères détaillés (optionnel)
    note_proprete = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    note_equipements = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    note_localisation = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    note_bailleur = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Vérification
    verifie = models.BooleanField(default=False, verbose_name="Vérifié (vrai locataire)")
    justificatif = models.FileField(upload_to='justificatifs/locataires/', blank=True, null=True, verbose_name="Justificatif (quittance de loyer)")
    
    # Dates
    date_avis = models.DateTimeField(auto_now_add=True)
    date_verification = models.DateTimeField(blank=True, null=True)
    verifie_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='avis_verifies')
    
    class Meta:
        ordering = ['-date_avis']
        verbose_name = "Avis locataire"
        verbose_name_plural = "Avis locataires"
        unique_together = ('logement', 'locataire')
    
    def __str__(self):
        return f"Avis de {self.locataire.username} sur {self.logement.titre} ({self.note}/5)"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculer la note moyenne du logement
        self.logement.recalculer_note_moyenne()



# ============================================
# FAVORIS
# ============================================


class Favori(models.Model):
    """Logements favoris des utilisateurs"""
    utilisateur = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mes_favoris')
    logement = models.ForeignKey(Logement, on_delete=models.CASCADE, related_name='favoris_utilisateurs')
    date_ajout = models.DateTimeField(auto_now_add=True)
    note_personnelle = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('utilisateur', 'logement')
        ordering = ['-date_ajout']
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        indexes = [
            models.Index(fields=['utilisateur', 'date_ajout'], name='favori_user_idx'),
        ]
    
    def __str__(self):
        return f"{self.utilisateur.email} - {self.logement.titre}"



# ============================================
# PROFIL ÉTENDU (OPTIONNEL)
# ============================================


class Profil(models.Model):
    """Profil étendu optionnel"""
    utilisateur = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profil_etendu')
    date_creation = models.DateTimeField(auto_now_add=True)
    bio_longue = models.TextField(blank=True, null=True)
    site_web = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Profil étendu"
        verbose_name_plural = "Profils étendus"
    
    def __str__(self):
        return f"Profil de {self.utilisateur.email}"



# ============================================
# HISTORIQUE DE CONNEXION
# ============================================


class LoginHistory(models.Model):
    """Historique des connexions"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    suspicious = models.BooleanField(default=False)
    reason = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Historique de connexion"
        verbose_name_plural = "Historiques de connexion"
    
    def __str__(self):
        return f"{self.user.email} - {self.timestamp}"



# ============================================
# SESSIONS ACTIVES
# ============================================


class UserSession(models.Model):
    """Sessions actives"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='active_sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_name = models.CharField(max_length=200)
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_current = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-last_activity']
        verbose_name = "Session active"
        verbose_name_plural = "Sessions actives"
    
    def __str__(self):
        return f"{self.user.email} - {self.device_name}"



# ============================================
# TOKENS DE VÉRIFICATION
# ============================================


class EmailVerificationToken(models.Model):
    """Tokens de vérification email"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at
    
    class Meta:
        verbose_name = "Token de vérification"
        verbose_name_plural = "Tokens de vérification"
    
    def __str__(self):
        return f"Token {self.user.email}"



class PasswordResetToken(models.Model):
    """Tokens de réinitialisation mot de passe"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField()
    
    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at
    
    class Meta:
        verbose_name = "Token réinitialisation"
        verbose_name_plural = "Tokens réinitialisation"
    
    def __str__(self):
        return f"Reset {self.user.email}"
