from setuptools import setup, find_packages

setup(
    name='elveirdor',
    version='0.1.0',
    description='Elveirdor unified pipeline (merged from user sources)',
    packages=find_packages(),
    include_package_data=True,
    entry_points={'console_scripts': ['elveirdor=elveirdor.cli:main']},
    install_requires=['numpy','pillow'],
)
