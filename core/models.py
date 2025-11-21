from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
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
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True, verbose_name="Image de couverture")
    profile_banner_image = models.ImageField(upload_to='banners/', blank=True, null=True, verbose_name="Bannière de profil (image)")
    profile_banner_video = models.FileField(upload_to='banners/videos/', blank=True, null=True, verbose_name="Bannière de profil (vidéo)")
    bio = models.TextField(max_length=500, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Rôle
    is_proprietaire = models.BooleanField(default=False, verbose_name="Est propriétaire")
    is_locataire = models.BooleanField(default=True, verbose_name="Est locataire")
    
    # Vérifications supplémentaires
    identity_verified = models.BooleanField(default=False, verbose_name="Identité vérifiée")
    proprietaire_verified = models.BooleanField(default=False, verbose_name="Propriétaire vérifié")
    
    # Localisation
    ville = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ville")
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name="Région")
    adresse_complete = models.TextField(blank=True, null=True, verbose_name="Adresse complète")
    
    # Réseaux sociaux
    linkedin_url = models.URLField(blank=True, null=True, verbose_name="LinkedIn")
    facebook_url = models.URLField(blank=True, null=True, verbose_name="Facebook")
    instagram_url = models.URLField(blank=True, null=True, verbose_name="Instagram")
    
    # Informations professionnelles
    profession = models.CharField(max_length=200, blank=True, null=True, verbose_name="Profession")
    employeur = models.CharField(max_length=200, blank=True, null=True, verbose_name="Employeur")
    situation_professionnelle = models.CharField(
        max_length=50,
        choices=[
            ('cdi', 'CDI'),
            ('cdd', 'CDD'),
            ('freelance', 'Freelance'),
            ('etudiant', 'Étudiant'),
            ('retraite', 'Retraité'),
            ('autre', 'Autre'),
        ],
        blank=True,
        null=True,
        verbose_name="Situation professionnelle"
    )
    
    # Propriétaire professionnel
    is_professionnel = models.BooleanField(default=False, verbose_name="Propriétaire professionnel")
    siret = models.CharField(max_length=20, blank=True, null=True, verbose_name="SIRET")
    siren = models.CharField(max_length=20, blank=True, null=True, verbose_name="SIREN")
    site_web = models.URLField(blank=True, null=True, verbose_name="Site web")
    email_professionnel = models.EmailField(blank=True, null=True, verbose_name="Email professionnel")
    
    # Disponibilité
    heures_disponibilite = models.CharField(max_length=200, blank=True, null=True, verbose_name="Heures de disponibilité")
    
    # Préférences
    newsletter_subscribed = models.BooleanField(default=False)
    notifications_enabled = models.BooleanField(default=True)
    
    # Visibilité/Confidentialité
    profil_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public - Visible par tous'),
            ('connections', 'Connexions uniquement - Visible par mes connexions'),
            ('private', 'Privé - Invisible, uniquement recherche par nom'),
        ],
        default='public',
        verbose_name="Visibilité du profil"
    )
    profil_public = models.BooleanField(default=True, verbose_name="Profil public (déprécié, utiliser profil_visibility)")  # À garder pour compatibilité
    afficher_statut_online = models.BooleanField(default=True, verbose_name="Afficher statut en ligne")
    afficher_derniere_visite = models.BooleanField(default=False, verbose_name="Afficher dernière visite")
    afficher_logements_profil = models.BooleanField(default=True, verbose_name="Afficher mes logements sur mon profil")
    afficher_activite_recente = models.BooleanField(default=True, verbose_name="Afficher mon activité récente")
    connect_disabled = models.BooleanField(default=False, verbose_name="Profil Connect désactivé")
    
    # Contrôle de confidentialité micro-niveau
    cacher_activite_reseau = models.BooleanField(default=False, verbose_name="Cacher mon activité réseau (connexions, follows)")
    cacher_logements_mais_garder_profil = models.BooleanField(default=False, verbose_name="Cacher mes logements mais garder le profil visible")
    cacher_uniquement_timeline = models.BooleanField(default=False, verbose_name="Cacher uniquement la timeline d'activité")
    cacher_statistiques = models.BooleanField(default=False, verbose_name="Cacher mes statistiques (vues, likes, etc.)")
    cacher_badges = models.BooleanField(default=False, verbose_name="Cacher mes badges et récompenses")
    cacher_recommandations = models.BooleanField(default=False, verbose_name="Cacher les recommandations reçues")
    cacher_historique_publications = models.BooleanField(default=False, verbose_name="Cacher mon historique de publications")
    cacher_groupes = models.BooleanField(default=False, verbose_name="Cacher les groupes auxquels je participe")
    cacher_commentaires = models.BooleanField(default=False, verbose_name="Cacher mes commentaires sur les posts")
    cacher_reactions = models.BooleanField(default=False, verbose_name="Cacher mes réactions (likes, etc.)")
    
    # Paramètres messagerie
    who_can_message = models.CharField(
        max_length=50,
        choices=[
            ('everyone', 'Tout le monde'),
            ('connections', 'Mes connexions uniquement'),
            ('verified', 'Utilisateurs vérifiés uniquement'),
        ],
        default='everyone',
        verbose_name="Qui peut m'envoyer un message"
    )
    message_email_notifications = models.BooleanField(default=True, verbose_name="Notifications email pour nouveaux messages")
    message_push_notifications = models.BooleanField(default=True, verbose_name="Notifications push pour nouveaux messages")
    
    # Paramètres notifications (JSON pour stocker les préférences par type)
    notification_settings = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Paramètres de notifications",
        help_text="Préférences de notifications par type (email, push, in_app)"
    )
    notification_email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immédiate'),
            ('daily', 'Résumé quotidien'),
            ('weekly', 'Résumé hebdomadaire'),
        ],
        default='immediate',
        verbose_name="Fréquence des emails de notification"
    )
    
    # Statut en ligne (calculé dynamiquement)
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Dernière activité")
    
    # Visibilité et statut de recherche
    recherche_logement_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Recherche active'),
            ('passive', 'Recherche passive'),
            ('none', 'Ne recherche pas'),
        ],
        default='none',
        verbose_name="Statut de recherche de logement"
    )
    recherche_locataire_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Recherche active'),
            ('passive', 'Recherche passive'),
            ('none', 'Ne recherche pas'),
        ],
        default='none',
        verbose_name="Statut de recherche de locataire"
    )
    disponibilite_rdv = models.CharField(
        max_length=20,
        choices=[
            ('disponible', 'Disponible'),
            ('occupe', 'Occupé'),
            ('bientot_disponible', 'Bientôt disponible'),
        ],
        default='disponible',
        verbose_name="Disponibilité pour rendez-vous"
    )
    prochain_creneau_disponible = models.DateTimeField(blank=True, null=True, verbose_name="Prochain créneau disponible")
    
    # Sécurité
    last_ip = models.GenericIPAddressField(blank=True, null=True)
    last_login_location = models.CharField(max_length=200, blank=True, null=True)
    account_locked = models.BooleanField(default=False)
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(blank=True, null=True)
    
    # Modération Admin (Phase 11)
    is_suspended = models.BooleanField(default=False, verbose_name="Compte suspendu")
    suspended_until = models.DateTimeField(blank=True, null=True, verbose_name="Suspendu jusqu'au")
    suspension_reason = models.TextField(blank=True, null=True, verbose_name="Raison de la suspension")
    is_banned = models.BooleanField(default=False, verbose_name="Compte banni")
    ban_reason = models.TextField(blank=True, null=True, verbose_name="Raison du bannissement")
    banned_at = models.DateTimeField(blank=True, null=True, verbose_name="Date du bannissement")
    banned_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='banned_users', verbose_name="Banni par")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
    
    def __str__(self):
        return self.email
    
    def get_profil_visibility_display_value(self):
        """Retourne la valeur booléenne pour compatibilité avec profil_public"""
        if not hasattr(self, 'profil_visibility') or not self.profil_visibility:
            return self.profil_public
        return self.profil_visibility == 'public'
    
    def can_view_profile(self, viewer):
        """Vérifie si un utilisateur peut voir ce profil"""
        if not viewer or not viewer.is_authenticated:
            return self.profil_visibility == 'public'
        
        if viewer == self:
            return True
        
        if self.connect_disabled:
            return False
        
        if self.profil_visibility == 'public':
            return True
        elif self.profil_visibility == 'connections':
            # Vérifier si connecté (utiliser la relation depuis la classe)
            # Note: UserConnection est défini plus bas dans le fichier
            # Pour éviter les imports circulaires, on utilise directement le nom du modèle
            try:
                # Utiliser le nom du modèle directement
                connection_model = self._meta.apps.get_model('core', 'UserConnection')
                return connection_model.objects.filter(
                    Q(user_from=viewer, user_to=self) | Q(user_from=self, user_to=viewer),
                    status='accepted'
                ).exists()
            except:
                # Si le modèle n'est pas encore chargé, retourner False
                return False
        else:  # private
            return False



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
# GESTION BAIL - CONTRAT DE LOCATION
# ============================================

class Bail(models.Model):
    """Contrat de location (bail)"""
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('resiliation_en_cours', 'En cours de résiliation'),
        ('resilie', 'Résilié'),
        ('termine', 'Terminé'),
    ]
    
    logement = models.ForeignKey(Logement, on_delete=models.CASCADE, related_name='baux', verbose_name="Logement")
    locataire = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='baux_locataire', verbose_name="Locataire")
    proprietaire = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='baux_proprietaire', verbose_name="Propriétaire")
    
    # Dates
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(blank=True, null=True, verbose_name="Date de fin")
    
    # Montants
    loyer_mensuel = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Loyer mensuel")
    charges_mensuelles = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Charges mensuelles")
    depot_garantie = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Dépôt de garantie")
    
    # Informations contrat
    duree_mois = models.IntegerField(default=12, verbose_name="Durée (en mois)")
    jour_paiement = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(31)], verbose_name="Jour de paiement mensuel")
    
    # Documents
    contrat_signe = models.FileField(upload_to='baux/contrats/%Y/%m/', blank=True, null=True, verbose_name="Contrat signé (PDF)")
    etat_lieux_entree = models.FileField(upload_to='baux/etat_lieux/%Y/%m/', blank=True, null=True, verbose_name="État des lieux d'entrée (PDF)")
    etat_lieux_sortie = models.FileField(upload_to='baux/etat_lieux/%Y/%m/', blank=True, null=True, verbose_name="État des lieux de sortie (PDF)")
    
    # Assurances
    assurance_habitation = models.FileField(upload_to='baux/assurances/%Y/%m/', blank=True, null=True, verbose_name="Assurance habitation")
    assurance_date_echeance = models.DateField(blank=True, null=True, verbose_name="Date d'échéance assurance")
    
    # Statut
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='actif', verbose_name="Statut")
    
    # Clauses importantes (résumé)
    clauses_importantes = models.TextField(blank=True, null=True, verbose_name="Clauses importantes")
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_debut']
        verbose_name = "Bail"
        verbose_name_plural = "Baux"
        indexes = [
            models.Index(fields=['locataire', 'statut']),
            models.Index(fields=['proprietaire', 'statut']),
            models.Index(fields=['date_debut', 'date_fin']),
        ]
    
    def __str__(self):
        return f"Bail {self.logement.titre} - {self.locataire.username}"
    
    def is_actif(self):
        """Vérifie si le bail est actif"""
        return self.statut == 'actif' and (not self.date_fin or self.date_fin > timezone.now().date())
    
    def get_prochain_paiement(self):
        """Retourne la date du prochain paiement"""
        from datetime import date
        today = timezone.now().date()
        if today.day < self.jour_paiement:
            # Le paiement est ce mois-ci
            return date(today.year, today.month, self.jour_paiement)
        else:
            # Le paiement est le mois prochain
            if today.month == 12:
                return date(today.year + 1, 1, self.jour_paiement)
            else:
                return date(today.year, today.month + 1, self.jour_paiement)
    
    def get_montant_total_mensuel(self):
        """Retourne le montant total mensuel (loyer + charges)"""
        return self.loyer_mensuel + self.charges_mensuelles


class PaiementLoyer(models.Model):
    """Paiement de loyer"""
    STATUT_CHOICES = [
        ('paye', 'Payé'),
        ('en_retard', 'En retard'),
        ('en_attente', 'En attente'),
    ]
    
    bail = models.ForeignKey(Bail, on_delete=models.CASCADE, related_name='paiements', verbose_name="Bail")
    locataire = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='paiements_loyer', verbose_name="Locataire")
    
    # Dates
    date_echeance = models.DateField(verbose_name="Date d'échéance")
    date_paiement = models.DateField(blank=True, null=True, verbose_name="Date de paiement")
    
    # Montants
    montant_loyer = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant loyer")
    montant_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant charges")
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant total")
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    
    # Document
    quittance = models.FileField(upload_to='baux/quittances/%Y/%m/', blank=True, null=True, verbose_name="Quittance (PDF)")
    
    # Informations de paiement
    mode_paiement = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mode de paiement")
    reference_paiement = models.CharField(max_length=200, blank=True, null=True, verbose_name="Référence paiement")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_echeance']
        verbose_name = "Paiement de loyer"
        verbose_name_plural = "Paiements de loyer"
        indexes = [
            models.Index(fields=['bail', '-date_echeance']),
            models.Index(fields=['locataire', 'statut']),
        ]
    
    def __str__(self):
        return f"Paiement {self.bail.logement.titre} - {self.date_echeance}"
    
    def mark_as_paid(self, date_paiement=None):
        """Marque le paiement comme payé"""
        self.statut = 'paye'
        self.date_paiement = date_paiement or timezone.now().date()
        self.save()
    
    def is_en_retard(self):
        """Vérifie si le paiement est en retard"""
        if self.statut == 'paye':
            return False
        return timezone.now().date() > self.date_echeance


class DemandeEntretien(models.Model):
    """Demande d'entretien/travaux du locataire"""
    TYPE_PROBLEME_CHOICES = [
        ('plomberie', 'Plomberie'),
        ('electricite', 'Électricité'),
        ('chauffage', 'Chauffage'),
        ('climatisation', 'Climatisation'),
        ('peinture', 'Peinture'),
        ('vitrerie', 'Vitrerie'),
        ('porte_fenetre', 'Porte/Fenêtre'),
        ('isolation', 'Isolation'),
        ('sanitaire', 'Sanitaire'),
        ('autre', 'Autre'),
    ]
    
    URGENCE_CHOICES = [
        ('urgent', 'Urgent'),
        ('normal', 'Normal'),
        ('faible', 'Faible'),
    ]
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
        ('refuse', 'Refusé'),
    ]
    
    bail = models.ForeignKey(Bail, on_delete=models.CASCADE, related_name='demandes_entretien', verbose_name="Bail")
    locataire = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='demandes_entretien', verbose_name="Locataire")
    proprietaire = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='demandes_entretien_recues', verbose_name="Propriétaire")
    
    # Informations demande
    type_probleme = models.CharField(max_length=30, choices=TYPE_PROBLEME_CHOICES, verbose_name="Type de problème")
    titre = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    urgence = models.CharField(max_length=20, choices=URGENCE_CHOICES, default='normal', verbose_name="Urgence")
    
    # Images
    photos = models.ManyToManyField('DemandeEntretienPhoto', blank=True, related_name='demandes', verbose_name="Photos")
    
    # Statut et réponse
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    reponse_proprietaire = models.TextField(blank=True, null=True, verbose_name="Réponse du propriétaire")
    date_reponse = models.DateTimeField(blank=True, null=True, verbose_name="Date de réponse")
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Demande d'entretien"
        verbose_name_plural = "Demandes d'entretien"
        indexes = [
            models.Index(fields=['bail', '-created_at']),
            models.Index(fields=['locataire', 'statut']),
            models.Index(fields=['proprietaire', 'statut']),
        ]
    
    def __str__(self):
        return f"Demande {self.type_probleme} - {self.bail.logement.titre}"


class DemandeEntretienPhoto(models.Model):
    """Photos pour une demande d'entretien"""
    demande = models.ForeignKey(DemandeEntretien, on_delete=models.CASCADE, related_name='photo_set', verbose_name="Demande")
    photo = models.ImageField(upload_to='baux/entretien/%Y/%m/', verbose_name="Photo")
    caption = models.CharField(max_length=200, blank=True, null=True, verbose_name="Légende")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Photo demande d'entretien"
        verbose_name_plural = "Photos demandes d'entretien"
    
    def __str__(self):
        return f"Photo {self.demande.titre}"


class DocumentBail(models.Model):
    """Document lié au bail"""
    TYPE_DOCUMENT_CHOICES = [
        ('contrat', 'Contrat/Bail signé'),
        ('etat_lieux_entree', 'État des lieux d\'entrée'),
        ('etat_lieux_sortie', 'État des lieux de sortie'),
        ('quittance', 'Quittance de loyer'),
        ('assurance', 'Assurance habitation'),
        ('facture_charges', 'Facture de charges'),
        ('autre', 'Autre'),
    ]
    
    bail = models.ForeignKey(Bail, on_delete=models.CASCADE, related_name='documents', verbose_name="Bail")
    type_document = models.CharField(max_length=30, choices=TYPE_DOCUMENT_CHOICES, verbose_name="Type de document")
    titre = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Fichier
    document = models.FileField(upload_to='baux/documents/%Y/%m/', verbose_name="Document")
    
    # Qui a uploadé
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='documents_bail_uploaded', verbose_name="Uploadé par")
    
    # Dates
    date_document = models.DateField(blank=True, null=True, verbose_name="Date du document")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Document bail"
        verbose_name_plural = "Documents bail"
        indexes = [
            models.Index(fields=['bail', 'type_document']),
            models.Index(fields=['uploaded_by', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_type_document_display()} - {self.bail.logement.titre}"


class Resiliation(models.Model):
    """Résiliation d'un bail"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('terminee', 'Terminée'),
    ]
    
    bail = models.OneToOneField(Bail, on_delete=models.CASCADE, related_name='resiliation', verbose_name="Bail")
    locataire = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='resiliations_locataire', verbose_name="Locataire")
    proprietaire = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='resiliations_proprietaire', verbose_name="Propriétaire")
    
    # Informations résiliation
    date_depart_souhaitee = models.DateField(verbose_name="Date de départ souhaitée")
    raison = models.TextField(blank=True, null=True, verbose_name="Raison (optionnelle)")
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    
    # Réponse propriétaire
    reponse_proprietaire = models.TextField(blank=True, null=True, verbose_name="Réponse du propriétaire")
    date_reponse = models.DateTimeField(blank=True, null=True, verbose_name="Date de réponse")
    date_fin_effective = models.DateField(blank=True, null=True, verbose_name="Date de fin effective")
    
    # Checklist sortie
    etat_lieux_sortie_fait = models.BooleanField(default=False, verbose_name="État des lieux de sortie effectué")
    cles_restituées = models.BooleanField(default=False, verbose_name="Clés restituées")
    depot_garantie_rendu = models.BooleanField(default=False, verbose_name="Dépôt de garantie rendu")
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Résiliation"
        verbose_name_plural = "Résiliations"
        indexes = [
            models.Index(fields=['locataire', 'statut']),
            models.Index(fields=['proprietaire', 'statut']),
        ]
    
    def accept(self, date_fin_effective=None):
        """Accepte la résiliation"""
        self.statut = 'acceptee'
        self.date_fin_effective = date_fin_effective or self.date_depart_souhaitee
        self.date_reponse = timezone.now()
        self.save()
        

# ============================================
# GESTION BAIL AVANCÉE - NOUVELLES FONCTIONNALITÉS
# ============================================

class SignatureElectronique(models.Model):
    """Signature électronique pour documents de bail"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente de signature'),
        ('signe_locataire', 'Signé par le locataire'),
        ('signe_proprietaire', 'Signé par le propriétaire'),
        ('signe_complet', 'Signé par les deux parties'),
        ('annule', 'Annulé'),
    ]
    
    bail = models.ForeignKey(Bail, on_delete=models.CASCADE, related_name='signatures', verbose_name="Bail")
    document = models.ForeignKey(DocumentBail, on_delete=models.CASCADE, related_name='signatures', verbose_name="Document")
    
    # Signatures
    signature_locataire = models.TextField(blank=True, null=True, verbose_name="Signature locataire (base64)")
    signature_proprietaire = models.TextField(blank=True, null=True, verbose_name="Signature propriétaire (base64)")
    
    # Dates de signature
    date_signature_locataire = models.DateTimeField(blank=True, null=True, verbose_name="Date signature locataire")
    date_signature_proprietaire = models.DateTimeField(blank=True, null=True, verbose_name="Date signature propriétaire")
    
    # IP et device info pour traçabilité
    ip_locataire = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP locataire")
    ip_proprietaire = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP propriétaire")
    device_info_locataire = models.TextField(blank=True, null=True, verbose_name="Info device locataire")
    device_info_proprietaire = models.TextField(blank=True, null=True, verbose_name="Info device propriétaire")
    
    # Statut
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    
    # Document signé final (PDF avec signatures)
    document_signe_final = models.FileField(upload_to='baux/signatures/%Y/%m/', blank=True, null=True, verbose_name="Document signé final")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Signature électronique"
        verbose_name_plural = "Signatures électroniques"
        indexes = [
            models.Index(fields=['bail', 'statut']),
            models.Index(fields=['document', 'statut']),
        ]
    
    def __str__(self):
        return f"Signature {self.document.titre} - {self.get_statut_display()}"


class FichierPartage(models.Model):
    """Fichier partagé entre propriétaire et locataire avec logs d'accès"""
    bail = models.ForeignKey(Bail, on_delete=models.CASCADE, related_name='fichiers_partages', verbose_name="Bail")
    
    # Fichier
    fichier = models.FileField(upload_to='baux/fichiers_partages/%Y/%m/', verbose_name="Fichier")
    nom = models.CharField(max_length=200, verbose_name="Nom du fichier")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Upload
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='fichiers_partages_uploaded', verbose_name="Uploadé par")
    
    # Visibilité
    visible_locataire = models.BooleanField(default=True, verbose_name="Visible pour le locataire")
    visible_proprietaire = models.BooleanField(default=True, verbose_name="Visible pour le propriétaire")
    
    # Taille et type
    taille_fichier = models.BigIntegerField(blank=True, null=True, verbose_name="Taille (octets)")
    type_fichier = models.CharField(max_length=50, blank=True, null=True, verbose_name="Type MIME")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Fichier partagé"
        verbose_name_plural = "Fichiers partagés"
        indexes = [
            models.Index(fields=['bail', '-created_at']),
            models.Index(fields=['uploaded_by']),
        ]
    
    def __str__(self):
        return f"{self.nom} - {self.bail.logement.titre}"


