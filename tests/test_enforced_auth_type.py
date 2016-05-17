from unittest import TestCase

from awsauthhelper import AWSArgumentParser


class TestEnforcedAuthType(TestCase):
    def test_auth_enforcement_keys(self):
        arg_parser = AWSArgumentParser(role_session_name='test', enforce_auth_type='keys')
        self.assertEqual(len(arg_parser._actions), 5)

        key_arg = filter(lambda action: '--aws-access-key-id' in action.option_strings, arg_parser._actions)
        self.assertGreater(len(key_arg), 0)
        secret_arg = filter(lambda action: '--aws-secret-access-key' in action.option_strings, arg_parser._actions)
        self.assertGreater(len(secret_arg), 0)

    def test_auth_enforcement_keys_with_session(self):
        arg_parser = AWSArgumentParser(role_session_name='test', enforce_auth_type='keys_with_session')
        self.assertEqual(len(arg_parser._actions), 6)

        key_arg = filter(lambda action: '--aws-access-key-id' in action.option_strings, arg_parser._actions)
        self.assertEqual(len(key_arg), 1)
        secret_arg = filter(lambda action: '--aws-secret-access-key' in action.option_strings, arg_parser._actions)
        self.assertEqual(len(secret_arg), 1)
        session_arg = filter(lambda action: '--aws-session-token' in action.option_strings, arg_parser._actions)
        self.assertEqual(len(session_arg), 1)

    def test_auth_enforcement_profile(self):
        arg_parser = AWSArgumentParser(role_session_name='test', enforce_auth_type='profile')
        self.assertEqual(len(arg_parser._actions), 4)

        key_arg = filter(lambda action: '--profile' in action.option_strings, arg_parser._actions)
        self.assertEqual(len(key_arg), 1)

    def test_auth_enforcement_profile_role(self):
        arg_parser = AWSArgumentParser(role_session_name='test', enforce_auth_type='profile_role')
        self.assertEqual(len(arg_parser._actions), 5)

        key_arg = filter(lambda action: '--profile' in action.option_strings, arg_parser._actions)
        self.assertEqual(len(key_arg), 1)

        role_key = filter(lambda action: '--role' in action.option_strings, arg_parser._actions)
        self.assertEqual(len(key_arg), 1)

    def test_auth_enforcement_config(self):
        arg_parser = AWSArgumentParser(role_session_name='test', enforce_auth_type='config')
        self.assertEqual(len(arg_parser._actions), 4)

        key_arg = filter(lambda action: '--config-path' in action.option_strings, arg_parser._actions)
        self.assertEqual(len(key_arg), 1)

    def test_auth_enforcement_credentials(self):
        arg_parser = AWSArgumentParser(role_session_name='test', enforce_auth_type='credentials')
        self.assertEqual(len(arg_parser._actions), 4)

        key_arg = filter(lambda action: '--credentials-path' in action.option_strings, arg_parser._actions)
        self.assertEqual(len(key_arg), 1)

    def test_auth_enforcement_none(self):
        self.assertEqual(
            len(AWSArgumentParser(role_session_name='test')._actions),
            10
        )
