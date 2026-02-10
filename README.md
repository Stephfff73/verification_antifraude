# 🔍 In'li - Système Anti-Fraude Documentaire

Application de détection automatique de fraude dans les dossiers de candidature locataire.

## 📋 Vue d'ensemble

Cette application analyse automatiquement les documents fournis par les postulants locataires pour détecter :
- Modifications de documents
- Retouches graphiques
- Incohérences de données
- Contradictions entre documents

### 📄 Documents analysés

- ✅ Contrat de travail
- ✅ Fiches de paie (3 dernières)
- ✅ Avis d'imposition
- ✅ Pièce d'identité
- ✅ Quittances de loyer
- ✅ Justificatifs CAF (APL)

## 🚀 Installation

### Prérequis

- Python 3.9 ou supérieur
- Tesseract OCR installé sur votre système

#### Installation de Tesseract

**Ubuntu/Debian :**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-fra poppler-utils
```

**macOS :**
```bash
brew install tesseract tesseract-lang poppler
```

**Windows :**
Téléchargez l'installateur depuis : https://github.com/UB-Mannheim/tesseract/wiki

### Installation du projet

1. Clonez le repository :
```bash
git clone https://github.com/VOTRE_USERNAME/inli-antifraud-verification.git
cd inli-antifraud-verification
```

2. Créez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Créez les dossiers nécessaires :
```bash
mkdir -p data/uploads data/results
touch data/uploads/.gitkeep data/results/.gitkeep
```

## 🎯 Utilisation

### Lancement en local

```bash
streamlit run app_fraud.py
```

L'application sera accessible à l'adresse : http://localhost:8501

### Workflow

1. **Upload des documents** : Uploadez tous les documents du dossier locataire
2. **Analyse automatique** : Lancez l'analyse qui va :
   - Extraire les métadonnées
   - Effectuer l'OCR
   - Vérifier chaque document
   - Croiser les données
3. **Consultation des résultats** : Consultez le score de fraude et les anomalies détectées
4. **Génération du rapport** : Téléchargez un rapport PDF complet

## 📊 Fonctionnalités

### Détection de fraude

#### 1. Analyse des métadonnées
- Logiciel de création
- Dates de création/modification
- Signatures de manipulation

#### 2. Extraction OCR
- Texte intégral
- Données structurées (SIRET, dates, montants)
- Validation de format

#### 3. Vérifications spécifiques

**Contrat de travail :**
- Présence SIRET employeur
- Clauses obligatoires
- Cohérence des dates

**Fiches de paie :**
- Numéro URSSAF
- Calculs brut/net/cotisations
- Consécutivité des mois

**Avis d'imposition :**
- Numéro fiscal
- Cachet DGFiP
- Cohérence revenus

**Pièce d'identité :**
- Numéro de document
- Date de validité
- Mentions officielles

**Quittances de loyer :**
- Montant et période
- Coordonnées bailleur
- Adresse logement

#### 4. Validation croisée
- Cohérence des adresses
- Identité (nom/prénom)
- Revenus (fiches de paie vs impôts)
- SIRET employeur unique

### Scoring

Le système calcule un score de fraude de 0 à 100 :

- **0-20 : ✅ Dossier fiable** - Acceptation recommandée
- **20-40 : ⚠️ Vigilance** - Vérification manuelle suggérée
- **40-70 : 🔴 Suspicion** - Vérification approfondie requise
- **70-100 : 🚨 Fraude probable** - Rejet recommandé

## 🌐 Déploiement sur Streamlit Cloud

### Étape 1 : Créer le repository GitHub

1. Créez un nouveau repository sur GitHub (privé recommandé pour RGPD)
2. Pushez le code :

```bash
git init
git add .
git commit -m "Initial commit - In'li Anti-Fraude System"
git branch -M main
git remote add origin https://github.com/VOTRE_USERNAME/inli-antifraud-verification.git
git push -u origin main
```

### Étape 2 : Déployer sur Streamlit Cloud

1. Allez sur https://share.streamlit.io
2. Connectez-vous avec votre compte GitHub
3. Cliquez sur "New app"
4. Sélectionnez :
   - Repository : `inli-antifraud-verification`
   - Branch : `main`
   - Main file path : `app_fraud.py`
5. Cliquez sur "Deploy!"

### Étape 3 : Configuration des dépendances système

Créez un fichier `packages.txt` à la racine :

```
tesseract-ocr
tesseract-ocr-fra
poppler-utils
libgl1
```

Puis re-déployez :

```bash
git add packages.txt
git commit -m "Add system dependencies"
git push
```

### Étape 4 : Variables d'environnement (optionnel)

Si vous avez des clés API, créez un fichier `.streamlit/secrets.toml` :

```toml
[api]
entreprise_api_key = "votre_clé"
```

**⚠️ Ne commitez JAMAIS ce fichier !**

Ajoutez les secrets via l'interface Streamlit Cloud : Settings > Secrets

## 📂 Structure du projet

```
inli-antifraud-verification/
│
├── app_fraud.py              # Application Streamlit principale
├── requirements.txt          # Dépendances Python
├── packages.txt              # Dépendances système (Streamlit Cloud)
├── .gitignore               # Fichiers à ignorer
├── README.md                # Ce fichier
│
├── utils/                   # Modules utilitaires
│   ├── __init__.py
│   ├── metadata_analyzer.py    # Analyse métadonnées
│   ├── ocr_processor.py        # OCR et extraction
│   ├── fraud_detector.py       # Détection fraude
│   ├── cross_validator.py      # Validation croisée
│   └── scoring_engine.py       # Scoring et rapports
│
├── config/                  # Configuration
│   ├── __init__.py
│   └── settings.py
│
└── data/                    # Données (gitignored)
    ├── uploads/            # Documents uploadés
    └── results/            # Rapports générés
```

## 🔒 Sécurité et RGPD

### Données sensibles

- ❌ **Ne jamais commiter** les documents uploadés
- ❌ **Ne jamais commiter** les rapports générés
- ✅ Toujours vérifier que `data/` est dans `.gitignore`

### Recommandations

1. **Repository privé** obligatoire
2. **Chiffrement** des données au repos (si déploiement production)
3. **Suppression automatique** des documents après X jours
4. **Logs d'accès** pour traçabilité
5. **Conformité RGPD** : informer les utilisateurs du traitement

## 🛠️ Développement

### Tests

```bash
# Lancer les tests unitaires (à implémenter)
pytest tests/
```

### Contribution

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📈 Améliorations futures

### Version 1.1
- [ ] Génération de rapports PDF formatés (ReportLab)
- [ ] Export Excel des résultats
- [ ] Détection avancée d'images manipulées (ELA, détection copier-coller)
- [ ] Vérification SIRET via API entreprise.data.gouv.fr

### Version 1.2
- [ ] Authentification utilisateur
- [ ] Base de données pour historique
- [ ] Tableau de bord statistiques
- [ ] API REST

### Version 2.0
- [ ] IA pour détection avancée (modèles ML)
- [ ] OCR amélioré avec deep learning
- [ ] Détection de deepfakes sur photos d'identité
- [ ] Intégration ERP In'li

## 📝 Licence

Propriétaire - In'li - Tous droits réservés

## 👥 Support

Pour toute question ou problème :
- Email : support@inli.fr
- Issues GitHub : [Créer une issue](https://github.com/VOTRE_USERNAME/inli-antifraud-verification/issues)

## 🙏 Crédits

Développé par l'équipe technique In'li avec l'assistance de Claude AI (Anthropic).

---

**Version Beta 1.0** - Février 2026
