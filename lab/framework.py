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
import os
import json
import logging
import svgwrite
import datetime
from passlib.hash import argon2
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF


# django imports
from django.utils import timezone
from django.conf import settings

# app imports
import lab.models as models
import lab.custom as custom

# define logger
log = logging.getLogger(__name__)

# secret key
SECRET = settings.SECRET


class Labels(object):
    def __init__(self):
        self.dpi = 600
        self.margin = self.pixel(4)  # 3 mm margin top/bottom/left/right
        self.width = self.pixel(62)  # 62 mm width
        self.height = self.pixel(29)  # 29 mm height
        self.json_b = self._get_json_b
        self.json_c = self._get_json_c
        self.json_inv_b = self._get_json_inv_b
        self._bar = 8
        self._code = str()
        self._font_size = '140px'
        self._font_family = 'arial'
        self._svg = str()
        self._pdf_url = str()
        self._pdf = str()
        # self.quiet_zone = self.margin + 10 * self.bar

    def pixel(self, value):
        return round((self.dpi * value) / 25.4)

    @property
    def _get_json_b(self):
        with open(settings.FILES_DIR + '/128B.json') as json_file:
            return json.load(json_file)

    @property
    def _get_json_c(self):
        with open(settings.FILES_DIR + '/128C.json') as json_file:
            return json.load(json_file)

    @property
    def _get_json_inv_b(self):
        _return = dict()
        for x in self.json_b:
            _return[self.json_b[x]["Value"]] = {"Character": x, "Pattern": self.json_b[x]["Pattern"]}
        return _return

    def pattern_json_b(self, digit):
        return str(self.json_b[digit]["Pattern"])

    def pattern_json_c(self, digit):
        return str(self.json_c[digit]["Pattern"])

    def value_json_b(self, digit):
        return self.json_b[digit]["Value"]

    def value_json_c(self, digit):
        return self.json_c[digit]["Value"]

    def value_json_inv_b(self, value):
        return str(self.json_inv_b[value]["Pattern"])

    @property
    def stop(self):
        return str(self.json_b["Stop"]["Pattern"]) + "11"

    @property
    def start(self):
        return str(self.json_b["Start Code B"]["Pattern"]), self.json_b["Start Code B"]["Value"]

    @property
    def bar(self):
        return self._bar

    @bar.setter
    def bar(self, value):
        self._bar = value

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        self._font_size = value

    @property
    def font_family(self):
        return self._font_family

    @font_family.setter
    def font_family(self, value):
        self._font_family = value

    @property
    def svg(self):
        return self._svg

    @svg.setter
    def svg(self, value):
        self._svg = settings.MEDIA_ROOT + '/' + value

    @property
    def pdf(self):
        return self._pdf

    @pdf.setter
    def pdf(self, value):
        self._pdf = settings.MEDIA_ROOT + '/' + value

    @property
    def pdf_url(self):
        return self._pdf_url

    @pdf_url.setter
    def pdf_url(self, value):
        self._pdf_url = settings.MEDIA_URL + value

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, data):
        # 0 - slice data into leading character and numbers
        leading = data[0]
        tmp = data[1:]
        numbers = [tmp[i:i + 2] for i in range(0, len(tmp), 2)]
        # 1 - get start pattern and value for code b
        pattern, value = self.start
        # 2 - add leading character in code b
        pattern += self.pattern_json_b(leading)
        value += self.value_json_b(leading)
        # 3 - add start pattern and value for code c
        weight = 2
        pattern += self.pattern_json_b("Code C")
        value += weight * self.value_json_b("Code C")
        # 4 - process data input
        for position in numbers:
            weight += 1
            pattern += self.pattern_json_c(position)
            value += weight * self.value_json_c(position)

        # 5 - check symbol (remainder mod 103)
        remainder = value % 103
        pattern += self.value_json_inv_b(remainder)
        # 6 - stop symbol
        pattern += self.stop
        self._code = pattern

    @property
    def exists(self):
        return os.path.isfile(self.pdf)

    def reagent(self, unique, version):
        """Function to create a standard reagent label.

            :param unique: unique value of reagent for creating label
            :type unique: str
            :param version: reagent record version
            :type version: int
            :returns: flag + path for printing
            :rtype: bool, str
        """
        # define variables for reagent label
        self.font_size = '80px'
        # _path must match exactly that pattern: no leading slash, but must end with slash
        _path = 'reagents/'
        # create .svg and .pdf paths and file names
        self.svg = _path + '{}_v-{}.svg'.format(unique, version)
        self.svg_url = _path + '{}_v-{}.svg'.format(unique, version)

        # check if label already exists
        if self.exists:
            log.info('SVG label file for reagent "{}" version "{}" already exists. Using existing SVG for printing.'
                     .format(unique, version))
            return True, self.svg_url
        else:
            # generate code
            self.code = unique
            # label design
            dwg = svgwrite.Drawing(filename=self.svg, size=(self.width, self.height))
            dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))
            dwg.add(dwg.text(unique, insert=(self.margin + 100, self.margin + 50), font_size=self.font_size,
                             font_family=self.font_family, font_weight="bold"))

            # left cutting line
            dwg.add(dwg.line(start=(self.margin, self.margin),
                             end=(self.margin, self.height),
                             stroke="black", stroke_width=self.bar))

            for idx, y in enumerate(self.code):
                if y is "0":
                    stroke = "white"
                else:
                    stroke = "black"
                dwg.add(dwg.line(start=(self.quiet_zone + idx * self.bar, self.margin + 100),
                                 end=(self.quiet_zone + idx * self.bar, self.height),
                                 stroke=stroke, stroke_width=self.bar))

            # right cutting line
            cut_end = self.bar * len(self.code) + self.quiet_zone + 10 * self.bar
            dwg.add(dwg.line(start=(self.margin + cut_end, self.margin),
                             end=(self.margin + cut_end, self.height),
                             stroke="black", stroke_width=self.bar))
            # try to save SVG file
            try:
                dwg.save()
                message = 'SVG label file "{}" for reagent "{}" version "{}" has successfully been created.' \
                    .format(self.svg, unique, version)
                log.info(message)
            except:
                # raise error
                message = 'Could not create SVG label file for reagent "{}" version "{}".'.format(unique, version)
                raise NameError(message)
            # log entries for successful pdf generation
            return True, self.svg_url

    def default(self, unique, version, label):
        """Function to create a standard label.

            :param unique: unique label value
            :type unique: str
            :param version: label version
            :type version: str
            :param label: label object can be "location", "box" or "reagent"
            :returns: flag + path for printing
            :rtype: bool, str
        """
        # validation
        if not isinstance(unique, str) or not isinstance(label, str) or not isinstance(version, str):
            raise TypeError('Argument of type string expected.')
        allowed = ['location', 'box', 'reagent']
        if label not in allowed:
            raise ValueError('Argument "label" must match "location", "box" or "reagent".')
        # create .svg and .pdf paths and file names
        self.svg = label + '/{}_v-{}.svg'.format(unique, version)
        self.pdf = label + '/{}_v-{}.pdf'.format(unique, version)
        self.pdf_url = label + '/{}_v-{}.pdf'.format(unique, version)

        # check if label already exists
        if self.exists:
            log.info('PDF File for {} "{}" version "{}" already exists. Using existing PDF file for printing.'
                     .format(label, unique, version))
            return True, self.pdf_url
        else:
            # generate code
            self.code = unique
            # label design
            dwg = svgwrite.Drawing(filename=self.svg, size=(self.width, self.height))
            dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))
            dwg.add(dwg.text(unique, insert=(self.margin + 50, self.margin + 100), font_size=self.font_size,
                             font_family=self.font_family, font_weight="bold"))

            # determine barcode length
            barcode_length = len(self.code) * self.bar
            left = (self.width - barcode_length) / 2

            # barcode
            for idx, y in enumerate(self.code):
                if y is "0":
                    stroke = "white"
                else:
                    stroke = "black"
                dwg.add(dwg.line(start=(left + idx * self.bar, self.margin + 170),
                                 end=(left + idx * self.bar, self.height - self.margin),
                                 stroke=stroke, stroke_width=self.bar))

            try:
                # save SVG
                dwg.save()
                message = 'SVG label file "{}" for {} "{}" version "{}" has successfully been created.' \
                    .format(self.svg, label, unique, version)
                log.info(message)
            except:
                # raise error
                message = 'Could not create SVG file for {} "{}" version "{}".'.format(label, unique, version)
                raise NameError(message)
            else:
                try:
                    # save raw PDF
                    drawing = svg2rlg(self.svg)
                    renderPDF.drawToFile(drawing, self.pdf)
                    message = 'PDF label file "{}" for {} "{}" version "{}" has successfully been created.' \
                        .format(self.pdf, label, unique, version)
                    log.info(message)
                except:
                    # raise error
                    message = 'Could not create PDF file for {} "{}" version "{}".' \
                        .format(label, unique, version)
                    raise NameError(message)
                else:
                    return True, self.pdf_url


