"""
turtle-lab.org
Copyright (C) 2017  Henrik Baran

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


# python imports
import datetime
from passlib.hash import argon2


ALPHABET = {
    'A': 1,
    'B': 2,
    'C': 3,
    'D': 4,
    'E': 5,
    'F': 6,
    'G': 7,
    'H': 8,
    'I': 9,
    'J': 10,
    'K': 11,
    'L': 12,
    'M': 13,
    'N': 14,
    'O': 15,
    'P': 16,
    'Q': 17,
    'R': 18,
    'S': 19,
    'T': 20,
    'U': 21,
    'V': 22,
    'W': 23,
    'X': 24,
    'Y': 25,
    'Z': 26,
}

ALPHABET_INV = {v: k for k, v in ALPHABET.items()}


class Echo:
    """An object that implements just the write method of the file-like interface."""
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def check_equal(iterator):
    """Function to check, if all items of a list are equal.

    :param iterator: list of values to check equality
    :type iterator: list

    :return: equal or not
    :rtype: bool
    """
    if not isinstance(iterator, list):
        raise TypeError('Argument of type list expected.')
    return len(set(iterator)) <= 1


def capitalize(header):
    """Table header names provided as strings in a list are capitalized and underscores get replaced with spaces.  

        :param header: default table header list provided by django
        :type header: list
        
        :returns: well formatted table headers 
        :rtype: list
    """
    if not isinstance(header, list):
        raise TypeError('Argument of type list expected.')
    x = 0
    for item in header:
        header[x] = item.capitalize().replace('_', ' ')
        x += 1
    return header


def identifier(prefix, table_id):
    """Generate 6-digit identifiers in combination with a prefix.  

        :param prefix: one digit prefix
        :type prefix: str
        :param table_id: table primary key unique id
        :type table_id: int, str

        :returns: generated identifier  
        :rtype: str
    """
    if not isinstance(prefix, str):
        raise TypeError('Argument "prefix" expects type str.')
    if not isinstance(table_id, int) and not isinstance(table_id, str):
        raise TypeError('Argument "table_id" expects type int or str.')
    if len(prefix) > 1:
        raise ValueError('Argument "prefix" must not exceed one digit.')
    if len(str(table_id)) > 6:
        raise ValueError('Argument "table_id" must not exceed six digits.')
    return '{}{}{}'.format(prefix, (6 - len(str(table_id))) * '0', table_id)


def timedelta(uom, duration):
    """Generate a datetime timedelta object by using unit of measurements and durations 

        :param uom: unit of measurement ("d" / "s" / "min" / "h")
        :type uom: str
        :param duration: duration 
        :type duration: int

        :returns: generated timedelta object
        :rtype: object
    """
    if not isinstance(uom, str):
        raise TypeError('Argument "uom" expects type str.')
    if not isinstance(duration, int):
        raise TypeError('Argument "duration" expects type int.')
    allowed = ['d', 's', 'min', 'h']
    if uom not in allowed:
        raise ValueError('Argument "uom" must match "d", "s", "min" or "h". ')
    if uom == 'd':
        return datetime.timedelta(days=duration)
    elif uom == 's':
        return datetime.timedelta(seconds=duration)
    elif uom == 'min':
        return datetime.timedelta(minutes=duration)
    elif uom == 'h':
        return datetime.timedelta(hours=duration)


def timedelta_reverse(uom, dt):
    """Convert a datetime timedelta object to integer of passed unit of measurement.  

        :param uom: unit of measurement ("d" / "s" / "min" / "h")
        :type uom: str
        :param dt: datetime timedelta object 
        :type dt: datetime.timedelta

        :returns: datetime duration in days, seconds, minutes or hours
        :rtype: int
    """
    if not isinstance(uom, str):
        raise TypeError('Argument "uom" expects type str.')
    if not isinstance(dt, datetime.timedelta):
        raise TypeError('Argument "dt" expects type datetime.timedelta object.')
    if uom == 'd':
        return dt.days
    elif uom == 's':
        return int(dt.total_seconds())
    elif uom == 'min':
        return int(dt.total_seconds() / 60)
    elif uom == 'h':
        return int(dt.total_seconds() / 3600)


def generate_checksum(to_hash):
    """Generates a hash string. 

        :param to_hash: string to hash
        :type to_hash: str

        :returns: hash string
        :rtype: str
    """
    if not isinstance(to_hash, str):
        raise TypeError('Argument "to_hash" expects type str.')
    return argon2.using(salt_len=32, digest_size=32, rounds=1).hash(to_hash)


def hash_password(to_hash):
    """Generates a password hash string. 

        :param to_hash: password string to hash
        :type to_hash: str

        :returns: hash string
        :rtype: str
    """
    if not isinstance(to_hash, str):
        raise TypeError('Argument "to_hash" expects type str.')
    return argon2.using(salt_len=32, digest_size=32, rounds=100).hash(to_hash)


class UserName(object):
    def __init__(self, first_name, last_name, existing_users):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.length = len(last_name)
        self._tmp_first_name = str()
        self.existing = existing_users

    @property
    def tmp_first_name(self):
        return self._tmp_first_name

    @tmp_first_name.setter
    def tmp_first_name(self, value):
        self._tmp_first_name = value

    @property
    def algorithm(self):
        """Function to generate unique user names. 

            :returns: username
            :rtype: str
        """
        for x in range(self.length):
            first_name = '{}{}'.format(self.tmp_first_name, self.first_name[x])
            username = '{}{}'.format(self.last_name, first_name)
            if username in self.existing:
                self.tmp_first_name = first_name
            else:
                return username
        for x in range(100):
            first_name = '{}{}'.format(self.first_name, x + 1)
            username = '{}{}'.format(self.last_name, first_name)
            if username in self.existing:
                self.tmp_first_name = first_name
            else:
                return username


def transform_box_type_figures(value):
    """Transforms strings to integers if integer content or alphabet characters to integers if possible.

    :param value: string containing integers or alphabet characters
    :type value: str

    :return: transformed integer
    :rtype: int
    """
    if not isinstance(value, str):
        raise TypeError('Argument of type string expected.')
    try:
        _value = int(value)
        if isinstance(_value, int):
            return _value
    except ValueError:
        return ALPHABET[value.capitalize()]


def determine_box_type_figures_type(value):
    """Determine if a box type row/column is a character or a integer.

    :param value: string containing integers or alphabet characters
    :type value: str

    :return: integer ir string depending on type
    :rtype: int/str
    """
    if not isinstance(value, str):
        raise TypeError('Argument of type string expected.')
    try:
        _value = int(value)
        if isinstance(_value, int):
            return int
    except ValueError:
        return str


def determine_box_position(alignment, x, y, value):
    """This function determines the box target position by coordinates using alignment, max row and max column.

    :param alignment: box alignment
    :type alignment: str
    :param x: max column
    :type x: str
    :param y: max row
    :type y: str
    :param value: target position
    :type value: int

    :return: box position as string
    :rtype: str
    """
    if not isinstance(alignment, str):
        raise TypeError('Argument of type string expected.')
    if not isinstance(x, str):
        raise TypeError('Argument of type string expected.')
    if not isinstance(y, str):
        raise TypeError('Argument of type string expected.')
    if not isinstance(value, int):
        raise TypeError('Argument of type integer expected.')
    i = 0.999
    x_max = transform_box_type_figures(x)
    y_max = transform_box_type_figures(y)
    if alignment == 'Horizontal':
        _second = int(value / x_max + i)
        _first = value - x_max * (_second - 1)
        if determine_box_type_figures_type(x) is int:
            first = _first
        else:
            first = ALPHABET_INV[_first]
        if determine_box_type_figures_type(y) is int:
            second = _second
        else:
            second = ALPHABET_INV[_second]
    else:
        _second = int(value / y_max + i)
        _first = value - y_max * (_second - 1)
        if determine_box_type_figures_type(x) is int:
            second = _second
        else:
            second = ALPHABET_INV[_second]
        if determine_box_type_figures_type(y) is int:
            first = _first
        else:
            first = ALPHABET_INV[_first]
    return '{}{}'.format(first, second)


def value_to_bool(value):
    """Converts 0/1 values to bool

    :param value: value containing 0 or 1
    :type value: int/str
    :return: bool
    """
    if not isinstance(value, int):
        value = value_to_int(value)
    if value > 1:
        raise ValueError('Only 0 or 1 allowed.')
    return bool(value)


def value_to_int(value):
    """Converts value to real integer

    :param value: string with integer content or integer
    :type value: str/int
    :return: int
    """
    if not isinstance(value, str):
        if isinstance(value, int):
            return value
        else:
            raise TypeError('Argument of type string or integer expected.')
    try:
        return int(value)
    except ValueError:
        raise ValueError('Can not convert "{}" to integer.'.format(value))
