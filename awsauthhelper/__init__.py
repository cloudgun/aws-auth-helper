"""
AWS Auth Argument Parser and Session helper
"""
import argparse
import logging
import os
import warnings
from builtins import input

import boto3
from boto3 import Session

__author__ = 'Drew J. Sonne <drew.sonne@gmail.com>'


class AWSArgumentParser(argparse.ArgumentParser):
    """
    Helper Class containing a preset set of cli arguments for parsing into the Credentials object.
    If not explicitly set, arguments are read from the environment variables.
    """

    def __init__(self, role_session_name, region=None, profile=None,
                 enforce_auth_type=None, **kwargs):
        """
        Create our arguments and determine if we need to enforce an auth method.

        :param str role_session_name: Default name for the role session, in case a user does not provide one.
        :param str region: AWS Region
        :param str profile: Name of the profile in the AWS profile to use as the base configuration.
        :param str enforce_auth_type: The Authentication method can be locked to one of {'keys', 'keys_with_session', \
            'profile', 'profile_role','config','credentials'}
        :param dict kwargs:
        :return awsauthhelper.AWSArgumentParser:
        """

        super(AWSArgumentParser, self).__init__(add_help=False, **kwargs)

        aws_group = self.add_argument_group('AWS credentials')

        enforce_auth = (enforce_auth_type is not None)
        auth_uses_keys = (enforce_auth_type == 'keys')
        auth_uses_keys_with_session = (
            enforce_auth_type == 'keys_with_session')
        auth_uses_profile = (enforce_auth_type == 'profile')
        auth_uses_profile_role = (enforce_auth_type == 'profile_role')
        auth_uses_config_file = (enforce_auth_type == 'config')
        auth_uses_credentials_file = (enforce_auth_type == 'credentials')

        if (not enforce_auth) or (auth_uses_keys or auth_uses_keys_with_session):
            aws_group.add_argument(
                '--aws-access-key-id', help='AWS access key',
                action=EnvDefault, variable_name='AWS_ACCESS_KEY_ID',
                required=(auth_uses_keys or auth_uses_keys_with_session)
            )

        if (not enforce_auth) or (auth_uses_keys or auth_uses_keys_with_session):
            aws_group.add_argument(
                '--aws-secret-access-key',
                help=('Access and secret key variables override credentials '
                      'stored in credential and config files'),
                action=EnvDefault, variable_name='AWS_SECRET_ACCESS_KEY',
                required=(auth_uses_keys or auth_uses_keys_with_session)
            )

        if (not enforce_auth) or auth_uses_keys_with_session:
            aws_group.add_argument(
                '--aws-session-token',
                help='A session token is only required if you are using '
                     'temporary security credentials.',
                action=EnvDefault, variable_name='AWS_SESSION_TOKEN',
                required=auth_uses_keys_with_session
            )

        if (not enforce_auth) or (auth_uses_profile or auth_uses_profile_role):
            aws_group.add_argument(
                '--profile',
                help='This can be the name of a profile stored in a '
                     'credential or config file, or default to use the '
                     'default profile.',
                action=EnvDefault, variable_name='AWS_DEFAULT_PROFILE',
                default=profile,
                required=(auth_uses_profile or auth_uses_profile_role)
            )

        if (not enforce_auth) or auth_uses_profile_role:
            aws_group.add_argument(
                '--role', help='Fully qualified role arn to assume',
                required=auth_uses_profile_role
            )

        if (not enforce_auth) or auth_uses_config_file:
            aws_group.add_argument(
                '--config-path',
                help='Specify a custom location for ~/.aws/config',
                action=EnvDefault, variable_name='AWS_CONFIG_FILE',
                required=auth_uses_config_file
            )

        if (not enforce_auth) or auth_uses_credentials_file:
            aws_group.add_argument(
                '--credentials-path',
                help='Specify a custom location for ~/.aws/credentials',
                action=EnvDefault, variable_name='AWS_SHARED_CREDENTIALS_FILE',
                required=auth_uses_credentials_file
            )

        aws_group.add_argument(
            '--auth-debug',
            help='Enter debug mode, which will print credentials and exit at '
                 '`create_session`.',
            action='store_true', default=False
        )

        aws_group.add_argument(
            '--region',
            help='This variable overrides the default region of the in-use profile, if set.',
            action=EnvDefault, variable_name='AWS_DEFAULT_REGION',
            default=region, required=False
        )

        aws_group.add_argument(
            '--mfa-serial',
            help='MFA Device Serial ID',
            default=None, required=False,
        )

        # We can optionally have a default role session name.
        role_options = {
            'help': 'If you have assigned a role, set a --role-session-name'
        }
        if role_session_name is not None:
            role_options['default'] = role_session_name

        aws_group.add_argument('--role-session-name', **role_options)


