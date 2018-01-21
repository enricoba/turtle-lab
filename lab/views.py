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
import json

# django imports
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required

# app imports
import lab.forms as forms
import lab.models as models
import lab.custom as custom
import lab.decorators as decorators
import lab.framework as framework

# define logger
log = logging.getLogger(__name__)

# secret key
SECRET = settings.SECRET


@require_GET
def index(request):
    context = {'tables': None,
               'content': 'index',
               'session': None,
               'user': None}
    if request.user.is_authenticated:
        return HttpResponseRedirect('/home')
    else:
        context['login'] = forms.LoginForm()
        context['modal_password'] = forms.PasswordForm()
        return render(request, 'lab/index.html', context)


@require_POST
@decorators.require_ajax
def index_login(request):
    form = forms.LoginForm(request.POST, request=request)
    if form.is_valid():
        username = form.cleaned_data['user']
        password = form.cleaned_data['password']
        # authenticate user
        user = authenticate(request=request, username=username, password=password)
        # change password if initial
        if user.initial_password is True:
            data = {'response': True,
                    'user': username,
                    'action': 'initial'}
            return JsonResponse(data)
        else:
            # login user
            login(request, user)
            # message + log entry
            message = 'Authentication successful! User "{}" logged in.'.format(user)
            # create public log entry
            framework.new_login_log(username=username, action='login', active=True)
            log.info(message)
            data = {'response': True}
            return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_login',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@decorators.require_ajax
def index_password(request):
    form = forms.PasswordForm(request.POST, request=request)
    if form.is_valid():
        username = form.cleaned_data['user']
        password = form.cleaned_data['password_change']
        password_new = form.cleaned_data['password_new']
        # authenticate user
        user = authenticate(request=request, username=username, password=password)
        user_new = models.Users.objects.set_initial_password(username=user.username,
                                                             password=password_new,
                                                             operation_user=username,
                                                             initial_password=False)
        if user_new is not None:
            # login user
            login(request, user_new)
            # message + log entry
            message = 'Authentication successful! User "{}" logged in.'.format(user)
            # create public log entry
            framework.new_login_log(username=user_new.username, action='login', active=True)
            log.info(message)
            data = {'response': True}
            return JsonResponse(data)
        else:
            response = False
        data = {'response': response}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_password',
                'errors': form.errors}
        return JsonResponse(data)


@require_GET
@login_required
def index_logout(request):
    # message + log entry
    message = 'User "{}" logged out.'.format(request.user.username)
    username = request.user.username
    logout(request)
    log.info(message)
    # create public log entry
    framework.new_login_log(username=username, action='logout')
    return HttpResponseRedirect('/')


@require_GET
@login_required
@decorators.permission('ro_r', 'ro_w', 'ro_d')
def roles(request):
    context = framework.html_and_data(
        context={'tables': True,
                 'content': 'roles',
                 'session': True,
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.Roles),
        get_audit_trail=framework.GetAuditTrail(table=models.RolesAuditTrail),
        form_render_new=forms.RolesFormNew(),
        form_render_edit=forms.RolesFormEdit())
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('ro_r', 'ro_w', 'ro_d')
@decorators.require_ajax
def roles_audit_trail(request):
    response, data = framework.GetAuditTrail(
        table=models.RolesAuditTrail).get(
        id_ref=models.Roles.objects.id(request.GET.get('unique')))
    data = {'response': response,
            'data': data}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('ro_w')
@decorators.require_ajax
def roles_new(request):
    form = forms.RolesFormNew(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.Roles,
                                                   table_audit_trail=models.RolesAuditTrail)
        permissions = form.cleaned_data['permissions'].strip('[').strip(']').strip("'")
        response, message = manipulation.new_at(user=request.user.username,
                                                role=form.cleaned_data['role'],
                                                permissions=permissions)
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_new',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('ro_w')
@decorators.require_ajax
def roles_edit(request):
    form = forms.RolesFormEdit(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.Roles,
                                                   table_audit_trail=models.RolesAuditTrail)
        permissions = form.cleaned_data['permissions'].strip('[').strip(']').strip("'")
        response, message = manipulation.edit_at(user=request.user.username,
                                                 role=form.cleaned_data['role'],
                                                 permissions=permissions)
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_edit',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('ro_d')
@decorators.require_ajax
def roles_delete(request):
    manipulation = framework.TableManipulation(table=models.Roles,
                                               table_audit_trail=models.RolesAuditTrail)
    response = manipulation.delete_multiple(records=json.loads(request.POST.get('items')),
                                            user=request.user.username)
    data = {'response': response}
    return JsonResponse(data)


