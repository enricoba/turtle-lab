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
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from lab.models import UNIQUE_LENGTH, GENERATED_LENGTH, TIMES, \
    Conditions, Locations, FreezeThawAccounts, PERMISSIONS, Roles, \
    Types, BoxTypes

# app imports
import lab.models as models
import lab.custom as custom
import lab.framework as framework

# define logger
log = logging.getLogger(__name__)

# variables
COLOR_MANDATORY = '#FA5858'


def validate_unique_condition(value):
    if models.Conditions.objects.exist(value):
        raise ValidationError('Record already exists.')


def validate_unique_box_type(value):
    if models.BoxTypes.objects.exist(value):
        raise ValidationError('Record already exists.')


def validate_unique_type(value):
    if models.Types.objects.exist(value):
        raise ValidationError('Record already exists.')


def validate_unique_roles(value):
    if models.Roles.objects.exist(value):
        raise ValidationError('Record already exists.')


def validate_unique_freeze_thaw_accounts(value):
    if models.FreezeThawAccounts.objects.exist(value):
        raise ValidationError('Record already exists.')


def validate_password_length(value):
    if len(value) < 8:
        raise ValidationError('Password must be longer than 8 characters.')


def validate_box_types_figures(value):
    try:
        _value = int(value)
        if _value > 26:
            raise ValidationError('Input must be smaller than 27.')
    except ValueError:
        if value.capitalize() not in custom.ALPHABET.keys():
            raise ValidationError('Input must be a character of the alphabet.')


def validate_digits(value):
    x = 0
    for char in value:
        if char.isdigit():
            x += 1
    if x < 2:
        raise ValidationError('Password must at least contain 2 numbers.')


def validate_upper(value):
    x = 0
    for char in value:
        if char.isupper():
            x += 1
    if x < 2:
        raise ValidationError('Password must at least contain 2 capital letters.')


def validate_lower(value):
    x = 0
    for char in value:
        if char.islower():
            x += 1
    if x < 2:
        raise ValidationError('Password must at least contain 2 lowercase letters.')


def validate_positive_number(value):
    if value < 0:
        raise ValidationError('Number must be positive.')


def validate_box_exist(value):
    if not models.Boxes.objects.box_by_type(type=value):
        raise ValidationError('No box for type "{}" found'.format(value))


class ConditionFormNew(forms.Form):
    condition = forms.CharField(label='condition', max_length=UNIQUE_LENGTH,
                                widget=forms.TextInput(attrs={'class': 'form-control'}),
                                help_text='Enter a condition.',
                                validators=[validate_unique_condition])


class ConditionFormEdit(forms.Form):
    condition = forms.CharField(label='condition', max_length=UNIQUE_LENGTH,
                                widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'disabled': True},))


# groups
class RolesFormNew(forms.Form):
    role = forms.CharField(label='role', max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control'}),
                           help_text='Enter a role.',
                           validators=[validate_unique_roles])
    permissions = forms.CharField(label='permissions', required=False,
                                  help_text='Select permissions.',
                                  widget=forms.SelectMultiple(choices=PERMISSIONS, attrs={'class': 'form-control perm',
                                                                                          'size': '20'}))


class RolesFormEdit(forms.Form):
    role = forms.CharField(label='role', max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True},))
    permissions = forms.CharField(label='permissions', required=False,
                                  help_text='Select permissions.',
                                  widget=forms.SelectMultiple(choices=PERMISSIONS, attrs={'class': 'form-control perm',
                                                                                          'size': '20'}))


# user
class UsersFormNew(forms.Form):
    first_name = forms.CharField(label='first name', max_length=UNIQUE_LENGTH,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}),
                                 help_text='Enter your first name.')
    last_name = forms.CharField(label='last name', max_length=UNIQUE_LENGTH,
                                widget=forms.TextInput(attrs={'class': 'form-control'}),
                                help_text='Enter your last name.')
    password = forms.CharField(label='password',
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                               help_text='Enter a new password. Must be longer than 8 characters'
                                         'and include 2 uppercase, 2 lowercase letters and 2 numbers.',
                               validators=[validate_password_length,
                                           validate_digits,
                                           validate_lower,
                                           validate_upper]
                               )
    password_repeat = forms.CharField(label='password repeat',
                                      widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                      help_text='Repeat your new password.')
    is_active = forms.BooleanField(label='active', required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-control',
                                                                     'style': 'align: left'}),
                                   help_text='Select the active status.')
    role = forms.ModelChoiceField(label='role', queryset=Roles.objects.all(), empty_label=None,
                                  widget=forms.Select(attrs={'class': 'form-control'}),
                                  help_text='Select a role.')

    def clean(self):
        cleaned_data = super(UsersFormNew, self).clean()
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')
        if password and password_repeat:
            if password != password_repeat:
                raise forms.ValidationError('New passwords must match.')


