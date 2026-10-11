@echo off
rem Stops the ELTA bot (until next Windows logon or scripts\start_elta_bot.vbs). Other bots are not touched.
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { ($_.Name -eq 'powershell.exe' -and $_.CommandLine -match 'ELTA-bot\\scripts\\run_bot\.ps1') -or ($_.Name -match '^python' -and $_.CommandLine -match 'ELTA-bot\\backend\\src\\main\.py') -or ($_.Name -eq 'cloudflared.exe' -and $_.CommandLine -match '127\.0\.0\.1:8080') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
echo ELTA bot to'xtatildi / ELTA bot stopped.
timeout /t 3 >nul 2>nul
