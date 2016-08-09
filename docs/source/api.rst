=============
API Reference
=============

-----------------
AWSArgumentParser
-----------------

This class provides a prepackaged set of cli options for AWS authentication.

    +-----------------------------+-----------------------------------+-------------------------------------------------------+
    | CLI Option                  | Default                           | Description                                           |
    +=============================+===================================+=======================================================+
    | ``--aws-access-key-id``     | ``$AWS_ACCESS_KEY_ID``            |                                                       |
    +-----------------------------+-----------------------------------+-------------------------------------------------------+
    | ``--aws-secret-access-key`` | ``$AWS_SECRET_ACCESS_KEY``        |                                                       |
    +-----------------------------+-----------------------------------+-------------------------------------------------------+
    | ``--aws-session-token``     | ``$AWS_SESSION_TOKEN``            |                                                       |
    +-----------------------------+-----------------------------------+-------------------------------------------------------+
    | ``--region``                | ``$AWS_DEFAULT_REGION``           |                                                       |
    +-----------------------------+-----------------------------------+-------------------------------------------------------+
    | ``--profile``               | ``$AWS_DEFAULT_PROFILE``          |                                                       |
    +-----------------------------+-----------------------------------+-------------------------------------------------------+
    | ``--role``                  |                                   |                                                       |
    +-----------------------------+-----------------------------------+-------------------------------------------------------+
    | ``--config-path``           | ``$AWS_CONFIG_FILE``              | Custom path to an AWS config file                     |
    +-----------------------------+-----------------------------------+-------------------------------------------------------+
    | ``--credentials-path``      | ``$AWS_SHARED_CREDENTIALS_FILE``  | Custom path to an AWS credentials path                |
    +-----------------------------+-----------------------------------+-------------------------------------------------------+
    | ``--auth-debug``            |                                   | If this flag is enabled, execution of the             |
    |                             |                                   | application will stop when                            |
    |                             |                                   | :py:meth:`~awsauthhelper.Credentials.create_session`  |
    |                             |                                   | is called.                                            |
    +-----------------------------+-----------------------------------+-------------------------------------------------------+

The :py:class:`~awsauthhelper.AWSArgumentParser` class takes all the arguments of a :py:class:`argparser.ArgumentParser`
class in addition to:

- *role\_session\_name* is a default value in case ``--role_session_name`` is not provided by the user.
- *region* is a default value in case ``--region`` is not provided by the user.
- *profile* is a default value in case ``--profile`` is not provided by the user.
- *enforce_auth_type* enforces the type of arguments which must be passed to this utility. Can be one of:

    +---------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | Argument                  | Description                                                                                                             |
    +===========================+=========================================================================================================================+
    | ``keys``                  | Both ``aws_access_key_id`` and ``aws_secret_access_key`` must be provided by the user.                                  |
    +---------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | ``keys_with_session``     | All of ``aws_access_key_id``,  ``aws_secret_access_key``, and ``aws_session_token`` must be provided by the user.       |
    +---------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | ``profile``               | Only ``profile`` must be provided by the user.                                                                          |
    +---------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | ``profile_role``          | Both ``profile``, and ``role`` must be provided by the user.                                                            |
    +---------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | ``config``                | Only ``config_path`` must be provided by the user.                                                                      |
    +---------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | ``credentials``           | Only ``credentials_path`` must be provided by the user.                                                                 |
    +---------------------------+-------------------------------------------------------------------------------------------------------------------------+


Like :py:class:`argparse.ArgumentParser`, :py:class:`~awsauthhelper.AWSArgumentParser` allows chaining/inclusion of multiple
:py:class:`~argparse.ArgumentParser` objects through the ``list[argparse.ArgumentParser]: parents`` constructor
argument. The child :py:class:`~argparse.ArgumentParser` appears last in the list of options when ``--help`` is called,
so it's best to add *other* :py:class:`~argparse.ArgumentParser` objects to :py:class:`~awsauthhelper.AWSArgumentParser`, rather
than the reverse.

.. autoclass:: awsauthhelper.AWSArgumentParser
  :members:

--------------
validate_creds
--------------

Helper function validate your credential combinations

.. autofunction:: awsauthhelper.validate_creds

-----------
Credentials
-----------

The :py:class:`~awsauthhelper.Credentials` class allows us to encapsulate and hide all the aws auth
operations, exposing three key methods:

  -  :py:meth:`~awsauthhelper.Credentials.has_role`
  -  :py:meth:`~awsauthhelper.Credentials.assume_role()`
  -  :py:meth:`~awsauthhelper.Credentials.create_session()`

The arguments this class takes are the same format as
``libawsauth.ArgumentParser()``, so the Namespace object returned from
``argparse.ArgumentPareser.parse_args()`` can be wrapped in
``vars(...)`` and injected as *kwargs* into the ``Credentials(...)``
constructor.

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

.. autoclass:: awsauthhelper.Credentials
  :members:

-------------------
Password generation
-------------------

.. autofunction:: awsauthhelper.password.generate