@require_GET
@login_required
@decorators.permission('us_r', 'us_w', 'us_a', 'us_p')
def users(request):
    context = framework.html_and_data(
        context={'tables': True,
                 'content': 'users',
                 'session': True,
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.Users),
        get_audit_trail=framework.GetAuditTrail(table=models.UserAuditTrail),
        form_render_new=forms.UsersFormNew(),
        form_render_edit=forms.UsersFormEdit())
    context['modal_password_users'] = forms.PasswordFormUsers()
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('us_r', 'us_w', 'us_a', 'us_p')
@decorators.require_ajax
def users_audit_trail(request):
    response, data = framework.GetAuditTrail(
        table=models.UserAuditTrail).get(
        id_ref=models.Users.objects.id(request.GET.get('unique')))
    data = {'response': response,
            'data': data}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('us_w')
@decorators.require_ajax
def users_new(request):
    form = forms.UsersFormNew(request.POST)
    if form.is_valid():
        user = models.Users.objects.create_user(password=form.cleaned_data['password'],
                                                first_name=form.cleaned_data['first_name'],
                                                last_name=form.cleaned_data['last_name'],
                                                is_active=form.cleaned_data['is_active'],
                                                role=form.cleaned_data['role'],
                                                operation_user=request.user.username)
        if user is not None:
            message = 'Success!'
            response = True
        else:
            message = 'Fail!'
            response = False
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_new',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('us_w')
@decorators.require_ajax
def users_edit(request):
    form = forms.UsersFormEdit(request.POST)
    if form.is_valid():
        user = models.Users.objects.update_user(username=form.cleaned_data['username'],
                                                first_name=form.cleaned_data['first_name'],
                                                last_name=form.cleaned_data['last_name'],
                                                role=str(form.cleaned_data['role']),
                                                operation_user=request.user.username)
        if user is not None:
            message = 'Success!'
            response = True
        else:
            message = 'Fail!'
            response = False
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_edit',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('us_p')
@decorators.require_ajax
def users_password(request):
    form = forms.PasswordFormUsers(request.POST)
    if form.is_valid():
        username = form.cleaned_data['user']
        password_new = form.cleaned_data['password_new_users']
        password_repeat = form.cleaned_data['password_repeat_users']
        if password_new == password_repeat:
            user = models.Users.objects.set_initial_password(username=username,
                                                             password=password_new,
                                                             operation_user=request.user.username,
                                                             initial_password=True)
            if user is not None:
                message = 'Success!'
                response = True
            else:
                message = 'Fail!'
                response = False
            data = {'response': response,
                    'message': message}
            return JsonResponse(data)
        else:
            message = 'New password must match.'
            data = {'response': False,
                    'message': message}
            return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_password_users',
                'errors': form.errors}
        return JsonResponse(data)


@require_GET
@login_required
@decorators.permission('us_a')
@decorators.require_ajax
def users_active(request):
    unique = request.GET.get('unique')
    user = models.Users.objects.get(username=unique)
    data = {'response': True,
            'is_active': user.is_active,
            'unique': user.username}
    return JsonResponse(data)


@require_GET
@login_required
@decorators.permission('us_a')
@decorators.require_ajax
def users_activate(request):
    unique = request.GET.get('unique')
    user = models.Users.objects.set_is_active(username=unique,
                                              operation_user=request.user.username,
                                              is_active=True)
    if user is not None:
        message = 'Success!'
        response = True
    else:
        message = 'Fail!'
        response = False
    data = {'response': response,
            'message': message}
    return JsonResponse(data)


@require_GET
@login_required
@decorators.permission('us_a')
@decorators.require_ajax
def users_deactivate(request):
    unique = request.GET.get('unique')
    user = models.Users.objects.set_is_active(username=unique,
                                              operation_user=request.user.username,
                                              is_active=False)
    if user is not None:
        message = 'Success!'
        response = True
    else:
        message = 'Fail!'
        response = False
    data = {'response': response,
            'message': message}
    return JsonResponse(data)


