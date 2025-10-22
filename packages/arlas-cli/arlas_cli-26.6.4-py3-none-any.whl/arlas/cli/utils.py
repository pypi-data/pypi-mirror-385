import re
import unicodedata


def clean_str(str_value: str) -> str:
    """Normalize a string: remove accents, replace non-alphanumeric characters with underscores,
    convert to lowercase, and trim leading/trailing underscores.

    Args:
        str_value (str): Input string to normalize. Can contain accents, spaces, or special characters.

    Returns:
        str: Normalized string in lowercase, without accents, and with underscores replacing
             non-alphanumeric characters. Leading/trailing underscores are removed.
    """
    # Normalize unicode (é -> e)
    clean_str_value = unicodedata.normalize('NFKD', str(str_value)).encode('ascii', 'ignore').decode('utf-8')
    # Convert to lowercase
    clean_str_value = clean_str_value.lower()
    # Replace non-alphanumeric characters with underscores
    clean_str_value = re.sub(r'[^0-9a-z]+', '_', clean_str_value)
    # Collapse multiple underscores into one
    clean_str_value = re.sub(r'_+', '_', clean_str_value)
    # Trim leading/trailing underscores
    clean_str_value = clean_str_value.strip('_')
    return clean_str_value


def is_float(string: str) -> bool:
    """
    Check if a string can be converted to a float.

    Args:
        string (str): The string to check.

    Returns:
        bool: True if the string is a valid float, False otherwise.
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def is_int(string: str) -> bool:
    """
    Check if a string can be converted to an int.

    Args:
        string (str): The string to check.

    Returns:
        bool: True if the string is a valid int, False otherwise.
    """
    try:
        int(string)
        return True
    except ValueError:
        return False


def is_valid_uuid(uuid: str) -> bool:
    """
    Check if a string is a valid UUID.

    Args:
        uuid (str): The string to check.

    Returns:
        bool: True if the string is a valid UUID, False otherwise.
    """
    # Regular expression for a generic UUID
    uuid_regex = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_regex.match(uuid))
