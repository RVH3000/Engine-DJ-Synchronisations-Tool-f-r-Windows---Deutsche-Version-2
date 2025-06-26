@echo off
title Engine DJ Synchronize - Deutsche EXE erstellen
color 0A

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║          ENGINE DJ SYNCHRONIZE DEUTSCH           ║
echo  ║              EXE Builder v1.1.2                  ║
echo  ║                 Von DJ ABO                       ║
echo  ╚══════════════════════════════════════════════════╝
echo.

REM Prüfen ob Python installiert ist
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo FEHLER: Python ist nicht installiert oder nicht im PATH!
    echo.
    echo Bitte Python von python.org installieren:
    echo https://www.python.org/downloads/
    echo.
    echo Nach der Installation dieses Script erneut ausführen.
    pause
    exit /b 1
)

echo ✅ Python gefunden! Version:
python --version
echo.

echo 📦 Installiere PyInstaller...
pip install pyinstaller --quiet

if %errorlevel% neq 0 (
    echo ❌ Fehler beim Installieren von PyInstaller!
    echo.
    echo Versuche es manuell mit:
    echo pip install pyinstaller
    pause
    exit /b 1
)

echo ✅ PyInstaller installiert!
echo.

echo 🔧 Erstelle deutsche EXE-Datei...
echo Optimiert für: Denon DJ Prime 4+ und Max/MSP Integration
echo.

REM Deutsche EXE erstellen
pyinstaller --onefile --windowed --name "EngineSynchronize-DE-1.1.2" --distpath . EngineSynchronize-DE-1.1.2.py

if %errorlevel% equ 0 (
    echo.
    echo  ╔══════════════════════════════════════════════════╗
    echo  ║                  ERFOLGREICH!                    ║
    echo  ║            Deutsche EXE erstellt!                ║
    echo  ╚══════════════════════════════════════════════════╝
    echo.
    echo 🎯 Die deutsche EXE befindet sich hier:
    echo %CD%\EngineSynchronize-DE-1.1.2.exe
    echo.
    echo 🎵 Features der deutschen Version:
    echo ✅ Vollständig deutsche Benutzeroberfläche
    echo ✅ Windows-optimierte Laufwerk-Erkennung
    echo ✅ Denon DJ Prime 4+ Hardware-Support
    echo ✅ Performance-Daten und Stem-Files Support
    echo ✅ SoundSwitch-Integration für Visuals
    echo ✅ Smartlist-Synchronisation
    echo ✅ Rote Dateien automatisch reparieren
    echo.
    echo 🎛️ READY FOR BERLIN CLUB PERFORMANCE!
    echo.
    echo Starte jetzt: EngineSynchronize-DE-1.1.2.exe
    echo.
    
    REM Aufräumen
    if exist "build" rmdir /s /q "build"
    if exist "EngineSynchronize-DE-1.1.2.spec" del "EngineSynchronize-DE-1.1.2.spec"
    
    echo 🧹 Build-Dateien aufgeräumt.
    echo.
    
) else (
    echo.
    echo ❌ FEHLER beim Erstellen der EXE!
    echo.
    echo Mögliche Lösungen:
    echo 1. Python-Dependencies installieren:
    echo    pip install tkinter sqlite3 pathlib
    echo.
    echo 2. PyInstaller manuell ausführen:
    echo    pyinstaller --onefile EngineSynchronize-DE-1.1.2.py
    echo.
    echo 3. Antivirus-Software temporär deaktivieren
    echo.
    echo 4. Als Administrator ausführen
    echo.
)

echo Drücke eine beliebige Taste zum Beenden...
pause >nul