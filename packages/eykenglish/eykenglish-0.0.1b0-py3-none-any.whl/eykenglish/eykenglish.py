# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import datetime
import random
import socket
import string
import re
import math
import shutil
from collections import Counter
from typing import List, Dict, Any, Union, Tuple, Callable


class Logger:
    """
    A simple static class for logging messages with timestamps.
    """

    @staticmethod
    def _get_timestamp() -> str:
        """Returns the current formatted timestamp."""
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def info(message: str) -> None:
        """Prints an informational message."""
        print(f"[INFO] {Logger._get_timestamp()} - {message}")

    @staticmethod
    def warning(message: str) -> None:
        """Prints a warning message."""
        print(f"[WARNING] {Logger._get_timestamp()} - {message}")

    @staticmethod
    def error(message: str) -> None:
        """Prints an error message."""
        print(f"[ERROR] {Logger._get_timestamp()} - {message}")


# ==============================================================================
# Text Processing and String Utilities
# ==============================================================================
# This section handles general text conversion and analysis operations.
# Note: Turkish-specific character handling and translation functions are removed
# to adhere to an English-only utility focus.

def to_upper(text: str) -> str:
    """
    Converts the entire given text to standard uppercase using locale-independent rules.

    Args:
        text (str): The text to be converted.

    Returns:
        str: The text converted to uppercase.
    """
    # Simplified to standard Python upper()
    return text.upper()


def to_lower(text: str) -> str:
    """
    Converts the entire given text to standard lowercase using locale-independent rules.

    Args:
        text (str): The text to be converted.

    Returns:
        str: The text converted to lowercase.
    """
    # Simplified to standard Python lower()
    return text.lower()


def get_word_frequency(text: str) -> Dict[str, int]:
    """
    Counts the frequency of each word in the given text.
    Punctuation and case sensitivity are ignored.

    Args:
        text (str): The text to be analyzed.

    Returns:
        Dict[str, int]: A dictionary containing the frequency of each word.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    return dict(Counter(words))


def remove_punctuation(text: str) -> str:
    """
    Removes all punctuation marks from the given text.

    Args:
        text (str): The text to be processed.

    Returns:
        str: The text with punctuation removed.
    """
    return text.translate(str.maketrans('', '', string.punctuation))


def wrap_text_to_lines(text: str, line_length: int = 80) -> List[str]:
    """
    Splits a text into parts based on the specified line length, breaking at spaces if possible.

    Args:
        text (str): The text to be split.
        line_length (int): The maximum length of each line.

    Returns:
        List[str]: A list of the split lines.
    """
    lines = []
    while text:
        if len(text) <= line_length:
            lines.append(text)
            break

        # Find the last space before the line_length limit
        split_point = text.rfind(' ', 0, line_length)
        if split_point == -1:
            # No space found, hard break at line_length
            split_point = line_length

        lines.append(text[:split_point].strip())
        text = text[split_point:].strip()
    return lines


def extract_numbers(text: str) -> List[Union[int, float]]:
    """
    Returns all numbers (integers or floats) in the text as a list.

    Args:
        text (str): The text to search for numbers.

    Returns:
        List[Union[int, float]]: A list of the found numbers.
    """
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
    return [float(s) if '.' in s else int(s) for s in numbers]


def tokenize_text(text: str) -> List[str]:
    """
    Tokenizes a text into words and punctuation marks.

    Args:
        text (str): The text to be tokenized.

    Returns:
        List[str]: A list of tokens.
    """
    return re.findall(r'\b\w+\b|\S', text)


# ==============================================================================
# File System and Data Handling
# ==============================================================================

def read_file(filepath: str) -> str:
    """
    Reads the text content of the specified file path and returns it.
    Returns an empty string if the file is not found or a read error occurs.

    Args:
        filepath (str): The path to the file to be read.

    Returns:
        str: The content of the file.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        Logger.error(f"File not found: {filepath}")
    except Exception as e:
        Logger.error(f"File reading error: {e}")
    return ""


