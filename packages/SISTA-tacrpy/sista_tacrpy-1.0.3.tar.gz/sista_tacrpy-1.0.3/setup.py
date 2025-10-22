import sys
from setuptools import setup, find_packages

# get version from arguments start
#index = sys.argv.index('--version')
#sys.argv.pop(index)
#version = sys.argv.pop(index)
version = '1.0.3'

setup(
    name='SISTA-tacrpy',
    version=version,
    description='stahovani dat ze sista',
    long_description='komentar',
    author='velci panove tacru',
    author_email='rozalie.bilkova@tacr.cz',
    packages=find_packages(),
    project_urls={
        'Documentation': 'https://youtu.be/1RulQYSl1aw?feature=shared'
    },
    install_requires=[
        'pandas',
        'gspread',
        'numpy',
        'requests',
        'unidecode'
        ]
)
