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
import csv

# django imports
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse, StreamingHttpResponse
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
        return HttpResponseRedirect('/overview/')
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


@require_POST
@decorators.require_ajax
@login_required
def offset(request):
    # get timezone delta from client and set session key
    request.session['offset'] = request.POST.get('dt')
    data = {'response': True}
    return JsonResponse(data)


@require_POST
@decorators.require_ajax
@login_required
def sidebar(request):
    # get sidebar status and set session key
    request.session['sidebar'] = request.POST.get('status')
    data = {'response': True}
    return JsonResponse(data)


@require_GET
@login_required
@decorators.permission('ro_r', 'ro_w', 'ro_d')
def roles(request):
    context = framework.html_and_data(
        context={'tables': True,
                 'content': 'roles',
                 'session': True,
                 'sidebar': request.session.get('sidebar', 'false'),
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.Roles, dt=request.session['offset']),
        get_audit_trail=framework.GetAuditTrail(table=models.RolesAuditTrail, dt=request.session['offset']),
        form_render_new=forms.RolesFormNew(),
        form_render_edit=forms.RolesFormEdit())
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('ro_r', 'ro_w', 'ro_d')
@decorators.require_ajax
def roles_audit_trail(request):
    response, data = framework.GetAuditTrail(
        table=models.RolesAuditTrail, dt=request.session['offset']).get(
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
                 'sidebar': request.session.get('sidebar', 'false'),
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.Users, dt=request.session['offset']),
        get_audit_trail=framework.GetAuditTrail(table=models.UserAuditTrail, dt=request.session['offset']),
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
        table=models.UserAuditTrail, dt=request.session['offset']).get(
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
                 'sidebar': request.session.get('sidebar', 'false'),
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.Conditions, dt=request.session['offset']),
        get_audit_trail=framework.GetAuditTrail(table=models.ConditionsAuditTrail, dt=request.session['offset']),
        form_render_new=forms.ConditionFormNew(),
        form_render_edit=forms.ConditionFormEdit())
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('co_r', 'co_w', 'co_d')
@decorators.require_ajax
def conditions_audit_trail(request):
    response, data = framework.GetAuditTrail(
        table=models.ConditionsAuditTrail, dt=request.session['offset']).get(
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
                 'sidebar': request.session.get('sidebar', 'false'),
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.Locations, dt=request.session['offset']),
        get_audit_trail=framework.GetAuditTrail(table=models.LocationsAuditTrail, dt=request.session['offset']),
        form_render_new=forms.LocationsFormNew(),
        form_render_edit=forms.LocationsFormEdit())
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('lo_r', 'lo_w', 'lo_d', 'lo_l')
@decorators.require_ajax
def locations_audit_trail(request):
    response, data = framework.GetAuditTrail(
        table=models.LocationsAuditTrail, dt=request.session['offset']).get(
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
                                                           condition=form.cleaned_data['condition'],
                                                           max_boxes=form.cleaned_data['max_boxes'])
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
                                                 condition=form.cleaned_data['condition'],
                                                 max_boxes=form.cleaned_data['max_boxes'])
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
    response, filename = label.default(unique=request.POST.get('unique'),
                                       version=request.POST.get('version'),
                                       label='location')
    if response:
        log.info('Label print for "{}" version "{}" was requested.'.format(request.POST.get('unique'),
                                                                           request.POST.get('version')))
        # log record
        manipulation = framework.TableManipulation(table=models.LabelLog)
        manipulation.new_log(unique='label', label=filename.split('/')[3], user=request.user.username,
                             action='print attempt', timestamp=timezone.now())
    data = {'response': response,
            'pdf': filename}
    return JsonResponse(data)


@require_GET
@login_required
@decorators.permission('ty_r', 'ty_w', 'ty_d')
def types(request):
    context = framework.html_and_data(
        context={'tables': True,
                 'content': 'types',
                 'session': True,
                 'sidebar': request.session.get('sidebar', 'false'),
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.Types, dt=request.session['offset']),
        get_audit_trail=framework.GetAuditTrail(table=models.TypesAuditTrail, dt=request.session['offset']),
        form_render_new=forms.TypesFormNew(),
        form_render_edit=forms.TypesFormEdit())
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('ty_r', 'ty_w', 'ty_d')
@decorators.require_ajax
def types_audit_trail(request):
    response, data = framework.GetAuditTrail(
        table=models.TypesAuditTrail, dt=request.session['offset']).get(
        id_ref=models.Types.objects.id(request.GET.get('unique')))
    data = {'response': response,
            'data': data}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('ty_w')