def write_file(filepath: str, content: str) -> bool:
    """
    Writes the given content to the specified file path.

    Args:
        filepath (str): The path to the file to be written.
        content (str): The text content to write to the file.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        Logger.info(f"Content successfully written to '{filepath}'.")
        return True
    except Exception as e:
        Logger.error(f"File writing error: {e}")
    return False


def read_json_file(filepath: str) -> Any:
    """
    Reads the specified JSON file and converts it to a Python object.

    Args:
        filepath (str): The path to the JSON file to be read.

    Returns:
        Any: The JSON content or None in case of an error.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        Logger.error(f"JSON file not found: {filepath}")
    except json.JSONDecodeError:
        Logger.error(f"JSON file format is corrupted: {filepath}")
    except Exception as e:
        Logger.error(f"JSON reading error: {e}")
    return None


def write_json_file(filepath: str, data: Any) -> bool:
    """
    Writes a Python object to the specified JSON file.

    Args:
        filepath (str): The path to the JSON file to be written.
        data (Any): The Python object to write to the file.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        Logger.info(f"Data successfully written to '{filepath}'.")
        return True
    except Exception as e:
        Logger.error(f"JSON writing error: {e}")
    return False


def file_exists(filepath: str) -> bool:
    """
    Checks if the specified file path exists and is a file.

    Args:
        filepath (str): The path of the file to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.exists(filepath) and os.path.isfile(filepath)


def create_directory(directory_path: str) -> bool:
    """
    Creates the specified directory path if it does not already exist.

    Args:
        directory_path (str): The path of the directory to be created.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        Logger.info(f"Directory successfully created or already existed: {directory_path}")
        return True
    except Exception as e:
        Logger.error(f"Directory creation error: {e}")
    return False


def list_directory_contents(directory_path: str) -> List[str]:
    """
    Lists all files and directories in the specified directory.

    Args:
        directory_path (str): The path of the directory to be listed.

    Returns:
        List[str]: A list of the contents. Empty list in case of an error.
    """
    try:
        return os.listdir(directory_path)
    except FileNotFoundError:
        Logger.error(f"Directory not found: {directory_path}")
    except Exception as e:
        Logger.error(f"Directory listing error: {e}")
    return []


def get_file_extension(filename: str) -> str:
    """
    Returns the extension of a file name.

    Args:
        filename (str): The file name whose extension will be retrieved.

    Returns:
        str: The file extension (without the dot).
    """
    return os.path.splitext(filename)[1].lstrip('.')


# ==============================================================================
# Mathematical and Data Manipulation
# ==============================================================================

def fibonacci_series(n: int) -> List[int]:
    """
    Returns a list containing the first n Fibonacci numbers.

    Args:
        n (int): The number of Fibonacci numbers to generate.

    Returns:
        List[int]: The Fibonacci series.
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]

    series = [0, 1]
    while len(series) < n:
        series.append(series[-1] + series[-2])
    return series


def is_prime(number: int) -> bool:
    """
    Checks if a number is prime.

    Args:
        number (int): The number to be checked.

    Returns:
        bool: True if the number is prime, False otherwise.
    """
    if number < 2:
        return False
    if number == 2:
        return True
    if number % 2 == 0:
        return False

    for i in range(3, int(math.sqrt(number)) + 1, 2):
        if number % i == 0:
            return False
    return True


def factorial(n: int) -> int:
    """
    Calculates the factorial of a number.

    Args:
        n (int): The number whose factorial is to be calculated.

    Returns:
        int: The factorial of the number. Returns 1 for negative numbers (crash-proof approach).
    """
    if n < 0:
        return 1
    if n == 0:
        return 1

    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


def reverse_list(input_list: List[Any]) -> List[Any]:
    """
    Reverses a list.

    Args:
        input_list (List[Any]): The list to be reversed.

    Returns:
        List[Any]: The reversed list.
    """
    return input_list[::-1]


def remove_duplicates(input_list: List[Any]) -> List[Any]:
    """
    Removes duplicate elements from a list while preserving the original order.

    Args:
        input_list (List[Any]): The list to be processed.

    Returns:
        List[Any]: The list with duplicate elements removed.
    """
    seen = set()
    new_list = []
    for element in input_list:
        if element not in seen:
            new_list.append(element)
            seen.add(element)
    return new_list


# ==============================================================================
# Networking and Connection Utilities
# ==============================================================================

