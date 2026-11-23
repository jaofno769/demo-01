@echo off
setlocal
pushd "%~dp0" || exit /b 1

if not exist ".venv\Scripts\python.exe" (
    echo Python environment missing. Run: uv venv --python 3.11
    echo Then run: uv pip install -r requirements.txt
    pause
    exit /b 1
)

where node.exe >nul 2>&1
if errorlevel 1 (
    echo Node.js is missing from PATH. Install Node.js before running this script.
    pause
    exit /b 1
)

if not exist "node_modules\concurrently\package.json" goto missing_dev_deps
if not exist "node_modules\nodemon\bin\nodemon.js" goto missing_dev_deps
if not exist "node_modules\vite\bin\vite.js" goto missing_dev_deps

node dev.cjs
set "dev_exit=%errorlevel%"
popd
exit /b %dev_exit%

:missing_dev_deps
echo Development dependencies missing. Run: npm ci
pause
exit /b 1
