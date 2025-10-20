from setuptools import setup

setup(
    name='klsosdoids5',
    version='0.1',
    packages=['klsosdoids5'],
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'klsosdoids2-run = klsosdoids2.__main__:main',
        ],
    },
)