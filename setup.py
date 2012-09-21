from os.path import abspath, dirname, join, normpath

from setuptools import find_packages, setup


setup(

    # Basic package information:
    name = 'zero-common',
    version = '0.1.2',
    packages = find_packages(),

    # Packaging options:
    zip_safe = False,
    include_package_data = True,

    # Package dependencies:
    install_requires = ['Django>=1.3.1', 'South>=0.7.3'],

    # Metadata for PyPI:
    author = 'Jose Maria Zambrana Arze',
    author_email = 'contact@josezambrana.com',
    license = 'apache license v2.0',
    url = 'http://github.com/mandlaweb/Zero-Common',
    keywords = 'zero common app',
    description = 'App with common views, libs and templates that can be used by other apps',
    long_description = "An app with generic views, templates and styles to use in your project."

)