class Master(object):
    def __init__(self, table):
        self.table = table
        self.table_name = table._meta.db_table
        self.unique = self.table.objects.unique
        self._timestamp = None

    @property
    def _table_header(self):
        return [head.name for head in self.table._meta.get_fields()]

    def query(self, order_by=False, **dic):
        """Function to create new standard audit trail entries. 

            :param order_by: order field (bool for no order necessary)
            :type order_by: bool, str
            :param dic: custom table fields 
            :type dic: str/int/float

            :returns: django query set
            :rtype: dict
        """
        try:
            if not order_by:
                _return = self.table.objects.filter(**dic).values()
            else:
                _return = self.table.objects.order_by(order_by).filter(**dic).values()
            return _return
        except:
            # raise error
            message = 'Could not query "{}" in table "{}".'.format(dic, self.table_name)
            raise NameError(message)

    def record_version(self, unique):
        return self.table.objects.version(unique)

    def record_id(self, unique):
        return self.table.objects.id(unique)

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value


class GetStandard(Master):
    def __init__(self, table, dt=None):
        super().__init__(table)
        if dt:
            self.dt = datetime.timedelta(seconds=int(dt) * 60)
            self.utc_offset = custom.fill_up_time_delta(dt)

    @property
    def header(self):
        _header = self._table_header
        _header.remove('id')
        _header.remove('checksum')
        if self.unique == 'username':
            _header.remove('last_login')
        return _header

    @property
    def js_header(self):
        _header = self.header
        _header.remove('version')
        # add amount field for AJAX in case of sample master data dialog
        if self.unique == 'sample':
            _header.append('amount')
        if self.unique == 'username':
            _header.append('password_repeat')
        return _header

    @property
    def html_header(self):
        _header = self.header
        return custom.capitalize(_header)

    @property
    def js_get(self):
        _return = list()
        for item in self.js_header:
            if item == 'permissions':
                _return.append('var v_{0} = $(myDomElement).find("#id_{0}").val().toString();'.format(item))
            elif item == 'is_active' or item == 'default' or item == 'mandatory':
                _return.append('var v_{0} = $(myDomElement).find("#id_{0}").is(":checked");'.format(item))
            else:
                _return.append('var v_{0} = $(myDomElement).find("#id_{0}").val();'.format(item))
        return _return

    @property
    def js_post(self):
        _return = list()
        for item in self.js_header:
            _return.append('"{0}": v_{0},'.format(item))
        return _return

    @property
    def order_by(self):
        return '-id'

    def table_row_head(self, row=None):
        if row is None or self.verify_checksum(row=row):
            return '<tr>'
        else:
            return '<tr style="color: red">'

    def verify_checksum(self, row):
        """Function to get standard table entries. 

            :param row: Django queryset
            :type row: dict

            :returns: flag
            :rtype: bool
        """
        to_verify = str()
        for field in self.header:
            to_verify += '{}:{};'.format(field, row[field])

        to_verify += str(SECRET)
        checksum = row['checksum']
        try:
            result = argon2.verify(to_verify, checksum)
            if not result:
                # return false + log entry
                message = 'Checksum for "{}" of table "{}" was not correct. Data integrity is at risk!'. \
                    format(row[self.unique], self.table_name)
                log.warning(message)
            return result
        except ValueError or TypeError:
            # return false + log entry
            message = 'Checksum for "{}" of table "{}" was not correct. Data integrity is at risk!'.\
                format(row[self.unique], self.table_name)
            log.warning(message)
            return False

    def get(self, **dic):
        """Function to get standard table entries. 

            :param dic: custom table fields
            :type dic: str/int/float

            :returns: flag + data
            :rtype: bool, list
        """
        _query = self.query(order_by=self.order_by, **dic)
        _list = list()
        for row in _query:
            # open table
            tmp = self.table_row_head(row=row)
            for field in self.header:
                # tagging the unique field
                if field == self.unique:
                    tmp += '<td class="unique gui">{}</td>'.format(row[field])
                # formatting the timestamp
                elif field == 'timestamp':
                    tmp += '<td>{}</td>'.format(custom.format_timestamp(timestamp=row[field],
                                                                        dt=self.dt,
                                                                        utc_offset=self.utc_offset))
                # formatting duration fields
                elif field == 'freeze_time':
                    tmp += '<td class="gui">{}</td>'.format(custom.timedelta_reverse(uom=row['freeze_uom'],
                                                                                     dt=row[field]))
                    # formatting duration fields
                elif field == 'thaw_time':
                    tmp += '<td class="gui">{}</td>'.format(custom.timedelta_reverse(uom=row['thaw_uom'],
                                                                                     dt=row[field]))
                # tagging the version for printing correct label
                elif field == 'version':
                    tmp += '<td class="version">{}</td>'.format(row[field])
                elif field == 'password':
                    tmp += '<td>*****</td>'
                elif field == 'is_active' or field == 'initial_password' or field == 'active' or field == 'default' \
                        or field == 'mandatory':
                    if row[field]:
                        tmp += '<td class="gui"><p style="display: none">True</p>' \
                               '<i class="fas fa-check-circle" style="color: green"></td>'
                    else:
                        tmp += '<td class="gui"><p style="display: none">False</p>' \
                               '<i class="fas fa-minus-circle" style="color: red"></i></td>'
                elif field != self.unique and field != 'version':
                    tmp += '<td class="gui">{}</td>'.format(row[field])
                else:
                    tmp += '<td>{}</td>'.format(row[field])
            # close table
            tmp += '</tr>'
            # append table row
            _list.append(tmp)
        return _list

    @property
    def export(self):
        value_list = self.table.objects.values_list(*self.header)
        _return = [tuple(custom.capitalize(self.header))]
        for row in value_list:
            _return.append(row)
        return _return


