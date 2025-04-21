from setuptools import setup, find_packages

setup(
    name='c32check',
    version='0.1.0',
    description='Pure Python implementation of C32Check encoding/decoding for Stacks and Bitcoin interoperability',
    author='Fabo Hax',
    author_email='40230@pm.me',
    url='https://github.com/fabohax/c32check',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    include_package_data=True,
)
