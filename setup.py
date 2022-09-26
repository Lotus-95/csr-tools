from setuptools import setup, find_packages

DEPENDENCIES = [
    'tqdm',
    'prettytable',
    'requests'
]

setup(
    name='csr',
    version='0.1',
    packages=find_packages(),
    author='Wenkang Qin',
    author_email='wkqin@outlook.com',
    keywords='ssh tools for csr',
    install_requires=DEPENDENCIES,
    entry_points={
        'console_scripts': [
            'csr = csr.__main__:cmd'
        ]
    }
)
