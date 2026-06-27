# ConvertPro — Convertisseur de fichiers universel
## Guide d'utilisation

---

## 📦 Installation

### Étapes simples :
1. **Placez ces 2 fichiers dans le même dossier** :
   - `INSTALLER_ConvertPro.bat`
   - `convertisseur.py`

2. **Double-cliquez sur `INSTALLER_ConvertPro.bat`**

3. L'installateur fait tout automatiquement :
   - Vérifie si Python est installé (et le télécharge si absent)
   - Installe toutes les bibliothèques nécessaires
   - Copie les fichiers dans `%LOCALAPPDATA%\ConvertPro`
   - Crée un raccourci sur votre **Bureau** et dans le **menu Démarrer**

4. Cliquez **"O"** pour lancer ConvertPro immédiatement !

---

## 🔄 Conversions disponibles

| Type | De | Vers |
|------|-----|------|
| Image → PDF | JPG, PNG, BMP, GIF, WEBP, TIFF | PDF |
| PDF → Images | PDF | PNG (une image par page) |
| Image → Image | JPG, PNG, BMP, GIF, WEBP, TIFF | Format au choix |
| PNG → JPEG | PNG | JPG |
| JPEG → PNG | JPG, JPEG | PNG |
| Texte → PDF | TXT, CSV | PDF |
| MP4 → MP3 | MP4, AVI, MKV, MOV | MP3 (nécessite FFmpeg) |
| MP4 → AVI | MP4 | AVI (nécessite FFmpeg) |
| Fusion PDF | PDF (plusieurs fichiers) | Un seul PDF fusionné |

---

## 🎬 Conversions vidéo/audio (optionnel)

Pour activer les conversions MP4/MP3/AVI, installez **FFmpeg** :
1. Téléchargez FFmpeg : https://ffmpeg.org/download.html
2. Extrayez l'archive
3. Ajoutez le dossier `bin` au PATH Windows

---

## 🗑️ Désinstallation

Ouvrez `%LOCALAPPDATA%\ConvertPro\` et lancez `Désinstaller ConvertPro.bat`

---

## ⚠️ Notes

- Windows 10 / 11 recommandé
- Python 3.8+ requis (téléchargé automatiquement si absent)
- Connexion internet requise lors de la première installation
- Si le raccourci bureau ne se crée pas, lancez le BAT en tant qu'administrateur
