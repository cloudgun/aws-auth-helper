import json
import sys
from argparse import ArgumentParser

from awsauthhelper import AWSArgumentParser, Credentials

ENV_VAR_MAPPING = {
    'aws_access_key_id': 'AWS_ACCESS_KEY_ID',
    'aws_secret_access_key': 'AWS_SECRET_ACCESS_KEY',
    'aws_session_token': 'AWS_SESSION_TOKEN'
}


def main(args=sys.argv):
    utility_args = ArgumentParser(description='aws-auth-helper')
    utility_args.add_argument('--use-sts', action='store_true', default=False)
    utility_args.add_argument('--shell-init', action='store_true', default=False)
    utility_args.add_argument('--demo', action='store_true', default=False)

    cli_parser = AWSArgumentParser(role_session_name='aws-auth-helper-cli', parents=[utility_args])
    cli_options = cli_parser.parse_args()

    credentials = Credentials(**vars(cli_options))

    # if credentials.has_mfa():
    #     credentials.authenticate_mfa()

    if credentials.has_role():
        credentials.assume_role()
    elif cli_options.use_sts:
        credentials.assume_temp_session()

    session_generator = credentials.get_session_generator()

    if cli_options.shell_init:

        env_vars = []
        for key, value in credentials._build_kwargs().items():
            env_vars.append(
                "export {ENVNAME}=\"{ENVVALUE}\"".format(
                    ENVNAME=ENV_VAR_MAPPING[key],
                    ENVVALUE=value
                )
            )

        print("\n".join(env_vars))
    elif cli_options.demo:
        for ec2_instance in session_generator().resource('ec2').instances.all():
            print(ec2_instance)

    else:
        print
        json.dumps(credentials._build_kwargs(), indent=4)


if __name__ == '__main__':
    main()
