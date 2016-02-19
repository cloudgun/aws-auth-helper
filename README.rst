aws-auth-helper
===============

Helper library providing ArgumentParser and Credentials class for AWS
authentication

.. image:: https://www.quantifiedcode.com/api/v1/project/ea5b743486474c47b50734f846586474/badge.svg
  :target: https://www.quantifiedcode.com/app/project/ea5b743486474c47b50734f846586474
  :alt: Code issues

.. image:: https://codecov.io/github/drewsonne/pyum/coverage.svg?branch=master
  :target: https://codecov.io/github/cloudgun/aws-auth-helper?branch=master

.. image:: https://travis-ci.org/cloudgun/aws-auth-helper.svg?branch=master
  :target: https://travis-ci.org/cloudgun/aws-auth-helper

Setup
-----

Installation
------------

::

    $ pip install aws-auth-helper

Usage
-----

This library provides two main classes:

-  ``awsauthhelper.ArgumentParser``
-  ``awsauthhelper.Credentials``

awsauthhelper.ArgumentParser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This class provides a prepackaged set of cli options for AWS
authentication. ``awsauthhelper.ArgumentParser(...)`` takes all the
arguments of a ``argparser.ArgumentParser(...)`` in addition to
*default\_role\_session\_name*. When using a role, you'll need to set a
*default\_role\_session\_name* in case one is not provided through the
command line arguments.

Like its superclass, ``awsauthhelper.ArgumentParser(...)`` allows
chaining/inclusion of multiple ``ArgumentParsers`` through the
``list[argparseArgumentParser]: parents`` constructor argument. The
child ArgumentParser appears last in the list of options when ``--help``
is called, so it's best to add *other* ArgumentParsers to
awsauthhelper's ArgumentParser, rather than the reverse. For example,

::

    >>> import argparse
    >>> import awsauthhelper

    >>> my_aws_app = argparse.ArgumentParser(
    ...     description='Lists EC2 instances'
    ... )
    >>> my_aws_app.add_argument('--max-instances', type=int, required=True)

    >>> aws_options = awsauthhelper.AWSArgumentParser(default_role_session_name='my_app', parents=[my_aws_app])
    >>> aws_options.print_help()

    usage:  [-h] --max-instances MAX_INSTANCES
        [--aws-access-key-id AWS_ACCESS_KEY_ID]
        [--aws-secret-access-key AWS_SECRET_ACCESS_KEY]
        [--aws-session-token AWS_SESSION_TOKEN] [--region REGION]
        [--profile PROFILE] [--role ROLE] [--auth-debug]
        [--role-session-name ROLE_SESSION_NAME]

    optional arguments:
      -h, --help            show this help message and exit
      --max-instances MAX_INSTANCES

    AWS credentials:
      --aws-access-key-id AWS_ACCESS_KEY_ID
                            AWS access key
      --aws-secret-access-key AWS_SECRET_ACCESS_KEY
                            Access and secret key variables override credentials
                            stored in credential and config files
      --aws-session-token AWS_SESSION_TOKEN
                            A session token is only required if you are using
                            temporary security credentials.
      --region REGION       This variable overrides the default region of the in-
                            use profile, if set.
      --profile PROFILE     This can be the name of a profile stored in a
                            credential or config file, or default to use the
                            default profile.
      --role ROLE           Fully qualified role arn to assume
      --auth-debug          Enter debug mode, which will print credentials and
                            then exist at `create_session`.
      --role-session-name ROLE_SESSION_NAME
                            If you have assigned a role, set a --role-session-name  

*Note* that the AWS options appeared after our application options.

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

If your environment variables are set, they will be used as defaults for
``awsauthhelper.ArgumentParser(...)``. The class maps to and is aware of
the following environment variables:

+-----------------------------+-------------------------------+
| Environment Variable        | cli option                    |
+=============================+===============================+
| ``AWS_ACCESS_KEY_ID``       | ``--aws-access-key-id``       |
+-----------------------------+-------------------------------+
| ``AWS_SECRET_ACCESS_KEY``   | ``--aws-secret-access-key``   |
+-----------------------------+-------------------------------+
| ``AWS_SESSION_TOKEN``       | ``--aws-session-token``       |
+-----------------------------+-------------------------------+
| ``AWS_DEFAULT_REGION``      | ``--region``                  |
+-----------------------------+-------------------------------+
| ``AWS_DEFAULT_PROFILE``     | ``--profile``                 |
+-----------------------------+-------------------------------+

awsauthhelper.Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~

The Credentials class allows us to encapsulate and hide all the aws auth
operations, exposing three key methods:

-  ``has_role()``
-  ``assume_role()``
-  ``create_session()``

The arguments this class takes are the same format as
``libawsauth.ArgumentParser()``, so the Namespace object returned from
``argparse.ArgumentPareser.parse_args()`` can be wrapped in
``vars(...)`` and injected as *kwargs* into the ``Credentials(...)``
constructor. Following from the previous example:

::

    >>> configs = aws_options.parse_args()
    >>> credentials = awsauthhelper.Credentials(
    ...   **vars(configs)
    ... )

    >>> if credentials.has_role():
    >>>     credentials.assume_role()
    >>> boto3_session = credentials.create_session()

    >>> s3 = boto3_session().resource('s3')
    >>> for bucket in s3.buckets.all():
    >>>    print(bucket.name)

    >>> for region in regions:
    >>>    # The session object can be 're-authorised' across regions.
    >>>    print(
    ...       boto3_session(region=region['RegionName']).client('ec2').describe_instances()
    ...    )

Contributing
------------

Please create a feature/branch, and create test cases for any edits you
make. When doing pull requests, please create the request onto the
development branch.

Virtual Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~

When doing development and testing, it's good practice to use a
virtualenv. A virtualenv is a sandboxed python environment which does
not modify the system python installation You'll need the following
utilities:

Install `virtualenv <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`__
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    $ pip install virtualenv

Install `pyenv <https://github.com/yyuu/pyenv>`__
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Please read instructions at https://github.com/yyuu/pyenv#installation

Install `pyenv-virtualenv <https://github.com/yyuu/pyenv-virtualenv>`__
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Please read instructions at
https://github.com/yyuu/pyenv-virtualenv#installation

Create python virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    $ pyenv install 2.7.10
    $ pyenv virtualenv 2.7.10 aws-auth-helper
    $ pyenv versions
    * system
      2.7.10
      myvirtualenv
    $ pyenv activate aws-auth-helper

Configuring environment
^^^^^^^^^^^^^^^^^^^^^^^

Now that you have a working virtualenv, you can install the utility in
development mode. Keep in mind that the 'activate' step, is valid only
for a single session. If you close the terminal you'll have to run
``pyenv activate aws-auth-helper`` again. You can now run pip, python,
and aws-auth-helper while only referring to the local python environment
created in $WORKSPACE/aws-auth-helper. You can see this by running:

::

    (my-utility)$ which pip
    ~/.pyenv/versions/aws-auth-helper/bin/pip
    (my-utility)$ which python
    ~/.pyenv/versions/aws-auth-helper/bin/python

Development Mode
~~~~~~~~~~~~~~~~

When testing this utility, you can install it and still edit the source files.

Installation
^^^^^^^^^^^^

::

    $ cd $WORKSPACE/aws-auth-helper
    $ make install