class LogAccesFichier(models.Model):
    """Log d'accès à un fichier partagé"""
    fichier = models.ForeignKey(FichierPartage, on_delete=models.CASCADE, related_name='logs_acces', verbose_name="Fichier")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='logs_acces_fichiers', verbose_name="Utilisateur")
    
    # Type d'action
    ACTION_CHOICES = [
        ('view', 'Consultation'),
        ('download', 'Téléchargement'),
        ('upload', 'Upload'),
        ('delete', 'Suppression'),
    ]
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Action")
    
    # Informations de traçabilité
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Log d'accès fichier"
        verbose_name_plural = "Logs d'accès fichiers"
        indexes = [
            models.Index(fields=['fichier', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.fichier.nom}"


class ChecklistEtatLieux(models.Model):
    """Checklist numérique pour état des lieux"""
    TYPE_CHOICES = [
        ('entree', 'État des lieux d\'entrée'),
        ('sortie', 'État des lieux de sortie'),
    ]
    
    bail = models.ForeignKey(Bail, on_delete=models.CASCADE, related_name='checklists_etat_lieux', verbose_name="Bail")
    type_checklist = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type")
    
    # Validation
    valide_par_locataire = models.BooleanField(default=False, verbose_name="Validé par le locataire")
    valide_par_proprietaire = models.BooleanField(default=False, verbose_name="Validé par le propriétaire")
    date_validation_locataire = models.DateTimeField(blank=True, null=True, verbose_name="Date validation locataire")
    date_validation_proprietaire = models.DateTimeField(blank=True, null=True, verbose_name="Date validation propriétaire")
    
    # Photos
    photos = models.ManyToManyField('ImageLogement', blank=True, related_name='checklists_etat_lieux', verbose_name="Photos")
    
    # Commentaires
    commentaires_locataire = models.TextField(blank=True, null=True, verbose_name="Commentaires locataire")
    commentaires_proprietaire = models.TextField(blank=True, null=True, verbose_name="Commentaires propriétaire")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Checklist état des lieux"
        verbose_name_plural = "Checklists état des lieux"
        indexes = [
            models.Index(fields=['bail', 'type_checklist']),
        ]
    
    def __str__(self):
        return f"{self.get_type_checklist_display()} - {self.bail.logement.titre}"


class ItemChecklist(models.Model):
    """Item d'une checklist état des lieux"""
    checklist = models.ForeignKey(ChecklistEtatLieux, on_delete=models.CASCADE, related_name='items', verbose_name="Checklist")
    
    # Description
    piece = models.CharField(max_length=100, verbose_name="Pièce")
    element = models.CharField(max_length=200, verbose_name="Élément")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # État
    ETAT_CHOICES = [
        ('bon', 'Bon état'),
        ('moyen', 'État moyen'),
        ('mauvais', 'Mauvais état'),
        ('a_reparer', 'À réparer'),
    ]
    etat_entree = models.CharField(max_length=20, choices=ETAT_CHOICES, blank=True, null=True, verbose_name="État entrée")
    etat_sortie = models.CharField(max_length=20, choices=ETAT_CHOICES, blank=True, null=True, verbose_name="État sortie")
    
    # Photos
    photo_entree = models.ImageField(upload_to='baux/checklist/entree/%Y/%m/', blank=True, null=True, verbose_name="Photo entrée")
    photo_sortie = models.ImageField(upload_to='baux/checklist/sortie/%Y/%m/', blank=True, null=True, verbose_name="Photo sortie")
    
    # Notes
    notes_locataire = models.TextField(blank=True, null=True, verbose_name="Notes locataire")
    notes_proprietaire = models.TextField(blank=True, null=True, verbose_name="Notes propriétaire")
    
    # Validation
    valide_par_locataire = models.BooleanField(default=False, verbose_name="Validé par locataire")
    valide_par_proprietaire = models.BooleanField(default=False, verbose_name="Validé par propriétaire")
    
    order = models.IntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'piece', 'element']
        verbose_name = "Item checklist"
        verbose_name_plural = "Items checklist"
    
    def __str__(self):
        return f"{self.piece} - {self.element}"


class TicketIntervention(models.Model):
    """Ticket/intervention avec suivi d'état et auto-escalade"""
    PRIORITE_CHOICES = [
        ('critique', 'Critique'),
        ('haute', 'Haute'),
        ('normale', 'Normale'),
        ('basse', 'Basse'),
    ]
    
    STATUT_CHOICES = [
        ('nouveau', 'Nouveau'),
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
        ('ferme', 'Fermé'),
        ('escalade', 'Escaladé à l\'admin'),
    ]
    
    bail = models.ForeignKey(Bail, on_delete=models.CASCADE, related_name='tickets', verbose_name="Bail")
    demande_entretien = models.ForeignKey(DemandeEntretien, on_delete=models.SET_NULL, blank=True, null=True, related_name='tickets', verbose_name="Demande d'entretien liée")
    
    # Création
    cree_par = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tickets_crees', verbose_name="Créé par")
    assigne_a = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='tickets_assignes', verbose_name="Assigné à")
    
    # Informations
    titre = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='normale', verbose_name="Priorité")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='nouveau', verbose_name="Statut")
    
    # Dates importantes
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_derniere_activite = models.DateTimeField(auto_now=True, verbose_name="Date dernière activité")
    date_resolution = models.DateTimeField(blank=True, null=True, verbose_name="Date de résolution")
    date_escalade = models.DateTimeField(blank=True, null=True, verbose_name="Date d'escalade")
    
    # Auto-escalade
    jours_sans_activite = models.IntegerField(default=0, verbose_name="Jours sans activité")
    escalade_auto = models.BooleanField(default=False, verbose_name="Escaladé automatiquement")
    
    # Résolution
    resolution = models.TextField(blank=True, null=True, verbose_name="Résolution")
    resolu_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='tickets_resolus', verbose_name="Résolu par")
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Ticket/Intervention"
        verbose_name_plural = "Tickets/Interventions"
        indexes = [
            models.Index(fields=['bail', 'statut']),
            models.Index(fields=['cree_par', 'statut']),
            models.Index(fields=['assigne_a', 'statut']),
            models.Index(fields=['priorite', 'statut']),
        ]
    
    def __str__(self):
        return f"{self.titre} - {self.bail.logement.titre}"


class CommentaireTicket(models.Model):
    """Commentaire sur un ticket"""
    ticket = models.ForeignKey(TicketIntervention, on_delete=models.CASCADE, related_name='commentaires', verbose_name="Ticket")
    auteur = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='commentaires_tickets', verbose_name="Auteur")
    contenu = models.TextField(verbose_name="Contenu")
    
    # Pièces jointes
    fichier = models.FileField(upload_to='baux/tickets/commentaires/%Y/%m/', blank=True, null=True, verbose_name="Fichier joint")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Commentaire ticket"
        verbose_name_plural = "Commentaires tickets"
    
    def __str__(self):
        return f"Commentaire {self.ticket.titre} - {self.auteur.username}"


class RappelAutomatise(models.Model):
    """Rappel automatisé multi-canal"""
    TYPE_RAPPEL_CHOICES = [
        ('paiement', 'Paiement de loyer'),
        ('echeance', 'Échéance contrat'),
        ('entretien', 'Entretien/Maintenance'),
        ('document', 'Document à signer'),
        ('visite', 'Visite prévue'),
        ('autre', 'Autre'),
    ]
    
    CANAL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Notification push'),
        ('in_app', 'Notification in-app'),
    ]
    
    bail = models.ForeignKey(Bail, on_delete=models.CASCADE, related_name='rappels', verbose_name="Bail")
    
    # Type et destinataire
    type_rappel = models.CharField(max_length=20, choices=TYPE_RAPPEL_CHOICES, verbose_name="Type de rappel")
    destinataire = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rappels_recus', verbose_name="Destinataire")
    
    # Contenu
    titre = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    
    # Canaux
    envoyer_email = models.BooleanField(default=True, verbose_name="Envoyer par email")
    envoyer_sms = models.BooleanField(default=False, verbose_name="Envoyer par SMS")
    envoyer_push = models.BooleanField(default=True, verbose_name="Envoyer notification push")
    envoyer_in_app = models.BooleanField(default=True, verbose_name="Envoyer notification in-app")
    
    # Planning
    date_rappel = models.DateTimeField(verbose_name="Date du rappel")
    date_echeance = models.DateField(blank=True, null=True, verbose_name="Date d'échéance concernée")
    
    # Statut
    envoye = models.BooleanField(default=False, verbose_name="Envoyé")
    date_envoi = models.DateTimeField(blank=True, null=True, verbose_name="Date d'envoi")
    
    # Répétition
    repeter = models.BooleanField(default=False, verbose_name="Répéter")
    intervalle_jours = models.IntegerField(default=0, verbose_name="Intervalle (jours)")
    nombre_repetitions = models.IntegerField(default=0, verbose_name="Nombre de répétitions")
    repetitions_effectuees = models.IntegerField(default=0, verbose_name="Répétitions effectuées")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date_rappel']
        verbose_name = "Rappel automatisé"
        verbose_name_plural = "Rappels automatisés"
        indexes = [
            models.Index(fields=['bail', 'date_rappel']),
            models.Index(fields=['destinataire', 'envoye']),
            models.Index(fields=['type_rappel', 'date_rappel']),
        ]
    
    def __str__(self):
        return f"{self.titre} - {self.destinataire.username}"


# ============================================
# FIN GESTION BAIL AVANCÉE
# ============================================
    
    def reject(self, raison):
        """Refuse la résiliation"""
        self.statut = 'refusee'
        self.reponse_proprietaire = raison
        self.date_reponse = timezone.now()
        self.save()

# ============================================
# PHASE 3 : MODÈLE IMAGE LOGEMENT
# À ajouter dans core/models.py
# ============================================

# Ajouter cette classe APRÈS le modèle Logement :

class ImageLogement(models.Model):
    """Images associées à un logement"""
    logement = models.ForeignKey(
        Logement, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name="Logement"
    )
    image = models.ImageField(
        upload_to='logements/%Y/%m/',
        verbose_name="Image"
    )
    titre = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name="Titre de l'image"
    )
    description = models.TextField(
        blank=True, 
        verbose_name="Description"
    )
    ordre = models.IntegerField(
        default=0, 
        verbose_name="Ordre d'affichage"
    )
    est_principale = models.BooleanField(
        default=False, 
        verbose_name="Image principale"
    )
    date_ajout = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        ordering = ['ordre', '-est_principale', '-date_ajout']
        verbose_name = "Image logement"
        verbose_name_plural = "Images logement"
        indexes = [
            models.Index(fields=['logement', 'ordre']),
        ]
    
    def __str__(self):
        return f"Image - {self.logement.titre}"
    
    def save(self, *args, **kwargs):
        # S'il y a une seule image, la mettre en principale
        if not ImageLogement.objects.filter(
            logement=self.logement, 
            est_principale=True
        ).exclude(id=self.id).exists():
            self.est_principale = True
        super().save(*args, **kwargs)

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
# CANDIDATURES (Phase 14.3)
# ============================================

class Candidature(models.Model):
    """Candidature d'un locataire pour un logement"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('annulee', 'Annulée'),
    ]
    
    logement = models.ForeignKey(Logement, on_delete=models.CASCADE, related_name='candidatures', verbose_name="Logement")
    candidat = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mes_candidatures', verbose_name="Candidat")
    
    # Informations candidature
    message = models.TextField(verbose_name="Message de motivation", blank=True, null=True)
    revenus_mensuels = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Revenus mensuels")
    garant = models.CharField(max_length=200, blank=True, null=True, verbose_name="Garant (nom et contact)")
    
    # Documents (optionnel)
    pieces_justificatives = models.FileField(upload_to='candidatures/pieces/%Y/%m/', blank=True, null=True, verbose_name="Pièces justificatives (PDF)")
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    
    # Réponse du propriétaire
    reponse_proprietaire = models.TextField(blank=True, null=True, verbose_name="Réponse du propriétaire")
    date_reponse = models.DateTimeField(blank=True, null=True, verbose_name="Date de réponse")
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de candidature")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"
        unique_together = [['logement', 'candidat']]  # Un candidat ne peut candidater qu'une fois par logement
        indexes = [
            models.Index(fields=['logement', 'statut']),
            models.Index(fields=['candidat', 'statut']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Candidature de {self.candidat.username} pour {self.logement.titre}"
    
    @property
    def proprietaire(self):
        """Retourne le propriétaire du logement"""
        return self.logement.proprietaire if self.logement.proprietaire else None


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


# ============================================
# MAGIC LINK (CONNEXION SANS MOT DE PASSE)
# ============================================

class MagicLinkToken(models.Model):
    """Token pour connexion sans mot de passe (Magic Link)"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='magic_links')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Magic Link"
        verbose_name_plural = "Magic Links"
    
    def __str__(self):
        return f"Magic Link {self.user.email}"


# ============================================
# 2FA - CODES DE RÉCUPÉRATION
# ============================================

class TwoFactorBackupCode(models.Model):
    """Codes de récupération pour 2FA"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='backup_codes')
    code = models.CharField(max_length=10, unique=True)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Code de récupération 2FA"
        verbose_name_plural = "Codes de récupération 2FA"
    
    def __str__(self):
        return f"Backup code {self.user.email}"


# ============================================
# BADGES ET ACHIEVEMENTS
# ============================================

class Badge(models.Model):
    """Badge/Achievement disponible"""
    BADGE_TYPES = [
        ('security', 'Sécurité'),
        ('activity', 'Activité'),
        ('social', 'Social'),
        ('premium', 'Premium'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🏆')  # Emoji ou nom d'icône
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES, default='activity')
    rarity = models.CharField(max_length=20, choices=[
        ('common', 'Commun'),
        ('rare', 'Rare'),
        ('epic', 'Épique'),
        ('legendary', 'Légendaire'),
    ], default='common')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
    
    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """Badge obtenu par un utilisateur"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='users')
    earned_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=100)  # Pourcentage de progression si applicable
    
    class Meta:
        unique_together = ('user', 'badge')
        ordering = ['-earned_at']
        verbose_name = "Badge utilisateur"
        verbose_name_plural = "Badges utilisateurs"
    
    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"


# ============================================
# NOTIFICATIONS
# ============================================