@require_GET
@login_required
@decorators.permission('co_r', 'co_w', 'co_d')
def conditions(request):
    context = framework.html_and_data(
        context={'tables': True,
                 'content': 'conditions',
                 'session': True,
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.Conditions),
        get_audit_trail=framework.GetAuditTrail(table=models.ConditionsAuditTrail),
        form_render_new=forms.ConditionFormNew(),
        form_render_edit=forms.ConditionFormEdit())
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('co_r', 'co_w', 'co_d')
@decorators.require_ajax
def conditions_audit_trail(request):
    response, data = framework.GetAuditTrail(
        table=models.ConditionsAuditTrail).get(
        id_ref=models.Conditions.objects.id(request.GET.get('unique')))
    data = {'response': response,
            'data': data}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('co_w')
@decorators.require_ajax
def conditions_new(request):
    form = forms.ConditionFormNew(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.Conditions,
                                                   table_audit_trail=models.ConditionsAuditTrail)
        response, message = manipulation.new_at(user=request.user.username,
                                                condition=form.cleaned_data['condition'])
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_new',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('co_w')
@decorators.require_ajax
def conditions_edit(request):
    form = forms.ConditionFormEdit(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.Conditions,
                                                   table_audit_trail=models.ConditionsAuditTrail)
        response, message = manipulation.edit_at(user=request.user.username,
                                                 condition=form.cleaned_data['condition'])
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_edit',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('co_d')
@decorators.require_ajax
def conditions_delete(request):
    manipulation = framework.TableManipulation(table=models.Conditions,
                                               table_audit_trail=models.ConditionsAuditTrail)
    response = manipulation.delete_multiple(records=json.loads(request.POST.get('items')),
                                            user=request.user.username)
    data = {'response': response}
    return JsonResponse(data)


@require_GET
@login_required
@decorators.permission('lo_r', 'lo_w', 'lo_d', 'lo_l')
def locations(request):
    context = framework.html_and_data(
        context={'tables': True,
                 'content': 'locations',
                 'session': True,
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.Locations),
        get_audit_trail=framework.GetAuditTrail(table=models.LocationsAuditTrail),
        form_render_new=forms.LocationsFormNew(),
        form_render_edit=forms.LocationsFormEdit())
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('lo_r', 'lo_w', 'lo_d', 'lo_l')
@decorators.require_ajax
def locations_audit_trail(request):
    response, data = framework.GetAuditTrail(
        table=models.LocationsAuditTrail).get(
        id_ref=models.Locations.objects.id(request.GET.get('unique')))
    data = {'response': response,
            'data': data}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('lo_w')
@decorators.require_ajax
def locations_new(request):
    form = forms.LocationsFormNew(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.Locations,
                                                   table_audit_trail=models.LocationsAuditTrail)
        response, message = manipulation.new_identifier_at(user=request.user.username, prefix='L',
                                                           location='L {}'.format(str(timezone.now())),
                                                           name=form.cleaned_data['name'],
                                                           condition=form.cleaned_data['condition'])
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_new',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('lo_w')
@decorators.require_ajax
def locations_edit(request):
    form = forms.LocationsFormEdit(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.Locations,
                                                   table_audit_trail=models.LocationsAuditTrail)
        response, message = manipulation.edit_at(user=request.user.username,
                                                 location=form.cleaned_data['location'],
                                                 name=form.cleaned_data['name'],
                                                 condition=form.cleaned_data['condition'])
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_edit',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('lo_d')
@decorators.require_ajax
def locations_delete(request):
    manipulation = framework.TableManipulation(table=models.Locations,
                                               table_audit_trail=models.LocationsAuditTrail)
    response = manipulation.delete_multiple(records=json.loads(request.POST.get('items')),
                                            user=request.user.username)
    data = {'response': response}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('lo_l')
@decorators.require_ajax
def locations_label(request):
    label = framework.Labels()
    # barcode printing
    response, filename = label.location(unique=request.POST.get('unique'),
                                        version=request.POST.get('version'))
    if response:
        log.info('Label print for "{}" version "{}" was requested.'.format(request.POST.get('unique'),
                                                                           request.POST.get('version')))
        # log record
        manipulation = framework.TableManipulation(table=models.LabelLog)
        manipulation.new_log(unique='label', label=filename.split('/')[3], user=request.user.username, action='print',
                             timestamp=timezone.now())
    data = {'response': response,
            'pdf': filename}
    return JsonResponse(data)


