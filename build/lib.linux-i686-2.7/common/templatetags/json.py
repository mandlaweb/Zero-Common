# -*- coding: utf-8 -*-
from django import template
from django.utils import simplejson as json
from django.contrib.sites.models import Site


register = template.Library()


@register.filter(name="escapejson")
def escapejson(value, arg=None):
    """
    Cambia value a formato json.
    """
    base = json.dumps(value)
    return base.replace('/', r'\/')


@register.filter(name="urljson")
def urljson(object, arg=None):
    """
    Devuelve la url absoluta del objeto en formato json junto con el nombre del
    dominio.
    """
    current_site = Site.objects.get_current()
    base = json.dumps("http://%s%s" % (current_site.domain, object.get_absolute_url()))
    return base.replace('/', r'\/')
    