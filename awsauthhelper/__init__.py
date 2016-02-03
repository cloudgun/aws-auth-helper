import argparse
import os
import logging
from boto3 import Session

__author__ = 'drews'

class AWSArgumentParser(argparse.ArgumentParser):
    """
    >>> import argparse
    >>> import awsauthhelper

    # My cli utilities arguments
    >>> my_options = argparse.ArgumentParser(description='Lists EC2 instances')
    >>> my_options.add_argument('--message', required=True)
    >>> my_options.print_help()

    usage: my_app [-h] --message MESSAGE

    Lists EC2 instances

    optional arguments:
      -h, --help         show this help message and exit
      --message MESSAGE

    # Add the aws defaults
    >>> aws_options = awsauthhelper.AWSArgumentParser(default_role_session_name='elasticsearch_creation')

    >>> my_aws_app = argparse.ArgumentParser(
    >>>     description='Lists EC2 instances',
    >>>     parents=[
    >>>       aws_options
    >>>     ]
    >>> )
    >>> my_aws_app.add_argument('--max-instances', type=int)
    >>> my_aws_app.print_help()
    usage: demo.py [-h] [--aws-access-key-id AWS_ACCESS_KEY_ID]
               [--aws-secret-access-key AWS_SECRET_ACCESS_KEY]
               [--aws-session-token AWS_SESSION_TOKEN] [--region REGION]
               [--profile PROFILE] [--role ROLE]
               [--role-session-name ROLE_SESSION_NAME]
               [--max-instances MAX_INSTANCES]

    Lists EC2 instances

    optional arguments:
      -h, --help            show this help message and exit
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
      --role ROLE           Role to assume
      --role-session-name ROLE_SESSION_NAME
                            If you have assigned a role, set a RoleSessionName
      --max-instances MAX_INSTANCES
    """
    def __init__(self, default_role_session_name, **kwargs):

        super(AWSArgumentParser, self).__init__(add_help=False, **kwargs)

        aws_group = self.add_argument_group('AWS credentials')

        aws_group.add_argument('--aws-access-key-id', action=EnvDefault, envvar='AWS_ACCESS_KEY_ID', help='AWS access key', required=False)
        aws_group.add_argument('--aws-secret-access-key', action=EnvDefault, envvar='AWS_SECRET_ACCESS_KEY',
                               help='Access and secret key variables override credentials stored in credential and config files', required=False)
        aws_group.add_argument('--aws-session-token', action=EnvDefault, envvar='AWS_SESSION_TOKEN',
                               help='A session token is only required if you are using temporary security credentials.', required=False)
        aws_group.add_argument('--region', action=EnvDefault, envvar='AWS_DEFAULT_REGION',
                               help='This variable overrides the default region of the in-use profile, if set.', required=False)
        aws_group.add_argument('--profile', action=EnvDefault, envvar='AWS_DEFAULT_PROFILE',
                               help='This can be the name of a profile stored in a credential or config file, or default to use the default profile.',
                               default=None, required=False)
        aws_group.add_argument('--role', help='Fully qualified role arn to assume')
        aws_group.add_argument('--auth-debug', help='Enter debug mode, which will print credentials and then exist at `create_session`.', action='store_true', default=False)

        # We can optionally have a default role session name.
        role_options = {
            'help': 'If you have assigned a role, set a --role-session-name'
        }
        if default_role_session_name is not None:
            role_options['default'] = default_role_session_name

        aws_group.add_argument('--role-session-name', **role_options)

DEBUG_ENV = False
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
    The general usage is the following form:

        >>> credentials = awsauthhelper.Credentials(**kwargs) # **kwargs passed from awsauthhelper.get_arg_parser
        >>> default_session = credentials.create_session()

        # Use our default credentials to get a list of all regions
        >>> regions = default_session().client('ec2').describe_regions()

        # For the rest of our script, we want to assume a role
        >>> if credentials.using_role():
        >>>     credentials.freeze()                 # Remember our default credentials
        >>>     credentials.assume_role()            # Assume the role we provided in **kwargs
        >>> role_session = credentials.create_session()

        >>> for region in regions:
               # The session object can be 're-authorised' across regions.
        >>>    print(role_session(region=region['RegionName']).client('ec2').describe_instances())

    """
    freeze_properties = ['region', 'aws_secret_access_key', 'aws_access_key_id', 'aws_session_token', 'profile', 'role']
    default = None

    def __init__(self, region=None, aws_secret_access_key=None, aws_access_key_id=None, aws_session_token=None,
                 profile=None, role=None, role_session_name=None, auth_debug=False, **kwargs):

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

        # Vars to store original creds, incase we assume a role
        self._freeze = {}

        if Credentials.default is None:
            Credentials.default = self

    def assume_role(self):
        if self.using_role():
            self.logger.debug('assume_role(): self.using_role()=True')
            self._assume_role()
        else:
            self.logger.debug('assume_role(): self.using_role()=False')
            raise ValueError("Could not find keys or profile")
        return self

    def freeze(self):
        """
        Take a snapshot fo the credentials and remember them.
        :return:
        """
        for property in self.freeze_properties:
            self._freeze[property] = getattr(self, property, None)
        self.logger.debug('freeze(): self._freeze={value}'.format(value=self._freeze))

    def reset(self):
        """
        Reset Credentials object back to original state, pre any role assumptions.
        :return:
        """
        self.logger.debug('reset(): before self={value}'.format(value=vars(self)))
        for property in self.freeze_properties:
            setattr(self, property, self._freeze[property])
        self.logger.debug('reset(): after self={value}'.format(value=vars(self._freeze)))

    def create_session(self, internal=False):

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
            session_credentials['region_name'] = region
            self.logger.debug('build_session(): region={value}'.format(value=self.region))

            if exit_at_session:
                exit(1)

            return Session(**session_credentials)

        return build_session

    def _assume_role(self):
        """
        Assume the new role, and store the old credentials
        :return:
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
        self.logger.debug('_assume_role(): self.aws_access_key_id={value}'.format(value=credentials['Credentials']['AccessKeyId']))

        self.aws_secret_access_key = credentials['Credentials']['SecretAccessKey']
        self.logger.debug('_assume_role(): self.aws_secret_access_key={value}'.format(value=credentials['Credentials']['SecretAccessKey']))

        self.aws_session_token = credentials['Credentials']['SessionToken']
        self.logger.debug('_assume_role(): self.aws_session_token={value}'.format(value=credentials['Credentials']['SessionToken']))

    def has_keys(self):
        """
        Do we have key credentials?
        :return:
        """
        return (self.aws_access_key_id is not None) and \
               (self.aws_secret_access_key is not None)

    def has_session_keys(self):
        """
        Do we have temporal key credentials?
        :return:
        """
        return (self.aws_session_token is not None) and \
               self.has_keys()

    def has_profile(self):
        """
        Do we have profile credentials?
        :return:
        """
        return self.profile is not None

    def has_role(self):
        """
        Do we have a role to assume?
        :return:
        """
        return self.role is not None

    def using_role(self):
        """
        If we have a role and either a set of credentials or a profile, then we should assume the role
        :return:
        """
        return (
            self.has_role() and
            (self.has_keys() or self.has_profile())
        )

def validate_creds(aws_access_key_id, aws_secret_access_key, aws_session_token, profile, **kwargs):
    # 1 - Check if we have temporal keys
    if aws_session_token is not None:
        if (aws_secret_access_key is None) or (aws_access_key_id is None):
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