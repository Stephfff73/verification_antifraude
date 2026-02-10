"""
Traitement OCR et extraction de texte depuis PDF et images
"""

import re
from datetime import datetime
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from config.settings import OCR_CONFIG, REGEX_PATTERNS


def extract_text_from_pdf(pdf_path, dpi=300):
    """
    Convertit un PDF en images puis applique l'OCR
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        dpi: Résolution de conversion (300 recommandé)
        
    Returns:
        str: Texte extrait
    """
    try:
        # Conversion PDF → Images
        images = convert_from_path(pdf_path, dpi=dpi)
        
        all_text = ""
        for page_num, img in enumerate(images, start=1):
            # OCR avec Tesseract
            text = pytesseract.image_to_string(
                img, 
                lang=OCR_CONFIG['lang'],
                config=f'--psm {OCR_CONFIG["psm"]}'
            )
            all_text += f"\n--- PAGE {page_num} ---\n{text}\n"
        
        return all_text.strip()
    
    except Exception as e:
        return f"ERREUR OCR: {str(e)}"


def extract_text_from_image(image_path):
    """
    Applique l'OCR directement sur une image
    
    Args:
        image_path: Chemin vers l'image
        
    Returns:
        str: Texte extrait
    """
    try:
        image = Image.open(image_path)
        
        text = pytesseract.image_to_string(
            image,
            lang=OCR_CONFIG['lang'],
            config=f'--psm {OCR_CONFIG["psm"]}'
        )
        
        return text.strip()
    
    except Exception as e:
        return f"ERREUR OCR: {str(e)}"


def extract_structured_data(text, doc_type):
    """
    Extrait des données structurées selon le type de document
    
    Args:
        text: Texte brut extrait par OCR
        doc_type: Type de document (contrat_travail, fiche_paie, etc.)
        
    Returns:
        dict: Données structurées extraites
    """
    data = {
        'raw_text': text,
        'siret': None,
        'dates': [],
        'montants': [],
        'email': None,
        'telephone': None,
        'nom': None,
        'adresse': None
    }
    
    # Extraction SIRET
    siret_match = re.search(REGEX_PATTERNS['siret'], text)
    if siret_match:
        data['siret'] = siret_match.group()
    
    # Extraction dates
    dates = re.findall(REGEX_PATTERNS['date_fr'], text)
    data['dates'] = dates
    
    # Extraction montants en euros
    montants = re.findall(REGEX_PATTERNS['montant_euro'], text)
    data['montants'] = [m.replace(' ', '').replace(',', '.') for m in montants]
    
    # Extraction email
    email_match = re.search(REGEX_PATTERNS['email'], text)
    if email_match:
        data['email'] = email_match.group()
    
    # Extraction téléphone
    tel_match = re.search(REGEX_PATTERNS['telephone'], text)
    if tel_match:
        data['telephone'] = tel_match.group()
    
    # Extraction spécifique selon type de document
    if doc_type == 'fiche_paie':
        data.update(extract_fiche_paie_data(text))
    
    elif doc_type == 'contrat_travail':
        data.update(extract_contrat_travail_data(text))
    
    elif doc_type == 'avis_imposition':
        data.update(extract_avis_imposition_data(text))
    
    return data


def extract_fiche_paie_data(text):
    """Extrait données spécifiques d'une fiche de paie"""
    fiche_data = {
        'salaire_brut': None,
        'salaire_net': None,
        'net_imposable': None,
        'periode': None,
        'urssaf': False
    }
    
    # Salaire brut
    brut_match = re.search(r'(?:salaire\s+)?brut[:\s]+(\d+[,\.]?\d*)', text, re.IGNORECASE)
    if brut_match:
        fiche_data['salaire_brut'] = float(brut_match.group(1).replace(',', '.'))
    
    # Salaire net
    net_match = re.search(r'(?:salaire\s+)?net\s+(?:à\s+payer)?[:\s]+(\d+[,\.]?\d*)', text, re.IGNORECASE)
    if net_match:
        fiche_data['salaire_net'] = float(net_match.group(1).replace(',', '.'))
    
    # Net imposable
    imposable_match = re.search(r'net\s+imposable[:\s]+(\d+[,\.]?\d*)', text, re.IGNORECASE)
    if imposable_match:
        fiche_data['net_imposable'] = float(imposable_match.group(1).replace(',', '.'))
    
    # Période
    periode_match = re.search(r'période[:\s]+(\d{2}/\d{4})', text, re.IGNORECASE)
    if periode_match:
        fiche_data['periode'] = periode_match.group(1)
    
    # URSSAF
    if 'urssaf' in text.lower():
        fiche_data['urssaf'] = True
    
    return fiche_data


def extract_contrat_travail_data(text):
    """Extrait données spécifiques d'un contrat de travail"""
    contrat_data = {
        'type_contrat': None,
        'fonction': None,
        'salaire': None,
        'date_debut': None
    }
    
    # Type de contrat
    if re.search(r'\bCDI\b', text, re.IGNORECASE):
        contrat_data['type_contrat'] = 'CDI'
    elif re.search(r'\bCDD\b', text, re.IGNORECASE):
        contrat_data['type_contrat'] = 'CDD'
    
    # Fonction/Poste
    fonction_match = re.search(r'(?:fonction|poste)[:\s]+([A-ZÀ-Ÿa-zà-ÿ\s]+)', text, re.IGNORECASE)
    if fonction_match:
        contrat_data['fonction'] = fonction_match.group(1).strip()[:100]
    
    # Salaire
    salaire_match = re.search(r'(?:rémunération|salaire)[:\s]+(\d+[,\.]?\d*)', text, re.IGNORECASE)
    if salaire_match:
        contrat_data['salaire'] = float(salaire_match.group(1).replace(',', '.'))
    
    return contrat_data


def extract_avis_imposition_data(text):
    """Extrait données spécifiques d'un avis d'imposition"""
    avis_data = {
        'numero_fiscal': None,
        'revenu_imposable': None,
        'impot_sur_revenu': None,
        'annee_revenus': None,
        'dgfip': False
    }
    
    # Numéro fiscal
    numero_match = re.search(REGEX_PATTERNS['numero_fiscal'], text)
    if numero_match:
        avis_data['numero_fiscal'] = numero_match.group()
    
    # Revenu fiscal de référence
    revenu_match = re.search(r'revenu\s+fiscal\s+de\s+référence[:\s]+(\d+[\s\d]*)', text, re.IGNORECASE)
    if revenu_match:
        avis_data['revenu_imposable'] = int(revenu_match.group(1).replace(' ', ''))
    
    # Impôt sur le revenu
    impot_match = re.search(r'impôt\s+sur\s+le\s+revenu[:\s]+(\d+[\s\d]*)', text, re.IGNORECASE)
    if impot_match:
        avis_data['impot_sur_revenu'] = int(impot_match.group(1).replace(' ', ''))
    
    # Année des revenus
    annee_match = re.search(r'revenus\s+(\d{4})', text, re.IGNORECASE)
    if annee_match:
        avis_data['annee_revenus'] = int(annee_match.group(1))
    
    # DGFiP
    if 'dgfip' in text.lower() or 'direction générale des finances publiques' in text.lower():
        avis_data['dgfip'] = True
    
    return avis_data


def normalize_text(text):
    """Normalise le texte pour comparaisons"""
    import unicodedata
    
    # Supprimer accents
    normalized = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    
    # Minuscules + espaces multiples
    normalized = re.sub(r'\s+', ' ', normalized.lower()).strip()
    
    return normalized
