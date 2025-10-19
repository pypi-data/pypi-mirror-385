#!/bin/bash

set -e

# "Linux" binary is not supported in pypi

if [ -z "$1" ]; then
        echo "publish.sh <PASS_WORD_FILE>"
	exit 1     
fi

targets=( "Windows" "MacOS" )

mkdir -p /tmp/grel
pushd /tmp/grel

rm -rf dist
mkdir -p dist

REL=$(curl -Ls -o /dev/null -w %{url_effective}  https://github.com/mmertama/Gempyre-Python/releases/latest | grep -o "[^/]*$")

for value in "${targets[@]}"; do
    ARCH=gempyre-py-$REL-$value.tar.gz
    echo Request "https://github.com/mmertama/Gempyre-Python/releases/download/$REL/$ARCH" 
    wget "https://github.com/mmertama/Gempyre-Python/releases/download/$REL/$ARCH"
    tar -xzvf $ARCH
    rm $ARCH
done

USER=__token__
PASS=$(cat $1)

twine upload dist/* -u $USER -p $PASS 

popd

