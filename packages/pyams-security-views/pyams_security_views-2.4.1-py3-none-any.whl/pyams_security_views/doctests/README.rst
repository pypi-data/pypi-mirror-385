============================
PyAMS security views package
============================

Introduction
------------

This package is composed of a set of utility functions, usable into any Pyramid application.

    >>> import pprint

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)
    >>> config.registry.settings['zodbconn.uri'] = 'memory://'

    >>> from pyramid_zodbconn import includeme as include_zodbconn
    >>> include_zodbconn(config)
    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)
    >>> from pyams_viewlet import includeme as include_viewlet
    >>> include_viewlet(config)
    >>> from pyams_site import includeme as include_site
    >>> include_site(config)
    >>> from pyams_security import includeme as include_security
    >>> include_security(config)
    >>> from pyams_layer import includeme as include_layer
    >>> include_layer(config)
    >>> from pyams_form import includeme as include_form
    >>> include_form(config)
    >>> from pyams_skin import includeme as include_skin
    >>> include_skin(config)
    >>> from pyams_zmi import includeme as include_zmi
    >>> include_zmi(config)
    >>> from pyams_security_views import includeme as include_security_views
    >>> include_security_views(config)
    >>> from pyams_i18n_views import includeme as include_i18n_view
    >>> include_i18n_view(config)

    >>> from pyams_utils.registry import get_utility, set_local_registry
    >>> registry = config.registry
    >>> set_local_registry(registry)

    >>> from pyams_site.generations import upgrade_site
    >>> request = DummyRequest()
    >>> app = upgrade_site(request)
    Upgrading PyAMS timezone to generation 1...
    Upgrading PyAMS security to generation 2...

    >>> from zope.traversing.interfaces import BeforeTraverseEvent
    >>> from pyams_utils.registry import handle_site_before_traverse
    >>> handle_site_before_traverse(BeforeTraverseEvent(app, request))

    >>> from pyams_security.interfaces import ISecurityManager
    >>> sm = get_utility(ISecurityManager)


Security manager properties edit form
-------------------------------------

    >>> from zope.interface import alsoProvides
    >>> from pyams_zmi.interfaces import IAdminLayer

    >>> request = DummyRequest(context=app)
    >>> alsoProvides(request, IAdminLayer)

    >>> from pyams_security_views.zmi.manager import SecurityPropertiesEditForm
    >>> form = SecurityPropertiesEditForm(sm, request)
    >>> form.update()
    >>> form.widgets.keys()
    odict_keys(['credentials_plugins_names', 'authentication_plugins_names', 'directory_plugins_names'])
    >>> print(form.widgets['credentials_plugins_names'].render())
    <table class="table border border-top-0 table-xs width-100">
        <tbody>
            <tr
                id="form-widgets-credentials_plugins_names-0">
                <td>Internal request authentication</td>
            </tr>
        </tbody>
    </table>
    >>> print(form.widgets['authentication_plugins_names'].render())
    <table class="table border border-top-0 table-xs datatable width-100"
           data-ams-modules="plugins"
           data-searching="false" data-info="false" data-paging="false" data-ordering="false"
           data-row-reorder='{
                "update": false
           }'
           data-ams-reorder-input-target="#form-widgets-authentication_plugins_names">
        <thead class="hidden">
                <tr>
                        <th data-ams-column='{"className": "reorder"}'></th>
                        <th></th>
                </tr>
        </thead>
        <tbody>
                <tr
                        id="form-widgets-authentication_plugins_names-0"
                        data-ams-row-value="__system__">
                        <td><i class="fas fa-arrows-alt-v"></i></td>
                        <td>System manager authentication</td>
                </tr>
      <tr
                        id="form-widgets-authentication_plugins_names-1"
                        data-ams-row-value="__internal__">
                        <td><i class="fas fa-arrows-alt-v"></i></td>
                        <td>internal service</td>
                </tr>
        </tbody>
    </table>
    <input type="hidden"
           id="form-widgets-authentication_plugins_names"
           name="form.widgets.authentication_plugins_names"
           value="__system__;__internal__" />

    >>> output = form.render()


Security policy edit form
-------------------------

    >>> from pyams_security_views.zmi.policy import ProtectedObjectSecurityPolicyEditForm
    >>> form = ProtectedObjectSecurityPolicyEditForm(app, request)
    >>> form.update()
    >>> form.widgets.keys()
    odict_keys(['inherit_parent_security', 'everyone_denied', 'everyone_granted', 'authenticated_denied', 'authenticated_granted', 'inherit_parent_roles'])

    >>> output = form.render()


