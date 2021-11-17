$(document).ready(function(){
        
        
    });

    function initModalDialog(event, modal_element) {
        /*
            You can customize the modal layout specifing optional "data" attributes
            in the element (either <a> or <button>) which triggered the event;
            "modal_element" identifies the modal HTML element.

            Sample call:

            <a href=""
               data-title="Set value"
               data-subtitle="Insert the new value to be assigned to the Register"
               data-dialog-class="modal-lg"
               data-icon="fa-keyboard-o"
               data-button-save-label="Save"
               onclick="openModalDialog(event, '#modal_generic'); return false;">
                <i class="fa fa-keyboard-o" style="pointer-events: none;"></i> Open generic modal (no contents)
            </a>
        */
        var modal = $(modal_element);
        var target = $(event.target);

        var title = target.data('title') || '';
        var subtitle = target.data('subtitle') || '';
        // either "modal-lg" or "modal-sm" or nothing
        var dialog_class = (target.data('dialog-class') || '') + ' modal-dialog';
        var icon_class = (target.data('icon') || 'fa-laptop') + ' fa modal-icon';
        var button_save_label = target.data('button-save-label') || 'Save changes';

        modal.find('.modal-dialog').attr('class', dialog_class);
        modal.find('.modal-title').text(title);
        modal.find('.modal-subtitle').text(subtitle);
        modal.find('.modal-header .title-wrapper i').attr('class', icon_class);
        modal.find('.modal-footer .btn-save').text(button_save_label);
        modal.find('.modal-body').html('');

        // Annotate with target (just in case)
        modal.data('target', target);

        return modal;
    }

    function openMyModal(event) {
        var modal = initModalDialog(event, '#MyModal');
        var url = $(event.target).data('action');
        var idobj = $(event.target).data('idobj');

        $.ajax({
            type: "GET",
            url: url,
            data : {
                idobj: idobj,
            }
        }).done(function(data, textStatus, jqXHR) {
            modal.find('.modal-body').html(data.html_form);
            modal.modal('show');
            formAjaxSubmit(modal, url, null, null);
        }).fail(function(jqXHR, textStatus, errorThrown) {
            alert("SERVER ERROR: " + errorThrown);
        });
    }

    /*function afterModalLoad(modal) {
        console.log('modal %o loaded', modal);
    }

    function afterModalSuccess(modal) {
        console.log('modal %o succeeded', modal);
    }*/

    function formAjaxSubmit(modal, action, cbAfterLoad, cbAfterSuccess) {
        var form = modal.find('.modal-body form');
        var header = $(modal).find('.modal-header');

        // use footer save button, if available
        var btn_save = modal.find('.modal-footer .btn-save');
        if (btn_save) {
            modal.find('.modal-body form .form-submit-row').hide();
            btn_save.off().on('click', function(event) {
                modal.find('.modal-body form').submit();
            });
        }
        if (cbAfterLoad) { cbAfterLoad(modal); }

        // Give focus to first visible form field
        modal.find('form input:visible').first().focus();

        // bind to the form’s submit event
        $(form).on('submit', function(event) {

            // prevent the form from performing its default submit action
            event.preventDefault();
            header.addClass('loading');

            var url = $(this).attr('action') || action;

            // serialize the form’s content and send via an AJAX call
            // using the form’s defined action and method
            $.ajax({
                type: $(this).attr('method'),
                url: url,
                idobj: $(this).attr('idobj'),
                data: $(this).serialize(),
                success: function(xhr, ajaxOptions, thrownError) {
                    // If the server sends back a successful response,
                    // we need to further check the HTML received

                    // update the modal body with the new form
                    $(modal).find('.modal-body').html(xhr['html_form']);

                    // If xhr contains any field errors,
                    // the form did not validate successfully,
                    // so we keep it open for further editing
                    if ($(xhr['html_form']).find('.errorlist').length > 0) {
                        formAjaxSubmit(modal, url, cbAfterLoad, cbAfterSuccess);
                    } else {
                        // otherwise, we've done and can close the modal
                        $(modal).modal('hide');
                        window.location.href = '/parametro/'

                        if (cbAfterSuccess) { cbAfterSuccess(modal); }
                    }
                },
                error: function(xhr, ajaxOptions, thrownError) {
                    console.log('SERVER ERROR: ' + thrownError);
                },
                complete: function() {
                    header.removeClass('loading');
                }
            });

        });

    }