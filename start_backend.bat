@echo off
chcp 65001 >nul
echo ==========================================
echo    ProjectKu Web - 启动后端服务
echo ==========================================
echo.

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%back"
set "MAVEN_HOME=E:\AI\LearningSpace\apache-maven-3.9.9"

:: 检查后端是否已运行
netstat -ano | findstr ":8080.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo 后端服务已在运行 (端口 8080)
    echo 地址: http://localhost:8080/api
    echo API文档: http://localhost:8080/api/swagger-ui-custom.html
    pause
    exit /b 0
)

echo 正在启动后端服务...
echo.

cd /d "%BACKEND_DIR%"
set MAVEN_HOME=%MAVEN_HOME%
set PATH=%MAVEN_HOME%\bin;%PATH%

mvn spring-boot:run

pause
