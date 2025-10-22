# django-static-bootstrap


Django application contain bootstrap static files.


## Install

```shell
pip install django-static-bootstrap
```

## Settings

```
INSTALLED_APPS = [
    ...
    'django_static_bootstrap',
    ...
]
```

## Use static resource

```
{% load staticfiles %}

<link rel="stylesheet" href="{% static "bootstrap/css/bootstrap.min.css" %}">
<script src="{% static "admin/js/vendor/jquery/jquery.js" %}"></script>
<script src="{% static "bootstrap/js/bootstrap.min.js" %}"></script>
```

- You can use django's jquery.js, but be careful about django's jquery.init.js. bootstrap/js/bootstrap.min.js must be loaded after jquery.js and before jquery.init.js.
- If you are not using django framework, you can try django-static-jquery3>=5.0.0 to get jquery.js.

## About releases

The first three number is the same with bootstrap project's version.
The fourth number is our release number, it's optional.

## Releases

### v3.3.7.1 2018/03/27

- First release.

### v4.4.1 2020/02/27

- Upgrade the resources to version 4.4.1.

### v4.4.1.2 2020/09/08

- No depends on django.

### v4.4.1.4 2023/09/15

- Doc update.

### v4.6.2.1 2023/09/16

- Upgrade to bootstrap v4.6.2.

### v4.6.2.2 2025/10/21

- Doc update.
