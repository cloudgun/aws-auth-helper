import boto3
import typing
import argparse
import awsauthhelper


class AWSArgumentParser(argparse.ArgumentParser):
    def __init__(
            self,
            role_session_name: str,
            region: str = None,
            profile: str = None,
            enforce_auth_type: str = None,
            **kwargs: typing.Dict[str, typing.Union[str, int, bool]]
    ) -> None: ...


class Credentials(object):
    freeze_properties = ...  # type: typing.List[str]
    default = ...  # type: Credentials

    def __init__(
            self,
            region=None,
            aws_secret_access_key=None,
            aws_access_key_id=None,
            aws_session_token=None,
            profile=None,
            role=None,
            role_session_name=None,
            config_path=None,
            credentials_path=None,
            auth_debug=False,
            **kwargs: typing.Dict[str, typing.Union[str, int, bool]]
    ) -> None: 
        self.role = None
        self.role_session_name = None
        self._freeze = None
        self.auth_debug = None
        self.region = None
        self.profile = None
        self.logger = None
        self.aws_session_token = None
        self.aws_secret_access_key = None
        self.aws_access_key_id = None
        ...

    def assume_role(self) -> awsauthhelper.Credentials: ...

    def freeze(self) -> awsauthhelper.Credentials: ...

    def reset(self) -> awsauthhelper.Credentials: ...

    def create_session(self, internal=False) -> typing.Callable[[str], boto3.Session]: ...

    def _assume_role(self) -> awsauthhelper.Credentials: ...

    def _switch_auth_scope(self, credentials) -> awsauthhelper.Credentials: ...

    def has_keys(self) -> bool: ...

    def has_session_keys(self) -> bool: ...

    def has_profile(self) -> bool: ...

    def has_role(self) -> bool: ...

    def using_role(self) -> bool: ...


def validate_creds(
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_session_token: str,
        profile: str,
        **kwargs: typing.Dict[str, typing.Union[str, int, bool]]
) -> bool: ...