DEBUG_ENV = os.environ.get('DEBUG_ENV', False)
if DEBUG_ENV:
    logging.basicConfig(level=logging.DEBUG)


class EnvDefault(argparse.Action):
    """
    Allow argparse values to be pulled from environment variables
    """

    def __init__(self, variable_name, required=True, default=None, **kwargs):
        if not default and variable_name:
            if variable_name in os.environ:
                logging.debug(
                    'EnvDefault:__init__(): os.environ["{environment_variable}"]={value}'.format(
                        value=os.environ[variable_name],
                        environment_variable=variable_name
                    ))
                default = os.environ[variable_name]
            else:
                logging.debug(
                    'EnvDefault:__init__(): "{environment_variable}" not in os.environ'.format(
                        environment_variable=variable_name))
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required,
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class Credentials(object):
    """
    Encapsulates processing of AWS credentials.
    """
    freeze_properties = [
        'region',
        'aws_secret_access_key',
        'aws_access_key_id',
        'aws_session_token',
        'profile',
        'role',
        'mfa_serial'
    ]
    default = None

    def __init__(self, region=None, aws_secret_access_key=None, aws_access_key_id=None, aws_session_token=None,
                 profile=None, role=None, role_session_name=None, config_path=None, credentials_path=None,
                 mfa_serial=None, mfa_session_life=900, mfa_token=None, force_mfa=False, auth_debug=False, **kwargs):
        """
        Handle the assumption of roles, and creation of Session objects.

        :param str region: AWS region
        :param str aws_secret_access_key:  ``AWS_SECRET_ACCESS_KEY`` to use for the base credentials.
        :param str aws_access_key_id: ``AWS_ACCESS_KEY_ID`` to use for the base credentials.
        :param str aws_session_token:  ``AWS_SESSION_TOKEN`` to use for the base credentials. Generally this should
            not be needed as roles are assumed through providing a role argument.
        :param str profile: Name of the profile in the AWS profile to use as the base configuration.
        :param str role: ARN of the AWS IAM Role to assume.
        :param str role_session_name: Custom name of the role session to override the default.
        :param str config_path:  Custom path to the aws config file if it is not in a location botocore expects.
        :param str credentials_path: Custom path to the aws credentials file if it is not in a path botocore expects.
        :param str mfa_serial: Identification number of the MFA device. If you set this argument, your  will be
            prompted for your MFA token.
        :param str mfa_session_life: The duration, in seconds, that the mfa credentials should remain valid.
        :param str mfa_token: MFA token to authentication to AWS with.
        :param bool auth_debug: Whether or not to print debug information. If True, exit() is throw at create_session()
        :param dict kwargs: catcher to allow arbitrary ``**var(my_args.parse_args(...))`` to be passed in.\
            Arguments in ``**kwargs`` not used at all.
        :return awsauthhelper.Credentials:
        """

        self.auth_debug = auth_debug

        if self.auth_debug:
            logging.basicConfig(level=logging.DEBUG)

        self.logger = logging.getLogger(__name__)

        self.region = region

        self.aws_secret_access_key = aws_secret_access_key
        self.logger.debug(
            '__init__(): self.aws_secret_access_key={value}'.format(value=aws_secret_access_key))

        self.aws_access_key_id = aws_access_key_id
        self.logger.debug('__init__(): self.aws_access_key_id={value}'.format(value=aws_access_key_id))

        self.aws_session_token = aws_session_token
        self.logger.debug('__init__(): self.aws_session_token={value}'.format(value=aws_secret_access_key))

        self.profile = profile
        self.logger.debug('__init__(): self.profile={value}'.format(value=profile))

        self.role = role
        self.logger.debug('__init__(): self.role={value}'.format(value=role))

        self.role_session_name = role_session_name
        self.logger.debug('__init__(): self.role_session_name={value}'.format(value=role_session_name))

        self.mfa_serial = mfa_serial
        self.logger.debug('__init__(): self.mfa_serial={value}'.format(value=mfa_serial))
        self.mfa_session_life = mfa_session_life
        self.logger.debug('__init__(): self.mfa_session_life={value}'.format(value=mfa_session_life))
        self.mfa_token = mfa_token
        self.logger.debug('__init__(): self.mfa_token={value}'.format(value=mfa_token))
        self._is_mfa_authenticated = False

        self.credentials_path = credentials_path
        self.logger.debug('__init__(): self.credentials_path={value}'.format(value=credentials_path))
        # Tell boto that we have a custom credentials location
        if self.credentials_path is not None:
            self.logger.debug('__init__(): os.environ[\'AWS_SHARED_CREDENTIALS_FILE\'] = {value}'.format(
                value=self.credentials_path))
            os.environ['AWS_SHARED_CREDENTIALS_FILE'] = self.credentials_path

        self.config_path = config_path
        self.logger.debug('__init__(): self.config_path={value}'.format(value=config_path))
        # Tell boto that we have a custom config location
        if self.config_path is not None:
            self.logger.debug('__init__(): os.environ[\'AWS_CONFIG_FILE\'] = {value}'.format(value=self.config_path))
            os.environ['AWS_CONFIG_FILE'] = self.config_path

        # Vars to store original credentials, in case we assume a role
        self._freeze = {}

        self.force_mfa = force_mfa
        self.logger.debug('__init__(): self.force_mfa={value}'.format(value=force_mfa))

        if Credentials.default is None:
            Credentials.default = self

    def assume_role(self):
        """
        Check if we have a role, and assume it if we do. Otherwise, raise exception.

        :raises ValueError: If a role has not be specified.
        :return awsauthhelper.Credentials: Allow chaining.
        """
        if self.using_role():
            self.logger.debug('assume_role(): self.using_role()=True')
            self._assume_role()
        else:
            self.logger.debug('assume_role(): self.using_role()=False')
            raise ValueError("Could not find keys or profile")
        return self

    def assume_temp_session(self):
        """
        Retrieve some temporary credentials from AWS

        :return awsauthhelper.Credentials: Allow chaining.
        """
        generate_session = self.get_session_generator(internal=True)
        response = generate_session().client('sts').get_session_token(DurationSeconds=self.mfa_session_life)
        self._switch_auth_scope(response)

        return self

    def freeze(self):
        """
        Take a snapshot of the credentials and remember them.

        :return awsauthhelper.Credentials:
        """
        for property_key in self.freeze_properties:
            self._freeze[property_key] = getattr(self, property_key, None)
        self.logger.debug('freeze(): self._freeze={value}'.format(value=self._freeze))

        return self

    def reset(self):
        """
        Reset Credentials object back to original state, pre any role assumptions.

        :return awsauthhelper.Credentials:
        """
        self.logger.debug('reset(): before self={value}'.format(value=vars(self)))
        for property_key in self.freeze_properties:
            setattr(self, property_key, self._freeze[property_key])
        self.logger.debug('reset(): after self={value}'.format(value=self._freeze))

        return self

    def create_session(self, internal=False):
        """
        DEPRECATED. Use awsauthhelper.Credentials.get_session_generator() instead.

        :return:
        """
        warnings.warn("Credentials.create_session() is deprecated in favour of Credentials.get_session_generator()",
                      DeprecationWarning)
        return self.get_session_generator(internal)

    def get_session_generator(self, internal=False):
        """
        Return a callable which will generate a boto3 Session

        :param bool internal: Whether or not this method was called from internal or external to the class
        :return callable(region):
        """
        session_credentials = {}
        self.logger.debug('create_session(): session_credentials={value}'.format(value=session_credentials))
        # Get the credentials which can assume the role
        if self.has_keys():
            self.logger.debug('create_session(): self.has_keys()=True')
            session_credentials['aws_access_key_id'] = self.aws_access_key_id
            session_credentials['aws_secret_access_key'] = self.aws_secret_access_key
            self.logger.debug('create_session(): session_credentials={value}'.format(value=session_credentials))
            if self.has_session_keys():
                self.logger.debug('create_session(): self.has_session_keys()=True')
                session_credentials['aws_session_token'] = self.aws_session_token
                self.logger.debug('create_session(): session_credentials={value}'.format(value=session_credentials))
        elif self.has_profile():
            self.logger.debug('create_session(): self.has_profile()=True')
            session_credentials['profile_name'] = self.profile
            self.logger.debug('create_session(): session_credentials={value}'.format(value=session_credentials))

        default_region = self.region
        self.logger.debug('create_session(): default_region={value}'.format(value=self.region))

        exit_at_session = self.auth_debug & (not internal)

        def build_session(region=default_region):
            """
            Return a Session for the specified region

            :param str region: AWS region to authenticate to
            :return boto3.session.Session:
            """
            session_credentials['region_name'] = region
            self.logger.debug('build_session(): region={value}'.format(value=self.region))

            # When debugging, end our auth process when our session is created.
            if exit_at_session:
                exit(1)

            return Session(**session_credentials)

        return build_session

    def authenticate_mfa(self):
        """
        Use the provided mfa_serial, the existing credentials, and get an mfa session token

        :return:
        """

        # Check we have an MFA token
        mfa_token = self.mfa_token
        if mfa_token is None:
            mfa_token = input('Enter MFA token: ')

        # Assume the role
        generate_session = self.get_session_generator(internal=True)
        credentials = generate_session().client('sts').get_session_token(
            SerialNumber=self.mfa_serial,
            DurationSeconds=self.mfa_session_life,
            TokenCode=mfa_token
        )

        self.logger.debug('authenticate_mfa(): credentials={value}'.format(value=credentials))
        self._is_mfa_authenticated = True

        return self._switch_auth_scope(credentials)

    def _assume_role(self):
        """
        Assume the new role, and store the old credentials.

        :return awsauthhelper.Credentials:
        """
        # Remember the state
        self.freeze()

        # Assume the role
        generate_session = self.get_session_generator(internal=True)
        credentials = generate_session().client('sts').assume_role(
            RoleArn=self.role,
            RoleSessionName=self.role_session_name
        )
        self.logger.debug('_assume_role(): credentials={value}'.format(value=credentials))

        return self._switch_auth_scope(credentials)

    def _switch_auth_scope(self, credential_payload):
        self._orig_aws_access_key_id = self.aws_access_key_id
        self._orig_aws_secret_access_key = self.aws_secret_access_key
        self._orig_aws_session_token = self.aws_session_token

        credentials = credential_payload['Credentials']

        self.aws_access_key_id = credentials['AccessKeyId']
        self.logger.debug('_assume_role(): self.aws_access_key_id={value}'.format(value=credentials['AccessKeyId']))

        self.aws_secret_access_key = credentials['SecretAccessKey']
        self.logger.debug(
            '_assume_role(): self.aws_secret_access_key={value}'.format(value=credentials['SecretAccessKey']))

        self.aws_session_token = credentials['SessionToken']
        self.logger.debug('_assume_role(): self.aws_session_token={value}'.format(value=credentials['SessionToken']))

        return self

    def _build_kwargs(self):
        """
        Build a dict, which can be used to pass into a boto3.Session object.

        :return Dict[str, str]:
        """
        keys = {}

        if self.aws_access_key_id is not None:
            keys['aws_access_key_id'] = self.aws_access_key_id

        if self.aws_secret_access_key is not None:
            keys['aws_secret_access_key'] = self.aws_secret_access_key

        if self.profile is not None:
            keys['profile_name'] = self.profile

        if self.region is not None:
            keys['region_name'] = self.region

        if self.has_session_keys():
            keys['aws_session_token'] = self.aws_session_token

        return keys

    def has_keys(self):
        """
        Do we have key credentials?

        :return bool:
        """
        return (self.aws_access_key_id is not None) and (self.aws_secret_access_key is not None)

    def has_session_keys(self):
        """
        Do we have temporal key credentials?

        :return bool:
        """
        return (self.aws_session_token is not None) and self.has_keys()

    def has_profile(self):
        """
        Do we have profile credentials?

        :return bool:
        """
        return self.profile is not None

    def has_role(self):
        """
        Do we have a role to assume?

        :return bool:
        """
        return self.role is not None

    def using_role(self):
        """
        If we have a role and either a set of credentials or a profile, then we should assume the role.

        :return bool:
        """
        return (self.has_role() and (self.has_keys() or self.has_profile()))

    def has_mfa(self):
        """
        Have we been provided an mfa_serial to use?

        :return bool:
        """
        return self.mfa_serial is not None

    def use_as_global(self):
        """
        Set this object to use its current credentials as the global boto3 settings.
        If a role has been assumed, the assumed credentials will be used.
        If a role is set but has not been assumed, the base credentials will be used.
        WARNING: This will affect all calls made to boto3.

        :return awsauthhelper.Credentials:
        """
        boto3.setup_default_session(**self._build_kwargs())


