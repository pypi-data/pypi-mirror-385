# setup.py
from setuptools import setup, find_packages

setup(
    name='custom-sort-cli', # Назва пакету на PyPI
    version='0.1.0',
    packages=find_packages(),
    author='Bohdan',
    author_email='your.email@example.com',
    description='A custom sort command line tool using Python and Click.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/bohdanfariyon/custom-sort', # Посилання на ваш GitHub репозиторій
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'csort=custom_sort.main:cli', # Створює команду csort
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)