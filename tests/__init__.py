from unittest import TestCase


class AuthHelperTestCase(TestCase):
    """
    Implement some custom tests functions
    """

    def assertAnyIn(self, needles, haystack):
        if not any(x in haystack for x in needles):
            raise AssertionError('None of \'{needles}\' in \'{haystack}\''.format(
                    needles=",".join(needles),
                    haystack=haystack
            ))
