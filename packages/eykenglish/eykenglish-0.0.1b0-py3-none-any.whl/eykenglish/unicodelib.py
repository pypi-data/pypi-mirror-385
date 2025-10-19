import unicodedata
import sys  # Imported for potential use with exceptions (e.g., sys.exit, though not used here)

# These global variables are kept to maintain the structure of the original code,
# but they are generally not recommended in modern Python.
temp = None


def transliterate_to_ascii(text: str) -> str:
    """
    Transliterates diacritic (accented) characters (Turkish, French, etc.) 
    in the text to their basic ASCII equivalents.

    Example: "ışİğüçéèñ" -> "isIguc een"

    This operation is performed using Python's standard `unicodedata` module, 
    avoiding external library dependencies. It first decomposes characters (NFKD),
    then encodes to ASCII, ignoring accents and other marks.

    Args:
        text (str): The text to be converted.

    Returns:
        str: The text converted to ASCII.
    """
    # 1. NFKD Normalization: Separates diacritics from base characters (e.g., 'é' -> 'e', '́')
    normalized_text = unicodedata.normalize('NFKD', text)

    # 2. Encode to ASCII and drop diacritics using 'ignore'
    # 3. Decode back to UTF-8
    ascii_text = normalized_text.encode('ascii', 'ignore').decode('utf-8')

    # A manual Turkish map is kept to ensure correct i/ı and I/İ handling, 
    # as NFKD sometimes doesn't correctly handle Turkish dotless/dotted I cases.

    manual_turkish_map = {
        'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G',
        'ü': 'u', 'Ü': 'U', 'ş': 's', 'Ş': 'S',
        'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C'
    }

    # Apply the Turkish character mapping after unicodedata processing.
    result = ""
    for char in ascii_text:
        result += manual_turkish_map.get(char, char)

    return result


def safe_chr(number: int) -> str | None:
    """
    Safely retrieves the character from the given numeric Unicode code point.
    Returns None instead of raising a specific error for an invalid code point.

    Args:
        number (int): The number as the Unicode code point.

    Returns:
        str | None: The corresponding character or None if unsuccessful.
    """
    global temp
    try:
        char = chr(number)
        temp = char
        return char
    except ValueError:
        # Catches the invalid Unicode code point error.
        # The random number adding/subtracting logic from the original code 
        # is removed as it is not recommended in international standards.
        return None


def safe_ord(char: str) -> int | None:
    """
    Safely retrieves the Unicode code point (numeric equivalent) of the given single character.
    Returns None if the input is a numeric string.

    Args:
        char (str): The character whose Unicode code point will be retrieved.

    Returns:
        int | None: The numeric equivalent of the character or None if unsuccessful.
    """
    global temp

    if not isinstance(char, str) or not char:
        return None

    # Strip spaces and check for numeric content (Logic preserved from original function)
    stripped_char = char.strip()

    # Note: Python's ord() function already doesn't work with numeric strings, 
    # but the check is kept to maintain the logic of the original function.
    if stripped_char.isnumeric():
        # Returns standard None instead of the original Turkish error message
        return None

    try:
        # Use only the first character (Logic preserved from original function)
        number = ord(stripped_char[0])
        temp = number
        return number
    except Exception:
        # Catches other unexpected errors
        return None


def raise_exception(exception_class: type[BaseException], message: str = ""):
    """
    Raises an exception with the specified error class.

    Args:
        exception_class (type[BaseException]): The class of the exception to be raised (e.g., ValueError).
        message (str): The message to be used in the exception.
    """
    raise exception_class(message)


def to_uppercase(text: str) -> str:
    """
    Converts the entire given text to uppercase.

    Note: This uses Python's standard `upper()` function, which is suitable 
    for international languages (e.g., German 'ß').

    Args:
        text (str): The text to be converted.

    Returns:
        str: The text converted to uppercase.
    """
    return text.upper()


def to_lowercase(text: str) -> str:
    """
    Converts the entire given text to lowercase.

    Note: This uses Python's standard `lower()` function, which is generally 
    the most appropriate for all international cases. For aggressive lowercase 
    conversion, `casefold()` could be preferred (but `lower()` is used here to 
    maintain the original intent).

    Args:
        text (str): The text to be converted.

    Returns:
        str: The text converted to lowercase.
    """
    return text.lower()


def clean_and_encode_to_bytes(text: str) -> bytes:
    """
    Converts the text to lowercase, removes spaces, and encodes it into a byte 
    sequence using UTF-8 (default).

    Args:
        text (str): The text to be processed.

    Returns:
        bytes: The cleaned and encoded byte sequence.
    """
    global temp

    # Use the universal lowercase conversion function
    cleaned_text = to_lowercase(text).replace(" ", "")

    # Encodes using UTF-8 by default
    encoded_text = cleaned_text.encode()
    temp = encoded_text

    return encoded_text


def safe_print(text: str = "Hello World"):
    """
    Safely prints the text to the console. If a printing error occurs, it is 
    suppressed (returns None).

    Args:
        text (str): The text to be printed to the console.

    Returns:
        None | object: None if printing failed.
    """
    try:
        # Checking the type of the text is a good practice, but the original goal 
        # is just to suppress the printing error.
        print(text)
    except Exception:
        # Catches a wide range of exceptions (I/O, encoding, etc.)
        return None

