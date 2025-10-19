from setuptools import setup, find_packages

setup(
    name='aurx',  # your package name on PyPI
    version='0.1.0',
    description='Interpreter for AuraScript (.aurx files)',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'aurx=aurx.interpreter:main',  # command-line script entry point
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # or your license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