class GetAuditTrail(GetStandard):
    @property
    def header(self):
        _header = self._table_header
        _header.remove('id')
        _header.remove('checksum')
        _header.remove('id_ref')
        return _header

    def table_row_head(self, row=None):
        if self.verify_checksum(row=row):
            return '<tr class="tmp_audit_trail">'
        else:
            return '<tr class="tmp_audit_trail" style="color: red">'

    def get(self, **dic):
        """Function to get audit trail table entries. 

            :param dic: custom table fields (for audit trail mostly "id_ref")
            :type dic: str/int/float

            :returns: flag + data
            :rtype: bool, list
        """
        _query = self.query(order_by=self.order_by, **dic)
        _list = list()
        for row in _query:
            # open table
            tmp = self.table_row_head(row=row)
            for field in self.header:
                # formatting the timestamp
                if field == 'timestamp':
                    tmp += '<td>{}</td>'.format(custom.format_timestamp(timestamp=row[field],
                                                                        dt=self.dt,
                                                                        utc_offset=self.utc_offset))
                # formatting duration fields
                elif field == 'freeze_time':
                    tmp += '<td>{}</td>'.format(custom.timedelta_reverse(uom=row['freeze_uom'], dt=row[field]))
                # formatting duration fields
                elif field == 'thaw_time':
                    tmp += '<td>{}</td>'.format(custom.timedelta_reverse(uom=row['thaw_uom'], dt=row[field]))
                elif field == 'is_active' or field == 'initial_password' or field == 'active' or field == 'default' \
                        or field == 'mandatory':
                    if row[field]:
                        tmp += '<td><p style="display: none">True</p>' \
                               '<i class="fas fa-check-circle" style="color: green"></td>'
                    else:
                        tmp += '<td><p style="display: none">False</p>' \
                               '<i class="fas fa-minus-circle" style="color: red"></td>'
                else:
                    tmp += '<td>{}</td>'.format(row[field])
            # close table
            tmp += '</tr>'
            # append table row
            _list.append(tmp)
        return True, _list


