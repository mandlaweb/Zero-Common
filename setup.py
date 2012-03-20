import os
import logging

from distutils.command.install import INSTALL_SCHEMES
from distutils.core import setup


for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']


packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('common'):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]

    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])


setup(
    name='zero-common',
    version='0.1',
    description='App with common views, libs and templates that can be used by other apps',
    author='Jose Maria Zambrana Arze',
    author_email='contact@josezambrana.com',
    url='http://github.com/mandlaweb/zerocommon',
    packages=packages,
    data_files=data_files,
    install_requires=['Django>=1.3.1', 'South>=0.7.3']
)
