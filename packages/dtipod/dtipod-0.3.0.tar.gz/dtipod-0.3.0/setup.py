#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2025 Matthias Büchse.
#
# This file is part of dtipod.
#
# dtipod is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# dtipod is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with dtipod.
# If not, see <https://www.gnu.org/licenses/>.
import setuptools
# see https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools


with open('requirements.txt', 'r') as fileobj:
    install_requires = fileobj.read().splitlines()


with open("README.md") as fileobj:
    readme = fileobj.read()


setuptools.setup(
    name="dtipod",
    version="0.3.0",
    description="Podcatcher do_the_internet.sh-style",
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords="podcast commandline terminal console podcatcher",
    url="https://git.sr.ht/~mbuechse/dtipod",
    author="Matthias Büchse",
    author_email="matthias@buech.se",
    license="GPL-3.0-or-later",
    packages=['dtipod'],
    python_requires='>=3',
    install_requires=install_requires,
    entry_points={'console_scripts': ['dtipod=dtipod.cli:main']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Topic :: Terminals'
    ],
)
