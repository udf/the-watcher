#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = '0.1.3'

setup(
  name='watcher-bot',
  version=VERSION,
  packages=find_packages(),
  install_requires=[
    'telethon',
    'aiohttp'
  ]
)