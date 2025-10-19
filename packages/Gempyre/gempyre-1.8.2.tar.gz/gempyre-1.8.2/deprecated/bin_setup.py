
from setuptools import setup, Extension, find_packages
import os
import sys
import platform
import subprocess


setup (
        name='Gempyre',
        version='1.6.1',
        license='MIT',
        description='Gempyre Framework',
        author='Markus Mertama',
        author_email='foobar@foobar',
        url='https://github.com/mmertama',
        long_description='''
Gempyre is C++ Framework for quick and simple UI development and Gempyre-Python apply that breeze to Python development.
''',
        packages=find_packages(),
        setup_requires=['wheel'],
        install_requires=['pywebview', 'websockets',],
        entry_points={
           'console_scripts': ['pyclient=client.pyclient:main']},
        package_data={
            'Gempyre': ['macos_lib/*', 'unix_lib/*', 'windows_lib/*']},
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
        ],
        python_requires='>=3.8',   
      )
       
