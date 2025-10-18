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

"""PyAMS_security_views.zmi.policy module

This module defines views and content providers which are used to manage roles and
security policy
"""

from pyramid.traversal import lineage
from zope.component import getAdapters
from zope.interface import Interface, implementer
from zope.schema import getFieldNamesInOrder

from pyams_form.ajax import ajax_form_config
from pyams_form.browser.checkbox import SingleCheckBoxFieldWidget
from pyams_form.field import Fields
from pyams_form.interfaces import DISPLAY_MODE, INPUT_MODE
from pyams_form.interfaces.form import IGroup, IInnerSubForm
from pyams_form.subform import InnerDisplayForm
from pyams_i18n.interfaces import II18n
from pyams_layer.interfaces import IPyAMSLayer
from pyams_security.interfaces import IDefaultProtectionPolicy, IProtectedObject, IRolesPolicy
from pyams_security.interfaces.base import IRole, MANAGE_ROLES_PERMISSION, MANAGE_SECURITY_PERMISSION, \
    VIEW_SYSTEM_PERMISSION
from pyams_security_views.zmi.interfaces import IObjectSecurityMenu, IProtectedObjectRolesEditForm
from pyams_skin.interfaces.view import IModalEditForm
from pyams_skin.interfaces.viewlet import IHelpViewletManager
from pyams_skin.viewlet.help import AlertMessage
from pyams_template.template import template_config
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces import ICacheKeyValue
from pyams_utils.list import boolean_iter
from pyams_utils.registry import get_utility
from pyams_utils.traversing import get_parent
from pyams_viewlet.manager import viewletmanager_config
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminEditForm, AdminInnerDisplayForm, AdminModalEditForm, FormGroupSwitcher
from pyams_zmi.interfaces import IAdminLayer, TITLE_SPAN_BREAK
from pyams_zmi.interfaces.form import IFormTitle
from pyams_zmi.interfaces.viewlet import ISiteManagementMenu
from pyams_zmi.utils import get_object_label
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_security_views import _  # pylint: disable=ungrouped-imports


#
# Object roles views
#

@viewletmanager_config(name='object-roles.menu', context=IDefaultProtectionPolicy,
                       layer=IAdminLayer, manager=ISiteManagementMenu, weight=900,
                       permission=VIEW_SYSTEM_PERMISSION,
                       provides=IObjectSecurityMenu)
class ObjectSecurityMenu(NavigationMenuItem):
    """Object security menu"""

    label = _("User roles")
    icon_class = 'fas fa-shield-alt'
    href = '#object-roles.html'


@implementer(IProtectedObjectRolesEditForm)
class ProtectedObjectRolesEditFormMixin:
    """Protected object roles edit form mixin"""

    legend = _("Granted object roles")
    _edit_permission = MANAGE_ROLES_PERMISSION

    @property
    def fields(self):
        """Form fields getter"""
        fields = Fields(Interface)
        for _name, policy in sorted(getAdapters((self.context,), IRolesPolicy),
                                    key=lambda x: x[1].weight):
            fields += Fields(policy.roles_interface)
        return fields

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        if self.mode == DISPLAY_MODE:
            return
        identity = self.request.identity
        if identity is None:
            return
        principals = identity['principals']
        for widget in self.widgets.values():
            widget.mode = DISPLAY_MODE
            role = get_utility(IRole, name=widget.field.role_id)
            if role.managers:
                for manager in role.managers:
                    if manager in principals:
                        widget.mode = INPUT_MODE
                        break


@ajax_form_config(name='object-roles.html', context=IDefaultProtectionPolicy,
                  layer=IPyAMSLayer, permission=VIEW_SYSTEM_PERMISSION)
class ProtectedObjectRolesEditForm(ProtectedObjectRolesEditFormMixin, AdminEditForm):
    """Protected object roles edit form"""

    title = _("User roles")


@ajax_form_config(name='modal-object-roles.html', context=IDefaultProtectionPolicy,
                  layer=IPyAMSLayer, permission=VIEW_SYSTEM_PERMISSION)
