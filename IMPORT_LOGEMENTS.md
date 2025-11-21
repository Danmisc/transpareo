# Import de Logements depuis des Sources Officielles Françaises

Ce script permet de supprimer les logements existants dans la base de données et d'importer de nouveaux logements depuis des sources officielles françaises avec leurs images.

## Fonctionnalités

✅ **Suppression automatique** : Supprime tous les logements existants et leurs images associées  
✅ **Adresses réelles** : Utilise l'API Adresse (data.gouv.fr) pour obtenir des adresses réelles en France  
✅ **Données réalistes** : Génère des données cohérentes (prix, surface, chambres) selon les villes  
✅ **Images** : Télécharge automatiquement 3-5 images par logement depuis Picsum Photos  
✅ **Système de notes** : Conserve le système de notes avec des valeurs aléatoires entre 3.5 et 5.0  

## Utilisation

### Commande de base

```bash
python manage.py import_logements_france
```

Cette commande va :
- Supprimer tous les logements existants
- Créer 500 logements par défaut répartis sur les principales villes françaises

### Options disponibles

#### Limiter le nombre de logements

```bash
python manage.py import_logements_france --limit 100
```

#### Choisir des villes spécifiques

```bash
python manage.py import_logements_france --cities "paris,lyon,marseille"
```

#### Combiner les options

```bash
python manage.py import_logements_france --limit 200 --cities "toulouse,bordeaux,nantes"
```

## Villes par défaut

Le script utilise par défaut ces villes :
- Paris
- Lyon
- Marseille
- Toulouse
- Nice
- Bordeaux
- Lille
- Strasbourg
- Nantes
- Montpellier

## Données générées

Pour chaque logement, le script génère :

- **Titre** : Basé sur le type, la surface et la ville
- **Adresse** : Adresse réelle via l'API Adresse (data.gouv.fr)
- **Coordonnées GPS** : Latitude et longitude précises
- **Prix** : Basé sur les prix moyens par ville (€/m²)
- **Surface** : Réaliste selon le type de logement
  - Studio : 20-35 m²
  - Appartement : 40-120 m²
  - Maison : 80-200 m²
- **Chambres** : Calculé selon la surface et le type
- **Description** : Description détaillée du logement
- **Note moyenne** : Entre 3.5 et 5.0 étoiles
- **Nombre d'avis** : Entre 0 et 25 avis
- **Images** : 3-5 images téléchargées automatiquement

## Prix moyens par ville

Les prix sont calculés selon les moyennes du marché :

| Ville | Prix min (€/m²) | Prix max (€/m²) |
|-------|----------------|----------------|
| Paris | 25 | 45 |
| Lyon | 15 | 25 |
| Marseille | 12 | 20 |
| Toulouse | 12 | 18 |
| Nice | 15 | 25 |
| Bordeaux | 14 | 22 |
| Lille | 12 | 18 |
| Strasbourg | 12 | 18 |
| Nantes | 13 | 20 |
| Montpellier | 13 | 20 |

## Images

Les images sont téléchargées depuis [Picsum Photos](https://picsum.photos/), un service gratuit qui fournit des images de haute qualité. Chaque logement reçoit 3-5 images aléatoires.

## Notes importantes

⚠️ **Attention** : Cette commande supprime **TOUS** les logements existants avant d'importer les nouveaux. Assurez-vous d'avoir une sauvegarde si nécessaire.

⏱️ **Temps d'exécution** : Pour 500 logements, comptez environ 5-10 minutes selon votre connexion internet (téléchargement des images).

🌐 **Connexion internet requise** : Le script nécessite une connexion internet pour :
- Récupérer les adresses via l'API Adresse
- Télécharger les images depuis Picsum Photos

## Exemples d'utilisation

### Créer 100 logements à Paris uniquement

```bash
python manage.py import_logements_france --limit 100 --cities "paris"
```

### Créer 1000 logements sur toutes les grandes villes

```bash
python manage.py import_logements_france --limit 1000
```

### Créer 50 logements dans 3 villes spécifiques

```bash
python manage.py import_logements_france --limit 50 --cities "toulouse,bordeaux,nantes"
```

## Dépannage

### Erreur de connexion à l'API Adresse

Si l'API Adresse ne répond pas, le script utilise un système de fallback qui génère des coordonnées approximatives pour la ville demandée.

### Erreur de téléchargement d'images

Si certaines images ne peuvent pas être téléchargées, le script continue avec les autres images. Les logements seront créés même si certaines images échouent.

### Erreur de base de données

Assurez-vous que les migrations Django sont à jour :

```bash
python manage.py migrate
```

## Support

Pour toute question ou problème, consultez les logs de la commande qui affichent les erreurs détaillées.

