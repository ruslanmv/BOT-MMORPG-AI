; Custom NSIS template for Tauri (v1.4+).
; This file is used by tauri-cli to generate the final installer.
; Variables are injected by the bundler at build time.
; Adds driver installation step (Interception + vJoy) during install.
; Includes component selection wizard for optional features.

!include "MUI2.nsh"
!include "Sections.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

; Use LZMA solid compression to handle large file counts efficiently.
; SOLID mode compresses all data as a single stream, reducing both
; installer size and NSIS compile-time memory issues with many files.
SetCompressor /SOLID lzma
SetDatablockOptimize on

; -----------------------------------------------------------------------------
; Canonical tauri-bundler 1.6.x defines.
;
; MAINBINARYSRCPATH: source path of the freshly built Rust binary, injected by
; the bundler. Using this two-step indirection (rather than inlining
; {{main_binary_path}} into a quoted File argument) is the pattern used by the
; official tauri-v1.6.6 installer.nsi (lines 29-30, 541-542). The direct-inline
; form passes raw Windows paths through Handlebars without unescape-dollar-sign
; and can produce a string NSIS parses oddly.
;
; MAINBINARYNAME: forced UPPERCASE here. tauri-bundler derives the handlebars
; var {{main_binary_name}} from Cargo.toml's name (lowercase: "bot-mmorpg-ai"),
; not from productName ("BOT-MMORPG-AI"). Every shortcut, registry key, and
; MUI_FINISHPAGE_RUN below references ${MAINBINARYNAME}.exe and we want them
; all to land on BOT-MMORPG-AI.exe consistently.
; -----------------------------------------------------------------------------
!define MAINBINARYNAME "BOT-MMORPG-AI"
!define MAINBINARYSRCPATH "{{main_binary_path}}"

Name "{{product_name}}"
OutFile "{{out_file}}"

; Force a stable default folder (per-machine).
; $PROGRAMFILES64 resolves to "C:\Program Files" on 64-bit Windows.
InstallDir "$PROGRAMFILES64\BOT-MMORPG-AI"

; Remember previous install location for upgrades/reinstalls
InstallDirRegKey HKLM "Software\BOT-MMORPG-AI" "InstallDir"

; We need admin to install drivers reliably.
RequestExecutionLevel admin

; --- UI Customization ---
!define MUI_ABORTWARNING
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP_NOSTRETCH
!define MUI_WELCOMEFINISHPAGE_BITMAP_NOSTRETCH

; Custom text for welcome page
!define MUI_WELCOMEPAGE_TITLE "Welcome to BOT MMORPG AI Setup"
!define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of BOT MMORPG AI.$\r$\n$\r$\nBOT MMORPG AI is a powerful gaming assistant with AI capabilities. You can choose to install just the core application or include optional AI models for enhanced features.$\r$\n$\r$\nClick Next to continue."

; Custom text for components page
!define MUI_COMPONENTSPAGE_TEXT_TOP "Select the components you want to install. The core application (UI + Backend) is required. AI models are optional and can be downloaded later if needed."
!define MUI_COMPONENTSPAGE_TEXT_COMPLIST "Check the components to install:"

; Custom text for finish page
!define MUI_FINISHPAGE_TITLE "Installation Complete"
!define MUI_FINISHPAGE_TEXT "BOT MMORPG AI has been installed successfully.$\r$\n$\r$\nYou can now launch the application from your Start Menu or Desktop.$\r$\n$\r$\nThank you for choosing BOT MMORPG AI!"
!define MUI_FINISHPAGE_RUN "$INSTDIR\${MAINBINARYNAME}.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch BOT MMORPG AI"

; --- Wizard Pages ---
!insertmacro MUI_PAGE_WELCOME

