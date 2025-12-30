[Setup]
AppName=CAR Manager Pro
AppVersion=1.0
DefaultDirName={autopf}\CAR Manager Pro
DefaultGroupName=CAR Manager Pro
OutputDir=Output
OutputBaseFilename=CAR_Manager_Pro_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\CAR Manager Pro.exe

[Files]
Source: "dist\CAR Manager Pro.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\CAR Manager Pro"; Filename: "{app}\CAR Manager Pro.exe"; IconFilename: "{app}\app_icon.ico"
Name: "{commondesktop}\CAR Manager Pro"; Filename: "{app}\CAR Manager Pro.exe"; IconFilename: "{app}\app_icon.ico"

[Run]
Filename: "{app}\CAR Manager Pro.exe"; Description: "Start CAR Manager Pro"; Flags: nowait postinstall skipifsilent
