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

"""PyAMS_security_views.zmi.login module

This module provides views and content providers used to manage login page configuration.
"""

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.group import Group
from pyams_form.interfaces.form import IAJAXFormRenderer, IGroup
from pyams_layer.interfaces import IPyAMSLayer
from pyams_security.interfaces.base import MANAGE_SYSTEM_PERMISSION
from pyams_security_views.interfaces.login import ILoginConfiguration
from pyams_site.interfaces import ISiteRoot
from pyams_skin.interfaces.viewlet import IHeaderViewletManager
from pyams_skin.viewlet.help import AlertMessage
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_viewlet.manager import viewletmanager_config
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminEditForm, FormGroupChecker
from pyams_zmi.helper.event import get_json_widget_refresh_callback
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.zmi.interfaces import IConfigurationMenu
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_security_views import _  # pylint: disable=ungrouped-imports


@viewletmanager_config(name='login-form-configuration.menu',
                       context=ISiteRoot, layer=IAdminLayer,
                       manager=IConfigurationMenu, weight=20,
                       permission=MANAGE_SYSTEM_PERMISSION)
class LoginFormConfigurationMenu(NavigationMenuItem):
    """Login form configuration menu"""

    label = _("Login form")
    href = '#login-form-configuration.html'


@ajax_form_config(name='login-form-configuration.html',
                  context=ISiteRoot, layer=IPyAMSLayer,
                  permission=MANAGE_SYSTEM_PERMISSION)
class LoginFormConfigurationForm(AdminEditForm):
    """Login form configuration form"""

    title = _("Login form configuration")
    legend = _("Form properties")

    fields = Fields(ILoginConfiguration).omit('open_registration', 'users_folder',
                                              'registration_expiration', 'allow_password_reset',
                                              'activation_delay')

    def get_content(self):
        return ILoginConfiguration(self.context)

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        if 'header' in self.widgets:
            self.widgets['header'].set_widgets_attr('rows', 5)
            self.widgets['header'].add_widgets_class('monospace')
        if 'footer' in self.widgets:
            self.widgets['footer'].set_widgets_attr('rows', 5)
            self.widgets['footer'].add_widgets_class('monospace')


@adapter_config(name='security-registration',
                required=(ISiteRoot, IAdminLayer, LoginFormConfigurationForm),
                provides=IGroup)
class OpenRegistrationGroup(FormGroupChecker):
    """Login form registration group"""

    fields = Fields(ILoginConfiguration).select('open_registration', 'users_folder',
                                                'activation_delay')


@viewlet_config(name='security-registration.header',
                context=ISiteRoot, layer=IAdminLayer, view=OpenRegistrationGroup,
                manager=IHeaderViewletManager, weight=1)
class OpenRegistrationHeader(AlertMessage):
    """Open registration header"""

    status = 'info'

    _message = _("Open registration can be used when you want external users to be able to "
                 "freely register their user account.\n"
                 "You then have to select the users folder into which their profile will be "
                 "stored.\n"
                 "THIS CAN BE DANGEROUS! You should enable this feature carefully...")


@adapter_config(name='password-reset',
                required=(ISiteRoot, IAdminLayer, LoginFormConfigurationForm),
                provides=IGroup)
class PasswordResetGroup(Group):
    """Login form password reset group"""

    fields = Fields(ILoginConfiguration).select('allow_password_reset')


@adapter_config(required=(ISiteRoot, IAdminLayer, LoginFormConfigurationForm),
                provides=IAJAXFormRenderer)
class LoginFormConfigurationRenderer(ContextRequestViewAdapter):
    """Login form configuration form AJAX renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if changes and ('logo' in changes.get(ILoginConfiguration, ())):
            return get_json_widget_refresh_callback(self.view, 'logo', self.request)
        return None
