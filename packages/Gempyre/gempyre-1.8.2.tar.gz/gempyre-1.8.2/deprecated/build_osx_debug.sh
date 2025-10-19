cmake CMakeLists.txt -DGEMPYRE_LIB=${GEMPYRE_DIR}/builds/build-Gempyre-Desktop_Qt_5_15_0_clang_64bit-Debug

cmake --build . --config Debug
OS_VER_LONG=$(defaults read loginwindow SystemVersionStampAsString)
OS_VER=$(echo "${OS_VER_LONG}" | grep -o '[0-9]\+.[0-9]\+')
PY_VER_LONG=$(python3 --version)
PY_VER=$(echo "${PY_VER_LONG}" | grep -o '[0-9]\+.[0-9]\+')
mv *.so build/lib.macosx-${OS_VER}-x86_64-${PY_VER}/
pip3 install -e . --user
