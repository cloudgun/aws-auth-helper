from setuptools import find_packages, setup

__version__ = '1.5.0'

setup(
    name='aws-auth-helper',
    long_description="""
awsauthhelper
=============

Introduction
------------

Helper library providing ArgumentParser and Credentials class for AWS
authentication.

|Code Issues|

|Code Coverage|

|Test Results|

Documentation
-------------

Full documentation can be found at `aws-auth-helper.readthedocs.org`_.

.. _aws-auth-helper.readthedocs.org: http://aws-auth-helper.readthedocs.io/en/latest/

.. |Code Issues| image:: https://www.quantifiedcode.com/api/v1/project/ea5b743486474c47b50734f846586474/badge.svg
   :target: https://www.quantifiedcode.com/app/project/ea5b743486474c47b50734f846586474
.. |Code Coverage| image:: https://codecov.io/github/drewsonne/awsauthhelper/coverage.svg?branch=master
   :target: https://codecov.io/github/drewsonne/awsauthhelper?branch=master
.. |Test Results| image:: https://travis-ci.org/drewsonne/awsauthhelper.svg?branch=master
   :target: https://travis-ci.org/drewsonne/awsauthhelper

""",
    description='Helper library providing ArgumentParser and Credentials class for AWS authentication',
    version=__version__,
    install_requires=['boto3'],
    packages=find_packages(),
    # tests_requires=['unittest2', 'mock'],
    url='http://aws-auth-helper.readthedocs.org/',
    download_url='https://github.com/drewsonne/awsauthhelper/archive/v.{version}.tar.gz'.format(version=__version__),
    license='GPLv2',
    test_suite='tests',
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
