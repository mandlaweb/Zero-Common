# -*- coding: utf-8 -*-
import re
import base64
import logging

from django.db import models
from south.modelsinspector import add_introspection_rules
from django.forms import RegexField

try:
    import cPickle as pickle
except ImportError:
    import pickle



class DictField(models.TextField):
    """
    Campo para manejar y almacenar datos de tipo diccionario.
    """

    __metaclass__ = models.SubfieldBase

    description = "Campo que almacena datos de tipo diccionario"

    def to_python(self, value):
        """
        Convierte el valor guardado en la base de datos a un diccionario.
        """

        if value is None:
            return {}
        
        if isinstance(value, dict):
            return value
        
        try:
            res = pickle.loads(base64.b64decode(value))
        except EOFError:
            res = {}

        return res
        
    def get_db_prep_save(self, value, **kwargs):
        """
        Serializa el valor y lo codifica para almacenarlo en la base de datos.
        """

        if value is None:
            value = {}

        return base64.b64encode(pickle.dumps(value, protocol=-1))

    def validate(self, value, model_instance):
        if not isinstance(value, dict):
            raise exceptions.ValidationError("No es un diccionario %s" % value)
        

class ListField(models.TextField):
    """
    Campo para manejar y almacenar datos de tipo lista.
    """
    
    __metaclass__ = models.SubfieldBase

    description = "Campo que almacena datos de tipo diccionario"

    def to_python(self, value):
        """
        Convierte los datos en una lista.
        """

        if value is None:
            return []
        
        if isinstance(value, list):
            return value
        
        try:
            res = pickle.loads(base64.b64decode(value))
        except EOFError:
            res = []
        
        return res
        
    def get_db_prep_save(self, value, **kwargs):
        """
        Serializa y codifica la lista para almacenarlo en la base de datos.
        """
        
        if value is None:
            value = []
        
        return base64.b64encode(pickle.dumps(value, protocol=-1))

    def validate(self, value, model_instance):
        if not isinstance(value, list):
            raise exceptions.ValidationError(u'No es una lista %s' % value)


HEX_COLOR = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')


class ColorField(models.CharField):
    """
    Campo para almacenar un color en formato hexadecimal.
    """

    __metaclass__ = models.SubfieldBase
    description = "Un color en formato hexadecimal"
    
    def __init__(self, *args, **kwargs):
        if not 'max_length' in kwargs:
            kwargs['max_length'] = 7
        
        return super(ColorField, self).__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        if not isinstance(value, basestring) and not HEX_COLOR.match(value):
            raise exceptions.ValidationError(u'No es un color válido.')

    def formfield(self, **kwargs):
        defaults = {
            'max_length': 7,
            'min_length': 4,
            'form_class': RegexField,
            'regex': HEX_COLOR
        }
        defaults.update(kwargs)
        return super(ColorField, self).formfield(**defaults)


# Registra el campo dict para manejar las migraciones. 
add_introspection_rules([], ["^common\.fields\.DictField"])
add_introspection_rules([], ["^common\.fields\.ListField"])
add_introspection_rules([], ["^common\.fields\.ColorField"])

