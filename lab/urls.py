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
    # export
    url(r'^export/(?P<dialog>\w+)/$', views.export, name='export'),
    url(r'^import/(?P<dialog>\w+)/$', views.import_data, name='import'),
    # index
    url(r'^$', views.index, name='index'),
    url(r'^index/login/$', views.index_login, name='index login'),
    url(r'^index/password/$', views.index_password, name='index password'),
    url(r'^index/logout/$', views.index_logout, name='index logout'),
    # conditions
    url(r'^conditions/$', views.conditions, name='conditions'),
    url(r'^conditions/new/$', views.conditions_new, name='conditions new'),
    url(r'^conditions/edit/$', views.conditions_edit, name='conditions edit'),
    url(r'^conditions/delete/$', views.conditions_delete, name='conditions delete'),
    url(r'^conditions/audit_trail/$', views.conditions_audit_trail, name='conditions audit trail'),
    # types
    url(r'^types/$', views.types, name='types'),
    url(r'^types/new/$', views.types_new, name='types new'),
    url(r'^types/edit/$', views.types_edit, name='types edit'),
    url(r'^types/delete/$', views.types_delete, name='types delete'),
    url(r'^types/audit_trail/$', views.types_audit_trail, name='types audit trail'),
    # type attributes
    url(r'^type_attributes/$', views.type_attributes, name='type attributes'),
    url(r'^type_attributes/new/$', views.type_attributes_new, name='type attributes new'),
    url(r'^type_attributes/edit/$', views.type_attributes_edit, name='type attributes edit'),
    url(r'^type_attributes/delete/$', views.type_attributes_delete, name='type attributes delete'),
    url(r'^type_attributes/audit_trail/$', views.type_attributes_audit_trail, name='type attributes audit trail'),
    # locations
    url(r'^locations/$', views.locations, name='locations'),
    url(r'^locations/new/$', views.locations_new, name='locations new'),
    url(r'^locations/edit/$', views.locations_edit, name='locations edit'),
    url(r'^locations/delete/$', views.locations_delete, name='locations delete'),
    url(r'^locations/audit_trail/$', views.locations_audit_trail, name='locations audit trail'),
    url(r'^locations/label/$', views.locations_label, name='locations label'),
    # boxes
    url(r'^boxes/$', views.boxes, name='boxes'),
    url(r'^boxes/new/$', views.boxes_new, name='boxes new'),
    url(r'^boxes/edit/$', views.boxes_edit, name='boxes edit'),
    url(r'^boxes/delete/$', views.boxes_delete, name='boxes delete'),
    url(r'^boxes/audit_trail/$', views.boxes_audit_trail, name='boxes audit trail'),
    url(r'^boxes/label/$', views.boxes_label, name='boxes label'),
    # box types
    url(r'^box_types/$', views.box_types, name='box types'),
    url(r'^box_types/new/$', views.box_types_new, name='box types new'),
    url(r'^box_types/edit/$', views.box_types_edit, name='box types edit'),
    url(r'^box_types/delete/$', views.box_types_delete, name='box types delete'),
    url(r'^box_types/audit_trail/$', views.box_types_audit_trail, name='box types audit trail'),
    # samples
    # url(r'^samples/$', views.samples, name='samples'),
    # url(r'^samples/new/$', views.samples_new, name='samples new'),
    # url(r'^samples/edit/$', views.samples_edit, name='samples edit'),
    # url(r'^samples/delete/$', views.samples_delete, name='samples delete'),
    # url(r'^samples/audit_trail/$', views.samples_audit_trail, name='samples audit trail'),
    # url(r'^samples/label/$', views.samples_label, name='samples label'),
    # reagents
    url(r'^reagents/$', views.reagents, name='reagents'),
    url(r'^reagents/new/$', views.reagents_new, name='reagents new'),
    url(r'^reagents/edit/$', views.reagents_edit, name='reagents edit'),
    url(r'^reagents/delete/$', views.reagents_delete, name='reagents delete'),
    url(r'^reagents/audit_trail/$', views.reagents_audit_trail, name='reagents audit trail'),
    url(r'^reagents/label/$', views.reagents_label, name='reagents label'),
    # accounts
    # url(r'^freeze_thaw_accounts/$', views.freeze_thaw_accounts, name='freeze_thaw_accounts'),
    # url(r'^freeze_thaw_accounts/new/$', views.freeze_thaw_accounts_new, name='freeze_thaw_accounts new'),
    # url(r'^freeze_thaw_accounts/edit/$', views.freeze_thaw_accounts_edit, name='freeze_thaw_accounts edit'),
    # url(r'^freeze_thaw_accounts/delete/$', views.freeze_thaw_accounts_delete, name='freeze_thaw_accounts delete'),
    # url(r'^freeze_thaw_accounts/audit_trail/$', views.freeze_thaw_accounts_audit_trail, name='freeze_thaw_accounts audit trail'),
    # logs
    url(r'^movement_log/$', views.movement_log, name='movement log'),
    url(r'^login_log/$', views.login_log, name='login log'),
    url(r'^label_log/$', views.label_log, name='label log'),
    url(r'^boxing_log/$', views.boxing_log, name='boxing log'),
    # roles
    url(r'^roles/$', views.roles, name='roles'),
    url(r'^roles/new/$', views.roles_new, name='roles new'),
    url(r'^roles/edit/$', views.roles_edit, name='roles edit'),
    url(r'^roles/delete/$', views.roles_delete, name='roles delete'),
    url(r'^roles/audit_trail/$', views.roles_audit_trail, name='roles audit trail'),
    # users
    url(r'^users/$', views.users, name='users'),
    url(r'^users/new/$', views.users_new, name='users new'),
    url(r'^users/edit/$', views.users_edit, name='users edit'),
    url(r'^users/password/$', views.users_password, name='users password'),
    url(r'^users/audit_trail/$', views.users_audit_trail, name='users audit trail'),
    url(r'^users/active/$', views.users_active, name='users active'),
    url(r'^users/activate/$', views.users_activate, name='users activate'),
    url(r'^users/deactivate/$', views.users_deactivate, name='users deactivate'),
    # rtd
    # url(r'^home/$', views.home, name='home'),
    # url(r'^home/movement/$', views.home_movement, name='home movement'),
    # url(r'^home/move/$', views.home_move, name='home move'),
    # url(r'^home/box/$', views.home_box, name='home box'),
    # url(r'^home/boxing/$', views.home_boxing, name='home boxing'),
    # overview
    url(r'^overview/$', views.overview, name='overview'),
    url(r'^overview/boxing/$', views.overview_boxing, name='overview boxing'),
    url(r'^overview/locate/$', views.overview_locate, name='overview locate')
]
