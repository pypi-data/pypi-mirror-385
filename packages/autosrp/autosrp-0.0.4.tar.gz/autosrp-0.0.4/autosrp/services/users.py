"""
Some helper functions, so we don't mess up other files too much
"""

# Django
from django.contrib.auth.models import User

# Alliance Auth
from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter

def get_deleted_user():
    return User.objects.get_or_create(username="deleted")[0]


def get_main_for_character(character: EveCharacter) -> EveCharacter | None:
    """
    Get the main character for a given eve character

    :param character:
    :type character:
    :return:
    :rtype:
    """

    try:
        return character.character_ownership.user.profile.main_character
    except (
        AttributeError,
        EveCharacter.character_ownership.RelatedObjectDoesNotExist,
        CharacterOwnership.user.RelatedObjectDoesNotExist,
    ):
        return None


def get_user_for_character(character: EveCharacter) -> User:
    """
    Get the user for a character

    :param character:
    :type character:
    :return:
    :rtype:
    """

    try:
        return character.character_ownership.user.profile.user
    except (
        AttributeError,
        EveCharacter.character_ownership.RelatedObjectDoesNotExist,
        CharacterOwnership.user.RelatedObjectDoesNotExist,
    ):
        return get_deleted_user()