class UsersFormEdit(forms.Form):
    username = forms.CharField(label='username', max_length=GENERATED_LENGTH,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))
    first_name = forms.CharField(label='first name', max_length=UNIQUE_LENGTH,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}),
                                 help_text='Enter your first name.')
    last_name = forms.CharField(label='last name', max_length=UNIQUE_LENGTH,
                                widget=forms.TextInput(attrs={'class': 'form-control'}),
                                help_text='Enter your last name.')
    role = forms.ModelChoiceField(label='role', queryset=Roles.objects.all(), empty_label=None,
                                  widget=forms.Select(attrs={'class': 'form-control'}),
                                  help_text='Select a role.')


# locations
class LocationsFormNew(forms.Form):
    name = forms.CharField(label='name', max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control'}), required=False,
                           help_text='Enter a location name.')
    condition = forms.ModelChoiceField(label='condition', queryset=Conditions.objects.all(), empty_label=None,
                                       widget=forms.Select(attrs={'class': 'form-control'}),
                                       help_text='Select a condition.')
    max_boxes = forms.IntegerField(label='max boxes', widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                   help_text='Enter an appropriate value for maximum box capacity.',
                                   validators=[validate_positive_number], required=False)


class LocationsFormEdit(forms.Form):
    location = forms.CharField(label='location', max_length=GENERATED_LENGTH,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))
    name = forms.CharField(label='name', max_length=UNIQUE_LENGTH, help_text='Enter a location name.',
                           widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    condition = forms.ModelChoiceField(label='condition', queryset=Conditions.objects.all(), empty_label=None,
                                       widget=forms.Select(attrs={'class': 'form-control'}),
                                       help_text='Select a condition.')
    max_boxes = forms.IntegerField(label='max boxes', widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                   help_text='Enter an appropriate value for maximum box capacity.',
                                   validators=[validate_positive_number], required=False)


#########
# TYPES #
#########


class TypesFormNew(forms.Form):
    type = forms.CharField(label='type', max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control'}),
                           help_text='Enter a type.',
                           validators=[validate_unique_type])
    affiliation = forms.CharField(label='affiliation', max_length=UNIQUE_LENGTH, help_text='Select an affiliation.',
                                  widget=forms.Select(choices=models.AFFILIATIONS,
                                                      attrs={'class': 'form-control manual'}))
    storage_condition = forms.ModelChoiceField(label='storage condition', queryset=Conditions.objects.all(),
                                               widget=forms.Select(attrs={'class': 'form-control'}), empty_label=None,
                                               help_text='Select a storage condition.')
    usage_condition = forms.ModelChoiceField(label='usage condition', queryset=Conditions.objects.all(), required=False,
                                             widget=forms.Select(attrs={'class': 'form-control'}), empty_label='',
                                             help_text='Select a usage condition. Optional for reagents.')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TypesFormNew, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(TypesFormNew, self).clean()
        affiliation = cleaned_data.get('affiliation')
        usage_condition = cleaned_data.get('usage_condition')
        if affiliation == 'Samples':
            if usage_condition is None:
                raise forms.ValidationError('Samples must have usage condition.')


class TypesFormEdit(TypesFormNew):
    type = forms.CharField(label='type', max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))


#########
# BOXES #
#########


