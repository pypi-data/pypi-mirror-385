# django-static-ace-builds

Django application contain ace-builds(Ajax.org Cloud9 Editor) static files. See details about the static resources at https://ace.c9.io/.

## Install

```
pip install django-static-ace-builds
```

## Usage

**pro/settings.py**

```python
INSTALLED_APPS = [
    ...
    "django_static_ace_builds",
    ...
]
```

**app/template/app/index.html**

```html
{% load static %}

<script src="{% static "ace-builds/ace.js" %}"></script>
```

## About releases

1. The first three number is the same with ace-builds project's version.
1. The fourth number is our release number, it's optional.

## Releases

### v1.4.12.0 2020/08/31

- First release.

### v1.5.0.0 2023/09/12

- Upgrade to ace-build v1.5.0.

### v1.5.0.1 2025/10/18

- Doc update.

