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
import logging

# django imports
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

# app imports
import lab.custom as custom

# secret key
SECRET = settings.SECRET

# define logger
log = logging.getLogger(__name__)


##########
# GLOBAL #
##########


CHECKSUM_LENGTH = 200
UNIQUE_LENGTH = 50
ACTION_LENGTH = 6
GENERATED_LENGTH = 40
LABEL_LENGTH = 50
PASSWORD_LENGTH = 128
DEFAULT = 255


class GlobalManager(models.Manager):
    def version(self, unique):
        dic = {self.unique: unique}
        return self.filter(**dic)[0].version

    def exist(self, unique):
        dic = {self.unique: unique}
        return self.filter(**dic).exists()

    def id(self, unique):
        dic = {self.unique: unique}
        return self.filter(**dic)[0].id

    def checksum(self, unique):
        dic = {self.unique: unique}
        return self.filter(**dic)[0].checksum


class GlobalAuditTrailManager(models.Manager):
    def checksum(self, unique):
        return self.filter(id=unique)[0].checksum

    @property
    def unique(self):
        return 'id'


###############
# CONDITIONS #
###############

# manager
class ConditionsManager(GlobalManager):
    @property
    def unique(self):
        return 'condition'


# table
class Conditions(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    condition = models.CharField(max_length=UNIQUE_LENGTH, unique=True)
    # system fields
    version = models.IntegerField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = ConditionsManager()

    def __str__(self):
        return self.condition


# audit trail manager
class ConditionsAuditTrailManager(GlobalAuditTrailManager):
    pass


# audit trail table
class ConditionsAuditTrail(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    id_ref = models.IntegerField()
    # custom fields
    condition = models.CharField(max_length=UNIQUE_LENGTH)
    # system fields
    version = models.IntegerField()
    action = models.CharField(max_length=ACTION_LENGTH)
    user = models.CharField(max_length=UNIQUE_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = ConditionsAuditTrailManager()


#############
# LOCATIONS #
#############

# manager
class LocationsManager(GlobalManager):
    @property
    def unique(self):
        return 'location'

    def condition(self, unique):
        dic = {self.unique: unique}
        return self.filter(**dic)[0].condition

    def locations_by_type(self, type):
        condition = Types.objects.storage_condition(type=type)
        if condition:
            try:
                return self.filter(condition=condition).all()
            except IndexError:
                return False
        else:
            return False

    def ref_check(self, unique):
        try:
            return self.filter(condition=unique).exists()
        except IndexError:
            return False

    def ref_items(self, unique):
        try:
            return self.filter(condition=unique).values_list(self.unique, flat=True)
        except IndexError:
            return None


# table
class Locations(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    location = models.CharField(max_length=GENERATED_LENGTH, unique=True)
    name = models.CharField(max_length=UNIQUE_LENGTH)
    condition = models.CharField(max_length=UNIQUE_LENGTH)
    max_boxes = models.CharField(max_length=UNIQUE_LENGTH)
    # system fields
    version = models.IntegerField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = LocationsManager()

    def __str__(self):
        if self.name == '':
            _return = self.location
        else:
            _return = '{} ({})'.format(self.location, self.name)
        return _return


# audit trail manager
class LocationsAuditTrailManager(GlobalAuditTrailManager):
    pass


# audit trail table
class LocationsAuditTrail(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    id_ref = models.IntegerField()
    # custom fields
    location = models.CharField(max_length=GENERATED_LENGTH)
    name = models.CharField(max_length=UNIQUE_LENGTH)
    condition = models.CharField(max_length=UNIQUE_LENGTH)
    max_boxes = models.CharField(max_length=UNIQUE_LENGTH)
    # system fields
    version = models.IntegerField()
    action = models.CharField(max_length=ACTION_LENGTH)
    user = models.CharField(max_length=UNIQUE_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = LocationsAuditTrailManager()


#########
# TYPES #
#########


AFFILIATIONS = (('Reagents', 'Reagents'),
                ('Samples', 'Samples'))


# manager
class TypesManager(GlobalManager):
    @property
    def unique(self):
        return 'type'

    @property
    def reagents(self):
        return self.filter(affiliation='Reagents')

    @property
    def samples(self):
        return self.filter(affiliation='Samples')

    def get_affiliation(self, type):
        try:
            return self.filter(type=type)[0].affiliation
        except IndexError:
            return False

    def storage_condition(self, type):
        try:
            return self.filter(type=type)[0].storage_condition
        except IndexError:
            return False


# table
class Types(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    type = models.CharField(max_length=GENERATED_LENGTH, unique=True)
    affiliation = models.CharField(max_length=UNIQUE_LENGTH, choices=AFFILIATIONS)
    storage_condition = models.CharField(max_length=UNIQUE_LENGTH)
    usage_condition = models.CharField(max_length=UNIQUE_LENGTH)
    # system fields
    version = models.IntegerField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = TypesManager()

    def __str__(self):
        return self.type


# audit trail manager
class TypesAuditTrailManager(GlobalAuditTrailManager):
    pass


# audit trail table
class TypesAuditTrail(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    id_ref = models.IntegerField()
    # custom fields
    type = models.CharField(max_length=GENERATED_LENGTH)
    affiliation = models.CharField(max_length=UNIQUE_LENGTH)
    storage_condition = models.CharField(max_length=UNIQUE_LENGTH)
    usage_condition = models.CharField(max_length=UNIQUE_LENGTH)
    # system fields
    version = models.IntegerField()
    action = models.CharField(max_length=ACTION_LENGTH)
    user = models.CharField(max_length=UNIQUE_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = TypesAuditTrailManager()


###################
# TYPE ATTRIBUTES #
###################

# manager
class TypeAttributesManager(GlobalManager):
    @property
    def unique(self):
        return 'column'

    def columns_as_list(self, type):
        try:
            return list(self.filter(type=type).order_by('id').values_list('column', flat=True))
        except IndexError:
            return list()

    def all_list_exchanged(self, type):
        try:
            query = list(self.filter(type=type).order_by('id'))
            for row in query:
                if row.list_values:
                    row.list_values = row.list_values.split(',')
            return query
        except IndexError:
            return list()


# table
class TypeAttributes(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    column = models.CharField(max_length=UNIQUE_LENGTH, unique=True)
    type = models.CharField(max_length=UNIQUE_LENGTH)
    list_values = models.CharField(max_length=DEFAULT)
    default_value = models.CharField(max_length=DEFAULT)
    mandatory = models.BooleanField()
    # system fields
    version = models.IntegerField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = TypeAttributesManager()

    def __str__(self):
        return self.column


# audit trail manager
class TypeAttributesAuditTrailManager(GlobalAuditTrailManager):
    pass


# audit trail table
class TypeAttributesAuditTrail(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    id_ref = models.IntegerField()
    # custom fields
    column = models.CharField(max_length=UNIQUE_LENGTH)
    type = models.CharField(max_length=UNIQUE_LENGTH)
    list_values = models.CharField(max_length=DEFAULT)
    default_value = models.CharField(max_length=DEFAULT)
    mandatory = models.BooleanField()
    # system fields
    version = models.IntegerField()
    action = models.CharField(max_length=ACTION_LENGTH)
    user = models.CharField(max_length=UNIQUE_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = TypeAttributesAuditTrailManager()


####################
# DYNAMIC REAGENTS #
####################

# manager
class DynamicReagentsManager(GlobalManager):
    @property
    def unique(self):
        return 'id'

    def list_of_type_attributes(self, id_main):
        try:
            return list(self.filter(id_main=id_main).order_by('id').values_list('type_attribute', flat=True))
        except IndexError:
            return list()


# table
class DynamicReagents(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    id_main = models.IntegerField()
    # custom fields
    type_attribute = models.CharField(max_length=UNIQUE_LENGTH)
    value = models.CharField(max_length=DEFAULT)
    # system fields
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = DynamicReagentsManager()


# audit trail manager
class DynamicReagentsAuditTrailManager(GlobalAuditTrailManager):
    def list_of_type_attributes(self, id_main, version):
        try:
            return list(self.filter(id_main=id_main, id_ref=version).order_by('id').
                        values_list('type_attribute', flat=True))
        except IndexError:
            return list()


# audit trail table
class DynamicReagentsAuditTrail(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    id_ref = models.IntegerField()
    # custom fields
    id_main = models.IntegerField()
    type_attribute = models.CharField(max_length=UNIQUE_LENGTH)
    value = models.CharField(max_length=DEFAULT)
    # system fields
    action = models.CharField(max_length=ACTION_LENGTH)
    user = models.CharField(max_length=UNIQUE_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = DynamicReagentsAuditTrailManager()


#############
# BOX TYPES #
#############


BOX_ALIGNMENT = (('Horizontal', 'Horizontal'),
                 ('Vertical', 'Vertical'))


# manager
class BoxTypesManager(GlobalManager):
    @property
    def unique(self):
        return 'box_type'

    @property
    def default(self):
        dic = {'default': True}
        return self.filter(**dic)

    def max(self, unique):
        dic = {self.unique: unique}
        rows = custom.transform_box_type_figures(self.filter(**dic)[0].rows)
        columns = custom.transform_box_type_figures(self.filter(**dic)[0].columns)
        return rows * columns


# table
class BoxTypes(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    box_type = models.CharField(max_length=UNIQUE_LENGTH, unique=True)
    alignment = models.CharField(max_length=UNIQUE_LENGTH, choices=BOX_ALIGNMENT)
    rows = models.CharField(max_length=UNIQUE_LENGTH)
    columns = models.CharField(max_length=UNIQUE_LENGTH)
    default = models.BooleanField()
    # system fields
    version = models.IntegerField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = BoxTypesManager()

    def __str__(self):
        return self.box_type


# audit trail manager
class BoxTypesAuditTrailManager(GlobalAuditTrailManager):
    pass


# audit trail table
class BoxTypesAuditTrail(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    id_ref = models.IntegerField()
    # custom fields
    box_type = models.CharField(max_length=UNIQUE_LENGTH)
    alignment = models.CharField(max_length=UNIQUE_LENGTH)
    rows = models.CharField(max_length=UNIQUE_LENGTH)
    columns = models.CharField(max_length=UNIQUE_LENGTH)
    default = models.BooleanField()
    # system fields
    version = models.IntegerField()
    action = models.CharField(max_length=ACTION_LENGTH)
    user = models.CharField(max_length=UNIQUE_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = BoxTypesAuditTrailManager()


#########
# BOXES #
#########


# manager
class BoxesManager(GlobalManager):
    @property
    def unique(self):
        return 'box'

    def count_box_by_type(self, type):
        try:
            return self.filter(type=type).count()
        except IndexError:
            return 0

    def box_by_type(self, type, count=0):
        try:
            return self.filter(type=type).order_by('box')[count].__str__()
        except IndexError:
            return False

    def ref_check(self, unique):
        try:
            return self.filter(box_type=unique).exists()
        except IndexError:
            return False

    def ref_items(self, unique):
        try:
            return self.filter(box_type=unique).values_list(self.unique, flat=True)
        except IndexError:
            return None


# table
class Boxes(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    box = models.CharField(max_length=GENERATED_LENGTH, unique=True)
    name = models.CharField(max_length=UNIQUE_LENGTH)
    type = models.CharField(max_length=UNIQUE_LENGTH)
    box_type = models.CharField(max_length=UNIQUE_LENGTH)
    # system fields
    version = models.IntegerField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = BoxesManager()

    def __str__(self):
        if self.name == '':
            _return = self.box
        else:
            _return = '{} ({})'.format(self.box, self.name)
        return _return


# audit trail manager
class BoxesAuditTrailManager(GlobalAuditTrailManager):
    pass


# audit trail table
class BoxesAuditTrail(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    id_ref = models.IntegerField()
    # custom fields
    box = models.CharField(max_length=GENERATED_LENGTH)
    name = models.CharField(max_length=UNIQUE_LENGTH)
    type = models.CharField(max_length=UNIQUE_LENGTH)
    box_type = models.CharField(max_length=UNIQUE_LENGTH)
    # system fields
    version = models.IntegerField()
    action = models.CharField(max_length=ACTION_LENGTH)
    user = models.CharField(max_length=UNIQUE_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = BoxesAuditTrailManager()


###########
# SAMPLES #
###########


# manager
class SamplesManager(GlobalManager):
    @property
    def unique(self):
        return 'sample'

    def account(self, unique):
        dic = {self.unique: unique}
        return self.filter(**dic)[0].account

    def conditions(self, unique):
        dic = {self.unique: unique}
        account = self.filter(**dic)[0].account
        return [FreezeThawAccounts.objects.filter(account=account)[0].freeze_condition,
                FreezeThawAccounts.objects.filter(account=account)[0].thaw_condition]


# table
class Samples(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    sample = models.CharField(max_length=GENERATED_LENGTH, unique=True)
    name = models.CharField(max_length=UNIQUE_LENGTH)
    account = models.CharField(max_length=UNIQUE_LENGTH)

    # system fields
    version = models.IntegerField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = SamplesManager()

    def __str__(self):
        return self.sample


# audit trail manager
class SamplesAuditTrailManager(GlobalAuditTrailManager):
    pass


# audit trail table
class SamplesAuditTrail(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    id_ref = models.IntegerField()
    # custom fields
    sample = models.CharField(max_length=GENERATED_LENGTH)
    name = models.CharField(max_length=UNIQUE_LENGTH)
    account = models.CharField(max_length=UNIQUE_LENGTH)

    # system fields
    version = models.IntegerField()
    action = models.CharField(max_length=ACTION_LENGTH)
    user = models.CharField(max_length=UNIQUE_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = SamplesAuditTrailManager()


############
# REAGENTS #
############


# manager
class ReagentsManager(GlobalManager):
    @property
    def unique(self):
        return 'reagent'

    def condition(self, reagent):
        try:
            _type = self.filter(reagent=reagent)[0].type
            return Types.objects.storage_condition(type=_type)
        except IndexError:
            return False


# table
class Reagents(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    reagent = models.CharField(max_length=GENERATED_LENGTH, unique=True)
    name = models.CharField(max_length=UNIQUE_LENGTH)
    type = models.CharField(max_length=UNIQUE_LENGTH)

    # system fields
    version = models.IntegerField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = ReagentsManager()

    def __str__(self):
        return self.reagent


# audit trail manager
class ReagentsAuditTrailManager(GlobalAuditTrailManager):
    pass


# audit trail table
class ReagentsAuditTrail(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    id_ref = models.IntegerField()
    # custom fields
    reagent = models.CharField(max_length=GENERATED_LENGTH)
    name = models.CharField(max_length=UNIQUE_LENGTH)
    type = models.CharField(max_length=UNIQUE_LENGTH)

    # system fields
    version = models.IntegerField()
    action = models.CharField(max_length=ACTION_LENGTH)
    user = models.CharField(max_length=UNIQUE_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = ReagentsAuditTrailManager()


############
# ACCOUNTS #
############

TIMES = (('d', 'd - days'),
         ('h', 'h - hours'),
         ('min', 'min - minutes'),
         ('s', 's - seconds'))


# manager
class FreezeThawAccountsManager(GlobalManager):
    @property
    def unique(self):
        return 'account'

    def conditions(self, unique):
        dic = {self.unique: unique}
        return self.filter(**dic)[0].freeze_condition, self.filter(**dic)[0].thaw_condition


# table
class FreezeThawAccounts(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    account = models.CharField(max_length=UNIQUE_LENGTH, unique=True)
    freeze_condition = models.CharField(max_length=UNIQUE_LENGTH)
    freeze_time = models.DurationField()
    freeze_uom = models.CharField(max_length=GENERATED_LENGTH, choices=TIMES)
    thaw_condition = models.CharField(max_length=UNIQUE_LENGTH)
    thaw_time = models.DurationField()
    thaw_uom = models.CharField(max_length=GENERATED_LENGTH, choices=TIMES)
    thaw_count = models.IntegerField()
    # system fields
    version = models.IntegerField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = FreezeThawAccountsManager()

    def __str__(self):
        return self.account


# audit trail manager
class FreezeThawAccountsAuditTrailManager(GlobalAuditTrailManager):
    pass


# audit trail table
class FreezeThawAccountsAuditTrail(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    id_ref = models.IntegerField()
    # custom fields
    account = models.CharField(max_length=UNIQUE_LENGTH)
    freeze_condition = models.CharField(max_length=UNIQUE_LENGTH)
    freeze_time = models.DurationField()
    freeze_uom = models.CharField(max_length=GENERATED_LENGTH, choices=TIMES)
    thaw_condition = models.CharField(max_length=UNIQUE_LENGTH)
    thaw_time = models.DurationField()
    thaw_uom = models.CharField(max_length=GENERATED_LENGTH, choices=TIMES)
    thaw_count = models.IntegerField()
    # system fields
    version = models.IntegerField()
    action = models.CharField(max_length=ACTION_LENGTH)
    user = models.CharField(max_length=UNIQUE_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = FreezeThawAccountsAuditTrailManager()


################
# MOVEMENT LOG #
################


# manager
class MovementLogManager(GlobalManager):
    @property
    def unique(self):
        return 'id'


# table
class MovementLog(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    object = models.CharField(max_length=UNIQUE_LENGTH)
    method = models.CharField(max_length=UNIQUE_LENGTH)
    initial_location = models.CharField(max_length=UNIQUE_LENGTH)
    new_location = models.CharField(max_length=UNIQUE_LENGTH)
    # system fields
    user = models.CharField(max_length=UNIQUE_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = MovementLogManager()

    def __str__(self):
        return self.object


#################
# Run Time Data #
#################


# manager
class RTDManager(GlobalManager):
    @property
    def unique(self):
        return 'object'

    def location(self, unique):
        try:
            return Locations.objects.filter(location=self.filter(object=unique)[0].location)[0].__str__()
        except IndexError:
            return '---'

    def method(self, unique):
        return self.filter(object=unique)[0].type

    def box(self, unique):
        return self.filter(object=unique)[0].box

    def validate_location(self, box, sample):
        if self.filter(object=box)[0].location != self.filter(object=sample)[0].location:
            return True


# table
class RTD(models.Model):
    id = models.BigIntegerField(primary_key=True)
    object = models.CharField(max_length=UNIQUE_LENGTH)
    type = models.IntegerField()
    location = models.CharField(max_length=UNIQUE_LENGTH)
    box = models.CharField(max_length=UNIQUE_LENGTH)
    remaining_thaw_count = models.IntegerField()
    remaining_freeze_time = models.DurationField()

    # manager
    objects = RTDManager()

    class Meta:
        managed = False
        db_table = 'rtd'

    def __str__(self):
        return self.object


############
# Overview #
############


# manager
class OverviewManager(GlobalManager):
    @property
    def unique(self):
        return 'object'

    def location(self, unique):
        try:
            return Locations.objects.filter(location=self.filter(object=unique)[0].location)[0].__str__()
        except IndexError:
            return ''

    def method(self, unique):
        return self.filter(object=unique)[0].type

    def box(self, unique):
        try:
            return self.filter(object=unique)[0].box
        except IndexError:
            return None

    def position(self, unique):
        try:
            return self.filter(object=unique)[0].position
        except IndexError:
            return None

    def type(self, unique):
        try:
            return self.filter(object=unique)[0].type
        except IndexError:
            return False

    def affiliation(self, unique):
        try:
            return self.filter(object=unique)[0].affiliation
        except IndexError:
            return False


# table
class Overview(models.Model):
    id = models.BigIntegerField(primary_key=True)
    object = models.CharField(max_length=UNIQUE_LENGTH)
    affiliation = models.CharField(max_length=UNIQUE_LENGTH)
    type = models.CharField(max_length=UNIQUE_LENGTH)
    location = models.CharField(max_length=UNIQUE_LENGTH)
    box = models.CharField(max_length=UNIQUE_LENGTH)
    position = models.CharField(max_length=UNIQUE_LENGTH)

    # manager
    objects = OverviewManager()

    class Meta:
        managed = False
        db_table = 'overview'

    def __str__(self):
        return self.object


#########
# TIMES #
#########

# manager
class TimesManager(GlobalManager):
    @property
    def unique(self):
        return 'id'

    def time(self, id_ref, id_second):
        return self.filter(id_ref=id_ref, id_second=id_second)[0].time

    def freeze_time(self, item):
        return self.filter(item=item, method='freeze').order_by('-id_second')[0].time

    def method(self, item):
        return str(self.filter(item=item).order_by('-id_second')[0].method)


# table
class Times(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    id_ref = models.IntegerField()
    # id counting for each item
    id_second = models.IntegerField()
    # custom fields
    item = models.CharField(max_length=UNIQUE_LENGTH)
    method = models.CharField(max_length=UNIQUE_LENGTH)
    time = models.DateTimeField()
    duration = models.DurationField(blank=True, null=True)
    # system fields
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = TimesManager()

    def __str__(self):
        return self.item


##########
# BOXING #
##########


# manager
class BoxingManager(GlobalManager):
    @property
    def unique(self):
        return 'object'

    def next_position(self, box):
        try:
            return self.filter(object='', box=box).order_by('id')[0].position
        except IndexError:
            return False

    def exist_object(self, unique):
        try:
            return self.filter(object=unique)[0].id
        except IndexError:
            return False


# table
class Boxing(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    object = models.CharField(max_length=UNIQUE_LENGTH, blank=True)
    box = models.CharField(max_length=UNIQUE_LENGTH)
    position = models.CharField(max_length=UNIQUE_LENGTH, blank=True)
    # system fields
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = BoxingManager()

    def __str__(self):
        return self.object


#########
# ROLES #
#########


PERMISSIONS = (
    # ('ac_r', 'Accounts read'),
    # ('ac_w', 'Accounts write'),
    # ('ac_d', 'Accounts delete'),
    ('bo_r', 'Boxes read'),
    ('bo_w', 'Boxes write'),
    ('bo_d', 'Boxes delete'),
    ('bo_l', 'Boxes labels'),
    ('bt_r', 'Box Types read'),
    ('bt_w', 'Box Types write'),
    ('bt_d', 'Box Types delete'),
    ('co_r', 'Conditions read'),
    ('co_w', 'Conditions write'),
    ('co_d', 'Conditions delete'),
    ('lo_r', 'Locations read'),
    ('lo_w', 'Locations write'),
    ('lo_d', 'Locations delete'),
    ('lo_l', 'Locations labels'),
    ('ty_r', 'Types read'),
    ('ty_w', 'Types write'),
    ('ty_d', 'Types delete'),
    ('ta_r', 'Type attributes read'),
    ('ta_w', 'Type attributes write'),
    ('ta_d', 'Type attributes delete'),
    ('overview', 'Overview'),
    # ('home', 'Home'),
    ('bo', 'Overview boxing'),
    ('mo', 'Overview movements'),
    # ('sa_r', 'Samples read'),
    # ('sa_w', 'Samples write'),
    # ('sa_d', 'Samples delete'),
    # ('sa_l', 'Samples labels'),
    ('re_r', 'Reagents read'),
    ('re_w', 'Reagents write'),
    ('re_d', 'Reagents delete'),
    ('re_l', 'Reagents labels'),
    ('log_mo', 'Logs movement'),
    ('log_lo', 'Logs login'),
    ('log_la', 'Logs labels'),
    ('log_bo', 'Logs boxing'),
    ('ro_r', 'Roles read'),
    ('ro_w', 'Roles write'),
    ('ro_d', 'Roles delete'),
    ('us_r', 'Users read'),
    ('us_w', 'Users write'),
    ('us_a', 'Users activate'),
    ('us_p', 'Users password'),
)


# manager
class RolesManager(GlobalManager):
    @property
    def unique(self):
        return 'role'

    def permission(self, role, permission):
        if permission in self.filter(role=role)[0].permissions.split(','):
            return True
        else:
            return False

    def permissions(self, role):
        return self.filter(role=role)[0].permissions.split(',')


# table
class Roles(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    role = models.CharField(max_length=UNIQUE_LENGTH, unique=True)
    permissions = models.CharField(max_length=255)
    # system fields
    version = models.IntegerField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = RolesManager()

    def __str__(self):
        return '{}'.format(self.role)


# audit trail manager
class RolesAuditTrailManager(GlobalAuditTrailManager):
    pass


# audit trail table
class RolesAuditTrail(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    id_ref = models.IntegerField()
    # custom fields
    role = models.CharField(max_length=UNIQUE_LENGTH)
    permissions = models.CharField(max_length=255)
    # system fields
    version = models.IntegerField()
    action = models.CharField(max_length=ACTION_LENGTH)
    user = models.CharField(max_length=UNIQUE_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = RolesAuditTrailManager()


#########
# USERS #
#########

# manager
class UsersManager(BaseUserManager, GlobalManager):
    @property
    def unique(self):
        return 'username'

    @property
    def existing_users(self):
        return self.values_list('username', flat=True)

    use_in_migrations = True

    def _create_user(self, password, first_name, last_name, role, is_active, username=None):
        if username is None:
            username = custom.UserName(first_name=first_name, last_name=last_name,
                                       existing_users=self.existing_users).algorithm
        try:
            user = self.model(username=username, first_name=first_name, last_name=last_name, version=1, role=role,
                              is_active=is_active, initial_password=True)
            user.set_password(password)
            to_hash = 'username:{};first_name:{};last_name:{};role:{};is_active:{};' \
                      'initial_password:{};password:{};version:{};{}'\
                .format(username, first_name, last_name, role, is_active, True, user.password, 1, SECRET)
            user.checksum = custom.generate_checksum(to_hash)
            user.save(using=self._db)
            # success message + log entry
            message = 'Record "{}" has been created.'.format(username)
            log.info(message)
        except:
            # raise error
            message = 'Could not create record "{}".'.format(username)
            raise NameError(message)
        else:
            return user

    def _update_user(self, username, password=None, first_name=None, last_name=None, role=None, is_active=None,
                     initial_password=None):
        existing = self.filter(username=username)[0]
        version = existing.version + 1
        if first_name is None:
            first_name = existing.first_name
        if last_name is None:
            last_name = existing.last_name
        if role is None:
            role = existing.role
        if is_active is None:
            is_active = existing.is_active
        if initial_password is None:
            initial_password = existing.initial_password
        try:
            user = Users.objects.get(username=username)
            user.first_name = first_name
            user.last_name = last_name
            user.role = role
            user.is_active = is_active
            user.initial_password = initial_password
            user.version = version
            if password is not None:
                user.set_password(password)
            to_hash = 'username:{};first_name:{};last_name:{};role:{};is_active:{};' \
                      'initial_password:{};password:{};version:{};{}'\
                .format(username, first_name, last_name, role, is_active,
                        initial_password, user.password, version, SECRET)
            user.checksum = custom.generate_checksum(to_hash)
            user.save(using=self._db)
            # success message + log entry
            message = 'Record "{}" has been updated.'.format(username)
            log.info(message)
        except:
            # raise error
            message = 'Could not update record "{}".'.format(username)
            raise NameError(message)
        else:
            return user

    def create_user(self, password, first_name, last_name, role, is_active, operation_user):
        user = self._create_user(password=password, first_name=first_name, last_name=last_name, role=role,
                                 is_active=is_active)
        UserAuditTrail.objects.create_record(username=user.username, first_name=first_name, last_name=last_name,
                                             role=role, is_active=is_active, version=user.version, id_ref=user.id,
                                             initial_password=user.initial_password, user=operation_user,
                                             action='Create')
        return user

    def create_superuser(self, username, password):
        first_name = '-'
        last_name = '-'
        role = 'all'
        is_active = True
        user = self._create_user(username=username, password=password, first_name=first_name, last_name=last_name,
                                 role=role, is_active=is_active)
        UserAuditTrail.objects.create_record(username=user.username, first_name=first_name, last_name=last_name,
                                             role=role, is_active=is_active, version=user.version, id_ref=user.id,
                                             initial_password=user.initial_password, user='-',
                                             action='Create')
        return user

    def update_user(self, username, first_name, last_name, role, operation_user):
        user = self._update_user(username=username, first_name=first_name, last_name=last_name, role=role)
        UserAuditTrail.objects.create_record(username=user.username, first_name=user.first_name,
                                             last_name=user.last_name, role=user.role, is_active=user.is_active,
                                             version=user.version, id_ref=user.id,
                                             initial_password=user.initial_password, user=operation_user,
                                             action='Update')
        return user

    def set_initial_password(self, username, password, operation_user, initial_password):
        user = self._update_user(username=username, password=password, initial_password=initial_password)
        UserAuditTrail.objects.create_record(username=user.username, first_name=user.first_name,
                                             last_name=user.last_name, role=user.role, is_active=user.is_active,
                                             version=user.version, id_ref=user.id,
                                             initial_password=user.initial_password, user=operation_user,
                                             action='Update')
        return user

    def set_is_active(self, username, operation_user, is_active):
        user = self._update_user(username=username, is_active=is_active)
        UserAuditTrail.objects.create_record(username=user.username, first_name=user.first_name,
                                             last_name=user.last_name, role=user.role, is_active=user.is_active,
                                             version=user.version, id_ref=user.id,
                                             initial_password=user.initial_password, user=operation_user,
                                             action='Update')
        return user


# table
class Users(AbstractBaseUser):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    username = models.CharField(max_length=UNIQUE_LENGTH, unique=True)
    first_name = models.CharField(max_length=UNIQUE_LENGTH)
    last_name = models.CharField(max_length=UNIQUE_LENGTH)
    role = models.CharField(max_length=UNIQUE_LENGTH)
    is_active = models.BooleanField()
    initial_password = models.BooleanField()
    password = models.CharField(max_length=PASSWORD_LENGTH)
    last_login = models.DateTimeField(blank=True, null=True)
    # system fields
    version = models.IntegerField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = UsersManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return '{}'.format(self.username)

    def get_short_name(self):
        return '{}'.format(self.username)

    def permission(self, permission):
        return Roles.objects.permission(role=self.role, permission=permission)

    @property
    def permissions(self):
        return Roles.objects.permissions(role=self.role)


# audit trail manager
class UserAuditTrailManager(GlobalAuditTrailManager):
    def create_record(self, id_ref, username, first_name, last_name, role, is_active, initial_password, version,
                      action, user):
        timestamp = timezone.now()
        to_hash = 'username:{};first_name:{};last_name:{};role:{};is_active:{};' \
                  'initial_password:{};version:{};action:{};user:{};timestamp:{};{}'.format(
                   username, first_name, last_name, role, is_active, initial_password, version, action, user,
                   timestamp, SECRET)
        checksum = custom.generate_checksum(to_hash)
        try:
            record = self.model(
                id_ref=id_ref,
                username=username,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_active=is_active,
                initial_password=initial_password,
                version=version,
                action=action,
                user=user,
                timestamp=timestamp,
                checksum=checksum
            )
            record.save(using=self._db)
            # return true and success message + log entry
            message = 'Audit trail record for "{}" has been created.'.format(username)
            log.info(message)
        except:
            # raise error
            message = 'Could not create audit trail record for "{}".'.format(username)
            raise NameError(message)


# audit trail table
class UserAuditTrail(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    id_ref = models.IntegerField()
    # custom fields
    username = models.CharField(max_length=UNIQUE_LENGTH)
    first_name = models.CharField(max_length=UNIQUE_LENGTH)
    last_name = models.CharField(max_length=UNIQUE_LENGTH)
    role = models.CharField(max_length=UNIQUE_LENGTH)
    is_active = models.BooleanField()
    initial_password = models.BooleanField()
    # system fields
    version = models.IntegerField()
    action = models.CharField(max_length=ACTION_LENGTH)
    user = models.CharField(max_length=UNIQUE_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = UserAuditTrailManager()


#############
# LOGIN LOG #
#############


# manager
class LoginLogManager(GlobalManager):
    @property
    def unique(self):
        return 'id'

    @property
    def attempts(self):
        return self.attempts


# table
class LoginLog(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    user = models.CharField(max_length=UNIQUE_LENGTH)
    action = models.CharField(max_length=UNIQUE_LENGTH)
    attempts = models.IntegerField()
    method = models.CharField(max_length=UNIQUE_LENGTH)
    active = models.BooleanField()
    timestamp = models.DateTimeField()
    # system fields
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = LoginLogManager()

    def __str__(self):
        return self.user


#############
# LABEL LOG #
#############


# manager
class LabelLogManager(GlobalManager):
    @property
    def unique(self):
        return 'id'


# table
class LabelLog(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    # custom fields
    label = models.CharField(max_length=UNIQUE_LENGTH)
    action = models.CharField(max_length=UNIQUE_LENGTH)
    # system fields
    user = models.CharField(max_length=GENERATED_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = LabelLogManager()

    def __str__(self):
        return self.user


##############
# BOXING LOG #
##############

# manager
class BoxingLogManager(GlobalManager):
    @property
    def unique(self):
        return 'id'


# table
class BoxingLog(models.Model):
    # id
    id = models.AutoField(primary_key=True)
    object = models.CharField(max_length=UNIQUE_LENGTH)
    box = models.CharField(max_length=UNIQUE_LENGTH)
    position = models.CharField(max_length=GENERATED_LENGTH)
    # system fields
    user = models.CharField(max_length=GENERATED_LENGTH)
    timestamp = models.DateTimeField()
    checksum = models.CharField(max_length=CHECKSUM_LENGTH)
    # manager
    objects = BoxingLogManager()


# tables for reference checks used in delete validation
REF_TABLES = {
    'lab_conditions': Locations,
    'lab_boxtypes': Boxes
}

# tables for export/import
TABLES = {
    'samples': Samples,
    'reagents': Reagents,
    'boxes': Boxes,
    'box_types': BoxTypes,
    'conditions': Conditions,
    'types': Types,
    'locations': Locations,
    'roles': Roles,
    'users': Users,
    'freeze_thaw_accounts': FreezeThawAccounts,
    'movement_log': MovementLog,
    'login_log': LoginLog,
    'label_log': LabelLog,
    'boxing_log': BoxingLog,
    'home': RTD,
    'overview': Overview,
    'type_attributes': TypeAttributes
}

# tables for export audit trails
TABLES_AT = {
    'reagents': ReagentsAuditTrail,
    'boxes': BoxesAuditTrail,
    'box_types': BoxTypesAuditTrail,
    'conditions': ConditionsAuditTrail,
    'types': TypesAuditTrail,
    'locations': LocationsAuditTrail,
    'roles': RolesAuditTrail,
    'users': UserAuditTrail,
    'type_attributes': TypeAttributesAuditTrail
}

EXPORT_PERMISSIONS = {
    'samples': 'sa_r',
    'reagents': 're_r',
    'boxes': 'bo_r',
    'box_types': 'bt_r',
    'conditions': 'co_r',
    'types': 'ty_r',
    'locations': 'lo_r',
    'roles': 'ro_r',
    'users': 'us_r',
    'freeze_thaw_accounts': 'ac_r',
    'movement_log': 'log_mo',
    'login_log': 'log_lo',
    'label_log': 'log_la',
    'boxing_log': 'log_bo',
    'home': 'home',
    'overview': 'overview',
    'type_attributes': 'ta_r'
}
