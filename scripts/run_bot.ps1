# Запускает бота ELTA и перезапускает его, если он остановился.
# Обычно запускается скрыто через scripts\start_elta_bot.vbs (автозагрузка Windows).
$root = Split-Path -Parent $PSScriptRoot          # папка проекта ELTA-bot
Set-Location -LiteralPath (Join-Path $root 'backend')
$logs = Join-Path $root 'logs'
New-Item -ItemType Directory -Force $logs | Out-Null
$log = Join-Path $logs 'bot.log'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUNBUFFERED = '1'

# Вторую копию не запускаем
$others = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" |
    Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine -match 'run_bot\.ps1' }
if ($others) { exit }

$python = Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps\python.exe'
if (-not (Test-Path $python)) { $python = 'python' }

while ($true) {
    # После включения компьютера интернет появляется не сразу — ждём Telegram
    while (-not (Test-NetConnection api.telegram.org -Port 443 -InformationLevel Quiet -WarningAction SilentlyContinue)) {
        Start-Sleep 10
    }
    # Убираем туннель, оставшийся от прошлого запуска
    Get-CimInstance Win32_Process -Filter "Name='cloudflared.exe'" |
        Where-Object { $_.CommandLine -match '127\.0\.0\.1:8080' } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

    if (Test-Path $log) { Move-Item $log (Join-Path $logs 'bot.prev.log') -Force }
    "=== запуск $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File $log -Encoding utf8
    cmd /c "`"$python`" `"$root\backend\src\main.py`" >> `"$log`" 2>&1"
    "=== бот остановился (код $LASTEXITCODE) $(Get-Date -Format 'HH:mm:ss'), перезапуск через 10 сек ===" |
        Out-File $log -Append -Encoding utf8
    Start-Sleep 10
}
