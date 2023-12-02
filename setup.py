from setuptools import setup, find_packages

setup(
    name='plox',
    version='0.0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'plox = plox.__main__:main'
        ]
    }
)
