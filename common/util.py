# -*- coding: utf-8 -*-
import uuid
import logging

from time import time

  
_generate_uuid = lambda: uuid.uuid4().hex


def generate_uuid():
    """
    Genera una cadena aleatoria única
    """
    return _generate_uuid()


def log_time(message, clean=False, indent=2, initial=None,
                      logmethod=logging.info, extra=''):
    """
    Registra en el log un mensaje con el tiempo de respuesta
    """
    
    prefix = " " * indent
    
    stamp = time()
    
    total = None
    if initial is not None:
        total = stamp - initial
    
    prefix = "%s%s (%s)" % (prefix, extra, stamp)
    if total is not None:
        prefix = "%s|total:%s" % (prefix, total)
    
    message = "%s> %s" % (prefix, message)
    message = message if clean else message.ljust(40, '-')

    if logmethod is not None:
        logmethod(message)
        return stamp

    return message


