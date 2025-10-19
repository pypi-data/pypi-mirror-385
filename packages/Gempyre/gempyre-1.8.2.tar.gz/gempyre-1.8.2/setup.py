from setuptools import find_packages
from skbuild import setup  # This line replaces 'from setuptools import setup'
import os

setup (name='Gempyre',
       packages=["Gempyre", "Gempyre_utils"],
       package_dir={"": "src"},
       cmake_install_dir="src/Gempyre",
      )
