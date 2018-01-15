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


# django imports
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from lab.models import UNIQUE_LENGTH, GENERATED_LENGTH, VOLUMES, TIMES, \
    Conditions, Locations, ORIGIN, FreezeThawAccounts, PERMISSIONS, Groups

# app imports
import lab.models as models


# variables
COLOR_MANDATORY = '#FA5858'


class ConditionFormNew(forms.Form):
    condition = forms.CharField(label='condition', max_length=UNIQUE_LENGTH,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))


class ConditionFormEdit(forms.Form):
    condition = forms.CharField(label='condition', max_length=UNIQUE_LENGTH,
                                widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'disabled': True},))


# groups
class GroupsFormNew(forms.Form):
    group = forms.CharField(label='group', max_length=UNIQUE_LENGTH,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    permissions = forms.CharField(label='permissions', required=False,
                                  widget=forms.SelectMultiple(choices=PERMISSIONS, attrs={'class': 'form-control'}))


class GroupsFormEdit(forms.Form):
    group = forms.CharField(label='group', max_length=UNIQUE_LENGTH,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'disabled': True},))
    permissions = forms.CharField(label='permissions', required=False,
                                  widget=forms.SelectMultiple(choices=PERMISSIONS, attrs={'class': 'form-control'}))


# user
class UsersFormNew(forms.Form):
    first_name = forms.CharField(label='first name', max_length=UNIQUE_LENGTH,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='last name', max_length=UNIQUE_LENGTH,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='password',
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_repeat = forms.CharField(label='password repeat',
                                      widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    is_active = forms.BooleanField(label='active', required=False,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-control',
                                                                     'style': 'align: left'}))
    group = forms.ModelChoiceField(label='group', queryset=Groups.objects.all(), empty_label=None,
                                   widget=forms.Select(attrs={'class': 'form-control'}))