@require_GET
@login_required
@decorators.permission('bo_r', 'bo_w', 'bo_d', 'bo_l')
def boxes(request):
    context = framework.html_and_data(
        context={'tables': True,
                 'content': 'boxes',
                 'session': True,
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.Boxes),
        get_audit_trail=framework.GetAuditTrail(table=models.BoxesAuditTrail),
        form_render_new=forms.BoxesFormNew(),
        form_render_edit=forms.BoxesFormEdit())
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('bo_r', 'bo_w', 'bo_d', 'bo_l')
@decorators.require_ajax
def boxes_audit_trail(request):
    response, data = framework.GetAuditTrail(
        table=models.BoxesAuditTrail).get(
        id_ref=models.Boxes.objects.id(request.GET.get('unique')))
    data = {'response': response,
            'data': data}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('bo_w')
@decorators.require_ajax
def boxes_new(request):
    form = forms.BoxesFormNew(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.Boxes,
                                                   table_audit_trail=models.BoxesAuditTrail)
        response, message = manipulation.new_identifier_at(user=request.user.username, prefix='B',
                                                           box='B {}'.format(str(timezone.now())),
                                                           name=form.cleaned_data['name'],
                                                           alignment=form.cleaned_data['alignment'],
                                                           row_type=form.cleaned_data['row_type'],
                                                           rows=form.cleaned_data['rows'],
                                                           column_type=form.cleaned_data['column_type'],
                                                           columns=form.cleaned_data['columns'],
                                                           origin=form.cleaned_data['origin'])
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_new',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('bo_w')
@decorators.require_ajax
def boxes_edit(request):
    form = forms.BoxesFormEdit(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.Boxes,
                                                   table_audit_trail=models.BoxesAuditTrail)
        response, message = manipulation.edit_at(user=request.user.username,
                                                 box=form.cleaned_data['box'],
                                                 name=form.cleaned_data['name'],
                                                 alignment=form.cleaned_data['alignment'],
                                                 row_type=form.cleaned_data['row_type'],
                                                 rows=form.cleaned_data['rows'],
                                                 column_type=form.cleaned_data['column_type'],
                                                 columns=form.cleaned_data['columns'],
                                                 origin=form.cleaned_data['origin'])
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_edit',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('bo_d')
@decorators.require_ajax
def boxes_delete(request):
    manipulation = framework.TableManipulation(table=models.Boxes,
                                               table_audit_trail=models.BoxesAuditTrail)
    response = manipulation.delete_multiple(records=json.loads(request.POST.get('items')),
                                            user=request.user.username)
    data = {'response': response}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('bo_l')
@decorators.require_ajax
def boxes_label(request):
    label = framework.Labels()
    # barcode printing
    response, filename = label.location(unique=request.POST.get('unique'),
                                        version=request.POST.get('version'))
    if response:
        log.info('Label print for "{}" version "{}" was requested.'.format(request.POST.get('unique'),
                                                                           request.POST.get('version')))
        # log record
        manipulation = framework.TableManipulation(table=models.LabelLog)
        manipulation.new_log(unique='label', label=filename.split('/')[3], user=request.user.username, action='print',
                             timestamp=timezone.now())
    data = {'response': response,
            'pdf': filename}
    return JsonResponse(data)


@require_GET
@login_required
@decorators.permission('sa_r', 'sa_w', 'sa_d', 'sa_l')
def samples(request):
    context = framework.html_and_data(
        context={'tables': True,
                 'content': 'samples',
                 'session': True,
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.Samples),
        get_audit_trail=framework.GetAuditTrail(table=models.SamplesAuditTrail),
        form_render_new=forms.SamplesFormNew(),
        form_render_edit=forms.SamplesFormEdit())
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('sa_r', 'sa_w', 'sa_d', 'sa_l')
@decorators.require_ajax
def samples_audit_trail(request):
    response, data = framework.GetAuditTrail(
        table=models.SamplesAuditTrail).get(
        id_ref=models.Samples.objects.id(request.GET.get('unique')))
    data = {'response': response,
            'data': data}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('sa_w')
