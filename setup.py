#! /usr/bin/env python
"""Installation script."""

from setuptools import setup

setup(
    name='rcon',
    version_format='{tag}',
    setup_requires=['setuptools-git-version'],
    author='Richard Neumann',
    author_email='mail@richard-neumann.de',
    python_requires='>=3.8',
    packages=['rcon'],
    extras_require={'GUI':  ['pygobject', 'pygtk']},
    scripts=['files/rcongui', 'files/rconclt', 'files/rconshell'],
    url='https://github.com/conqp/rcon',
    license='GPLv3',
    description='A RCON client library library.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords='python rcon client'
)
