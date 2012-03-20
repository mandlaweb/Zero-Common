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



import datetime
import logging

from django import template
from django.utils.translation import ugettext, ungettext
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='humanize_datetime')
def humanize_datetime(dtime):
    """
    Da formato a las estampas de tiempo para que sea legible a los usuarios:

    * hace unos momentos.
    * hace %d hora(s).
    * hace %d semana(s).
    * hace %d años(s).
    """
    
    logging.info('__class__: %s ' % dtime.__class__)
    logging.info('dtime: %s' % dtime)
     
    delta = datetime.datetime.now() - dtime

    num_years = delta.days / 365
    if (num_years > 0):
        return ungettext(mark_safe(u"hace %d año"),
                        mark_safe(u"hace %d años"), num_years) % num_years

    num_weeks = delta.days / 7
    if (num_weeks > 0):
        return ungettext(u"hace %d semana", u"hace %d semanas", num_weeks) % num_weeks

    if (delta.days > 0):
        return ungettext(mark_safe(u"hace %d día"),
                        mark_safe(u"hace %d días"), delta.days) % delta.days

    num_hours = delta.seconds / 3600
    if (num_hours > 0):
        return ungettext(u"hace %d hora", u"hace %d horas", num_hours) % num_hours

    num_minutes = delta.seconds / 60
    if (num_minutes > 0):
        return ungettext(u"hace %d minuto", u"hace %d minutos", num_minutes) % num_minutes

    return ugettext(u"hace unos momentos")