@decorators.require_ajax
def samples_new(request):
    form = forms.SamplesFormNew(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.Samples,
                                                   table_audit_trail=models.SamplesAuditTrail)
        for x in range(form.cleaned_data['amount']):
            response, message = manipulation.new_identifier_at(user=request.user.username, prefix='S',
                                                               sample='S {}'.format(str(timezone.now())),
                                                               name=form.cleaned_data['name'],
                                                               type=form.cleaned_data['type'],
                                                               account=form.cleaned_data['account'],
                                                               volume=form.cleaned_data['volume'],
                                                               uom=form.cleaned_data['uom'])
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_new',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('sa_w')
@decorators.require_ajax
def samples_edit(request):
    form = forms.SamplesFormEdit(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.Samples,
                                                   table_audit_trail=models.SamplesAuditTrail)
        response, message = manipulation.edit_at(user=request.user.username,
                                                 sample=form.cleaned_data['sample'],
                                                 name=form.cleaned_data['name'],
                                                 type=form.cleaned_data['type'],
                                                 account=form.cleaned_data['account'],
                                                 volume=form.cleaned_data['volume'],
                                                 uom=form.cleaned_data['uom'])
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_edit',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('sa_d')
@decorators.require_ajax
def samples_delete(request):
        manipulation = framework.TableManipulation(table=models.Samples,
                                                   table_audit_trail=models.SamplesAuditTrail)
        response = manipulation.delete_multiple(records=json.loads(request.POST.get('items')),
                                                user=request.user.username)
        data = {'response': response}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('sa_l')
@decorators.require_ajax
def samples_label(request):
    label = framework.Labels()
    # barcode printing
    response, filename = label.location(unique=request.POST.get('unique'),
                                        version=request.POST.get('version'))
    if response:
        log.info('Label print for "{}" version "{}" was requested.'.format(request.POST.get('unique'),
                                                                           request.POST.get('version')))
        # log record
        manipulation = framework.TableManipulation(table=models.LabelLog)
        manipulation.new_log(unique='label', label=filename.split('/')[3], user=request.user.username, action='print',
                             timestamp=timezone.now())
    data = {'response': response,
            'pdf': filename}
    return JsonResponse(data)


@require_GET
@login_required
@decorators.permission('ac_r', 'ac_w', 'ac_d')
def freeze_thaw_accounts(request):
    context = framework.html_and_data(
        context={'tables': True,
                 'content': 'freeze_thaw_accounts',
                 'session': True,
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.FreezeThawAccounts),
        get_audit_trail=framework.GetAuditTrail(table=models.FreezeThawAccountsAuditTrail),
        form_render_new=forms.FreezeTHawAccountsFormNew(),
        form_render_edit=forms.FreezeThawAccountsFormEdit())
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('ac_r', 'ac_w', 'ac_d')
@decorators.require_ajax
def freeze_thaw_accounts_audit_trail(request):
    response, data = framework.GetAuditTrail(
        table=models.FreezeThawAccountsAuditTrail).get(
        id_ref=models.FreezeThawAccounts.objects.id(request.GET.get('unique')))
    data = {'response': response,
            'data': data}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('ac_w')
@decorators.require_ajax
def freeze_thaw_accounts_new(request):
    form = forms.FreezeTHawAccountsFormNew(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.FreezeThawAccounts,
                                                   table_audit_trail=models.FreezeThawAccountsAuditTrail)
        response, message = manipulation.new_at(user=request.user.username,
                                                account=form.cleaned_data['account'],
                                                freeze_condition=form.cleaned_data['freeze_condition'],
                                                freeze_time=custom.timedelta(
                                                    uom=str(form.cleaned_data['freeze_uom']),
                                                    duration=form.cleaned_data['freeze_time']),
                                                freeze_uom=form.cleaned_data['freeze_uom'],
                                                thaw_condition=form.cleaned_data['thaw_condition'],
                                                thaw_time=custom.timedelta(
                                                    uom=str(form.cleaned_data['thaw_uom']),
                                                    duration=form.cleaned_data['thaw_time']),
                                                thaw_uom=form.cleaned_data['thaw_uom'],
                                                thaw_count=form.cleaned_data['thaw_count'])
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_new',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('ac_w')
@decorators.require_ajax
def freeze_thaw_accounts_edit(request):
    form = forms.FreezeThawAccountsFormEdit(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.FreezeThawAccounts,
                                                   table_audit_trail=models.FreezeThawAccountsAuditTrail)
        response, message = manipulation.edit_at(user=request.user.username,
                                                 account=form.cleaned_data['account'],
                                                 freeze_condition=form.cleaned_data['freeze_condition'],
                                                 freeze_time=custom.timedelta(
                                                     uom=str(form.cleaned_data['freeze_uom']),
                                                     duration=form.cleaned_data['freeze_time']),
                                                 freeze_uom=form.cleaned_data['freeze_uom'],
                                                 thaw_condition=form.cleaned_data['thaw_condition'],
                                                 thaw_time=custom.timedelta(
                                                     uom=str(form.cleaned_data['thaw_uom']),
                                                     duration=form.cleaned_data['thaw_time']),
                                                 thaw_uom=form.cleaned_data['thaw_uom'],
                                                 thaw_count=form.cleaned_data['thaw_count'])
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_edit',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('ac_d')
@decorators.require_ajax
def freeze_thaw_accounts_delete(request):
    manipulation = framework.TableManipulation(table=models.FreezeThawAccounts,
                                               table_audit_trail=models.FreezeThawAccountsAuditTrail)
    response = manipulation.delete_multiple(records=json.loads(request.POST.get('items')),
                                            user=request.user.username)
    data = {'response': response}
    return JsonResponse(data)