class BoxesFormNew(forms.Form):
    name = forms.CharField(label='name', max_length=UNIQUE_LENGTH, help_text='Enter a box name.',
                           widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    box_type = forms.ModelChoiceField(label='box type', queryset=BoxTypes.objects.all(), empty_label=None,
                                      widget=forms.Select(attrs={'class': 'form-control'}),
                                      help_text='Select a box type.')
    type = forms.ModelChoiceField(label='type', queryset=Types.objects.all(), empty_label='',
                                  widget=forms.Select(attrs={'class': 'form-control'}), required=False,
                                  help_text='Select a type. This field is optional.')


class BoxesFormEdit(forms.Form):
    box = forms.CharField(label='box', max_length=GENERATED_LENGTH,
                          widget=forms.TextInput(attrs={'class': 'form-control',
                                                        'disabled': True}))
    name = forms.CharField(label='name', max_length=UNIQUE_LENGTH, help_text='Enter a box name.',
                           widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    box_type = forms.ModelChoiceField(label='box type', queryset=BoxTypes.objects.all(), empty_label=None,
                                      widget=forms.Select(attrs={'class': 'form-control',
                                                                 'disabled': True}))
    type = forms.ModelChoiceField(label='type', queryset=Types.objects.all(), empty_label='',
                                  widget=forms.Select(attrs={'class': 'form-control'}), required=False,
                                  help_text='Select a type. This field is optional.')


#############
# BOX TYPES #
#############


class BoxTypesFormNew(forms.Form):
    box_type = forms.CharField(label='box type', max_length=UNIQUE_LENGTH, help_text='Enter a box type.',
                               widget=forms.TextInput(attrs={'class': 'form-control'}),
                               validators=[validate_unique_box_type])
    alignment = forms.CharField(label='alignment', max_length=UNIQUE_LENGTH, help_text='Select an alignment type.',
                                widget=forms.Select(choices=models.BOX_ALIGNMENT,
                                                    attrs={'class': 'form-control manual'}))
    rows = forms.CharField(label='rows', widget=forms.TextInput(attrs={'class': 'form-control'}),
                           help_text='Enter box rows in numbers of characters of the alphabet.',
                           validators=[validate_box_types_figures])
    columns = forms.CharField(label='columns', widget=forms.TextInput(attrs={'class': 'form-control'}),
                              help_text='Enter box columns in numbers of characters of the alphabet.',
                              validators=[validate_box_types_figures])
    default = forms.BooleanField(label='default', required=False, help_text='Select the default status.',
                                 widget=forms.CheckboxInput(attrs={'class': 'form-control', 'style': 'align: left'}),
                                 )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BoxTypesFormNew, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(BoxTypesFormNew, self).clean()
        default = models.BoxTypes.objects.default
        if cleaned_data.get('default') and default.exists():
            if cleaned_data.get('box_type') != default[0].box_type:
                raise ValidationError('Only one box type can be default.')


class BoxTypesFormEdit(BoxTypesFormNew):
    box_type = forms.CharField(label='box type', max_length=UNIQUE_LENGTH,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))


###########
# SAMPLES #
###########


class SamplesFormNew(forms.Form):
    name = forms.CharField(label='name', max_length=UNIQUE_LENGTH, help_text='Enter a sample name.',
                           widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    account = forms.ModelChoiceField(label='account', queryset=FreezeThawAccounts.objects.all(),
                                     widget=forms.Select(attrs={'class': 'form-control'}), empty_label=None,
                                     help_text='Select an account.')
    amount = forms.IntegerField(label='amount', initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                required=False, max_value=100, help_text='Enter sample amount.',
                                validators=[validate_positive_number])


class SamplesFormEdit(forms.Form):
    sample = forms.CharField(label='sample', max_length=GENERATED_LENGTH,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))
    name = forms.CharField(label='name', max_length=UNIQUE_LENGTH, help_text='Enter a sample name.',
                           widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    account = forms.ModelChoiceField(label='account', queryset=FreezeThawAccounts.objects.all(),
                                     widget=forms.Select(attrs={'class': 'form-control', 'disabled': True}),
                                     help_text='Select an account.', empty_label=None)


############
# REAGENTS #
############


class ReagentsFormNew(forms.Form):
    name = forms.CharField(label='name', max_length=UNIQUE_LENGTH, help_text='Enter a reagent name.',
                           widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    type = forms.ModelChoiceField(label='type', queryset=Types.objects.reagents,
                                  widget=forms.Select(attrs={'class': 'form-control'}), empty_label=None,
                                  help_text='Select a type.')


class ReagentsFormEdit(forms.Form):
    reagent = forms.CharField(label='reagent', max_length=GENERATED_LENGTH,
                              widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))
    name = forms.CharField(label='name', max_length=UNIQUE_LENGTH, help_text='Enter a reagent name.',
                           widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    type = forms.ModelChoiceField(label='type', queryset=Types.objects.reagents,
                                  widget=forms.Select(attrs={'class': 'form-control', 'disabled': True}),
                                  empty_label=None, help_text='Select a type.')


class MovementsForm(forms.Form):
    actual_location = forms.CharField(label='actual location', max_length=UNIQUE_LENGTH, required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))
    new_location = forms.ModelChoiceField(label='target location', queryset=Locations.objects.all(), empty_label=None,
                                          widget=forms.Select(attrs={'class': 'form-control'}),
                                          help_text='Select the target location.')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MovementsForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(MovementsForm, self).clean()
        actual_location = cleaned_data.get('actual_location')
        new_location = str(cleaned_data.get('new_location'))[:7]
        unique = self.request.POST.get('unique')
        if actual_location == new_location:
            raise forms.ValidationError('Actual location is equal to new location.')
        if unique[:1] == 'B':
            boxed_samples = models.RTD.objects.filter(box=unique[:7])
            for sample in boxed_samples:
                if models.Locations.objects.condition(new_location) not in models.Samples.objects.conditions(sample):
                    raise forms.ValidationError('Target location has no suitable condition for {}.'.format(sample))
        if unique[:1] == 'S':
            if models.Locations.objects.condition(new_location) not in models.Samples.objects.conditions(unique):
                raise forms.ValidationError('Target location has no suitable condition.')


class BoxingForm(forms.Form):
    actual_box = forms.CharField(label='actual box', max_length=UNIQUE_LENGTH, required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))
    new_box = forms.ModelChoiceField(label='target box', queryset=models.Boxes.objects.all(), empty_label='',
                                     widget=forms.Select(attrs={'class': 'form-control'}), required=False,
                                     help_text='Select the target box.')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BoxingForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(BoxingForm, self).clean()
        actual_box = cleaned_data.get('actual_box')
        new_box = str(cleaned_data.get('new_box'))[:7]
        unique = self.request.POST.get('unique')
        if new_box != 'None':
            if models.RTD.objects.validate_location(box=new_box, sample=unique):
                raise forms.ValidationError('Sample and box must be in the same location.')
            if actual_box == new_box:
                raise forms.ValidationError('Actual box is equal to new box.')


class OverviewBoxingForm(forms.Form):
    r_s = forms.ChoiceField(label='R / S', choices=(('R', 'Reagent'), ('S', 'Sample')), required=False,
                            widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_r_s'}))
    type_r = forms.ModelChoiceField(label='Type R', queryset=models.Types.objects.reagents.all(), empty_label=None,
                                    widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_r'}),
                                    required=False, validators=[validate_box_exist])
    type_s = forms.ModelChoiceField(label='Type S', queryset=models.Types.objects.samples.all(), empty_label=None,
                                    widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_s'}),
                                    required=False, validators=[validate_box_exist])
    box = forms.CharField(label='Box', max_length=UNIQUE_LENGTH,
                          widget=forms.TextInput(attrs={'class': 'form-control',
                                                        'placeholder': 'scan target box'}))


class PasswordForm(forms.Form):
    user = forms.CharField(label='Username',
                           max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'disabled': True}))
    password_change = forms.CharField(label='Password',
                                      max_length=UNIQUE_LENGTH,
                                      widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                        'placeholder': 'current password'}),
                                      help_text='Enter your password.')
    password_new = forms.CharField(label='New password',
                                   max_length=UNIQUE_LENGTH,
                                   widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                     'placeholder': 'new password'}),
                                   help_text='Enter a new password. Must be longer than 8 characters'
                                             'and include 2 uppercase, 2 lowercase letters and 2 numbers.',
                                   validators=[validate_password_length,
                                               validate_digits,
                                               validate_lower,
                                               validate_upper])
    password_repeat = forms.CharField(label='New password confirmation',
                                      max_length=UNIQUE_LENGTH,
                                      widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                        'placeholder': 'new password'}),
                                      help_text='Repeat your new password.')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(PasswordForm, self).clean()
        username = cleaned_data.get('user')
        password = cleaned_data.get('password_change')
        password_new = cleaned_data.get('password_new')
        password_repeat = cleaned_data.get('password_repeat')
        user = authenticate(request=self.request, username=username, password=password)
        if username is not None and password is not None:
            if user is None:
                # new_login_log(username=username, action='attempt')
                # log.warning(message)
                raise forms.ValidationError('Authentication failed! Please provide valid username and password.')
            if password_new and password_repeat:
                if password_new != password_repeat:
                    raise forms.ValidationError('New passwords must match.')


