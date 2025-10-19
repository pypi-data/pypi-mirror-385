#!/bin/bash
set -e
mkdir -p mingw_build
pushd mingw_build

PYPATH=

HAS_PY=$(which py)
if [ ! "$HAS_PY" == "" ]; then
  while IFS= read -r line; do
    if [ ${#line} -ge 2 ]; then
      tokens=( $line )
      PYPATH=$(dirname ${tokens[1]})
      #PYPATH=$(cygpath -u $FPATH)
      break
    fi  
  done < <(py -0p)
fi

echo "Using Python from: ${PYPATH}"

cmake .. -DCMAKE_BUILD_TYPE=Release -DPYTHON_PATH=${PYPATH}

cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
${PYPATH}/pip3 install -e .. --user

popd
