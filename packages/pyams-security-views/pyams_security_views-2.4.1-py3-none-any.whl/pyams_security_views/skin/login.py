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

"""PyAMS_security_views.skin.login module

This module defines login and modal login views.
These views are automatically associated with Pyramid forbidden views.
"""

from pyramid.csrf import new_csrf_token
from pyramid.decorator import reify
from pyramid.events import subscriber
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from pyramid.response import Response
from pyramid.security import forget, remember
from pyramid.view import forbidden_view_config, view_config
from zope.interface import Interface, Invalid, implementer
from zope.schema.fieldproperty import FieldProperty

from pyams_form.ajax import ajax_form_config
from pyams_form.button import Buttons, handler
from pyams_form.field import Fields
from pyams_form.form import AddForm
from pyams_form.interfaces import HIDDEN_MODE
from pyams_form.interfaces.form import IAJAXFormRenderer, IDataExtractedEvent
from pyams_i18n.interfaces import II18n
from pyams_layer.interfaces import IPyAMSLayer
from pyams_layer.skin import apply_skin
from pyams_security.credential import Credentials
from pyams_security.interfaces import ISecurityManager, LOGIN_REFERER_KEY
from pyams_security.interfaces.plugin import AuthenticatedPrincipalEvent
from pyams_security.interfaces.profile import IUserRegistrationViews
from pyams_security_views.interfaces.login import ILoginConfiguration, ILoginFormButtons, \
    ILoginFormFields, ILoginPageTarget, ILoginView, IModalLoginFormButtons
from pyams_skin.interfaces.view import IModalFullPage, IModalPage
from pyams_skin.interfaces.viewlet import IFooterViewletManager, IHeaderViewletManager
from pyams_template.template import template_config
from pyams_utils.adapter import ContextRequestViewAdapter, NullAdapter, adapter_config
from pyams_utils.interfaces.data import IObjectData
from pyams_utils.registry import query_utility
from pyams_utils.text import text_to_html
from pyams_viewlet.manager import viewletmanager_config
from pyams_viewlet.viewlet import Viewlet, viewlet_config
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.zmi.viewlet.toolbar import ModalToolbarViewletManager

__docformat__ = 'restructuredtext'

from pyams_security_views import _  # pylint: disable=ungrouped-imports


@forbidden_view_config(request_type=IPyAMSLayer)
def ForbiddenView(request):  # pylint: disable=invalid-name
    """Default forbidden view"""
    request.session[LOGIN_REFERER_KEY] = request.url
    return HTTPFound('login.html?forbidden=true')


@forbidden_view_config(request_type=IPyAMSLayer, renderer='json', xhr=True)
def ForbiddenAJAXView(request):  # pylint: disable=invalid-name
    """AJAX forbidden view"""
    request.response.status = HTTPForbidden.code
    return {
        'status': 'modal',
        'location': 'login-dialog.html?forbidden=true'
    }


def get_login_buttons(interface, request):
    """Login buttons getter"""
    buttons = Buttons(interface)
    login_configuration = ILoginConfiguration(request.root)
    if not login_configuration.open_registration:
        buttons = buttons.omit('register')
    if not login_configuration.allow_password_reset:
        buttons = buttons.omit('reset_password')
    return buttons


@ajax_form_config(name='login.html',
                  layer=IPyAMSLayer)  # pylint: disable=abstract-method
@implementer(IModalFullPage, ILoginView, IObjectData)
class LoginForm(AddForm):
    """Login form"""

    prefix = 'login_form.'
    legend = _("Please enter valid credentials")

    modal_class = FieldProperty(IModalFullPage['modal_class'])
    modal_content_class = FieldProperty(IModalFullPage['modal_content_class'])

    fields = Fields(ILoginFormFields)

    def __init__(self, context, request):
        super().__init__(context, request)
        login_config = ILoginConfiguration(self.request.root)
        apply_skin(self.request, login_config.skin)

    @reify
    def title(self):
        """Form title getter"""
        if 'forbidden' in self.request.params:
            return _("You must authenticate")
        return None

    @property
    def title_class(self):
        return 'alert alert-info' if self.title else ''

    @property
    def buttons(self):
        """Form buttons getter"""
        return get_login_buttons(ILoginFormButtons, self.request)

    edit_permission = None

    object_data = {
        'ams-warn-on-change': False,
        'ams-modules': 'callbacks helpers',
        'ams-callback': 'MyAMS.helpers.setLoginHash'
    }

    def update(self):
        super().update()
        new_csrf_token(self.request)

    def update_actions(self):
        super().update_actions()
        registration_views = self.request.registry.queryMultiAdapter((self.context, self.request),
                                                                     IUserRegistrationViews)
        action = self.actions.get('register')
        if action is not None:
            if registration_views is None:
                action.add_class('hidden')
            else:
                action.add_class('btn-info')
                if 'reset_password' not in self.actions:
                    action.add_class('mr-sm-auto')
                action.href = registration_views.register_view
        action = self.actions.get('reset_password')
        if action is not None:
            if registration_views is None:
                action.add_class('hidden')
            else:
                action.add_class('btn-secondary mr-sm-auto')
                action.href = registration_views.password_reset_view

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        hash = self.widgets.get('hash')
        if hash is not None:
            hash.mode = HIDDEN_MODE

    @handler(ILoginFormButtons['login'])
    def login_handler(self, action):  # pylint: disable=unused-argument
        """Login button handler"""
        data, errors = self.extract_data()
        if errors:
            self.status = self.form_errors_message
            return None
        principal_id = data.get('principal_id')
        if principal_id is not None:
            request = self.request
            headers = remember(request, principal_id)
            response = request.response
            response.headerlist.extend(headers)
            if not self.request.is_xhr:
                response.status_code = 302
                login_target = request.registry.queryMultiAdapter((self.context, self.request, self),
                                                                  ILoginPageTarget)
                if login_target is not None:
                    response.location = login_target
                else:
                    session = request.session
                    hash = data.get('hash') or ''
                    if LOGIN_REFERER_KEY in session:
                        response.location = f'{session[LOGIN_REFERER_KEY]}{hash}'
                        del session[LOGIN_REFERER_KEY]
                    else:
                        response.location = f'/{hash}'
            plugin = data.get('plugin')
            if plugin:
                request.registry.notify(
                    AuthenticatedPrincipalEvent(plugin, principal_id))
            self.finished_state.update({
                'action': action,
                'changes': principal_id
            })
            return response
        return None