class UserNotification(models.Model):
    """Notifications utilisateur avec système avancé de catégories, ranking et feedback"""
    NOTIFICATION_TYPES = [
        # Réseau social
        ('connection_accepted', 'Connexion acceptée'),
        ('connection_request', 'Demande de connexion'),
        ('follow', 'Nouveau follower'),
        ('invitation_received', 'Invitation reçue'),
        # Posts & Contenu
        ('post_liked', 'Like sur un post'),
        ('post_commented', 'Commentaire sur un post'),
        ('post_reaction', 'Réaction sur un post'),
        ('comment_replied', 'Réponse à un commentaire'),
        ('post_mentioned', 'Mention dans un post'),
        ('comment_mentioned', 'Mention dans un commentaire'),
        ('post_shared', 'Post partagé'),
        ('collaborative_post_joined', 'Rejoint un post collaboratif'),
        # Messages
        ('new_message', 'Nouveau message'),
        ('message_reaction', 'Réaction sur un message'),
        ('message_mentioned', 'Mention dans un message'),
        # Groupes
        ('group_invitation', 'Invitation à rejoindre un groupe'),
        ('group_post', 'Nouveau post dans un groupe'),
        ('group_meetup', 'Nouveau meetup dans un groupe'),
        ('group_sondage', 'Nouveau sondage dans un groupe'),
        ('group_question_answered', 'Réponse à votre question'),
        # Logements & Baux
        ('property_updated', 'Mise à jour d\'un logement favori'),
        ('property_favorited', 'Logement ajouté aux favoris'),
        ('review_received', 'Avis reçu'),
        ('review_replied', 'Réponse à votre avis'),
        # Gestion bail
        ('bail_payment_due', 'Paiement de loyer à venir'),
        ('bail_payment_received', 'Paiement de loyer reçu'),
        ('bail_document_signed', 'Document signé'),
        ('bail_maintenance_request', 'Nouvelle demande d\'entretien'),
        ('bail_ticket_created', 'Nouveau ticket créé'),
        ('bail_ticket_resolved', 'Ticket résolu'),
        ('bail_reminder', 'Rappel automatique'),
        # Vérifications & Sécurité
        ('verification_approved', 'Vérification approuvée'),
        ('verification_rejected', 'Vérification rejetée'),
        ('security', 'Alerte de sécurité'),
        ('login_new_device', 'Connexion depuis un nouvel appareil'),
        # Système
        ('system', 'Notification système'),
        ('badge_earned', 'Badge obtenu'),
    ]
    
    CATEGORY_CHOICES = [
        ('social', 'Réseau social'),
        ('content', 'Contenu & Posts'),
        ('messages', 'Messages'),
        ('groups', 'Groupes'),
        ('properties', 'Logements'),
        ('lease', 'Gestion bail'),
        ('security', 'Sécurité'),
        ('system', 'Système'),
    ]
    
    IMPORTANCE_CHOICES = [
        ('critical', 'Critique'),
        ('high', 'Haute'),
        ('medium', 'Moyenne'),
        ('low', 'Basse'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='system')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='system', verbose_name="Catégorie")
    importance = models.CharField(max_length=20, choices=IMPORTANCE_CHOICES, default='medium', verbose_name="Importance")
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Utilisateur source de la notification
    from_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        blank=True,
        null=True,
        verbose_name="De l'utilisateur"
    )
    
    # Liens vers les éléments concernés
    action_url = models.CharField(max_length=500, blank=True, null=True, verbose_name="URL d'action")
    related_post = models.ForeignKey('Post', on_delete=models.CASCADE, blank=True, null=True, related_name='notifications')
    related_comment = models.ForeignKey('PostComment', on_delete=models.CASCADE, blank=True, null=True, related_name='notifications')
    related_conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, blank=True, null=True, related_name='notifications')
    related_group = models.ForeignKey('Group', on_delete=models.CASCADE, blank=True, null=True, related_name='notifications')
    related_logement = models.ForeignKey('Logement', on_delete=models.CASCADE, blank=True, null=True, related_name='notifications')
    
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    icon = models.CharField(max_length=50, default='🔔')
    
    # Feedback utilisateur
    feedback_not_interested = models.BooleanField(default=False, verbose_name="Pas intéressant")
    feedback_at = models.DateTimeField(blank=True, null=True, verbose_name="Feedback donné à")
    
    # Push notifications
    push_sent = models.BooleanField(default=False, verbose_name="Push envoyé")
    push_sent_at = models.DateTimeField(blank=True, null=True, verbose_name="Push envoyé à")
    email_sent = models.BooleanField(default=False, verbose_name="Email envoyé")
    email_sent_at = models.DateTimeField(blank=True, null=True, verbose_name="Email envoyé à")
    
    # Données supplémentaires (JSON)
    extra_data = models.JSONField(default=dict, blank=True, verbose_name="Données supplémentaires")
    
    class Meta:
        ordering = ['-importance', '-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        indexes = [
            models.Index(fields=['user', 'read', '-created_at']),
            models.Index(fields=['user', 'category', '-created_at']),
            models.Index(fields=['user', 'importance', '-created_at']),
            models.Index(fields=['user', 'notification_type', '-created_at']),
            models.Index(fields=['from_user', '-created_at']),
            models.Index(fields=['feedback_not_interested']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    def mark_as_read(self):
        """Marque la notification comme lue"""
        if not self.read:
            self.read = True
            self.read_at = timezone.now()
            self.save()
    
    def mark_not_interested(self):
        """Marque la notification comme "pas intéressante" pour affiner le ranking"""
        self.feedback_not_interested = True
        self.feedback_at = timezone.now()
        self.save()
    
    def get_action_url(self):
        """Retourne l'URL d'action selon le type de notification"""
        if self.action_url:
            return self.action_url
        
        # Générer l'URL selon le type
        if self.notification_type in ['connection_accepted', 'connection_request']:
            if self.from_user:
                return f'/profile/{self.from_user.id}/'
        
        elif self.notification_type in ['post_liked', 'post_commented', 'post_mentioned']:
            if self.related_post:
                return f'/connect/?post={self.related_post.id}'
        
        elif self.notification_type in ['comment_replied', 'comment_mentioned']:
            if self.related_comment and self.related_comment.post:
                return f'/connect/?post={self.related_comment.post.id}#comment-{self.related_comment.id}'
        
        elif self.notification_type == 'new_message':
            if self.related_conversation:
                return f'/connect/messages/?conversation={self.related_conversation.id}'
        
        elif self.notification_type in ['group_invitation', 'group_post']:
            if self.related_group:
                return f'/connect/groups/{self.related_group.id}/'
        
        elif self.notification_type == 'property_updated':
            if self.related_logement:
                return f'/logement/{self.related_logement.id}/'
        
        elif self.notification_type == 'review_received':
            if self.related_logement:
                return f'/logement/{self.related_logement.id}/'
        
        elif self.notification_type == 'verification_approved':
            return '/connect/settings/'
        
        return '/connect/notifications/'


# ============================================
# ALERTES DE SÉCURITÉ
# ============================================

class SecurityAlert(models.Model):
    """Alertes de sécurité pour l'utilisateur"""
    ALERT_TYPES = [
        ('login_new_device', 'Connexion depuis un nouvel appareil'),
        ('login_new_location', 'Connexion depuis un nouvel emplacement'),
        ('password_changed', 'Mot de passe modifié'),
        ('email_changed', 'Email modifié'),
        ('2fa_enabled', '2FA activé'),
        ('2fa_disabled', '2FA désactivé'),
        ('suspicious_activity', 'Activité suspecte'),
        ('account_locked', 'Compte verrouillé'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='security_alerts')
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    device_info = models.TextField(blank=True)
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('critical', 'Critique'),
    ], default='medium')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Alerte de sécurité"
        verbose_name_plural = "Alertes de sécurité"
        indexes = [
            models.Index(fields=['user', 'read', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"


# ============================================
# TRANSPAREO CONNECT - MESSAGES ENTRE UTILISATEURS
# ============================================

class Conversation(models.Model):
    """Conversation entre deux utilisateurs"""
    participants = models.ManyToManyField(CustomUser, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True, related_name='conversation_last')
    
    # Lien avec bail (Phase 14.4) - Si la conversation est liée à un bail
    bail = models.ForeignKey('Bail', on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations', verbose_name="Bail associé")
    
    # Statuts par utilisateur (via ConversationStatus)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        indexes = [
            models.Index(fields=['-updated_at']),
            models.Index(fields=['bail']),  # Index pour filtrage rapide
        ]
    
    def __str__(self):
        if self.bail:
            return f"Conversation Bail {self.bail.id} - {self.bail.logement.titre}"
        return f"Conversation {self.id}"
    
    def get_other_participant(self, user):
        """Retourne l'autre participant de la conversation (actif uniquement)"""
        return self.participants.filter(is_active=True).exclude(id=user.id).first()
    
    def get_unread_count(self, user):
        """Retourne le nombre de messages non lus pour un utilisateur"""
        return Message.objects.filter(
            conversation=self,
            read=False
        ).exclude(sender=user).count()
    
    def is_archived_by(self, user):
        """Vérifie si la conversation est archivée par un utilisateur"""
        status = ConversationStatus.objects.filter(conversation=self, user=user).first()
        return status.archived if status else False
    
    def is_favorited_by(self, user):
        """Vérifie si la conversation est en favoris par un utilisateur"""
        status = ConversationStatus.objects.filter(conversation=self, user=user).first()
        return status.favorited if status else False
    
    def is_lease_related(self):
        """Vérifie si la conversation est liée à un bail (Phase 14.4)"""
        return self.bail is not None
    
    def get_lease_info(self):
        """Retourne les informations du bail si la conversation est liée (Phase 14.4)"""
        if self.bail:
            return {
                'bail_id': self.bail.id,
                'logement': self.bail.logement.titre,
                'logement_id': self.bail.logement.id,
                'locataire': self.bail.locataire,
                'proprietaire': self.bail.proprietaire,
            }
        return None


class Message(models.Model):
    """Message dans une conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Pièces jointes
    image = models.ImageField(upload_to='messages/images/%Y/%m/', blank=True, null=True, verbose_name="Image")
    document = models.FileField(upload_to='messages/documents/%Y/%m/', blank=True, null=True, verbose_name="Document")
    document_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nom du document")
    
    # Sécurité & Modération (Phase 12)
    is_quarantined = models.BooleanField(default=False, verbose_name="En quarantaine")
    is_spam = models.BooleanField(default=False, verbose_name="Spam détecté")
    is_fraud = models.BooleanField(default=False, verbose_name="Arnaque détectée")
    is_inappropriate = models.BooleanField(default=False, verbose_name="Contenu inapproprié")
    is_suspicious = models.BooleanField(default=False, verbose_name="Suspect")
    spam_reason = models.CharField(max_length=200, blank=True, null=True, verbose_name="Raison du spam")
    security_score = models.IntegerField(default=0, verbose_name="Score de sécurité (0-100)")
    reviewed_by_admin = models.BooleanField(default=False, verbose_name="Révisé par admin")
    
    # Nouveaux champs pour fonctionnalités avancées
    is_pinned = models.BooleanField(default=False, verbose_name="Message épinglé")
    pinned_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='pinned_messages', verbose_name="Épinglé par")
    pinned_at = models.DateTimeField(blank=True, null=True, verbose_name="Épinglé à")
    
    # Accusé de réception
    delivered = models.BooleanField(default=False, verbose_name="Message délivré")
    delivered_at = models.DateTimeField(blank=True, null=True, verbose_name="Délivré à")
    
    # Partage de logement/document
    shared_logement = models.ForeignKey('Logement', on_delete=models.SET_NULL, null=True, blank=True, related_name='shared_in_messages', verbose_name="Logement partagé")
    shared_document = models.ForeignKey('DocumentBail', on_delete=models.SET_NULL, null=True, blank=True, related_name='shared_in_messages', verbose_name="Document partagé")
    
    # Message vocal
    audio = models.FileField(upload_to='messages/audio/%Y/%m/', blank=True, null=True, verbose_name="Message vocal")
    audio_duration = models.IntegerField(blank=True, null=True, verbose_name="Durée audio (secondes)")
    
    # Lien avec appel (si message lié à un appel)
    call = models.ForeignKey('Call', on_delete=models.SET_NULL, null=True, blank=True, related_name='messages', verbose_name="Appel associé")
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['read']),
        ]
    
    def __str__(self):
        return f"Message de {self.sender.username} dans conversation {self.conversation.id}"
    
    def mark_as_read(self):
        """Marque le message comme lu"""
        if not self.read:
            self.read = True
            self.read_at = timezone.now()
            self.save()
    
    def has_attachment(self):
        """Vérifie si le message a une pièce jointe"""
        return bool(self.image or self.document)
    
    def check_suspicious_content(self):
        """Vérifie si le contenu est suspect (spam, arnaque, etc.)"""
        suspicious_keywords = [
            'virement', 'argent', 'prêt', 'gagner', 'gratuit', 'urgent',
            'cliquez ici', 'offre limitée', 'héritage', 'loterie',
            'compte suspendu', 'vérifier votre compte', 'banque'
        ]
        suspicious_domains = ['bit.ly', 'tinyurl.com', 't.co']
        
        content_lower = self.content.lower()
        
        # Vérifier les mots-clés suspects
        for keyword in suspicious_keywords:
            if keyword in content_lower:
                self.is_suspicious = True
                self.spam_reason = f"Mot-clé suspect détecté: {keyword}"
                return True
        
        # Vérifier les liens suspects
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, self.content)
        
        for url in urls:
            for domain in suspicious_domains:
                if domain in url:
                    self.is_suspicious = True
                    self.spam_reason = f"Lien suspect détecté: {domain}"
                    return True
        
        return False


# ============================================
# TRANSPAREO CONNECT - STATUT CONVERSATION
# ============================================

class ConversationStatus(models.Model):
    """Statut d'une conversation pour un utilisateur (archivée, favoris, etc.)"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='conversation_statuses')
    archived = models.BooleanField(default=False, verbose_name="Archivée")
    favorited = models.BooleanField(default=False, verbose_name="Favoris")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('conversation', 'user')
        verbose_name = "Statut de conversation"
        verbose_name_plural = "Statuts de conversation"
        indexes = [
            models.Index(fields=['user', 'archived']),
            models.Index(fields=['user', 'favorited']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Conversation {self.conversation.id} ({'Archivée' if self.archived else 'Active'})"


# ============================================
# TRANSPAREO CONNECT - GROUPES & COMMUNAUTÉS
# ============================================

class Group(models.Model):
    """Groupe/Communauté dans Transpareo Connect"""
    CATEGORY_CHOICES = [
        ('locataires', 'Locataires'),
        ('proprietaires', 'Propriétaires'),
        ('mixte', 'Mixte'),
        ('quartier', 'Quartier'),
        ('theme', 'Thème'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nom du groupe")
    description = models.TextField(blank=True, null=True, verbose_name="Description courte")
    full_description = models.TextField(blank=True, null=True, verbose_name="Description complète")
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_groups')
    members = models.ManyToManyField(CustomUser, related_name='connect_groups', blank=True, through='GroupMembership')
    admins = models.ManyToManyField(CustomUser, related_name='administered_connect_groups', blank=True)
    moderators = models.ManyToManyField(CustomUser, related_name='moderated_groups', blank=True)
    
    # Visibilité et type
    is_public = models.BooleanField(default=True, verbose_name="Groupe public")
    require_approval = models.BooleanField(default=False, verbose_name="Demande d'approbation requise")
    
    # Catégorie et localisation
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='mixte',
        verbose_name="Catégorie"
    )
    ville = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ville")
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name="Région")
    
    # Règles et informations
    rules = models.TextField(blank=True, null=True, verbose_name="Règles du groupe")
    
    # Images
    cover_image = models.ImageField(upload_to='groups/covers/', blank=True, null=True, verbose_name="Image de couverture")
    icon = models.CharField(max_length=50, default='👥', verbose_name="Icône")
    
    # Tags et événements
    tags = models.CharField(max_length=500, blank=True, null=True, verbose_name="Tags (séparés par des virgules)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Groupe"
        verbose_name_plural = "Groupes"
        indexes = [
            models.Index(fields=['category', 'is_public']),
            models.Index(fields=['ville', 'region']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_members_count(self):
        """Retourne le nombre de membres actifs"""
        return self.memberships.filter(status='accepted').count()
    
    def get_posts_count(self):
        """Retourne le nombre de posts dans le groupe"""
        return self.posts.count()
    
    def is_member(self, user):
        """Vérifie si un utilisateur est membre du groupe"""
        if not user.is_authenticated:
            return False
        membership = GroupMembership.objects.filter(group=self, user=user, status='accepted').first()
        return membership is not None
    
    def is_admin(self, user):
        """Vérifie si un utilisateur est admin du groupe"""
        if not user.is_authenticated:
            return False
        return user in self.admins.all() or user == self.creator
    
    def is_moderator(self, user):
        """Vérifie si un utilisateur est modérateur du groupe"""
        if not user.is_authenticated:
            return False
        return user in self.moderators.all() or self.is_admin(user)
    
    def can_post(self, user):
        """Vérifie si un utilisateur peut publier dans le groupe"""
        if not user.is_authenticated:
            return False
        return self.is_member(user) or self.is_admin(user)
    
    def add_member(self, user, role='member'):
        """Ajoute un membre au groupe"""
        membership, created = GroupMembership.objects.get_or_create(
            group=self,
            user=user,
            defaults={'role': role, 'status': 'accepted'}
        )
        if not created and membership.status != 'accepted':
            membership.status = 'accepted'
            membership.role = role
            membership.save()
        return membership
    
    def remove_member(self, user):
        """Retire un membre du groupe"""
        GroupMembership.objects.filter(group=self, user=user).delete()
    
    def ban_member(self, user):
        """Bannit un membre du groupe"""
        membership = GroupMembership.objects.filter(group=self, user=user).first()
        if membership:
            membership.status = 'banned'
            membership.save()
        else:
            GroupMembership.objects.create(group=self, user=user, status='banned', role='member')


# ============================================
# TRANSPAREO CONNECT - MEMBRES DE GROUPE
# ============================================

class GroupMembership(models.Model):
    """Membres d'un groupe avec rôles et statuts"""
    ROLE_CHOICES = [
        ('member', 'Membre'),
        ('moderator', 'Modérateur'),
        ('admin', 'Administrateur'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Accepté'),
        ('rejected', 'Refusé'),
        ('banned', 'Banni'),
    ]
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='group_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name="Rôle")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('group', 'user')
        ordering = ['-joined_at']
        verbose_name = "Membre de groupe"
        verbose_name_plural = "Membres de groupe"
        indexes = [
            models.Index(fields=['group', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['group', 'role']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.role})"
    
    def accept(self):
        """Accepte la demande d'adhésion"""
        self.status = 'accepted'
        self.save()
    
    def reject(self):
        """Refuse la demande d'adhésion"""
        self.status = 'rejected'
        self.save()
    
    def ban(self):
        """Bannit le membre"""
        self.status = 'banned'
        self.save()
    

# ============================================
# TRANSPAREO CONNECT - GROUPES AVANCÉS
# ============================================

class SousGroupe(models.Model):
    """Sous-groupe thématique dans un groupe principal"""
    parent_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='sous_groupes', verbose_name="Groupe parent")
    name = models.CharField(max_length=200, verbose_name="Nom du sous-groupe")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    icon = models.CharField(max_length=50, default='📁', verbose_name="Icône")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Sous-groupe"
        verbose_name_plural = "Sous-groupes"
    
    def __str__(self):
        return f"{self.parent_group.name} - {self.name}"


class GroupMeetup(models.Model):
    """Événement Meetup/Visio live dans un groupe"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='meetups', verbose_name="Groupe")
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    date_start = models.DateTimeField(verbose_name="Date de début")
    date_end = models.DateTimeField(blank=True, null=True, verbose_name="Date de fin")
    is_live = models.BooleanField(default=False, verbose_name="En direct")
    visio_link = models.URLField(blank=True, null=True, verbose_name="Lien visio")
    replay_link = models.URLField(blank=True, null=True, verbose_name="Lien replay")
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_meetups', verbose_name="Créé par")
    participants = models.ManyToManyField(CustomUser, related_name='participated_meetups', blank=True, verbose_name="Participants")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_start']
        verbose_name = "Meetup/Visio"
        verbose_name_plural = "Meetups/Visios"
    
    def __str__(self):
        return f"{self.group.name} - {self.title}"


class GroupSondage(models.Model):
    """Sondage dans un groupe"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='sondages', verbose_name="Groupe")
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='sondage', null=True, blank=True, verbose_name="Post associé")
    question = models.CharField(max_length=500, verbose_name="Question")
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_sondages', verbose_name="Créé par")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    show_results_public = models.BooleanField(default=True, verbose_name="Afficher résultats publiquement")
    date_end = models.DateTimeField(blank=True, null=True, verbose_name="Date de fin")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Sondage"
        verbose_name_plural = "Sondages"
    
    def __str__(self):
        return f"{self.group.name} - {self.question}"


class SondageOption(models.Model):
    """Option de réponse pour un sondage"""
    sondage = models.ForeignKey(GroupSondage, on_delete=models.CASCADE, related_name='options', verbose_name="Sondage")
    text = models.CharField(max_length=200, verbose_name="Texte de l'option")
    votes_count = models.IntegerField(default=0, verbose_name="Nombre de votes")
    order = models.IntegerField(default=0, verbose_name="Ordre")
    
    class Meta:
        ordering = ['order', 'text']
        verbose_name = "Option de sondage"
        verbose_name_plural = "Options de sondage"
    
    def __str__(self):
        return f"{self.sondage.question} - {self.text}"


class SondageVote(models.Model):
    """Vote d'un utilisateur pour une option de sondage"""
    sondage = models.ForeignKey(GroupSondage, on_delete=models.CASCADE, related_name='votes', verbose_name="Sondage")
    option = models.ForeignKey(SondageOption, on_delete=models.CASCADE, related_name='votes', verbose_name="Option")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sondage_votes', verbose_name="Utilisateur")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('sondage', 'user')
        verbose_name = "Vote de sondage"
        verbose_name_plural = "Votes de sondage"
    
    def __str__(self):
        return f"{self.user.username} a voté pour {self.option.text}"


class QuestionReponse(models.Model):
    """Question-réponse validée dans un groupe"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='questions_reponses', verbose_name="Groupe")
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='question_reponse', verbose_name="Post question")
    question = models.TextField(verbose_name="Question")
    best_answer = models.ForeignKey('ReponseQuestion', on_delete=models.SET_NULL, null=True, blank=True, related_name='best_for_question', verbose_name="Meilleure réponse")
    is_solved = models.BooleanField(default=False, verbose_name="Résolu")
    official_solution = models.ForeignKey('ReponseQuestion', on_delete=models.SET_NULL, null=True, blank=True, related_name='official_for_question', verbose_name="Solution officielle")
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_questions', verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Question-Réponse"
        verbose_name_plural = "Questions-Réponses"
    
    def __str__(self):
        return f"{self.group.name} - {self.question[:50]}"


class ReponseQuestion(models.Model):
    """Réponse à une question dans un groupe"""
    question = models.ForeignKey(QuestionReponse, on_delete=models.CASCADE, related_name='reponses', verbose_name="Question")
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='reponse_question', null=True, blank=True, verbose_name="Post réponse")
    content = models.TextField(verbose_name="Contenu de la réponse")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reponses_questions', verbose_name="Auteur")
    votes_count = models.IntegerField(default=0, verbose_name="Nombre de votes")
    is_official = models.BooleanField(default=False, verbose_name="Solution officielle")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-votes_count', '-created_at']
        verbose_name = "Réponse à une question"
        verbose_name_plural = "Réponses aux questions"
    
    def __str__(self):
        return f"Réponse de {self.author.username} à {self.question.question[:30]}"


class VoteReponse(models.Model):
    """Vote pour une réponse (meilleure réponse)"""
    reponse = models.ForeignKey(ReponseQuestion, on_delete=models.CASCADE, related_name='votes', verbose_name="Réponse")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='votes_reponses', verbose_name="Utilisateur")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('reponse', 'user')
        verbose_name = "Vote de réponse"
        verbose_name_plural = "Votes de réponses"
    
    def __str__(self):
        return f"{self.user.username} a voté pour la réponse de {self.reponse.author.username}"


# ============================================
# TRANSPAREO CONNECT - MESSAGERIE AVANCÉE
# ============================================

class MessageReaction(models.Model):
    """Réaction emoji sur un message"""
    REACTION_CHOICES = [
        ('👍', '👍'), ('❤️', '❤️'), ('😂', '😂'), ('😮', '😮'),
        ('😢', '😢'), ('🔥', '🔥'), ('👏', '👏'), ('✅', '✅'),
    ]
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions', verbose_name="Message")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='message_reactions', verbose_name="Utilisateur")
    emoji = models.CharField(max_length=10, choices=REACTION_CHOICES, verbose_name="Emoji")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('message', 'user', 'emoji')
        ordering = ['-created_at']
        verbose_name = "Réaction de message"
        verbose_name_plural = "Réactions de messages"
        indexes = [
            models.Index(fields=['message', 'emoji']),
        ]
    
    def __str__(self):
        return f"{self.user.username} a réagi {self.emoji} au message {self.message.id}"


class MessageMention(models.Model):
    """Mention d'un utilisateur dans un message (@utilisateur)"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='mentions', verbose_name="Message")
    mentioned_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='message_mentions', verbose_name="Utilisateur mentionné")
    position = models.IntegerField(verbose_name="Position dans le texte")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['position']
        verbose_name = "Mention dans message"
        verbose_name_plural = "Mentions dans messages"
        indexes = [
            models.Index(fields=['message', 'mentioned_user']),
        ]
    
    def __str__(self):
        return f"{self.mentioned_user.username} mentionné dans message {self.message.id}"


class TypingIndicator(models.Model):
    """Indicateur de frappe en cours"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='typing_indicators', verbose_name="Conversation")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='typing_indicators', verbose_name="Utilisateur")
    is_typing = models.BooleanField(default=True, verbose_name="En train de taper")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('conversation', 'user')
        verbose_name = "Indicateur de frappe"
        verbose_name_plural = "Indicateurs de frappe"
        indexes = [
            models.Index(fields=['conversation', 'is_typing']),
        ]
    
    def __str__(self):
        return f"{self.user.username} tape dans conversation {self.conversation.id}"


class Call(models.Model):
    """Appel vocal ou vidéo entre utilisateurs"""
    CALL_TYPE_CHOICES = [
        ('voice', 'Appel vocal'),
        ('video', 'Appel vidéo'),
    ]
    
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('ringing', 'Sonnerie'),
        ('answered', 'Répondu'),
        ('ended', 'Terminé'),
        ('missed', 'Manqué'),
        ('rejected', 'Rejeté'),
        ('cancelled', 'Annulé'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='calls', verbose_name="Conversation")
    caller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='calls_initiated', verbose_name="Appelant")
    call_type = models.CharField(max_length=10, choices=CALL_TYPE_CHOICES, default='voice', verbose_name="Type d'appel")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated', verbose_name="Statut")
    
    # Participants
    participants = models.ManyToManyField(CustomUser, related_name='calls_participated', verbose_name="Participants")
    
    # Dates
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Début")
    answered_at = models.DateTimeField(blank=True, null=True, verbose_name="Répondu à")
    ended_at = models.DateTimeField(blank=True, null=True, verbose_name="Terminé à")
    duration = models.IntegerField(blank=True, null=True, verbose_name="Durée (secondes)")
    
    # Enregistrement (si activé)
    recording = models.FileField(upload_to='calls/recordings/%Y/%m/', blank=True, null=True, verbose_name="Enregistrement")
    recording_enabled = models.BooleanField(default=False, verbose_name="Enregistrement activé")
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = "Appel"
        verbose_name_plural = "Appels"
        indexes = [
            models.Index(fields=['conversation', 'started_at']),
            models.Index(fields=['caller', 'started_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Appel {self.call_type} - {self.caller.username} - {self.status}"
    
    def calculate_duration(self):
        """Calcule la durée de l'appel"""
        if self.ended_at and self.answered_at:
            delta = self.ended_at - self.answered_at
            self.duration = int(delta.total_seconds())
            self.save()
        return self.duration


# ============================================
# TRANSPAREO CONNECT - CONNEXIONS ENTRE UTILISATEURS
# ============================================

class UserConnection(models.Model):
    """Connexion entre deux utilisateurs (réseau social)"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('blocked', 'Bloquée'),
    ]
    
    user_from = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='connections_sent')
    user_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='connections_received')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ('user_from', 'user_to')
        ordering = ['-created_at']
        verbose_name = "Connexion"
        verbose_name_plural = "Connexions"
        indexes = [
            models.Index(fields=['user_from', 'status']),
            models.Index(fields=['user_to', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user_from.username} -> {self.user_to.username} ({self.status})"
    
    def accept(self):
        """Accepte la demande de connexion"""
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.save()
    
    @staticmethod
    def get_connection_count(user):
        """Retourne le nombre de connexions acceptées d'un utilisateur"""
        return UserConnection.objects.filter(
            Q(user_from=user) | Q(user_to=user),
            status='accepted'
        ).count()


# ============================================
# TRANSPAREO CONNECT - POSTS & PUBLICATIONS
# ============================================

class Post(models.Model):
    """Post dans le fil d'actualité Transpareo Connect"""
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('connections', 'Connexions uniquement'),
        ('group', 'Groupe spécifique'),
    ]
    
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(verbose_name="Contenu")
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='posts')
    hashtags = models.CharField(max_length=500, blank=True, null=True, verbose_name="Hashtags")
    mentions = models.ManyToManyField(CustomUser, related_name='mentioned_in_posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Nouvelles fonctionnalités
    related_logement = models.ForeignKey('Logement', on_delete=models.SET_NULL, null=True, blank=True, related_name='related_posts', verbose_name="Logement associé")
    is_collaborative = models.BooleanField(default=False, verbose_name="Post collaboratif")
    content_type = models.CharField(
        max_length=20,
        choices=[
            ('news', 'Actualité'),
            ('guide', 'Guide'),
            ('offer', 'Offre'),
            ('discussion', 'Discussion'),
            ('property', 'Logement'),
            ('group', 'Groupe'),
        ],
        default='discussion',
        verbose_name="Type de contenu"
    )
    
    # Compteurs (pour performance, mis à jour via signals)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    
    # Sécurité & Modération (Phase 12)
    is_quarantined = models.BooleanField(default=False, verbose_name="En quarantaine")
    quarantine_reason = models.TextField(blank=True, null=True, verbose_name="Raison de la quarantaine")
    is_spam = models.BooleanField(default=False, verbose_name="Spam détecté")
    is_fraud = models.BooleanField(default=False, verbose_name="Arnaque détectée")
    is_inappropriate = models.BooleanField(default=False, verbose_name="Contenu inapproprié")
    security_score = models.IntegerField(default=0, verbose_name="Score de sécurité (0-100)")
    reviewed_by_admin = models.BooleanField(default=False, verbose_name="Révisé par admin")
    
    # Média
    images = models.ManyToManyField('PostImage', blank=True, related_name='post_images')
    documents = models.ManyToManyField('PostDocument', blank=True, related_name='post_documents')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['visibility', '-created_at']),
            models.Index(fields=['group', '-created_at']),
        ]
    
    def __str__(self):
        return f"Post de {self.author.username} - {self.created_at}"
    
    def get_likes_count(self):
        """Retourne le nombre réel de likes"""
        return self.likes.filter(active=True).count()
    
    def get_comments_count(self):
        """Retourne le nombre réel de commentaires"""
        return self.comments.filter(parent__isnull=True).count()
    
    def get_shares_count(self):
        """Retourne le nombre réel de partages"""
        return self.shares.count()
    
    def is_liked_by(self, user):
        """Vérifie si l'utilisateur a liké ce post"""
        return self.likes.filter(user=user, active=True).exists()
    
    def is_visible(self, user=None):
        """Vérifie si le post est visible pour un utilisateur (pas en quarantaine)"""
        if not self.is_quarantined:
            return True
        # Les admins peuvent voir les posts en quarantaine
        if user and (user.is_staff or user.is_superuser):
            return True
        return False


class PostImage(models.Model):
    """Image attachée à un post"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_images_rel')
    image = models.ImageField(upload_to='posts/images/%Y/%m/', verbose_name="Image")
    caption = models.CharField(max_length=200, blank=True, null=True, verbose_name="Légende")
    order = models.IntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Image de post"
        verbose_name_plural = "Images de posts"
    
    def __str__(self):
        return f"Image {self.id} - Post {self.post.id}"


class PostDocument(models.Model):
    """Document attaché à un post"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_documents_rel')
    document = models.FileField(upload_to='posts/documents/%Y/%m/', verbose_name="Document")
    title = models.CharField(max_length=200, verbose_name="Titre")
    file_type = models.CharField(max_length=50, blank=True, verbose_name="Type de fichier")
    file_size = models.IntegerField(blank=True, null=True, verbose_name="Taille (octets)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Document de post"
        verbose_name_plural = "Documents de posts"
    
    def __str__(self):
        return f"{self.title} - Post {self.post.id}"


class PostLike(models.Model):
    """Like sur un post"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)  # Pour permettre unlike
    
    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']
        verbose_name = "Like"
        verbose_name_plural = "Likes"
    
    def __str__(self):
        return f"{self.user.username} aime le post {self.post.id}"


class PostComment(models.Model):
    """Commentaire sur un post (avec support nested)"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='post_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField(verbose_name="Contenu")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        indexes = [
            models.Index(fields=['post', 'parent', 'created_at']),
        ]
    
    def __str__(self):
        return f"Commentaire de {self.author.username} sur post {self.post.id}"
    
    def get_likes_count(self):
        """Retourne le nombre réel de likes"""
        return self.comment_likes.filter(active=True).count()
    
    def is_liked_by(self, user):
        """Vérifie si l'utilisateur a liké ce commentaire"""
        return self.comment_likes.filter(user=user, active=True).exists()


class CommentLike(models.Model):
    """Like sur un commentaire"""
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='comment_likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('comment', 'user')
        verbose_name = "Like de commentaire"
        verbose_name_plural = "Likes de commentaires"
    
    def __str__(self):
        return f"{self.user.username} aime le commentaire {self.comment.id}"


class PostShare(models.Model):
    """Partage d'un post"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='post_shares')
    comment = models.TextField(blank=True, null=True, verbose_name="Commentaire du partage")
    shared_to_feed = models.BooleanField(default=True, verbose_name="Partagé sur le feed")
    shared_to_message = models.BooleanField(default=False, verbose_name="Partagé en message privé")
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Partage"
        verbose_name_plural = "Partages"
    
    def __str__(self):
        return f"{self.user.username} a partagé le post {self.post.id}"


class PostReaction(models.Model):
    """Réaction emoji sur un post (👍, 🔥, ❤️, etc.)"""
    REACTION_CHOICES = [
        ('👍', '👍'),
        ('🔥', '🔥'),
        ('❤️', '❤️'),
        ('😊', '😊'),
        ('😮', '😮'),
        ('😢', '😢'),
        ('👏', '👏'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='post_reactions')
    emoji = models.CharField(max_length=10, choices=REACTION_CHOICES, verbose_name="Emoji")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user', 'emoji')
        ordering = ['-created_at']
        verbose_name = "Réaction"
        verbose_name_plural = "Réactions"
        indexes = [
            models.Index(fields=['post', 'emoji']),
        ]
    
    def __str__(self):
        return f"{self.user.username} a réagi {self.emoji} au post {self.post.id}"


class Story(models.Model):
    """Story éphémère (24h) pour annonces rapides"""
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='stories')
    content = models.TextField(blank=True, null=True, verbose_name="Contenu texte")
    image = models.ImageField(upload_to='stories/images/%Y/%m/', blank=True, null=True, verbose_name="Image")
    video = models.FileField(upload_to='stories/videos/%Y/%m/', blank=True, null=True, verbose_name="Vidéo")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name="Expire à")
    views_count = models.IntegerField(default=0, verbose_name="Nombre de vues")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Story"
        verbose_name_plural = "Stories"
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Story de {self.author.username} - {self.created_at}"
    
    def is_expired(self):
        """Vérifie si la story a expiré"""
        from django.utils import timezone
        return timezone.now() > self.expires_at


class PinnedAnnouncement(models.Model):
    """Annonce épinglée par l'admin en haut du feed"""
    title = models.CharField(max_length=200, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    link = models.URLField(blank=True, null=True, verbose_name="Lien (optionnel)")
    link_text = models.CharField(max_length=100, blank=True, null=True, verbose_name="Texte du lien")
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_announcements', verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Annonce épinglée"
        verbose_name_plural = "Annonces épinglées"
    
    def __str__(self):
        return self.title


class CommentImage(models.Model):
    """Image attachée à un commentaire"""
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='comment_images')
    image = models.ImageField(upload_to='comments/images/%Y/%m/', verbose_name="Image")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Image de commentaire"
        verbose_name_plural = "Images de commentaires"
    
    def __str__(self):
        return f"Image commentaire {self.id}"


class CommentDocument(models.Model):
    """Document attaché à un commentaire"""
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='comment_documents')
    document = models.FileField(upload_to='comments/documents/%Y/%m/', verbose_name="Document")
    title = models.CharField(max_length=200, verbose_name="Titre")
    file_type = models.CharField(max_length=50, blank=True, verbose_name="Type de fichier")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Document de commentaire"
        verbose_name_plural = "Documents de commentaires"
    
    def __str__(self):
        return f"{self.title} - Commentaire {self.comment.id}"


# ============================================
# TRANSPAREO CONNECT - FOLLOWERS & FOLLOWING
# ============================================

class Follow(models.Model):
    """Système de suivi (follow) - pour recevoir les mises à jour"""
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'followed')
        ordering = ['-created_at']
        verbose_name = "Suivi"
        verbose_name_plural = "Suivis"
        indexes = [
            models.Index(fields=['follower', '-created_at']),
            models.Index(fields=['followed', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.follower.username} suit {self.followed.username}"
    
    @staticmethod
    def get_followers_count(user):
        """Retourne le nombre d'abonnés (followers)"""
        return Follow.objects.filter(followed=user).count()
    
    @staticmethod
    def get_following_count(user):
        """Retourne le nombre de personnes suivies"""
        return Follow.objects.filter(follower=user).count()
    
    @staticmethod
    def is_following(follower_user, followed_user):
        """Vérifie si un utilisateur suit un autre"""
        return Follow.objects.filter(follower=follower_user, followed=followed_user).exists()


# ============================================
# TRANSPAREO CONNECT - RECHERCHE UTILISATEURS & INVITATIONS
# ============================================

class InvitationPersonnalisee(models.Model):
    """Invitation personnalisée avec message optionnel"""
    TYPE_INVITATION_CHOICES = [
        ('connection', 'Demande de connexion'),
        ('group', 'Invitation à un groupe'),
        ('event', 'Invitation à un événement'),
        ('collaboration', 'Invitation à collaborer'),
        ('other', 'Autre'),
    ]
    
    envoyeur = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='invitations_envoyees', verbose_name="Envoyeur")
    destinataire = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='invitations_recues', verbose_name="Destinataire")
    
    # Type et contenu
    type_invitation = models.CharField(max_length=30, choices=TYPE_INVITATION_CHOICES, default='connection', verbose_name="Type d'invitation")
    message_personnalise = models.TextField(blank=True, null=True, verbose_name="Message personnalisé")
    
    # Recommandation groupée
    est_recommandation_groupée = models.BooleanField(default=False, verbose_name="Recommandation groupée")
    autres_recommandeurs = models.ManyToManyField(CustomUser, blank=True, related_name='recommandations_groupées', verbose_name="Autres recommandeurs")
    
    # Statut
    statut = models.CharField(
        max_length=20,
        choices=[
            ('envoyee', 'Envoyée'),
            ('acceptee', 'Acceptée'),
            ('refusee', 'Refusée'),
            ('annulee', 'Annulée'),
        ],
        default='envoyee',
        verbose_name="Statut"
    )
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    repondu_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Invitation personnalisée"
        verbose_name_plural = "Invitations personnalisées"
        indexes = [
            models.Index(fields=['envoyeur', 'statut']),
            models.Index(fields=['destinataire', 'statut']),
            models.Index(fields=['type_invitation', 'statut']),
        ]
    
    def __str__(self):
        return f"Invitation de {self.envoyeur.username} à {self.destinataire.username}"


class SuggestionIA(models.Model):
    """Suggestions d'utilisateurs générées par IA"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='suggestions_ia', verbose_name="Utilisateur")
    utilisateur_suggere = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='suggestions_recues', verbose_name="Utilisateur suggéré")
    
    # Score et raison
    score_similarite = models.FloatField(default=0.0, verbose_name="Score de similarité")
    raisons = models.JSONField(default=list, verbose_name="Raisons de la suggestion")
    
    # Type de suggestion
    TYPE_SUGGESTION_CHOICES = [
        ('proche', 'Utilisateur proche'),
        ('similaire', 'Profil similaire'),
        ('quartier', 'Spécialisé dans le même quartier'),
        ('interet', 'Intérêts communs'),
        ('reseau', 'Réseau commun'),
    ]
    type_suggestion = models.CharField(max_length=30, choices=TYPE_SUGGESTION_CHOICES, verbose_name="Type de suggestion")
    
    # Statut
    vue = models.BooleanField(default=False, verbose_name="Vue")
    acceptee = models.BooleanField(default=False, verbose_name="Acceptée")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-score_similarite', '-created_at']
        verbose_name = "Suggestion IA"
        verbose_name_plural = "Suggestions IA"
        indexes = [
            models.Index(fields=['user', '-score_similarite']),
            models.Index(fields=['type_suggestion', '-score_similarite']),
        ]
    
    def __str__(self):
        return f"Suggestion {self.utilisateur_suggere.username} pour {self.user.username} ({self.score_similarite})"


# ============================================
# TRANSPAREO CONNECT - PRÉFÉRENCES NOTIFICATIONS
# ============================================

class NotificationPreference(models.Model):
    """Préférences personnalisées de notifications par utilisateur"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='notification_preferences', verbose_name="Utilisateur")
    
    # Filtres par catégorie
    filter_social = models.BooleanField(default=True, verbose_name="Réseau social")
    filter_content = models.BooleanField(default=True, verbose_name="Contenu & Posts")
    filter_messages = models.BooleanField(default=True, verbose_name="Messages")
    filter_groups = models.BooleanField(default=True, verbose_name="Groupes")
    filter_properties = models.BooleanField(default=True, verbose_name="Logements")
    filter_lease = models.BooleanField(default=True, verbose_name="Gestion bail")
    filter_security = models.BooleanField(default=True, verbose_name="Sécurité")
    filter_system = models.BooleanField(default=True, verbose_name="Système")
    
    # Filtres par importance
    filter_critical = models.BooleanField(default=True, verbose_name="Critique")
    filter_high = models.BooleanField(default=True, verbose_name="Haute")
    filter_medium = models.BooleanField(default=True, verbose_name="Moyenne")
    filter_low = models.BooleanField(default=False, verbose_name="Basse")
    
    # Filtres par type spécifique (JSON pour flexibilité)
    disabled_types = models.JSONField(default=list, blank=True, verbose_name="Types désactivés")
    
    # Canaux de notification
    enable_push = models.BooleanField(default=True, verbose_name="Notifications push navigateur")
    enable_toast = models.BooleanField(default=True, verbose_name="Notifications toast")
    enable_email = models.BooleanField(default=True, verbose_name="Notifications email")
    enable_in_app = models.BooleanField(default=True, verbose_name="Notifications in-app")
    
    # Fréquence email
    email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immédiate'),
            ('hourly', 'Résumé horaire'),
            ('daily', 'Résumé quotidien'),
            ('weekly', 'Résumé hebdomadaire'),
        ],
        default='daily',
        verbose_name="Fréquence email"
    )
    
    # Heures silencieuses (ne pas envoyer de notifications)
    quiet_hours_start = models.TimeField(blank=True, null=True, verbose_name="Début heures silencieuses")
    quiet_hours_end = models.TimeField(blank=True, null=True, verbose_name="Fin heures silencieuses")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Préférence notification"
        verbose_name_plural = "Préférences notifications"
    
    def __str__(self):
        return f"Préférences notifications - {self.user.username}"
    
    def should_notify(self, notification_type, category, importance):
        """Vérifie si une notification doit être envoyée selon les préférences"""
        # Vérifier le type désactivé
        if notification_type in self.disabled_types:
            return False
        
        # Vérifier la catégorie
        category_map = {
            'social': self.filter_social,
            'content': self.filter_content,
            'messages': self.filter_messages,
            'groups': self.filter_groups,
            'properties': self.filter_properties,
            'lease': self.filter_lease,
            'security': self.filter_security,
            'system': self.filter_system,
        }
        if not category_map.get(category, True):
            return False
        
        # Vérifier l'importance
        importance_map = {
            'critical': self.filter_critical,
            'high': self.filter_high,
            'medium': self.filter_medium,
            'low': self.filter_low,
        }
        if not importance_map.get(importance, True):
            return False
        
        return True


# ============================================
# TRANSPAREO CONNECT - VÉRIFICATIONS
# ============================================

class VerificationRequest(models.Model):
    """Demande de vérification (propriétaire ou identité)"""
    VERIFICATION_TYPES = [
        ('identity', 'Identité'),
        ('proprietaire', 'Propriétaire'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_requests')
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPES, verbose_name="Type de vérification")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    
    # Documents pour vérification propriétaire
    justificatif_propriete = models.FileField(
        upload_to='verifications/proprietaires/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Justificatif de propriété"
    )
    
    # Documents pour vérification identité
    piece_identite = models.FileField(
        upload_to='verifications/identite/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Pièce d'identité"
    )
    selfie_identite = models.ImageField(
        upload_to='verifications/identite/selfies/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Selfie avec pièce d'identité"
    )
    
    message = models.TextField(blank=True, null=True, verbose_name="Message explicatif")
    
    # Traitement admin
    reviewed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_requests',
        verbose_name="Révisé par"
    )
    admin_comment = models.TextField(blank=True, null=True, verbose_name="Commentaire administrateur")
    
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Demande de vérification"
        verbose_name_plural = "Demandes de vérification"
        indexes = [
            models.Index(fields=['user', 'verification_type', 'status']),
        ]
    
    def __str__(self):
        return f"Vérification {self.verification_type} - {self.user.username} ({self.status})"
    
    def approve(self, admin_user, comment=''):
        """Approuve la demande de vérification"""
        self.status = 'approved'
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.admin_comment = comment
        self.save()
        
        # Mettre à jour le statut de vérification de l'utilisateur
        if self.verification_type == 'proprietaire':
            self.user.proprietaire_verified = True
        elif self.verification_type == 'identity':
            self.user.identity_verified = True
        self.user.save()
    
    def reject(self, admin_user, comment):
        """Rejette la demande de vérification"""
        self.status = 'rejected'
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.admin_comment = comment
        self.save()


# ============================================
# TRANSPAREO CONNECT - BLOCAGE UTILISATEURS
# ============================================

class UserBlock(models.Model):
    """Blocage d'un utilisateur"""
    blocker = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blocked_users')
    blocked = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=200, blank=True, null=True, verbose_name="Raison")
    
    class Meta:
        unique_together = ('blocker', 'blocked')
        ordering = ['-created_at']
        verbose_name = "Blocage"
        verbose_name_plural = "Blocages"
    
    def __str__(self):
        return f"{self.blocker.username} a bloqué {self.blocked.username}"
    
    @staticmethod
    def is_blocked(blocker_user, blocked_user):
        """Vérifie si un utilisateur a bloqué un autre"""
        return UserBlock.objects.filter(blocker=blocker_user, blocked=blocked_user).exists()


