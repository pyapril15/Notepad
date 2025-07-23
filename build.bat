@echo off
echo ============================================
echo     Modern Notepad - Build Script
echo              Version 1.0.0
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH!
    echo Please install Python 3.7 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not available!
    echo Please ensure pip is installed with Python.
    echo.
    pause
    exit /b 1
)

echo Installing/Updating dependencies...
echo This may take a few minutes for first-time installation...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Error: Failed to install dependencies!
    echo Please check your internet connection and try again.
    echo.
    echo Trying to install core dependencies individually...
    pip install pyspellchecker>=0.7.0

    if errorlevel 1 (
        echo Error: Could not install core dependencies!
        pause
        exit /b 1
    )
)

REM Install PyInstaller separately to ensure it's available
echo Installing PyInstaller for building executable...
pip install pyinstaller>=6.0.0
if errorlevel 1 (
    echo Warning: Failed to install PyInstaller, build may fail
)

echo.
echo Dependencies installed successfully!
echo.

REM Check if main.py exists
if not exist "main.py" (
    echo Error: main.py not found!
    echo Please ensure you are running this script from the project directory.
    echo Current directory: %cd%
    echo.
    pause
    exit /b 1
)

REM Create assets directory structure if it doesn't exist
if not exist "assets" (
    echo Creating assets directory structure...
    mkdir assets
    mkdir assets\icons
    mkdir assets\fonts
    mkdir assets\screenshots
    mkdir assets\toolbar
    echo Please place your notepad.ico file in assets\icons\ directory
    echo.
)

if not exist "assets\icons" mkdir assets\icons
if not exist "assets\fonts" mkdir assets\fonts
if not exist "assets\screenshots" mkdir assets\screenshots
if not exist "assets\toolbar" mkdir assets\toolbar

REM Check for required directories
if not exist "features" (
    echo Warning: features directory not found!
    echo Creating empty features directory...
    mkdir features
    echo. > features\__init__.py
)

if not exist "themes" (
    echo Warning: themes directory not found!
    echo Creating empty themes directory...
    mkdir themes
    echo. > themes\__init__.py
)

if not exist "ui" (
    echo Warning: ui directory not found!
    echo Creating empty ui directory...
    mkdir ui
    echo. > ui\__init__.py
)

if not exist "utils" (
    echo Warning: utils directory not found!
    echo Creating empty utils directory...
    mkdir utils
    echo. > utils\__init__.py
)

REM Check for icon file
if not exist "assets\icons\notepad.ico" (
    echo Warning: Icon file not found at assets\icons\notepad.ico
    echo The executable will be built without a custom icon.
    echo You can add the icon file later and rebuild.
    echo.
)

REM Test the application before building
echo Testing the application...
python -c "import main; print('Application import test: OK')"
if errorlevel 1 (
    echo Error: Application failed import test!
    echo Please check for syntax errors in main.py
    echo.
    pause
    exit /b 1
)

echo Application test passed!
echo.

echo Cleaning previous build files...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "Modern_Notepad.spec" del "Modern_Notepad.spec"
echo.

echo ============================================
echo       Building Modern Notepad
echo ============================================
echo.
echo This process will:
echo • Create a standalone executable (.exe)
echo • Include all dependencies
echo • Bundle assets and modules
echo • Optimize for performance
echo • Create distribution files
echo.
echo Please wait... This may take 5-10 minutes
echo.

