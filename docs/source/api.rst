=============
API Reference
=============

.. toctree::
    :maxdepth: 2

-----------------
AWSArgumentParser
-----------------

.. autoclass:: awsauthhelper.AWSArgumentParser
    :members:
    :special-members:
    
This class provides a prepackaged set of cli options for AWS
authentication. ``awsauthhelper.ArgumentParser(...)`` takes all the
arguments of a ``argparser.ArgumentParser(...)`` in addition to:

- *role\_session\_name* is a default value in case ``--role_session_name`` is not provided by the user.
- *region* is a default value in case ``--region`` is not provided by the user.
- *profile* is a default value in case ``--profile`` is not provided by the user.
- *enforce_auth_type* enforces the type of arguments which can be passed to this utility. Can be one of:
   - ``'keys'``
   - ``'keys_with_session'``
   - ``'profile'``
   - ``'profile_role'``
   - ``'config'``
   - ``'credentials'``


Like its superclass, ``awsauthhelper.ArgumentParser(...)`` allows
chaining/inclusion of multiple ``ArgumentParsers`` through the
``list[argparseArgumentParser]: parents`` constructor argument. The
child ArgumentParser appears last in the list of options when ``--help``
is called, so it's best to add *other* ArgumentParsers to
awsauthhelper's ArgumentParser, rather than the reverse.

-----------
Credentials
-----------

.. autoclass:: awsauthhelper.Credentials
    :members:
    :special-members:
    

-------------------
Password generation
-------------------

.. autofunction:: awsauthhelper.password.generate