@decorators.require_ajax
def types_new(request):
    form = forms.TypesFormNew(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.Types,
                                                   table_audit_trail=models.TypesAuditTrail)
        response, message = manipulation.new_at(user=request.user.username,
                                                type=form.cleaned_data['type'],
                                                affiliation=form.cleaned_data['affiliation'],
                                                storage_condition=form.cleaned_data['storage_condition'],
                                                usage_condition=form.cleaned_data['usage_condition'])
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
@decorators.permission('ty_w')
@decorators.require_ajax
def types_edit(request):
    form = forms.TypesFormEdit(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.Types,
                                                   table_audit_trail=models.TypesAuditTrail)
        response, message = manipulation.edit_at(user=request.user.username,
                                                 type=form.cleaned_data['type'],
                                                 affiliation=form.cleaned_data['affiliation'],
                                                 storage_condition=form.cleaned_data['storage_condition'],
                                                 usage_condition=form.cleaned_data['usage_condition'])
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
@decorators.permission('ty_d')
@decorators.require_ajax
def types_delete(request):
    manipulation = framework.TableManipulation(table=models.Types,
                                               table_audit_trail=models.TypesAuditTrail)
    response = manipulation.delete_multiple(records=json.loads(request.POST.get('items')),
                                            user=request.user.username)
    data = {'response': response}
    return JsonResponse(data)


#########
# BOXES #
#########


@require_GET
@login_required
@decorators.permission('bo_r', 'bo_w', 'bo_d', 'bo_l')
def boxes(request):
    context = framework.html_and_data(
        context={'tables': True,
                 'content': 'boxes',
                 'session': True,
                 'sidebar': request.session.get('sidebar', 'false'),
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.Boxes, dt=request.session['offset']),
        get_audit_trail=framework.GetAuditTrail(table=models.BoxesAuditTrail, dt=request.session['offset']),
        form_render_new=forms.BoxesFormNew(),
        form_render_edit=forms.BoxesFormEdit())
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('bo_r', 'bo_w', 'bo_d', 'bo_l')
@decorators.require_ajax
def boxes_audit_trail(request):
    response, data = framework.GetAuditTrail(
        table=models.BoxesAuditTrail, dt=request.session['offset']).get(
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
        response, created_box = manipulation.new_identifier_at(user=request.user.username, prefix='B',
                                                               box='B {}'.format(str(timezone.now())),
                                                               name=form.cleaned_data['name'],
                                                               box_type=form.cleaned_data['box_type'],
                                                               type=form.cleaned_data['type'])
        if response:
            query = models.BoxTypes.objects.filter(box_type=form.cleaned_data['box_type'])[0]
            _max = models.BoxTypes.objects.max(form.cleaned_data['box_type'])
            manipulation_boxing = framework.TableManipulation(table=models.Boxing)
            _success_list = list()
            for x in range(_max):
                _position = custom.determine_box_position(alignment=query.alignment, x=query.columns, y=query.rows,
                                                          value=x + 1)
                _success = manipulation_boxing.new_boxing(object='', box=created_box, position=_position)
                _success_list.append(_success)
            response = custom.check_equal(_success_list)

        data = {'response': response,
                'message': created_box}
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
                                                 box_type=form.cleaned_data['box_type'],
                                                 type=form.cleaned_data['type'])
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
    response, filename = label.default(unique=request.POST.get('unique'),
                                       version=request.POST.get('version'),
                                       label='box')
    if response:
        log.info('Label print for "{}" version "{}" was requested.'.format(request.POST.get('unique'),
                                                                           request.POST.get('version')))
        # log record
        manipulation = framework.TableManipulation(table=models.LabelLog)
        manipulation.new_log(unique='label', label=filename.split('/')[3], user=request.user.username,
                             action='print attempt', timestamp=timezone.now())
    data = {'response': response,
            'pdf': filename}
    return JsonResponse(data)