def validate_credentials(aws_access_key_id=None, aws_secret_access_key=None,
                         aws_session_token=None, profile=None, **kwargs):
    """
    Perform validation on CLI options

    :param str aws_access_key_id:
    :param str aws_secret_access_key:
    :param str aws_session_token:
    :param str profile:
    :param kwargs:
    :raise argparse.ArgumentError: If ``--aws-session-token`` is specified but ``--aws-secret-access-key`` and \
        ``--aws-access-key-id`` are not
    :raise argparse.ArgumentError: If ``--profile`` is specified and ``--aws-secret-access-key`` or \
        ``--aws-access-key-id`` are also specified.
    :raise argparse.ArgumentError: If one of ``--aws-secret-access-key`` or ``--aws-access-key-id`` have been
        provided but not both.
    :return:
    """
    # 1 - Check if we have temporal keys
    if (aws_session_token is not None) and ((aws_secret_access_key is None) or (aws_access_key_id is None)):
        raise argparse.ArgumentError(
            argument=None,
            message="'--aws-session-token' requires '--aws-secret-access-key' and '--aws-access-key-id'"
        )

    # 2 - Check if we have a profile
    if profile and (aws_access_key_id or aws_secret_access_key):
        raise argparse.ArgumentError(
            argument=None,
            message="You can not set both '--profile' and '--aws-secret-access-key'/'--aws-access-key-id'"
        )

    # 3 - Check if we have keys
    if bool(aws_secret_access_key) != bool(aws_access_key_id):
        raise argparse.ArgumentError(
            argument=None,
            message="'Both '--aws-secret-access-key' and '--aws-access-key-id' must be provided."
        )

    return True
