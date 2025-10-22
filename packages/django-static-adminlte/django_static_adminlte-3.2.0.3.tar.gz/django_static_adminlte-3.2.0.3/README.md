# django-static-adminlte

Django application contain adminlte static files.

## Install

```
pip install django-static-adminlte
```

## Licenses

- All resource files of ADMINLTE are unzip from AdminLTE-x.x.x.tar.gz which download from https://adminlte.io/ without any changes.
- All resource files of ADMINLTE obey ADMINLTE License, see details at https://github.com/ColorlibHQ/AdminLTE/blob/master/LICENSE.
- We don't guarantee the latest jQuery version.


## Usage

**pro/settings.py**

```python
INSTALLED_APPS = [
    ...
    "django_static_fontawesome",
    "django_static_ionicons",
    "django_static_jquery3",
    "django_static_bootstrap",
    "django_static_adminlte",
    ...
]
```

**app/template/app/index.html**

```html
{% load static %}

{% block style %}
<link rel="stylesheet" href="{% static "bootstrap/css/bootstrap.min.css" %}">
<link rel="stylesheet" href="{% static "fontawesome/css/all.min.css" %}">
<link rel="stylesheet" href="{% static "ionicons/css/ionicons.css" %}">
<link rel="stylesheet" href="{% static "adminlte/css/adminlte.min.css" %}">
{% endblock %}

{% block script %}
<script src="{% static "jquery/jquery.js" %}"></script>
<script src="{% static "bootstrap/js/bootstrap.min.js" %}"></script>
<script src="{% static "adminlte/js/adminlte.min.js" %}"></script>
{% endblock %}

```

## About releases

- The first number is our release number.
- The other three numbers are the same with ADMINLTE's release version.

## Releases

### 2.4.3

- First release.

### 2.4.3.2

- Update.

### 2.4.3.3

- Doc update.

### 3.2.0.1

- Upgrade adminlte to 3.2.0.

### 3.2.0.2

- Fix static files missing problem.

### 3.2.0.3

- Doc update.
