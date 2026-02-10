"""
Analyseur de métadonnées pour détecter les manipulations de documents
"""

import os
from datetime import datetime
from PyPDF2 import PdfReader
from PIL import Image
from PIL.ExifTags import TAGS
import pikepdf


def analyze_pdf_metadata(file_path):
    """
    Extrait et analyse les métadonnées d'un fichier PDF
    
    Args:
        file_path: Chemin vers le fichier PDF
        
    Returns:
        dict: Métadonnées et indicateurs de fraude
    """
    metadata = {
        'creator': 'Unknown',
        'producer': 'Unknown',
        'creation_date': None,
        'modification_date': None,
        'is_encrypted': False,
        'page_count': 0,
        'file_size_mb': 0,
        'suspicious_signs': [],
        'fraud_indicators': []
    }
    
    try:
        # Taille du fichier
        metadata['file_size_mb'] = os.path.getsize(file_path) / (1024 * 1024)
        
        # Extraction métadonnées avec PyPDF2
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            metadata['page_count'] = len(reader.pages)
            
            if reader.metadata:
                metadata['creator'] = str(reader.metadata.get('/Creator', 'Unknown'))
                metadata['producer'] = str(reader.metadata.get('/Producer', 'Unknown'))
                metadata['creation_date'] = reader.metadata.get('/CreationDate')
                metadata['modification_date'] = reader.metadata.get('/ModDate')
        
        # Analyse avancée avec pikepdf
        with pikepdf.open(file_path, allow_overwriting_input=True) as pdf:
            metadata['is_encrypted'] = pdf.is_encrypted
            
            # DÉTECTION 1: Logiciels de retouche photo
            suspicious_creators = [
                'Photoshop', 'GIMP', 'Paint.NET', 'Pixlr',
                'Adobe Illustrator', 'CorelDRAW', 'Inkscape'
            ]
            for creator in suspicious_creators:
                if creator.lower() in metadata['creator'].lower():
                    metadata['suspicious_signs'].append(
                        f'Créé avec logiciel de retouche graphique: {creator}'
                    )
                    metadata['fraud_indicators'].append('graphic_software')
            
            # DÉTECTION 2: Modification après création
            if metadata['modification_date'] and metadata['creation_date']:
                if metadata['modification_date'] != metadata['creation_date']:
                    metadata['suspicious_signs'].append(
                        'Document modifié après création initiale'
                    )
                    metadata['fraud_indicators'].append('post_creation_modification')
            
            # DÉTECTION 3: Créateur/Producteur suspect
            suspicious_producers = [
                'online', 'converter', 'free', 'pdf editor',
                'smallpdf', 'ilovepdf', 'sejda'
            ]
            for producer in suspicious_producers:
                if producer.lower() in metadata['producer'].lower():
                    metadata['suspicious_signs'].append(
                        f'Produit par outil de conversion en ligne: {metadata["producer"]}'
                    )
                    metadata['fraud_indicators'].append('online_tool')
            
            # DÉTECTION 4: Fichier PDF trop récent
            if metadata['creation_date']:
                try:
                    # Parser date PDF (format D:YYYYMMDDHHmmSS)
                    date_str = metadata['creation_date'].replace('D:', '').split('+')[0].split('-')[0]
                    if len(date_str) >= 14:
                        creation_datetime = datetime.strptime(date_str[:14], '%Y%m%d%H%M%S')
                        days_old = (datetime.now() - creation_datetime).days
                        
                        if days_old < 7:
                            metadata['suspicious_signs'].append(
                                f'Document créé il y a seulement {days_old} jours'
                            )
                            metadata['fraud_indicators'].append('recently_created')
                except Exception as e:
                    pass
        
    except Exception as e:
        metadata['error'] = str(e)
        metadata['fraud_indicators'].append('analysis_error')
    
    return metadata


def analyze_image_metadata(file_path):
    """
    Extrait et analyse les métadonnées EXIF d'une image
    
    Args:
        file_path: Chemin vers le fichier image
        
    Returns:
        dict: Métadonnées EXIF et indicateurs de fraude
    """
    metadata = {
        'exif_data': {},
        'camera_model': None,
        'software': None,
        'datetime': None,
        'gps_info': None,
        'suspicious_signs': [],
        'fraud_indicators': []
    }
    
    try:
        image = Image.open(file_path)
        
        # Extraction EXIF
        exif_data = image.getexif()
        
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                metadata['exif_data'][tag] = str(value)
            
            # Champs importants
            metadata['camera_model'] = metadata['exif_data'].get('Model')
            metadata['software'] = metadata['exif_data'].get('Software')
            metadata['datetime'] = metadata['exif_data'].get('DateTime')
            
            # DÉTECTION 1: Logiciel de retouche
            if metadata['software']:
                suspicious_software = [
                    'Photoshop', 'GIMP', 'Paint', 'Pixlr', 'Lightroom'
                ]
                for soft in suspicious_software:
                    if soft.lower() in metadata['software'].lower():
                        metadata['suspicious_signs'].append(
                            f'Image éditée avec: {metadata["software"]}'
                        )
                        metadata['fraud_indicators'].append('image_editing_software')
            
            # DÉTECTION 2: Absence de métadonnées caméra
            if not metadata['camera_model']:
                metadata['suspicious_signs'].append(
                    'Aucune information sur l\'appareil photo (possible screenshot)'
                )
                metadata['fraud_indicators'].append('no_camera_info')
        
        else:
            # Aucune métadonnée EXIF = TRÈS suspect
            metadata['suspicious_signs'].append(
                'AUCUNE métadonnée EXIF - Image probablement manipulée'
            )
            metadata['fraud_indicators'].append('no_exif_data')
        
    except Exception as e:
        metadata['error'] = str(e)
        metadata['fraud_indicators'].append('analysis_error')
    
    return metadata


def get_file_metadata(file_path):
    """
    Analyse automatique selon l'extension du fichier
    
    Args:
        file_path: Chemin vers le fichier
        
    Returns:
        dict: Métadonnées complètes
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        return analyze_pdf_metadata(file_path)
    elif ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
        return analyze_image_metadata(file_path)
    else:
        return {
            'error': f'Extension non supportée: {ext}',
            'fraud_indicators': ['unsupported_format']
        }
