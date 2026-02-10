"""
Module d'analyse des métadonnées de documents
Détecte les signatures de création, modification et manipulation
"""

from PyPDF2 import PdfReader
from PIL import Image
from PIL.ExifTags import TAGS
import pikepdf
from datetime import datetime
import os


def analyze_document_metadata(file_path):
    """
    Analyse les métadonnées d'un document (PDF ou image)
    
    Args:
        file_path: Chemin vers le fichier
        
    Returns:
        dict: Métadonnées et signes suspects
    """
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return analyze_pdf_metadata(file_path)
    elif file_ext in ['.jpg', '.jpeg', '.png']:
        return analyze_image_metadata(file_path)
    else:
        return {'error': 'Format non supporté'}


def analyze_pdf_metadata(file_path):
    """
    Extrait et analyse les métadonnées d'un PDF
    
    Détecte:
    - Logiciel de création
    - Dates de création/modification
    - Chiffrement
    - Signatures de manipulation
    """
    
    metadata = {
        'creator': None,
        'producer': None,
        'creation_date': None,
        'modification_date': None,
        'is_encrypted': False,
        'suspicious_signs': [],
        'file_size': os.path.getsize(file_path),
        'pages_count': 0
    }
    
    try:
        # Méthode 1 : PyPDF2 pour métadonnées basiques
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            
            if reader.metadata:
                metadata['creator'] = reader.metadata.get('/Creator', 'Unknown')
                metadata['producer'] = reader.metadata.get('/Producer', 'Unknown')
                metadata['creation_date'] = reader.metadata.get('/CreationDate', '')
                metadata['modification_date'] = reader.metadata.get('/ModDate', '')
            
            metadata['pages_count'] = len(reader.pages)
        
        # Méthode 2 : pikepdf pour analyse avancée
        try:
            with pikepdf.open(file_path, allow_overwriting_input=True) as pdf:
                metadata['is_encrypted'] = pdf.is_encrypted
                
                # Détection de logiciels de retouche
                creator_str = str(metadata.get('creator', '')).lower()
                producer_str = str(metadata.get('producer', '')).lower()
                
                suspicious_softwares = [
                    'photoshop', 'gimp', 'paint.net', 'inkscape',
                    'affinity', 'pixelmator', 'sketch'
                ]
                
                for soft in suspicious_softwares:
                    if soft in creator_str or soft in producer_str:
                        metadata['suspicious_signs'].append(
                            f'Document créé avec un logiciel de retouche : {soft.title()}'
                        )
                
                # Vérifier si modifié après création
                if metadata['modification_date'] and metadata['creation_date']:
                    if metadata['modification_date'] != metadata['creation_date']:
                        metadata['suspicious_signs'].append(
                            'Document modifié après sa création initiale'
                        )
                
                # Vérifier dates dans le futur
                try:
                    if metadata['creation_date']:
                        # Format PDF date: D:YYYYMMDDHHmmSS
                        date_str = metadata['creation_date'].replace('D:', '').replace("'", '')[:14]
                        if len(date_str) >= 8:
                            year = int(date_str[:4])
                            month = int(date_str[4:6])
                            day = int(date_str[6:8])
                            
                            doc_date = datetime(year, month, day)
                            
                            if doc_date > datetime.now():
                                metadata['suspicious_signs'].append(
                                    'Date de création dans le futur !'
                                )
                except:
                    pass
        
        except Exception as e:
            metadata['suspicious_signs'].append(f'Erreur analyse avancée: {str(e)}')
    
    except Exception as e:
        metadata['error'] = f'Erreur lecture PDF: {str(e)}'
    
    return metadata


def analyze_image_metadata(file_path):
    """
    Extrait les métadonnées EXIF d'une image
    
    Détecte:
    - Appareil photo / scanner
    - Logiciel de traitement
    - GPS (si présent)
    - Dates
    """
    
    metadata = {
        'camera_model': None,
        'software': None,
        'datetime_original': None,
        'datetime_modified': None,
        'gps_info': None,
        'suspicious_signs': [],
        'file_size': os.path.getsize(file_path)
    }
    
    try:
        image = Image.open(file_path)
        exif_data = image.getexif()
        
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                
                if tag == 'Make':
                    metadata['camera_model'] = value
                elif tag == 'Software':
                    metadata['software'] = value
                elif tag == 'DateTimeOriginal':
                    metadata['datetime_original'] = value
                elif tag == 'DateTime':
                    metadata['datetime_modified'] = value
                elif tag == 'GPSInfo':
                    metadata['gps_info'] = value
            
            # Détection logiciels de retouche
            if metadata['software']:
                suspicious_softwares = ['photoshop', 'gimp', 'lightroom', 'snapseed']
                
                for soft in suspicious_softwares:
                    if soft in metadata['software'].lower():
                        metadata['suspicious_signs'].append(
                            f'Image traitée avec {soft.title()}'
                        )
            
            # Vérifier dates
            if metadata['datetime_original'] and metadata['datetime_modified']:
                if metadata['datetime_original'] != metadata['datetime_modified']:
                    metadata['suspicious_signs'].append(
                        'Image modifiée après la prise de vue'
                    )
        
        else:
            metadata['suspicious_signs'].append(
                'Aucune métadonnée EXIF (potentiellement supprimée)'
            )
    
    except Exception as e:
        metadata['error'] = f'Erreur lecture image: {str(e)}'
    
    return metadata


def detect_metadata_manipulation(metadata):
    """
    Score de manipulation basé sur les métadonnées
    
    Returns:
        float: Score 0-1 (1 = très suspect)
    """
    
    score = 0.0
    
    # +0.3 si logiciel de retouche
    suspicious_signs = metadata.get('suspicious_signs', [])
    for sign in suspicious_signs:
        if 'retouche' in sign.lower() or 'photoshop' in sign.lower():
            score += 0.3
            break
    
    # +0.2 si modification après création
    for sign in suspicious_signs:
        if 'modifié après' in sign.lower():
            score += 0.2
            break
    
    # +0.4 si date dans le futur
    for sign in suspicious_signs:
        if 'futur' in sign.lower():
            score += 0.4
            break
    
    # +0.3 si métadonnées manquantes
    for sign in suspicious_signs:
        if 'aucune métadonnée' in sign.lower():
            score += 0.3
            break
    
    # +0.2 si document chiffré
    if metadata.get('is_encrypted'):
        score += 0.2
    
    return min(score, 1.0)
