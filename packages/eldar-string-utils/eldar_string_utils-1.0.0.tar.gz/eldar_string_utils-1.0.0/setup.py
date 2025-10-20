from setuptools import setup, find_packages

setup(
    name='eldar-string-utils',
    version='1.0.0',
    author='Eldar Eliyev',
    author_email='eldar@example.com',
    description='A lightweight string processing and analysis library',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://pypi.org/project/eldar-string-utils/',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