class GetView(GetStandard):
    @property
    def header(self):
        _header = self._table_header
        _header.remove('id')
        return _header

    @property
    def html_header(self):
        _header = self.header
        return custom.capitalize(_header)

    @property
    def order_by(self):
        return '-object'

    def get(self, **dic):
        """Function to get view entries. 

            :param dic: custom table fields 
            :type dic: str/int/float

            :returns: flag + data
            :rtype: bool, list
        """
        _query = self.query(order_by=self.order_by, **dic)
        _list = list()
        for row in _query:
            # open table
            tmp = self.table_row_head()
            for field in self.header:
                # locations and box can be empty
                if field == 'location' or field == 'box' or field == 'position':
                    tmp += '<td>{}</td>'.format('' if row[field] is None else row[field])
                # thaw count
                elif field == 'remaining_thaw_count':
                    tmp += '<td>{}</td>'.format('' if row[field] is None else row[field])
                # freeze time
                elif field == 'remaining_freeze_time':
                    if row[field] is None:
                        formatting = ''
                    else:
                        # get current state
                        state = models.Times.objects.method(row[self.unique])
                        if state == 'freeze':
                            dt = row[field] - (timezone.now() - models.Times.objects.freeze_time(row[self.unique]))
                            formatting = datetime.timedelta(seconds=int(dt.total_seconds()))
                        else:
                            formatting = datetime.timedelta(seconds=int((row[field].total_seconds())))
                    tmp += '<td>{}</td>'.format(formatting)
                else:
                    tmp += '<td>{}</td>'.format(row[field])
            # close table
            tmp += '</tr>'
            # append table row
            _list.append(tmp)
        return _list


class GetLog(GetStandard):
    pass


class GetDynamic(GetStandard):
    def __init__(self, table, dynamic_table, type):
        super().__init__(table)
        self.type = type
        self.type_attributes = models.TypeAttributes.objects.columns_as_list(type=type)
        self.dynamic_table = dynamic_table
        self.dynamic_table_name = dynamic_table._meta.db_table
        self.dynamic_table_unique = self.dynamic_table.objects.unique
        self.affiliation = models.Types.objects.get_affiliation(type=type)

    @property
    def js_header(self):
        _header = self.header_start
        for column in self.type_attributes:
            _header.append(column)
        return _header

    @property
    def _table_header_dynamic(self):
        return [head.name for head in self.dynamic_table._meta.get_fields()]

    def query_dynamic(self, id_main):
        """Query dynamic table for main record id.

            :param id_ref: main record identifier id
            :type id_ref: int

            :return: records for id_ref
            :rtype: django.db.models.query.QuerySet
        """
        return self.dynamic_table.objects.filter(id_main=id_main).values()

    @property
    def header_dynamic(self):
        _header_dynamic = self._table_header_dynamic
        _header_dynamic.remove('id')
        _header_dynamic.remove('checksum')
        return _header_dynamic

    @property
    def header_start(self):
        _header_start = self.header
        if self.affiliation == 'Reagents':
            _header_start.remove('type')
        _header_start.remove('version')
        return _header_start

    @property
    def html_header(self):
        _header = self.header_start + self.type_attributes
        _header.append('Version')
        return custom.capitalize(_header)

    def table_row_head_total(self, row, query_dynamic):
        if self.verify_checksum(row=row):
            _success_list = list()
            for row in query_dynamic:
                if not self.verify_checksum_dynamic(row=row):
                    _success_list.append(False)
                else:
                    _success_list.append(True)
            if custom.check_equal(_success_list):
                return '<tr>'
            else:
                return '<tr style="color: red">'
        else:
            return '<tr style="color: red">'

    def verify_checksum_dynamic(self, row):
        """Verify checksum of dynamic class table.

            :param row: element of Django queryset
            :type row: dict

            :returns: success flag
            :rtype: bool
        """
        to_verify = str()
        for field in self.header_dynamic:
            to_verify += '{}:{};'.format(field, row[field])

        to_verify += str(SECRET)
        checksum = row['checksum']
        try:
            result = argon2.verify(to_verify, checksum)
            if not result:
                # return false + log entry
                unique_main = models.Reagents.objects.filter(id=row['id_main'])[0].reagent
                message = 'Checksum for "{}" attribute "{}" with id "{}" of table "{}" was not correct. ' \
                          'Data integrity is at risk!'. \
                    format(unique_main, row['type_attribute'], row[self.dynamic_table_unique], self.dynamic_table_name)
                log.warning(message)
            return result
        except ValueError or TypeError:
            # return false + log entry
            unique_main = models.Reagents.objects.filter(id=row['id_main'])[0].reagent
            message = 'Checksum for "{}" attribute "{}" with id "{}" of table "{}" was not correct. ' \
                      'Data integrity is at risk!'. \
                format(unique_main, row['type_attribute'], row[self.dynamic_table_unique], self.dynamic_table_name)
            log.warning(message)
            return False

    def get(self, **dic):
        _query = self.query(order_by=self.order_by, type=self.type)
        _list = list()
        for row in _query:
            _query_dynamic = self.query_dynamic(row['id'])
            tmp = self.table_row_head_total(row=row, query_dynamic=_query_dynamic)
            # adding all tds for builder_header_start
            for field in self.header_start:
                # tagging the unique field
                if field == self.unique:
                    tmp += '<td class="unique gui">{}</td>'.format(row[field])
                else:
                    tmp += '<td class="gui">{}</td>'.format(row[field])
            # adding all tds for builder_header_dynamic
            for field in self.type_attributes:
                if field not in self.dynamic_table.objects.list_of_type_attributes(id_main=row['id']):
                    tmp += '<td class="gui"></td>'
                else:
                    for row_dynamic in _query_dynamic:
                        if field == row_dynamic['type_attribute']:
                            tmp += '<td class="gui">{}</td>'.format(row_dynamic['value'])
            # adding all tds for builder_header_end
            tmp += '<td>{}</td>'.format(row['version'])
            # close table
            tmp += '</tr>'
            # append table row
            _list.append(tmp)
        return _list

    @property
    def export(self):
        _query = self.query(order_by=self.order_by, type=self.type)
        _list = list()
        for row in _query:
            _query_dynamic = self.query_dynamic(row['id'])
            _tuple = tuple()
            for field in self.header_start:
                _tuple += (row[field], )

            for field in self.type_attributes:
                if field not in self.dynamic_table.objects.list_of_type_attributes(id_main=row['id']):
                    _tuple += ('', )
                else:
                    for row_dynamic in _query_dynamic:
                        if field == row_dynamic['type_attribute']:
                            _tuple += (row_dynamic['value'], )
            _tuple += (row['version'], )
            _list.append(_tuple)
        _return = [tuple(custom.capitalize(self.header_start)) +
                   tuple(custom.capitalize(self.type_attributes)) +
                   ('Version', )]
        for row in _list:
            _return.append(row)
        return _return


