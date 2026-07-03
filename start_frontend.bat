@echo off
chcp 65001 >nul
echo ==========================================
echo    ProjectKu Web - 启动前端服务
echo ==========================================
echo.

set "ROOT=%~dp0"
set "FRONTEND_DIR=%ROOT%frontend"

:: 检查前端是否已运行
netstat -ano | findstr ":5173.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo 前端服务已在运行 (端口 5173)
    echo 地址: http://localhost:5173
    pause
    exit /b 0
)

echo 正在启动前端服务...
echo.

cd /d "%FRONTEND_DIR%"
npm run dev

pause
