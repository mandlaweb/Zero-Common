# -*- coding: utf-8 -*-
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
