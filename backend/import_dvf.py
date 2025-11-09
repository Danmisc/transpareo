#!/usr/bin/env python
"""
Script d'import DVF complet - TOUS LOGEMENTS
Détecte automatiquement les noms de colonnes
"""

import os
import sys
import django
import pandas as pd
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, r'D:\transpareo html version\backend')
django.setup()

from core.models import Logement

# Chemin du fichier DVF
DVF_FILE = r'D:\transpareo html version\backend\data\dvf.csv.gz'

print("=" * 70)
print("🏠 IMPORT DVF COMPLET - TOUS LOGEMENTS")
print("=" * 70)

# ==================== CHARGEMENT ====================
print("\n📥 Chargement du fichier DVF...")
df = pd.read_csv(
    DVF_FILE, 
    sep=',',  # 👈 UTILISER VIRGULE COMME DÉLIMITEUR
    low_memory=False, 
    encoding='utf-8', 
    on_bad_lines='skip'
)

print(f"✅ {len(df):,} lignes chargées")
print(f"📋 Nombre de colonnes : {len(df.columns)}")

# ==================== AFFICHER LES COLONNES ====================
print(f"\n📋 Premières colonnes :")
for i, col in enumerate(df.columns[:15], 1):
    print(f"   {i:2}. '{col}'")

# ==================== MAPPING DIRECT ====================
print("\n🔍 Utilisation du mapping direct...")

col_map = {
    'latitude': 'latitude',
    'longitude': 'longitude',
    'valeur_fonciere': 'valeur_fonciere',
    'surface': 'surface_reelle_bati',
    'pieces': 'nombre_pieces_principales',
    'type_local': 'type_local',
    'numero': 'adresse_numero',
    'rue': 'adresse_nom_voie',
    'code_postal': 'code_postal',
    'date_mutation': 'date_mutation'
}

print(f"✅ Colonnes mappées :")
for key, value in col_map.items():
    exists = '✓' if value in df.columns else '✗'
    print(f"   {exists} {key:20} → '{value}'")

# ==================== NETTOYAGE ====================
print("\n🧹 Nettoyage des données...")

# Garder uniquement les lignes avec coordonnées
df_clean = df.dropna(subset=[col_map['latitude'], col_map['longitude']]).copy()
print(f"✅ {len(df_clean):,} lignes avec coordonnées GPS")

# Nettoyer les valeurs numériques
df_clean[col_map['valeur_fonciere']] = pd.to_numeric(
    df_clean[col_map['valeur_fonciere']], 
    errors='coerce'
).fillna(0)

df_clean[col_map['surface']] = pd.to_numeric(
    df_clean[col_map['surface']], 
    errors='coerce'
).fillna(0)

df_clean[col_map['pieces']] = pd.to_numeric(
    df_clean[col_map['pieces']], 
    errors='coerce'
).fillna(1)

df_clean[col_map['latitude']] = pd.to_numeric(
    df_clean[col_map['latitude']], 
    errors='coerce'
)

df_clean[col_map['longitude']] = pd.to_numeric(
    df_clean[col_map['longitude']], 
    errors='coerce'
)

# Filtrer valeurs raisonnables
df_clean = df_clean[
    (df_clean[col_map['valeur_fonciere']] > 0) & 
    (df_clean[col_map['surface']] > 0)
]

print(f"✅ {len(df_clean):,} lignes valides après nettoyage")

# ==================== IMPORT ====================
print(f"\n📥 Création des logements...")

logements = []
errors = 0

for idx, row in df_clean.iterrows():
    try:
        # Coordonnées
        lat = float(row[col_map['latitude']])
        lon = float(row[col_map['longitude']])
        
        # Adresse
        numero = str(int(row[col_map['numero']])) if pd.notna(row[col_map['numero']]) else ''
        rue = str(row[col_map['rue']]) if pd.notna(row[col_map['rue']]) else 'Adresse inconnue'
        adresse = f"{numero} {rue}".strip()
        
        # Valeurs
        valeur = float(row[col_map['valeur_fonciere']])
        surface = float(row[col_map['surface']])
        pieces = int(row[col_map['pieces']])
        type_local = str(row[col_map['type_local']]) if pd.notna(row[col_map['type_local']]) else 'Bien'
        
        # Code postal
        cp = str(int(row[col_map['code_postal']])) if pd.notna(row[col_map['code_postal']]) else '00000'
        
        # Loyer estimé
        loyer = int(abs(valeur * 0.045 / 12))
        
        # Titre
        titre = f"{type_local} {int(surface)}m²"
        
        # Description
        description = f"Surface : {int(surface)}m²\nPrix de vente : {int(valeur):,}€\nLoyer estimé : {loyer}€/mois"
        
        # Date
        date_mutation = pd.to_datetime(row[col_map['date_mutation']], errors='coerce') if pd.notna(row[col_map['date_mutation']]) else None
        
        # Créer
        logement = Logement(
            titre=titre,
            adresse=adresse,
            code_postal=cp,
            latitude=lat,
            longitude=lon,
            prix=Decimal(str(loyer)),
            surface=Decimal(str(surface)),
            chambres=pieces,
            description=description,
            type_logement='appartement',
            date_mutation=date_mutation,
            valeur_fonciere=Decimal(str(valeur)),
            statut='disponible'
        )
        
        logements.append(logement)
        
        # Progression
        if len(logements) % 10000 == 0:
            print(f"  ⏳ {len(logements):,} logements préparés...")
    
    except Exception as e:
        errors += 1
        if errors <= 3:
            print(f"  ⚠️ Erreur ligne {idx}: {str(e)[:80]}")

print(f"\n✅ {len(logements):,} logements prêts à importer")
print(f"⚠️ {errors:,} erreurs ignorées")

# ==================== SAUVEGARDE ====================
if logements:
    print(f"\n📥 Import en base de données...")
    print(f"  Suppression des anciens logements...")
    Logement.objects.all().delete()
    
    print(f"  Création des logements...")
    Logement.objects.bulk_create(logements, batch_size=5000)
    
    total = Logement.objects.count()
    print(f"\n✅ IMPORT TERMINÉ !")
    print(f"📊 Total en base : {total:,} logements")
else:
    print("\n❌ Aucun logement à importer !")

print("\n" + "=" * 70)
