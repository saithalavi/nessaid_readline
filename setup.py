# Copyright 2021 by Saithalavi M, saithalavi@gmail.com
# All rights reserved.
# This file is part of the Nessaid readline Framework, nessaid_readline python package
# and is released under the "MIT License Agreement". Please see the LICENSE
# file included as part of this package.
#

import os
import sys
import shutil
from setuptools import setup


pkg_name = 'nessaid_readline'
sub_packages = []

install_packages = [pkg_name] + [pkg_name + "." + sub_pkg for sub_pkg in sub_packages]

clanup_dirs = ['build', 'dist', pkg_name + '.egg-info']


def do_cleanup_fixes():
    dir_content = os.listdir()
    for d in clanup_dirs:
        if d in dir_content:
            try:
                shutil.rmtree(d)
            except Exception:
                pass


long_description = """Common library with minimal readline functionality for Windows, Linux and Mac systems.
"""

install_requires = [
    "asyncio"
]

setup(
    name=pkg_name,
    version='0.2.1',
    url='https://github.com/saithalavi/nessaid_readline',
    description="Nessaid's readkey tool",
    long_description=long_description,
    author='Saithalavi M',
    author_email='saithalavi@gmail.com',
    packages=install_packages,
    include_package_data=True,
    install_requires=install_requires,
    python_requires='>=3',
    keywords='readkey readchar',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    project_urls = {
        'Documentation': 'https://github.com/saithalavi/nessaid_readline/blob/master/README.md',
        'Source': 'https://github.com/saithalavi/nessaid_readline',
        'Tracker': 'https://github.com/saithalavi/nessaid_readline/issues',
    },
)

if __name__ == '__main__':
    if 'clean' in sys.argv and 'install' not in sys.argv:
        do_cleanup_fixes()