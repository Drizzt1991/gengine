import codecs
import os
import re
import sys
from setuptools import setup, find_packages


with codecs.open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'gengine', '__init__.py'), 'r', 'latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'\r?$",
                             fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')

if sys.version_info >= (3, 4):
    install_requires = []
else:
    install_requires = ['asyncio']


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()

args = dict(
    name='gengine',
    version=version,
    description=('Simple game server implementation'),
    long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'],
    author='Taras Voinarovskyi',
    author_email='voyn1991@gmail.com',
    url='https://github.com/Drizzt1991/gengine',
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'gengine-client = gengine.client.client:main',
            'gengine-server = gengine.world.server:main',
            'gengine-asteroid = gengine.examples.asteroids.main:main',
        ],
    }
    )
setup(**args)
