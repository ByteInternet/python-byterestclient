from setuptools import setup, find_packages

setup(
    name='apiclient',
    version='0.1',
    packages=find_packages(exclude=['test*']),
    url='',
    license='',
    author='Allard Hoeve',
    author_email='allard@byte.nl',
    description='A generic API client',
    install_requires=['requests>=2.2.1'],
    test_suite="tests",
)