class GetDynamicAuditTrail(GetStandard):
    def __init__(self, table, dynamic_table, type):
        super().__init__(table)
        self.type = type

    def table_row_head_total(self, row, query_dynamic):
        # TODO #59
        if self.verify_checksum(row=row):
            for row in query_dynamic:
                if not self.verify_checksum_dynamic(row=row):
                    return '<tr class="tmp_audit_trail" style="color: red">'
            return '<tr class="tmp_audit_trail">'
        else:
            return '<tr class="tmp_audit_trail" style="color: red">'

    def get(self, **dic):
        _query = self.query(order_by=self.order_by, type=self.type)
        _list = list()
        for row in _query:
            _query_dynamic = self.query_dynamic(row['id'])
            tmp = self.table_row_head_total(row=row, query_dynamic=_query_dynamic)
            # adding all tds for builder_header_start
            for field in self.header_start:
                # tagging the unique field
                if field == self.unique:
                    tmp += '<td class="unique gui">{}</td>'.format(row[field])
                else:
                    tmp += '<td class="gui">{}</td>'.format(row[field])
            # adding all tds for builder_header_dynamic
            for field in self.type_attributes:
                if field not in self.dynamic_table.objects.list_of_type_attributes(id_main=row['id']):
                    tmp += '<td class="gui"></td>'
                else:
                    for row_dynamic in _query_dynamic:
                        if field == row_dynamic['type_attribute']:
                            tmp += '<td class="gui">{}</td>'.format(row_dynamic['value'])
            # adding all tds for builder_header_end
            tmp += '<td>{}</td>'.format(row['version'])
            # close table
            tmp += '</tr>'
            # append table row
            _list.append(tmp)
        return _list


