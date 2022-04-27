import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyezviz',
    version="0.2.0.8",
    license='Apache Software License 2.0',
    author='Renier Moorcroft',
    author_email='renierm26@users.github.com',
    description='ADT Secure Home API',
    long_description="API for accessing ADT Secure Home. Please view readme on github",
    url='https://github.com/RenierM26/pyadtsecurehome/',
    packages=setuptools.find_packages(),
    setup_requires=[
        'requests',
        'setuptools'
    ],
    install_requires=[
        'requests',
        'pandas',
        'pycryptodome'
    ],
    entry_points={
    'console_scripts': ['pyadtsecurehome = pyadtsecurehome.__main__:main']
    },
    python_requires = '>=3.6'
)