# ============================================
# PHASE 11 : MODÉRATION & GESTION ADMIN
# ============================================

class SignalementPost(models.Model):
    """Signalement d'un post"""
    RAISON_CHOICES = [
        ('spam', 'Spam'),
        ('harcelement', 'Harcèlement'),
        ('arnaque', 'Arnaque/Fraude'),
        ('contenu_inapproprie', 'Contenu inapproprié'),
        ('fausse_information', 'Fausse information'),
        ('violence', 'Violence'),
        ('usurpation', 'Usurpation d\'identité'),  # Phase 12.3
        ('autre', 'Autre'),
    ]
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('traite', 'Traité'),
        ('ignore', 'Ignoré'),
    ]
    
    SEVERITE_CHOICES = [
        ('faible', 'Faible'),
        ('moyenne', 'Moyenne'),
        ('haute', 'Haute'),
        ('critique', 'Critique'),
    ]
    
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='signalements', verbose_name="Post signalé")
    signalant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='signalements_posts', verbose_name="Utilisateur signalant")
    raison = models.CharField(max_length=30, choices=RAISON_CHOICES, verbose_name="Raison")
    description = models.TextField(blank=True, verbose_name="Description supplémentaire")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    severite = models.CharField(max_length=20, choices=SEVERITE_CHOICES, default='moyenne', verbose_name="Sévérité")
    
    # Métadonnées
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    device_info = models.CharField(max_length=200, blank=True, null=True, verbose_name="Informations appareil")
    
    # Récidive
    is_recidive = models.BooleanField(default=False, verbose_name="Récidive")
    nombre_recidives = models.IntegerField(default=0, verbose_name="Nombre de récidives")
    
    traite_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='signalements_posts_traites', verbose_name="Traité par")
    traite_le = models.DateTimeField(blank=True, null=True, verbose_name="Traité le")
    commentaire_admin = models.TextField(blank=True, verbose_name="Commentaire admin")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de signalement")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Signalement de post"
        verbose_name_plural = "Signalements de posts"
        unique_together = [['post', 'signalant']]  # Un utilisateur ne peut signaler qu'une fois
        indexes = [
            models.Index(fields=['statut', '-created_at']),
            models.Index(fields=['severite', 'statut']),
            models.Index(fields=['is_recidive', '-created_at']),
        ]
    
    def __str__(self):
        return f"Signalement de {self.post.author.username} - {self.raison}"


