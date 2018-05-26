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


class TestCheckEqual(TestCase):
    def test_check_equal(self):
        self.assertEqual(custom.check_equal([True, True, True, True]), True)
        self.assertEqual(custom.check_equal([True, True, False, True]), False)

        with self.assertRaises(TypeError):
            custom.check_equal('1')
            custom.check_equal(2)
            custom.check_equal(dict())
            custom.check_equal(tuple())
            custom.check_equal(object())


class FillUpTimeDelta(TestCase):
    def test_fill_up_time_delta(self):
        self.assertEqual(custom.fill_up_time_delta('-120'), '+02')
        self.assertEqual(custom.fill_up_time_delta('120'), '-02')
        self.assertEqual(custom.fill_up_time_delta('-180'), '+03')
        self.assertEqual(custom.fill_up_time_delta('-600'), '+10')
        self.assertEqual(custom.fill_up_time_delta('+660'), '-11')

        with self.assertRaises(TypeError):
            custom.transform_box_type_figures(2)
            custom.transform_box_type_figures(list())
            custom.transform_box_type_figures(dict())
            custom.transform_box_type_figures(tuple())
            custom.transform_box_type_figures(object())


class TestTransformBoxTypeFigures(TestCase):
    def test_transform_box_type_figures(self):
        self.assertEqual(custom.transform_box_type_figures('2'), 2)
        self.assertEqual(custom.transform_box_type_figures('B'), 2)
        self.assertEqual(custom.transform_box_type_figures('c'), 3)

        with self.assertRaises(TypeError):
            custom.transform_box_type_figures(2)
            custom.transform_box_type_figures(list())
            custom.transform_box_type_figures(dict())
            custom.transform_box_type_figures(tuple())
            custom.transform_box_type_figures(object())


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


class TestDetermineBoxTypeFiguresType(TestCase):
    def test_determine_box_type_figures_type(self):
        self.assertEqual(custom.determine_box_type_figures_type('2'), int)
        self.assertEqual(custom.determine_box_type_figures_type('B'), str)
        self.assertEqual(custom.determine_box_type_figures_type('c'), str)

        with self.assertRaises(TypeError):
            custom.determine_box_type_figures_type(2)
            custom.determine_box_type_figures_type(list())
            custom.determine_box_type_figures_type(dict())
            custom.determine_box_type_figures_type(tuple())
            custom.determine_box_type_figures_type(object())


class TestDetermineBoxPosition(TestCase):
    def test_determine_box_position(self):
        self.assertEqual(custom.determine_box_position('Horizontal', '4', '4', 15), '34')
        self.assertEqual(custom.determine_box_position('Horizontal', 'D', '4', 12), 'D3')
        self.assertEqual(custom.determine_box_position('Vertical', '4', 'D', 6), 'B2')
        self.assertEqual(custom.determine_box_position('Vertical', '4', '4', 3), '31')

        with self.assertRaises(TypeError):
            custom.determine_box_position(2, '4', '4', 15)
            custom.determine_box_position(list(), '4', '4', 15)
            custom.determine_box_position(dict(), '4', '4', 15)
            custom.determine_box_position(tuple(), '4', '4', 15)
            custom.determine_box_position(object(), '4', '4', 15)
            custom.determine_box_position('Horizontal', 2, '4', 15)
            custom.determine_box_position('Horizontal', list(), '4', 15)
            custom.determine_box_position('Horizontal', dict(), '4', 15)
            custom.determine_box_position('Horizontal', tuple(), '4', 15)
            custom.determine_box_position('Horizontal', object(), '4', 15)
            custom.determine_box_position('Horizontal', '4', 2, 15)
            custom.determine_box_position('Horizontal', '4', list(), 15)
            custom.determine_box_position('Horizontal', '4', dict(), 15)
            custom.determine_box_position('Horizontal', '4', tuple(), 15)
            custom.determine_box_position('Horizontal', '4', object(), 15)
            custom.determine_box_position('Horizontal', '4', '4', '2')
            custom.determine_box_position('Horizontal', '4', '4', list())
            custom.determine_box_position('Horizontal', '4', '4', dict())
            custom.determine_box_position('Horizontal', '4', '4', tuple())
            custom.determine_box_position('Horizontal', '4', '4', object())