###################
# TYPE ATTRIBUTES #
###################


@require_GET
@login_required
@decorators.permission('ta_r', 'ta_w', 'ta_d')
def type_attributes(request):
    context = framework.html_and_data(
        context={'tables': True,
                 'content': 'type_attributes',
                 'session': True,
                 'sidebar': request.session.get('sidebar', 'false'),
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.TypeAttributes, dt=request.session['offset']),
        get_audit_trail=framework.GetAuditTrail(table=models.TypeAttributesAuditTrail, dt=request.session['offset']),
        form_render_new=forms.TypeAttributesFormNew(),
        form_render_edit=forms.TypeAttributesFormEdit())
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('ta_r', 'ta_w', 'ta_d')
@decorators.require_ajax
def type_attributes_audit_trail(request):
    response, data = framework.GetAuditTrail(
        table=models.TypeAttributesAuditTrail, dt=request.session['offset']).get(
        id_ref=models.TypeAttributes.objects.id(request.GET.get('unique')))
    data = {'response': response,
            'data': data}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('ta_w')
@decorators.require_ajax
def type_attributes_new(request):
    form = forms.TypeAttributesFormNew(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.TypeAttributes,
                                                   table_audit_trail=models.TypeAttributesAuditTrail)
        response, created_box = manipulation.new_at(user=request.user.username,
                                                    column=form.cleaned_data['column'],
                                                    type=form.cleaned_data['type'],
                                                    list_values=form.cleaned_data['list_values'],
                                                    default_value=form.cleaned_data['default_value'],
                                                    mandatory=form.cleaned_data['mandatory'])
        data = {'response': response,
                'message': created_box}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_new',
                'errors': form.errors}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('ta_w')
@decorators.require_ajax
def type_attributes_edit(request):
    form = forms.TypeAttributesFormEdit(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.TypeAttributes,
                                                   table_audit_trail=models.TypeAttributesAuditTrail)
        response, message = manipulation.edit_at(user=request.user.username,
                                                 column=form.cleaned_data['column'],
                                                 type=form.cleaned_data['type'],
                                                 list_values=form.cleaned_data['list_values'],
                                                 default_value=form.cleaned_data['default_value'],
                                                 mandatory=form.cleaned_data['mandatory'])
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
@decorators.permission('ta_d')
@decorators.require_ajax
def type_attributes_delete(request):
    manipulation = framework.TableManipulation(table=models.TypeAttributes,
                                               table_audit_trail=models.TypeAttributesAuditTrail)
    response = manipulation.delete_multiple(records=json.loads(request.POST.get('items')),
                                            user=request.user.username)
    data = {'response': response}
    return JsonResponse(data)

#############
# BOX TYPES #
#############


@require_GET
@login_required
@decorators.permission('bt_r', 'bt_w', 'bt_d')
def box_types(request):
    context = framework.html_and_data(
        context={'tables': True,
                 'content': 'box_types',
                 'session': True,
                 'sidebar': request.session.get('sidebar', 'false'),
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetStandard(table=models.BoxTypes, dt=request.session['offset']),
        get_audit_trail=framework.GetAuditTrail(table=models.BoxTypesAuditTrail, dt=request.session['offset']),
        form_render_new=forms.BoxTypesFormNew(),
        form_render_edit=forms.BoxTypesFormEdit())
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('bt_r', 'bt_w', 'bt_d')
@decorators.require_ajax
def box_types_audit_trail(request):
    response, data = framework.GetAuditTrail(
        table=models.BoxTypesAuditTrail, dt=request.session['offset']).get(
        id_ref=models.BoxTypes.objects.id(request.GET.get('unique')))
    data = {'response': response,
            'data': data}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('bt_w')
@decorators.require_ajax
def box_types_new(request):
    form = forms.BoxTypesFormNew(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.BoxTypes,
                                                   table_audit_trail=models.BoxTypesAuditTrail)
        response, message = manipulation.new_at(user=request.user.username,
                                                box_type=form.cleaned_data['box_type'],
                                                alignment=form.cleaned_data['alignment'],
                                                rows=form.cleaned_data['rows'].capitalize(),
                                                columns=form.cleaned_data['columns'].capitalize(),
                                                default=form.cleaned_data['default'])
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
@decorators.permission('bt_w')
@decorators.require_ajax
def box_types_edit(request):
    form = forms.BoxTypesFormEdit(request.POST)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.BoxTypes,
                                                   table_audit_trail=models.BoxTypesAuditTrail)
        response, message = manipulation.edit_at(user=request.user.username,
                                                 box_type=form.cleaned_data['box_type'],
                                                 alignment=form.cleaned_data['alignment'],
                                                 rows=form.cleaned_data['rows'],
                                                 columns=form.cleaned_data['columns'],
                                                 default=form.cleaned_data['default'])
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
@decorators.permission('bt_d')
@decorators.require_ajax
def box_types_delete(request):
    manipulation = framework.TableManipulation(table=models.BoxTypes,
                                               table_audit_trail=models.BoxTypesAuditTrail)
    response = manipulation.delete_multiple(records=json.loads(request.POST.get('items')),
                                            user=request.user.username)
    data = {'response': response}
    return JsonResponse(data)


