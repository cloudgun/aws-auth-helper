from unittest import TestCase

from awsauthhelper import Credentials


class TestCredentials(TestCase):
    def test_has_role(self):
        credentials = Credentials(role='my_role')
        self.assertTrue(credentials.has_role())

    def test_has_profile(self):
        credentials = Credentials(profile='my_role')
        self.assertTrue(credentials.has_profile())

    def test_has_keys(self):
        credentials = Credentials(aws_secret_access_key='my_key', aws_access_key_id='my_key')
        self.assertTrue(credentials.has_keys())

    def test_has_session_keys(self):
        credentials = Credentials(aws_secret_access_key='my_key', aws_access_key_id='my_key',
                                  aws_session_token='my_session')
        self.assertTrue(credentials.has_session_keys())

    def test_using_role(self):
        credentials = Credentials(role='my_role', profile='my_profile')
        self.assertTrue(credentials.using_role())

        credentials = Credentials(role='my_role', aws_secret_access_key='my_key', aws_access_key_id='my_key')
        self.assertTrue(credentials.using_role())

    def test__build_kwargs(self):
        credentials = Credentials(aws_secret_access_key='my_key', aws_access_key_id='my_id')
        self.assertDictEqual(credentials._build_kwargs(), {
            'aws_secret_access_key': 'my_key',
            'aws_access_key_id': 'my_id'
        })

        credentials = Credentials(aws_secret_access_key='my_key', aws_access_key_id='my_id',
                                  aws_session_token='my_token')
        self.assertDictEqual(credentials._build_kwargs(), {
            'aws_secret_access_key': 'my_key',
            'aws_access_key_id': 'my_id',
            'aws_session_token': 'my_token'
        })

        credentials = Credentials(profile='my_profile')
        self.assertDictEqual(credentials._build_kwargs(), {
            'profile_name': 'my_profile'
        })

        credentials = Credentials(region='my_region')
        self.assertDictEqual(credentials._build_kwargs(), {
            'region_name': 'my_region'
        })

        credentials = Credentials(region='my_region', aws_secret_access_key='my_key', aws_access_key_id='my_id')
        self.assertDictEqual(credentials._build_kwargs(), {
            'region_name': 'my_region',
            'aws_secret_access_key': 'my_key',
            'aws_access_key_id': 'my_id'
        })

    def test_freeze(self):
        credentials = Credentials(
            region='test_region',
            aws_secret_access_key='test_key',
            aws_access_key_id='test_id'
        )

        self.assertEqual(credentials.region, 'test_region')
        self.assertEqual(credentials.aws_secret_access_key, 'test_key')
        self.assertEqual(credentials.aws_access_key_id, 'test_id')

        self.assertDictEqual(credentials._freeze, {})

        credentials.freeze()
        credentials.profile = 'my_test_profile'
        credentials.role = 'my_test_role'

        self.assertEqual(credentials.profile, 'my_test_profile')
        self.assertEqual(credentials.role, 'my_test_role')

        self.assertEqual(credentials._freeze['region'], 'test_region')
        self.assertEqual(credentials._freeze['aws_secret_access_key'], 'test_key')
        self.assertEqual(credentials._freeze['aws_access_key_id'], 'test_id')

        credentials.reset()

        self.assertEqual(credentials.region, 'test_region')
        self.assertEqual(credentials.aws_secret_access_key, 'test_key')
        self.assertEqual(credentials.aws_access_key_id, 'test_id')

    def test_has_mfa(self):
        credentials = Credentials()

        self.assertFalse(credentials.has_mfa())

        credentials.mfa_serial = "mock_serial"
        self.assertTrue(credentials.has_mfa())

    def test__switch_auth_scope(self):
        credentials = Credentials()
        credentials._switch_auth_scope({
            'Credentials': {
                'AccessKeyId': 'mock_key_id',
                'SecretAccessKey': 'mock_secret_key',
                'SessionToken': 'mock_session_token'
            }
        })

        self.assertEqual(credentials.aws_access_key_id, 'mock_key_id')
        self.assertEqual(credentials.aws_secret_access_key, 'mock_secret_key')
        self.assertEqual(credentials.aws_session_token, 'mock_session_token')
