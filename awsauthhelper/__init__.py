import os
import boto3
import logging
import argparse
from boto3 import Session

__author__ = 'drews'


class AWSArgumentParser(argparse.ArgumentParser):
    """
    Helper Class containing a preset set of cli arguments for parsing into the Credentials object.
    If not explicity set, arguments are read from the environment variables.
    """

    def __init__(self, role_session_name, region=None, profile=None, enforce_auth_type=None, **kwargs):
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
        auth_must_use_keys = (enforce_auth_type == 'keys')
        auth_must_use_keys_with_session = (enforce_auth_type == 'keys_with_session')
        auth_must_use_profile = (enforce_auth_type == 'profile')
        auth_must_use_profile_role = (enforce_auth_type == 'profile_role')
        auth_must_use_config_file = (enforce_auth_type == 'config')
        auth_must_use_credentials_file = (enforce_auth_type == 'credentials')

        if (not enforce_auth) or (auth_must_use_keys or auth_must_use_keys_with_session):
            aws_group.add_argument(
                '--aws-access-key-id', help='AWS access key',
                action=EnvDefault, envvar='AWS_ACCESS_KEY_ID',
                required=(auth_must_use_keys or auth_must_use_keys_with_session)
            )

        if (not enforce_auth) or (auth_must_use_keys or auth_must_use_keys_with_session):
            aws_group.add_argument(
                '--aws-secret-access-key', help=('Access and secret key variables override credentials '
                                                 'stored in credential and config files'),
                action=EnvDefault, envvar='AWS_SECRET_ACCESS_KEY',
                required=(auth_must_use_keys or auth_must_use_keys_with_session)
            )

        if (not enforce_auth) or auth_must_use_keys_with_session:
            aws_group.add_argument(
                '--aws-session-token',
                help='A session token is only required if you are using temporary security credentials.',
                action=EnvDefault, envvar='AWS_SESSION_TOKEN',
                required=auth_must_use_keys_with_session
            )

        if (not enforce_auth) or (auth_must_use_profile or auth_must_use_profile_role):
            aws_group.add_argument(
                '--profile', help=('This can be the name of a profile stored in a credential or config file, or '
                                   'default to use the default profile.'),
                action=EnvDefault, envvar='AWS_DEFAULT_PROFILE',
                default=profile, required=(auth_must_use_profile or auth_must_use_profile_role)
            )

        if (not enforce_auth) or auth_must_use_profile_role:
            aws_group.add_argument(
                '--role', help='Fully qualified role arn to assume',
                required=auth_must_use_profile_role
            )

        if (not enforce_auth) or auth_must_use_config_file:
            aws_group.add_argument(
                '--config-path', help='Specify a custom location for ~/.aws/config',
                action=EnvDefault, envvar='AWS_CONFIG_FILE',
                required=auth_must_use_config_file
            )

        if (not enforce_auth) or auth_must_use_credentials_file:
            aws_group.add_argument(
                '--credentials-path', help='Specify a custom location for ~/.aws/credentials',
                action=EnvDefault, envvar='AWS_SHARED_CREDENTIALS_FILE',
                required=auth_must_use_credentials_file
            )

        aws_group.add_argument(
            '--auth-debug', help='Enter debug mode, which will print credentials and  exist at `create_session`.',
            action='store_true', default=False
        )
        
        aws_group.add_argument(
            '--region', help='This variable overrides the default region of the in-use profile, if set.',
            action=EnvDefault, envvar='AWS_DEFAULT_REGION',
            default=region, required=False
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

    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                logging.debug('EnvDefault:__init__(): os.environ["{envvar}"]={value}'.format(
                    value=os.environ[envvar],
                    envvar=envvar
                ))
                default = os.environ[envvar]
            else:
                logging.debug('EnvDefault:__init__(): "{envvar}" not in os.environ'.format(envvar=envvar))
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class Credentials(object):
    """
    Encapsulates processing of AWS credentials.
    """
    freeze_properties = ['region', 'aws_secret_access_key', 'aws_access_key_id', 'aws_session_token', 'profile', 'role']
    default = None

    def __init__(self, region=None, aws_secret_access_key=None, aws_access_key_id=None, aws_session_token=None,
                 profile=None, role=None, role_session_name=None, config_path=None, credentials_path=None,
                 auth_debug=False, **kwargs):
        """
        Handle the assumption of roles, and creation of Session objects.

        :param str region: AWS region
        :param str aws_secret_access_key:  ``AWS_SECRET_ACCESS_KEY`` to use for the base credentials.
        :param str aws_access_key_id: ``AWS_ACCESS_KEY_ID`` to use for the base credentials.
        :param str aws_session_token:  ``AWS_SESSION_TOKEN`` to use for the base credentials. Generally this should not\
            be needed as roles are assumed through providing a role argument.
        :param str profile: Name of the profile in the AWS profile to use as the base configuration.
        :param str role: ARN of the AWS IAM Role to assume.
        :param str role_session_name: Custom name of the role session to override the default.
        :param str config_path:  Custom path to the aws config file if it is not in a location botocore expects.
        :param str credentials_path: Custom path to the aws credentials file if it is not in a path botocore expects.
        :param bool auth_debug: Whether or not to print debug information. If True,  exit() is throw at create_session()
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
        self.logger.debug('__init__(): self.aws_secret_access_key={value}'.format(value=aws_secret_access_key))

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

        self.credentials_path = credentials_path
        self.logger.debug('__init__(): self.credentials_path={value}'.format(value=credentials_path))
        # Tell boto that we have a custom credentials location
        if self.credentials_path is not None:
            self.logger.debug('__init__(): os.environ[\'AWS_SHARED_CREDENTIALS_FILE\'] = {value}'.format(
                value=self.credentials_path
            ))
            os.environ['AWS_SHARED_CREDENTIALS_FILE'] = self.credentials_path

        self.config_path = config_path
        self.logger.debug('__init__(): self.config_path={value}'.format(value=config_path))
        # Tell boto that we have a custom config location
        if self.config_path is not None:
            self.logger.debug('__init__(): os.environ[\'AWS_CONFIG_FILE\'] = {value}'.format(
                value=self.config_path
            ))
            os.environ['AWS_CONFIG_FILE'] = self.config_path

        # Vars to store original creds, incase we assume a role
        self._freeze = {}

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
        Return a function to generate our session with local vars as a closure.

        :param bool internal: Wether or not this method was called from internal or external to the class
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

    def _assume_role(self):
        """
        Assume the new role, and store the old credentials.

        :return awsauthhelper.Credentials:
        """
        # Remember the state
        self.freeze()

        # Assume the role
        session = self.create_session(internal=True)
        credentials = session().client('sts').assume_role(
            RoleArn=self.role,
            RoleSessionName=self.role_session_name
        )
        self.logger.debug('_assume_role(): credentials={value}'.format(value=credentials))

        self._orig_aws_access_key_id = self.aws_access_key_id
        self._orig_aws_secret_access_key = self.aws_secret_access_key
        self._orig_aws_session_token = self.aws_session_token

        self.aws_access_key_id = credentials['Credentials']['AccessKeyId']
        self.logger.debug(
            '_assume_role(): self.aws_access_key_id={value}'.format(
                value=credentials['Credentials']['AccessKeyId']))

        self.aws_secret_access_key = credentials['Credentials']['SecretAccessKey']
        self.logger.debug('_assume_role(): self.aws_secret_access_key={value}'.format(
            value=credentials['Credentials']['SecretAccessKey']))

        self.aws_session_token = credentials['Credentials']['SessionToken']
        self.logger.debug(
            '_assume_role(): self.aws_session_token={value}'.format(
                value=credentials['Credentials']['SessionToken']))

        return self

    def _build_kwargs(self):
        """
        Build a dict, which can be used to pass into a boto3.Session object.

        :return Dict[str, str]:
        """
        keys = {
            'aws_access_key_id': self.aws_access_key_id,
            'aws_secret_access_key': self.aws_secret_access_key
        }
        if self.has_session_keys():
            keys['aws_session_token'] = self.aws_session_token
        return keys

    def has_keys(self):
        """
        Do we have key credentials?

        :return bool:
        """
        return (self.aws_access_key_id is not None) and \
               (self.aws_secret_access_key is not None)

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
        return (
            self.has_role() and
            (self.has_keys() or self.has_profile())
        )

    def use_as_global(self):
        """
        Set this object to use its current credentials as the global boto3 settings.
        If a role has been assumed, the assumed credentials will be used.
        If a role is set but has not been assumed, the base credentials will be used.
        WARNING: This will affect all calls made to boto3.

        :return awsauthhelper.Credentials:
        """
        boto3.setup_default_session(**self._build_kwargs())


def validate_creds(aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None, profile=None, **kwargs):
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
    :raise argparse.ArgumentError: If one of ``--aws-secret-access-key`` or ``--aws-access-key-id`` have been provided \
        but not both.
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
