' Запускает бота ELTA в фоне, без окна. Ярлык на этот файл лежит в автозагрузке Windows.
' Можно запустить и вручную двойным щелчком.
Set sh = CreateObject("WScript.Shell")
dir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
sh.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & dir & "\run_bot.ps1""", 0, False