class PasswordFormUsers(forms.Form):
    user = forms.CharField(label='username', max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))
    password_new_users = forms.CharField(label='new password', max_length=UNIQUE_LENGTH,
                                         widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                         help_text='Enter a new password. Must be longer than 8 characters'
                                                   'and include 2 uppercase, 2 lowercase letters and 2 numbers.',
                                         validators=[validate_password_length,
                                                     validate_digits,
                                                     validate_lower,
                                                     validate_upper])
    password_repeat_users = forms.CharField(label='password repeat',
                                            max_length=UNIQUE_LENGTH,
                                            widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                            help_text='Repeat your new password.')

    def clean(self):
        cleaned_data = super(PasswordFormUsers, self).clean()
        password_new = cleaned_data.get('password_new_users')
        password_repeat = cleaned_data.get('password_repeat_users')
        if password_new and password_repeat:
            if password_new != password_repeat:
                raise forms.ValidationError('New passwords must match.')


class FreezeTHawAccountsFormNew(forms.Form):
    account = forms.CharField(label='account', max_length=40, help_text='Enter an account name.',
                              widget=forms.TextInput(attrs={'class': 'form-control'}),
                              validators=[validate_unique_freeze_thaw_accounts])
    freeze_condition = forms.ModelChoiceField(label='freeze condition', queryset=Conditions.objects.all(),
                                              empty_label=None, widget=forms.Select(attrs={'class': 'form-control'}),
                                              help_text='Select a freeze condition.')
    freeze_time = forms.IntegerField(label='freeze time', widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                     help_text='Enter a freeze time.')
    freeze_uom = forms.CharField(label='freeze uom', max_length=GENERATED_LENGTH,
                                 widget=forms.Select(choices=TIMES, attrs={'class': 'form-control manual'}),
                                 help_text='Select freeze time unit of measurement.')
    thaw_condition = forms.ModelChoiceField(label='thaw condition', queryset=Conditions.objects.all(), empty_label=None,
                                            widget=forms.Select(attrs={'class': 'form-control'}),
                                            help_text='Select a thaw condition.')
    thaw_time = forms.IntegerField(label='thaw time', widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                   help_text='Enter a thaw time.')
    thaw_uom = forms.CharField(label='thaw uom', max_length=GENERATED_LENGTH,
                               help_text='Select thaw time unit of measurement.',
                               widget=forms.Select(choices=TIMES, attrs={'class': 'form-control manual'}))
    thaw_count = forms.IntegerField(label='thaw count', widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                    help_text='Enter thaw count.')


