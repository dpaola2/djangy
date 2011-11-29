from setuptools import setup, find_packages

dependencies = []
try:
    import json
except ImportError:
    dependencies.append('simplejson')

setup(
    name="Djangy",
    version="0.14",
    packages = find_packages(),
    author="David J. Paola",
    author_email="dave@djangy.com",
    description="Djangy.com client application",
    keywords="djangy django",
    url="http://www.djangy.com",
    install_requires = dependencies,
    entry_points = {
        'console_scripts': [
            'djangy = djangy:main'
        ]
    },
    license="University of Illinois/NCSA Open Source License"
)
