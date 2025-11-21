"""
Script de management Django pour importer des logements depuis des sources officielles françaises
- Supprime les logements existants
- Récupère des adresses réelles via l'API Adresse (data.gouv.fr)
- Génère des données réalistes
- Télécharge des images depuis Unsplash
- Conserve le système de notes
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db import transaction
from core.models import Logement, ImageLogement
import requests
import random
import time
from decimal import Decimal
from io import BytesIO
from PIL import Image


class Command(BaseCommand):
    help = 'Supprime les logements existants et importe de nouveaux logements depuis des sources officielles françaises'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=500,
            help='Nombre de logements à créer (défaut: 500)',
        )
        parser.add_argument(
            '--cities',
            type=str,
            default='paris,lyon,marseille,toulouse,nicer,bordeaux,lille,strasbourg,nantes,montpellier',
            help='Villes séparées par des virgules (défaut: principales villes françaises)',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        cities = [c.strip() for c in options['cities'].split(',')]
        
        self.stdout.write(self.style.WARNING('🗑️  Suppression des logements existants...'))
        
        # Supprimer les images d'abord (CASCADE supprimera automatiquement les logements)
        try:
            ImageLogement.objects.all().delete()
            Logement.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'✅ {Logement.objects.count()} logements supprimés'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors de la suppression : {e}'))
            return
        
        self.stdout.write(self.style.SUCCESS('✅ Logements et images supprimés avec succès'))
        
        self.stdout.write(self.style.WARNING(f'🏗️  Création de {limit} logements en France...'))
        
        # Types de logements
        types_logements = ['appartement', 'maison', 'studio', 'appartement', 'appartement']
        
        # Prix moyens par ville (€/m²/mois approximatif)
        prix_par_ville = {
            'paris': (25, 45),  # Prix min et max par m²
            'lyon': (15, 25),
            'marseille': (12, 20),
            'toulouse': (12, 18),
            'nice': (15, 25),
            'bordeaux': (14, 22),
            'lille': (12, 18),
            'strasbourg': (12, 18),
            'nantes': (13, 20),
            'montpellier': (13, 20),
        }
        
        logements_crees = []
        erreurs = 0
        
        # Répartir les logements entre les villes
        logements_par_ville = limit // len(cities)
        reste = limit % len(cities)
        
        for idx, city in enumerate(cities):
            if idx < reste:
                nb_logements = logements_par_ville + 1
            else:
                nb_logements = logements_par_ville
            
            self.stdout.write(f'📍 Traitement de {city} ({nb_logements} logements)...')
            
            for i in range(nb_logements):
                try:
                    # Récupérer une adresse réelle via l'API Adresse
                    adresse_data = self.get_adresse_reelle(city)
                    
                    if not adresse_data:
                        erreurs += 1
                        continue
                    
                    # Générer des données réalistes
                    type_log = random.choice(types_logements)
                    surface = self.generate_surface(type_log)
                    chambres = self.generate_chambres(type_log, surface)
                    
                    # Prix basé sur la ville
                    prix_par_m2 = prix_par_ville.get(city.lower(), (12, 18))
                    prix_m2 = random.uniform(prix_par_m2[0], prix_par_m2[1])
                    prix = int(surface * prix_m2)
                    
                    # Créer le logement
                    logement = Logement(
                        titre=self.generate_titre(type_log, surface, city),
                        adresse=adresse_data['adresse'],
                        code_postal=adresse_data.get('code_postal', '00000'),
                        latitude=adresse_data['latitude'],
                        longitude=adresse_data['longitude'],
                        prix=Decimal(str(prix)),
                        surface=Decimal(str(surface)),
                        chambres=chambres,
                        type_logement=type_log,
                        etage=random.choice(['rdc', 'etage', 'dernier']),
                        description=self.generate_description(type_log, surface, chambres, city),
                        statut='disponible',
                        note_moyenne=round(random.uniform(3.5, 5.0), 1),  # Notes aléatoires entre 3.5 et 5.0
                        nombre_avis=random.randint(0, 25),  # Nombre d'avis aléatoire
                    )
                    logement.save()
                    
                    # Télécharger des images depuis Unsplash
                    self.download_images_for_logement(logement, type_log)
                    
                    logements_crees.append(logement)
                    
                    if (i + 1) % 10 == 0:
                        self.stdout.write(f'  ✓ {i + 1}/{nb_logements} logements créés pour {city}')
                    
                    # Pause pour ne pas surcharger les APIs
                    time.sleep(0.1)
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ❌ Erreur pour logement {i+1} à {city}: {e}'))
                    erreurs += 1
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ {len(logements_crees)} logements créés avec succès !'))
        if erreurs > 0:
            self.stdout.write(self.style.WARNING(f'⚠️  {erreurs} erreurs rencontrées'))
        
        self.stdout.write(f'\n📊 Statistiques:')
        self.stdout.write(f'  - Total logements: {Logement.objects.count()}')
        self.stdout.write(f'  - Total images: {ImageLogement.objects.count()}')
        self.stdout.write(f'  - Villes couvertes: {len(cities)}')
    
    def get_adresse_reelle(self, city):
        """
        Récupère une adresse réelle via l'API Adresse (data.gouv.fr)
        """
        try:
            # Utiliser l'API Adresse pour obtenir des adresses réelles
            # On cherche des adresses dans la ville spécifiée
            url = "https://api-adresse.data.gouv.fr/search/"
            params = {
                'q': f"{city}, France",
                'limit': 100,
                'type': 'housenumber',
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])
                
                if features:
                    # Prendre une adresse aléatoire parmi les résultats
                    feature = random.choice(features)
                    props = feature.get('properties', {})
                    geometry = feature.get('geometry', {})
                    coords = geometry.get('coordinates', [])
                    
                    if coords and len(coords) == 2:
                        adresse = props.get('label', f"Adresse à {city}")
                        code_postal = props.get('postcode', '00000')
                        
                        return {
                            'adresse': adresse,
                            'code_postal': code_postal,
                            'latitude': coords[1],
                            'longitude': coords[0],
                        }
            
            # Fallback: générer des coordonnées dans la ville
            return self.generate_fallback_adresse(city)
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Erreur API Adresse pour {city}: {e}'))
            return self.generate_fallback_adresse(city)
    
    def generate_fallback_adresse(self, city):
        """
        Génère des coordonnées de fallback pour une ville
        """
        # Coordonnées approximatives des principales villes françaises
        villes_coords = {
            'paris': (48.8566, 2.3522),
            'lyon': (45.7640, 4.8357),
            'marseille': (43.2965, 5.3698),
            'toulouse': (43.6047, 1.4442),
            'nice': (43.7102, 7.2620),
            'bordeaux': (44.8378, -0.5792),
            'lille': (50.6292, 3.0573),
            'strasbourg': (48.5734, 7.7521),
            'nantes': (47.2184, -1.5536),
            'montpellier': (43.6108, 3.8767),
        }
        
        base_lat, base_lon = villes_coords.get(city.lower(), (46.2276, 2.2137))  # Centre de la France par défaut
        
        # Ajouter une variation aléatoire (environ 5km de rayon)
        lat = base_lat + random.uniform(-0.05, 0.05)
        lon = base_lon + random.uniform(-0.05, 0.05)
        
        # Générer un numéro et une rue fictive mais réaliste
        numero = random.randint(1, 200)
        rues_communes = [
            "Rue de la République", "Rue Victor Hugo", "Avenue Jean Jaurès",
            "Boulevard de la Liberté", "Rue de la Paix", "Rue du Commerce",
            "Avenue des Champs", "Rue de la Gare", "Place de la Mairie",
            "Rue de l'Église", "Avenue de la République", "Rue Nationale",
        ]
        rue = random.choice(rues_communes)
        
        return {
            'adresse': f"{numero} {rue}, {city.capitalize()}",
            'code_postal': '00000',
            'latitude': lat,
            'longitude': lon,
        }
    
    def generate_surface(self, type_log):
        """Génère une surface réaliste selon le type de logement"""
        if type_log == 'studio':
            return random.randint(20, 35)
        elif type_log == 'appartement':
            return random.randint(40, 120)
        elif type_log == 'maison':
            return random.randint(80, 200)
        else:
            return random.randint(30, 100)
    
    def generate_chambres(self, type_log, surface):
        """Génère un nombre de chambres réaliste"""
        if type_log == 'studio':
            return 1
        elif type_log == 'appartement':
            # Environ 1 chambre pour 25-30m²
            return min(4, max(1, int(surface / 30)))
        elif type_log == 'maison':
            return random.randint(3, 6)
        else:
            return random.randint(1, 3)
    
    def generate_titre(self, type_log, surface, city):
        """Génère un titre pour le logement"""
        qualificatifs = ['Beau', 'Spacieux', 'Lumineux', 'Moderne', 'Charmant', 'Confortable']
        qualificatif = random.choice(qualificatifs)
        return f"{qualificatif} {type_log.capitalize()} {int(surface)}m² - {city.capitalize()}"
    
    def generate_description(self, type_log, surface, chambres, city):
        """Génère une description pour le logement"""
        descriptions = [
            f"Magnifique {type_log} de {int(surface)}m² situé à {city.capitalize()}. "
            f"Composé de {chambres} chambre{'s' if chambres > 1 else ''}, "
            f"ce bien est idéal pour une location. Proche des commodités et des transports.",
            
            f"Superbe {type_log} de {int(surface)}m² à {city.capitalize()}. "
            f"Appartement avec {chambres} chambre{'s' if chambres > 1 else ''}, "
            f"parfaitement situé. Disponible immédiatement.",
            
            f"Joli {type_log} de {int(surface)}m² dans le centre de {city.capitalize()}. "
            f"{chambres} chambre{'s' if chambres > 1 else ''}, "
            f"bien entretenu et lumineux. Idéal pour une location longue durée.",
        ]
        return random.choice(descriptions)
    
    def download_images_for_logement(self, logement, type_log):
        """
        Télécharge des images depuis Unsplash pour le logement
        Utilise l'API Unsplash (gratuite avec attribution)
        """
        try:
            # Mots-clés pour la recherche d'images selon le type
            keywords = {
                'studio': 'apartment-interior',
                'appartement': 'modern-apartment',
                'maison': 'house-interior',
                'chambre': 'bedroom',
            }
            
            keyword = keywords.get(type_log, 'apartment')
            
            # Télécharger 3-5 images par logement
            nb_images = random.randint(3, 5)
            
            for i in range(nb_images):
                try:
                    # Utiliser l'API Unsplash (gratuite, pas besoin de clé pour les images aléatoires)
                    # Format: https://images.unsplash.com/photo-{random_id}?w=800&h=600&fit=crop
                    # Ou utiliser un service de placeholder avec des images réelles
                    
                    # Méthode 1: Utiliser Picsum (service de placeholder avec vraies photos)
                    # Plus fiable que Unsplash Source API
                    image_url = f"https://picsum.photos/800/600?random={logement.id}_{i}"
                    
                    # Télécharger l'image
                    response = requests.get(image_url, timeout=10, allow_redirects=True)
                    
                    if response.status_code == 200:
                        # Vérifier que c'est bien une image
                        img = Image.open(BytesIO(response.content))
                        
                        # Convertir en RGB si nécessaire
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Redimensionner si nécessaire (max 1200px)
                        max_size = 1200
                        if img.width > max_size or img.height > max_size:
                            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                        
                        # Sauvegarder dans un BytesIO
                        img_io = BytesIO()
                        img.save(img_io, format='JPEG', quality=85, optimize=True)
                        img_io.seek(0)
                        
                        # Créer l'ImageLogement
                        image_logement = ImageLogement(
                            logement=logement,
                            titre=f"Image {i+1} - {logement.titre}",
                            ordre=i,
                            est_principale=(i == 0),  # Première image = principale
                        )
                        
                        # Sauvegarder l'image
                        image_logement.image.save(
                            f"logement_{logement.id}_img_{i+1}.jpg",
                            ContentFile(img_io.read()),
                            save=True
                        )
                        
                        # Petite pause pour ne pas surcharger le service
                        time.sleep(0.1)
                    
                except Exception as e:
                    # Si une image échoue, continuer avec les autres
                    self.stdout.write(self.style.WARNING(f'    ⚠️  Erreur image {i+1} pour logement {logement.id}: {e}'))
                    continue
                    
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Erreur lors du téléchargement des images pour logement {logement.id}: {e}'))

