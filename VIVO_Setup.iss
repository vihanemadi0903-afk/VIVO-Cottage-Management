#define MyAppName "VIVO"
#define MyAppVersion "5.0.1"
#define MyAppPublisher "VIVO"
#define MyAppExeName "VIVO.exe"

[Setup]
AppId={{A8C4F3D2-7B91-4E62-9A35-VIVO0201}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\VIVO
DefaultGroupName=VIVO

OutputDir=installer
OutputBaseFilename=VIVO_Setup_5.0.1

Compression=lzma
SolidCompression=yes

WizardStyle=modern

SetupIconFile=assets\icons\logo.ico
UninstallDisplayIcon={app}\VIVO.exe

PrivilegesRequired=admin

DisableProgramGroupPage=yes

[Tasks]
Name: "desktopicon"; \
    Description: "Create a desktop shortcut"; \
    GroupDescription: "Additional shortcuts:"; \
    Flags: unchecked

[Files]

; Main application
Source: "dist\VIVO.exe"; \
    DestDir: "{app}"; \
    Flags: ignoreversion

; Application assets and icons
Source: "assets\*"; \
    DestDir: "{app}\assets"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

; Initial database
Source: "data\vivo.db"; \
    DestDir: "{app}\data"; \
    Flags: ignoreversion onlyifdoesntexist

[Dirs]

; Application data directory
Name: "{app}\data"

[Icons]

; Start Menu shortcut
Name: "{group}\VIVO"; \
    Filename: "{app}\VIVO.exe"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\assets\icons\logo.ico"

; Desktop shortcut
Name: "{autodesktop}\VIVO"; \
    Filename: "{app}\VIVO.exe"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\assets\icons\logo.ico"; \
    Tasks: desktopicon

[Run]

Filename: "{app}\VIVO.exe"; \
    Description: "Launch VIVO"; \
    WorkingDir: "{app}"; \
    Flags: nowait postinstall skipifsilent

[UninstallDelete]

; Remove only installed application files.
; User database and personal data are intentionally preserved.
Type: filesandordirs; Name: "{app}"