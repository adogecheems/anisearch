import re
from dataclasses import dataclass
from datetime import time
from functools import lru_cache
from typing import Tuple, Optional

from .. import log, SizeFormatError, TimeFormatError

size_pattern = re.compile(r'^(\d+(?:\.\d+)?)\s*(\w+)$')
magnet_hash_pattern = re.compile(r'btih:([a-fA-F0-9]+)')

conversion_factors = {
    'B': 1,
    'KB': 1 << 10,
    'MB': 1 << 20,
    'GB': 1 << 30,
    'TB': 1 << 40,
    'KIB': 1 << 10,
    'MIB': 1 << 20,
    'GIB': 1 << 30,
    'TIB': 1 << 40
}


@dataclass
class Anime:
    time: str
    title: str
    size: str
    magnet: str
    torrent: Optional[str] = None

    def size_format(self, unit: str = 'MB') -> None:
        """
        Format the size of the file to the specified unit.

        Args:
            unit (str, optional): The target unit. Defaults to 'MB'.

        Raises:
            SizeFormatError: When size formatting fails.
        """
        result = self.extract_value_and_unit(self.size)
        if not result:
            raise SizeFormatError(f"Failed to format size of the anime: {self.title}")

        value, pre_unit = result
        if pre_unit.upper() == unit.upper():
            return

        converted_value = self.convert_byte(value, pre_unit, unit)
        if converted_value is None:
            raise SizeFormatError(f"Failed to format size of the anime: {self.title}")

        self.size = f"{value}{unit}"

    def set_timefmt(self, from_timefmt: str, to_timefmt: str):
        """
        Convert the time string from one format to another.

        Args:
            from_timefmt (str): The original time format.
            to_timefmt (str): The target time format.


        """
        try:
            return time.strftime(to_timefmt, time.strptime(self.time, from_timefmt))
        except Exception as e:
            raise TimeFormatError(f"Invalid time format: {e.args[0]}")


    @staticmethod
    @lru_cache(maxsize=128)
    def convert_byte(value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """
        Convert a byte value from one unit to another.

        Args:
            value (float): The value to convert.
            from_unit (str): The unit to convert from.
            to_unit (str): The unit to convert to.

        Returns:
            Optional[float]: The converted value or None if conversion fails.
        """
        try:
            from_factor = conversion_factors[from_unit.upper()]
            to_factor = conversion_factors[to_unit.upper()]
            return round(value * (from_factor / to_factor), 2)
        except KeyError as e:
            log.error(f"Convert: invalid storage unit '{e.args[0] if e.args else 'unknown'}'")
            return None

    @staticmethod
    @lru_cache(maxsize=128)
    def extract_value_and_unit(size: str) -> Optional[Tuple[float, str]]:
        """
        Extract the numeric value and unit from a size string.

        Args:
            size (str): The size string to parse.

        Returns:
            Optional[Tuple[float, str]]: The extracted value and unit, or None if parsing fails.
        """
        if not size:
            log.error("Extract: size string is empty")
            return None

        match = size_pattern.match(size)
        if not match:
            log.error(f"Extract: invalid size format '{size}'")
            return None

        try:
            value = float(match.group(1))
            unit = match.group(2)
            return value, unit
        except ValueError:
            log.error(f"Extract: failed to convert value in '{size}'")
            return None

    def __eq__(self, other: object) -> bool:
        """
        Compare two Anime objects based on their magnet hash.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if the magnet hashes are equal, False otherwise.
        """
        if not isinstance(other, Anime):
            return NotImplemented

        try:
            return self._get_hash(self.magnet) == self._get_hash(other.magnet)
        except AttributeError:
            log.error("Magnet hash extraction failed.")
            return False

    def __hash__(self) -> int:
        """
        Calculate hash value for the Anime object.

        Returns:
            int: Hash value based on the magnet hash.
        """
        try:
            return hash(self._get_hash(self.magnet))
        except AttributeError:
            return hash(self.magnet)

    def __str__(self) -> str:
        """
        Return a string representation of the Anime object.

        Returns:
            str: The string representation.
        """
        try:
            hash_value = self._get_hash(self.magnet)
        except AttributeError:
            hash_value = "unknown"
        return f"Anime '{self.title}' with hash {hash_value}"

    @lru_cache(maxsize=1)
    def _get_hash(self, magnet: str) -> str:
        """
        Extract and return the hash from the magnet link.

        Args:
            magnet (str): The magnet link.

        Returns:
            str: The lowercase hash value.

        Raises:
            AttributeError: If hash extraction fails.
        """
        match = magnet_hash_pattern.search(magnet)
        return match.group(1).lower()
