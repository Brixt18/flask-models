from setuptools import find_packages, setup

setup.setup(
    name='flask_models',
    packages=find_packages(include=["models"]),
    version='0.0.2',
    description='Basics models for Python-Flask',
    author='Brixt18',
    license='MIT',
    setup_requires=['flask', "flask-login", "flask-sqlalchemy", ],
)