from unittest import TestCase


class AuthHelperTestCase(TestCase):
    """
    Implement some custom tests functions
    """

    def assertAnyIn(self, needles, haystack):
        """
        Asserts wether any of needles exists in haystack
        :param list needles: Collection what we are searching for
        :param list haystack: Source of truth
        :return:
        """
        if not any(x in haystack for x in needles):
            raise AssertionError('None of \'{needles}\' in \'{haystack}\''.format(
                    needles=",".join(needles),
                    haystack=haystack
            ))
