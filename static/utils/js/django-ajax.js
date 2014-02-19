/**
 * This file provides a $.djAjax function for making ajax requests
 * that containt the csrf token as a header.
 * For this  to  work,  the CSRF token needs to be present on the page,
 * preferrably added in base.html with {{ csrf }}.
 */

(function($) {

    $.djAjax = function(settings) {

        settings = $.extend(settings, {
            crossDomain: false,
            beforeSend: function(jqXHR, settings) {
                // Pull the token out of the DOM.
                jqXHR.setRequestHeader('X-CSRFToken', $('input[name=csrfmiddlewaretoken]').val());
            },
        });

        $.ajax(settings);
    };

    $.djGet = function(url, data, success, error) {
        $.djAjax({
            type: 'GET',
            url: url,
            data: data,
            success: success,
            error: error
        });
    };

    $.djPost = function(url, data, success, error) {
        $.djAjax({
            type: 'POST',
            url: url,
            data: data,
            success: success,
            error: error
        });
    };

    $.fn.djCrispyAjaxForm = function() {
        var form = this;
        this.submit(function() {
            $.ajax({
                type: 'POST',
                url: form.attr('action'),
                data: form.serialize(),
                success: function(data) {
                    form.replaceWith('<div class="alert alert-success">' + 'Created successfuly.' + '</div>');
                },
                error: function(data, x1, x2, x3) {
                    form.replaceWith(data.responseText);
                }
            });

            return false;
        });
    };

    /**
     * Requires a generic view with the utils.forms.AjaxableResponseMixin mixin.
     */
    $.fn.djAjaxForm = function(settings) {

        settings = $.extend({
            success: null,
            error: null,
        }, settings);

        var form = this;
        this.submit(function() {
            var conf = {
                type: 'POST',
                url: form.attr('action'),
                data: form.serialize(),
                success: function(data) {
                    form.replaceWith('<div class="alert alert-success">' + 'Succesful.' + '</div>');
                },
                error: function(xhr) {
                    data = xhr.responseJSON;
                    if (data && 'errors' in data) {
                        form.find('.form-group').removeClass('has-error');
                        for (var key in data.errors) {
                            form.find('#div_id_' + key).addClass('has-error').attr('title', data.errors[key][0]);
                        }
                    }
                    else {
                        console.log('Unknown error: ', xhr, data);
                    }
                }
            };

            if (settings.success) {
                conf.success = settings.success;
            }
            if (settings.error) {
                conf.error = error;
            }

            $.ajax(conf);

            return false;
        });
    };

}(jQuery));