###########
# SAMPLES #
###########

"""
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
                                                               account=form.cleaned_data['account'])
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
                                                 account=form.cleaned_data['account'])
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
"""


############
# REAGENTS #
############


@require_GET
@login_required
@decorators.permission('re_r', 're_w', 're_d', 're_l')
def reagents(request, reagent):
    context = framework.html_and_data(
        context={'tables': True,
                 'content': 'reagents',
                 'content_dynamic': reagent,
                 'type_attributes': models.TypeAttributes.objects.all_list_exchanged(type=reagent),
                 'session': True,
                 'sidebar': request.session.get('sidebar', 'false'),
                 'user': request.user.username,
                 'perm': request.user.permissions},
        get_standard=framework.GetDynamic(table=models.Reagents, dynamic_table=models.DynamicReagents, type=reagent),
        get_audit_trail=framework.GetDynamicAuditTrail(table=models.ReagentsAuditTrail,
                                                       dynamic_table=models.DynamicReagentsAuditTrail,
                                                       type=reagent, dt=request.session['offset']),
        form_render_new=forms.ReagentsFormNew(),
        form_render_edit=forms.ReagentsFormEdit())
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('re_r', 're_w', 're_d', 're_l')
@decorators.require_ajax
def reagents_audit_trail(request, reagent):
    response, data = framework.GetDynamicAuditTrail(table=models.ReagentsAuditTrail,
                                                    dynamic_table=models.DynamicReagentsAuditTrail,
                                                    type=reagent, dt=request.session['offset']).get(
        id_ref=models.Reagents.objects.id(request.GET.get('unique')))
    data = {'response': response,
            'data': data}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('re_w')
