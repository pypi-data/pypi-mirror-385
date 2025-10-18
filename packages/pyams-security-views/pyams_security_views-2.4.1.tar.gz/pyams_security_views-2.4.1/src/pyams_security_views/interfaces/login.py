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

"""PyAMS_*** module

"""

from zope.interface import Interface, Invalid, invariant
from zope.schema import Bool, Choice, Int, Password, TextLine

from pyams_file.schema import ImageField
from pyams_i18n.schema import I18nTextField
from pyams_layer.interfaces import BASE_SKINS_VOCABULARY_NAME
from pyams_security.interfaces import USERS_FOLDERS_VOCABULARY_NAME
from pyams_skin.schema.button import ActionButton, CloseButton, ResetButton, SubmitButton
from pyams_utils.text import PYAMS_HTML_RENDERERS_VOCABULARY
from pyams_zmi.interfaces import PYAMS_ADMIN_SKIN_NAME


__docformat__ = 'restructuredtext'

from pyams_security_views import _


class ILoginConfiguration(Interface):
    """Login configuration interface"""

    skin = Choice(title=_("Login skin"),
                  description=_("This is the skin applied to the login screen"),
                  vocabulary=BASE_SKINS_VOCABULARY_NAME,
                  default=PYAMS_ADMIN_SKIN_NAME,
                  required=True)

    logo = ImageField(title=_("Login logo"),
                      description=_("Image used in login form"),
                      required=False)

    header = I18nTextField(title=_("Login header"),
                           description=_("This text will be displayed in login page header"),
                           required=False)

    header_renderer = Choice(title=_("Header renderer"),
                             description=_("Text renderer used for the header"),
                             required=True,
                             vocabulary=PYAMS_HTML_RENDERERS_VOCABULARY,
                             default='text')

    footer = I18nTextField(title=_("Login footer"),
                           description=_("This text will be displayed in login page footer"),
                           required=False)

    footer_renderer = Choice(title=_("Footer renderer"),
                             description=_("Text renderer used for the footer"),
                             required=True,
                             vocabulary=PYAMS_HTML_RENDERERS_VOCABULARY,
                             default='text')

    open_registration = Bool(title=_("Enable free registration?"),
                             description=_("If 'Yes', any use will be able to create a new user "
                                           "account"),
                             required=True,
                             default=False)

    users_folder = Choice(title=_("Users folder"),
                          description=_("Name of users folder used to store registered principals"),
                          required=False,
                          vocabulary=USERS_FOLDERS_VOCABULARY_NAME)

    activation_delay = Int(title=_("Activation delay"),
                           description=_("This is the maximum delay, in days, until which "
                                         "unactivated user profiles are automatically deleted"),
                           required=False,
                           min=0,
                           default=10)

    @invariant
    def check_users_folder(self):
        """Check for open registration"""
        if self.open_registration and not self.users_folder:
            raise Invalid(_("You can't activate open registration without selecting a users "
                            "folder"))

    allow_password_reset = Bool(title=_("Allow password reset"),
                                description=_("If 'Yes', users will be able reset their password"),
                                required=True,
                                default=False)


class ILoginView(Interface):
    """Login view marker interface"""


class ILoginFormFields(Interface):
    """Login form fields"""

    hash = TextLine(title=_("Redirection hash"),
                    required=False)

    login = TextLine(title=_("User ID"),
                     description=_("Your user ID can be your email address or a custom login"))

    password = Password(title=_("Password"))


class IBaseLoginFormButtons(Interface):
    """Base login form buttons interface"""

    register = ActionButton(name='register',
                            title=_("Register"))

    reset_password = ActionButton(name='reset_password',
                                  title=_("Reset password"))

    login = SubmitButton(name='login',
                         title=_("Connect"))


class ILoginFormButtons(IBaseLoginFormButtons):
    """Login form buttons"""

    reset = ResetButton(name='reset',
                        title=_("Reset"))


class IModalLoginFormButtons(IBaseLoginFormButtons):
    """Modal login form buttons"""

    close = CloseButton(name='close',
                        title=_("Cancel"))


class ILoginPageTarget(Interface):
    """Login page target interface

    This interface is used to get location URL of the view used after
    a successful login.
    """
