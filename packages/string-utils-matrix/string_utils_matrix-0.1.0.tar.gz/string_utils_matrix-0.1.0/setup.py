from setuptools import setup, find_packages

setup(
    name='string-utils-matrix',                     
    version='0.1.0',                         
    author='Eldar Eliyev',
    author_email='your_email@example.com',   
    description='A Python utility library with 30+ string methods.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/eldar/string-utils',  
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
