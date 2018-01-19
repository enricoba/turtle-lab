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
        self.margin = self.pixel(3)  # 3 mm margin top/bottom/left/right
        self.width = self.pixel(62)  # 62 mm width
        self.height = self.pixel(29)  # 29 mm height
        self.json_b = self._get_json_b
        self.json_c = self._get_json_c
        self.json_inv_b = self._get_json_inv_b
        self._bar = 4  # 5 pixel
        self.quiet_zone = self.margin + 10 * self.bar
        self._code = str()
        self._font_size = '22px'
        self._font_family = 'arial'
        self._svg = str()
        self._svg_url = str()

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
    def svg_url(self):
        return self._svg_url

    @svg_url.setter
    def svg_url(self, value):
        self._svg_url = settings.MEDIA_URL + value

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
        return os.path.isfile(self.svg)

    def location(self, unique, version):
        """Function to create a standard location label. 

            :param unique: unique value of location for creating label
            :type unique: str
            :param version: location entry version
            :type version: int
            :returns: flag + path for printing
            :rtype: bool, str
        """
        # define variables for location label
        self.font_size = '80px'
        # _path must match exactly that pattern: no leading slash, but must end with slash
        _path = 'locations/'
        # create .svg and .pdf paths and file names
        self.svg = _path + '{}_v-{}.svg'.format(unique, version)
        self.svg_url = _path + '{}_v-{}.svg'.format(unique, version)

        # check if label already exists
        if self.exists:
            log.info('SVG label file for location "{}" version "{}" already exists. Using existing SVG for printing.'
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
                message = 'SVG label file "{}" for location "{}" version "{}" has successfully been created.' \
                    .format(self.svg, unique, version)
                log.info(message)
            except:
                # raise error
                message = 'Could not create SVG label file for location "{}" version "{}".'.format(unique, version)
                raise NameError(message)
            # log entries for successful pdf generation
            return True, self.svg_url


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
    def __init__(self, table):
        super().__init__(table)

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
        _header.append('integrity')
        return custom.capitalize(_header)

    @property
    def js_get(self):
        _return = list()
        for item in self.js_header:
            if item == 'permissions':
                _return.append('var v_{0} = $(myDomElement).find("#id_{0}").val().toString();'.format(item))
            elif item == 'is_active':
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

    @property
    def table_row_head(self):
        return '<tr>'

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
        checksum = self.table.objects.checksum(row[self.unique])
        try:
            return argon2.verify(to_verify, checksum)
        except TypeError or ValueError:
            # return false + log entry
            message = 'Checksum for "{}" of table "{}" was not correct.\nData integrity is at risk!'.\
                format(row[self.unique], self.table_name)
            log.warning(message)
            return False

    def generate_integrity_column(self, row=None):
        if self.verify_checksum(row=row):
            _tmp = '<td><i class="fa fa-check-circle" style="color: green"></td>'
        else:
            _tmp = '<td><i class="fa fa-close" style="color: red"></i></td>'
        return _tmp

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
            tmp = self.table_row_head
            for field in self.header:
                # tagging the unique field
                if field == self.unique:
                    tmp += '<td class="unique gui">{}</td>'.format(row[field])
                # formatting the timestamp
                elif field == 'timestamp':
                    tmp += '<td>{}</td>'.format(row[field].strftime("%Y-%m-%d %H:%M:%S %Z %z"))
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
                elif field == 'is_active' or field == 'initial_password' or field == 'active':
                    if row[field]:
                        tmp += '<td><i class="fa fa-check-circle" style="color: green"></td>'
                    else:
                        tmp += '<td><i class="fa fa-minus-circle" style="color: red"></i></td>'
                elif field != self.unique and field != 'version':
                    tmp += '<td class="gui">{}</td>'.format(row[field])
                else:
                    tmp += '<td>{}</td>'.format(row[field])
            # add verify column
            tmp += self.generate_integrity_column(row=row)
            # close table
            tmp += '</tr>'
            # append table row
            _list.append(tmp)
        return _list


class GetAuditTrail(GetStandard):
    @property
    def header(self):
        _header = self._table_header
        _header.remove('id')
        _header.remove('checksum')
        _header.remove('id_ref')
        return _header

    @property
    def _table_row_head(self):
        return '<tr class="tmp_audit_trail">'

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
            tmp = self._table_row_head
            for field in self.header:
                # formatting the timestamp
                if field == 'timestamp':
                    tmp += '<td>{}</td>'.format(row[field].strftime("%Y-%m-%d %H:%M:%S %Z %z"))
                # formatting duration fields
                elif field == 'freeze_time':
                    tmp += '<td>{}</td>'.format(custom.timedelta_reverse(uom=row['freeze_uom'], dt=row[field]))
                # formatting duration fields
                elif field == 'thaw_time':
                    tmp += '<td>{}</td>'.format(custom.timedelta_reverse(uom=row['thaw_uom'], dt=row[field]))
                elif field == 'is_active' or field == 'initial_password':
                    if row[field]:
                        tmp += '<td><i class="fa fa-check-circle" style="color: green"></td>'
                    else:
                        tmp += '<td><i class="fa fa-minus-circle" style="color: red"></i></td>'
                else:
                    tmp += '<td>{}</td>'.format(row[field])
            # add verify column
            tmp += self.generate_integrity_column(row=row)
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
            tmp = self.table_row_head
            for field in self.header:
                # locations can be empty
                if field == 'location':
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


class TableManipulation(Master):
    def __init__(self, table, table_audit_trail=None):
        super().__init__(table)
        self.table_audit_trail = table_audit_trail
        self._json = str()
        self._dict = dict()
        self._id = int
        self._user = str()
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

    def parsing(self, version=None, **kwargs):
        """Function to parse passed dict to generate json string, generate checksum and result dict for return. 

            :param version: record version 
            :type version: int
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
                    else str(kwargs[field])
                # else str(kwargs[field]) if type(kwargs[field]) is object else kwargs[field]
                # create json string for checksum
                _json += '{}:{};'.format(field, '' if kwargs[field] is None else kwargs[field])
            else:
                # raise error
                message = 'Field "{}" is missing in argument list.'.format(field)
                raise NameError(message)
        # add version
        if version is not None:
            version = version
            _dict['version'] = version
            _json += 'version:{};'.format(version)
        self.json = _json
        self.dict = _dict
        # print("json: ", _json)
        # print("dict: ", _dict)
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
            checksum = self.parsing(version=1, **kwargs)
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
            version = self.record_version(self.unique_value) + 1
            checksum = self.parsing(version=version, **kwargs)
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

    def new_at(self, user, **kwargs):
        result, message = self.new(user=user, **kwargs)
        if result:
            if self.audit_trail(action='Create'):
                return True, 'Success!'
        else:
            return result, message

    def new_identifier_at(self, user, prefix, **kwargs):
        result, message = self.new(user=user, **kwargs)
        if result:
            # generate identifier for new table entry
            _identifier = custom.identifier(prefix=prefix, table_id=self.id)
            if prefix == 'S' or prefix == 'B' or prefix == 'L':
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
                return True, 'Success!'
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
            self.parsing(version=_query[0]["version"], **self.prepare(_query))
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

    def movement(self, user, unique, new_location):
        # get actual information
        initial_location = '' if models.RTD.objects.location(unique=unique) is None else models.RTD.objects.location(
            unique=unique)
        # verify if new location is actual location
        if initial_location != str(new_location):
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
        else:
            # message + log entry
            message = 'Movement for "{}" failed, actual location is equal to new location.'.format(unique)
            log.info(message)
            return False, message


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
        if query.action == 'attempt':
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
    context['modal_new'] = [form_render_new.as_p()]
    context['modal_edit'] = [form_render_edit.as_p()]
    context['header'] = get_standard.html_header
    context['header_audit_trail'] = get_audit_trail.html_header
    # pass verified query
    context['query'] = get_standard.get()
    return context
