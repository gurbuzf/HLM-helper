from setuptools import setup, find_packages

VERSION = '0.0.0.dev1' 
DESCRIPTION = 'hlm_helper'
LONG_DESCRIPTION = 'Set of tools facilitating use of Hillslope-link Model'

setup(
        name="hlm_helper", 
        version=VERSION,
        url='https://github.com/gurbuzf/HLM-helper',
        author="faruk gurbuz",
        author_email="<no email@gmail.com>",
        description='hlm_helper',
        long_description='Set of tools facilitating use of Hillslope-link Model',
        packages=find_packages(),
        package_dir={'hlm_helper': 'hlm_helper'},
        package_data={'hlm_helper': ['base_files/*.gbl']},
        install_requires=['h5py'],
        keywords=['python', 'HLM'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: Microsoft :: Windows",
        ]
)

