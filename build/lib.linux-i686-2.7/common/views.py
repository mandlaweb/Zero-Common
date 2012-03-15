# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import REDIRECT_FIELD_NAME

from django.http import Http404
from django.template.loader import render_to_string
from django.forms import models as model_forms

from django.views.generic import View

from django.views.generic import TemplateView as DjangoTemplateView
from django.views.generic import CreateView as DjangoCreateView
from django.views.generic import DetailView as DjangoDetailView
from django.views.generic import ListView as DjangoListView
from django.views.generic import UpdateView as DjangoUpdateView
from django.views.generic import DeleteView as DjangoDeleteView

from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin
from django.views.generic.edit import ProcessFormView
from django.views.generic.edit import BaseFormView

from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse

from django.shortcuts import redirect


MIMES = {
    'html': 'text/html',
    'xhtml': 'text/html',
    'json': 'application/json',
    'atom': 'application/atom+xml',
    'xml': 'application/xml'
}


class TemplateView(DjangoTemplateView):
    def get_context_data(self, **kwargs):
        return kwargs


class MultipleFormatResponseMixin(TemplateResponseMixin):
    """
    Clase vista para retornar en multiples formatos.
    """
    
    #: Formato de la respuesta
    format = None

    #: Formato por defecto
    default_format = 'html'

    #: Templates por formato
    templates = {
        'html': 'base/base.html',
    }

    #: Determina si se tiene que redireccionar.
    redirect = None
    #: La url donde se tiene que redireccionar.
    redirect_url = None
     
    def get_format(self):
        """
        Retorna el formato en el que se ha de renderizar la página
        """
        
        if self.format is not None:
            return self.format
        
        if self.request.is_ajax():
            self.format = 'json'
        else:
            self.format = self.kwargs.get('format', self.default_format)
        
        # TODO: esto no esta muy coherente.
        if self.format in self.templates or self.format == 'json':
            return self.format
        
        raise ImproperlyConfigured(u'Format not allowed: %s ' % self.format)
    
    def get_template_names(self):
        """
        Retorna el template que se ha de utilizar para renderizar la página
        """

        format = self.get_format()
        
        if format not in self.templates:
            raise ImproperlyConfigured('%s have to define a template for '
                    'format %s' % (self.__class__.__name__, format))
        else:
            template = self.templates.get(format)

            return [template]

    def get_redirect_url(self, **kwargs):
        """
        Retorna la url donde redireccionar.
        """

        if self.redirect_url is not None:
            return self.redirect_url

        raise ImproperlyConfigured('%s have to define a redirect url'
                % self.__class__.__name__)
    
    def get_json_response(self, context):
        """
        Obtiene la respuesta de la vista en formato json
        """
        
        json_data = json.dumps(context)
        
        return HttpResponse(json_data, 'application/json')
    
    def render_to_response(self, context, **response_kwargs):
        """
        Retorna la respuesta a la llamada de la vista.
        """
        
        self.format = self.get_format()
         
        if self.format == 'json':
            if self.redirect:
                context['redirect'] = True
                context['redirect_url'] = self.get_redirect_url()
            else:
                context['redirect'] = False

            return self.get_json_response(context)

        elif self.format == 'html':
            if self.redirect:
                return redirect(self.get_redirect_url())

        response_kwargs['mimetype'] = MIMES.get(format, 'text/html')
        
        return super(MultipleFormatResponseMixin, self).render_to_response(context, **response_kwargs)
    

