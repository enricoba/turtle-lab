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
from functools import wraps
# django imports
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
# app imports
from lab.models import EXPORT_PERMISSIONS


def permission(*perms):
    """Permission decorator to validate permissions."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            for perm in perms:
                if request.user.permission(perm):
                    return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapper
    return decorator


def require_ajax(view_func):
    """AJAX decorator to validate the use of ajax."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return view_func(request, *args, **kwargs)
    return wrapper


def export_permission(view_func):
    """Decorator to validate permissions for export"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        perm = EXPORT_PERMISSIONS[kwargs['dialog']]
        if request.user.permission(perm):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper
