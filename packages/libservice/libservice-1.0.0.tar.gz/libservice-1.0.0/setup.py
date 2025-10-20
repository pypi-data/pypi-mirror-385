"""setup.py
locan installation: pip install -e .

python setup.py sdist
twine upload --repository pypitest dist/libservice-x.x.x.tar.gz
twine upload --repository pypi dist/libservice-x.x.x.tar.gz
"""
from setuptools import setup, find_packages
from version import __version__ as version

try:
    with open('README.md', 'r') as f:
        long_description = f.read()
except IOError:
    long_description = ''

install_requires = [
    'colorlog',
    'cryptography',
    'msgpack',
    'python-thingsdb',
]

setup(
    name='libservice',
    packages=find_packages(),
    version=version,
    description='Library for building InfraSonar services',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Cesbit',
    author_email='info@cesbit.com',
    url='https://github.com/infrasonar/python-libservice',
    download_url=(
        'https://github.com/infrasonar/'
        'python-libservice/tarball/v{}'.format(version)),
    keywords=['monitoring', 'infrasonar', 'service'],
    install_requires=install_requires,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic'
    ],
)
