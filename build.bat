@echo off
cd /d "%~dp0"
echo ========================================================
echo   [1/3] Проверка и подготовка виртуального окружения...
echo ========================================================

if not exist .venv\Scripts\python.exe (
    echo Окружение .venv не найдено. Создание .venv...
    python -m venv .venv
)

call .\.venv\Scripts\activate.bat
echo Установка / обновление зависимостей и PyInstaller...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo ========================================================
echo   [2/3] Компиляция приложения через VoiceChangerPro.spec...
echo ========================================================
pyinstaller VoiceChangerPro.spec --clean -y

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Сборка завершилась с ошибкой!
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo   [3/3] Сборка успешно завершена!
echo ========================================================
echo Скомпилированная программа: dist\VoiceChangerPro\VoiceChangerPro.exe
echo.
echo Теперь откройте файл installer.iss в Inno Setup и нажмите кнопку 'Compile' (Ctrl+F9),
echo чтобы собрать готовый установочный файл в папку 'release\'.
echo ========================================================
pause
