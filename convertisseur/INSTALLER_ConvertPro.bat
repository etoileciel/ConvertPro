@echo off
setlocal EnableDelayedExpansion
title ConvertPro — Installation automatique
color 0B
cls

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║         CONVERTPRO — Installation automatique           ║
echo  ║         Convertisseur de fichiers universel             ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
echo  Ce programme va installer ConvertPro sur votre ordinateur.
echo.
pause

:: ── 1. Vérifier / installer Python ──────────────────────────────────────────
echo.
echo  [1/5]  Vérification de Python...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Python non trouvé. Téléchargement en cours...
    echo  (Cela peut prendre quelques minutes selon votre connexion)
    echo.

    :: Télécharger le programme d'installation Python 3.12
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe' -OutFile '%TEMP%\python_setup.exe'}"

    if not exist "%TEMP%\python_setup.exe" (
        echo  ERREUR : Impossible de télécharger Python.
        echo  Veuillez installer Python 3.12 manuellement depuis https://www.python.org
        pause
        exit /b 1
    )

    echo  Installation de Python 3.12...
    "%TEMP%\python_setup.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_tcltk=1
    
    :: Rafraîchir les variables d'environnement
    call :RefreshPath

    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo  ERREUR : L'installation de Python a échoué.
        echo  Relancez ce fichier en tant qu'administrateur ou installez Python manuellement.
        pause
        exit /b 1
    )
    echo  Python installé avec succès !
) else (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo  Python %%v détecté. OK
)

:: ── 2. Mettre à jour pip ─────────────────────────────────────────────────────
echo.
echo  [2/5]  Mise à jour de pip...
python -m pip install --upgrade pip --quiet

:: ── 3. Installer les dépendances ─────────────────────────────────────────────
echo.
echo  [3/5]  Installation des dépendances (Pillow, reportlab, pypdf, img2pdf...)
echo  (Première installation uniquement — patientez...)
echo.

python -m pip install pillow reportlab pypdf img2pdf pydub pdf2image --quiet
if %errorlevel% neq 0 (
    echo.
    echo  AVERTISSEMENT : Certains paquets n'ont pas pu être installés.
    echo  Les conversions de base fonctionneront quand même.
)

:: Tentative installation ffmpeg-python pour les conversions vidéo/audio
python -m pip install imageio-ffmpeg --quiet

echo  Dépendances installées !

:: ── 4. Créer le dossier d'installation ───────────────────────────────────────
echo.
echo  [4/5]  Copie des fichiers dans le dossier d'installation...

set INSTALL_DIR=%LOCALAPPDATA%\ConvertPro
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copier le script principal
copy /y "%~dp0convertisseur.py" "%INSTALL_DIR%\convertisseur.py" >nul

:: Créer le lanceur
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo pythonw convertisseur.py
) > "%INSTALL_DIR%\ConvertPro.bat"

:: Créer le lanceur .pyw (sans fenêtre console)
copy /y "%INSTALL_DIR%\convertisseur.py" "%INSTALL_DIR%\ConvertPro.pyw" >nul

echo  Fichiers copiés dans : %INSTALL_DIR%

:: ── 5. Créer les raccourcis ───────────────────────────────────────────────────
echo.
echo  [5/5]  Création des raccourcis...

set DESKTOP=%USERPROFILE%\Desktop
set STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs

:: Raccourci bureau via PowerShell
powershell -Command "& {$ws=[Runtime.InteropServices.Marshal]::GetActiveObject('WScript.Shell'); $sl=$ws.CreateShortcut('%DESKTOP%\ConvertPro.lnk'); $sl.TargetPath='pythonw.exe'; $sl.Arguments='\"%INSTALL_DIR%\convertisseur.py\"'; $sl.WorkingDirectory='%INSTALL_DIR%'; $sl.IconLocation='pythonw.exe,0'; $sl.Save()}" >nul 2>&1

:: Méthode de secours si WScript n'est pas disponible
if not exist "%DESKTOP%\ConvertPro.lnk" (
    powershell -Command "& {$s=(New-Object -COM WScript.Shell).CreateShortcut('%DESKTOP%\ConvertPro.lnk'); $s.TargetPath='%SystemRoot%\System32\cmd.exe'; $s.Arguments='/c \"%INSTALL_DIR%\ConvertPro.bat\"'; $s.WorkingDirectory='%INSTALL_DIR%'; $s.Save()}"
)

:: Raccourci menu Démarrer
if not exist "%STARTMENU%\ConvertPro" mkdir "%STARTMENU%\ConvertPro"
powershell -Command "& {$s=(New-Object -COM WScript.Shell).CreateShortcut('%STARTMENU%\ConvertPro\ConvertPro.lnk'); $s.TargetPath='%SystemRoot%\System32\cmd.exe'; $s.Arguments='/c \"%INSTALL_DIR%\ConvertPro.bat\"'; $s.WorkingDirectory='%INSTALL_DIR%'; $s.Save()}" >nul 2>&1

:: Raccourci désinstallation
(
echo @echo off
echo title ConvertPro — Désinstallation
echo echo Désinstallation de ConvertPro...
echo rmdir /s /q "%INSTALL_DIR%"
echo del /f "%DESKTOP%\ConvertPro.lnk"
echo rmdir /s /q "%STARTMENU%\ConvertPro"
echo echo ConvertPro a été désinstallé.
echo pause
) > "%INSTALL_DIR%\Désinstaller ConvertPro.bat"

:: ── Fin ───────────────────────────────────────────────────────────────────────
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║              INSTALLATION TERMINÉE !                    ║
echo  ║                                                          ║
echo  ║  Un raccourci a été créé sur votre Bureau.              ║
echo  ║  Double-cliquez sur "ConvertPro" pour démarrer.        ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

set /p LAUNCH="  Lancer ConvertPro maintenant ? (O/N) : "
if /i "!LAUNCH!"=="O" (
    start "" pythonw "%INSTALL_DIR%\convertisseur.py"
)

echo.
echo  Merci d'utiliser ConvertPro !
timeout /t 4 >nul
exit /b 0

:: ── Sous-routine rafraîchir PATH ─────────────────────────────────────────────
:RefreshPath
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USERPATH=%%b"
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SYSPATH=%%b"
set "PATH=%SYSPATH%;%USERPATH%"
goto :eof