@decorators.require_ajax
def reagents_new(request, reagent):
    form = forms.ReagentsFormNew(request.POST, request=request, type=reagent)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.Reagents,
                                                   table_audit_trail=models.ReagentsAuditTrail)
        response, message = manipulation.new_identifier_at(user=request.user.username, prefix='R',
                                                           reagent='R {}'.format(str(timezone.now())),
                                                           name=form.cleaned_data['name'],
                                                           type=reagent)
        if response:
            manipulation_dynamic = framework.TableManipulation(table=models.DynamicReagents,
                                                               table_audit_trail=models.DynamicReagentsAuditTrail)
            _success_list = list()
            for field in models.TypeAttributes.objects.columns_as_list(type=reagent):
                response, message = manipulation_dynamic.new_dynamic_at(user=request.user.username,
                                                                        identifier=manipulation.unique_value,
                                                                        main_version=manipulation.version,
                                                                        timestamp=manipulation.timestamp,
                                                                        id_main=manipulation.id,
                                                                        type_attribute=field,
                                                                        value=request.POST.get(field))
                _success_list.append(response)
            response = custom.check_equal(_success_list)
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
@decorators.permission('re_w')
@decorators.require_ajax
def reagents_edit(request, reagent):
    form = forms.ReagentsFormEdit(request.POST, request=request, type=reagent)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.Reagents,
                                                   table_audit_trail=models.ReagentsAuditTrail)
        response, message = manipulation.edit_at(user=request.user.username,
                                                 reagent=form.cleaned_data['reagent'],
                                                 name=form.cleaned_data['name'],
                                                 type=reagent)
        if response:
            manipulation_dynamic = framework.TableManipulation(table=models.DynamicReagents,
                                                               table_audit_trail=models.DynamicReagentsAuditTrail)
            _success_list = list()
            for field in models.TypeAttributes.objects.columns_as_list(type=reagent):
                response, message = manipulation_dynamic.edit_dynamic_at(user=request.user.username,
                                                                         identifier=manipulation.unique_value,
                                                                         main_version=manipulation.version,
                                                                         timestamp=manipulation.timestamp,
                                                                         id_main=manipulation.id,
                                                                         type_attribute=field,
                                                                         value=request.POST.get(field))
                _success_list.append(response)
            response = custom.check_equal(_success_list)
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
@decorators.permission('re_d')
@decorators.require_ajax
def reagents_delete(request):
        manipulation = framework.TableManipulation(table=models.Reagents,
                                                   table_audit_trail=models.ReagentsAuditTrail)
        manipulation_boxing = framework.TableManipulation(table=models.Boxing)
        # individual loop for deleting reagents to clear boxing list
        _success_list = list()
        for item in json.loads(request.POST.get('items')):
            box = models.Overview.objects.box(unique=item)
            position = models.Overview.objects.position(unique=item)
            response = manipulation.delete_at(record=item, user=request.user.username)
            if box and response:
                response = manipulation_boxing.clear_boxing(box=box, object='', position=position)
            _success_list.append(response)
        response = custom.check_equal(_success_list)

        """if response:
            manipulation_dynamic = framework.TableManipulation(table=models.DynamicReagents,
                                                               table_audit_trail=models.DynamicReagentsAuditTrail)
            print(manipulation.id)
            # manipulation_dynamic.delete_dynamic(id_main=manipulation.id, identifier=manipulation.unique_value,
            #                                     timestamp=manipulation.timestamp)
        _success_list = list()
        print(request.POST.get('items'))"""
        data = {'response': response}
        return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('re_l')
@decorators.require_ajax
def reagents_label(request):
    label = framework.Labels()
    # barcode printing
    response, filename = label.default(unique=request.POST.get('unique'),
                                       version=request.POST.get('version'),
                                       label='reagent')
    if response:
        log.info('Label print for "{}" version "{}" was requested.'.format(request.POST.get('unique'),
                                                                           request.POST.get('version')))
        # log record
        manipulation = framework.TableManipulation(table=models.LabelLog)
        manipulation.new_log(unique='label', label=filename.split('/')[3], user=request.user.username,
                             action='print attempt', timestamp=timezone.now())
    data = {'response': response,
            'pdf': filename}
    return JsonResponse(data)


############
# ACCOUNTS #
############
"""

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
"""


