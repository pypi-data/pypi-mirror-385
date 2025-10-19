#!/bin/bash

# crete a clean dist folder
rm -rf dist
mkdir dist
pushd dist

REL=v1.6.1

# get artifacts
ARTS=("Linux.tar.xz" "macOS.tar.xz" "Windows-MSVC.tar.xz")
for i in "${ARTS[@]}"; do
	wget https://github.com/mmertama/Gempyre-Python/releases/download/$REL/$i
    tar -xf $i
    rm $i 
done

# get binaries

for i in "${ARTS[@]}"; do
	wget https://github.com/mmertama/Gempyre/releases/download/Gempyre-$REL/$i
    tar -xf $i
    rm $i 
done


# get python modules

cp -r ../Gempyre_utils .

# get setup

cp ../setup.py .

# supportive files

cp ../LICENSE.txt . 

# release
#twine upload -r Gempyre dist/*

popd



