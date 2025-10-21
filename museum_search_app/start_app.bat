@echo off
echo ================================
echo SARA Museum Soege App
echo ================================
echo.
echo Aktiverer virtuelt miljoe...
call venv\Scripts\activate.bat

echo.
@echo off
echo Starting SARA Museum Search App...
cd /d "C:\Users\mfed\Desktop\App\museum_search_app"
call venv\Scripts\activate.bat
python main.py
pause
echo (Tryk Ctrl+C for at afslutte)
echo.

python main.py

echo.
echo App afsluttet.
pause