class SignalementCommentaire(models.Model):
    """Signalement d'un commentaire"""
    RAISON_CHOICES = SignalementPost.RAISON_CHOICES
    
    STATUT_CHOICES = SignalementPost.STATUT_CHOICES
    SEVERITE_CHOICES = SignalementPost.SEVERITE_CHOICES
    
    commentaire = models.ForeignKey('PostComment', on_delete=models.CASCADE, related_name='signalements', verbose_name="Commentaire signalé")
    signalant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='signalements_commentaires', verbose_name="Utilisateur signalant")
    raison = models.CharField(max_length=30, choices=RAISON_CHOICES, verbose_name="Raison")
    description = models.TextField(blank=True, verbose_name="Description supplémentaire")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    severite = models.CharField(max_length=20, choices=SEVERITE_CHOICES, default='moyenne', verbose_name="Sévérité")
    
    # Métadonnées
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    device_info = models.CharField(max_length=200, blank=True, null=True, verbose_name="Informations appareil")
    
    # Récidive
    is_recidive = models.BooleanField(default=False, verbose_name="Récidive")
    nombre_recidives = models.IntegerField(default=0, verbose_name="Nombre de récidives")
    
    traite_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='signalements_commentaires_traites', verbose_name="Traité par")
    traite_le = models.DateTimeField(blank=True, null=True, verbose_name="Traité le")
    commentaire_admin = models.TextField(blank=True, verbose_name="Commentaire admin")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de signalement")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Signalement de commentaire"
        verbose_name_plural = "Signalements de commentaires"
        unique_together = [['commentaire', 'signalant']]
    
    def __str__(self):
        return f"Signalement de {self.commentaire.author.username} - {self.raison}"


class SignalementMessage(models.Model):
    """Signalement d'un message privé"""
    RAISON_CHOICES = [
        ('spam', 'Spam'),
        ('harcelement', 'Harcèlement'),
        ('arnaque', 'Arnaque/Fraude'),
        ('contenu_inapproprie', 'Contenu inapproprié'),
        ('menace', 'Menace'),
        ('autre', 'Autre'),
    ]
    
    STATUT_CHOICES = SignalementPost.STATUT_CHOICES
    SEVERITE_CHOICES = SignalementPost.SEVERITE_CHOICES
    
    message = models.ForeignKey('Message', on_delete=models.CASCADE, related_name='signalements', verbose_name="Message signalé")
    signalant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='signalements_messages', verbose_name="Utilisateur signalant")
    raison = models.CharField(max_length=30, choices=RAISON_CHOICES, verbose_name="Raison")
    description = models.TextField(blank=True, verbose_name="Description supplémentaire")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    severite = models.CharField(max_length=20, choices=SEVERITE_CHOICES, default='moyenne', verbose_name="Sévérité")
    
    # Métadonnées
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    device_info = models.CharField(max_length=200, blank=True, null=True, verbose_name="Informations appareil")
    
    # Récidive
    is_recidive = models.BooleanField(default=False, verbose_name="Récidive")
    nombre_recidives = models.IntegerField(default=0, verbose_name="Nombre de récidives")
    
    traite_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='signalements_messages_traites', verbose_name="Traité par")
    traite_le = models.DateTimeField(blank=True, null=True, verbose_name="Traité le")
    commentaire_admin = models.TextField(blank=True, verbose_name="Commentaire admin")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de signalement")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Signalement de message"
        verbose_name_plural = "Signalements de messages"
        unique_together = [['message', 'signalant']]
    
    def __str__(self):
        return f"Signalement de {self.message.sender.username} - {self.raison}"


class SignalementGroupe(models.Model):
    """Signalement d'un groupe"""
    RAISON_CHOICES = [
        ('contenu_inapproprie', 'Contenu inapproprié'),
        ('spam', 'Spam'),
        ('arnaque', 'Arnaque/Fraude'),
        ('hate_speech', 'Discours de haine'),
        ('autre', 'Autre'),
    ]
    
    STATUT_CHOICES = SignalementPost.STATUT_CHOICES
    
    groupe = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='signalements', verbose_name="Groupe signalé")
    signalant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='signalements_groupes', verbose_name="Utilisateur signalant")
    raison = models.CharField(max_length=30, choices=RAISON_CHOICES, verbose_name="Raison")
    description = models.TextField(blank=True, verbose_name="Description supplémentaire")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    
    traite_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='signalements_groupes_traites', verbose_name="Traité par")
    traite_le = models.DateTimeField(blank=True, null=True, verbose_name="Traité le")
    commentaire_admin = models.TextField(blank=True, verbose_name="Commentaire admin")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de signalement")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Signalement de groupe"
        verbose_name_plural = "Signalements de groupes"
        unique_together = [['groupe', 'signalant']]
    
    def __str__(self):
        return f"Signalement de {self.groupe.name} - {self.raison}"


class TicketSupport(models.Model):
    """Ticket support pour Connect"""
    CATEGORIE_CHOICES = [
        ('technique', 'Problème technique'),
        ('question', 'Question'),
        ('reclamation', 'Réclamation'),
        ('bug', 'Bug'),
        ('suggestion', 'Suggestion'),
        ('autre', 'Autre'),
    ]
    
    STATUT_CHOICES = [
        ('ouvert', 'Ouvert'),
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
        ('ferme', 'Fermé'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tickets_support', verbose_name="Utilisateur")
    sujet = models.CharField(max_length=200, verbose_name="Sujet")
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES, verbose_name="Catégorie")
    message_initial = models.TextField(verbose_name="Message initial")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ouvert', verbose_name="Statut")
    
    traite_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_traites', verbose_name="Traité par")
    resolu_le = models.DateTimeField(blank=True, null=True, verbose_name="Résolu le")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ouverture")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Ticket support"
        verbose_name_plural = "Tickets support"
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.sujet}"


class TicketSupportReponse(models.Model):
    """Réponse à un ticket support"""
    ticket = models.ForeignKey(TicketSupport, on_delete=models.CASCADE, related_name='reponses', verbose_name="Ticket")
    auteur = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reponses_tickets', verbose_name="Auteur")
    message = models.TextField(verbose_name="Message")
    est_admin = models.BooleanField(default=False, verbose_name="Réponse admin")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de réponse")
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Réponse ticket support"
        verbose_name_plural = "Réponses tickets support"
    
    def __str__(self):
        return f"Réponse #{self.id} - Ticket #{self.ticket.id}"


