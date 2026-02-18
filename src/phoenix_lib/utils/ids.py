"""ID utility functions."""

import secrets
import string


def short_id(length: int = 8) -> str:
    """Generate a short random ID.

    Args:
        length: The length of the ID to generate. Defaults to 8.

    Returns:
        A random string containing lowercase letters and digits.
    """
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))