REM Build using Python setup script
python setup.py
if errorlevel 1 (
    echo.
    echo Error: Build failed!
    echo Trying alternative build method...
    echo.

    REM Alternative build using direct PyInstaller command
    if exist "assets\icons\notepad.ico" (
        echo Building with custom icon...
        pyinstaller --onefile ^
                    --windowed ^
                    --name=Modern_Notepad ^
                    --icon=assets/icons/notepad.ico ^
                    --distpath=dist ^
                    --workpath=build ^
                    --clean ^
                    --noconfirm ^
                    --optimize=2 ^
                    --noupx ^
                    --hidden-import=tkinter ^
                    --hidden-import=tkinter.ttk ^
                    --hidden-import=tkinter.messagebox ^
                    --hidden-import=tkinter.filedialog ^
                    --hidden-import=tkinter.scrolledtext ^
                    --hidden-import=pyspellchecker ^
                    --hidden-import=features ^
                    --hidden-import=themes ^
                    --hidden-import=ui ^
                    --hidden-import=utils ^
                    --add-data=assets;assets ^
                    --add-data=features;features ^
                    --add-data=themes;themes ^
                    --add-data=ui;ui ^
                    --add-data=utils;utils ^
                    main.py
    ) else (
        echo Building without custom icon...
        pyinstaller --onefile ^
                    --windowed ^
                    --name=Modern_Notepad ^
                    --distpath=dist ^
                    --workpath=build ^
                    --clean ^
                    --noconfirm ^
                    --optimize=2 ^
                    --noupx ^
                    --hidden-import=tkinter ^
                    --hidden-import=tkinter.ttk ^
                    --hidden-import=tkinter.messagebox ^
                    --hidden-import=tkinter.filedialog ^
                    --hidden-import=tkinter.scrolledtext ^
                    --hidden-import=pyspellchecker ^
                    --hidden-import=features ^
                    --hidden-import=themes ^
                    --hidden-import=ui ^
                    --hidden-import=utils ^
                    --add-data=assets;assets ^
                    --add-data=features;features ^
                    --add-data=themes;themes ^
                    --add-data=ui;ui ^
                    --add-data=utils;utils ^
                    main.py
    )

    if errorlevel 1 (
        echo.
        echo Error: Both build methods failed!
        echo Please check the error messages above and try the following:
        echo 1. Ensure all dependencies are installed correctly
        echo 2. Check that main.py has no syntax errors
        echo 3. Verify that PyInstaller is properly installed
        echo 4. Make sure all required directories exist
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ============================================
echo           Build Completed Successfully!
echo ============================================
echo.

REM Check if executable was created
if not exist "dist\Modern_Notepad.exe" (
    echo Error: Executable was not created!
    echo Please check the build logs above for errors.
    echo.
    pause
    exit /b 1
)

REM Get file size
for %%A in ("dist\Modern_Notepad.exe") do set SIZE=%%~zA
set /a SIZE_MB=%SIZE%/1024/1024

echo Build Summary:
echo • Executable: dist\Modern_Notepad.exe
echo • File size: %SIZE_MB% MB
echo • Build date: %date% %time%
echo.

echo Distribution files created:
if exist "dist\README_DIST.txt" echo • README_DIST.txt - User documentation
if exist "dist\LICENSE.txt" echo • LICENSE.txt - License information
echo.

REM Ask if user wants to test the executable
set /p test="Test the executable now? (y/n): "
if /i "%test%"=="y" (
    echo Launching Modern Notepad for testing...
    echo The application should start in a few seconds...
    echo Close it when you're satisfied with the test.
    echo.
    start "" "dist\Modern_Notepad.exe"

    REM Wait a moment then check if it's running
    timeout /t 3 /nobreak >nul
    tasklist /FI "IMAGENAME eq Modern_Notepad.exe" 2>NUL | find /I /N "Modern_Notepad.exe">NUL
    if errorlevel 1 (
        echo Warning: Application may not have started correctly.
        echo Please manually test the executable in the dist folder.
    ) else (
        echo ✓ Application started successfully!
    )
    echo.
)

REM Ask about cleanup
set /p cleanup="Clean up build files? (y/n): "
if /i "%cleanup%"=="y" (
    echo Cleaning up temporary build files...
    if exist "build" rmdir /s /q "build"
    if exist "Modern_Notepad.spec" del "Modern_Notepad.spec"
    if exist "__pycache__" rmdir /s /q "__pycache__"
    if exist "features\__pycache__" rmdir /s /q "features\__pycache__"
    if exist "themes\__pycache__" rmdir /s /q "themes\__pycache__"
    if exist "ui\__pycache__" rmdir /s /q "ui\__pycache__"
    if exist "utils\__pycache__" rmdir /s /q "utils\__pycache__"
    echo Cleanup completed.
    echo.
)

echo ============================================
echo            Build Process Complete!
echo ============================================
echo.
echo Your Modern Notepad is ready!
echo.
echo 📁 Location: %cd%\dist\Modern_Notepad.exe
echo 💾 Size: %SIZE_MB% MB
echo 🎯 Status: Ready for distribution
echo.
echo Features included in your build:
echo ✓ Advanced text editing capabilities
echo ✓ Syntax highlighting support
echo ✓ Multiple themes and customization
echo ✓ Find and replace functionality
echo ✓ Auto-save and recovery features
echo ✓ Spell checking (if enabled)
echo ✓ Line numbers and word wrap
echo ✓ Tabbed interface support
echo ✓ Professional user interface
echo.
echo Next Steps:
echo • Test the executable thoroughly
echo • Test all features and themes
echo • Verify spell checking works
echo • Test file operations
echo • Share with users or distribute
echo • Gather feedback for improvements
echo.

REM Create a simple batch file to run the application
echo @echo off > "Run_Modern_Notepad.bat"
echo cd /d "%~dp0" >> "Run_Modern_Notepad.bat"
echo start "" "dist\Modern_Notepad.exe" >> "Run_Modern_Notepad.bat"

echo Created Run_Modern_Notepad.bat for easy launching.
echo.

echo Thank you for using the Modern Notepad build system!
echo.
echo Press any key to exit...
pause >nul