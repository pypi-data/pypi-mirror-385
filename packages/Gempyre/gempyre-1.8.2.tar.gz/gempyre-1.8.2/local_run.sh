#!/bin/bash

if [ -z ""$@"" ]; then
    echo "Locally installed (venv?) 'pip3 install -e .' may not find the Gempyre library correctly."
    echo "This scipts attemps to set the correctly python path for the call. e.g. $(basename $0) my_script.py arg1 arg2..."
    exit 1
fi

POTATO=$(python3 -c 'import sysconfig
platform_info = sysconfig.get_platform()
python_version = sysconfig.get_python_version()
print(f"{platform_info}-{python_version}")')
echo $POTATO
PYTHONPATH=./_skbuild/$POTATO/cmake-install/src python3 "$@"


