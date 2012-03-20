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


import logging

from django.contrib.sites.models import Site
from django.conf import settings


def basic(request=None):
    """
    Añade al contexto las variables básicas:

    * DOMAIN: Dominio sobre el cual se ejecuta la aplicación.
    * SITE_NAME: Nombre de la aplicación.
    * SITE_KEYWORDS: Keywords por defecto de la aplicación.
    * SITE_DESCRIPTION: Descripción por defecto de la aplicación.
    """
    
    current_site = Site.objects.get_current()
    
    return {
        'DOMAIN': current_site.domain,
        'SITE_URL': 'http://www.%s' % current_site.domain,
        'SITE_NAME': current_site.name,
        'SITE_KEYWORDS': settings.SITE_KEYWORDS,
        'SITE_DESCRIPTION': settings.SITE_DESCRIPTION,
    }
