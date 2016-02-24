from setuptools import find_packages, setup

setup(
    name='aws-auth-helper',
    long_description=open('README.rst').read(),
    description='Helper library providing ArgumentParser and Credentials class for AWS authentication',
    version='1.2.4',
    install_requires=['boto3'],
    packages=find_packages(),
    tests_requires=['unittest2','mock'],
    url='http://github.com/cloudgun/aws-auth-helper',
    license='GPLv2',
    author='Drew J. Sonne',
    author_email='drew.sonne@gmail.com',
)