@ajax_form_config(name='login-dialog.html',
                  layer=IPyAMSLayer)  # pylint: disable=abstract-method
@implementer(IModalPage, ILoginView)
class ModalLoginForm(LoginForm):
    """Modal login form"""

    modal_class = 'modal-lg'

    @property
    def buttons(self):
        """Form buttons getter"""
        return get_login_buttons(IModalLoginFormButtons, self.request)

    @handler(IModalLoginFormButtons['login'])
    def login_handler(self, action):
        """Login button handler"""
        return super().login_handler(self, action)


@subscriber(IDataExtractedEvent, form_selector=ILoginView)
def handle_login_form_data(event):
    """Check credentials after data extraction"""
    data = event.data
    if 'principal_id' in data:
        del data['principal_id']
    sm = query_utility(ISecurityManager)  # pylint: disable=invalid-name
    if sm is None:
        event.form.widgets.errors += (Invalid(_("Missing security manager utility. "
                                                "Please contact your system administrator!")), )
    else:
        credentials = Credentials('form', id=data['login'], **data)
        principal_id, plugin = sm.authenticate(credentials, event.form.request,
                                               get_plugin=True)
        if principal_id is None:
            event.form.widgets.errors += (Invalid(_("Invalid credentials!")),)
        else:
            data['principal_id'] = principal_id
            data['plugin'] = plugin


@adapter_config(required=(Interface, IPyAMSLayer, ILoginView),
                provides=IAJAXFormRenderer)
class LoginFormAJAXRenderer(ContextRequestViewAdapter):
    """Login form result renderer"""

    def render(self, changes):  # pylint: disable=unused-argument
        """AJAX form renderer"""
        status = {'status': 'redirect'}
        hash = self.request.params.get('login_form.widgets.hash', '')
        session = self.request.session
        if LOGIN_REFERER_KEY in session:
            status['location'] = f"{session[LOGIN_REFERER_KEY] or '/'}{hash}"
            del session[LOGIN_REFERER_KEY]
        else:
            status['location'] = f'/{hash}'
        return status


@viewlet_config(name='login.logo',
                layer=IPyAMSLayer, view=ILoginView,
                manager=IHeaderViewletManager, weight=1)
@template_config(template='templates/login-logo.pt')
class LoginLogoViewlet(Viewlet):
    """Login logo viewlet"""

    @property
    def logo(self):
        """Logo getter"""
        configuration = ILoginConfiguration(self.request.root, None)
        if configuration:
            return II18n(configuration).query_attribute('logo', request=self.request)
        return None


@viewlet_config(name='pyams.content_header',
                layer=IAdminLayer, view=ILoginView,
                manager=IHeaderViewletManager, weight=10)
class LoginViewHeaderViewlet(NullAdapter):
    """Disabled login view header viewlet"""


@viewletmanager_config(name='pyams.toolbar',
                       layer=IAdminLayer, view=ILoginView)
class LoginViewToolbarViewlet(ModalToolbarViewletManager):
    """Disabled login view toolbar viewlet"""


@template_config(template='templates/login-viewlet.pt')
class LoginViewlet(Viewlet):
    """Base login viewlet"""

    text_value = None
    attribute_name = 'header'
    renderer_getter = lambda x, y: y

    @reify
    def configuration(self):
        """Configuration getter"""
        return ILoginConfiguration(self.request.root, None)

    def render(self):
        configuration = self.configuration
        if configuration:
            # pylint: disable=assignment-from-no-return
            value = II18n(configuration).query_attribute(self.attribute_name,
                                                         request=self.request)
            if value:
                renderer = self.renderer_getter(configuration)  # pylint: disable=no-value-for-parameter
                if renderer == 'text':
                    self.text_value = value
                    return super().render()
                return text_to_html(value, renderer=renderer)
        return ''


@viewlet_config(name='login.header',
                layer=IPyAMSLayer, view=ILoginView,
                manager=IHeaderViewletManager, weight=100)
class LoginHeaderViewlet(LoginViewlet):
    """Login header viewlet"""

    attribute_name = 'header'
    renderer_getter = lambda x, config: config.header_renderer


@viewlet_config(name='login.footer',
                layer=IPyAMSLayer, view=ILoginView,
                manager=IFooterViewletManager, weight=100)
class LoginFooterViewlet(LoginViewlet):
    """Login footer viewlet"""

    attribute_name = 'footer'
    renderer_getter = lambda x, config: config.footer_renderer


@view_config(name='logout',
             request_type=IPyAMSLayer)
def logout(request):
    """Logout view"""
    headers = forget(request)
    response = Response()
    response.headerlist.extend(headers)
    response.status_code = 302
    response.location = '/'
    return response
