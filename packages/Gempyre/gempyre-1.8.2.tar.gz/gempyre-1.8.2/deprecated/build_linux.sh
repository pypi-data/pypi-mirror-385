
PYDEV_INSTALLED=$(dpkg-query -W -f='${Status}' python3-dev 2>/dev/null | grep -c "ok installed")
if [[ "$PYDEV_INSTALLED" -eq "0" ]]; then
  echo "Python3 dev is missing...apt-get install it, please"	
  sudo apt-get install python3-dev  # for python3.x installs
fi	

PIP3_INSTALLED=$(dpkg-query -W -f='${Status}' python3-pip 2>/dev/null | grep -c "ok installed")
if [[ "$PIP3_INSTALLED" -eq "0" ]]; then
   echo "Pip3 is missing...apt-get install it, please"	
   sudo apt-get install python3-pip 
fi	

set -e

mkdir -p build
pushd build


PY_VER_LONG=$(python3 --version)
PY_VER=$(echo "${PY_VER_LONG}" | grep -o '[0-9]\+.[0-9]\+')

IS_RASPEBERRY=$(python3 -c "import platform; print('raspberrypi' in platform.uname())")

if [ $IS_RASPEBERRY == "True" ]; then
  echo This is Raspberry!
  EXTRA="-DRASPBERRY=1"
fi

set +e  

cmake .. -DCMAKE_BUILD_TYPE=RELEASE $EXTRA
rval=$?
if [ $rval -ne 0 ]; then
  echo "Is Gempyre installed? See https://github.com/mmertama/Gempyre"
  popd
  exit
fi  

cmake --build . --config Release
rval=$?
if [ $rval -ne 0 ]; then
  popd
  return
fi

pip3 install -e .. --user

popd
