import os
from setuptools import setup, find_packages

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='python-byterestclient',
    version='0.1',
    url='https:/github.com/ByteInternet/python-byterestclient',
    author='Allard Hoeve',
    author_email='allard@byte.nl',
    description='A generic REST client',
    install_requires=['requests'],
    test_suite="tests",
    packages=['byterestclient']
)
