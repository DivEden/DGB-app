@echo off
echo ================================
echo SARA Museum Soege App
echo ================================
echo.
echo Aktiverer virtuelt miljoe og starter app...
cd /d "C:\Users\mfed\Desktop\App\museum_search_app"
call venv\Scripts\activate.bat

echo.
echo Starting SARA Museum Search App...
python main.py

echo.
echo App afsluttet.
pause