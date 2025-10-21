# Django
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Memberaudit Doctrine Checker
from madc import __title__, models

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def get_manage_permission(request, character_id):
    """Check if the user has permission to manage."""
    perms = True
    main_char = EveCharacter.objects.select_related(
        "character_ownership",
        "character_ownership__user__profile",
        "character_ownership__user__profile__main_character",
    ).get(character_id=character_id)
    try:
        main_char = main_char.character_ownership.user.profile.main_character
    except ObjectDoesNotExist:
        pass

    # check access
    visible = models.SkillList.objects.manage_to(request.user)
    if main_char not in visible:
        account_chars = (
            request.user.profile.main_character.character_ownership.user.character_ownerships.all()
        )
        if main_char in account_chars:
            pass
        else:
            perms = False
    return perms, main_char


def get_main_character(request, character_id):
    perms = True
    main_char = EveCharacter.objects.select_related(
        "character_ownership",
        "character_ownership__user__profile",
        "character_ownership__user__profile__main_character",
    ).get(character_id=character_id)
    try:
        main_char = main_char.character_ownership.user.profile.main_character
    except ObjectDoesNotExist:
        pass

    # check access
    visible = models.SkillList.objects.visible_eve_characters(request.user)
    if main_char not in visible:
        account_chars = (
            request.user.profile.main_character.character_ownership.user.character_ownerships.all()
        )
        if main_char in account_chars:
            pass
        else:
            perms = False
    return perms, main_char


def get_corporation(request, corporation_id) -> tuple[bool, EveCorporationInfo | None]:
    perms = True
    try:
        corporation = EveCorporationInfo.objects.get(corporation_id=corporation_id)
    except ObjectDoesNotExist:
        return False, None

    # check access
    visible = models.SkillList.objects.visible_eve_corporations(request.user)
    if corporation not in visible:
        perms = False
    return perms, corporation


def get_alts_queryset(main_char):
    try:
        linked_characters = (
            main_char.character_ownership.user.character_ownerships.all().values_list(
                "character_id", flat=True
            )
        )

        return EveCharacter.objects.filter(id__in=linked_characters)
    except ObjectDoesNotExist:
        return EveCharacter.objects.filter(pk=main_char.pk)


def generate_button(pk: int, template, queryset, settings, request) -> mark_safe:
    """Generate a html button with the given template and queryset."""
    return format_html(
        render_to_string(
            template,
            {
                "pk": pk,
                "queryset": queryset,
                "settings": settings,
            },
            request=request,
        )
    )


def _collect_user_doctrines(skills_list: dict, active_skilllists) -> dict:
    """Collect all doctrines for a user across all their characters."""
    user_doctrines = {}

    # Process each character's skill data
    for __, character_data in skills_list.items():
        if "doctrines" not in character_data:
            continue

        for doctrine_key, doctrine_data in character_data["doctrines"].items():
            # Filter out inactive skill lists
            if doctrine_key not in active_skilllists:
                continue

            if doctrine_key not in user_doctrines:
                user_doctrines[doctrine_key] = doctrine_data
            else:
                # Take the best result (fewer missing skills) across all chars
                # Empty skills dict means all skills are trained
                current_missing_count = len(doctrine_data.get("skills", {}))
                existing_missing_count = len(
                    user_doctrines[doctrine_key].get("skills", {})
                )

                # Prefer the character with fewer missing skills (0 is best)
                if current_missing_count < existing_missing_count:
                    user_doctrines[doctrine_key] = doctrine_data

    return user_doctrines