; License page is optional.
; If the bundler provides a license file path, it will be shown.
{{#if license_file}}
!insertmacro MUI_PAGE_LICENSE "{{license_file}}"
{{/if}}

; Components page - allows users to choose what to install
!insertmacro MUI_PAGE_COMPONENTS

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; --- Installation Types ---
InstType "Full Installation"
InstType "Minimal Installation (Recommended)"

; --- Sections ---

; Core application section (required, cannot be unchecked)
Section "BOT MMORPG AI (UI + Backend)" SecCore
  SectionIn RO 1 2  ; Required in all installation types

  SetOutPath "$INSTDIR"

  ; Per-machine install: write shortcuts to the All Users Start Menu /
  ; Desktop instead of the current user's folders. Without this,
  ; $SMPROGRAMS and $DESKTOP resolve to %APPDATA%\Microsoft\Windows\
  ; Start Menu\... and %USERPROFILE%\Desktop\..., which is wrong for an
  ; admin-elevated per-machine installer (and any other admin user
  ; logging into the same machine wouldn't see the shortcuts).
  SetShellVarContext all

  ; Display what we're installing
  DetailPrint "Installing BOT MMORPG AI core application..."

  ; Install main application executable from the bundler-provided source path.
  ; Use /oname to force the canonical UPPERCASE filename regardless of what
  ; cargo's package.name renders to.
  File "/oname=${MAINBINARYNAME}.exe" "${MAINBINARYSRCPATH}"

  ; Fail loud if the File directive silently produced nothing. NSIS does not
  ; abort the install just because /oname extracted zero bytes -- it would
  ; merrily continue, write Uninstall.exe, and the user ends up with an
  ; install dir containing English.nsh + installer.nsi + Uninstall.exe but
  ; NO main exe. That is precisely the failure this template now guards
  ; against. Steam/AAA installers all do this -- silent partial installs
  ; are the worst possible user experience.
  IfFileExists "$INSTDIR\${MAINBINARYNAME}.exe" main_exe_ok
    MessageBox MB_OK|MB_ICONSTOP "FATAL: ${MAINBINARYNAME}.exe was not extracted to $INSTDIR.$\r$\nThe installer is corrupt; please re-download."
    Abort
  main_exe_ok:

  ; Install WebView2 bootstrapper if needed
  {{#if install_webview2_mode}}
  File "{{webview2_installer_path}}"
  {{/if}}

  ; App files packaged by Tauri (resources, sidecars, etc.)
  ; IMPORTANT: `/oname=...` MUST be quoted. Without quotes, resource
  ; filenames that contain a space cause NSIS to parse the rest of the
  ; directive as extra arguments and print `Usage: File ...`, aborting the
  ; build. The unescape-dollar-sign helper is required because raw Windows
  ; source paths can contain `$` which NSIS would otherwise misinterpret as
  ; a variable reference. This matches the canonical tauri-v1.6.6 NSIS
  ; template (line 548).

  ; Defense-in-depth for re-install over an existing install:
  ; (1) Try to remove driver-installer payloads that are commonly held
  ;     open by Windows Defender real-time scanning or by a previously
  ;     loaded Interception/vJoy helper. If the Delete itself fails
  ;     (because the file is locked), it fails silently -- that's fine,
  ;     the SetOverwrite try below handles the actual extraction.
  ; (2) Switch to SetOverwrite try for the bundled-resources loop so a
  ;     locked destination file is left in place rather than triggering
  ;     the "Error opening file for writing" Abort/Retry/Ignore dialog.
  ;     This is the canonical NSIS pattern for files that may be locked
  ;     by AV / running helpers. The pre-existing copy is the same
  ;     binary content (oblitum/Interception releases are stable), so
  ;     leaving it in place is correct behavior.
  Delete "$INSTDIR\drivers\interception\install-interception.exe"
  Delete "$INSTDIR\drivers\vjoy\vJoySetup.exe"

  ; --- Bundled resources (Tauri 1.x canonical pattern) ---
  ;
  ; Two separate loops, exactly matching tauri-bundler 1.7.4's own
  ; installer.nsi template. The first loop CreateDirectory's every
  ; parent dir from the resources_dirs set; the second loop runs the
  ; File directive against each resource's destination path (the
  ; second tuple element). Parent dir creation is the job of the
  ; first loop, not of the resources loop.
  ;
  ; Backslash rule (CRITICAL): inside an NSIS path string, when a
  ; backslash directly precedes a handlebars expression, write TWO
  ; backslashes in the source. handlebars-rust interprets a single
  ; backslash before a double-curly-open as an escape that suppresses
  ; expression parsing -- which is what produced literal-text
  ; subfolder names in the previously broken build. Doubling the
  ; backslash emits one literal backslash followed by a parsed
  ; expression, which is what NSIS needs.
  {{#each resources_dirs}}
  CreateDirectory "$INSTDIR\\{{this}}"
  {{/each}}

  SetOverwrite try
  {{#each resources}}
  File /a "/oname={{this.[1]}}" "{{unescape-dollar-sign @key}}"
  {{/each}}
  SetOverwrite on

  ; Remember install location (useful for upgrades)
  SetRegView 64
  WriteRegStr HKLM "Software\BOT-MMORPG-AI" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "Software\BOT-MMORPG-AI" "Version" "{{version}}"

  ; Add to Windows Programs list
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\BOT-MMORPG-AI" "DisplayName" "BOT MMORPG AI"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\BOT-MMORPG-AI" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\BOT-MMORPG-AI" "DisplayIcon" "$INSTDIR\${MAINBINARYNAME}.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\BOT-MMORPG-AI" "Publisher" "BOT MMORPG AI Team"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\BOT-MMORPG-AI" "DisplayVersion" "{{version}}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\BOT-MMORPG-AI" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\BOT-MMORPG-AI" "NoRepair" 1

  ; --- Shortcuts ---
  DetailPrint "Creating shortcuts..."
  CreateDirectory "$SMPROGRAMS\BOT-MMORPG-AI"
  CreateShortCut "$SMPROGRAMS\BOT-MMORPG-AI\BOT-MMORPG-AI.lnk" "$INSTDIR\${MAINBINARYNAME}.exe" "" "$INSTDIR\${MAINBINARYNAME}.exe" 0
  CreateShortCut "$SMPROGRAMS\BOT-MMORPG-AI\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
  CreateShortCut "$DESKTOP\BOT-MMORPG-AI.lnk" "$INSTDIR\${MAINBINARYNAME}.exe" "" "$INSTDIR\${MAINBINARYNAME}.exe" 0

  ; --- Driver installers ---
  ; Interception
  IfFileExists "$INSTDIR\drivers\interception\install-interception.exe" 0 +4
    DetailPrint "Installing Interception driver..."
    ExecWait '"$INSTDIR\drivers\interception\install-interception.exe" /install'
    DetailPrint "Interception install step finished."

  ; vJoy
  ; The build pipeline writes a 12-byte placeholder when the real installer
  ; is unavailable. Running that placeholder would do nothing yet exit 0,
  ; making NSIS report success for a no-op step. Gate on a real-size check
  ; (>= 1 MB) instead of just IfFileExists.
  ${If} ${FileExists} "$INSTDIR\drivers\vjoy\vJoySetup.exe"
    ${GetSize} "$INSTDIR\drivers\vjoy" "/M=vJoySetup.exe /S=0B" $0 $1 $2
    ${If} $0 >= 1048576
      DetailPrint "Installing vJoy driver..."
      ExecWait '"$INSTDIR\drivers\vjoy\vJoySetup.exe" /S'
      DetailPrint "vJoy install step finished."
    ${Else}
      DetailPrint "Skipping vJoy: installer is a placeholder ($0 bytes). Install manually if needed."
    ${EndIf}
  ${EndIf}

  ; --- Uninstaller ---
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ; Defensive cleanup: scrub leftover NSIS build artifacts that some
  ; tauri-bundler 1.x revisions copy into $INSTDIR. These Deletes run AFTER
  ; WriteUninstaller (and again from .onInstSuccess) so we catch the case
  ; where the bundler stages them late in the extraction order.
  ;
  ; CRITICAL: do NOT delete bot-mmorpg-ai.exe here. Windows NTFS is
  ; case-insensitive by default, so Delete "$INSTDIR\bot-mmorpg-ai.exe"
  ; matches AND DELETES the canonical $INSTDIR\BOT-MMORPG-AI.exe that
  ; the File /oname=... directive just created. That was the cause of
  ; the previous "Uninstall.exe is present but main exe is missing"
  ; failure mode -- the install completed cleanly, then the main exe
  ; got wiped right before .onInstSuccess.
  Delete "$INSTDIR\installer.nsi"
  Delete "$INSTDIR\English.nsh"
  Delete "$INSTDIR\nsis-output.exe"

  DetailPrint "Core application installed successfully!"
SectionEnd

; Optional AI Models section (unchecked by default)
Section /o "AI Models (Optional)" SecModels
  SectionIn 1  ; Only in Full installation type

  DetailPrint "Preparing to download AI models..."

  ; Create models directory
  CreateDirectory "$INSTDIR\models"

  ; Check if download script exists
  IfFileExists "$INSTDIR\resources\scripts\download_models.ps1" 0 skip_models
    DetailPrint "Downloading AI models from repository..."
    DetailPrint "This may take several minutes depending on your internet connection..."

    ; Run PowerShell script to download models
    nsExec::ExecToLog 'powershell -ExecutionPolicy Bypass -NoProfile -File "$INSTDIR\resources\scripts\download_models.ps1" -Dest "$INSTDIR\models"'
    Pop $0

    ${If} $0 == 0
      DetailPrint "AI models downloaded successfully!"
      WriteRegStr HKLM "Software\BOT-MMORPG-AI" "ModelsInstalled" "true"
    ${Else}
      DetailPrint "Warning: AI models download failed or was incomplete."
      DetailPrint "You can download models manually later from the application."
      WriteRegStr HKLM "Software\BOT-MMORPG-AI" "ModelsInstalled" "false"
    ${EndIf}
    Goto done_models

  skip_models:
    DetailPrint "Models download script not found. Skipping models installation."
    MessageBox MB_OK|MB_ICONINFORMATION "The AI models download script was not found.$\r$\n$\r$\nYou can download models later from within the application or manually from the project repository."

  done_models:
SectionEnd

; Developer Tools section (unchecked by default)
Section /o "Developer Tools (Optional)" SecDevTools
  SectionIn 1  ; Only in Full installation type

  DetailPrint "Installing developer tools..."

  ; Create developer directories
  CreateDirectory "$INSTDIR\dev"
  CreateDirectory "$INSTDIR\dev\datasets"
  CreateDirectory "$INSTDIR\dev\templates"
  CreateDirectory "$INSTDIR\dev\docs"

  ; Create a shortcut to the models folder for easy access
  CreateShortCut "$SMPROGRAMS\BOT-MMORPG-AI\Models Folder.lnk" "$INSTDIR\models"
  CreateShortCut "$SMPROGRAMS\BOT-MMORPG-AI\Developer Tools.lnk" "$INSTDIR\dev"

  ; Create a README for developers
  FileOpen $0 "$INSTDIR\dev\README.txt" w
  FileWrite $0 "BOT MMORPG AI - Developer Tools$\r$\n"
  FileWrite $0 "================================$\r$\n$\r$\n"
  FileWrite $0 "This folder contains resources for creating and training custom AI models.$\r$\n$\r$\n"
  FileWrite $0 "Folders:$\r$\n"
  FileWrite $0 "  - datasets/  : Place your training datasets here$\r$\n"
  FileWrite $0 "  - templates/ : Model templates and examples$\r$\n"
  FileWrite $0 "  - docs/      : Developer documentation$\r$\n$\r$\n"
  FileWrite $0 "For more information, visit the project documentation.$\r$\n"
  FileClose $0

  DetailPrint "Developer tools installed successfully!"
  WriteRegStr HKLM "Software\BOT-MMORPG-AI" "DevToolsInstalled" "true"
SectionEnd

; --- Section Descriptions ---
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Core application files including the user interface and backend. This component is required and provides all essential functionality for gaming assistance."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecModels} "Download pre-trained AI models from the project repository. These models enhance the bot's capabilities but require an internet connection and additional disk space (~500MB-2GB). You can skip this and download models later from within the application."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDevTools} "Tools and resources for developers who want to create custom AI models. Includes sample datasets, model templates, and documentation. Only install this if you plan to develop custom models."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; --- Post-install cleanup ---
; .onInstSuccess fires once the entire install completes. This is the
; correct place to scrub bundler-staged artifacts (English.nsh,
; installer.nsi) because by definition every File directive has already
; finished executing -- there's no extraction order ambiguity here.
;
; CRITICAL: do NOT delete bot-mmorpg-ai.exe here. See the matching
; comment in SecCore. Windows NTFS is case-insensitive, so deleting
; the lowercase variant wipes the canonical BOT-MMORPG-AI.exe.
Function .onInstSuccess
  Delete "$INSTDIR\installer.nsi"
  Delete "$INSTDIR\English.nsh"
  Delete "$INSTDIR\nsis-output.exe"
FunctionEnd

; --- Uninstaller Section ---
Section "Uninstall"
  DetailPrint "Removing BOT MMORPG AI..."

  ; Match the install-time shell-var context so $SMPROGRAMS / $DESKTOP
  ; resolve to the All Users folders where the shortcuts actually live.
  SetShellVarContext all

  ; Remove shortcuts
  Delete "$DESKTOP\BOT-MMORPG-AI.lnk"
  Delete "$SMPROGRAMS\BOT-MMORPG-AI\BOT-MMORPG-AI.lnk"
  Delete "$SMPROGRAMS\BOT-MMORPG-AI\Uninstall.lnk"
  Delete "$SMPROGRAMS\BOT-MMORPG-AI\Models Folder.lnk"
  Delete "$SMPROGRAMS\BOT-MMORPG-AI\Developer Tools.lnk"
  RMDir "$SMPROGRAMS\BOT-MMORPG-AI"

  ; Ask user if they want to keep their models and data.
  ; /SD IDNO: in silent uninstall (e.g. our verify_installer.ps1 dry-run, or
  ; an unattended upgrade), default to "remove everything" so $INSTDIR is
  ; fully cleaned up. Without this the silent uninstall would fall through
  ; the MessageBox without taking the IDYES jump and behave non-deterministically
  ; across NSIS versions.
  MessageBox MB_YESNO|MB_ICONQUESTION "Do you want to keep your AI models and custom data?$\r$\n$\r$\nSelect 'No' to remove everything (clean uninstall).$\r$\nSelect 'Yes' to keep your models and data for future installations." /SD IDNO IDYES keep_data

  ; Remove everything
  DetailPrint "Performing clean uninstall..."
  RMDir /r "$INSTDIR"
  Goto done_uninstall

  keep_data:
    DetailPrint "Keeping user data and models..."
    ; Remove application files but keep models and dev folders
    Delete "$INSTDIR\${MAINBINARYNAME}.exe"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir /r "$INSTDIR\drivers"
    RMDir /r "$INSTDIR\resources"
    ; Note: $INSTDIR\models and $INSTDIR\dev are preserved

  done_uninstall:

  ; Remove registry keys
  SetRegView 64
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\BOT-MMORPG-AI"
  DeleteRegKey HKLM "Software\BOT-MMORPG-AI"

  DetailPrint "Uninstall complete!"
SectionEnd
