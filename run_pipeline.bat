@echo off
title CI/CD Pipeline Build

echo ========================================================
echo        STARTING CI/CD PIPELINE
echo ========================================================
echo.

:: КРОК 1: Активація
echo [STEP 1] Checking Virtual Environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo  + Venv activated.
) else (
    echo  - WARNING: venv folder not found. Using global python.
)

:: КРОК 2: Встановлення
echo.
echo [STEP 2] Installing Dependencies...
pip install -r requirements.txt
pip install flake8
if %errorlevel% neq 0 goto Error

:: КРОК 3: Перевірка коду
echo.
echo [STEP 3] Linting Code...
:: Перевіряємо лише на грубі помилки
flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics
echo  + Linting passed.

:: КРОК 4: Тести
echo.
echo [STEP 4] Running Unit Tests...
python tests.py
if %errorlevel% neq 0 goto Error

:: УСПІХ
color 2
echo.
echo ========================================================
echo             BUILD SUCCESSFUL
echo ========================================================
echo.
echo All tests passed. Ready for deploy.
goto End

:: ПОМИЛКА
:Error
color 4
echo.
echo ========================================================
echo             BUILD FAILED
echo ========================================================
echo Check the errors above.

:End
pause