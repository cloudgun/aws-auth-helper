from unittest import TestCase

from awsauthhelper import EnvDefault


class TestEnvDefault(TestCase):
    def test_suceeds(self):
        env_object = EnvDefault()