def check_internet_connection(host: str = "8.8.8.8", port: int = 53, timeout: int = 3) -> bool:
    """
    Checks for internet connectivity by attempting to connect to a DNS server (default: Google DNS).

    Args:
        host (str): The server address to check (default: Google DNS).
        port (int): The port of the server (default: 53 for DNS).
        timeout (int): Connection timeout (seconds).

    Returns:
        bool: True if a connection is available, False otherwise.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        Logger.info("Internet connection is available.")
        return True
    except socket.error as ex:
        Logger.error(f"No internet connection: {ex}")
    return False


def establish_tcp_connection(host: str, port: int) -> Union[socket.socket, None]:
    """
    Establishes a TCP connection to the specified host and port.

    Args:
        host (str): The IP address or domain name of the host.
        port (int): The port number to connect to.

    Returns:
        Union[socket.socket, None]: The socket object if successful, otherwise None.
    """
    try:
        sock = socket.create_connection((host, port), timeout=5)
        Logger.info(f"Connection to {host}:{port} successful.")
        return sock
    except socket.error as ex:
        Logger.error(f"Failed to connect to {host}:{port}: {ex}")
    return None


def send_data(sock: socket.socket, data: str) -> bool:
    """
    Sends data over a socket.

    Args:
        sock (socket.socket): The socket object to send data through.
        data (str): The text data to be sent.

    Returns:
        bool: True if sending was successful, False otherwise.
    """
    try:
        sock.sendall(data.encode('utf-8'))
        return True
    except socket.error as ex:
        Logger.error(f"Data sending error: {ex}")
    return False


def receive_data(sock: socket.socket, buffer_size: int = 4096) -> str:
    """
    Receives data from a socket.

    Args:
        sock (socket.socket): The socket object to receive data from.
        buffer_size (int): The size of the data packet to receive.

    Returns:
        str: The received data, or an empty string in case of an error.
    """
    try:
        data = sock.recv(buffer_size)
        return data.decode('utf-8')
    except socket.timeout:
        Logger.warning("Data reception timed out.")
    except socket.error as ex:
        Logger.error(f"Data reception error: {ex}")
    return ""


# ==============================================================================
# Helper Functions and Random Operations
# ==============================================================================

def generate_random_password(length: int = 12) -> str:
    """
    Generates a random alphanumeric password of the specified length.
    The password includes letters (upper/lower), digits, and punctuation.

    Args:
        length (int): The length of the password to be generated.

    Returns:
        str: The randomly generated password.
    """
    if length <= 0:
        return ""

    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(characters) for _ in range(length))


def validate_email(email: str) -> bool:
    """
    Validates the basic format of an email address using a simple regex pattern.
    This validation does not guarantee complete correctness, only checks the basic format.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email format is valid, False otherwise.
    """
    # A more robust regex for email validation
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.search(regex, email) is not None


def format_datetime(date_time: datetime.datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Converts a datetime object to a string in the specified format.

    Args:
        date_time (datetime.datetime): The datetime object to format.
        format_str (str): The date format string.

    Returns:
        str: The formatted date string.
    """
    try:
        return date_time.strftime(format_str)
    except Exception as e:
        Logger.error(f"Datetime formatting error: {e}")
    return ""


def calculate_duration_string(start_time: float, end_time: float) -> str:
    """
    Returns the duration between two timestamps in a readable format.

    Args:
        start_time (float): The start timestamp (seconds).
        end_time (float): The end timestamp (seconds).

    Returns:
        str: The calculated duration (in "X.XX seconds" format).
    """
    difference = end_time - start_time
    return f"{difference:.2f} seconds"


# ==============================================================================
# Data Set Manipulation (Example Inventory Data)
# ==============================================================================

# Example data set with English keys
example_inventory_data = {
    "users": [
        {"id": 1, "first_name": "Ahmet", "last_name": "Yilmaz", "email": "ahmet@mail.com"},
        {"id": 2, "first_name": "Ayse", "last_name": "Kara", "email": "ayse@mail.com"},
        {"id": 3, "first_name": "Mehmet", "last_name": "Demir", "email": "mehmet@mail.com"}
    ],
    "products": [
        {"id": 101, "name": "Computer", "price": 15000, "stock": 50},
        {"id": 102, "name": "Phone", "price": 8000, "stock": 120},
        {"id": 103, "name": "Keyboard", "price": 750, "stock": 200}
    ]
}


