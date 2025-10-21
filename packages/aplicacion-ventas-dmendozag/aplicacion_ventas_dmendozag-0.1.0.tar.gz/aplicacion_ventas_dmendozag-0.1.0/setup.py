from setuptools import setup,find_packages #setuptools es una biblioteca que tiene las funcionales estandar de python

setup(
    name = 'aplicacion_ventas_dmendozag',
    version = '0.1.0',
    author = 'Diego Mendoza',
    author_email = "diegomendozagarcia@gmail.com",
    description = "Paquetes para gestionar ventas, precios, impuestos y descuentos",
    long_description = open('README.MD').read(),
    long_description_content_type = 'text/markdown',
    packages=find_packages(),
    install_requires = [],
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', #Cambia esto segun sea necesario
        'Operating System :: OS Independent'
    ],
    python_requires = '>=3.6'

)

#https://pypi.org/account/register/