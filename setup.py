from setuptools import setup, find_packages

setup(
    name='bsm2tools',
    version='0.1.0',
    author='María',
    description='Herramientas para análisis y visualización causal en EDARs usando BSM2',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'plotly'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
