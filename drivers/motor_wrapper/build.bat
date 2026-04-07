@echo off
setlocal

REM ============================================================
REM DIRETORIO DO PROJETO (onde este .bat está)
REM ============================================================
set PROJECT_DIR=%~dp0

REM Remove barra invertida final, se quiser consistência
if "%PROJECT_DIR:~-1%"=="\" set PROJECT_DIR=%PROJECT_DIR:~0,-1%

REM ============================================================
REM CAMINHOS RELATIVOS AO PROJETO
REM ============================================================
set NI_INCLUDE=%PROJECT_DIR%
set NI_LIB=%PROJECT_DIR%

REM ============================================================
REM MOSTRAR CONFIGURAÇÃO
REM ============================================================
echo.
echo ============================================
echo  PROJECT_DIR = %PROJECT_DIR%
echo  NI_INCLUDE  = %NI_INCLUDE%
echo  NI_LIB      = %NI_LIB%
echo ============================================
echo.

REM ============================================================
REM VALIDAR CAMINHOS
REM ============================================================
if not exist "%NI_INCLUDE%\nimotion.h" (
    echo [ERRO] Nao encontrei nimotion.h em:
    echo %NI_INCLUDE%
    exit /b 1
)

if not exist "%NI_LIB%\nimotion.lib" (
    echo [ERRO] Nao encontrei nimotion.lib em:
    echo %NI_LIB%
    exit /b 1
)

if not exist "%PROJECT_DIR%\motor_wrapper.c" (
    echo [ERRO] Nao encontrei motor_wrapper.c em:
    echo %PROJECT_DIR%
    exit /b 1
)

REM ============================================================
REM LIMPAR ARQUIVOS ANTIGOS
REM ============================================================
if exist "%PROJECT_DIR%\motor_wrapper.obj" del /Q "%PROJECT_DIR%\motor_wrapper.obj"
if exist "%PROJECT_DIR%\motor_wrapper.exp" del /Q "%PROJECT_DIR%\motor_wrapper.exp"
if exist "%PROJECT_DIR%\motor_wrapper.lib" del /Q "%PROJECT_DIR%\motor_wrapper.lib"
if exist "%PROJECT_DIR%\motor_wrapper.dll" del /Q "%PROJECT_DIR%\motor_wrapper.dll"

REM ============================================================
REM COMPILAR DLL
REM ============================================================
cl /LD /O2 /W4 /Fe:"%PROJECT_DIR%\motor_wrapper.dll" ^
   "%PROJECT_DIR%\motor_wrapper.c" ^
   /I"%NI_INCLUDE%" ^
   /link /LIBPATH:"%NI_LIB%"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERRO] Falha na compilacao/linkedição.
    exit /b %ERRORLEVEL%
)

echo.
echo [OK] Build concluido com sucesso.
echo.

dir "%PROJECT_DIR%\motor_wrapper.*"

endlocal