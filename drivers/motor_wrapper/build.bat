@echo off
setlocal

REM ============================================================================
REM Configuração
REM ============================================================================

set SRC=tx_motor_wrapper.c
set OUT=tx_motor_wrapper.dll
set IMPLIB=tx_motor_wrapper.lib
set OBJ=tx_motor_wrapper.obj
set NI_LIB=nimotion.lib

REM ============================================================================
REM Localizar Visual Studio / Build Tools via vswhere
REM ============================================================================

set VSWHERE="%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"

if not exist %VSWHERE% (
    echo [ERRO] Nao foi possivel localizar o vswhere.exe
    echo Esperado em:
    echo   %ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe
    echo.
    echo Isso normalmente indica que o Visual Studio / Build Tools nao esta instalado corretamente.
    pause
    exit /b 1
)

for /f "usebackq delims=" %%i in (`%VSWHERE% -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do (
    set VSINSTALL=%%i
)

if "%VSINSTALL%"=="" (
    echo [ERRO] Nao foi possivel localizar uma instalacao do Visual Studio com ferramentas C/C++.
    echo.
    echo Instale o workload:
    echo   Desktop development with C++
    pause
    exit /b 1
)

set VCVARS="%VSINSTALL%\VC\Auxiliary\Build\vcvarsall.bat"

if not exist %VCVARS% (
    echo [ERRO] Arquivo vcvarsall.bat nao encontrado em:
    echo   %VCVARS%
    pause
    exit /b 1
)

echo [INFO] Visual Studio encontrado em:
echo        %VSINSTALL%
echo.

echo [INFO] Inicializando ambiente x86...
call %VCVARS% x86
if errorlevel 1 (
    echo [ERRO] Falha ao inicializar ambiente do compilador.
    pause
    exit /b 1
)

echo [INFO] Ambiente MSVC inicializado com sucesso.
echo.

REM ============================================================================
REM Limpeza
REM ============================================================================

if exist "%OUT%" del /q "%OUT%"
if exist "%IMPLIB%" del /q "%IMPLIB%"
if exist "%OBJ%" del /q "%OBJ%"

REM ============================================================================
REM Verificacoes
REM ============================================================================

if not exist "%SRC%" (
    echo [ERRO] Arquivo fonte nao encontrado: %SRC%
    pause
    exit /b 1
)

if not exist "%NI_LIB%" (
    echo [ERRO] Biblioteca NI nao encontrada: %NI_LIB%
    pause
    exit /b 1
)

echo [INFO] Compilando %SRC% ...
echo.

REM ============================================================================
REM Build
REM ============================================================================

cl /TC /LD /O2 /W4 /D_CRT_SECURE_NO_WARNINGS /I. %SRC% /link %NI_LIB% /OUT:%OUT%
if errorlevel 1 (
    echo.
    echo [ERRO] Build falhou.
    pause
    exit /b 1
)

echo.
echo [OK] Build concluido com sucesso.
echo.

REM ============================================================================
REM Exportacoes
REM ============================================================================

echo [INFO] Exportacoes da DLL:
dumpbin /exports "%OUT%"
echo.

echo [OK] DLL gerada:
echo        %CD%\%OUT%
echo.

pause
endlocal