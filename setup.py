try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(
    name='zero-common-app',
    version='0.1',
    description='App with common views, libs and templates that can be used by other apps',
    author='Jose Maria Zambrana Arze',
    author_email='contact@josezambrana.com',
    url='http://github.com/mandlaweb/zerocommon',
    packages=find_packages(),
    install_requires=['Django>=1.3.1', 'South>=0.7.3']
)