@require_GET
@login_required
@decorators.permission('log_mo')
def movement_log(request):
    get_log = framework.GetLog(table=models.MovementLog, dt=request.session['offset'])
    context = {'tables': True,
               'content': 'movement_log',
               'session': True,
               'sidebar': request.session.get('sidebar', 'false'),
               'user': request.user.username,
               'perm': request.user.permissions,
               'header': get_log.html_header,
               'query': get_log.get(),
               'reagents': models.Types.objects.filter(affiliation='Reagents').values_list('type', flat=True),
               'samples': models.Types.objects.filter(affiliation='Samples').values_list('type', flat=True)}
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('log_lo')
def login_log(request):
    get_log = framework.GetLog(table=models.LoginLog, dt=request.session['offset'])
    context = {'tables': True,
               'content': 'login_log',
               'session': True,
               'sidebar': request.session.get('sidebar', 'false'),
               'user': request.user.username,
               'perm': request.user.permissions,
               'header': get_log.html_header,
               'query': get_log.get(),
               'reagents': models.Types.objects.filter(affiliation='Reagents').values_list('type', flat=True),
               'samples': models.Types.objects.filter(affiliation='Samples').values_list('type', flat=True)}
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('log_la')
def label_log(request):
    get_log = framework.GetLog(table=models.LabelLog, dt=request.session['offset'])
    context = {'tables': True,
               'content': 'label_log',
               'session': True,
               'sidebar': request.session.get('sidebar', 'false'),
               'user': request.user.username,
               'perm': request.user.permissions,
               'header': get_log.html_header,
               'query': get_log.get(),
               'reagents': models.Types.objects.filter(affiliation='Reagents').values_list('type', flat=True),
               'samples': models.Types.objects.filter(affiliation='Samples').values_list('type', flat=True)}
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('log_bo')
def boxing_log(request):
    get_log = framework.GetLog(table=models.BoxingLog, dt=request.session['offset'])
    context = {'tables': True,
               'content': 'boxing_log',
               'session': True,
               'sidebar': request.session.get('sidebar', 'false'),
               'user': request.user.username,
               'perm': request.user.permissions,
               'header': get_log.html_header,
               'query': get_log.get(),
               'reagents': models.Types.objects.filter(affiliation='Reagents').values_list('type', flat=True),
               'samples': models.Types.objects.filter(affiliation='Samples').values_list('type', flat=True)}
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('overview')
def overview(request):
    context = {'tables': True,
               'content': 'overview',
               'session': True,
               'sidebar': request.session.get('sidebar', 'false'),
               'user': request.user.username,
               'perm': request.user.permissions,
               'modal_overview_boxing': forms.OverviewBoxingForm(),
               'modal_movement': forms.MovementsForm(),
               'header': framework.GetView(table=models.Overview).html_header,
               'query': framework.GetView(table=models.Overview).get(),
               'reagents': models.Types.objects.filter(affiliation='Reagents').values_list('type', flat=True),
               'samples': models.Types.objects.filter(affiliation='Samples').values_list('type', flat=True)}
    return render(request, 'lab/index.html', context)


@require_GET
@login_required
@decorators.permission('mo')
@decorators.require_ajax
def overview_movement(request):
    unique = request.GET.get('unique')
    affiliation = models.Overview.objects.affiliation(unique=unique)
    if affiliation != 'box':
        data = {'response': False}
        return JsonResponse(data)
    location = models.Overview.objects.location(unique=unique)
    if not location:
        location = '---'
    targets = models.Locations.objects.locations_by_type(type=models.Overview.objects.type(unique=unique))
    tmp_dict = dict()
    if targets:
        for idx, target in enumerate(targets):
            keys = ['value', 'text']
            values = [target.id, target.__str__()]
            tmp_dict['Option{}'.format(idx)] = dict(zip(keys, values))
    else:
        keys = ['value', 'text']
        values = ['---', '---']
        tmp_dict['Option0'] = dict(zip(keys, values))
    data = {'response': True,
            'location': location,
            'targets': tmp_dict}
    return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('mo')
