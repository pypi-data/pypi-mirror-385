#
# Copyright (c) 2015-2020 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_security_views.api.principal module

This module only provides a small Cornice API to search for principals.
"""

import sys

from colander import MappingSchema, SchemaNode, SequenceSchema, String, drop
from cornice import Service
from cornice.validators import colander_validator
from pyramid.httpexceptions import HTTPOk

from pyams_security.interfaces import ISecurityManager
from pyams_security.interfaces.base import USE_INTERNAL_API_PERMISSION
from pyams_security.rest import check_cors_origin, set_cors_headers
from pyams_security_views.interfaces import REST_PRINCIPALS_SEARCH_ROUTE
from pyams_utils.registry import query_utility
from pyams_utils.rest import BaseResponseSchema, STATUS, rest_responses

__docformat__ = 'restructuredtext'


TEST_MODE = sys.argv[-1].endswith('/test')


class PrincipalsSearchQuery(MappingSchema):
    """Principals search query"""
    term = SchemaNode(String(),
                      description="Principals search string")


class Principal(MappingSchema):
    """Principal result schema"""
    id = SchemaNode(String(),
                    description="Principal ID")
    text = SchemaNode(String(),
                      description="Principal title")


class PrincipalsList(SequenceSchema):
    """Principals search results interface"""
    result = Principal()


class PrincipalsSearchResults(BaseResponseSchema):
    """Principals search results schema"""
    results = PrincipalsList(description="List of principals matching input term",
                             missing=drop)


principals_service = Service(name=REST_PRINCIPALS_SEARCH_ROUTE,
                             pyramid_route=REST_PRINCIPALS_SEARCH_ROUTE,
                             description="Principals management")


@principals_service.options(validators=(check_cors_origin, set_cors_headers))
def principals_options(request):  # pylint: disable=unused-argument
    """Principals service options"""
    return ''


class PrincipalsSearchRequest(MappingSchema):
    """Principals search request"""
    querystring = PrincipalsSearchQuery()


class PrincipalsGetterResponse(MappingSchema):
    """Principals getter response"""
    body = PrincipalsSearchResults()


principals_get_responses = rest_responses.copy()
principals_get_responses[HTTPOk.code] = PrincipalsGetterResponse(
    description="Search results")


@principals_service.get(permission=USE_INTERNAL_API_PERMISSION,
                        schema=PrincipalsSearchRequest(),
                        validators=(check_cors_origin, colander_validator, set_cors_headers),
                        response_schemas=principals_get_responses)
def get_principals(request):
    """Returns list of principals matching given query"""
    params = request.params if TEST_MODE else request.validated.get('querystring', {})
    query = params.get('term')
    if not query:
        return {
            'status': STATUS.ERROR.value,
            'message': "Missing arguments"
        }
    manager = query_utility(ISecurityManager)
    return {
        'status': STATUS.SUCCESS.value,
        'results': [{
            'id': principal.id,
            'text': principal.title
        } for principal in manager.find_principals(query)]
    }
