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
import tempfile
import shutil

from django.test import TestCase
from django.test.client import Client
from django.test.client import RequestFactory

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch
from django.utils import simplejson
from django import forms

from common.views import BaseView
from common.views import ActionView
from common.views import LoginRequiredMixin
from common.views import OwnerRequiredMixin
from common.views import FormView
from common.views import CreateView
from common.views import UpdateView
from common.models import Content


current_site = Site.objects.get_current()


class TestBase(TestCase):
    """
    Clase base con metodos esenciales para trabajar con tests.
    """

    #: El nombre de usuario del usuario de ejemplo ha utilizarse.
    username = 'fakeaccount'
    #: La contraseña del usuario de ejemplo.
    password = 'fakepass'
    #: El email del usuario de ejemplo
    email = 'account@fake.com'
    #: Nombre del servidor
    server_name = 'www.example.com'
    
    def setUp(self):
        # Definimos la aplicación para testing
        settings.TEST = True
        
        # Configuramos el media root como un directorio temporal
        self.__old_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = tempfile.mkdtemp()
        
        # Definimos el cliente y la fabrica de requests
        self.client = Client(SERVER_NAME=self.server_name)
        self.request_factory = RequestFactory()
        
        # Creamos un usuario de ejemplo
        self.user = User.objects.create(username=self.username, email=self.email)
        self.user.set_password(self.password)
        self.user.save()
        
        # Definimos el nivel de logging.
        logging.getLogger().setLevel(logging.INFO)

    def tearDown(self):
        # Eliminamos el directorio temporal y restablecemos el media root
        shutil.rmtree(settings.MEDIA_ROOT)
        self.MEDIA_ROOT = self.__old_media_root
    
    def request_get(self, path, **kwargs):
        """
        Retorna un request de tipo GET para validar vistas con la dirección *path*
        """

        return self.request_factory.get(path, **kwargs)
    
    def request_post(self, path, **kwargs):
        """
        Retorna un request de tipo POST para validar vistas con la direción *path*
        """

        return self.request_factory.post(path, **kwargs)

    def request_get_ajax(self, path, **kwargs):
        """
        Retorna un request ajax de tipo GET
        """
        
        kwargs.update({'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        return self.request_get(path, **kwargs)

    def request_post_ajax(self, path, **kwargs):
        """
        Retorna un request ajax de tipo POST
        """

        kwargs.update({'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        return self.request_post(path, **kwargs)
    
    def view_request(self, view, path='/', data={}, method='get', ajax=False, username=None, **kwargs):
        """
        Retorna la respuesta de la vista *view* con el path *path* y los datos
        *data* pasados con el método *method*. *ajax* define si es asincrono o 
        no.
        """

        methods = {
            'get': self.request_get,
            'post': self.request_post,
            'get_ajax': self.request_get_ajax,
            'post_ajax': self.request_post_ajax
        }
        method = 'get' if method.lower() == 'get' else 'post'
        method = '%s_ajax' % method if ajax else method
        
        request_call = methods.get(method)
        request = request_call(path, data=data)
        
        if username is not None:
            self._logged_user(request, username=username)
        else:
            self._anonymous_user(request)

        view_call = view.as_view()
        response = view_call(request, **kwargs)

        if hasattr(response, 'render'):
            response.render()
        
        return response

    def view_get(self, view, path='/', data={}, **kwargs):
        return self.view_request(view, path, data=data, method='get', ajax=False, **kwargs)

    def view_get_ajax(self, view, path='/', data={}, **kwargs):
        response = self.view_request(view, path, data=data, method='get', ajax=True, **kwargs)
        return simplejson.loads(response.content)

    def view_post(self, view, path='/', data={}, **kwargs):
        return self.view_request(view, path, data=data, method='post', ajax=False, **kwargs)

    def view_post_ajax(self, view, path='/', data={}, **kwargs):
        response = self.view_request(view, path, data=data, method='post', ajax=True, **kwargs)
        return simplejson.loads(response.content)
    
    def create_url(self, view_name, args=[]):
        """
        Crea la url con el nombre del dominio y el path completo
        """
        path = reverse(view_name, args=args)

        return "http://%s%s" % (current_site.domain, path)

    def client_request(self, name, args=[], data={}, follow=False, method='get', **kwargs):
        """
        Realiza una petición usando el cliente de tests de django a la vista de
        nombre *name* usando los argumentos *args* para la url y los datos
        *data* para la petición.
        
        Por ejemplo, para editar una entrada de blog con id *1* se realiza una 
        llamada POST a la siguiente vista::

            # la vista es:
            # url(r'posts/(?P<id>\d+)/edit', 'blog.views.create', name='blog_create')
            
            # los datos:
            data = {'title': 'nuevo titulo'
                    'body': 'body test'}

            # la petición
            client_request('blog_create', args=[1], data=data, method='post')

        """

        logging.info((' %s ' % method).upper().center(60, '*'))
        
        try:
            url = self.create_url(name, args=args)
        except NoReverseMatch:
            url = name

        call = getattr(self.client, method, 'get')

        logging.info("   * url: %s " % url)

        return call(url, data=data, follow=follow, **kwargs)

    def client_get(self, name, **kwargs):
        """
        Método de atajo para realizar una llamada get.
        """

        kwargs['method'] = 'get'
        return self.client_request(name, **kwargs)

    def client_post(self, name, **kwargs):
        """
        Método de atajo para realizar una llamada post.
        """

        kwargs['method'] = 'post'
        return self.client_request(name, **kwargs)

    def client_get_ajax(self, name, **kwargs):
        """
        Método de atajo para realizar una llamada get AJAX. Retorna la 
        respuesta en un diccionario.
        """

        kwargs.update({'HTTP_X_REQUESTED_WITH':'XMLHttpRequest'})
        response = self.client_get(name, **kwargs)
        return simplejson.loads(response.content)

    def client_post_ajax(self, name, **kwargs):
        """
        Método de atajo para realizar una llamada *post* AJAX. Retorna la
        respuesta en un diccionario.
        """

        kwargs.update({'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        response = self.client_post(name, **kwargs)
        return simplejson.loads(response.content)

    def login(self, username, password, **kwargs):
        """
        Atajo para identificar un usuario en el sitio.
        """

        data = {
            'username': username, 
            'password': password
        }
        response = self.client_post('users_login', data=data, **kwargs)
        assert response.status_code == 302
        return response

    def logout(self):
        """
        Atajo para hacer salir al usuario del sitio.
        """

        return self.client_get('users_logout')
    
    def _login(self):
        """
        Identifica al usuario de ejemplo.
        """

        # Verificamos que nombre de usuario y el password son correctos
        query = User.objects.filter(username=self.username)
        assert query.exists()
        user = query.get()
        assert user.check_password(self.password)

        # Identificamos al usuario
        response = self.login(self.username, self.password)

    def _logged_user(self, request, username=None):
        """
        Define en el request al usuario de ejemplo.
        """

        request.__class__.user = self.get_user(username=username)

    def _anonymous_user(self, request):
        """
        Crea un usuario anónimo de ejemplo en el request.
        """

        from django.contrib.auth.models import AnonymousUser
        request.__class__.user = AnonymousUser()

    def get_user(self, username=None):
        """
        Retorna el usuario con nombre de usuario *username* en caso de que 
        *username* sea *None* retorna el usuario de ejemplo definido en la 
        clase.
        """
        
        if username is None:
             username = self.username
             
        return User.objects.get(username=username)

    def assertLoginRequired(self, view_name, **kwargs):
        """
        Verifica que la vista requiere que el usuario este identificado.
        """

        from django.contrib.auth import REDIRECT_FIELD_NAME
        
        # Verificamos que el usuario tienen que estar logueado
        response = self.client_get(view_name, **kwargs)
        expected_url = 'http://%s%s?%s=%s' % (self.server_name,
                                     reverse('users_login'),
                                     REDIRECT_FIELD_NAME,
                                     reverse(view_name))
        self.assertRedirects(response, expected_url)

    @classmethod
    def _update(cls, content):
        model = content.__class__
        content = model.objects.get(pk=content.id)
        return content


class SomeView(BaseView):
    view_name = 'some-view'
    app_name = 'common'
    templates = {
        'html': 'base/base.html',
        'atom': 'base/atom.xml'
    }


class TestClassViews(TestBase):
    def get_json(self, response):
        return simplejson.loads(response.content)
    
    def test_json_response(self):
        """
        La vista debe ser capaz de retornar en formato json una vista.
        """
        
        # Generamos el request con un usuario anonimo
        request = self.request_get('/')
        self._anonymous_user(request)
        
        # Verificamos que la vista retorna un objeto json.
        view = SomeView.as_view()
        assert self.get_json(view(request, format='json')) is not None

        
    def _create_view(self, request, **kwargs):
        view = SomeView()
        view.request = request
        view.kwargs = kwargs
        return view

    def test_format_returned(self):
        """
        La vista debe ser capaz de utilizar el formato adecuado.
        """

        # Cuando es un request ajax utilizar json.
        request = self.request_get_ajax('/')
        view = self._create_view(request)
        format = view.get_format()
        assert view.get_format() == 'json'
        
        # Utilizar el formato que se pase por parametro.
        request = self.request_get('/')
        view = self._create_view(request, format='atom')
        assert view.get_format() == 'atom'
        
        # Solo permitir los formatos definidos en MIMES
        request = self.request_get('/')
        view = self._create_view(request, format='txt')
        from django.core.exceptions import ImproperlyConfigured
        self.assertRaises(ImproperlyConfigured, lambda: view.get_format())

    def test_redirect_when_is_defined(self):
        """
        La vista debe ser capaz de redireccionar en caso de que asi se lo defina.
        """

        request = self.request_get('/')
        view = self._create_view(request, format='html')
        
        # Verificamos el comportamiento por defecto
        response = view.render_to_response({})
        assert response.status_code == 200
        
        # Verificamos la redirección.
        view.redirect = True
        view.redirect_url = '/otra_url'
        response = view.render_to_response({})
        assert response.status_code == 302
        assert response['Location'] == '/otra_url'

        # Verificamos la redirección en ajax.
        request = self.request_get_ajax('/')
        view = self._create_view(request)
        view.redirect = True
        view.redirect_url = '/otra_url'
        response = view.render_to_response({})
        json_response = simplejson.loads(response.content)
        assert json_response['redirect']
        assert 'redirect_url' in json_response

        # Verificamos que es necesario definir una dirección para redireccionar
        view = self._create_view(request, format='html')
        view.redirect = True
        from django.core.exceptions import ImproperlyConfigured
        self.assertRaises(ImproperlyConfigured, lambda: view.render_to_response({}))
        

class ViewLoginRequired(LoginRequiredMixin, BaseView):
    view_name = 'login-required'
    app_name = 'common'


class TestLoginRequired(TestBase):
    """
    Clase para validar el mixin que obliga a que un usuario este conectado al
    tratar de acceder a una vista.
    """
    
    def test_verify_redirect_to_login(self):
        """
        El sistema debe ser capaz de redireccionar a la página de 
        identificación cuando se requiera la identificación del usuario.
        """
        
        # Via html
        response = self.view_get(ViewLoginRequired)
        assert response.status_code == 302
        assert response['Location'].startswith(settings.LOGIN_URL)
        
        # Via ajax
        response = self.view_get_ajax(ViewLoginRequired)
        assert not response['success']
        assert 'message' in response


    def test_continue_if_user_is_logged_in(self):
        """
        El sistema deber ser capaz de continuar con la petición si la vista
        requiere identificación y el usuario esta identificado.
        """
        
        # Via html
        response = self.view_get(ViewLoginRequired, username=self.username)
        assert response.status_code == 200
        
        # Via ajax
        response = self.view_get_ajax(ViewLoginRequired, username=self.username)
        assert response['success']


class SomeContent(Content):
    def get_absolute_url(self):
        return '/content/%s' % self.slug


class TestContent(TestBase):
    """

    """

    def setUp(self):
        super(TestContent, self).setUp()
        self.user = User.objects.create(username='testuser')
        self.content = SomeContent.objects.create(name='Test content', 
                user=self.user)

    def test_content_slug_create(self):
        """
        Un contenido debe crear su slug a partir del nombre
        """
        
        content = SomeContent.objects.create(name='Test slug', user=self.user)
        assert content.slug == 'test-slug'

    def test_content_slug_unique(self):
        """
        El contenido debe ser capaz de crear un slug unico.
        """
        
        content = SomeContent.objects.create(name='Test content', user=self.user)
        assert self.content.slug != content.slug

    def test_content_slug_unique_on_update(self):
        """
        El contenido debe ser capaz de crear un slug único cuando se actualiza
        sin solaparse con otros.
        """

        content = SomeContent.objects.create(name='Test a content', user=self.user)
        old_slug = content.slug
        content.name = 'Test content'
        content.save()

        assert content.slug != old_slug
        assert content.slug != self.content.slug


class WithOwnerRequired(OwnerRequiredMixin, BaseView):
    model = SomeContent


class TestOwnerRequired(TestBase):
    def setUp(self):
        super(TestOwnerRequired, self).setUp()
        
        self.owner = User.objects.create(username='owner')
        self.owner.set_password(self.password)
        self.owner.save()

        self.content = SomeContent.objects.create(name='Test', user=self.owner)

    def test_fail_when_is_not_the_owner(self):
        """
        El sistema no debe permitir visitar una vista que involucra un objeto y
        requiera que el usuario sea el propietario.
        """
        
        # Se necesita que el usuario este logueado.
        response = self.view_get(WithOwnerRequired, pk=self.content.id)
        assert response.status_code == 302
        response_json = self.view_get_ajax(WithOwnerRequired, pk=self.content.id)
        assert not response_json['success']

        # Se necesita que el usuario sea el propietario.
        response = self.view_get(WithOwnerRequired, pk=self.content.id, username=self.username)
        assert response.status_code == 302
        response_json = self.view_get_ajax(WithOwnerRequired, pk=self.content.id, username=self.username)
        assert not response_json['success']

    def test_continue_if_it_is_the_owner(self):
        """
        El sistema debe ser capaz de continuar si la vista require propiedad
        sobre el objeto incolucrado y el usuario activo es el propietario.
        """

        response = self.view_get(WithOwnerRequired, pk=self.content.id, username=self.owner.username)
        assert response.status_code == 200
        response_json = self.view_get_ajax(WithOwnerRequired, pk=self.content.id, username=self.owner.username)
        assert response_json['success']
        

class SomeActionView(ActionView):
    def action(self, request, **kwargs):
        num = request.REQUEST.get('num', None)
        if num is None:
            self.fail_message = 'No hay un numero'
            return False

        if int(num) % 2 != 0:
            self.fail_message = 'No es par'
            return False

        return True


class TestActionView(TestBase):
    """
    Verifica la funcionalidad de la vista ActionView
    """
    
    def setUp(self):
        super(TestActionView, self).setUp()
        self.action = ActionView()
    
    def test_action_get(self):
        """
        La vista debe ser capaz de mostrar un formulario de confirmación.
        """
        
        response = self.view_get(SomeActionView)
        self.assertContains(response, SomeActionView.confirm_message)

    def test_action_post(self):
        """
        La vista debe ser capaz de redireccionar al lugar adecuado en caso de 
        una operación exitosa o cuando exista un fallo.
        """
        
        # Operación exitosa
        response = self.view_post(SomeActionView, data={'num': 2})
        self.assertEquals(response['Location'], SomeActionView.get_success_redirect_url())

        # Operación con fallo
        response = self.view_post(SomeActionView, data={'num': 1})
        self.assertEquals(response['Location'], SomeActionView.get_fail_redirect_url())

    def test_action_get_ajax(self):
        """
        La vista debe retornar un diccionario en json con el mensaje de 
        confirmación cuando se realiza una llamada ajax de tipo GET
        """
        
        response = self.view_get_ajax(SomeActionView)
        assert 'confirm_message' in response
        assert SomeActionView.confirm_message == response.get('confirm_message')

    def test_action_post_ajax(self):
        """
        La vista debe ser capaz de retornar un valor positivo en caso de que la
        acción se realizó correctament o negativo en caso contrario. Además de
        un mensaje de éxito o fallo.
        """

        response = self.view_post_ajax(SomeActionView, data={'num': 2})
        assert response['success']
        assert SomeActionView.success_message == response['message']

        response = self.view_post_ajax(SomeActionView, data={})
        assert not response['success']
        assert 'No hay un numero' == response['message']

        response = self.view_post_ajax(SomeActionView, data={'num': 1})
        assert not response['success']
        assert 'No es par' == response['message']


class SomeForm(forms.Form):
    some_text = forms.CharField(max_length=255)


class TFormView(FormView):
    view_name = 'form-view'
    app_name = 'common'
    form_class = SomeForm


class TestFormMixin(TestBase):
    """
    Valida el mixin para manejar formularios.
    """
    
    def setUp(self):
        super(TestFormMixin, self).setUp()
    
    def test_html_form_get(self):
        """
        El sistema debe ser capaz de retornar el html del formulario cuando se 
        realiza una llamada GET por ajax.
        """

        response = self.view_get_ajax(TFormView)
        assert response['success']
        assert 'form' in response
        assert not response['redirect']
        
        response = self.view_get(TFormView)
        self.assertContains(response, '<form')
        self.assertContains(response, 'some_text')

    def test_valid_form_response(self):
        """
        El sistema debe ser capaz de retornar un mensaje de suceso en caso de 
        que se halla procesado correctamente el formulario.
        """

        response = self.view_post_ajax(TFormView, data={ 'some_text': 'test' } )
        assert response['success']
        assert 'message' in response
        logging.info('valid message: %s ' % response['message'])

        response = self.view_post(TFormView, data={ 'some_text': 'test' })
        assert response.status_code == 302
        
    def test_fail_form(self):
        """
        El sistema debe ser capaz de retornar un mensaje de fallo en caso de
        que haya existido un error en el proceso.
        """

        response = self.view_post_ajax(TFormView, data={})
        assert not response['success']
        assert 'message' in response
        logging.info('fail message: %s ' % response['message'])

        response = self.view_post(TFormView, data={})
        assert response.status_code == 200


class TCreateView(CreateView):
    view_name = 'create-view'
    app_name = 'common'
    model = SomeContent
    template_object = 'inc.content.html'
    

class TestCreateView(TestBase):
    def setUp(self):
        super(TestCreateView, self).setUp()
        self.user = User.objects.create(username='testuser')
        self.data = {
            'name': 'My test content',
            'user': self.user.id,
            'slug': 'my-test-content'
        }

    def test_valid_form(self):
        """
        El sistema debe ser capaz de crear un objeto cuando se envia valores 
        válidos por POST.
        """
        initial_count = SomeContent.objects.count()
        response = self.view_post(TCreateView, data=self.data)
        assert response.status_code == 302
        assert response['Location'] == '/content/my-test-content'
        assert (initial_count + 1) == SomeContent.objects.count()
        
        # Via ajax
        response  = self.view_post_ajax(TCreateView, data=self.data)
        assert 'message' in response
        assert response['success']
        assert 'object' in response and response['object'] is not None
        assert 'pk' in response and response['pk'] is not None
        assert (initial_count + 2) == SomeContent.objects.count()
    
    def test_invalid_form(self):
        """
        El sistema debe ser capaz debe ser capaz de lidiar con los errores de
        valiación.
        """
        initial_count = SomeContent.objects.count()
        self.data['name'] = ''
        self.data['slug'] = ''

        response = self.view_post(TCreateView, data=self.data)
        assert response.status_code == 200
        assert initial_count == SomeContent.objects.count()

        response = self.view_post_ajax(TCreateView, data=self.data)
        assert not response['success']
        assert 'message' in response
        assert initial_count == SomeContent.objects.count()

        logging.info('message: %s ' % response['message'])


class TUpdateView(UpdateView):
    view_name = 'update-view'
    app_name = 'common'
    model = SomeContent
    template_object = 'inc.content.html'


class TestUpdateView(TestBase):
    def setUp(self):
        super(TestUpdateView, self).setUp()

        self.content = SomeContent.objects.create(name='test content', 
                                                  user=self.user)
        self.data = {
            'name': 'test content',
            'user': self.user.id,
            'slug': 'test-content',
        }

    def test_valid_update(self):
        """
        El sistema debe ser capaz de actualizar los datos de un objeto.
        """
        new_name = 'name updated'
        initial_count = SomeContent.objects.count()
        self.data['name'] = new_name
        
        response = self.view_post(TUpdateView, data=self.data, pk=self.content.id)
        content = SomeContent.objects.get(pk=self.content.id)
        
        assert response.status_code == 302
        assert response['Location'] == content.get_absolute_url()
        assert content.name == new_name
        assert initial_count == SomeContent.objects.count()
        
        new_name = 'name updated by ajax'
        self.data['name'] = new_name
        
        response_ajax = self.view_post_ajax(TUpdateView, data=self.data, pk=self.content.id)
        content = SomeContent.objects.get(pk=self.content.id)
        
        assert response_ajax['success']
        assert 'pk' in response_ajax and response_ajax['pk'] == content.pk
        assert content.name == new_name
        assert initial_count == SomeContent.objects.count()
        assert 'message' in response_ajax and response_ajax['message'] is not None
        assert 'object' in response_ajax and response_ajax['object'] is not None

    def test_invalid_update(self):
        """
        El sistema debe ser capaz de lidiar con valores invalidos al momento
        de actualizar un objeto.
        """
        
        old_name = self.content.name
        self.data['name'] = ''

        response = self.view_post(TUpdateView, data=self.data, pk=self.content.id)
        content = SomeContent.objects.get(pk=self.content.id)
        assert response.status_code == 200
        assert content.name == old_name

        response_ajax = self.view_post_ajax(TUpdateView, data=self.data, pk=self.content.id)
        content = SomeContent.objects.get(pk=self.content.id)
        assert not response_ajax['success']
        assert 'message' in response_ajax and response_ajax['message'] is not None
        assert content.name == old_name



