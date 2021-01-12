#! /usr/bin/env python
"""Installation script."""

from setuptools import setup

setup(
    name='rcon',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author='Richard Neumann',
    author_email='mail@richard-neumann.de',
    python_requires='>=3.8',
    packages=['rcon'],
    extras_require={'GUI':  ['pygobject', 'pygtk']},
    entry_points={
        'console_scripts': [
            'rcongui = rcon.gui:main',
            'rconclt = rcon.rconclt:main',
            'rconshell = rcon.rconshell:main',
        ],
    },
    url='https://github.com/conqp/rcon',
    license='GPLv3',
    description='A RCON client library library.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords='python rcon client'
)
