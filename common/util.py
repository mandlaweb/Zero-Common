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


