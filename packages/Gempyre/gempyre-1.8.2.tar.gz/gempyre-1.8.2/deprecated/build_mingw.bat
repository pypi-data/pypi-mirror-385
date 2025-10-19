rem @echo off
for /f "delims=" %%F in ('where grep') do set var=%%F 
if NOT %var%=="" goto pass_ver
echo Msys shall be in path - C:\msys64\mingw64\bin;C:\msys64\usr\bin;
goto exit
:pass_ver

if not exist "mingw_build" mkdir mingw_build

pushd mingw_build

if exist "C:\Program Files (x86)\gempyre" goto found
if exist "C:\Program Files\gempyre" goto found

git clone https://github.com/mmertama/Gempyre.git
pushd Gempyre
call mingw_install.bat
popd

:found

cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release

if not exist "..\build\lib.win-amd64-3.8" mkdir ..\build\lib.win-amd64-3.8
move /Y Release\*.pyd ..\build\lib.win-amd64-3.8\ 
pip3 install -e .. --user

popd

:exit
