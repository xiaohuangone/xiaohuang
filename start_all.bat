@echo off
echo ==========================================
echo    ProjectKu Web - Start All Services
echo ==========================================
echo.

set "ROOT=%~dp0"
set "MARIADB_DIR=%ROOT%mariadb\mariadb-10.11.4-winx64"
set "BACKEND_DIR=%ROOT%back"
set "FRONTEND_DIR=%ROOT%frontend"
set "MAVEN_HOME=E:\AI\LearningSpace\apache-maven-3.9.9"

echo [1/3] Checking MariaDB Database...
netstat -ano 2>nul | findstr ":3307" >nul
if %errorlevel% equ 0 (
    echo       MariaDB is running (port 3307)
) else (
    echo       Starting MariaDB...
    start "MariaDB" cmd /c ""%MARIADB_DIR%\bin\mysqld.exe" --datadir="%MARIADB_DIR%\data" --port=3307"
    echo       Waiting for MariaDB to start...
    timeout /t 5 /nobreak >nul
    netstat -ano 2>nul | findstr ":3307" >nul
    if %errorlevel% equ 0 (
        echo       MariaDB started successfully (port 3307)
    ) else (
        echo       MariaDB failed to start
        pause
        exit /b 1
    )
)

echo.
echo [2/3] Checking Backend Service...
netstat -ano 2>nul | findstr ":8080" >nul
if %errorlevel% equ 0 (
    echo       Backend is running (port 8080)
) else (
    echo       Starting Backend...
    start "Backend" cmd /c "cd /d %BACKEND_DIR% ^& set MAVEN_HOME=%MAVEN_HOME% ^& set PATH=%MAVEN_HOME%\bin;%PATH% ^& mvn spring-boot:run"
    echo       Backend starting, please wait...
    timeout /t 60 /nobreak >nul
)

echo.
echo [3/3] Checking Frontend Service...
netstat -ano 2>nul | findstr ":5173" >nul
if %errorlevel% equ 0 (
    echo       Frontend is running (port 5173)
) else (
    echo       Starting Frontend...
    start "Frontend" cmd /c "cd /d %FRONTEND_DIR% ^& npm run dev"
    echo       Frontend starting, please wait...
    timeout /t 15 /nobreak >nul
)

echo.
echo ==========================================
echo     Service Status
echo ==========================================
echo.

echo Database:
netstat -ano 2>nul | findstr ":3307" >nul
if %errorlevel% equ 0 (
    echo   [OK] MariaDB - localhost:3307 (root/123456)
) else (
    echo   [FAIL] MariaDB not running
)

echo.
echo Backend:
netstat -ano 2>nul | findstr ":8080" >nul
if %errorlevel% equ 0 (
    echo   [OK] Spring Boot - http://localhost:8080/api
) else (
    echo   [FAIL] Spring Boot not running
)

echo.
echo Frontend:
netstat -ano 2>nul | findstr ":5173" >nul
if %errorlevel% equ 0 (
    echo   [OK] Vue - http://localhost:5173
) else (
    echo   [FAIL] Vue not running
)

echo.
echo ==========================================
echo     Access URLs
echo ==========================================
echo   Frontend: http://localhost:5173
echo   Backend: http://localhost:8080/api
echo   API Docs: http://localhost:8080/api/swagger-ui-custom.html
echo ==========================================
echo.
pause
