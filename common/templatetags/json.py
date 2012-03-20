# -*- coding: utf-8 -*-
# Copyright 2012 Mandla Web Studio
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__author__ = 'Jose Maria Zambrana Arze'
__email__ = 'contact@josezambrana.com'
__version__ = '0.1'
__copyright__ = 'Copyright 2012, Mandla Web Studio'


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
    
