# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


version = '0.1.0'
setup(

  name = 'gitconsensusservice',

  version = version,
  packages=find_packages(),

  description = 'Automate Github Pull Requests using Reactions',
  long_description=long_description,
  python_requires='>=3',

  author = 'Robert Hafner',
  author_email = 'tedivm@tedivm.com',
  url = 'https://github.com/tedivm/gitconsensusservice',
  download_url = "https://github.com/tedivm/gitconsensusservice/archive/v%s.tar.gz" % (version),
  keywords = 'automation github consensus git',

  classifiers = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',

    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Topic :: Software Development :: Version Control',

    'Programming Language :: Python :: 3',
    'Environment :: Console',
  ],

  install_requires=[
    'cryptography>=2.1.4,<3',
    'click>=5.0,<6.0',
    'Flask>=0.12.2',
    'github3.py>=0.9.6,<0.10',
    'pyjwt>=1.5.3,<2',
    'PyYAML>=3.12,<3.13',
    'requests>=2.18.0,<2.19',
  ],

  extras_require={
    'dev': [
      'pypandoc',
      'twine',
      'wheel'
    ],
  },

  entry_points={
    'console_scripts': [
      'gitconsensusservice=gitconsensusservice:cli',
    ],
  },

)