class JournalActivite(models.Model):
    """Journal d'activité utilisateur affichable/téléchargeable"""
    TYPE_ACTIVITE_CHOICES = [
        # Connexion/Sécurité
        ('login', 'Connexion'),
        ('logout', 'Déconnexion'),
        ('password_change', 'Changement de mot de passe'),
        ('2fa_enabled', '2FA activé'),
        ('2fa_disabled', '2FA désactivé'),
        ('email_verified', 'Email vérifié'),
        ('phone_verified', 'Téléphone vérifié'),
        # Profil
        ('profile_update', 'Mise à jour du profil'),
        ('avatar_change', 'Changement d\'avatar'),
        ('cover_change', 'Changement de couverture'),
        # Réseau social
        ('connection_request', 'Demande de connexion envoyée'),
        ('connection_accepted', 'Connexion acceptée'),
        ('connection_rejected', 'Connexion refusée'),
        ('follow', 'Abonnement à un utilisateur'),
        ('unfollow', 'Désabonnement d\'un utilisateur'),
        # Posts & Contenu
        ('post_created', 'Post créé'),
        ('post_edited', 'Post modifié'),
        ('post_deleted', 'Post supprimé'),
        ('post_liked', 'Post liké'),
        ('post_unliked', 'Post unliké'),
        ('comment_created', 'Commentaire créé'),
        ('comment_edited', 'Commentaire modifié'),
        ('comment_deleted', 'Commentaire supprimé'),
        # Messages
        ('message_sent', 'Message envoyé'),
        ('message_received', 'Message reçu'),
        ('conversation_created', 'Conversation créée'),
        # Groupes
        ('group_joined', 'Groupe rejoint'),
        ('group_left', 'Groupe quitté'),
        ('group_post_created', 'Post dans un groupe créé'),
        # Logements
        ('logement_created', 'Logement créé'),
        ('logement_updated', 'Logement modifié'),
        ('logement_deleted', 'Logement supprimé'),
        ('logement_favorited', 'Logement ajouté aux favoris'),
        ('logement_unfavorited', 'Logement retiré des favoris'),
        ('avis_posted', 'Avis posté'),
        # Baux
        ('bail_created', 'Bail créé'),
        ('bail_signed', 'Bail signé'),
        ('payment_made', 'Paiement effectué'),
        ('maintenance_request', 'Demande d\'entretien créée'),
        ('ticket_created', 'Ticket créé'),
        # Paramètres
        ('settings_updated', 'Paramètres mis à jour'),
        ('privacy_updated', 'Paramètres de confidentialité mis à jour'),
        ('notification_settings_updated', 'Paramètres de notifications mis à jour'),
        # Autre
        ('badge_earned', 'Badge obtenu'),
        ('report_submitted', 'Signalement soumis'),
        ('account_suspended', 'Compte suspendu'),
        ('account_unsuspended', 'Compte réactivé'),
        ('account_deleted', 'Compte supprimé'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='journal_activite', verbose_name="Utilisateur")
    type_activite = models.CharField(max_length=50, choices=TYPE_ACTIVITE_CHOICES, verbose_name="Type d'activité")
    description = models.TextField(verbose_name="Description")
    
    # Données supplémentaires (JSON)
    extra_data = models.JSONField(default=dict, blank=True, verbose_name="Données supplémentaires")
    
    # Informations de contexte
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    device_info = models.CharField(max_length=200, blank=True, null=True, verbose_name="Informations appareil")
    
    # Liens vers objets liés (optionnels)
    related_post = models.ForeignKey('Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_entries', verbose_name="Post lié")
    related_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_journal_entries', verbose_name="Utilisateur lié")
    related_logement = models.ForeignKey('Logement', on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_entries', verbose_name="Logement lié")
    related_group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_entries', verbose_name="Groupe lié")
    related_conversation = models.ForeignKey('Conversation', on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_entries', verbose_name="Conversation liée")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de l'activité")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Entrée journal d'activité"
        verbose_name_plural = "Journal d'activité"
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'type_activite', '-created_at']),
            models.Index(fields=['type_activite', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_type_activite_display()} - {self.created_at}"


class AdminLog(models.Model):
    """Logs complets des actions admin avec métadonnées"""
    ACTION_CHOICES = [
        # Modération
        ('moderation_post_approved', 'Post approuvé'),
        ('moderation_post_rejected', 'Post rejeté'),
        ('moderation_post_deleted', 'Post supprimé'),
        ('moderation_comment_approved', 'Commentaire approuvé'),
        ('moderation_comment_rejected', 'Commentaire rejeté'),
        ('moderation_comment_deleted', 'Commentaire supprimé'),
        ('moderation_message_rejected', 'Message rejeté'),
        ('moderation_group_approved', 'Groupe approuvé'),
        ('moderation_group_rejected', 'Groupe rejeté'),
        # Utilisateurs
        ('user_suspended', 'Utilisateur suspendu'),
        ('user_unsuspended', 'Utilisateur réactivé'),
        ('user_banned', 'Utilisateur banni'),
        ('user_unbanned', 'Utilisateur débanni'),
        ('user_deleted', 'Utilisateur supprimé'),
        ('user_badges_revoked', 'Badges révoqués'),
        # Vérifications
        ('verification_approved', 'Vérification approuvée'),
        ('verification_rejected', 'Vérification rejetée'),
        # Actions batch
        ('batch_ban', 'Bannissement en lot'),
        ('batch_suspend', 'Suspension en lot'),
        ('batch_delete', 'Suppression en lot'),
        ('batch_severity_update', 'Mise à jour sévérité en lot'),
        # Autre
        ('settings_updated', 'Paramètres mis à jour'),
        ('export_data', 'Export de données'),
    ]
    
    admin_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='admin_logs', verbose_name="Admin")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name="Action")
    description = models.TextField(verbose_name="Description")
    
    # Objets concernés
    target_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_actions_received', verbose_name="Utilisateur cible")
    target_post = models.ForeignKey('Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_logs', verbose_name="Post cible")
    target_comment = models.ForeignKey('PostComment', on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_logs', verbose_name="Commentaire cible")
    target_group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_logs', verbose_name="Groupe cible")
    
    # Métadonnées complètes
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    device_info = models.CharField(max_length=200, blank=True, null=True, verbose_name="Informations appareil")
    browser = models.CharField(max_length=100, blank=True, null=True, verbose_name="Navigateur")
    os = models.CharField(max_length=100, blank=True, null=True, verbose_name="Système d'exploitation")
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name="Localisation")
    
    # Données supplémentaires (JSON)
    extra_data = models.JSONField(default=dict, blank=True, verbose_name="Données supplémentaires")
    
    # Tentatives d'accès suspectes
    is_suspicious = models.BooleanField(default=False, verbose_name="Suspect")
    suspicious_reason = models.CharField(max_length=200, blank=True, null=True, verbose_name="Raison suspecte")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de l'action")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Log admin"
        verbose_name_plural = "Logs admin"
        indexes = [
            models.Index(fields=['admin_user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['target_user', '-created_at']),
            models.Index(fields=['is_suspicious', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.get_action_display()} - {self.created_at}"


# ============================================
# BUSINESS MODEL CANVAS
# ============================================

class BusinessModelCanvas(models.Model):
    """Business Model Canvas principal"""
    
    # Version actuelle
    version = models.IntegerField(default=1, verbose_name="Version")
    
    # Les 9 blocs du canvas
    partenaires_cles = models.TextField(blank=True, null=True, verbose_name="Partenaires clés", 
                                         help_text="Agences immobilières, notaires, assureurs, banques...")
    activites_cles = models.TextField(blank=True, null=True, verbose_name="Activités clés",
                                      help_text="Plateforme de mise en relation, vérification profils, gestion contrats...")
    ressources_cles = models.TextField(blank=True, null=True, verbose_name="Ressources clés",
                                       help_text="Équipe tech, base de données logements, algorithme matching...")
    proposition_valeur = models.TextField(blank=True, null=True, verbose_name="Proposition de valeur",
                                          help_text="Location transparente avec avis vérifiés, réseau social immobilier...")
    relations_clients = models.TextField(blank=True, null=True, verbose_name="Relations clients",
                                         help_text="Self-service, communauté, support personnalisé...")
    canaux = models.TextField(blank=True, null=True, verbose_name="Canaux",
                              help_text="Site web, app mobile, réseaux sociaux, partenariats...")
    segments_clients = models.TextField(blank=True, null=True, verbose_name="Segments clients",
                                        help_text="Locataires 20-40 ans, propriétaires particuliers, entreprises...")
    structure_couts = models.TextField(blank=True, null=True, verbose_name="Structure de coûts",
                                       help_text="Développement, serveurs, marketing, salaires, support...")
    flux_revenus = models.TextField(blank=True, null=True, verbose_name="Flux de revenus",
                                    help_text="Abonnements premium, commissions, services additionnels...")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='canvas_created', verbose_name="Créé par")
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='canvas_updated', verbose_name="Modifié par")
    
    # Lien de partage (readonly)
    share_token = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="Token de partage")
    share_enabled = models.BooleanField(default=False, verbose_name="Partage activé")
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Business Model Canvas"
        verbose_name_plural = "Business Model Canvas"
    
    def __str__(self):
        return f"Business Model Canvas v{self.version} - {self.updated_at.strftime('%d/%m/%Y')}"
    
    def create_version(self, user=None):
        """Créer une version snapshot du canvas"""
        BusinessModelCanvasVersion.objects.create(
            canvas=self,
            version=self.version,
            partenaires_cles=self.partenaires_cles,
            activites_cles=self.activites_cles,
            ressources_cles=self.ressources_cles,
            proposition_valeur=self.proposition_valeur,
            relations_clients=self.relations_clients,
            canaux=self.canaux,
            segments_clients=self.segments_clients,
            structure_couts=self.structure_couts,
            flux_revenus=self.flux_revenus,
            created_by=user
        )


class BusinessModelCanvasVersion(models.Model):
    """Historique des versions du Business Model Canvas"""
    
    canvas = models.ForeignKey(BusinessModelCanvas, on_delete=models.CASCADE, related_name='versions',
                               verbose_name="Canvas")
    version = models.IntegerField(verbose_name="Version")
    
    # Les 9 blocs du canvas (snapshot)
    partenaires_cles = models.TextField(blank=True, null=True)
    activites_cles = models.TextField(blank=True, null=True)
    ressources_cles = models.TextField(blank=True, null=True)
    proposition_valeur = models.TextField(blank=True, null=True)
    relations_clients = models.TextField(blank=True, null=True)
    canaux = models.TextField(blank=True, null=True)
    segments_clients = models.TextField(blank=True, null=True)
    structure_couts = models.TextField(blank=True, null=True)
    flux_revenus = models.TextField(blank=True, null=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name="Créé par")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Version du Canvas"
        verbose_name_plural = "Versions du Canvas"
        unique_together = ['canvas', 'version']
    
    def __str__(self):
        return f"Version {self.version} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"


# ============================================
# BUSINESS PLAN
# ============================================

class BusinessPlan(models.Model):
    """Business Plan complet avec toutes les sections"""
    
    # Version actuelle
    version = models.IntegerField(default=1, verbose_name="Version")
    
    # ========== SECTION 1 - RÉSUMÉ EXÉCUTIF ==========
    vision = models.TextField(blank=True, null=True, verbose_name="Vision")
    mission = models.TextField(blank=True, null=True, verbose_name="Mission")
    objectifs_1_an = models.JSONField(default=list, blank=True, verbose_name="Objectifs 1 an")
    objectifs_3_ans = models.JSONField(default=list, blank=True, verbose_name="Objectifs 3 ans")
    investissement_requis = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Investissement requis (€)")
    roi_prevu = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Retour sur investissement prévu (%)")
    
    # ========== SECTION 2 - PRÉSENTATION ENTREPRISE ==========
    nom_entreprise = models.CharField(max_length=200, default="Transpareo", verbose_name="Nom entreprise")
    date_creation = models.DateField(null=True, blank=True, verbose_name="Date de création")
    forme_juridique = models.CharField(
        max_length=50,
        choices=[
            ('SAS', 'SAS - Société par Actions Simplifiée'),
            ('SARL', 'SARL - Société à Responsabilité Limitée'),
            ('SA', 'SA - Société Anonyme'),
            ('EURL', 'EURL - Entreprise Unipersonnelle à Responsabilité Limitée'),
            ('SASU', 'SASU - Société par Actions Simplifiée Unipersonnelle'),
            ('SCI', 'SCI - Société Civile Immobilière'),
        ],
        default='SAS',
        verbose_name="Forme juridique"
    )
    capital_social = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Capital social (€)")
    siege_social = models.TextField(blank=True, null=True, verbose_name="Siège social")
    equipe_fondatrice = models.JSONField(default=list, blank=True, verbose_name="Équipe fondatrice (nom, rôle, bio)")
    histoire_genese = models.TextField(blank=True, null=True, verbose_name="Histoire et genèse")
    
    # ========== SECTION 3 - ÉTUDE DE MARCHÉ ==========
    # A. Marché cible
    taille_marche = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Taille du marché")
    unite_marche = models.CharField(max_length=50, default="€", blank=True, verbose_name="Unité marché")
    croissance_annuelle = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Croissance annuelle (%)")
    tendances_marche = models.TextField(blank=True, null=True, verbose_name="Tendances marché")
    
    # B. Segments clients (tableau)
    segments_clients = models.JSONField(default=list, blank=True, verbose_name="Segments clients (tableau)")
    
    # C. Données marché (JSON pour flexibilité)
    donnees_marche = models.JSONField(default=dict, blank=True, verbose_name="Données marché")
    
    # ========== SECTION 4 - STRATÉGIE MARKETING ==========
    # Produit
    fonctionnalites_principales = models.JSONField(default=list, blank=True, verbose_name="Fonctionnalités principales")
    proposition_valeur_unique = models.TextField(blank=True, null=True, verbose_name="Proposition de valeur unique")
    roadmap_produit = models.JSONField(default=list, blank=True, verbose_name="Roadmap produit")
    
    # Prix
    grille_tarifaire = models.JSONField(default=list, blank=True, verbose_name="Grille tarifaire")
    strategie_pricing = models.CharField(
        max_length=50,
        choices=[
            ('freemium', 'Freemium'),
            ('abonnement', 'Abonnement'),
            ('commission', 'Commission'),
            ('licence', 'Licence'),
            ('hybride', 'Hybride'),
        ],
        default='freemium',
        verbose_name="Stratégie pricing"
    )
    positionnement_prix = models.CharField(max_length=100, blank=True, null=True, verbose_name="Positionnement prix")
    
    # Place
    canaux_distribution = models.JSONField(default=list, blank=True, verbose_name="Canaux distribution")
    couverture_geographique = models.JSONField(default=list, blank=True, verbose_name="Couverture géographique")
    plan_expansion = models.TextField(blank=True, null=True, verbose_name="Plan expansion")
    
    # Promotion
    canaux_marketing = models.JSONField(default=list, blank=True, verbose_name="Canaux marketing")
    budget_marketing_annuel = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Budget marketing annuel (€)")
    actions_marketing = models.JSONField(default=list, blank=True, verbose_name="Actions marketing prévues")
    
    # ========== SECTION 5 - PLAN OPÉRATIONNEL ==========
    infrastructure_technique = models.TextField(blank=True, null=True, verbose_name="Infrastructure technique")
    equipe_recrutements = models.JSONField(default=list, blank=True, verbose_name="Équipe et recrutements (tableau)")
    processus_cles = models.JSONField(default=list, blank=True, verbose_name="Processus clés")
    partenaires_operationnels = models.JSONField(default=list, blank=True, verbose_name="Partenaires opérationnels")
    outils_technologies = models.JSONField(default=list, blank=True, verbose_name="Outils et technologies")
    
    # ========== SECTION 6 - PROJECTIONS FINANCIÈRES ==========
    compte_resultat = models.JSONField(default=dict, blank=True, verbose_name="Compte de résultat prévisionnel")
    tableau_tresorerie = models.JSONField(default=dict, blank=True, verbose_name="Tableau de flux de trésorerie")
    bilans_previsionnels = models.JSONField(default=dict, blank=True, verbose_name="Bilans prévisionnels")
    indicateurs_cles = models.JSONField(default=dict, blank=True, verbose_name="Indicateurs clés")
    
    # ========== SECTION 7 - ANALYSE SWOT ==========
    forces = models.JSONField(default=list, blank=True, verbose_name="Forces (Strengths)")
    faiblesses = models.JSONField(default=list, blank=True, verbose_name="Faiblesses (Weaknesses)")
    opportunites = models.JSONField(default=list, blank=True, verbose_name="Opportunités (Opportunities)")
    menaces = models.JSONField(default=list, blank=True, verbose_name="Menaces (Threats)")
    
    # ========== SECTION 8 - ANNEXES ==========
    # Les documents seront gérés via un modèle séparé ou FileField multiple
    annexes_data = models.JSONField(default=dict, blank=True, verbose_name="Données annexes")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='business_plans_created', verbose_name="Créé par")
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='business_plans_updated', verbose_name="Modifié par")
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Business Plan"
        verbose_name_plural = "Business Plans"
    
    def __str__(self):
        return f"Business Plan v{self.version} - {self.updated_at.strftime('%d/%m/%Y')}"
    
    def create_version(self, user=None):
        """Créer une version snapshot du business plan"""
        BusinessPlanVersion.objects.create(
            plan=self,
            version=self.version,
            vision=self.vision,
            mission=self.mission,
            objectifs_1_an=self.objectifs_1_an,
            objectifs_3_ans=self.objectifs_3_ans,
            investissement_requis=self.investissement_requis,
            roi_prevu=self.roi_prevu,
            nom_entreprise=self.nom_entreprise,
            date_creation=self.date_creation,
            forme_juridique=self.forme_juridique,
            capital_social=self.capital_social,
            siege_social=self.siege_social,
            equipe_fondatrice=self.equipe_fondatrice,
            histoire_genese=self.histoire_genese,
            taille_marche=self.taille_marche,
            unite_marche=self.unite_marche,
            croissance_annuelle=self.croissance_annuelle,
            tendances_marche=self.tendances_marche,
            segments_clients=self.segments_clients,
            donnees_marche=self.donnees_marche,
            fonctionnalites_principales=self.fonctionnalites_principales,
            proposition_valeur_unique=self.proposition_valeur_unique,
            roadmap_produit=self.roadmap_produit,
            grille_tarifaire=self.grille_tarifaire,
            strategie_pricing=self.strategie_pricing,
            positionnement_prix=self.positionnement_prix,
            canaux_distribution=self.canaux_distribution,
            couverture_geographique=self.couverture_geographique,
            plan_expansion=self.plan_expansion,
            canaux_marketing=self.canaux_marketing,
            budget_marketing_annuel=self.budget_marketing_annuel,
            actions_marketing=self.actions_marketing,
            infrastructure_technique=self.infrastructure_technique,
            equipe_recrutements=self.equipe_recrutements,
            processus_cles=self.processus_cles,
            partenaires_operationnels=self.partenaires_operationnels,
            outils_technologies=self.outils_technologies,
            compte_resultat=self.compte_resultat,
            tableau_tresorerie=self.tableau_tresorerie,
            bilans_previsionnels=self.bilans_previsionnels,
            indicateurs_cles=self.indicateurs_cles,
            forces=self.forces,
            faiblesses=self.faiblesses,
            opportunites=self.opportunites,
            menaces=self.menaces,
            annexes_data=self.annexes_data,
            created_by=user
        )


class BusinessPlanVersion(models.Model):
    """Historique des versions du Business Plan"""
    
    plan = models.ForeignKey(BusinessPlan, on_delete=models.CASCADE, related_name='versions',
                            verbose_name="Business Plan")
    version = models.IntegerField(verbose_name="Version")
    
    # Toutes les données (snapshot) - structure identique à BusinessPlan
    vision = models.TextField(blank=True, null=True)
    mission = models.TextField(blank=True, null=True)
    objectifs_1_an = models.JSONField(default=list, blank=True)
    objectifs_3_ans = models.JSONField(default=list, blank=True)
    investissement_requis = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    roi_prevu = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    nom_entreprise = models.CharField(max_length=200, default="Transpareo")
    date_creation = models.DateField(null=True, blank=True)
    forme_juridique = models.CharField(max_length=50, default='SAS')
    capital_social = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    siege_social = models.TextField(blank=True, null=True)
    equipe_fondatrice = models.JSONField(default=list, blank=True)
    histoire_genese = models.TextField(blank=True, null=True)
    taille_marche = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    unite_marche = models.CharField(max_length=50, default="€", blank=True)
    croissance_annuelle = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tendances_marche = models.TextField(blank=True, null=True)
    segments_clients = models.JSONField(default=list, blank=True)
    donnees_marche = models.JSONField(default=dict, blank=True)
    fonctionnalites_principales = models.JSONField(default=list, blank=True)
    proposition_valeur_unique = models.TextField(blank=True, null=True)
    roadmap_produit = models.JSONField(default=list, blank=True)
    grille_tarifaire = models.JSONField(default=list, blank=True)
    strategie_pricing = models.CharField(max_length=50, default='freemium')
    positionnement_prix = models.CharField(max_length=100, blank=True, null=True)
    canaux_distribution = models.JSONField(default=list, blank=True)
    couverture_geographique = models.JSONField(default=list, blank=True)
    plan_expansion = models.TextField(blank=True, null=True)
    canaux_marketing = models.JSONField(default=list, blank=True)
    budget_marketing_annuel = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actions_marketing = models.JSONField(default=list, blank=True)
    infrastructure_technique = models.TextField(blank=True, null=True)
    equipe_recrutements = models.JSONField(default=list, blank=True)
    processus_cles = models.JSONField(default=list, blank=True)
    partenaires_operationnels = models.JSONField(default=list, blank=True)
    outils_technologies = models.JSONField(default=list, blank=True)
    compte_resultat = models.JSONField(default=dict, blank=True)
    tableau_tresorerie = models.JSONField(default=dict, blank=True)
    bilans_previsionnels = models.JSONField(default=dict, blank=True)
    indicateurs_cles = models.JSONField(default=dict, blank=True)
    forces = models.JSONField(default=list, blank=True)
    faiblesses = models.JSONField(default=list, blank=True)
    opportunites = models.JSONField(default=list, blank=True)
    menaces = models.JSONField(default=list, blank=True)
    annexes_data = models.JSONField(default=dict, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name="Créé par")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Version du Business Plan"
        verbose_name_plural = "Versions du Business Plan"
        unique_together = ['plan', 'version']
    
    def __str__(self):
        return f"Business Plan v{self.version} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class BusinessPlanDocument(models.Model):
    """Documents annexes du Business Plan"""
    
    plan = models.ForeignKey(BusinessPlan, on_delete=models.CASCADE, related_name='documents',
                             verbose_name="Business Plan")
    title = models.CharField(max_length=200, verbose_name="Titre")
    document = models.FileField(upload_to='business_plan/annexes/', verbose_name="Document")
    document_type = models.CharField(
        max_length=50,
        choices=[
            ('etude_marche', 'Étude de marché'),
            ('contrat', 'Contrat partenaire'),
            ('lettre_intention', 'Lettre d\'intention'),
            ('brevet', 'Brevet/Marque'),
            ('autre', 'Autre'),
        ],
        default='autre',
        verbose_name="Type de document"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'upload")
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name="Uploadé par")
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Document annexe"
        verbose_name_plural = "Documents annexes"
    
    def __str__(self):
        return f"{self.title} - {self.plan}"


class BusinessPlanComment(models.Model):
    """Commentaires par section du Business Plan"""
    
    plan = models.ForeignKey(BusinessPlan, on_delete=models.CASCADE, related_name='comments',
                            verbose_name="Business Plan")
    section = models.CharField(max_length=100, verbose_name="Section")
    comment = models.TextField(verbose_name="Commentaire")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name="Auteur")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
    
    def __str__(self):
        return f"Commentaire sur {self.section} - {self.created_at.strftime('%d/%m/%Y')}"


# ============================================
# ÉTUDES DE MARCHÉ & FORMS
# ============================================

class MarketStudy(models.Model):
    """Étude de marché avec questionnaire"""
    
    title = models.CharField(max_length=200, verbose_name="Titre de l'étude")
    description = models.TextField(blank=True, null=True, verbose_name="Description/contexte")
    
    # Dates
    date_start = models.DateField(null=True, blank=True, verbose_name="Date de début")
    date_end = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    
    # Statut
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Brouillon'),
            ('active', 'En cours'),
            ('completed', 'Terminée'),
            ('archived', 'Archivée'),
        ],
        default='draft',
        verbose_name="Statut"
    )
    
    # Cible
    target_type = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public - Accessible à tous'),
            ('private', 'Privé - Lien uniquement'),
            ('shareable', 'Partageable - Lien avec token'),
        ],
        default='public',
        verbose_name="Type de cible"
    )
    
    # Partage
    share_token = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="Token de partage")
    
    # Design du form
    theme_color = models.CharField(max_length=7, default='#D3580B', verbose_name="Couleur du thème")
    logo = models.ImageField(upload_to='market_studies/logos/', blank=True, null=True, verbose_name="Logo")
    completion_message = models.TextField(default="Merci pour votre participation !", verbose_name="Message de fin")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='market_studies_created', verbose_name="Créé par")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Étude de marché"
        verbose_name_plural = "Études de marché"
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def get_responses_count(self):
        """Retourne le nombre de réponses collectées"""
        return MarketStudyResponse.objects.filter(study=self).count()
    
    def get_completion_rate(self):
        """Calcule le taux de complétion"""
        total_responses = self.get_responses_count()
        completed_responses = MarketStudyResponse.objects.filter(study=self, completed=True).count()
        if total_responses == 0:
            return 0
        return round((completed_responses / total_responses) * 100, 1)
    
    def get_average_duration(self):
        """Calcule la durée moyenne de complétion en minutes"""
        completed_responses = MarketStudyResponse.objects.filter(
            study=self,
            completed=True,
            started_at__isnull=False,
            completed_at__isnull=False
        )
        if not completed_responses.exists():
            return 0
        
        total_duration = 0
        count = 0
        for response in completed_responses:
            duration = (response.completed_at - response.started_at).total_seconds() / 60
            total_duration += duration
            count += 1
        
        return round(total_duration / count, 1) if count > 0 else 0


