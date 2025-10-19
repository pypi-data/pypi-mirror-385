from setuptools import setup, find_packages

from pypaq.lipytools.files import get_requirements


setup(
    name=               'torchness',
    version=            'v2.0.1',
    url=                'https://github.com/piteren/torchness.git',
    author=             'Piotr Niewinski',
    author_email=       'pioniewinski@gmail.com',
    description=        'PyTorch tools',
    packages=           find_packages(),
    install_requires=   get_requirements(),
    license=            'MIT')