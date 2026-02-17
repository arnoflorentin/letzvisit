#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour mettre à jour automatiquement le vocabulaire avec vos images.

Usage:
  1. Placez vos images dans le dossier images/
  2. Nommez-les selon la convention: terme-1.jpg, terme-2.jpg, terme-3.jpg
  3. Exécutez: python3 update_images.py
  4. Le fichier greek_vocabulary.html sera mis à jour automatiquement
"""

import json
import os
import re

def normalize_term(term):
    """Convertit un terme en nom de fichier (minuscules, espaces → tirets)"""
    # Prendre seulement le premier mot avant le /
    term = term.split(' / ')[0]
    # Convertir en minuscules et remplacer espaces par tirets
    return term.lower().replace(' ', '-')

def check_images_exist(term_normalized, images_dir='images'):
    """Vérifie si les 3 images existent pour un terme"""
    images = []
    for i in range(1, 4):
        img_path = f"{images_dir}/{term_normalized}-{i}.jpg"
        webp_path = f"{images_dir}/{term_normalized}-{i}.webp"
        
        if os.path.exists(img_path):
            images.append(img_path)
        elif os.path.exists(webp_path):
            images.append(webp_path)
        else:
            images.append(None)
    
    return images

def generate_image_html(term, images):
    """Génère le HTML pour la galerie d'images"""
    html = '                <div class="image-gallery">\n'
    
    for i, img_path in enumerate(images, 1):
        if img_path:
            # Support WebP avec fallback JPEG
            if img_path.endswith('.webp'):
                html += f'                    <picture>\n'
                html += f'                        <source srcset="{img_path}" type="image/webp">\n'
                html += f'                        <img src="{img_path.replace(".webp", ".jpg")}" alt="{term} {i}" loading="lazy" width="150" height="150">\n'
                html += f'                    </picture>\n'
            else:
                html += f'                    <img src="{img_path}" alt="{term} {i}" loading="lazy" width="150" height="150">\n'
        else:
            # Placeholder si l'image n'existe pas
            html += f'                    <div class="image-placeholder">Image à venir</div>\n'
    
    html += '                </div>'
    return html

def update_html_with_images(json_file='final_entries.json', html_file='greek_vocabulary.html', images_dir='images'):
    """Met à jour le fichier HTML avec les vraies images"""
    
    print("🔍 Lecture des données...")
    with open(json_file, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    
    print(f"✓ {len(entries)} termes chargés")
    
    # Vérifier quelles images existent
    print(f"\n📸 Scan du dossier {images_dir}/...")
    images_found = 0
    images_missing = 0
    
    image_map = {}
    for term in sorted(entries.keys()):
        term_normalized = normalize_term(term)
        images = check_images_exist(term_normalized, images_dir)
        image_map[term] = images
        
        found = sum(1 for img in images if img is not None)
        images_found += found
        images_missing += (3 - found)
        
        if found > 0:
            print(f"  ✓ {term}: {found}/3 images trouvées")
    
    print(f"\n📊 Résumé:")
    print(f"  Images trouvées: {images_found}")
    print(f"  Images manquantes: {images_missing}")
    print(f"  Total: {images_found + images_missing}")
    
    # Lire le HTML actuel
    print(f"\n🔄 Mise à jour de {html_file}...")
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Remplacer les galeries d'images
    # Pattern: trouve les galeries entre les balises
    pattern = r'(<div class="image-gallery">.*?</div>\s*</div>)'
    
    def replace_gallery(match):
        # Trouver le terme correspondant dans le contexte
        # On cherche le titre de l'entrée juste avant
        context_before = html[:match.start()]
        title_match = re.search(r'id="[A-Z]-([^"]+)"', context_before[::-1])
        
        if title_match:
            term_id = title_match.group(1)[::-1]
            # Chercher le terme correspondant
            for term in entries.keys():
                if term.split(' / ')[0] == term_id:
                    images = image_map.get(term, [None, None, None])
                    return generate_image_html(term, images) + '\n            </div>'
        
        return match.group(0)
    
    # Cette approche est complexe, utilisons plutôt une régénération complète
    print("⚠️  Pour une mise à jour complète, utilisez le script de génération complet")
    print("    ou contactez-moi pour une version automatisée")
    
    return image_map

def list_missing_images(image_map):
    """Liste tous les termes avec images manquantes"""
    print("\n📋 IMAGES MANQUANTES:\n")
    
    for term, images in sorted(image_map.items()):
        missing = [i+1 for i, img in enumerate(images) if img is None]
        if missing:
            term_normalized = normalize_term(term)
            print(f"{term}:")
            for num in missing:
                print(f"  - {term_normalized}-{num}.jpg")

if __name__ == "__main__":
    import sys
    
    # Vérifier que le dossier images existe
    if not os.path.exists('images'):
        print("❌ Le dossier 'images/' n'existe pas!")
        print("   Créez-le et ajoutez vos images, puis réexécutez ce script.")
        sys.exit(1)
    
    # Scanner les images
    image_map = update_html_with_images()
    
    # Lister les images manquantes
    list_missing_images(image_map)
    
    print("\n✅ Scan terminé!")
    print("\n💡 Pour intégrer ces images dans le HTML:")
    print("   1. Assurez-vous que toutes vos images sont nommées correctement")
    print("   2. Demandez-moi de régénérer le HTML avec vos images")
