========
Tutorial
========


This tutorial will take you through a quick example of a normal ArgumentParser class, and then show you how to integrate
the AWSArgumentParser into this.

First import the default ArgumentParser

>>> from argparse import ArgumentParser

First, let's create an argument parser for the rest of the options in our new utility.

>>> # Instantiate an argument parser, add an argument, and print the help text
>>> my_aws_app = ArgumentParser(description='Lists EC2 instances', prog='my_app')
>>> my_aws_app.add_argument('--name', required=True)
>>> my_aws_app.print_help()
usage: my_app [-h] --name NAME
<BLANKLINE>
Lists EC2 instances
<BLANKLINE>
optional arguments:
  -h, --help         show this help message and exit
  --name NAME
<BLANKLINE>
>>> my_aws_app.parse_args(args=['--name', 'Hello, World!'])
Namespace(name='Hello, World!')
<BLANKLINE>

Now that we have a parser for the arguments of our utility, we can add the AWSArgumentParser.

>>> from awsauthhelper import AWSArgumentParser
>>> aws_options = AWSArgumentParser(role_session_name='ec2_audit')

.. note:: You **must** set a `role_session_name` parameter in-case the user does not provide one on the cli.

Now let's recreate our app options, so that we can chain the AWSArgumentParser.

>>> my_aws_app = argparse.ArgumentParser(
>>>     prog='my_app',
>>>     description='Lists EC2 instances',
>>>     parents=[
>>>       aws_options
>>>     ]
>>> )
>>> my_aws_app.add_argument('--max-instances', type=int)
>>> my_aws_app.print_help()
usage: my_app [-h] [--aws-access-key-id AWS_ACCESS_KEY_ID]
              [--aws-secret-access-key AWS_SECRET_ACCESS_KEY]
              [--aws-session-token AWS_SESSION_TOKEN] [--region REGION]
              [--profile PROFILE] [--role ROLE] [--config-path CONFIG_PATH]
              [--credentials-path CREDENTIALS_PATH] [--auth-debug]
              [--role-session-name ROLE_SESSION_NAME]
              [--max-instances MAX_INSTANCES]
<BLANKLINE>
Lists EC2 instances
<BLANKLINE>
optional arguments:
  -h, --help            show this help message and exit
  --max-instances MAX_INSTANCES
<BLANKLINE>
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
  --config-path CONFIG_PATH
                        Specify a custom location for ~/.aws/config
  --credentials-path CREDENTIALS_PATH
                        Specify a custom location for ~/.aws/credentials
  --auth-debug          Enter debug mode, which will print credentials and
                        then exist at `create_session`.
  --role-session-name ROLE_SESSION_NAME
                        If you have assigned a role, set a --role-session-name

.. note:: It is possible to use the AWSArgumentParser as your main ArgumentParser object, and  like you would with a normal ArgumentParser object, but if you chain the ArgumentParser and AWSArgumentParser, you can segment your options in the help text, as you can see here. Furthermore, if you set the AWSArgumentParser as the parent, the aws options will be rendered at the end of the help.