class MarketStudyQuestion(models.Model):
    """Question d'une étude de marché"""
    
    study = models.ForeignKey(MarketStudy, on_delete=models.CASCADE, related_name='questions',
                             verbose_name="Étude")
    order = models.IntegerField(default=0, verbose_name="Ordre")
    
    # Type de question
    question_type = models.CharField(
        max_length=50,
        choices=[
            ('text_short', 'Texte court (input)'),
            ('text_long', 'Texte long (textarea)'),
            ('single_choice', 'Choix unique (radio)'),
            ('multiple_choice', 'Choix multiple (checkboxes)'),
            ('scale', 'Échelle (1-5, 1-10)'),
            ('nps', 'NPS (Net Promoter Score)'),
            ('date', 'Date'),
            ('file', 'Fichier upload'),
        ],
        verbose_name="Type de question"
    )
    
    # Contenu
    label = models.CharField(max_length=500, verbose_name="Libellé de la question")
    description = models.TextField(blank=True, null=True, verbose_name="Description/aide")
    required = models.BooleanField(default=True, verbose_name="Obligatoire")
    
    # Options pour les questions à choix
    options = models.JSONField(default=list, blank=True, verbose_name="Options de réponse")
    
    # Paramètres spécifiques
    scale_min = models.IntegerField(default=1, verbose_name="Échelle min")
    scale_max = models.IntegerField(default=5, verbose_name="Échelle max")
    scale_label_min = models.CharField(max_length=100, blank=True, null=True, verbose_name="Label échelle min")
    scale_label_max = models.CharField(max_length=100, blank=True, null=True, verbose_name="Label échelle max")
    
    # Logique conditionnelle
    conditional_logic = models.JSONField(default=dict, blank=True, verbose_name="Logique conditionnelle")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Question"
        verbose_name_plural = "Questions"
    
    def __str__(self):
        return f"{self.label} ({self.get_question_type_display()})"


class MarketStudyResponse(models.Model):
    """Réponse d'un utilisateur à une étude de marché"""
    
    study = models.ForeignKey(MarketStudy, on_delete=models.CASCADE, related_name='responses',
                             verbose_name="Étude")
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                            related_name='market_study_responses', verbose_name="Utilisateur")
    
    # Statut
    completed = models.BooleanField(default=False, verbose_name="Complétée")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de début")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    
    # Métadonnées
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"
    
    def __str__(self):
        return f"Réponse à {self.study.title} - {self.created_at.strftime('%d/%m/%Y')}"
    
    def get_duration_minutes(self):
        """Calcule la durée de complétion en minutes"""
        if self.started_at and self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds() / 60
            return round(duration, 1)
        return None


class MarketStudyAnswer(models.Model):
    """Réponse à une question spécifique"""
    
    response = models.ForeignKey(MarketStudyResponse, on_delete=models.CASCADE, related_name='answers',
                                verbose_name="Réponse")
    question = models.ForeignKey(MarketStudyQuestion, on_delete=models.CASCADE, related_name='answers',
                                verbose_name="Question")
    
    # Réponse (JSON pour flexibilité selon le type de question)
    answer_value = models.JSONField(verbose_name="Valeur de la réponse")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        ordering = ['question__order', 'created_at']
        verbose_name = "Réponse à une question"
        verbose_name_plural = "Réponses aux questions"
        unique_together = ['response', 'question']
    
    def __str__(self):
        return f"Réponse: {self.answer_value} - Question: {self.question.label}"
    
    def get_answer_display(self):
        """Retourne la réponse formatée pour l'affichage"""
        if isinstance(self.answer_value, list):
            return ', '.join(str(v) for v in self.answer_value)
        return str(self.answer_value)


# ============================================
# ANALYSE CONCURRENTIELLE - PHASE 7
# ============================================

class Competitor(models.Model):
    """Concurrent pour l'analyse concurrentielle"""
    
    # Général
    logo = models.ImageField(upload_to='competitors/logos/', blank=True, null=True, verbose_name="Logo")
    name = models.CharField(max_length=200, verbose_name="Nom")
    website = models.URLField(blank=True, null=True, verbose_name="Site web")
    year_founded = models.IntegerField(null=True, blank=True, verbose_name="Année de création")
    funding_raised = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Levée de fonds (€)")
    estimated_users = models.IntegerField(null=True, blank=True, verbose_name="Nombre d'utilisateurs (estimé)")
    
    # Fonctionnalités
    feature_search = models.CharField(
        max_length=20,
        choices=[('yes', 'Oui'), ('no', 'Non'), ('partial', 'Partiel')],
        default='no',
        verbose_name="Recherche logements"
    )
    feature_verified_reviews = models.BooleanField(default=False, verbose_name="Avis vérifiés")
    feature_social_network = models.BooleanField(default=False, verbose_name="Réseau social")
    feature_lease_management = models.BooleanField(default=False, verbose_name="Gestion bail")
    feature_interactive_map = models.BooleanField(default=False, verbose_name="Carte interactive")
    feature_mobile_app = models.BooleanField(default=False, verbose_name="Application mobile")
    custom_features = models.JSONField(default=list, blank=True, verbose_name="Autres fonctionnalités custom")
    
    # Tarification
    pricing_model = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Gratuit'),
            ('freemium', 'Freemium'),
            ('paid', 'Payant'),
            ('commission', 'Commission'),
            ('mixed', 'Mixte'),
        ],
        default='free',
        verbose_name="Modèle tarifaire"
    )
    average_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix moyen (€)")
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Commission (%)")
    
    # UX/UI
    design_score = models.IntegerField(null=True, blank=True, verbose_name="Note design (/10)")
    mobile_friendly = models.BooleanField(default=False, verbose_name="Mobile-friendly")
    speed_score = models.IntegerField(null=True, blank=True, verbose_name="Note rapidité (/10)")
    
    # Marketing
    social_media_score = models.IntegerField(null=True, blank=True, verbose_name="Présence réseaux sociaux (/10)")
    seo_score = models.IntegerField(null=True, blank=True, verbose_name="SEO (/10)")
    advertising_type = models.CharField(max_length=200, blank=True, null=True, verbose_name="Type de publicité")
    
    # Points forts/faibles
    strengths = models.TextField(blank=True, null=True, verbose_name="Points forts")
    weaknesses = models.TextField(blank=True, null=True, verbose_name="Points faibles")
    
    # Notes libres
    notes = models.TextField(blank=True, null=True, verbose_name="Notes libres")
    
    # Métadonnées
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='competitors_created', verbose_name="Créé par")
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Concurrent"
        verbose_name_plural = "Concurrents"
    
    def __str__(self):
        return self.name
    
    def get_funding_display(self):
        """Retourne la levée de fonds formatée"""
        if self.funding_raised:
            if self.funding_raised >= 1000000:
                return f"{self.funding_raised / 1000000:.1f}M€"
            elif self.funding_raised >= 1000:
                return f"{self.funding_raised / 1000:.0f}K€"
            return f"{self.funding_raised:.0f}€"
        return "-"


class CompetitiveAnalysis(models.Model):
    """Analyse SWOT comparée et insights"""
    
    # SWOT Comparée
    our_strengths_vs_competitors = models.TextField(blank=True, null=True, verbose_name="Nos forces vs concurrents")
    their_strengths_to_adopt = models.TextField(blank=True, null=True, verbose_name="Leurs forces à adopter")
    market_opportunities = models.TextField(blank=True, null=True, verbose_name="Opportunités marché")
    competitive_threats = models.TextField(blank=True, null=True, verbose_name="Menaces concurrentielles")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='competitive_analyses_updated', verbose_name="Modifié par")
    
    class Meta:
        verbose_name = "Analyse SWOT Comparée"
        verbose_name_plural = "Analyses SWOT Comparées"
    
    def __str__(self):
        return f"Analyse SWOT - {self.updated_at.strftime('%d/%m/%Y')}"
    
    @classmethod
    def get_or_create_singleton(cls):
        """Récupère ou crée l'analyse unique"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


# ============================================
# PROJECTIONS FINANCIÈRES AVANCÉES - PHASE 8
# ============================================

class FinancialProjection(models.Model):
    """Projection financière principale (3 ans)"""
    
    # Revenus (par année)
    revenue_subscriptions_tenants = models.JSONField(default=dict, blank=True, verbose_name="Revenus abonnements locataires")
    revenue_subscriptions_owners = models.JSONField(default=dict, blank=True, verbose_name="Revenus abonnements propriétaires")
    revenue_subscriptions_companies = models.JSONField(default=dict, blank=True, verbose_name="Revenus abonnements entreprises")
    revenue_commissions_leases = models.JSONField(default=dict, blank=True, verbose_name="Commissions locations")
    revenue_additional_services = models.JSONField(default=dict, blank=True, verbose_name="Services additionnels")
    total_revenue = models.JSONField(default=dict, blank=True, verbose_name="Total revenus")
    
    # Charges variables (par année)
    variable_cost_payment_commissions = models.DecimalField(max_digits=5, decimal_places=2, default=2.0, verbose_name="% commissions paiement")
    variable_cost_support = models.JSONField(default=dict, blank=True, verbose_name="Coûts support client")
    variable_cost_marketing = models.JSONField(default=dict, blank=True, verbose_name="Marketing variable")
    total_variable_costs = models.JSONField(default=dict, blank=True, verbose_name="Total charges variables")
    
    # Charges fixes (par année)
    fixed_cost_salaries = models.JSONField(default=dict, blank=True, verbose_name="Salaires équipe")
    fixed_cost_rent = models.JSONField(default=dict, blank=True, verbose_name="Loyer bureaux")
    fixed_cost_infrastructure = models.JSONField(default=dict, blank=True, verbose_name="Serveurs et infrastructure")
    fixed_cost_marketing = models.JSONField(default=dict, blank=True, verbose_name="Marketing fixe")
    fixed_cost_insurance_legal = models.JSONField(default=dict, blank=True, verbose_name="Assurances et juridique")
    fixed_cost_other = models.JSONField(default=dict, blank=True, verbose_name="Autres charges fixes")
    total_fixed_costs = models.JSONField(default=dict, blank=True, verbose_name="Total charges fixes")
    
    # Résultats (calculés)
    gross_margin = models.JSONField(default=dict, blank=True, verbose_name="Marge brute")
    ebitda = models.JSONField(default=dict, blank=True, verbose_name="EBITDA")
    net_result = models.JSONField(default=dict, blank=True, verbose_name="Résultat net")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='financial_projections_updated', verbose_name="Modifié par")
    
    class Meta:
        verbose_name = "Projection Financière"
        verbose_name_plural = "Projections Financières"
    
    def __str__(self):
        return f"Projection Financière - {self.updated_at.strftime('%d/%m/%Y')}"
    
    @classmethod
    def get_or_create_singleton(cls):
        """Récupère ou crée la projection unique"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class CashFlow(models.Model):
    """Flux de trésorerie mensuel (année 1)"""
    
    # Mois (1-12)
    month = models.IntegerField(verbose_name="Mois")
    year = models.IntegerField(default=1, verbose_name="Année")
    
    # Encaissements
    inflows_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Ventes")
    inflows_funding = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Levées de fonds")
    inflows_loans = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Prêts")
    total_inflows = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total entrées")
    
    # Décaissements
    outflows_purchases_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Achats et charges")
    outflows_investments = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Investissements")
    outflows_loan_repayments = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Remboursements prêts")
    total_outflows = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total sorties")
    
    # Trésorerie
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Solde initial")
    variation = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Variation")
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Solde final")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        ordering = ['year', 'month']
        unique_together = ['month', 'year']
        verbose_name = "Flux de Trésorerie"
        verbose_name_plural = "Flux de Trésorerie"
    
    def __str__(self):
        return f"Trésorerie - {self.month}/{self.year}"


class BalanceSheet(models.Model):
    """Bilan prévisionnel (3 ans)"""
    
    year = models.IntegerField(verbose_name="Année")
    
    # Actif
    assets_fixed_assets = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Immobilisations")
    assets_receivables = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Créances clients")
    assets_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Trésorerie")
    total_assets = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total actif")
    
    # Passif
    liabilities_share_capital = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Capital social")
    liabilities_reserves = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Réserves")
    liabilities_financial_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Dettes financières")
    liabilities_trade_payables = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Dettes fournisseurs")
    total_liabilities = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total passif")
    
    # Vérification équilibre
    balance_check = models.BooleanField(default=True, verbose_name="Équilibre vérifié (Actif = Passif)")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        ordering = ['year']
        unique_together = ['year']
        verbose_name = "Bilan Prévisionnel"
        verbose_name_plural = "Bilans Prévisionnels"
    
    def __str__(self):
        return f"Bilan - Année {self.year}"
    
    def check_balance(self):
        """Vérifie que Actif = Passif"""
        self.total_assets = self.assets_fixed_assets + self.assets_receivables + self.assets_cash
        self.total_liabilities = self.liabilities_share_capital + self.liabilities_reserves + self.liabilities_financial_debt + self.liabilities_trade_payables
        self.balance_check = abs(float(self.total_assets) - float(self.total_liabilities)) < 0.01
        return self.balance_check


class FinancialScenario(models.Model):
    """Scénario financier (pessimiste, réaliste, optimiste)"""
    
    name = models.CharField(max_length=50, choices=[
        ('pessimistic', 'Pessimiste'),
        ('realistic', 'Réaliste'),
        ('optimistic', 'Optimiste'),
    ], verbose_name="Nom du scénario")
    
    # Paramètres
    revenue_growth_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Taux croissance CA (%)")
    conversion_rate_tenants = models.DecimalField(max_digits=5, decimal_places=2, default=5.0, verbose_name="Taux conversion locataires (%)")
    conversion_rate_owners = models.DecimalField(max_digits=5, decimal_places=2, default=3.0, verbose_name="Taux conversion propriétaires (%)")
    avg_subscription_price = models.DecimalField(max_digits=10, decimal_places=2, default=20.0, verbose_name="Prix moyen abonnement (€)")
    cac = models.DecimalField(max_digits=10, decimal_places=2, default=50.0, verbose_name="Coût acquisition client (€)")
    ltv = models.DecimalField(max_digits=10, decimal_places=2, default=200.0, verbose_name="Lifetime Value (€)")
    cost_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name="Multiplicateur coûts")
    
    # Utilisateurs mois 12
    users_month_12 = models.IntegerField(default=10000, verbose_name="Nombre utilisateurs mois 12")
    
    # Projections calculées (JSON)
    projected_revenue = models.JSONField(default=dict, blank=True, verbose_name="Revenus projetés")
    projected_costs = models.JSONField(default=dict, blank=True, verbose_name="Coûts projetés")
    projected_result = models.JSONField(default=dict, blank=True, verbose_name="Résultat projeté")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Scénario Financier"
        verbose_name_plural = "Scénarios Financiers"
    
    def __str__(self):
        return f"Scénario {self.get_name_display()}"


