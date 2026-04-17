@echo off
:: ================================================================
:: E-Shelle — Lancement de l'Agent Facebook IA
:: Lance le Worker Celery + le Beat Scheduler dans 2 fenêtres
:: ================================================================

SET PYTHON=C:\Users\USER\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
SET PROJECT_DIR=%~dp0
SET MANAGE=%PROJECT_DIR%manage.py

echo ============================================
echo   E-Shelle — Agent Facebook IA
echo ============================================
echo.

:: Vérifier que Python existe
if not exist "%PYTHON%" (
    echo [ERREUR] Python introuvable : %PYTHON%
    echo Modifie la variable PYTHON dans ce fichier.
    pause
    exit /b 1
)

:: Vérifier la connexion Redis (optionnel, continue si absent)
echo [1/3] Verification Redis...
%PYTHON% -c "import redis; r = redis.from_url('redis://localhost:6379/0'); r.ping(); print('Redis OK')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [AVERT] Redis local non disponible. Verifie CELERY_BROKER_URL dans .env
    echo         → Utilise Upstash ou installe Memurai : https://www.memurai.com/
    echo.
)

:: Lancer le Worker Celery dans une nouvelle fenêtre
echo [2/3] Lancement du Worker Celery...
start "Celery Worker — E-Shelle FB Agent" cmd /k "cd /d "%PROJECT_DIR%" && "%PYTHON%" -m celery -A edu_cm worker --loglevel=info --concurrency=2 -n worker1@%%h"

:: Attendre 2s pour que le worker démarre
timeout /t 2 /nobreak >nul

:: Lancer le Beat Scheduler dans une nouvelle fenêtre
echo [3/3] Lancement du Beat Scheduler...
start "Celery Beat — E-Shelle FB Agent" cmd /k "cd /d "%PROJECT_DIR%" && "%PYTHON%" -m celery -A edu_cm beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler"

echo.
echo ============================================
echo   Agent demarré ! Deux fenetres ouvertes :
echo   - "Celery Worker"  : execute les tâches
echo   - "Celery Beat"    : planifie les tâches
echo.
echo   Dashboard : http://localhost:8000/facebook-agent/
echo   Admin     : http://localhost:8000/admin/facebook_agent/
echo ============================================
echo.
pause
