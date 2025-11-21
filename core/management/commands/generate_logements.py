from django.core.management.base import BaseCommand
from core.models import Logement
import random

class Command(BaseCommand):
    help = 'Génère 100 logements fictifs à Toulouse'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('⚠️ Suppression des logements existants...'))
        
        # Supprimer en SQL brut
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM core_logement")
            self.stdout.write(self.style.SUCCESS('✅ Logements supprimés'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur : {e}'))
            return

        self.stdout.write(self.style.WARNING('🏗️ Création de 100 logements fictifs...'))

        # Coordonnées Toulouse
        toulouse_lat_min = 43.55
        toulouse_lat_max = 43.65
        toulouse_lon_min = 1.40
        toulouse_lon_max = 1.50

        # Rues
        rues = [
            "Rue de Metz", "Boulevard de Strasbourg", "Rue Bayard",
            "Rue Lalande", "Rue des Paradoux", "Rue du Taur",
            "Rue Saint-Antoine", "Rue de la Poulaillerie", "Rue Romiguières",
            "Rue Saint-Rome", "Rue du Colet", "Rue de la Concorde",
            "Rue des Trois Journées", "Rue Bouquière", "Rue Castellane",
            "Avenue de Toulouse", "Boulevard de Verdun", "Rue Pharaon",
            "Rue Delpech", "Rue des Filatiers"
        ]

        types = ["appartement", "maison", "studio"]

        # Créer les logements
        logements = []
        for i in range(100):
            lat = random.uniform(toulouse_lat_min, toulouse_lat_max)
            lon = random.uniform(toulouse_lon_min, toulouse_lon_max)
            rue = random.choice(rues)
            numero = random.randint(1, 150)
            type_log = random.choice(types)
            prix = random.randint(400, 2000)
            surface = random.randint(30, 200)
            chambres = random.randint(1, 5)

            if lat < 43.57:
                quartier = "Quartier Minimes"
            elif lat > 43.62:
                quartier = "Quartier Arnaud Bernard"
            else:
                quartier = "Centre-Ville"

            logement = Logement(
                titre=f"{type_log.capitalize()} {int(surface)}m² - {quartier}",
                adresse=f"{numero} {rue}, Toulouse",
                latitude=lat,
                longitude=lon,
                prix=prix,
                surface=surface,
                chambres=chambres,
                type_logement=type_log,
                etage=random.choice(['rdc', 'etage', 'dernier']),
                description=f"Beau {type_log} de {surface}m² à {quartier}. "
                           f"Idéalement situé près des commodités. "
                           f"Libre immédiatement.",
                # ❌ SUPPRIMÉ : note=round(random.uniform(3.5, 5.0), 1),
                statut='disponible'
            )
            logements.append(logement)

        # Créer en bulk
        try:
            Logement.objects.bulk_create(logements)
            self.stdout.write(self.style.SUCCESS(f'✅ {len(logements)} logements créés avec succès !'))
            self.stdout.write(f'📍 Coordonnées : Toulouse')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors de la création : {e}'))
