Changelog
=========

2.4.1
-----
 - added setter to be able to change principals widgets AJAX URL property

2.4.0
-----
 - display inherited roles in protected object roles edit forms

2.3.8
-----
 - updated doctests to match last PyAMS_security package

2.3.7
-----
 - added security plugins table marker interface
 - added support for Python 3.12

2.3.6
-----
 - updated login form button classes on mobile devices
 - hide activation delay from main login configuration form fields

2.3.5
-----
 - updated doctests

2.3.4
-----
 - versioning error

2.3.3
-----
 - updated logo wrapper padding in login view
 - updated translation

2.3.2
-----
 - don't use referer in logout view

2.3.1
-----
 - added support for custom modal content CSS class

2.3.0
-----
 - added property in login configuration to set user registration activation delay
 - updated roles edit form permission

2.2.0
-----
 - use plugin instance instead of plugin name in authenticated principal event

2.1.2
-----
 - updated REST API route name and path configuration setting name

2.1.1
-----
 - fixed doctests

2.1.0
-----
 - set finished state in login form handler; this can be used to handle redirect in form renderer
   based on authenticated user

2.0.3
-----
 - updated modal forms title

2.0.2
-----
 - updated Buildout configuration

2.0.1
-----
 - imports cleanup

2.0.0
-----
 - upgraded for Pyramid 2.0
 - notify user authentication only from a successful login from a login form

1.9.1
-----
 - updated doctests

1.9.0
-----
 - added support for user registration
 - added support for local user password change

1.8.5
-----
 - refactored Colander API schemas for better OpenAPI specifications

1.8.4
-----
 - updated login form templates
 - added support for Python 3.11

1.8.3
-----
 - added mixin class to handle protected object roles edit form and add modal support

1.8.2
-----
 - updated security plugin add form AJAX renderer

1.8.1
-----
 - updated security plugin edit form AJAX renderer

1.8.0
-----
 - added OPTIONS handler to REST services
 - added CORS validators to principals REST service
 - added CORS security configuration form

1.7.2
-----
 - PyAMS_security interfaces refactoring
 - added support for Python 3.10

1.7.1
-----
 - updated principal widget separator to handle principals containing "," in their ID (like in
   LDAP DNs)

1.7.0
-----
 - keep location hash when redirecting to log in form
 - grant access to object roles view to all authenticated users

1.6.3
-----
 - renamed variable to remove Pylint/Sonar "bug"

1.6.2
-----
 - use new context add action

1.6.1
-----
 - updated doctests

1.6.0
-----
 - updated security manager menus

1.5.0
-----
 - added security manager label adapter
 - updated plug-in add and edit forms title
 - updated package include scan

1.4.1
-----
 - remove edit permission on login form

1.4.0
-----
 - added default site root permission checker
 - handle single value in principal widget data converter
 - use new IObjectLabel interface

1.3.4
-----
 - pylint cleanup

1.3.3
-----
 - updated AJAX forms renderers

1.3.2
-----
 - added missing "context" argument to permission check
 - updated add menus registration for last PyAMS_zmi release

1.3.1
-----
 - updated security plug-ins base add form AJAX renderer

1.3.0
-----
 - removed support for Python < 3.7
 - updated principals search REST API using Colander schemas
 - added data converter for principal field
 - removed redirect warning from login view
 - changed fields order in local users forms

1.2.1
-----
 - updated Gitlab-CI configuration
 - removed Travis-CI configuration

1.2.0
-----
 - added CSRF token in login view
 - added permission check in security manager table element editor factory

1.1.0
-----
 - updated security manager properties edit form to display credentials plug-ins
 - updated doctests

1.0.2
-----
 - updated translation strings

1.0.1
-----
 - small update in protected object roles edit form

1.0.0
-----
 - initial release
