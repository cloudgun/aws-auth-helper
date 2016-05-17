from unittest import TestCase

from awsauthhelper import Credentials


class TestCredentials(TestCase):
    def test_has_role(self):
        creds = Credentials(role='my_role')
        self.assertTrue(creds.has_role())

    def test_has_profile(self):
        creds = Credentials(profile='my_role')
        self.assertTrue(creds.has_profile())

    def test_has_keys(self):
        creds = Credentials(aws_secret_access_key='my_key', aws_access_key_id='my_key')
        self.assertTrue(creds.has_keys())

    def test_has_session_keys(self):
        creds = Credentials(aws_secret_access_key='my_key', aws_access_key_id='my_key', aws_session_token='my_session')
        self.assertTrue(creds.has_session_keys())

    def test_using_role(self):
        creds = Credentials(role='my_role', profile='my_profile')
        self.assertTrue(creds.using_role())

        creds = Credentials(role='my_role', aws_secret_access_key='my_key', aws_access_key_id='my_key')
        self.assertTrue(creds.using_role())

    def test__build_kwargs(self):
        creds = Credentials(aws_secret_access_key='my_key', aws_access_key_id='my_id')
        self.assertDictEqual(creds._build_kwargs(), {
            'aws_secret_access_key': 'my_key',
            'aws_access_key_id': 'my_id'
        })

        creds = Credentials(aws_secret_access_key='my_key', aws_access_key_id='my_id', aws_session_token='my_token')
        self.assertDictEqual(creds._build_kwargs(), {
            'aws_secret_access_key': 'my_key',
            'aws_access_key_id': 'my_id',
            'aws_session_token': 'my_token'
        })

    def test_freeze(self):
        creds = Credentials(
            region='test_region',
            aws_secret_access_key='test_key',
            aws_access_key_id='test_id'
        )

        self.assertEqual(creds.region, 'test_region')
        self.assertEqual(creds.aws_secret_access_key, 'test_key')
        self.assertEqual(creds.aws_access_key_id, 'test_id')

        self.assertDictEqual(creds._freeze, {})

        creds.freeze()
        creds.profile = 'my_test_profile'
        creds.role = 'my_test_role'

        self.assertEqual(creds.profile, 'my_test_profile')
        self.assertEqual(creds.role, 'my_test_role')

        self.assertEqual(creds._freeze['region'], 'test_region')
        self.assertEqual(creds._freeze['aws_secret_access_key'], 'test_key')
        self.assertEqual(creds._freeze['aws_access_key_id'], 'test_id')

        creds.reset()

        self.assertEqual(creds.region, 'test_region')
        self.assertEqual(creds.aws_secret_access_key, 'test_key')
        self.assertEqual(creds.aws_access_key_id, 'test_id')
