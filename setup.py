#!/usr/bin/env python

from setuptools import setup, find_packages
from glob import glob

VERSION = '0.1.3'

setup(
  name='watcher-bot',
  version=VERSION,
  packages=find_packages(),
  data_files=[
    ('watcher-bot/plugins', glob('watcher-bot/plugins/*.py'))
  ],
  install_requires=[
    'telethon',
    'aiohttp'
  ]
)