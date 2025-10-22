# django-static-jquery3


Django application contains jquery and jquery-plugins' static files.

- Mostly we use jquery plugins, for django ships with jquery already. 
- We put many jquery plugins in this package, so that we will not use jquery's version from now on.
- Remove django from requirements.txt. We still keep django's file structure, but we will NOT need anything about django.

## jQuery License

- All resource files of jquery are unzip from jquery-xxx.zip which download from https://github.com/jquery/jquery/ without any changes.
- All resource files of jquery obey jQuery License, see details at https://github.com/jquery/jquery/blob/main/LICENSE.txt.
- We don't guarantee the latest jQuery version.

## jQuery Plugins Licenses

- Plugins may NOT a part of jquery.
- Plugins obey their own licenses.

## Install

```shell
pip install django-static-jquery3
```

## Installed Plugins

- jquery/plugins/jquery.cookie.js
- jquery/plugins/jquery.parseQuery.js
- jquery/plugins/jquery.utils.js
- jquery/plugins/jquery.jstree/jstree.js

## Usage

*pro/settings.py*

```python
INSTALLED_APPS = [
    ...
    "django_static_jquery3",
    ...
]
```

*app/template/app/index.html*

```html
{% load static %}

<script src="{% static "jquery/jquery.js" %}"></script>
<script src="{% static "jquery/plugins/jquery.cookie.js" %}"></script>
<script src="{% static "jquery/plugins/jquery.parseQuery.js" %}"></script>
<script src="{% static "jquery/plugins/jquery.utils.js" %}"></script>
<script src="{% static "jquery/plugins/jquery.cookie.js" %}"></script>
```

## About releases

- The first number is our release number.
- The other three numbers are the same with jquery's release version.

## Releases

## v6.3.7.2

- Doc update.

### v6.3.7.1

- Add jquery.parseQuery plugin.

### v5.3.7.1

- Upgrade jquery to v3.7.1.

### v5.1.0

- Add jquery.jstree plugin.

### v5.0.0

- Rename jquery3 folder to jquery.
- Mostly we use jquery plugins, for django ships with jquery already. 
- We put many jquery plugins in this package, so that we will not use jquery's version from now on.
- Remove django from requirements. We still keep django's file structure, but we will need anything about django.

### v3.4.1.1

- Add jquery plugin: jquery.cookie.
- Fix document.

### v3.4.1.0

- Upgrade jquery to 3.4.1.

### v3.3.1.1

- Upgrade jquery to 3.3.1.

## v3.2.1

- First release with jquery 3.2.1.

