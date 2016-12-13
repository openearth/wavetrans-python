from setuptools import setup, find_packages

setup(
    name='WaveTrans',
    version='0.0',
    author='Bas Hoonhout',
    author_email='bas.hoonhout@deltares.nl',
    packages=find_packages(),
    description='Creates SWAN spectrum shoreward of barrier',
    long_description=open('README.txt').read(),
    install_requires=[
        'numpy',
        'docopt',
    ],
    entry_points={'console_scripts': [
        'wavetrans = wavetrans.console:wavetrans',
    ]},
)
