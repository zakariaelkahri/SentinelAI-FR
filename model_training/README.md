# SentinelAI-FR
Objectif : Définir le périmètre fonctionnel pour assister les agents de sécurité via la détection automatique d'incidents, sans reconnaissance faciale.




--------------------------------------------
imges traitment :
Get-ChildItem -File | Where-Object {$_.Extension -eq ".avi"} | ForEach-Object {
>>     Remove-Item -LiteralPath $_.FullName -Force
>> }

----------
 cmd /c del /f /q *.avi   