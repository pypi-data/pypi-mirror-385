# django-fullname-localization

Add localization support for user's fullname.

## Install

```shell
pip install django-fullname-localization
```

## Settings

**pro/settings.py**

```python
INSTALLED_APPS = [
    ...
    'django_fullname_localization',
    ...
]

USE_FULL_NAME_INSTEAD_OF_SHORT_NAME = True
FULL_NAME_TEMPLATE = "{user.last_name}{user.first_name}"
```

*Note:*

* At django_fullname_localization app ready step, we override AbstractUser.get_full_name method, so that all user model that inherit from AbstractUser will get a new *.get_full_name() method.
* Use FULL_NAME_TEMPLATE to define your fullname style.
* USE_FULL_NAME_INSTEAD_OF_SHORT_NAME defaults to True, so that the short name will be replaced with our full name. Mostly our full name is short enough ^_^

## Fullname template setting

FULL_NAME_TEMPLATE default to "{user.last_name}{user.first_name}", it's our default name format ^_^.

*Notes:*

* If using default User model, you can use user.first_name and user.last_name parameter to write your own template.
* If using customer model that has more name parts, you can using parameter {user.your_own_field}.
* Some application that doesn't override the default User model but keep the full name in first_name and keep the last name in last_name, so that you just set FULL_NAME_TEMPLATE="{user.first_name}".

## Usage

**app/template/demo.html**

```html
{{request.user.get_full_name}}
```

**app/views.py**

```python

def page(request):
    ...
    fullname = request.user.get_full_name()
    ...
```


## Release

### v0.1.0 2020/02/29

- First release.

### v0.2.0 2020/09/09

- Add license in package.
- Add replacing short name with full name support. It is controlled by USE_FULL_NAME_INSTEAD_OF_SHORT_NAME option in settings. USE_FULL_NAME_INSTEAD_OF_SHORT_NAME defaults to True, so that the name used in the default django's admin site topbar will be our full name.
- Remove first_name, last_name parameter support for FULL_NAME_TEMPLATE, for user's customized User Model may not have first_name, last_name fields.
- Fix documentations.

### v0.2.1 2023/09/15

- Doc update.

### v0.2.2 2025/10/18

- Doc update.