class BaseViewMixin(object):
    """
    Clase vista base para todas las clases vista del proyecto.
    """
    
    #: Nombre de la vista
    view_name = None
    #: Título de la pagina legible para una persona
    title = None
    #: Nombre de la app
    app_name = None

    def get_view_name(self):
        """
        Retorna el nombre de la vista.
        """

        if self.view_name is not None:
            return self.view_name
        
        raise ImproperlyConfigured('%s have to define view_name' 
                % self.__class__.__name__)

    def get_title(self):
        """
        Retorna el título de la página.
        """

        if self.title is not None:
            return self.title

        try:
            return self.get_view_name()
        except ImproperlyConfigured, e:
            raise ImproperlyConfigured('%s have to define title or view_name'
                    % self.__class__.__name__)

    def get_app_name(self):
        """
        Retorna el nombre de la app.
        """
        
        if self.app_name is not None:
            return self.app_name
        
        raise ImproperlyConfigured('%s have to define an app_name' 
                % self.__class__.__name__)
        
    def get_context_data(self, **context):
        """
        Añade las variables básicas de la vista al contexto
        """

        context = super(BaseViewMixin, self).get_context_data(**context)
        context.update({
            'app_name': self.get_app_name(),
            'view_name': self.get_view_name(),
            'title': self.get_title(),
        })

        if self.get_format() != 'json':
            context.update({
                'request': self.request,
                'user': self.request.user
            })

        return context


class BaseView(MultipleFormatResponseMixin, BaseViewMixin, TemplateView):
    """
    Clase base de las vistas definidas por el desarrollador que no estan dentro
    del CRUD.
    """
    pass


class ActionResponseMixin(MultipleFormatResponseMixin):
    """
    Mixin para manejar acciones.
    """

    #: El mensaje que se muestra cuando la acción se ejecuta correctamente.
    success_message = _(u'La acción se realizo exitosamente')
    #: Si se necesita mostrar el mensaje de suceso
    show_success_message = True
    
    #: El mensaje que se muestra cuando la acción no se completo
    fail_message = _(u'La acción no pudo realizarse')
    #: Si se necesita mostrar el mensaje de falla.
    show_fail_message = True
    
    #: Si se redireccionará en caso de suceso o falla. Solo ajax en otro caso siempre redirecciona.
    redirect = False
    #: La url donde redireccionar si la acción se ejecuta exitosamente.
    success_url = None
    #: La url donde redireccionar si la acción falla.
    fail_url = None
    #: Si la acción se realizo con éxito o no.
    success = None
    
    def get_context_data(self, success=True, **context):
        """
        Retorna el contexto de la acción
        """
  
        self.success = success
        
        context.update({
            'success': success,
            'message': self.get_message(success),
            'redirect': self.redirect
        })
        
        if self.redirect and self.request.method == 'POST':
            context['redirect_url'] = self.get_redirect_url(success)
        
        return context

    def get_message(self, success):
        """
        Retorna el mensaje apropiado de acuerdo y existio una acción exitosa o
        si hubo una falla.
        """
        
        message = self.success_message if success else self.fail_message
        return unicode(message)
    
    @classmethod
    def get_success_redirect_url(self):
        """
        Retorna la url para redireccionar en caso de suceso.
        """
        
        if self.success_url is not None:
            return self.success_url
        
        self.success_url = reverse('home')
        return self.success_url
    
    @classmethod
    def get_fail_redirect_url(self):
        """
        Retorna la url para redireccionar en caso de falla.
        """
        
        if self.fail_url is not None:
            return self.fail_url
        
        self.fail_url = reverse('error')
        return self.fail_url
    
    def get_redirect_url(self, success=None):
        """
        Retorna la url apropiada para redireccionar.
        """

        if success is None:
            if self.redirect_url is not None:
                return self.redirect_url
            else:
                raise ImproperlyConfigured(u'La variable success tiene que ser Falso o verdadero')

        if success:
            return self.get_success_redirect_url()
        
        return self.get_fail_redirect_url()

    def action_response(self, success=True, message=None, redirect=None, 
                        redirect_url=None, **kwargs):
        """
        Retorna la respuesta de la acción.
        """

        self.success = success
        
        if message is not None:
            if success:
                self.success_message = message
            else:
                self.fail_message = message

        if redirect is not None:
            self.redirect = redirect

        if redirect_url is not None:
            self.redirect_url = redirect_url
        
        context = self.get_context_data(success=success, **kwargs)

        return self.render_to_response(context)

    def fail_response(self, message=None, redirect=None, redirect_url=None, 
                        **kwargs):
        """
        Retorna una respuesta de acción fallida.
        """

        return self.action_response(success=False,
                                    message=message,
                                    redirect=redirect,
                                    redirect_url=redirect_url,
                                    **kwargs)

    def success_response(self, message=None, redirect=None, redirect_url=None, 
                        **kwargs):
        """
        Retorna una respuesta de acción exitosa
        """
        
        return self.action_response(success=True,
                                    message=message,
                                    redirect=redirect,
                                    redirect_url=redirect_url,
                                    **kwargs)


