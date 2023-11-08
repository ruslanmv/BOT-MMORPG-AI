Invoke-WebRequest -URI https://github.com/shauleiz/vXboxInterface/releases/download/v1.0.0.1/ScpVBus-x64.zip -Outfile ./dependencies/ScpVBus-x64.zip
Invoke-WebRequest -URI https://github.com/oblitum/Interception/releases/download/v1.0.1/Interception.zip -Outfile ./dependencies/Interception.zip
Expand-Archive dependencies/ScpVBus-x64.zip -DestinationPath ./dependencies -Force
Expand-Archive dependencies/Interception.zip -DestinationPath ./dependencies -Force
Set-Location dependencies/ScpVBus-x64
./devcon.exe install ScpVBus.inf Root\ScpVBus
Set-Location ../
Set-Location "Interception\command line installer"
./install-interception.exe /install
Set-Location ../../../