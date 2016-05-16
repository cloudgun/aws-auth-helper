from random import randrange, choice, shuffle, random, sample
from math import floor, ceil

__author__ = 'drews'

SYMBOLS = "!@#$%^&*()_+-=[]{}|'"
LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NUMBERS = "0123456789"


def generate(password_policy):
    """
    Builds a password based on the password policy provided
    ``password_policy`` should be an object with the attributes:

      - **minimum_password_length** *(int)* -- Minimum length of password. Maximum length of password will be the \
        ceiling of 1.3 times this value.
      - **require_symbols** *(bool)* -- Make sure password contains ``!@#$%^&*()_+-=[]{}|'``.
      - **require_lowercase_characters** *(bool)* -- Make sure password contains ``abcdefghijklmnopqrstuvwxyz``.
      - **require_uppercase_characters** *(bool)* -- Make sure password contains ``ABCDEFGHIJKLMNOPQRSTUVWXYZ``.
      - **require_numbers** *(bool)* -- Make sure password contains ``0123456789``.

    :param iam.AccountPasswordPolicy password_policy: boto password policy
    :return basestring: New password
    """

    # Generate a password between: the specified min length; and 130% of the min length with a minimum
    # of 2 chars added.
    minimum_password_length = password_policy.minimum_password_length
    password_length = randrange(
        minimum_password_length,
        max(int(minimum_password_length * 1.3), minimum_password_length + 2)
    )

    # Extract the policy requirements
    policy_requirements = {
        'require_symbols': password_policy.require_symbols,
        'require_lowercase_characters': password_policy.require_lowercase_characters,
        'require_uppercase_characters': password_policy.require_uppercase_characters,
        'require_numbers': password_policy.require_numbers
    }

    # If the requirement was False, it means it does not *need* to be enforced but, that it *could* be enforced.
    for policy_key, setting in policy_requirements.items():
        if not policy_requirements[policy_key]:
            policy_requirements[policy_key] = choice([True, False])

    # If we have no policy requirements, make sure to set at least 2 policy requirements, with a maximum of all
    if sum(policy_requirements.values()) < 2:
        num_policies_to_set = randrange(2, len(policy_requirements) + 1)
        policies_to_set = sample(policy_requirements.keys(), num_policies_to_set)
        for policy_to_set in policies_to_set:
            policy_requirements[policy_to_set] = True

    # Number of policies to enforce
    number_of_char_groups = sum(policy_requirements.values())

    # Create a list of policies to enforce, and specify how many characters in the password will be composed of each
    # policy.
    char_num_groups = []
    for i in range(1, number_of_char_groups):
        char_num_groups.append(int(ceil(random() * (2 * float(password_length)) / float(number_of_char_groups))))
    char_num_groups.append(password_length - sum(char_num_groups))

    # There will be times where the above algorithm, will create a negative value as the last entry.
    # For these cases, we remove the negative and split the largest value in the array.
    if len([n for n in char_num_groups if n > 0]) != len(char_num_groups):
        # Filter the negative value
        char_num_groups = [n for n in char_num_groups if n > 0]
        # Get the biggest value
        biggest_group_num = max(char_num_groups)
        char_num_groups.remove(biggest_group_num)
        # Split it and re-append to list
        new_group1 = int(biggest_group_num / 2)
        new_group2 = biggest_group_num - new_group1
        char_num_groups.append(new_group1)
        char_num_groups.append(new_group2)

    def choose_n_chars(number_of_chars, chars):
        """
        Choose n characters at random from char, and return them
        :param int number_of_chars: number of characters to return
        :param str char: pool of characters to choose from
        :return:
        """
        # Choose a character from chars number_of_chars times.
        return [choice(chars) for _ in range(number_of_chars)]

    password_composition = []
    shuffle(char_num_groups)
    if policy_requirements['require_symbols']:
        password_composition.extend(choose_n_chars(char_num_groups.pop(0), SYMBOLS))
    if policy_requirements['require_lowercase_characters']:
        password_composition.extend(choose_n_chars(char_num_groups.pop(0), LOWERCASE))
    if policy_requirements['require_uppercase_characters']:
        password_composition.extend(choose_n_chars(char_num_groups.pop(0), UPPERCASE))
    if policy_requirements['require_numbers']:
        password_composition.extend(choose_n_chars(char_num_groups.pop(0), NUMBERS))

    # Make sure our character types are mixed.
    shuffle(password_composition)
    return ''.join(password_composition)
