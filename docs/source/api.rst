=============
API Reference
=============

.. toctree::
  :maxdepth: 1

-----------------
AWSArgumentParser
-----------------

.. autoclass:: awsauthhelper.AWSArgumentParser
  :members:

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
    | ``'keys'``                | Both ``--aws-access-key-id`` and ``--aws-secret-access-key`` must be provided by the user.                              |
    +---------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | ``'keys_with_session'``   | All of ``--aws-access-key-id``,  ``--aws-secret-access-key``, and ``--aws-session-token`` must be provided by the user. |
    +---------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | ``'profile'``             | Only ``--profile`` must be provided by the user.                                                                        |
    +---------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | ``'profile_role'``        | Both ``--profile``, and ``--role`` must be provided by the user.                                                        |
    +---------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | ``'config'``              | Only ``--config-path`` must be provided by the user.                                                                    |
    +---------------------------+-------------------------------------------------------------------------------------------------------------------------+
    | ``'credentials'``         | Only ``--credentials-path`` must be provided by the user.                                                               |
    +---------------------------+-------------------------------------------------------------------------------------------------------------------------+


Like :py:class:`argparse.ArgumentParser`, :py:class:`~awsauthhelper.AWSArgumentParser` allows chaining/inclusion of multiple
:py:class:`~argparse.ArgumentParser` objects through the ``list[argparse.ArgumentParser]: parents`` constructor
argument. The child :py:class:`~argparse.ArgumentParser` appears last in the list of options when ``--help`` is called,
so it's best to add *other* :py:class:`~argparse.ArgumentParser` objects to :py:class:`~awsauthhelper.AWSArgumentParser`, rather
than the reverse.

--------------
validate_creds
--------------

Helper function validate your credential combinations

.. autofunction:: awsauthhelper.validate_creds


-----------
Credentials
-----------

.. autoclass:: awsauthhelper.Credentials
:members:
      
      
-------------------
Password generation
-------------------

.. autofunction:: awsauthhelper.password.generate
