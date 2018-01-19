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
