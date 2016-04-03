from unittest import TestCase

from tests import AuthHelperTestCase


class TestTestHelper(TestCase):
    """
    Test our helper functions
    """

    def test_assertAnyIn_fails(self):
        """
        Make sure assertInAny fails correctly

        :return: 
        """
        test_case = AuthHelperTestCase('assertAnyIn')
        with self.assertRaises(AssertionError):
            test_case.assertAnyIn(['1', '2', '3'], ['a', 'b', 'c', 'd'])

    def test_assertAnyIn_suceeds(self):
        """
        Make sure assertInAny succeeds
        
        :return: 
        """
        test_case = AuthHelperTestCase('assertAnyIn')
        self.assertIsNone(test_case.assertAnyIn(['1', '2', '3'], ['1', 'b', 'c', 'd']))
