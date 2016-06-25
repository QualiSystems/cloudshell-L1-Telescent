pyinstaller --onefile driver.spec

taskkill /f /im Telescent.exe

sleep 3

copy dist\Telescent.exe                   "c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers"
copy telescent_runtime_configuration.json "c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers"


