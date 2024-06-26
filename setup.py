from setuptools import find_packages, setup

setup(
    name='flask_models',
    packages=find_packages(include=["flask_models"]),
    version='0.3.6',
    description='Basics models for Python-Flask',
    author='Brixt18',
    license='MIT',
    install_requires=['flask', "flask-sqlalchemy"],
)