def find_user_by_id(data_set: Dict, user_id: int) -> Union[Dict, None]:
    """
    Searches for a user in the given data set by their ID.

    Args:
        data_set (Dict): The data set to search within.
        user_id (int): The ID of the user to find.

    Returns:
        Union[Dict, None]: The user dictionary if found, otherwise None.
    """
    for user in data_set.get("users", []):
        if user.get("id") == user_id:
            return user
    return None


def update_product_price(data_set: Dict, product_id: int, new_price: float) -> bool:
    """
    Updates the price of a product by its ID.

    Args:
        data_set (Dict): The data set to update.
        product_id (int): The ID of the product whose price will be updated.
        new_price (float): The new price of the product.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    for product in data_set.get("products", []):
        if product.get("id") == product_id:
            product["price"] = new_price
            return True
    return False


def calculate_average_price(data_set: Dict) -> float:
    """
    Calculates the average price of all products in the data set.

    Args:
        data_set (Dict): The data set to perform the calculation on.

    Returns:
        float: The average price of the products.
    """
    products = data_set.get("products", [])
    if not products:
        return 0.0

    total_price = sum(product.get("price", 0) for product in products)
    return total_price / len(products)


def find_most_expensive_product(data_set: Dict) -> Union[Dict, None]:
    """
    Finds the most expensive product in the data set.

    Args:
        data_set (Dict): The data set to search within.

    Returns:
        Union[Dict, None]: The dictionary of the most expensive product or None.
    """
    products = data_set.get("products", [])
    if not products:
        return None

    most_expensive = max(products, key=lambda product: product.get("price", 0))
    return most_expensive


def find_cheapest_product(data_set: Dict) -> Union[Dict, None]:
    """
    Finds the cheapest product in the data set.

    Args:
        data_set (Dict): The data set to search within.

    Returns:
        Union[Dict, None]: The dictionary of the cheapest product or None.
    """
    products = data_set.get("products", [])
    if not products:
        return None

    cheapest = min(products, key=lambda product: product.get("price", float('inf')))
    return cheapest


def calculate_total_stock(data_set: Dict) -> int:
    """
    Calculates the total stock count of all products in the data set.

    Args:
        data_set (Dict): The data set to calculate from.

    Returns:
        int: The total stock count.
    """
    return sum(product.get("stock", 0) for product in data_set.get("products", []))


# ==============================================================================
# Miscellaneous and Advanced Utilities
# ==============================================================================

def get_file_size(filepath: str) -> int:
    """
    Returns the size of the specified file in bytes.
    Returns -1 if the file does not exist.

    Args:
        filepath (str): The path of the file to check size for.

    Returns:
        int: The file size or -1.
    """
    try:
        return os.path.getsize(filepath)
    except FileNotFoundError:
        Logger.error(f"File not found: {filepath}")
        return -1
    except Exception as e:
        Logger.error(f"Error getting file size: {e}")
        return -1


def timer_decorator(func: Callable) -> Callable:
    """
    A decorator that measures the execution time of a function.

    Args:
        func (Callable): The function whose execution time will be measured.

    Returns:
        Callable: The decorated function.
    """

    def wrapper_function(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        Logger.info(f"'{func.__name__}' executed in {end - start:.4f} seconds.")
        return result

    return wrapper_function


# Example Usage:
# @timer_decorator
# def slow_function():
#     time.sleep(2)
#     return "Process finished."

def shuffle_list(input_list: List[Any]) -> None:
    """
    Randomly shuffles a list in-place.

    Args:
        input_list (List[Any]): The list to be shuffled.
    """
    random.shuffle(input_list)


def generate_random_number_list(count: int, lower_bound: int, upper_bound: int) -> List[int]:
    """
    Creates a list of random numbers within the specified range and count.

    Args:
        count (int): The number of random numbers to generate.
        lower_bound (int): The lower limit.
        upper_bound (int): The upper limit.

    Returns:
        List[int]: The list of random numbers.
    """
    return [random.randint(lower_bound, upper_bound) for _ in range(count)]


def get_system_info() -> Dict[str, str]:
    """
    Returns basic system information as a dictionary.

    Returns:
        Dict[str, str]: System information details.
    """
    return {
        "platform": sys.platform,
        "python_version": sys.version,
        "operating_system": os.name,
        "current_directory": os.getcwd()
    }


def format_large_number(number: Union[int, float]) -> str:
    """
    Converts large numbers into a readable format (e.g., 1.2M, 1.5K).

    Args:
        number (Union[int, float]): The number to be formatted.

    Returns:
        str: The formatted number string.
    """
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)


def reverse_string(text: str) -> str:
    """
    Reverses the given text.

    Args:
        text (str): The text to be reversed.

    Returns:
        str: The reversed text.
    """
    return text[::-1]


def split_to_words(text: str) -> List[str]:
    """
    Splits a text into words and returns them as a list.

    Args:
        text (str): The text to be split into words.

    Returns:
        List[str]: The list of words.
    """
    return re.findall(r'\b\w+\b', text)


def find_most_frequent_word(text: str) -> Union[Tuple[str, int], None]:
    """
    Finds the most frequently used word and its count in a text.

    Args:
        text (str): The text to be analyzed.

    Returns:
        Union[Tuple[str, int], None]: A tuple of the most frequent word and its count
                                       (word, count), or None if the text is empty.
    """
    word_frequencies = get_word_frequency(text)
    if not word_frequencies:
        return None

    most_frequent_word = max(word_frequencies, key=word_frequencies.get)
    return (most_frequent_word, word_frequencies[most_frequent_word])


def caesar_encrypt(text: str, key: int) -> str:
    """
    Encrypts a text using a simple Caesar cipher.

    Args:
        text (str): The text to be encrypted.
        key (int): The encryption key (shift amount).

    Returns:
        str: The encrypted text.
    """
    encrypted_text = ""
    for character in text:
        if 'a' <= character.lower() <= 'z':
            start = ord('a') if 'a' <= character <= 'z' else ord('A')
            offset = (ord(character) - start + key) % 26
            encrypted_text += chr(start + offset)
        else:
            encrypted_text += character
    return encrypted_text


def caesar_decrypt(text: str, key: int) -> str:
    """
    Decrypts a text from a simple Caesar cipher.

    Args:
        text (str): The text to be decrypted.
        key (int): The encryption key (shift amount).

    Returns:
        str: The decrypted text.
    """
    return caesar_encrypt(text, -key)


def is_palindrome(text: str) -> bool:
    """
    Checks if the given text is a palindrome (reads the same forwards and backwards).
    Case and punctuation are ignored.

    Args:
        text (str): The text to be checked.

    Returns:
        bool: True if the text is a palindrome, False otherwise.
    """
    cleaned_text = re.sub(r'[\W_]', '', text).lower()
    return cleaned_text == cleaned_text[::-1]


def summarize_text_by_words(text: str, word_count: int) -> str:
    """
    Extracts a summary from the beginning of the text based on an approximate word count.

    Args:
        text (str): The text to be summarized.
        word_count (int): The approximate number of words desired in the summary.

    Returns:
        str: The summary of the text.
    """
    # Splits text by common sentence terminators (., !, ?)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    summary_sentences = []
    total_words = 0
    for sentence in sentences:
        words = sentence.split()
        total_words += len(words)
        summary_sentences.append(sentence)
        if total_words >= word_count:
            break

    summary = " ".join(summary_sentences)
    # Ensure the summary ends with punctuation if it doesn't already
    if summary and not summary.endswith(('.', '!', '?')):
        summary += "."
    return summary


def clear_file_content(filepath: str) -> bool:
    """
    Empties the content of a file.

    Args:
        filepath (str): The path to the file whose content will be cleared.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('')
        Logger.info(f"File content cleared: {filepath}")
        return True
    except FileNotFoundError:
        Logger.error(f"File not found: {filepath}")
    except Exception as e:
        Logger.error(f"File clearing error: {e}")
    return False


def copy_file(source: str, destination: str) -> bool:
    """
    Copies a file from one location to another.

    Args:
        source (str): The file to be copied.
        destination (str): The location where the file will be copied to.

    Returns:
        bool: True if the copy was successful, False otherwise.
    """
    try:
        shutil.copy2(source, destination)
        Logger.info(f"File copied: {source} -> {destination}")
        return True
    except FileNotFoundError:
        Logger.error("File not found.")
    except Exception as e:
        Logger.error(f"File copying error: {e}")
    return False
