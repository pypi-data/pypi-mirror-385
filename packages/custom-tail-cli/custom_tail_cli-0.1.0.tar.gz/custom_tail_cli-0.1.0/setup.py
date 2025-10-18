# setup.py
from setuptools import setup, find_packages

setup(
    name='custom-tail-cli', # Назва на PyPI
    version='0.1.0',
    packages=find_packages(),
    author='Your Name',
    author_email='your.email@example.com',
    description='A custom tail command line tool using Python and Click.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/bohdanfariyon/custom-tail', # Посилання на GitHub
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'ctail=custom_tail.main:cli', # Створює команду ctail
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)