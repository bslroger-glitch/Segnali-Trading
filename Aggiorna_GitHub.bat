@echo off
color 0A
title Sincronizzazione GitHub in corso...

echo.
echo ==============================================
echo    Sincronizzazione di App Segnali Trading
echo ==============================================
echo.

cd /d "%~dp0"

:: Configura Git se è assente l'identità
git config user.email >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo [!] Configurazione identità Git mancante.
    echo Inserisci i dati per firmare i tuoi salvataggi.
    set /p git_email="Tua Email (es: roger@example.com): "
    set /p git_name="Tuo Nome (es: Roger): "
    git config --global user.email "!git_email!"
    git config --global user.name "!git_name!"
    echo.
    color 0A
)

:: Controllo se e' la primissima volta (per il remote)
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo [!] Rilevato progetto non connesso a server remoto GitHub.
    echo Per favore, crea un nuovo repository VUOTO su GitHub.com
    set /p repo_url="e incolla qui il link (es: https://github.com/TuoNome/Progetto.git): "
    
    git init
    git branch -M main
    git remote add origin "!repo_url!"
    echo.
    color 0A
)

echo [1/3] Aggiungo i file modificati...
git add .
if %errorlevel% neq 0 (
    echo.
    color 0C
    echo ERRORE: Impossibile aggiungere i file. Git e' installato?
    pause
    exit /b %errorlevel%
)

echo.
echo [2/3] Creo il commit temporizzato...
set t=%time: =0%
set ts=%date:/=-%_%t:~0,2%-%t:~3,2%-%t:~6,2%
git commit -m "Auto-Update: Sincronizzazione %ts%"

echo.
echo [3/3] Carico su GitHub...
:: Se e' la prima spinta su un branch vuoto, uso -u
git push -u origin main 2>nul || git push origin main
if %errorlevel% neq 0 (
    echo.
    color 0C
    echo ERRORE: Caricamento fallito. 
    echo Assicurati che il link GitHub sia corretto e di avere i permessi.
    pause
    exit /b %errorlevel%
)

echo.
echo ==============================================
echo        Aggiornamento Completato con Successo!
echo ==============================================
echo.
timeout /t 4
