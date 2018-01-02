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


import lab.custom as custom

# import django test module to interact with test database
from django.test import TestCase


class TestCapitalize(TestCase):
    def test_capitalize(self):
        self.assertEqual(custom.capitalize(['freeze_condition']), ['Freeze condition'])
        self.assertEqual(custom.capitalize(['freeze_time', 'thaw_uom']), ['Freeze time', 'Thaw uom'])

        with self.assertRaises(TypeError):
            custom.capitalize('test')
            custom.capitalize(2)
            custom.capitalize((2, 3))


class TestIdentifier(TestCase):
    def test_identifier(self):
        self.assertEqual(custom.identifier('S', 6), 'S000006')
        self.assertEqual(custom.identifier('P', 534667), 'P534667')
        self.assertEqual(custom.identifier('P', '534667'), 'P534667')

        with self.assertRaises(TypeError):
            custom.identifier(2, 2)
            custom.identifier(['test'], 'str')

        with self.assertRaises(ValueError):
            custom.identifier('PD', 5)
            custom.identifier('S', 4234323235)
            custom.identifier('S', '4234323235')


class TestTimedelta(TestCase):
    def test_timedelta(self):
        self.assertEqual(custom.timedelta('h', 24), custom.datetime.timedelta(hours=24))

        with self.assertRaises(TypeError):
            custom.timedelta(2, 2)
            custom.timedelta('d', 'test')

        with self.assertRaises(ValueError):
            custom.timedelta('day', 5)


class TestTimedeltaReverse(TestCase):
    def test_timedelta_reverse(self):
        self.assertEqual(custom.timedelta_reverse('h', custom.datetime.timedelta(hours=24)), 24)
        self.assertEqual(custom.timedelta_reverse('d', custom.datetime.timedelta(days=365)), 365)
        self.assertEqual(custom.timedelta_reverse('min', custom.datetime.timedelta(minutes=60)), 60)
        self.assertEqual(custom.timedelta_reverse('s', custom.datetime.timedelta(seconds=30)), 30)

        with self.assertRaises(TypeError):
            custom.timedelta(2, 2)
            custom.timedelta('d', 'test')


class TestGenerateChecksum(TestCase):
    def test_generate_checksum(self):
        self.assertEqual(custom.generate_checksum('test123'),
                         custom.argon2.using(salt_len=32, digest_size=32, rounds=1).hash('test123'))

        with self.assertRaises(TypeError):
            custom.generate_checksum(233)
            custom.generate_checksum(list())
            custom.generate_checksum(tuple())
            custom.generate_checksum(object())