class LoginRequiredMixin(ActionResponseMixin):
    """
    Mixin para todas las vistas que necesitas al usuario identificado.
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Despacha al metodo adecuado verificando si el usuario esta identificado,
        si no, redirecciona a la página de login.
        """

        self.request = request
        self.args = args
        self.kwargs = kwargs
        
        if not request.user.is_authenticated():
            url = '%s?%s=%s' % (settings.LOGIN_URL, REDIRECT_FIELD_NAME, request.get_full_path())
            return self.fail_response(message=_(u'Necesitas identificarte para continuar.'),
                                      redirect=True, 
                                      redirect_url=url)
        
        return super(LoginRequiredMixin, self).dispatch(request, **kwargs)


class OwnerRequiredMixin(LoginRequiredMixin, SingleObjectMixin):
    """
    Mixin para verificar la propiedad de un usuario sobre un objeto.
    """

    def get_object(self):
        if hasattr(self, 'object') and self.object is not None:
            return self.object
        else:
            return super(OwnerRequiredMixin, self).get_object()

    def is_owner(self, content, user): 
        return content.user_id == user.id
    
    def dispatch(self, request, *args, **kwargs):
        """
        Despacha la petición al método apropiado vericando la propiedad del 
        usuario sobre el objeto.
        """ 

        self.request = request
        self.args = args
        self.kwargs = kwargs

        if not request.user.is_authenticated():
            return super(OwnerRequiredMixin, self).dispatch(request, **kwargs)
        
        try:
            self.object = self.get_object()
        except Http404:
            return self.fail_response(_(u'El contenido no existe'), redirect=True, 
                             redirect_url=reverse('error'))
         
        if not self.is_owner(self.object, self.request.user):
            return self.fail_response(_(u'No eres el propietario'), redirect=True, 
                             redirect_url=reverse('error'))
        
        return super(OwnerRequiredMixin, self).dispatch(request, **kwargs)


class BaseFormMixin(ActionResponseMixin):
    """
    Mixin para vistar que procesan formularios.
    """

    template_form = 'forms/form.html'
    
    def get_form_class(self):
        if self.form_class is not None:
            return self.form_class
        else:
            raise ImproperlyConfigured('%s have to define a form_class'
                                        % self.__class__.__name__)

    def get_context_data(self, *args, **kwargs):
        context = super(BaseFormMixin, self).get_context_data(*args, **kwargs)
        
        if self.get_format() == 'json':
            context['form'] = render_to_string(self.template_form, context)
        
        return context

    def get_success_url(self):
        return self.get_success_redirect_url()

    def form_valid(self, form):
        if self.get_format() == 'html':
            self.redirect = True
            self.redirect_url = self.get_success_url()

        return self.success_response(form=form)

    def form_invalid(self, form):
        self.fail_message = self.error_to_string(form)
        return self.fail_response(form=form)

    @classmethod
    def error_to_string(cls, form):
        """
        Retorna los mensajes de error de un formulario en una misma cadena.
        """
        
        errors = []
        for key, error in form.errors.items():
            errors.append('%s: %s' % (key, '. '.join(error)))
        
        message = '\n'.join(errors)
        
        return message


class FormView(BaseViewMixin, BaseFormMixin, BaseFormView):
    """
    Vista base para procesar un formulario
    """
    
    templates = {
        'html': 'page.form.html'
    }


