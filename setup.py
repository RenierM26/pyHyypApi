import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyhyypapi',
    version="0.0.0.4",
    license='Apache Software License 2.0',
    author='Renier Moorcroft',
    author_email='renierm26@users.github.com',
    description='IDS Hyyp/ADT Secure Home API',
    long_description="API for accessing IDS Hyyp. This is used by ADT Home Connect and possibly others. Please view readme on github",
    url='https://github.com/RenierM26/pyHyypApi/',
    packages=setuptools.find_packages(),
    setup_requires=[
        'requests',
        'setuptools'
    ],
    install_requires=[
        'requests',
        'pandas',
        'oscrypto',
        'protobuf',
        'http-ece',
        'appdirs'
    ],
    python_requires = '>=3.6'
)
