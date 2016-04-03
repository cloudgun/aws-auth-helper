import argparse
from unittest import TestCase

from awsauthhelper import validate_creds


class TestValidate_creds(TestCase):
    def test_validate_creds_keys_success(self):
        # Check keys
        self.assertTrue(validate_creds(
            aws_access_key_id='mine',
            aws_secret_access_key='mine'
        ))

    def test_validate_temp_creds_keys_success(self):
        # Check temporal keys
        self.assertTrue(validate_creds(
            aws_access_key_id='mine',
            aws_secret_access_key='mine',
            aws_session_token='mine'
        ))

    def test_validate_creds_profile_success(self):
        # Check profile
        self.assertTrue(validate_creds(
            profile='mine'
        ))

    def test_validate_creds_fails(self):
        # Check keys
        with self.assertRaises(argparse.ArgumentError):
            self.assertTrue(validate_creds(
                aws_session_token='mine',
                aws_secret_access_key='mine'
            ))

        with self.assertRaises(argparse.ArgumentError):
            self.assertTrue(validate_creds(
                aws_session_token='mine',
                aws_access_key_id='mine'
            ))

        with self.assertRaises(argparse.ArgumentError):
            self.assertTrue(validate_creds(
                aws_session_token='mine'
            ))

        # Check profile
        with self.assertRaises(argparse.ArgumentError):
            self.assertTrue(validate_creds(
                profile='mine',
                aws_secret_access_key='mine'
            ))

        with self.assertRaises(argparse.ArgumentError):
            self.assertTrue(validate_creds(
                aws_access_key_id='mine',
                profile='mine'
            ))

        # Check keys
        with self.assertRaises(argparse.ArgumentError):
            self.assertTrue(validate_creds(
                aws_access_key_id='mine',
            ))

        with self.assertRaises(argparse.ArgumentError):
            self.assertTrue(validate_creds(
                aws_secret_access_key='mine'
            ))