@require_GET
@login_required
@decorators.permission('log_mo')
def movement_log(request):
    get_log = framework.GetLog(table=models.MovementLog)
    context = {'tables': True,
               'content': 'movement_log',
               'session': True,
               'user': request.user.username,
               'perm': request.user.permissions,
               'header': get_log.html_header,
               'query': get_log.get()}
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('log_lo')
def login_log(request):
    get_log = framework.GetLog(table=models.LoginLog)
    context = {'tables': True,
               'content': 'login_log',
               'session': True,
               'user': request.user.username,
               'perm': request.user.permissions,
               'header': get_log.html_header,
               'query': get_log.get()}
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('log_la')
def label_log(request):
    get_log = framework.GetLog(table=models.LabelLog)
    context = {'tables': True,
               'content': 'label_log',
               'session': True,
               'user': request.user.username,
               'perm': request.user.permissions,
               'header': get_log.html_header,
               'query': get_log.get()}
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('log_bo')
def boxing_log(request):
    get_log = framework.GetLog(table=models.BoxingLog)
    context = {'tables': True,
               'content': 'boxing_log',
               'session': True,
               'user': request.user.username,
               'perm': request.user.permissions,
               'header': get_log.html_header,
               'query': get_log.get()}
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('home')
def home(request):
    context = {'tables': True,
               'content': 'home',
               'session': True,
               'user': request.user.username,
               'perm': request.user.permissions,
               'modal_movement': forms.MovementsForm(),
               'modal_boxing': forms.BoxingForm(),
               'header': framework.GetView(table=models.RTD).html_header,
               'query': framework.GetView(table=models.RTD).get()}
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('mo')
@decorators.require_ajax
def home_movement(request):
    unique = request.GET.get('unique')
    query_verify = models.RTD.objects.location(unique=unique)
    data = {'response': True,
            'data': query_verify}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('mo')
@decorators.require_ajax
def home_move(request):
    form = forms.MovementsForm(request.POST, request=request)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.MovementLog)
        # we need to know the type of thing we move
        response, message = manipulation.movement(user=request.user.username,
                                                  unique=request.POST.get('unique'),
                                                  new_location=str(form.cleaned_data['new_location'])[:7])
        data = {'response': response,
                'message': message}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_movement',
                'errors': form.errors}
        return JsonResponse(data)


@require_GET
@login_required
@decorators.permission('bo')
@decorators.require_ajax
def home_box(request):
    unique = request.GET.get('unique')
    # check if selected item is a sample
    if unique[:1] == 'B':
        return JsonResponse({'response': False})
    query_verify = models.RTD.objects.box(unique=unique)
    data = {'response': True,
            'data': query_verify}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('bo')
@decorators.require_ajax
def home_boxing(request):
    form = forms.BoxingForm(request.POST, request=request)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.BoxingLog)
        if manipulation.new_log(text='boxing', unique='sample', user=request.user.username,
                                sample=request.POST.get('unique'), box=str(form.cleaned_data.get('new_box'))[:7],
                                position='', timestamp=timezone.now()):
            return JsonResponse({'response': True})
    else:
        data = {'response': False,
                'form_id': 'id_form_boxing',
                'errors': form.errors}
        return JsonResponse(data)