class TableManipulation(Master):
    def __init__(self, table, table_audit_trail=None):
        super().__init__(table)
        self.table_audit_trail = table_audit_trail
        self._json = str()
        self._dict = dict()
        self._id = int
        self._user = str()
        self._version = None
        self._unique_value = None
        self.unique_old = self.unique + '_old'

    @property
    def json(self):
        return self._json

    @json.setter
    def json(self, value):
        self._json = value

    @property
    def dict(self):
        return self._dict

    @dict.setter
    def dict(self, value):
        self._dict = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def unique_value(self):
        return self._unique_value

    @unique_value.setter
    def unique_value(self, value):
        self._unique_value = value

    @property
    def header(self):
        _header = self._table_header
        _header.remove('id')
        try:
            _header.remove('version')
            _header.remove('last_login')
        except ValueError:
            pass
        _header.remove('checksum')
        return _header

    def parsing(self, **kwargs):
        """Function to parse passed dict to generate json string, generate checksum and result dict for return. 

            :param kwargs: custom table fields 
            :type kwargs: str/int/float

            :returns: checksum
            :rtype: str
        """
        # declare empty dictionary and string to fill by parser
        _dict = dict()
        _json = str()
        # check that all fields have been passed as arguments
        for field in self.header:
            if field in kwargs:
                # add field value to temporary dictionary
                _dict[field] = kwargs[field] if field == 'duration' else '' if kwargs[field] is None \
                    else '' if kwargs[field] == 'None' else str(kwargs[field])
                # else str(kwargs[field]) if type(kwargs[field]) is object else kwargs[field]
                # create json string for checksum
                _json += '{}:{};'.format(field, '' if kwargs[field] is None else kwargs[field])
            else:
                # raise error
                message = 'Field "{}" is missing in argument list.'.format(field)
                raise NameError(message)
        # add version
        if self.version is not None:
            _dict['version'] = self.version
            _json += 'version:{};'.format(self.version)
        self.json = _json
        self.dict = _dict
        # add secret to json string
        to_hash = _json + str(SECRET)
        # generate checksum
        checksum = custom.generate_checksum(to_hash=to_hash)
        return checksum

    def new(self, user, **kwargs):
        """Function to create new standard table records. 

            :param user: user id/name
            :type user: str
            :param kwargs: custom table fields 
            :type kwargs: str/int/float

            :returns: flag + message
            :rtype: bool, str
        """
        # verify if entry already exists
        if self.table.objects.exist(kwargs[self.unique]) is False:
            self.user = user
            self.unique_value = kwargs[self.unique]
            self.version = 1
            checksum = self.parsing(**kwargs)
            try:
                entry = self.table.objects.create(**self.dict, checksum=checksum)
                self.timestamp = timezone.now()
                self.id = entry.id
                # success message + log entry
                message = 'Record "{}" has been created.'.format(kwargs[self.unique])
                log.info(message)
            except:
                # raise error
                message = 'Could not create record "{}".'.format(kwargs[self.unique])
                raise NameError(message)
            else:
                return True, message
        else:
            # return false and error message + log entry
            message = 'Record "{}" already exists.'.format(kwargs[self.unique])
            log.info(message)
            return False, message

    def new_log(self, text='log', unique='object', **kwargs):
        """Function to create new log records. 

            :returns: flag
            :rtype: bool
        """
        # parse record data
        checksum = self.parsing(**kwargs)
        try:
            self.table.objects.create(**self.dict, checksum=checksum)
            # success message + log entry
            message = '{} record for "{}" has been created.'.format(text.capitalize(), kwargs[unique])
            log.info(message)
        except:
            # raise error
            message = 'Could not create {} record for "{}".'.format(text, kwargs[unique])
            raise NameError(message)
        else:
            return True

    def new_times(self, **kwargs):
        return self.new_log(text='times', unique='item', **kwargs)

    def new_dynamic(self, user, identifier, main_version, timestamp, **kwargs):
        """Function to create new dynamic table records.

            :param user: user id/name
            :type user: str
            :param identifier: identifier of main object
            :rtype identifier: str
            :param main_version: version of the main object
            :rtype main_version: int
            :param timestamp: timestamp from external
            :rtype timestamp: datetime object
            :param kwargs: custom table fields
            :type kwargs: str/int/float

            :returns: flag + message
            :rtype: bool, str
        """
        self.user = user
        self.unique_value = '{} - {}'.format(identifier, kwargs['type_attribute'])
        checksum = self.parsing(**kwargs)
        try:
            self.table.objects.create(**self.dict, checksum=checksum)
            self.timestamp = timestamp
            self.id = main_version
            # success message + log entry
            message = 'Record "{}" has been created.'.format(self.unique_value)
            log.info(message)
        except:
            # raise error
            message = 'Could not create record "{}".'.format(self.unique_value)
            raise NameError(message)
        else:
            return True, message

    def new_boxing(self, **kwargs):
        return self.new_log(text='boxing', unique='box', **kwargs)

    def clear_boxing(self, **kwargs):
        """Dedicated function to clear boxing records. WARNING, does not suit framework!

            :return: flag
            :rtype: bool
        """
        try:
            # parse record data
            checksum = self.parsing(**kwargs)
            self.table.objects.filter(box=kwargs['box'],
                                      position=kwargs['position']).update(**self.dict, checksum=checksum)
            # success message + log entry
            message = 'Boxing record for "{}" has been cleared.'.format(kwargs['object'])
            log.info(message)
        except:
            # raise error
            message = 'Could not clear boxing record for "{}".'.format(kwargs['object'])
            raise NameError(message)
        else:
            return True

    def edit_boxing(self, **kwargs):
        """Dedicated function to update boxing records. WARNING, does not suit framework!

            :return: flag
            :rtype: bool
        """
        try:
            if self.table.objects.exist_object(kwargs['object']):
                old = self.table.objects.filter(object=kwargs['object']).get()
                old_kwargs = {
                    'object': '',
                    'position': old.position,
                    'box': old.box
                }
                checksum = self.parsing(**old_kwargs)
                self.table.objects.filter(object=old.object).update(**self.dict, checksum=checksum)
                # success message + log entry
                message = 'Boxing record for "{}" has been updated.'.format(old.object)
                log.info(message)
            # parse record data
            checksum = self.parsing(**kwargs)
            self.table.objects.filter(box=kwargs['box'],
                                      position=kwargs['position']).update(**self.dict, checksum=checksum)
            # success message + log entry
            message = 'Boxing record for "{}" has been created.'.format(kwargs['object'])
            log.info(message)
        except:
            # raise error
            message = 'Could not create boxing record for "{}".'.format(kwargs['object'])
            raise NameError(message)
        else:
            return True

    def edit(self, user, **kwargs):
        """Function to update existing standard table records. 

            :param user: user id/name
            :type user: str
            :param kwargs: custom table fields 
            :type kwargs: str/int/float

            :returns: flag + message
            :rtype: bool, str
        """
        # verify if record still exists
        if self.table.objects.exist(kwargs[self.unique]):
            self.user = user
            self.unique_value = kwargs[self.unique]
            # get record version and increment
            self.version = self.record_version(self.unique_value) + 1
            checksum = self.parsing(**kwargs)
            try:
                filter_dic = {self.unique: self.unique_value}
                self.table.objects.filter(**filter_dic).update(**self.dict, checksum=checksum)
                self.timestamp = timezone.now()
                self.id = self.record_id(self.unique_value)
                # success message + log entry
                message = 'Record "{}" has been updated.'.format(kwargs[self.unique])
                log.info(message)
            except:
                # raise error
                message = 'Could not update record "{}".'.format(kwargs[self.unique])
                raise NameError(message)
            else:
                return True, message
        else:
            # return false and error message + log entry
            message = 'Record "{}" is not existing.'.format(kwargs[self.unique])
            log.warning(message)
            return False, message

    def edit_dynamic(self, user, identifier, main_version, timestamp, **kwargs):
        self.unique_value = '{} - {}'.format(identifier, kwargs['type_attribute'])
        keys = ['id_main', 'type_attribute']
        values = [kwargs['id_main'], kwargs['type_attribute']]
        filter_dic = dict(zip(keys, values))
        if self.table.objects.filter(**filter_dic).exists():
            self.user = user
            checksum = self.parsing(**kwargs)
            # self.version = main_version
            try:
                self.table.objects.filter(**filter_dic).update(**self.dict, checksum=checksum)
                self.timestamp = timestamp
                self.id = main_version
                # success message + log entry
                message = 'Record "{}" has been updated.'.format(self.unique_value)
                log.info(message)
            except:
                # raise error
                message = 'Could not update record "{}".'.format(self.unique_value)
                raise NameError(message)
            else:
                return True, message
        else:
            # error message + log entry
            message = 'Record "{}" is not existing. Therefore adding new record.'.format(self.unique_value)
            log.info(message)
            result, message = self.new_dynamic(user=user, identifier=identifier, main_version=main_version,
                                               timestamp=timestamp, **kwargs)
            return result, message

    def new_at(self, user, **kwargs):
        result, message = self.new(user=user, **kwargs)
        if result:
            if self.audit_trail(action='Create'):
                return True, 'Success!'
        else:
            return result, message

    def new_dynamic_at(self, user, identifier, main_version, timestamp, **kwargs):
        result, message = self.new_dynamic(user=user, identifier=identifier, main_version=main_version,
                                           timestamp=timestamp, **kwargs)
        if result:
            if self.audit_trail(action='Create'):
                return True, 'Success!'
        else:
            return result, message

    def edit_dynamic_at(self, user, identifier, main_version, timestamp, **kwargs):
        result, message = self.edit_dynamic(user=user, identifier=identifier, main_version=main_version,
                                            timestamp=timestamp, **kwargs)
        if result:
            if self.audit_trail(action='Update'):
                return True, 'Success!'
        else:
            return result, message

    def new_identifier_at(self, user, prefix, **kwargs):
        result, message = self.new(user=user, **kwargs)
        if result:
            # generate identifier for new table entry
            _identifier = custom.identifier(prefix=prefix, table_id=self.id)
            if prefix == 'S' or prefix == 'B' or prefix == 'L' or prefix == 'R':
                # generate new json string with new unique value generated by identifier
                self.json = '{}:{};{}'.format(self.unique, _identifier, self.json.split(';', 1)[1])
                self.dict[self.unique] = _identifier
            else:
                # raise error
                message = 'Could not generate identifier for id "{}". Prefix did not match "S" / "B" / "L".' \
                    .format(self.id)
                raise NameError(message)
            # add secret to json string
            to_hash_new = self.json + str(SECRET)
            # generate checksum
            checksum_new = custom.generate_checksum(to_hash=to_hash_new)
            try:
                # generate arguments for update
                _dict = {self.unique: _identifier}
                self.table.objects.filter(id=self.id).update(checksum=checksum_new, **_dict)
                # return true and success message + log entry
                message = 'Entry for "{}" has automatically been updated to "{}".'.format(self.unique_value,
                                                                                          _identifier)
                log.info(message)
                self.unique_value = _identifier
            except:
                # raise error
                message = 'Could not automatically update entry for "{}".'.format(self.unique_value)
                raise NameError(message)
            if self.audit_trail(action='Create'):
                return True, self.unique_value
        else:
            return result, message

    def audit_trail(self, action):
        """Function to create new standard audit trail records. 

            :param action: audit trail action ("Create" / "Update" / "Delete") 
            :type action: str

            :returns: flag
            :rtype: bool
        """
        # create json string
        to_hash = '{}action:{};user:{};timestamp:{};{}'.format(self.json, action, self.user, self.timestamp, SECRET)
        # generate checksum
        checksum = custom.generate_checksum(to_hash=to_hash)
        try:
            self.table_audit_trail.objects.create(**self.dict, id_ref=self.id, action=action, user=self.user,
                                                  timestamp=self.timestamp, checksum=checksum)
            # return true and success message + log entry
            message = 'Audit trail record for "{}" has been created.'.format(self.unique_value)
            log.info(message)
        except:
            # raise error
            message = 'Could not create audit trail record for "{}".'.format(self.unique_value)
            raise NameError(message)
        else:
            return True

    def edit_at(self, user, **kwargs):
        result, message = self.edit(user=user, **kwargs)
        if result:
            if self.audit_trail(action='Update'):
                return True, 'Success!'
        else:
            return result, message

    def prepare(self, query):
        _dic = dict()
        for field in self.header:
            _dic[field] = query[0][field]
        return _dic

    def delete_multiple(self, user, records):
        # setting the user for identification
        self.user = user
        # step through every record to delete
        for record in records:
            if self.delete(record):
                self.audit_trail(action='Delete')
            else:
                pass
        return True

    def delete_at(self, user, record):
        # setting the user for identification
        self.user = user
        if self.delete(record):
            return self.audit_trail(action='Delete')
        else:
            return False

    def delete(self, record):
        # check if record is existing in the db
        if self.table.objects.exist(record):
            self.unique_value = record
            _dic = {self.unique: record}
            # query for record to delete
            _query = self.query(**_dic)
            # set id for audit trail entry
            self.id = _query[0]["id"]
            # parse record values to generate json string and dict to pass for audit trail
            self.version = _query[0]["version"]
            self.parsing(**self.prepare(_query))
            # delete record
            try:
                self.table.objects.filter(**_dic).delete()
                self.timestamp = timezone.now()
                # log entry
                message = 'Record "{}" has been deleted.'.format(record)
                log.info(message)
            except:
                # raise error
                message = 'Could not delete record "{}".'.format(record)
                raise NameError(message)
            else:
                return True
        else:
            return False

    def delete_dynamic(self, id_main, identifier, timestamp):
        query = self.table.objects.filter(id_main=id_main)
        print('query: ', query)
        for record in query:
            print('record: ', record)
            self.unique_value = '{} - {}'.format(identifier, record.type_attribute)
            print('unique value: ', self.unique_value)
            self.id = record.id
            self.parsing(**self.prepare(record))
            try:
                self.table.object.filter(id=record.id).delete()
                self.timestamp = timestamp
                # log entry
                message = 'Record "{}" has been deleted.'.format(self.unique_value)
                log.info(message)
            except:
                # raise error
                message = 'Could not delete record "{}".'.format(self.unique_value)
                raise NameError(message)
        return True

    def movement(self, user, unique, new_location):
        # get actual information
        initial_location = '' if models.RTD.objects.location(unique=unique) is None else models.RTD.objects.location(
            unique=unique)
        # define user
        self.user = user
        # create movement log entry
        self.timestamp = timezone.now()
        method = models.RTD.objects.method(unique=unique)
        # only proceed if log record was written
        if self.new_log(user=user, object=unique, type=method, initial_location=initial_location,
                        new_location=new_location, timestamp=self.timestamp):
            # define new object to manipulate table times
            manipulation = TableManipulation(table=models.Times)
            # check if first move, then just move
            if initial_location != '':
                # if samples are moved
                if method == 'sample':
                    # reference id
                    id_ref = models.Samples.objects.id(unique=unique)
                    # get condition of new location
                    new_condition = models.Locations.objects.condition(new_location)
                    initial_condition = models.Locations.objects.condition(initial_location)
                    account = models.Samples.objects.account(unique=unique)
                    freeze_condition, thaw_condition = models.FreezeThawAccounts.objects.conditions(account)
                    if new_condition != initial_condition:
                        # determine latest id second (by counting rows, could be done via max of id_second value)
                        id_second = manipulation.table.objects.filter(id_ref=id_ref).count()
                        # freeze
                        if new_condition == freeze_condition:
                            method = 'freeze'
                        # thaw
                        elif new_condition == thaw_condition:
                            method = 'thaw'
                        manipulation.new_times(id_ref=id_ref, item=unique, method=method, time=self.timestamp,
                                               id_second=id_second + 1, duration=None, )
                        old_timestamp = manipulation.table.objects.time(id_ref=id_ref, id_second=id_second)
                        duration = self.timestamp - old_timestamp
                        # Update duration
                        try:
                            manipulation.table.objects.filter(id_ref=id_ref,
                                                              id_second=id_second).update(duration=duration)
                            # success message + log entry
                            message = 'Times record "{}" id second "{}" has been updated.'.format(unique, id_second)
                            log.info(message)
                        except:
                            # raise error
                            message = 'Could not update times record "{}" id second "{}".'.format(unique, id_second)
                            raise NameError(message)
                        else:
                            return True, message
                    else:
                        # message + log entry
                        message = 'Initial condition of "{}" is equal to new condition.'.format(unique)
                        log.info(message)
                        return True, message
                elif method == 'box':
                    # message + log entry
                    message = 'Box "{}" has been moved.'.format(unique)
                    log.info(message)
                    return True, message
            else:
                # if samples are moved
                if method == 'sample':
                    # reference id
                    id_ref = models.Samples.objects.id(unique=unique)
                    account = models.Samples.objects.account(unique=unique)
                    freeze_condition, thaw_condition = models.FreezeThawAccounts.objects.conditions(account)
                    new_condition = models.Locations.objects.condition(new_location)
                    manipulation.new_times(id_ref=id_ref, item=unique, time=self.timestamp, id_second=1,
                                           duration=None,
                                           method=('freeze' if new_condition == freeze_condition else 'thaw'))
                    # message + log entry
                    message = 'First movement for "{}" has been executed.'.format(unique)
                    log.info(message)
                    return True, message
                elif method == 'box':
                    # message + log entry
                    message = 'Box "{}" has been moved.'.format(unique)
                    log.info(message)
                    return True, message

    def move(self, user, obj, method, initial_location, new_location, timestamp):
        return self.new_log(user=user, object=obj, method=method, initial_location=initial_location,
                            new_location=new_location, timestamp=timestamp)


