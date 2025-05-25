#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = '0.1.5'

setup(
  name='watcher-bot',
  version=VERSION,
  packages=(
    find_packages()
    + [f'watcher-bot.plugins.{p}' for p in find_packages('watcher-bot/plugins')]
    + ['watcher-bot.plugins']
  ),
  install_requires=[
    'telethon',
    'aiohttp'
  ]
)