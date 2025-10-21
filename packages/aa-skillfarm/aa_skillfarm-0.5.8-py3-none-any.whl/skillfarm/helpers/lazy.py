"""This module provides lazy loading of some common functions and objects that are not needed for every request."""

# Django
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.eveonline.evelinks.eveimageserver import (
    character_portrait_url,
    type_render_url,
)


def get_character_portrait_url(
    character_id: int, size: int = 32, character_name: str = None, as_html: bool = False
) -> str:
    """Get the character portrait for a character ID."""

    render_url = character_portrait_url(character_id=character_id, size=size)

    if as_html:
        render_html = format_html(
            '<img class="character-portrait rounded-circle" src="{}" alt="{}">',
            render_url,
            character_name,
        )
        return render_html
    return render_url


def get_type_render_url(
    type_id: int, size: int = 32, type_name: str = None, as_html: bool = False
) -> str:
    """Get the type render for a type ID."""

    render_url = type_render_url(type_id=type_id, size=size)

    if as_html:
        render_html = format_html(
            '<img class="type-render rounded-circle" src="{}" alt="{}">',
            render_url,
            type_name,
        )
        return render_html
    return render_url


def str_normalize_time(evetime, hours: bool = False) -> str:
    """Normalize eve time to a string."""
    if hours:
        return timezone.localtime(evetime).strftime("%Y-%m-%d %H:%M")
    return timezone.localtime(evetime).strftime("%Y-%m-%d")


def get_status_icon(boolean: bool, size: int = 32) -> str:
    """Get the status icon for a status."""
    html = "<button class='btn bg-gradient rounded-circle "
    if boolean:
        html += "btn-success' "
        title = _("Active")
    else:
        html += "btn-danger' "
        title = _("Inactive")
    html += f"style='height: {size}px; width: {size}px;' "
    html += "data-tooltip-toggle='skillfarm-tooltip' "
    html += f" title='{title}'></button>"
    return format_html(html)
