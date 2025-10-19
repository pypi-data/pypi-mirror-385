rem @echo off
if "%VSCMD_ARG_HOST_ARCH%"=="x64" goto pass_ver

echo Execute in the x64 Native tools command prompt.
goto exit
:pass_ver

if not exist "msvc_build" mkdir msvc_build

pushd msvc_build

if exist "C:\Program Files (x86)\gempyre" goto found
if exist "C:\Program Files\gempyre" goto found

echo "Gempyre not installed"
goto exit

:found

cmake .. -DCMAKE_BUILD_TYPE=Release
if %ERRORLEVEL% NEQ 0 popd && exit /b %ERRORLEVEL%
copy Release\*.pyd ..\build\
cmake --build . --config Release
pip3 install -e .. --user

popd

:exit
