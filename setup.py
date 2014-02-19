from setuptools import setup, find_packages

setup(
    name='byterestclient',
    version='0.1',
    packages=find_packages(exclude=['test*']),
    url='https:/github.com/ByteInternet/pythono-byterestclient',
    author='Allard Hoeve',
    author_email='allard@byte.nl',
    description='A generic REST client',
    install_requires=['requests'],
    test_suite="tests",
)