@decorators.require_ajax
def overview_move(request):
    form = forms.MovementsForm(request.POST, request=request)
    if form.is_valid():
        manipulation = framework.TableManipulation(table=models.MovementLog)
        timestamp = timezone.now()
        box = request.POST.get('unique')[:7]
        response = manipulation.move(user=request.user.username,
                                     obj=box,
                                     method='manual',
                                     initial_location=str(form.cleaned_data['actual_location'])[:7],
                                     new_location=str(form.cleaned_data['new_location'])[:7],
                                     timestamp=timestamp)

        if response:
            manipulation_more = framework.TableManipulation(table=models.MovementLog)
            _success_list = list()
            boxed_objects = models.Overview.objects.filter(box=box)
            for obj in boxed_objects:
                response = manipulation_more.move(user=request.user.username,
                                                  obj=obj,
                                                  method=box,
                                                  initial_location=str(form.cleaned_data['actual_location'])[:7],
                                                  new_location=str(form.cleaned_data['new_location'])[:7],
                                                  timestamp=timestamp)
                _success_list.append(response)
            response = custom.check_equal(_success_list)
        data = {'response': response}
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
def overview_locate(request):
    affiliation = models.Overview.objects.affiliation(unique=request.GET.get('unique'))
    if affiliation == 'box':
        data = {'response': False}
        return JsonResponse(data)
    _type = models.Overview.objects.type(unique=request.GET.get('unique'))
    box_count = models.Boxes.objects.count_box_by_type(type=_type)
    count_mixed = models.Boxes.objects.count_box_by_type(type='')
    if box_count == 0 and count_mixed == 0:
        data = {'response': True,
                'location': '---',
                'box': '---',
                'position': '---'}
        return JsonResponse(data)
    else:
        # if dedicated boxes exist first check them
        if box_count > 0:
            # check dedicated boxes
            for x in range(box_count):
                box = models.Boxes.objects.box_by_type(type=_type, count=x)
                position = models.Boxing.objects.next_position(box=box[:7])
                location = models.Overview.objects.location(unique=box[:7])
                if not location:
                    location = '---'
                if position:
                    data = {'response': True,
                            'location': location,
                            'box': box,
                            'position': position}
                    return JsonResponse(data)
            # if no return happened, check if mixes boxes exist
            if count_mixed > 0:
                for x in range(count_mixed):
                    box = models.Boxes.objects.box_by_type(type='', count=x)
                    position = models.Boxing.objects.next_position(box=box[:7])
                    location = models.Overview.objects.location(unique=box[:7])
                    if not location:
                        location = '---'
                    if position:
                        data = {'response': True,
                                'location': location,
                                'box': box,
                                'position': position}
                        return JsonResponse(data)
                # no position in mixed boxes return nothing
                data = {'response': True,
                        'location': '---',
                        'box': '---',
                        'position': '---'}
                return JsonResponse(data)
            # return nothing if no mixed boxes available
            else:
                data = {'response': True,
                        'location': '---',
                        'box': '---',
                        'position': '---'}
                return JsonResponse(data)
        if count_mixed > 0:
            for x in range(count_mixed):
                box = models.Boxes.objects.box_by_type(type='', count=x)
                position = models.Boxing.objects.next_position(box=box[:7])
                location = models.Overview.objects.location(unique=box[:7])
                if not location:
                    location = '---'
                if position:
                    data = {'response': True,
                            'location': location,
                            'box': box,
                            'position': position}
                    return JsonResponse(data)
            # no position in mixed boxes return nothing
            data = {'response': True,
                    'location': '---',
                    'box': '---',
                    'position': '---'}
            return JsonResponse(data)


@require_POST
@login_required
@decorators.permission('bo')
@decorators.require_ajax
def overview_boxing(request):
    form = forms.OverviewBoxingForm(request.POST, request=request)
    if form.is_valid():
        # log record
        manipulation = framework.TableManipulation(table=models.Boxing)
        response = manipulation.edit_boxing(box=form.cleaned_data['box'],
                                            object=request.POST.get('unique'),
                                            position=request.POST.get('target_position'))
        if response:
            # log record
            manipulation_log = framework.TableManipulation(table=models.BoxingLog)
            manipulation_log.new_log(object=request.POST.get('unique'),
                                     user=request.user.username,
                                     box=form.cleaned_data['box'],
                                     position=request.POST.get('target_position'),
                                     timestamp=timezone.now())
        data = {'response': response}
        return JsonResponse(data)
    else:
        data = {'response': False,
                'form_id': 'id_form_overview_boxing',
                'errors': form.errors}
        return JsonResponse(data)


@require_GET
@login_required
@decorators.export_permission
def export(request, dialog):
    if dialog == 'home':
        queryset = framework.GetView(table=models.RTD)
        data = queryset.export
    elif dialog == 'overview':
        queryset = framework.GetView(table=models.Overview)
        data = queryset.export
    else:
        table = models.TABLES[dialog]
        queryset = framework.GetStandard(table=table)
        data = queryset.export
    # write pseudo buffer for streaming
    pseudo_buffer = custom.Echo()
    writer = csv.writer(pseudo_buffer, delimiter=';')
    # response
    response = StreamingHttpResponse((writer.writerow(row) for row in data), content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(dialog)
    return response


@require_GET
@login_required
@decorators.export_permission
def export_reagents(request, reagent, dialog):
    queryset = framework.GetDynamic(table=models.Reagents, dynamic_table=models.DynamicReagents, type=reagent)
    data = queryset.export
    # write pseudo buffer for streaming
    pseudo_buffer = custom.Echo()
    writer = csv.writer(pseudo_buffer, delimiter=';')
    # response
    response = StreamingHttpResponse((writer.writerow(row) for row in data), content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(reagent)
    return response


""""@require_POST
@login_required
def import_data(request, dialog):
    pass"""
