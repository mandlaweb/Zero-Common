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


import copy

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string

SITE_FROM_EMAIL = getattr(settings, 'SITE_FROM_EMAIL', None)


class Mailer(object):
    """
    Clase encargada de enviar emails.
    """
    
    def __init__(self, subject, plain_template, html_template, **kwargs):
        self.subject = subject
        self.kwargs = kwargs
        self.plain_template = plain_template
        self.html_template = html_template
    
    def send(self, emails, from_email=None):
        """
        Envia el email.
        """
        
        if isinstance(emails, basestring):
            emails = [emails]
            
        # Definimos el email de donde se envia
        from_email = from_email or SITE_FROM_EMAIL
        if from_email is None:
            raise ImproperlyConfigured(u'Se necesita definir una dirección de '
                                       u'email del sitio.')
        
        # renderizamos los mensajes
        message = self._render(self.plain_template, **self.kwargs)
        html_message = self._render(self.html_template, **self.kwargs)
        
        # Enviamos el mail
        return self.send_mail(emails, self.subject, message=message,
                                                    from_email=from_email,
                                                    html_message=html_message)

    @classmethod
    def send_mail(cls, emails, subject, message, from_email=None, html_message=None):
        """
        Envia el email a todos los destinatarios.
        """
        
        mail = EmailMultiAlternatives(subject, message, from_email, emails)
        mail.attach_alternative(html_message, "text/html")
        return mail.send()

    @classmethod
    def _render(cls, template_name, **kwargs):
        """
        Renderiza el mensaje.
        """
        
        # Generamos el contexto
        from common.context_processors import basic 
        kwargs['STATIC_URL'] = settings.STATIC_URL
        context = copy.copy(basic())
        context.update(kwargs)

        # renderizamos el mensaje
        message = render_to_string(template_name, context)

        return message


