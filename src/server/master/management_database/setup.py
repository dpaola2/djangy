from setuptools import setup, find_packages

setup(
    name="management_database",
    version="0.1",
    packages=find_packages(),
    install_requires=['Django>=1.0', 'mysql-python', 'South'],
    author="David J. Paola",
    author_email="dave@djangy.com",
    description="Djangy.com Management Database model specification",
    keywords="djangy django",
    url="http://www.djangy.com"
)
