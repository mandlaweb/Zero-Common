# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from common.views import FlashView


urlpatterns = patterns('',
    url('^error$', FlashView.as_view(), name='error')
)
