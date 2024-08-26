import re
from collections import OrderedDict
from typing import Tuple

from ..search import log

# Regular expression patterns
size_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*(\w+)')
magnet_hash_pattern = re.compile(r'btih:(\w+)')

# Conversion factors for different storage units
conversion_factors = OrderedDict([
    ('B', 1),
    ('KB', 1024),
    ('MB', 1048576),
    ('GB', 1073741824),
    ('TB', 1099511627776)
])


class Anime:
    def __init__(self, time: str, title: str, size: str, magnet: str):
        """
        Initialize an Anime object.

        Args:
            time: The time information.
            title: The title of the anime.
            size: The size of the file.
            magnet: The magnet link.
        """
        self.time = time
        self.title = title
        self.size = size
        self.magnet = magnet

    def size_format(self, unit) -> None:
        """
        Format the size of the file to the specified unit.

        Args:
            unit (str, optional): The target unit. Defaults to 'MB'.

        Raises:
            ValueError: If the size string is invalid or an invalid storage unit is provided.
        """
        try:
            value, pre_unit = self.extract_value_and_unit(self.size)
            if pre_unit != unit:
                value = self.convert_byte(value, pre_unit, unit)
                self.size = f"{value}{unit}"
        except ValueError as e:
            log.critical(f"Size format error: {e}")
            raise

    @staticmethod
    def convert_byte(value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert a byte value from one unit to another.

        Args:
            value (float): The value to convert.
            from_unit (str): The unit to convert from.
            to_unit (str): The unit to convert to.

        Returns:
            float: The converted value.

        Raises:
            ValueError: If an invalid storage unit is provided.
        """
        try:
            from_factor = conversion_factors[from_unit.upper()]
            to_factor = conversion_factors[to_unit.upper()]
        except KeyError as e:
            raise ValueError(f"Convert: invalid storage unit '{e.args[0]}'") from e

        return round(value * (from_factor / to_factor), 2)

    @staticmethod
    def extract_value_and_unit(size: str) -> Tuple[float, str]:
        """
        Extract the numeric value and unit from a size string.

        Args:
            size (str): The size string to parse.

        Returns:
            Tuple[float, str]: The extracted value and unit.

        Raises:
            ValueError: If the size string is invalid.
        """
        match = size_pattern.match(size)

        if match:
            value = float(match.group(1))
            unit = match.group(2)
            return value, unit
        else:
            raise ValueError(f"Extract: invalid size '{size}'")

    def __eq__(self, value: object) -> bool:
        """
        Compare two Anime objects based on their magnet hash.

        Args:
            value (object): The object to compare with.

        Returns:
            bool: True if the magnet hashes are equal, False otherwise.
        """
        if not isinstance(value, Anime):
            return False

        try:
            return magnet_hash_pattern.search(self.magnet).group(1) == magnet_hash_pattern.search(value.magnet).group(1)
        except AttributeError:
            log.critical("Magnet hash extraction failed.")
            return False

    def __ne__(self, other) -> bool:
        """
        Compare two Anime objects based on their magnet hash.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if the magnet hashes are not equal, False otherwise.
        """
        return not self.__eq__(other)

    def __str__(self) -> str:
        """
        Return a string representation of the Anime object.

        Returns:
            str: The string representation.
        """
        return f"Anime'{self.title}' with hash {magnet_hash_pattern.search(self.magnet).group(1)}"

    def __repr__(self) -> str:
        """
        Return a string representation of the Anime object.

        Returns:
            str: The string representation.
        """
        return f"Anime('{self.time}', '{self.title}', '{self.size}', '{self.magnet}')"
