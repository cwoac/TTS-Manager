!include "MUI2.nsh"

# name the installer
!define VERSION "v0.5.0"
Name "TTS Manager ${VERSION}"
OutFile "Setup TTS Manager ${VERSION}.exe"

InstallDir "$LOCALAPPDATA\TTS Manager"
InstallDirRegKey HKCU "Software\TTS Manager" ""

; up execution level if needs be
RequestExecutionLevel user

Var StartMenuFolder

!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_LICENSE LICENSE
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY

;Start Menu Folder Page Configuration
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\TTS Manager"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"

!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

!insertmacro MUI_PAGE_INSTFILES
  !define MUI_FINISHPAGE_NOAUTOCLOSE
  !define MUI_FINISHPAGE_RUN
  !define MUI_FINISHPAGE_RUN_NOTCHECKED
  !define MUI_FINISHPAGE_RUN_TEXT "Launch TTS Manager"
  !define MUI_FINISHPAGE_RUN_FUNCTION "LaunchLink"
  !define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED
  !define MUI_FINISHPAGE_SHOWREADME $INSTDIR\readme.txt
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"


Section "TTS Manager" SecBase
  SetOutPath "$INSTDIR"

  File /r dist\*
  File /oname=readme.txt README.md
  File /oname=license.txt LICENSE
  WriteRegStr HKCU "Software\TTS Manager" "" $INSTDIR

 !insertmacro MUI_STARTMENU_WRITE_BEGIN Application

    ;Create shortcuts
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\TTS Manager.lnk" $INSTDIR\tts_gui.exe"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

  !insertmacro MUI_STARTMENU_WRITE_END


  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd


LangString DESC_SecBase ${LANG_ENGLISH} "TTS Manager (required)."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecBase} $(DESC_SecBase)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Section "Uninstall"

  Delete "$INSTDIR\Uninstall.exe"

  RMDir "$INSTDIR"

  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder

  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"

  DeleteRegKey /ifempty HKCU "Software\TTS Manager"
SectionEnd

Function LaunchLink
  ExecShell "" "$SMPROGRAMS\$StartMenuFolder\TTS Manager.lnk"
FunctionEnd
