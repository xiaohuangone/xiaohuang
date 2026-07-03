@echo off
chcp 65001 >nul 2>&1
color 0A

:: Kill allure common port process
for %%p in (51195 5050 8080) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
)

:: Delete old result dir
if exist allure-results rd /s /q allure-results
:: Delete old report dir
if exist allure-report rd /s /q allure-report

echo Clean finished!
echo Please run test case first to generate allure-results
pause

:: Start allure service
allure serve allure-results
pause