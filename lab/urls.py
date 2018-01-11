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


from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),

    # conditions
    url(r'conditions/$', views.conditions, name='conditions'),
    url(r'conditions/new/$', views.conditions_new, name='conditions new'),
    url(r'conditions/edit/$', views.conditions_edit, name='conditions edit'),
    url(r'conditions/delete/$', views.conditions_delete, name='conditions delete'),
    url(r'conditions/audit_trail/$', views.conditions_audit_trail, name='conditions audit trail'),

    # locations
    url(r'locations/$', views.locations, name='locations'),
    url(r'locations/new/$', views.locations_new, name='locations new'),
    url(r'locations/edit/$', views.locations_edit, name='locations edit'),
    url(r'locations/delete/$', views.locations_delete, name='locations delete'),
    url(r'locations/audit_trail/$', views.locations_audit_trail, name='locations audit trail'),

    # boxes
    url(r'boxes/$', views.boxes, name='boxes'),
    url(r'samples/$', views.samples, name='samples'),
    url(r'freeze_thaw_accounts/$', views.freeze_thaw_accounts, name='freeze_thaw_accounts'),
    url(r'movement_log/$', views.movement_log, name='movement_log'),
    url(r'login_log/$', views.login_log, name='login_log'),
    # groups
    url(r'groups/$', views.groups, name='groups'),
    url(r'groups/new/$', views.groups_new, name='groups new'),
    url(r'groups/edit/$', views.groups_edit, name='groups edit'),
    url(r'groups/delete/$', views.groups_delete, name='groups delete'),
    url(r'groups/audit_trail/$', views.groups_audit_trail, name='groups audit trail'),

    url(r'users/$', views.users, name='users'),
    url(r'rtd/$', views.rtd, name='rtd'),
    url(r'logout/$', views.logout_view, name='logout_view'),
]
