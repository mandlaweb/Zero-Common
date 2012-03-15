# -*- coding: utf-8 -*-
import time
import logging

from django import template
from django.conf import settings
from django.contrib.sites.models import Site

from django.utils.hashcompat import sha_constructor

from django.template import TemplateSyntaxError
from django.template.loader_tags import ExtendsNode
from django.template.defaultfilters import urlize
from django.template.defaulttags import kwarg_re
from django.template.defaulttags import URLNode
from django.template.loader_tags import ExtendsNode


register = template.Library()
current_site = Site.objects.get_current()


@register.filter(name="urlize_blank")
def urlize_blank(value, autoescape=None):
    """
    Convierte en un enlace <a> las cadenas que tienen un formato de url.
    A diferencia del template tag por defecto de django, este convierte a
    enlaces que se abren en una nueva ventana y se añade el atributo
    rel="nofollow"
    """
    
    result = urlize(value, autoescape=autoescape)
    return result.replace('<a ', '<a target="_blank" rel="nofollow" ')


@register.filter
def hash(dictionary, key):
    """
    Retorna el objecto que tienen como clave *key* del diccionario *dictionary*
    """
    
    if dictionary:
        try:
            return dictionary[str(key)]
        except KeyError:
            pass

    return None


@register.tag
def urlfull(parser, token):
    bits = token.split_contents()
    
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument")
    
    viewname = bits[1]
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to url tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    return URLFullNode(viewname, args, kwargs, asvar)


class URLFullNode(URLNode):
    """
    Nodo para mostrar la url completa más el dominio:

    http://www.yourdomain.com/path
    
    """
    
    def render(self, context):
        url = super(URLFullNode, self).render(context)
        return "http://www.%s%s" % (current_site.domain, url)


