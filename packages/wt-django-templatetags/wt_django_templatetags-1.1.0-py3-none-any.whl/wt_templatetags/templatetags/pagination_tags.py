from typing import Union

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def relative_url(
        value: Union[int, str],
        field_name: str = 'page',
        urlencode: str = None
) -> str:
    """
    Create a relative URL for a particular 'page' number.

    Args:
        value: The position within the paginated QuerySet. Often an integer but
            can also be the string 'last.'
        field_name: The name of the parameter containing the position value.
            Most often 'page' but can be overridden. Defaults to 'page.'
        urlencode: Encoded GET parameters (if any). Will contain the position
            parameter if present in the query string. Defaults to None.

    Returns:
        A relative URL beginning with ?<field_name>=<value>. Any other
            parameters will be appended.
    """
    url = '?{}={}'.format(field_name, value)

    if urlencode:
        # Only include parameters that don't match field_name.
        qs = urlencode.split('&')
        filtered_qs = filter(lambda p: p.split('=')[0] != field_name, qs)
        encoded_qs = '&'.join(filtered_qs)

        if encoded_qs:
            url = '{}&{}'.format(url, encoded_qs)

    return mark_safe(url)
