from argparse import Namespace
from awsauthhelper.password import generate
from tests import AuthHelperTestCase

__author__ = 'drews'


class TestPassword(AuthHelperTestCase):
    """
    Make sure that our password generation has enough entropy.
    """
    SYMBOLS = list("!@#$%^&*()_+-=[]{}|'")
    LOWERCASE = list("abcdefghijklmnopqrstuvwxyz")
    UPPERCASE = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    NUMBERS = list("0123456789")

    class MockPasswordPolicy(Namespace):
        def __init__(self, **kwargs):
            kwargs.setdefault('minimum_password_length', 6)
            kwargs.setdefault('require_symbols', False)
            kwargs.setdefault('require_lowercase_characters', False)
            kwargs.setdefault('require_uppercase_characters', False)
            kwargs.setdefault('require_numbers', False)

            super(TestPassword.MockPasswordPolicy, self).__init__(**kwargs)

    def test_generate_length(self):
        # Test default
        new_password = generate(self.MockPasswordPolicy())
        self.assertGreaterEqual(len(new_password), 6)
        self.assertIsInstance(new_password, basestring)

        # Test override
        new_password = generate(self.MockPasswordPolicy(
                minimum_password_length=10
        ))
        self.assertGreaterEqual(len(new_password), 10)
        self.assertIsInstance(new_password, basestring)

    def test_generate_symbols(self):
        new_password = generate(self.MockPasswordPolicy(
                require_symbols=True
        ))
        self.assertAnyIn(self.SYMBOLS, new_password)
        self.assertIsInstance(new_password, basestring)

    def test_generate_lowercase(self):
        new_password = generate(self.MockPasswordPolicy(
                require_lowercase_characters=True
        ))
        self.assertAnyIn(self.LOWERCASE, new_password)
        self.assertIsInstance(new_password, basestring)

    def test_generate_uppercase(self):
        new_password = generate(self.MockPasswordPolicy(
                require_uppercase_characters=True
        ))
        self.assertAnyIn(self.UPPERCASE, new_password)
        self.assertIsInstance(new_password, basestring)

    def test_generate_numbers(self):
        new_password = generate(self.MockPasswordPolicy(
                require_numbers=True
        ))
        self.assertAnyIn(self.NUMBERS, new_password)
        self.assertIsInstance(new_password, basestring)

    def test_generate_secure(self):
        new_password = generate(self.MockPasswordPolicy(
                minimum_password_length=12,
                require_symbols=True,
                require_lowercase_characters=True,
                require_uppercase_characters=True,
                require_numbers=True
        ))
        self.assertGreaterEqual(len(new_password), 12)
        self.assertAnyIn(self.SYMBOLS, new_password)
        self.assertAnyIn(self.LOWERCASE, new_password)
        self.assertAnyIn(self.UPPERCASE, new_password)
        self.assertAnyIn(self.NUMBERS, new_password)
        self.assertIsInstance(new_password, basestring)