class ModelFormMixin(BaseFormMixin, SingleObjectMixin):
    """
    Vista para mostrar y procesar formularios para crear objetos.
    """

    template_object = None
    
    def get_form_kwargs(self):
        kwargs = super(ModelFormMixin, self).get_form_kwargs()
        kwargs.update({'instance': self.object})
        return kwargs

    def get_form_class(self):
        if self.form_class:
            return self.form_class
        else:
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model

            return model_forms.modelform_factory(model)

    def get_success_redirect_url(self):
        try:
            url = self.object.get_absolute_url()
        except AttributeError:
            url = super(ModelFormMixin, self).get_success_redirect_url()

        return url

    def form_valid(self, form):
        self.object = form.save()
        return super(ModelFormMixin, self).form_valid(form)

    def get_template_object(self):
        if self.template_object is not None:
            return self.template_object
        else:
            raise ImproperlyConfigured('%s have to define a template_object'
                                       % self.__class__.__name__)
    
    def get_context_data(self, success=True, **kwargs):
        context = super(ModelFormMixin, self).get_context_data(success=success, **kwargs)
        
        if hasattr(self, 'object'):
            context['object'] = self.object

            if self.get_format() == 'json' and self.object is not None:
                # Generamos el html del objeto.
                # Añadimos el request y el usuario pero luego lo eliminamos para
                # que se compatible con json
                context['user'] = self.request.user
                context['request'] = self.request
                context['object'] = render_to_string(self.get_template_object(), context)
                del context['user']
                del context['request']

                context['pk'] = self.object.pk

        return context


class CreateView(ModelFormMixin, FormView):
    """
    Clase base de las vistas para crear objetos.
    """
    
    def get(self, request, *args, **kwargs):
        self.object = None
        return super(CreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(CreateView, self).post(request, *args, **kwargs)


class UpdateView(ModelFormMixin, FormView):
    """
    Clase base para actualizar los datos de un objeto.
    """
     
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(UpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(UpdateView, self).post(request, *args, **kwargs)


class ActionView(ActionResponseMixin, TemplateView):
    """
    Vista para manejar acciones sobre objetos.
    """
    
    #: El mensaje que se muestra para confirmar la acción
    confirm_message = _(u'Deseas continuar con esta acción?')
    #: Si se necesita una confirmación para continuar con la acción. Solo en AJAX
    confirm = True
    
    templates = {
        'html': 'page.confirm.html'
    }
    
    def action(self, request, **kwargs):
        raise NotImplementedError
    
    def get_context_data(self, success=True, **context):
        """
        Retorna el contexto de la acción
        """
        
        context.update({
            'confirm_message': unicode(self.confirm_message),
            'confirm': True
        })

        return super(ActionView, self).get_context_data(success=success, **context)

    def post(self, request, **kwargs):
        """
        Ejecuta la acción.
        """
        
        # Ejecutamos la acción
        success = self.action(request, **kwargs)

        format = self.get_format()

        if format == 'html':
            self.redirect = True
            self.redirect_url = self.get_redirect_url(success)
        
        if success:
            return self.success_response()
        else:
            return self.fail_response()


class ListView(BaseViewMixin, MultipleFormatResponseMixin, DjangoListView):
    """
    Clase base de las vistas que muestran una lista de objetos.
    """
    pass


class DetailView(BaseViewMixin, MultipleFormatResponseMixin, DjangoDetailView):
    """
    Clase base de as vistas que muestran un objeto a detalle.
    """
    pass


class DeleteView(OwnerRequiredMixin, ActionView):
    """
    Clase base para eliminar un objeto.
    """
    
    def action(self, request, **kwargs):
        """
        Elimina el objeto.
        """
        
        try:
            content = self.get_object()
            content.delete()
            return True
        except Http404:
            self.fail_message = _(u'El contenido no existe')
            return False
            

class FlashView(BaseView):
    """
    Vista que muestra un mensaje para el usuario
    """

    view_name = 'flash-view'
    app_name = 'common'
    templates = {
        'html': 'flash_view.html'
    }

