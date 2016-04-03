from setuptools import find_packages, setup

__version__ = '1.4.1'

setup(
    name='aws-auth-helper',
    long_description=open('README.rst').read(),
    description='Helper library providing ArgumentParser and Credentials class for AWS authentication',
    version=__version__,
    install_requires=['boto3'],
    packages=find_packages(),
    tests_requires=['unittest2', 'mock'],
    url='http://aws-auth-helper.readthedocs.org/',
    download_url='https://github.com/drewsonne/awsauthhelper/archive/v.{version}.tar.gz'.format(version=__version__),
    license='GPLv2',
    author='Drew J. Sonne',
    author_email='drew.sonne@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration :: Authentication/Directory'
    ]
)
