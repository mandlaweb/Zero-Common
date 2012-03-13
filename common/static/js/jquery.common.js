/**
 * © Copyright 2011 Jose Maria Zambrana Arze
 *
 * @author Jose Maria Zambrana Arze <contact@josezambrana.com>
 *
 **/

var utils = {
    log_object: function(obj){
        for (var field in obj) {
            jQuery(document).log(field + ": " + obj[field])
        }
    },
    trim: function(text) {
        /* Elimina los espacios al principio y al final de una oración */

        return text.replace(/\s+$/,'').replace(/^\s+/,'');
    },
    inner_trim: function(text) {
        /* Elimina los espacios repetidos dentro de una oración */

        return text.replace(/\s+/g,' ')
    },
    split2array: function(text, character) {
        /* Devuelve un array cortado por character */

        if (character == undefined) {character = ' '}
        return text.split(character)
    },
    counter: {
        words: function(text, character) {
            /* Devuelve el numero de palabras */
            if (character == undefined) {character = ' '}
            if (text == undefined) {return 0;}

            return utils.split2array(utils.inner_trim(utils.trim(text))).length
        },
        tags: function(text) {
            /* Devuelve el numero de palabras */
            tags = utils.split2array(text, ',')
            count = 0
            for(tag in tags) {
                tag = utils.inner_trim(utils.trim(tags[tag]))
                if (tag != '') {
                    count++
                }
            }
            return count
        },
        chars: function(text) {
            /* Devuelve el numero de caracteres */
            if (text == undefined) {
                return 0;
            }
            return text.length;
        }
    },
    redirect: function(url) {
        // simulates similar behavior as an HTTP redirect
        window.location.replace(url);
    },
    replace_link: function($link, options) {
        /* Modifica un enlace por uno nuevo */
        
        // Remplazamos el enlace
        href = $link.attr('href');
        $link.attr('href', options.new_href);

        // Reemplazamos las clases
        $link.removeClass(options.old_class);
        $link.addClass(options.new_class);

        // Reemplazamos el texto
        $link.html(options.new_html);
    }
}

jQuery.noConflict();

(function($) {
    /***
     * Añade la opción de logging a los elementos jquery
     ***/

    $.fn.log = function (msg, options) {
        settings = {
            level: 'info'
        }
        try {
            if (settings.level == 'info') {
                console.log("%s: %o", msg, this);
            } else if (settings.level == 'error') {
                console.error("%s: %o", msg, this);
            }

            return this;
        } catch(e) {
            //alert(msg)
        }
        return this;
    };
})(jQuery);


var messages = {
    generate: function(type, options) {
        return jQuery("<div class='" + type + " corner' />").html(options.content)
    }
};


(function($) {
    /***
     * Configura el elementos que esta actuando como un mensaje del sistema
     **/
    
    $.fn.message = function(options) {
        var settings = {
            "fadeout": 1000,
            "delay": 5000,
            "closeklass": ".close"
        }
        
        if (options){
            $.extend(settings, options);
        }

        this.each(function(){
            $(this).delay(settings.delay)
                   .fadeOut(settings.fadeout);
        })
        
        $(settings.closeklass).click(function(event) {
            event.preventDefault();
            $($(this).attr("href"))
                     .clearQueue()
                     .fadeOut(settings.fadeout);
        });
    }
})(jQuery);

(function($) {
    /* *
     * Añade la clase cuando el puntero esta sobre el elemento y lo elimina 
     * cuando ya no lo esta.
     * */

    $.fn.addHover = function(options) {
        var settings = { klass: 'hover' }

        if (options) {
            $.extend(settings, options)
        }

        return this.hover(
            function(){ $(this).addClass(settings.klass); },
            function(){ $(this).removeClass(settings.klass); }
        )
    }
})(jQuery);


(function($) {
    /***
     * Incrementa o decrementa un contador definido en un elemento html. Recibe 
     * un parametro con la acción a realizar *increase* o *decrease*
     ***/
    $.fn.counter = function(action) {
        var $counter = this;
        
        if (action == 'decrease') {
            extra = -1;
        } else if (action == 'increase') {
            extra = 1;
        } else {
            console.error('invalid action')
            extra = 0;
        }

        try {
            $counter.html(parseInt($counter.html()) + extra)
        } catch (e) {
            $counter.log('El elemento no es un contador', {'level': 'error'});
        }

        return $counter;
    };
})(jQuery);


(function($) {
    /***
     * Configura un enlace para que acte como acción asincrona.
     **/
    
    $.fn.action = function(delegated, options) {
        var $object = this,
            selector = $object.selector;

        var show_alert = function($object, $link, data) {
            alert(data.message)
        }
        
        // Sobrescribimos la configuración
        var settings = {
            check_confirm: false,
            onsuccess: show_alert,
            onfail: show_alert,
            oncancel: show_alert
        };

        if (options) {
            $.extend(settings, options);
        }
        
        $object.delegate(delegated, 'click', function(event) {
            event.preventDefault();
            
            var $delegated = $(this),
                $object = $delegated.parents(selector),
                continue_action = true,
                url_action = $delegated.attr('href')
            
            // Verifica si la acción requiere confirmación.
            if (settings.check_confirm) {
                var confirm_message = "",
                    confirm_action = false;
                
                $.ajax({
                    url: url_action,
                    success: function(json) {
                        if (json.success) {
                            confirm_action = json.confirm
                            confirm_message = json.confirm_message
                        }
                    },
                    async: false,
                    dataType: 'json'
                });
                
                // Solicita la confirmación del usuario.
                if (confirm_action) {
                    continue_action = confirm(confirm_message)
                }
            }
            
            if (continue_action) {
                // Enviamos la petición para realizar la acción.
                $.post(url_action, function(json) {
                    if (json.success) {
                        settings.onsuccess($object, $delegated, json);
                    } else {
                        settings.onfail($object, $delegated, json);
                    }
                });
            } else {
                settings.oncancel($object, $delegated);
            }
        })
    }
})(jQuery);

(function($) {
    /***
     * Configura un formulario para que sea procesado asincronamente.
     ***/

    $.fn.async_form = function(options) {
        var show_message = function($form, json) {
            alert(json.message)
        }

        settings = {
            submit_selector: 'button',
            onsuccess: show_message,
            onfail: show_message
        }
        if (options) {
           $.extend(settings, options)
        }

        this.submit(function(event) {
            event.preventDefault();
            var $form = jQuery(this),
                $button = $form.find(settings.submit_selector);
            
            jQuery.post(
                $form.attr('action'), 
                $form.serialize(),
                function(json) {
                    if (json.success) {
                        settings.onsuccess($form, json);
                    } else {
                        settings.onfail($form, json);
                    }
                },
                'json'
            );
        });

    }
})(jQuery);


(function($) {
    /***
     * Configura una lista de elementos para que actuen como pestañas.
     ***/

    $.fn.tabs = function(options) {
        var $tabs = this,
            $links = $tabs.find('a');
        
        var settings = {
            onselection: function($link, related, $field) {
                // Ocultamos todos los relacionados.
                for (var index in related) {
                    jQuery(related[index]).log('related').hide();
                }

                // Mostramos el relacionado pertinente
                $field.log('field').show();
            }
        };

        if (options) {
            $.extend(settings, options);
        }
        
        $links.log('tab links').click(function(event) {
            event.preventDefault();
            
            $links.removeClass('current');
            $link = $(this);
            $link.addClass('current')
            var $field = settings.get_related($link);
            settings.onselection($link, settings.related, $field);
        });
    };
})(jQuery);