def new_login_log(username, action, method='manual', active=None):
    """Function to create new login log records. 

        :returns: status about log record 
        :rtype: bool
    """
    manipulation = TableManipulation(table=models.LoginLog)
    if active is None:
        active = models.Users.objects.get(username=username).is_active
    try:
        query = models.LoginLog.objects.filter(user=username).order_by('-id')[0]
        if query.action == 'attempt' and active is True and query.active is False:
            attempts = 1
        elif query.action == 'attempt':
            attempts = query.attempts + 1
        else:
            attempts = 1
    except IndexError:
        attempts = 1
    manipulation.new_log(unique='user', user=username, action=action,
                         attempts=attempts, method=method, active=active, timestamp=timezone.now())
    if attempts == 4 and action == 'attempt':
        models.Users.objects.set_is_active(username=username, operation_user=username, is_active=False)


def html_and_data(context, get_standard, get_audit_trail, form_render_new, form_render_edit):
    # html data
    context['modal_js_get'] = get_standard.js_get
    context['modal_js_post'] = get_standard.js_post
    context['modal_new'] = form_render_new
    context['modal_edit'] = form_render_edit
    context['header'] = get_standard.html_header
    context['header_audit_trail'] = get_audit_trail.html_header
    # pass verified query
    context['query'] = get_standard.get()
    context['reagents'] = models.Types.objects.filter(affiliation='Reagents').values_list('type', flat=True)
    context['samples'] = models.Types.objects.filter(affiliation='Samples').values_list('type', flat=True)
    return context