class FreezeThawAccountsFormEdit(forms.Form):
    account = forms.CharField(label='account', max_length=40,
                              widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'disabled': True}))
    freeze_condition = forms.ModelChoiceField(label='freeze condition', queryset=Conditions.objects.all(),
                                              empty_label=None, widget=forms.Select(attrs={'class': 'form-control'}),
                                              help_text='Select a freeze condition.')
    freeze_time = forms.IntegerField(label='freeze time', widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                     help_text='Enter a freeze time.')
    freeze_uom = forms.CharField(label='freeze uom', max_length=GENERATED_LENGTH,
                                 widget=forms.Select(choices=TIMES, attrs={'class': 'form-control manual'}),
                                 help_text='Select freeze time unit of measurement.')
    thaw_condition = forms.ModelChoiceField(label='thaw condition', queryset=Conditions.objects.all(), empty_label=None,
                                            widget=forms.Select(attrs={'class': 'form-control'}),
                                            help_text='Select a thaw condition.')
    thaw_time = forms.IntegerField(label='thaw time', widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                   help_text='Enter a thaw time.')
    thaw_uom = forms.CharField(label='thaw uom', max_length=GENERATED_LENGTH,
                               help_text='Select thaw time unit of measurement.',
                               widget=forms.Select(choices=TIMES, attrs={'class': 'form-control manual'}))
    thaw_count = forms.IntegerField(label='thaw count', widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                    help_text='Enter thaw count.')


class LoginForm(forms.Form):
    user = forms.CharField(label='username', max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': 'User name',
                                                         'style': 'width: 400px'}))
    password = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                   'placeholder': 'Password',
                                                                                   'style': 'width: 400px'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get('user')
        password = cleaned_data.get('password')
        if username is not None and password is not None:
            user = authenticate(request=self.request, username=username, password=password)
            if user is None:
                if models.Users.objects.filter(username=username).exists():
                    pass
                    log.warning('User "{}" tried to log in.'.format(username))
                    framework.new_login_log(username=username, action='attempt')
                else:
                    pass
                    log.warning('UNKNOWN ATTEMPT: "{}" tried to log in.'.format(username))
                raise forms.ValidationError('Authentication failed! Please provide valid username and password.')
