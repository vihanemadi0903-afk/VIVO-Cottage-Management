#define MyAppName "VIVO"
#define MyAppVersion "3.0.2"
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
OutputBaseFilename=VIVO_Setup_3.0.2

Compression=lzma
SolidCompression=yes

WizardStyle=modern

SetupIconFile=assets\icons\logo.ico
UninstallDisplayIcon={app}\VIVO.exe

PrivilegesRequired=admin

DisableProgramGroupPage=yes

[Tasks]
Name: "desktopicon"; \
    Description: "ایجاد میانبر روی دسکتاپ"; \
    GroupDescription: "میانبرها:"; \
    Flags: unchecked

[Files]

Source: "dist\VIVO.exe"; \
    DestDir: "{app}"; \
    Flags: ignoreversion

Source: "assets\*"; \
    DestDir: "{app}\assets"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

Source: "data\vivo.db"; \
    DestDir: "{app}\data"; \
    Flags: ignoreversion


[Dirs]

Name: "{app}\data"

[Icons]

; میانبر Start Menu
Name: "{group}\VIVO"; \
    Filename: "{app}\VIVO.exe"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\assets\icons\logo.ico"

; میانبر Desktop
Name: "{autodesktop}\VIVO"; \
    Filename: "{app}\VIVO.exe"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\assets\icons\logo.ico"; \
    Tasks: desktopicon

[Run]

Filename: "{app}\VIVO.exe"; \
    Description: "اجرای VIVO"; \
    WorkingDir: "{app}"; \
    Flags: nowait postinstall skipifsilent

[UninstallDelete]

; فقط فایل‌های نصب‌شده حذف شوند.
; دیتابیس و اطلاعات کاربر عمداً حذف نمی‌شوند.
Type: filesandordirs; Name: "{app}"