class FinancialKPI(models.Model):
    """Indicateurs clés financiers (KPIs)"""
    
    # CAC (Coût Acquisition Client)
    cac_current = models.DecimalField(max_digits=10, decimal_places=2, default=50.0, verbose_name="CAC actuel (€)")
    cac_history = models.JSONField(default=list, blank=True, verbose_name="Historique CAC")
    cac_sector_benchmark = models.DecimalField(max_digits=10, decimal_places=2, default=60.0, verbose_name="Benchmark secteur (€)")
    
    # LTV (Lifetime Value)
    ltv_current = models.DecimalField(max_digits=10, decimal_places=2, default=200.0, verbose_name="LTV actuel (€)")
    ltv_cac_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=4.0, verbose_name="Ratio LTV/CAC")
    
    # Churn Rate
    churn_rate_monthly = models.DecimalField(max_digits=5, decimal_places=2, default=5.0, verbose_name="Taux désabonnement mensuel (%)")
    churn_rate_history = models.JSONField(default=list, blank=True, verbose_name="Historique Churn")
    
    # MRR (Monthly Recurring Revenue)
    mrr_current = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="MRR actuel (€)")
    mrr_history = models.JSONField(default=list, blank=True, verbose_name="Historique MRR")
    
    # Burn Rate
    burn_rate_monthly = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Burn rate mensuel (€)")
    runway_months = models.IntegerField(default=12, verbose_name="Runway (mois)")
    
    # Seuil de Rentabilité
    break_even_month = models.IntegerField(null=True, blank=True, verbose_name="Mois seuil rentabilité")
    break_even_revenue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="CA nécessaire seuil (€)")
    
    # Métadonnées
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "KPI Financier"
        verbose_name_plural = "KPIs Financiers"
    
    def __str__(self):
        return f"KPIs Financiers - {self.updated_at.strftime('%d/%m/%Y')}"
    
    @classmethod
    def get_or_create_singleton(cls):
        """Récupère ou crée les KPIs unique"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def calculate_ltv_cac_ratio(self):
        """Calcule le ratio LTV/CAC"""
        if self.cac_current > 0:
            self.ltv_cac_ratio = round(float(self.ltv_current) / float(self.cac_current), 2)
        return self.ltv_cac_ratio


# ============================================
# MODÉRATION & TICKETS SUPPORT - PHASE 9
# ============================================

class ReportedContent(models.Model):
    """Contenu signalé (posts, commentaires, messages, profils)"""
    
    content_type = models.CharField(
        max_length=50,
        choices=[
            ('post', 'Post'),
            ('comment', 'Commentaire'),
            ('message', 'Message'),
            ('profile', 'Profil'),
        ],
        verbose_name="Type de contenu"
    )
    content_id = models.IntegerField(verbose_name="ID du contenu")
    content_preview = models.TextField(blank=True, null=True, verbose_name="Aperçu du contenu")
    content_full = models.TextField(blank=True, null=True, verbose_name="Contenu complet")
    
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reported_contents', 
                               verbose_name="Auteur du contenu")
    reported_by = models.ManyToManyField(CustomUser, related_name='reports_made', 
                                         verbose_name="Signalé par")
    reports_count = models.IntegerField(default=1, verbose_name="Nombre de signalements")
    
    reason = models.CharField(
        max_length=50,
        choices=[
            ('spam', 'Spam'),
            ('harassment', 'Harcèlement'),
            ('scam', 'Arnaque'),
            ('inappropriate', 'Contenu inapproprié'),
            ('fake', 'Faux contenu'),
            ('other', 'Autre'),
        ],
        verbose_name="Raison du signalement"
    )
    reason_detail = models.TextField(blank=True, null=True, verbose_name="Détails de la raison")
    
    severity = models.CharField(
        max_length=20,
        choices=[
            ('high', 'Haute'),
            ('medium', 'Moyenne'),
            ('low', 'Basse'),
        ],
        default='medium',
        verbose_name="Gravité"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'En attente'),
            ('treated', 'Traité'),
            ('ignored', 'Ignoré'),
            ('deleted', 'Supprimé'),
        ],
        default='pending',
        verbose_name="Statut"
    )
    
    treated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='treated_reports', verbose_name="Traité par")
    treated_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de traitement")
    treatment_notes = models.TextField(blank=True, null=True, verbose_name="Notes de traitement")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de signalement")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contenu signalé"
        verbose_name_plural = "Contenus signalés"
        unique_together = ['content_type', 'content_id']
    
    def __str__(self):
        return f"{self.get_content_type_display()} #{self.content_id} - {self.get_status_display()}"
    
    def add_report(self, user, reason, reason_detail=None):
        """Ajouter un signalement"""
        if user not in self.reported_by.all():
            self.reported_by.add(user)
            self.reports_count = self.reported_by.count()
            # Augmenter la gravité si plusieurs signalements
            if self.reports_count >= 5:
                self.severity = 'high'
            elif self.reports_count >= 3:
                self.severity = 'medium'
            self.save()


class UserModeration(models.Model):
    """Utilisateurs nécessitant une modération"""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='moderation_status',
                               verbose_name="Utilisateur")
    
    alert_type = models.CharField(
        max_length=50,
        choices=[
            ('multiple_reports', 'Plusieurs signalements'),
            ('suspicious_behavior', 'Comportement suspect (patterns IA)'),
            ('spam_detected', 'Spam détecté'),
            ('fake_profile', 'Profil suspect'),
            ('other', 'Autre'),
        ],
        verbose_name="Type d'alerte"
    )
    
    reports_count = models.IntegerField(default=0, verbose_name="Nombre de signalements")
    suspicious_patterns = models.JSONField(default=list, blank=True, verbose_name="Patterns suspects")
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('alert', 'Alerte'),
            ('warning_sent', 'Avertissement envoyé'),
            ('suspended', 'Suspendu'),
            ('banned', 'Banni'),
            ('ignored', 'Ignoré'),
        ],
        default='alert',
        verbose_name="Statut"
    )
    
    suspension_end = models.DateTimeField(null=True, blank=True, verbose_name="Fin de suspension")
    ban_reason = models.TextField(blank=True, null=True, verbose_name="Raison du bannissement")
    
    moderated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='moderated_users', verbose_name="Modéré par")
    moderated_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de modération")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Utilisateur à modérer"
        verbose_name_plural = "Utilisateurs à modérer"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_alert_type_display()}"


class PropertyClaimModeration(models.Model):
    """Réclamation de logement pour modération (distinct de ReclamationProprietaire)"""
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='property_claim_moderations',
                            verbose_name="Utilisateur réclamant")
    property_address = models.CharField(max_length=500, verbose_name="Adresse du bien")
    property_id = models.ForeignKey('Logement', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='claim_moderations', verbose_name="Bien concerné")
    
    claim_reason = models.TextField(verbose_name="Raison de la réclamation")
    documents = models.JSONField(default=list, blank=True, verbose_name="Documents fournis")
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'En attente'),
            ('under_review', 'En cours de vérification'),
            ('approved', 'Approuvé'),
            ('rejected', 'Refusé'),
            ('information_required', 'Informations requises'),
        ],
        default='pending',
        verbose_name="Statut"
    )
    
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='reviewed_claim_moderations', verbose_name="Révisé par")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de révision")
    review_notes = models.TextField(blank=True, null=True, verbose_name="Notes de révision")
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="Raison du refus")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de réclamation")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Réclamation de logement (Modération)"
        verbose_name_plural = "Réclamations de logement (Modération)"
    
    def __str__(self):
        return f"Réclamation - {self.user.username} - {self.property_address}"


class SupportTicket(models.Model):
    """Ticket de support"""
    
    ticket_id = models.CharField(max_length=20, unique=True, verbose_name="ID Ticket")
    title = models.CharField(max_length=200, verbose_name="Titre/Sujet")
    description = models.TextField(verbose_name="Description")
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='support_tickets',
                            verbose_name="Utilisateur")
    
    category = models.CharField(
        max_length=50,
        choices=[
            ('technical', 'Technique'),
            ('account', 'Compte'),
            ('payment', 'Paiement'),
            ('feature', 'Fonctionnalité'),
            ('other', 'Autre'),
        ],
        default='other',
        verbose_name="Catégorie"
    )
    
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Basse'),
            ('medium', 'Moyenne'),
            ('high', 'Haute'),
            ('urgent', 'Urgente'),
        ],
        default='medium',
        verbose_name="Priorité"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('open', 'Ouvert'),
            ('in_progress', 'En cours'),
            ('resolved', 'Résolu'),
            ('closed', 'Fermé'),
        ],
        default='open',
        verbose_name="Statut"
    )
    
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='assigned_tickets', verbose_name="Assigné à")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ouverture")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    last_reply_at = models.DateTimeField(null=True, blank=True, verbose_name="Dernière réponse")
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Ticket de support"
        verbose_name_plural = "Tickets de support"
    
    def __str__(self):
        return f"#{self.ticket_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            # Générer un ID unique
            import random
            import string
            self.ticket_id = 'T' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)


class TicketReply(models.Model):
    """Réponse à un ticket de support"""
    
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='replies',
                              verbose_name="Ticket")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ticket_replies',
                              verbose_name="Auteur")
    content = models.TextField(verbose_name="Contenu")
    is_admin_reply = models.BooleanField(default=False, verbose_name="Réponse admin")
    
    attachments = models.JSONField(default=list, blank=True, verbose_name="Pièces jointes")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Réponse ticket"
        verbose_name_plural = "Réponses tickets"
    
    def __str__(self):
        return f"Réponse #{self.ticket.ticket_id} - {self.author.username}"


class ReplyTemplate(models.Model):
    """Template de réponse pour tickets"""
    
    name = models.CharField(max_length=100, verbose_name="Nom du template")
    category = models.CharField(
        max_length=50,
        choices=[
            ('technical', 'Technique'),
            ('account', 'Compte'),
            ('payment', 'Paiement'),
            ('feature', 'Fonctionnalité'),
            ('other', 'Autre'),
        ],
        verbose_name="Catégorie"
    )
    content = models.TextField(verbose_name="Contenu du template")
    variables = models.JSONField(default=list, blank=True, 
                                verbose_name="Variables disponibles (ex: {user_name}, {ticket_id})")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Template de réponse"
        verbose_name_plural = "Templates de réponse"
    
    def __str__(self):
        return self.name


# ============================================
# PARAMÈTRES & CONFIGURATION - PHASE 10
# ============================================

class Settings(models.Model):
    """Paramètres généraux de la plateforme (singleton)"""
    
    # Informations entreprise
    site_name = models.CharField(max_length=200, default='Transpareo', verbose_name="Nom du site")
    site_logo = models.ImageField(upload_to='settings/logo/', blank=True, null=True, verbose_name="Logo")
    site_favicon = models.ImageField(upload_to='settings/favicon/', blank=True, null=True, verbose_name="Favicon")
    site_description = models.TextField(blank=True, null=True, verbose_name="Description")
    contact_email = models.EmailField(default='contact@transpareo.fr', verbose_name="Email de contact")
    contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    
    # Paramètres régionaux
    default_language = models.CharField(max_length=10, default='fr', choices=[
        ('fr', 'Français'),
        ('en', 'English'),
        ('es', 'Español'),
    ], verbose_name="Langue par défaut")
    default_currency = models.CharField(max_length=3, default='EUR', choices=[
        ('EUR', 'EUR (€)'),
        ('USD', 'USD ($)'),
        ('GBP', 'GBP (£)'),
    ], verbose_name="Devise")
    timezone = models.CharField(max_length=50, default='Europe/Paris', verbose_name="Fuseau horaire")
    date_format = models.CharField(max_length=20, default='DD/MM/YYYY', verbose_name="Format de date")
    
    # Maintenance
    maintenance_mode = models.BooleanField(default=False, verbose_name="Mode maintenance")
    maintenance_message = models.TextField(blank=True, null=True, verbose_name="Message de maintenance")
    maintenance_allowed_ips = models.JSONField(default=list, blank=True, verbose_name="IPs autorisées en maintenance")
    
    # Personnalisation
    primary_color = models.CharField(max_length=7, default='#D3580B', verbose_name="Couleur primaire")
    secondary_color = models.CharField(max_length=7, default='#1F2937', verbose_name="Couleur secondaire")
    font_family = models.CharField(max_length=50, default='Geist', choices=[
        ('Geist', 'Geist'),
        ('Inter', 'Inter'),
        ('Roboto', 'Roboto'),
        ('Arial', 'Arial'),
    ], verbose_name="Police principale")
    header_logo = models.ImageField(upload_to='settings/header/', blank=True, null=True, verbose_name="Logo header")
    
    # Pages légales
    cgu_content = models.TextField(blank=True, null=True, verbose_name="CGU")
    privacy_policy_content = models.TextField(blank=True, null=True, verbose_name="Politique de confidentialité")
    legal_notices_content = models.TextField(blank=True, null=True, verbose_name="Mentions légales")
    faq_data = models.JSONField(default=list, blank=True, verbose_name="FAQ (liste question/réponse)")
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="Meta title")
    meta_description = models.TextField(blank=True, null=True, verbose_name="Meta description")
    meta_keywords = models.JSONField(default=list, blank=True, verbose_name="Mots-clés")
    sitemap_auto_generate = models.BooleanField(default=True, verbose_name="Génération automatique sitemap")
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='settings_updated', verbose_name="Modifié par")
    
    class Meta:
        verbose_name = "Paramètres Généraux"
        verbose_name_plural = "Paramètres Généraux"
    
    def __str__(self):
        return f"Paramètres - {self.updated_at.strftime('%d/%m/%Y')}"
    
    @classmethod
    def get_or_create_singleton(cls):
        """Récupère ou crée les paramètres uniques"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Role(models.Model):
    """Rôles personnalisés avec permissions granulaires"""
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du rôle")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Permissions granulaires
    can_view_users = models.BooleanField(default=False, verbose_name="Voir utilisateurs")
    can_edit_users = models.BooleanField(default=False, verbose_name="Éditer utilisateurs")
    can_delete_users = models.BooleanField(default=False, verbose_name="Supprimer utilisateurs")
    
    can_view_properties = models.BooleanField(default=False, verbose_name="Voir logements")
    can_edit_properties = models.BooleanField(default=False, verbose_name="Éditer logements")
    can_delete_properties = models.BooleanField(default=False, verbose_name="Supprimer logements")
    
    can_view_moderation = models.BooleanField(default=False, verbose_name="Voir modération")
    can_treat_moderation = models.BooleanField(default=False, verbose_name="Traiter modération")
    
    can_view_business = models.BooleanField(default=False, verbose_name="Voir business")
    can_edit_business = models.BooleanField(default=False, verbose_name="Éditer business")
    
    can_view_finance = models.BooleanField(default=False, verbose_name="Voir finance")
    can_edit_finance = models.BooleanField(default=False, verbose_name="Éditer finance")
    
    can_view_settings = models.BooleanField(default=False, verbose_name="Voir paramètres")
    can_edit_settings = models.BooleanField(default=False, verbose_name="Éditer paramètres")
    
    can_view_analytics = models.BooleanField(default=False, verbose_name="Voir analytics")
    can_export_analytics = models.BooleanField(default=False, verbose_name="Exporter analytics")
    
    is_system = models.BooleanField(default=False, verbose_name="Rôle système (non modifiable)")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
    
    def __str__(self):
        return self.name


class AdminInvitation(models.Model):
    """Invitations d'administrateurs"""
    
    email = models.EmailField(verbose_name="Email")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, verbose_name="Rôle")
    token = models.CharField(max_length=100, unique=True, verbose_name="Token d'invitation")
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'En attente'),
            ('accepted', 'Acceptée'),
            ('expired', 'Expirée'),
            ('cancelled', 'Annulée'),
        ],
        default='pending',
        verbose_name="Statut"
    )
    
    invited_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='invitations_sent', verbose_name="Invité par")
    accepted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='invitations_accepted', verbose_name="Accepté par")
    
    expires_at = models.DateTimeField(verbose_name="Date d'expiration")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'invitation")
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name="Date d'acceptation")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Invitation Admin"
        verbose_name_plural = "Invitations Admin"
    
    def __str__(self):
        return f"Invitation {self.email} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if not self.token:
            import secrets
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)


class PaymentConfig(models.Model):
    """Configuration des paiements (singleton)"""
    
    # Moyens de paiement
    stripe_enabled = models.BooleanField(default=False, verbose_name="Stripe activé")
    stripe_public_key = models.CharField(max_length=200, blank=True, null=True, verbose_name="Stripe clé publique")
    stripe_secret_key = models.CharField(max_length=200, blank=True, null=True, verbose_name="Stripe clé secrète")
    
    paypal_enabled = models.BooleanField(default=False, verbose_name="PayPal activé")
    paypal_client_id = models.CharField(max_length=200, blank=True, null=True, verbose_name="PayPal Client ID")
    paypal_secret = models.CharField(max_length=200, blank=True, null=True, verbose_name="PayPal Secret")
    
    bank_transfer_enabled = models.BooleanField(default=True, verbose_name="Virement bancaire activé")
    
    # Tarification
    pricing_table = models.JSONField(default=list, blank=True, verbose_name="Grille tarifaire")
    
    # Commissions
    commission_rate_lease = models.DecimalField(max_digits=5, decimal_places=2, default=5.0, verbose_name="Taux commission location (%)")
    commission_rate_services = models.DecimalField(max_digits=5, decimal_places=2, default=3.0, verbose_name="Taux commission services (%)")
    
    # Facturation
    billing_company_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nom entreprise facturation")
    billing_siret = models.CharField(max_length=14, blank=True, null=True, verbose_name="SIRET")
    billing_vat = models.CharField(max_length=20, blank=True, null=True, verbose_name="Numéro TVA")
    billing_address = models.TextField(blank=True, null=True, verbose_name="Adresse facturation")
    invoice_template = models.TextField(blank=True, null=True, verbose_name="Template facture")
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Configuration Paiements"
        verbose_name_plural = "Configuration Paiements"
    
    def __str__(self):
        return "Configuration Paiements"
    
    @classmethod
    def get_or_create_singleton(cls):
        """Récupère ou crée la configuration unique"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class NotificationConfig(models.Model):
    """Configuration des notifications (singleton)"""
    
    # Notifications par défaut
    email_enabled_default = models.BooleanField(default=True, verbose_name="Email activé par défaut")
    push_enabled_default = models.BooleanField(default=True, verbose_name="Push navigateur activé par défaut")
    sms_enabled_default = models.BooleanField(default=False, verbose_name="SMS activé par défaut")
    
    # Notifications par événement (JSON)
    event_notifications = models.JSONField(default=dict, blank=True, verbose_name="Notifications par événement")
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Configuration Notifications"
        verbose_name_plural = "Configuration Notifications"
    
    def __str__(self):
        return "Configuration Notifications"
    
    @classmethod
    def get_or_create_singleton(cls):
        """Récupère ou crée la configuration unique"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class NotificationTemplate(models.Model):
    """Templates d'emails de notification"""
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du template")
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    body = models.TextField(verbose_name="Corps de l'email (HTML)")
    variables = models.JSONField(default=list, blank=True, verbose_name="Variables disponibles")
    
    template_type = models.CharField(
        max_length=50,
        choices=[
            ('welcome', 'Bienvenue'),
            ('confirmation', 'Confirmation'),
            ('reminder', 'Rappel'),
            ('alert', 'Alerte'),
            ('other', 'Autre'),
        ],
        default='other',
        verbose_name="Type de template"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Template Notification"
        verbose_name_plural = "Templates Notifications"
    
    def __str__(self):
        return self.name


class SecurityConfig(models.Model):
    """Configuration sécurité (singleton)"""
    
    # Authentification
    two_factor_required_admins = models.BooleanField(default=False, verbose_name="2FA obligatoire pour admins")
    session_duration_minutes = models.IntegerField(default=1440, verbose_name="Durée session (minutes)")
    
    # Politique mot de passe
    password_min_length = models.IntegerField(default=8, verbose_name="Longueur minimum mot de passe")
    password_require_uppercase = models.BooleanField(default=True, verbose_name="Requis majuscule")
    password_require_lowercase = models.BooleanField(default=True, verbose_name="Requis minuscule")
    password_require_number = models.BooleanField(default=True, verbose_name="Requis chiffre")
    password_require_special = models.BooleanField(default=False, verbose_name="Requis caractère spécial")
    
    # IPs autorisées
    admin_allowed_ips = models.JSONField(default=list, blank=True, verbose_name="IPs autorisées admin")
    
    # Rate limiting
    api_rate_limit = models.IntegerField(default=100, verbose_name="Limite requêtes API/minute")
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Configuration Sécurité"
        verbose_name_plural = "Configuration Sécurité"
    
    def __str__(self):
        return "Configuration Sécurité"
    
    @classmethod
    def get_or_create_singleton(cls):
        """Récupère ou crée la configuration unique"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class IntegrationConfig(models.Model):
    """Configuration des intégrations tierces"""
    
    # Google Maps
    google_maps_api_key = models.CharField(max_length=200, blank=True, null=True, verbose_name="Clé API Google Maps")
    google_maps_enabled = models.BooleanField(default=False, verbose_name="Google Maps activé")
    
    # Google Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID Google Analytics")
    google_analytics_enabled = models.BooleanField(default=False, verbose_name="Google Analytics activé")
    
    # Mailchimp/Sendinblue
    email_service = models.CharField(
        max_length=50,
        choices=[
            ('mailchimp', 'Mailchimp'),
            ('sendinblue', 'Sendinblue'),
            ('none', 'Aucun'),
        ],
        default='none',
        verbose_name="Service email"
    )
    email_service_api_key = models.CharField(max_length=200, blank=True, null=True, verbose_name="Clé API service email")
    email_service_list_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID liste de diffusion")
    email_service_auto_sync = models.BooleanField(default=False, verbose_name="Sync automatique utilisateurs")
    
    # Webhooks
    zapier_webhook_url = models.URLField(blank=True, null=True, verbose_name="URL Webhook Zapier")
    make_webhook_url = models.URLField(blank=True, null=True, verbose_name="URL Webhook Make")
    webhook_events = models.JSONField(default=list, blank=True, verbose_name="Événements déclencheurs webhooks")
    
    # Custom webhooks
    custom_webhooks = models.JSONField(default=list, blank=True, verbose_name="Webhooks personnalisés")
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Configuration Intégrations"
        verbose_name_plural = "Configuration Intégrations"
    
    def __str__(self):
        return "Configuration Intégrations"
    
    @classmethod
    def get_or_create_singleton(cls):
        """Récupère ou crée la configuration unique"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class ActivityLog(models.Model):
    """Logs d'activité admin"""
    
    admin = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='activity_logs', verbose_name="Admin")
    
    action = models.CharField(
        max_length=50,
        choices=[
            ('login', 'Connexion'),
            ('logout', 'Déconnexion'),
            ('create', 'Création'),
            ('update', 'Modification'),
            ('delete', 'Suppression'),
            ('view', 'Consultation'),
            ('export', 'Export'),
            ('other', 'Autre'),
        ],
        verbose_name="Action"
    )
    
    resource_type = models.CharField(
        max_length=50,
        choices=[
            ('user', 'Utilisateur'),
            ('property', 'Logement'),
            ('settings', 'Paramètres'),
            ('moderation', 'Modération'),
            ('ticket', 'Ticket'),
            ('business', 'Business'),
            ('finance', 'Finance'),
            ('other', 'Autre'),
        ],
        verbose_name="Type de ressource"
    )
    
    resource_id = models.IntegerField(null=True, blank=True, verbose_name="ID ressource")
    resource_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nom ressource")
    
    details = models.JSONField(default=dict, blank=True, verbose_name="Détails (JSON)")
    
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date/heure")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Log d'Activité"
        verbose_name_plural = "Logs d'Activité"
        indexes = [
            models.Index(fields=['admin', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['resource_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.admin.username if self.admin else 'Unknown'} - {self.get_action_display()} - {self.get_resource_type_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"