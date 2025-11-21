from django.core.management.base import BaseCommand
from core.models import Badge


class Command(BaseCommand):
    help = 'Crée les badges par défaut pour Transpareo'

    def handle(self, *args, **options):
        badges_data = [
            {
                'name': 'Premier pas',
                'description': 'Première connexion réussie',
                'icon': '👋',
                'badge_type': 'activity',
                'rarity': 'common'
            },
            {
                'name': 'Email vérifié',
                'description': 'Email vérifié avec succès',
                'icon': '✅',
                'badge_type': 'security',
                'rarity': 'common'
            },
            {
                'name': 'Téléphone vérifié',
                'description': 'Numéro de téléphone vérifié',
                'icon': '📱',
                'badge_type': 'security',
                'rarity': 'common'
            },
            {
                'name': 'Protection renforcée',
                'description': 'Authentification à deux facteurs activée',
                'icon': '🔐',
                'badge_type': 'security',
                'rarity': 'rare'
            },
            {
                'name': 'Collectionneur',
                'description': '10 favoris enregistrés',
                'icon': '⭐',
                'badge_type': 'activity',
                'rarity': 'common'
            },
            {
                'name': 'Explorateur',
                'description': '25 favoris enregistrés',
                'icon': '🗺️',
                'badge_type': 'activity',
                'rarity': 'rare'
            },
            {
                'name': 'Critique',
                'description': '5 avis laissés',
                'icon': '✍️',
                'badge_type': 'social',
                'rarity': 'common'
            },
            {
                'name': 'Influenceur',
                'description': '20 avis laissés',
                'icon': '💬',
                'badge_type': 'social',
                'rarity': 'rare'
            },
            {
                'name': 'Propriétaire actif',
                'description': '5 logements listés',
                'icon': '🏠',
                'badge_type': 'activity',
                'rarity': 'common'
            },
            {
                'name': 'Propriétaire expérimenté',
                'description': '15 logements listés',
                'icon': '🏘️',
                'badge_type': 'activity',
                'rarity': 'rare'
            },
            {
                'name': 'Top propriétaire',
                'description': 'Note moyenne supérieure à 4.5 avec 20+ avis',
                'icon': '👑',
                'badge_type': 'premium',
                'rarity': 'epic'
            },
            {
                'name': 'Locataire fiable',
                'description': 'Aucun problème de paiement et bons avis',
                'icon': '💳',
                'badge_type': 'social',
                'rarity': 'rare'
            },
            {
                'name': 'Réactif',
                'description': 'Répond en moins de 2h',
                'icon': '⚡',
                'badge_type': 'activity',
                'rarity': 'rare'
            },
            {
                'name': 'Respectueux',
                'description': 'Bon taux de respect des biens',
                'icon': '🤝',
                'badge_type': 'social',
                'rarity': 'common'
            },
            {
                'name': 'Communicatif',
                'description': 'Beaucoup de messages et interactions',
                'icon': '💬',
                'badge_type': 'social',
                'rarity': 'common'
            },
            {
                'name': 'Ancien',
                'description': 'Membre depuis plus d\'un an',
                'icon': '🎂',
                'badge_type': 'activity',
                'rarity': 'rare'
            },
            {
                'name': 'Vétéran',
                'description': 'Membre depuis plus de 3 ans',
                'icon': '🏆',
                'badge_type': 'activity',
                'rarity': 'epic'
            },
            {
                'name': 'Profil complet',
                'description': 'Profil complété à 100%',
                'icon': '📋',
                'badge_type': 'activity',
                'rarity': 'common'
            },
            {
                'name': 'Identité vérifiée',
                'description': 'Identité vérifiée par Transpareo',
                'icon': '🆔',
                'badge_type': 'security',
                'rarity': 'epic'
            },
            {
                'name': 'Propriétaire vérifié',
                'description': 'Statut de propriétaire vérifié',
                'icon': '✓',
                'badge_type': 'security',
                'rarity': 'epic'
            },
        ]
        
        created_count = 0
        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'[OK] Badge cree: {badge.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'[EXISTE] Badge existe deja: {badge.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n{created_count} nouveaux badges créés sur {len(badges_data)} au total.'))

