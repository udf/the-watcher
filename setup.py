#!/usr/bin/env python

from setuptools import setup

VERSION = '0.1.3'

setup(
  name='watcher-bot',
  version=VERSION,
  packages=['watcher-bot'],
  install_requires=[
    'telethon',
    'aiohttp'
  ]
)