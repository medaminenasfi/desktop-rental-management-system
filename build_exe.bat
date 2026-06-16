@echo off
echo Building Rental Management System...
echo.

REM Create build directory if it doesn't exist
if not exist "build" mkdir build
if not exist "dist" mkdir dist

echo Cleaning previous builds...
rmdir /s /q build
rmdir /s /q dist

echo Building executable with PyInstaller...
pyinstaller --onefile --windowed --name "RentalManagementSystem" --icon=icon.ico main.py

echo.
echo Build completed!
echo Your executable is located in: dist\RentalManagementSystem.exe
echo.
pause
