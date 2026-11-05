; Inno Setup Script for Voice Changer Pro
; Скрипт сборки инсталлятора для Windows

#define MyAppName "Voice Changer Pro"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Voice Changer Pro Team"
#define MyAppURL "https://github.com"
#define MyAppExeName "VoiceChangerPro.exe"

[Setup]
AppId={{D37E614A-7A8B-4B6A-9147-38C526A3732B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Иконка самого инсталлятора и иконка в «Панели управления»
SetupIconFile=assets\app_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Путь установки по умолчанию (Program Files или AppData)
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Папка и имя итогового файла установщика
OutputDir=release
OutputBaseFilename=VoiceChangerPro_Setup_v{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

; Права установки: подходит и для обычного пользователя, и для администратора
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Упаковываем все скомпилированные файлы из dist\VoiceChangerPro
Source: "dist\VoiceChangerPro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