Protected object roles edit form
--------------------------------

    >>> from pyams_security_views.zmi.policy import ProtectedObjectRolesEditForm
    >>> form = ProtectedObjectRolesEditForm(app, request)
    >>> form.update()
    >>> form.widgets.keys()
    odict_keys(['internal_api', 'public_api', 'managers', 'viewers'])
    >>> print(form.widgets['managers'].render())
    <select id="form-widgets-managers"
            name="form.widgets.managers"
            class="form-control select2 select-widget principalssetfield-field"
            multiple="multiple"
            size="1"
            data-allow-clear="true"
            data-placeholder="No selected principal"
            data-ajax--url="/api/security/principals"
            data-minimum-input-length="2">
            <option></option>
    </select>
    <input name="form.widgets.managers-empty-marker" type="hidden" value="1" />

    >>> output = form.render()


Principals searching API
------------------------

    >>> from pyams_security_views.api.principal import get_principals
    >>> request = DummyRequest(params={'term': 'admin'})
    >>> pprint.pprint(get_principals(request))
    {'results': [{'id': 'system:admin', 'text': 'System manager authentication'}],
     'status': 'success'}


Login form configuration edit form
----------------------------------

    >>> class MockNumberFormatter(object):
    ...     def format(self, value):
    ...         if value is None:
    ...             # execution should never get here
    ...             raise ValueError('Cannot format None')
    ...         return str(value)

    >>> class MockLocale:
    ...     def getFormatter(self, category):
    ...         return MockNumberFormatter()

    >>> from babel.core import Locale
    >>> request = DummyRequest(context=app, locale=Locale('en', 'US'))
    >>> request.locale.numbers = MockLocale()
    >>> alsoProvides(request, IAdminLayer)

    >>> from pyams_security_views.zmi.login import LoginFormConfigurationForm
    >>> form = LoginFormConfigurationForm(app, request)
    >>> form.update()
    >>> form.widgets.keys()
    odict_keys(['skin', 'logo', 'header', 'header_renderer', 'footer', 'footer_renderer'])

    >>> output = form.render()


Login form
----------

    >>> from pyams_layer.interfaces import IPyAMSLayer
    >>> from pyams_security_views.skin.login import LoginForm

    >>> request = DummyRequest(root=app, is_xhr=False)
    >>> alsoProvides(request, IPyAMSLayer)
    >>> form = LoginForm(app, request)
    >>> form.update()
    >>> output = form.render()
    >>> print(output)
    <section class="rounded-lg ">
        <form class="ams-form "
              id="login_form"
              name="login_form"
              action="http://example.com"
              method="post"
              data-async
              data-ams-modules="form plugins"
              data-ams-data='{"ams-warn-on-change": false, "ams-modules": "callbacks helpers", "ams-callback": "MyAMS.helpers.setLoginHash"}'>
            <fieldset
                class="border">
                <legend>Please enter valid credentials</legend>
                <input type="hidden"
                       id="login_form-widgets-hash"
                       name="login_form.widgets.hash"
                       value=""
                       class="hidden-widget" />
                <div class="form-group widget-group row">
                    <label for="login_form-widgets-login"
                           class="col-form-label text-sm-right col-sm-3 col-md-4 required">
                        User ID
                        <i class="fa fa-question-circle hint"
                           data-original-title="Your user ID can be your email address or a custom login"></i>
                    </label>
                    <div class="col-sm-9 col-md-8">
                        <div class="form-widget ">
                            <input type="text"
                                   id="login_form-widgets-login"
                                   name="login_form.widgets.login"
                                   class="form-control text-widget required textline-field"
                                   value="" />
                        </div>
                    </div>
                </div>
                <div class="form-group widget-group row">
                    <label for="login_form-widgets-password"
                           class="col-form-label text-sm-right col-sm-3 col-md-4 required">
                        Password
                    </label>
                    <div class="col-sm-9 col-md-8">
                        <div class="form-widget ">
                            <input type="password"
                                   id="login_form-widgets-password"
                                   name="login_form.widgets.password"
                                   class="form-control password-widget required password-field" />
                        </div>
                    </div>
                </div>
            </fieldset>
            <footer>
                <button
                    type="submit"
                    id="login_form-buttons-login"
                    name="login_form.buttons.login"
                    class="btn btn-primary submit-widget submitbutton-field "
                    value="Connect"
                    data-loading-test="Connect...">
                    Connect
                </button>
                <button
                    type="reset"
                    id="login_form-buttons-reset"
                    name="login_form.buttons.reset"
                    class="btn btn-light submit-widget resetbutton-field"
                    value="Reset">Reset</button>
            </footer>
        </form>
    </section>

    >>> request = DummyRequest(root=app, is_xhr=False, params={
    ...     'login_form.widgets.login': 'admin',
    ...     'login_form.widgets.password': 'admin',
    ...     'login_form.buttons.login': 'Connect'
    ... })
    >>> alsoProvides(request, IPyAMSLayer)
    >>> form = LoginForm(app, request)
    >>> form.update()
    >>> form.widgets.keys()
    odict_keys(['hash', 'login', 'password'])

    >>> output = form.render()
    >>> output
    ''
    >>> request.response.status_code
    302
    >>> request.response.location
    'http://example.com'


Tests cleanup:

    >>> tearDown()
