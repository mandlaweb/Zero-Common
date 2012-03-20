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


from time import time

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


class Content(models.Model):
    """
    Modelo base con atributos primarios para los contenidos que son visibles
    en el sitio.
    """

    #: Nombre del contenido
    name = models.CharField(_('Nombre'), max_length=255)
    #: Slug para usarse en la url y mostrar el contenido
    slug = models.SlugField(_('slug'))

    #: El usuario propietario del contenido
    user = models.ForeignKey(User, verbose_name=_(u'Propietario'))

    #: Fecha de creación del contenido
    created_at = models.DateTimeField(_(u'Fecha de creación'), 
            auto_now_add=True)
    
    #: Fecha de última actualización del contenido
    updated_at = models.DateTimeField(_(u'Fecha de última modificación'), 
            auto_now=True)

    #: Fecha de publicación del contenido
    published_at = models.DateTimeField(_(u'Fecha Publicación'), 
            auto_now_add=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        model = self.__class__

        query = model.objects.filter(slug=slug)
        if not query.exists():
            self.slug = slug
        else:
            content = query.get()
            if self.id is None:
                self.slug = "%s-%s" % (slug, int(time()))
            elif self.id == content.id:
                self.slug = slug
            else:
                self.slug = "%s-%s" % (self.slug, self.id)
        return super(Content, self).save(*args, **kwargs)