class UsersFormEdit(forms.Form):
    username = forms.CharField(label='username', max_length=GENERATED_LENGTH,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))
    first_name = forms.CharField(label='first name', max_length=UNIQUE_LENGTH,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='last name', max_length=UNIQUE_LENGTH,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    group = forms.ModelChoiceField(label='group', queryset=Groups.objects.all(), empty_label=None,
                                   widget=forms.Select(attrs={'class': 'form-control'}))


# locations
class LocationsFormNew(forms.Form):
    name = forms.CharField(label='name', max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    condition = forms.ModelChoiceField(label='condition', queryset=Conditions.objects.all(), empty_label=None,
                                       widget=forms.Select(attrs={'class': 'form-control'}))


class LocationsFormEdit(forms.Form):
    location = forms.CharField(label='location', max_length=GENERATED_LENGTH,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))
    name = forms.CharField(label='name', max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    condition = forms.ModelChoiceField(label='condition', queryset=Conditions.objects.all(), empty_label=None,
                                       widget=forms.Select(attrs={'class': 'form-control'}))


class BoxesFormNew(forms.Form):
    name = forms.CharField(label='name', max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    rows = forms.IntegerField(label='rows', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    columns = forms.IntegerField(label='columns', widget=forms.NumberInput(attrs={'class': 'form-control'}))


class BoxesFormEdit(forms.Form):
    box = forms.CharField(label='box', max_length=GENERATED_LENGTH,
                          widget=forms.TextInput(attrs={'class': 'form-control',
                                                        'disabled': True}))
    name = forms.CharField(label='name', max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    rows = forms.IntegerField(label='rows', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    columns = forms.IntegerField(label='columns', widget=forms.NumberInput(attrs={'class': 'form-control'}))


class SamplesFormNew(forms.Form):
    name = forms.CharField(label='name', max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    account = forms.ModelChoiceField(label='account', queryset=FreezeThawAccounts.objects.all(),
                                     widget=forms.Select(attrs={'class': 'form-control'}), empty_label=None)
    type = forms.CharField(label='type', max_length=GENERATED_LENGTH,
                           widget=forms.Select(choices=ORIGIN, attrs={'class': 'form-control manual'}))
    volume = forms.FloatField(label='volume', required=False,
                              widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    uom = forms.CharField(label='uom', max_length=GENERATED_LENGTH,
                          widget=forms.Select(choices=VOLUMES, attrs={'class': 'form-control manual'}), required=False)
    amount = forms.IntegerField(label='amount', initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                required=False, max_value=100)


class SamplesFormEdit(forms.Form):
    sample = forms.CharField(label='samples', max_length=GENERATED_LENGTH,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))
    name = forms.CharField(label='name', max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    account = forms.ModelChoiceField(label='account', queryset=FreezeThawAccounts.objects.all(),
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    type = forms.CharField(label='type', max_length=GENERATED_LENGTH,
                           widget=forms.Select(choices=ORIGIN, attrs={'class': 'form-control manual'}))
    volume = forms.FloatField(label='volume', required=False,
                              widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    uom = forms.CharField(label='uom', max_length=GENERATED_LENGTH,
                          widget=forms.Select(choices=VOLUMES, attrs={'class': 'form-control manual'}), required=False)


class MovementsForm(forms.Form):
    actual_location = forms.CharField(label='actual_location', max_length=UNIQUE_LENGTH, required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': True}))
    new_location = forms.ModelChoiceField(label='new_location', queryset=Locations.objects.all(), empty_label=None,
                                          widget=forms.Select(attrs={'class': 'form-control'}))


def validate_password_length(value):
    if len(value) < 8:
        raise ValidationError('Password must be longer than 8 characters.')


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
                                             'and include 2 uppercase, 2 lowercase letters and two numbers.',
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
                                         help_text='Enter a new password. Must be longer than 8 characters.',
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
    account = forms.CharField(label='account', max_length=40,
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    freeze_condition = forms.ModelChoiceField(label='freeze condition', queryset=Conditions.objects.all(),
                                              empty_label=None, widget=forms.Select(attrs={'class': 'form-control'}))
    freeze_time = forms.IntegerField(label='freeze time', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    freeze_uom = forms.CharField(label='freeze uom', max_length=GENERATED_LENGTH,
                                 widget=forms.Select(choices=TIMES, attrs={'class': 'form-control manual'}))
    thaw_condition = forms.ModelChoiceField(label='thaw condition', queryset=Conditions.objects.all(), empty_label=None,
                                            widget=forms.Select(attrs={'class': 'form-control'}))
    thaw_time = forms.IntegerField(label='thaw time', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    thaw_uom = forms.CharField(label='thaw uom', max_length=GENERATED_LENGTH,
                               widget=forms.Select(choices=TIMES, attrs={'class': 'form-control manual'}))
    thaw_count = forms.IntegerField(label='thaw count', widget=forms.NumberInput(attrs={'class': 'form-control'}))


class FreezeThawAccountsFormEdit(forms.Form):
    account = forms.CharField(label='account', max_length=40,
                              widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'disabled': True}))
    freeze_condition = forms.ModelChoiceField(label='freeze condition', queryset=Conditions.objects.all(),
                                              empty_label=None, widget=forms.Select(attrs={'class': 'form-control'}))
    freeze_time = forms.IntegerField(label='freeze time', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    freeze_uom = forms.CharField(label='freeze uom', max_length=GENERATED_LENGTH,
                                 widget=forms.Select(choices=TIMES, attrs={'class': 'form-control manual'}))
    thaw_condition = forms.ModelChoiceField(label='thaw condition', queryset=Conditions.objects.all(), empty_label=None,
                                            widget=forms.Select(attrs={'class': 'form-control'}))
    thaw_time = forms.IntegerField(label='thaw time', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    thaw_uom = forms.CharField(label='thaw uom', max_length=GENERATED_LENGTH,
                               widget=forms.Select(choices=TIMES, attrs={'class': 'form-control manual'}))
    thaw_count = forms.IntegerField(label='thaw count', widget=forms.NumberInput(attrs={'class': 'form-control'}))


class LoginForm(forms.Form):
    user = forms.CharField(label='username', max_length=UNIQUE_LENGTH,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

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
                    # log.warning('User "{}" tried to log in.'.format(username))
                    # new_login_log(username=username, action='attempt')
                else:
                    pass
                    # log.warning('UNKNOWN ATTEMPT: "{}" tried to log in.'.format(username))
                raise forms.ValidationError('Authentication failed! Please provide valid username and password.')