class ProtectedObjectRolesModalEditForm(ProtectedObjectRolesEditFormMixin, AdminModalEditForm):
    """Protected object roles modal edit form"""

    subtitle = _("User roles")


@adapter_config(required=(IDefaultProtectionPolicy, IAdminLayer, ProtectedObjectRolesModalEditForm),
                provides=IFormTitle)
def protected_object_roles_edit_form_title(context, request, form):
    """Protected object roles edit form title"""
    parent = get_parent(context, IDefaultProtectionPolicy, allow_context=False)
    return TITLE_SPAN_BREAK.format(
        get_object_label(parent, request, form),
        get_object_label(context, request, form))


@viewlet_config(name='object-roles.alert', context=IDefaultProtectionPolicy,
                layer=IAdminLayer, view=ProtectedObjectRolesEditFormMixin,
                manager=IHelpViewletManager, weight=1)
class ProtectedObjectRolesAlert(AlertMessage):
    """Protected object roles alert"""

    def __new__(cls, context, request, view, manager):  # pylint: disable=unused-argument
        if not view.widgets:
            return AlertMessage.__new__(cls)
        return None

    status = 'danger'
    _message = _("Roles are not defined for this context!")


@adapter_config(name='parent-roles',
                required=(IDefaultProtectionPolicy, IAdminLayer, IProtectedObjectRolesEditForm),
                provides=IInnerSubForm)
@template_config(template='templates/parent-roles.pt', layer=IAdminLayer)
class ParentRolesInnerForm(InnerDisplayForm):
    """Parent roles inner form"""
    
    def get_parents(self):
        for parent in lineage(self.context.__parent__):
            protection = IProtectedObject(parent, None)
            if (protection is not None) and not protection.inherit_parent_roles:
                return
            has_adapters, _adapters = boolean_iter(getAdapters((parent,), IRolesPolicy))
            if has_adapters:
                yield parent
        
    @staticmethod
    def get_fields(context):
        fields = Fields(Interface)
        for _name, policy in sorted(getAdapters((context,), IRolesPolicy),
                                    key=lambda x: x[1].weight):
            roles = policy.roles_interface(context)
            fields += Fields(policy.roles_interface).select(*(
                role_name
                for role_name in getFieldNamesInOrder(policy.roles_interface)
                if getattr(roles, role_name)
            ))
        return fields
    
    def get_subforms(self):
        for parent in self.get_parents():
            fields = self.get_fields(parent)
            if not fields:
                continue
            switcher = FormGroupSwitcher(parent, self.request, self)
            switcher.prefix = f'roles_form-{ICacheKeyValue(parent)}.'
            switcher.form_content = parent
            switcher.legend = get_object_label(parent, self.request, self)
            switcher.mode = DISPLAY_MODE
            switcher.switcher_mode = 'never'
            switcher.fields = fields
            switcher.update()
            yield switcher
        

#
# Security policy views
#

@viewlet_config(name='security-policy.menu', context=IDefaultProtectionPolicy,
                layer=IAdminLayer, manager=IObjectSecurityMenu,
                permission=MANAGE_SECURITY_PERMISSION, weight=10)
class ProtectedObjectSecurityPolicyMenuItem(NavigationMenuItem):
    """Protected object security policy menu item"""

    label = _("Security policy")
    icon_class = 'fas fa-key'
    href = '#security-policy.html'


@ajax_form_config(name='security-policy.html', context=IDefaultProtectionPolicy,
                  layer=IPyAMSLayer, permission=MANAGE_SECURITY_PERMISSION)
class ProtectedObjectSecurityPolicyEditForm(AdminEditForm):
    """Protected object security policy edit form"""

    title = _("Security policy")
    legend = _("Security policy management")

    fields = Fields(IProtectedObject)
    fields['inherit_parent_security'].widget_factory = SingleCheckBoxFieldWidget
    fields['inherit_parent_roles'].widget_factory = SingleCheckBoxFieldWidget

    def get_content(self):
        return IProtectedObject(self.context)
