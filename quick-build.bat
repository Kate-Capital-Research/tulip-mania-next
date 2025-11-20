@echo off
REM quick-build.bat - Fast iteration script for CSS/content changes (Windows)
REM Usage: quick-build.bat [commit message]

echo ==========================================
echo Quick Build ^& Deploy Script
echo ==========================================

REM Get current branch
for /f %%i in ('git branch --show-current') do set BRANCH=%%i
echo Current branch: %BRANCH%

REM Step 1: Pull latest changes
echo.
echo Step 1/5: Pulling latest changes...
git pull origin %BRANCH%
if errorlevel 1 goto error

REM Step 2: Build the book
echo.
echo Step 2/5: Building Jupyter Book...
poetry run jupyter book build --html --all
if errorlevel 1 goto error

REM Step 3: Add changed files
echo.
echo Step 3/5: Adding changes...
git add .

REM Check if there are changes to commit
git diff --staged --quiet
if %errorlevel% equ 0 (
  echo No changes to commit. Exiting.
  goto end
)

REM Step 4: Commit with message
echo.
echo Step 4/5: Committing changes...
if "%~1"=="" (
  set COMMIT_MSG=Quick build: CSS and content updates
) else (
  set COMMIT_MSG=%~1
)
git commit -m "%COMMIT_MSG%"
if errorlevel 1 goto error

REM Step 5: Push to remote
echo.
echo Step 5/5: Pushing to origin/%BRANCH%...
git push origin %BRANCH%
if errorlevel 1 goto error

echo.
echo ==========================================
echo Done! Changes pushed to %BRANCH%
echo ==========================================
goto end

:error
echo.
echo ==========================================
echo ERROR: Build or deploy failed!
echo ==========================================
exit /b 1

:end
