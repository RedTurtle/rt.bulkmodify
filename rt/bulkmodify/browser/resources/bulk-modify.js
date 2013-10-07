/*jshint forin:true, noarg:true, noempty:true, eqeqeq:true, strict:true, undef:true, unused:true, curly:true, browser:true, jquery:true, indent:4, maxerr:50*/

/**
 * Bulk Modify - JavaScript Code
 */

(function ($) {
    $(document).ready(function () {

        var $main = $('#bulkModify');
        // quick way to exit: do not try to do nothing if we are not in the right template
        if ($main.length === 0) {
            return;
        }

        $('a[rel=external]').live('click', function (event) {
            event.preventDefault();
            window.open($(this).attr('href'));
        });

		// Select all types command
		$('#selectAllTypes').click(function(event) {
            if ($(this).is(':checked')) {
                $('.typeCheck > :checkbox').attr('checked', 'checked');
            } else {
                $('.typeCheck > :checkbox').removeAttr('checked');
            }
        });

        // Areas
        var $form = $('#bulkSearchForm');
        var $results = $('#results');

        // Data
        var $searchQuery = $('#searchQuery');
        var $replaceQuery = $('#replaceQuery');
        var $replaceTypes = $(':input[name=replace_type]');

        // Buttons
        var commandSearchButton = $('#searchButton');
        var commandPauseButton = $('#pauseButton');
        var commandContinueButton = $('#continueButton');
        var commandModifySelected = $($('#modelModifySelectedButton').text() || $('#modelModifySelectedButton').html());
        commandModifySelected.attr('value', $main.data('i18n-modify-selected'));
        var $changeCommands = $('#changeCommands').remove();

        // Models
        var $modelDataRow = $($('#modelDataRow').text() || $('#modelDataRow').html());
        var $modelDataRowNoResults = $($('#modelDataRowNoResults').text() || $('#modelDataRowNoResults').html());
        $modelDataRowNoResults.find('td').text($main.data('i18n-no-results-found'));
        var modelLoading = $('<tr id="loading"><td colspan="3"><img alt="Loading..." title="Loading..." src="' + portal_url + '/++resource++rt.bulkmodify.resources/ajax-load.gif" /><span class="counter currentDocument"></span><span class="counter totalDocuments"></span></td></tr>');

        var flags = 0;
        var b_size = 20;
        var b_start = 0;
        var really_checked_docs = 0;
        var emptyResults = $results.clone();

        // Temp vars
        var running = false;
        var lastSearchQuery, lastReplaceQuery, lastFlags, lastReplaceType, lastCalledView;

        var markMessage = function (element, info, msgType) {
            var content_link = element.find('a[rel=external]').remove();
            var link_text = element.find('label').text();
            element.html('<td colspan="3" class="substitutionMsg ' + (msgType==='ok'?'substitutionDone':'substitutionError') +  '"><strong>' + (msgType==='ok'?$main.data('i18n-messages-done'):$main.data('i18n-messages-error')) + '</strong> - </td>');
            content_link.text($main.data('i18n-messages-view-content'));
            element.find('td').append(content_link).append('<div class="discreet">' + link_text + '</div>');
            return element.find('td')[0];
        };

        var checkNoResultsFound = function () {
            if ($("#results").find('td').length === 0) {
                $("#results").find('table').append($modelDataRowNoResults.clone());
            }
        };

        var submitSelected = function (event) {
            event.preventDefault();
            var allCheckbox = $('.selectCommand:checked:not(:disabled)');
            var submittedCount = 0;
            var update_time = $('#update_time').is(':checked') ? 'True' : 'False';
            var new_version = $('#new_version').is(':checked') ? 'True' : 'False';

            if (allCheckbox.length > 0) {
                var callServerSideChange = function () {
                    var ids = [];
                    var checkbox = $(allCheckbox.get(submittedCount));
                    var allSameContentCheckBox = $('.selectCommand[data-uid=' + checkbox.data('uid') + ']');
                    var sameContentCheckBox = $('.selectCommand:checked[data-uid=' + checkbox.data('uid') + ']');
                    sameContentCheckBox.attr('disabled', 'disabled');
                    sameContentCheckBox.after($(' <img alt="" src="' + portal_url + '/++resource++rt.bulkmodify.resources/ajax-loader-mini.gif" />'));

                    // now grouping changes to the same content in the same request
                    if (sameContentCheckBox.length > 1) {
                        sameContentCheckBox.each(function () {
                            ids.push($(this).val());
                        });
                        // skipping other check for the same content
                        submittedCount = submittedCount + sameContentCheckBox.length - 1;
                    } else {
                        ids = [checkbox.val()];
                    }

                    $.ajax({
                        dataType: "json",
                        type: 'POST',
                        url: portal_url + '/@@replaceText',
                        traditional: true,
                        data: {'id:list': ids, searchQuery: lastSearchQuery, replaceQuery: lastReplaceQuery, 'flags:int': lastFlags, replace_type: lastReplaceType, 'update_time:boolean': update_time, 'new_version:boolean': new_version},
                        success: function (data) {
                            var done_elems = [], err_elems = [];
                            for (var j=0; j<data.length; j++) {
                                var serverMessage = data[j];
                                if (serverMessage.status && serverMessage.status==='OK') {
                                    done_elems.push(markMessage($(sameContentCheckBox.get(j)).closest('tr'), serverMessage, 'ok'));
                                } else {
                                    err_elems.push(markMessage($(sameContentCheckBox.get(j)).closest('tr'), serverMessage, 'ko'));
                                }                                
                            }
                            // need to fix id for remaining checkboxes of the same type
                            allSameContentCheckBox.filter(':visible').each(function() {
                                var ndiff = $(this).closest('tr').prevAll('tr').find('.substitutionMsg').length;
                                var cb_id = parseInt($(this).val().split('-')[$(this).val().split('-').length-1], 10);
                                $(this).val($(this).val().replace(RegExp("-" + cb_id + "$"), '-' + (cb_id-ndiff)));
                            });
                            
                            // let's display only one messages per type
                            $(done_elems).filter(':not(:first)').remove();
                            $(err_elems).filter(':not(:first)').remove();

                            submittedCount++;
                            if (submittedCount<allCheckbox.length) {
                                callServerSideChange();
                            }
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                            var err_elems = [];
                            sameContentCheckBox.each(function() {
                                err_elems.push(markMessage($(this).closest('tr'), textStatus, 'ko'));
                            });
                            $(err_elems).filter('not:first').remove();
                            submittedCount++;
                            if (submittedCount<allCheckbox.length) {
                                callServerSideChange();
                            }
                        }
                    });                
                };
                callServerSideChange();
            }
        };

        // select/unselect all
        var selectAllCommand = $('<input type="checkbox" id="bulkmodifySelectAll">/');
        selectAllCommand.click(function(event) {
            if ($(this).is(':checked')) {
                $('.selectCommand', $results).attr('checked', 'checked');
            } else {
                $('.selectCommand', $results).removeAttr('checked');
            }
        });

        var showResults = function(results) {
            var lastId = 0;
            var lastElement = null;
            var data = results.results;

            if (results.total_documents_count) {
                really_checked_docs = results.really_checked_docs;
                $('.totalDocuments').text(' / ' + results.total_documents_count
                        + ' (' + really_checked_docs +' '
                        + $main.data('i18n-checked-docs') + ')');
            }
            $('.currentDocument').text(b_start);

            for (var i=0;i<data.length;i++) {
                var element = data[i];
                var isNewDoc = false;
                var allOfTheDocsSelection = null;

                if (lastElement===element.id) {
                    // same document as before
                    lastId = lastId+1;
                } else {
                    // this is a new document
                    lastElement = element.id;
                    lastId = 0;
                    // remove the all-of-the-document checkbox in the row above
                    // AKA: there's only one match so two checkboxes can confuse
                    $('table tr:last', $results).find('.allOfTheDoc').remove();
                    // check fox selecting all changes in the document
                    allOfTheDocsSelection = $('<input class="allOfTheDoc" type="checkbox" name="" value="" />');
                    allOfTheDocsSelection.click(function(event) {
                        if ($(this).is(':checked')) {
                            $('input[data-uid='+ $(this).prev(':checkbox').attr('data-uid') +']').attr('checked', 'checked');
                        } else {
                            $('input[data-uid='+ $(this).prev(':checkbox').attr('data-uid') +']').removeAttr('checked');
                        }
                    }).mouseenter(function() {
                        $('input[data-uid='+ $(this).prev(':checkbox').attr('data-uid') +']').closest('tr').addClass('allDocFocus');
                    }).mouseleave(function() {
                        $('input[data-uid='+ $(this).prev(':checkbox').attr('data-uid') +']').closest('tr').removeClass('allDocFocus');
                    });
                }
                var newRes = $modelDataRow.clone();
                
                if (allOfTheDocsSelection) {
                    newRes.find(':checkbox').after(allOfTheDocsSelection);
                }

                if (i % 2 === 0) {
                    newRes.addClass('even');
                } else {
                    newRes.addClass('odd');
                }
                if ($replaceQuery.val() || $replaceTypes.filter(':checked').val()) {
                    // match id for server side changes (is uid-xxx)
                    $(':checkbox', newRes).attr('value', element.id+'-'+lastId).attr("data-uid", element.uid).attr('id', element.id+'-'+lastId);
                } else {
                    $(':checkbox', newRes).remove();
                }
                // document title and URL
                var $label = $('<label>' + element.title + '</label>');
                $('.matchDocument', newRes).append($label);
                newRes.find('label').attr('for', element.id+'-'+lastId);
                // icon
                if (element.icon) {
                    $label.before('<img alt="" src="' + portal_url + '/' + element.icon + '" />&nbsp;');
                } else {
                    $label.addClass('contenttype-' + element.normalized_portal_type);
                }
                $label.after($('<br />'));
                $('.matchDocument', newRes).append($('<a href="' + element.url + '" rel="external">' + element.url + '</a>'));
                // text!
                if (element['new']) {
                    $('.matchText', newRes).html('<div class="preChange"><span class="pre"></span><span class="content"></span><span class="post"></span></div>\n'
							+'<div class="postChange"><span class="pre"></span><span class="content"></span><span class="post"></span></div>');
                    $('.matchText .preChange .content', newRes).text(element.old);
					$('.matchText .preChange .pre', newRes).html(element.pre_text);
					$('.matchText .preChange .post', newRes).html(element.post_text);
                    $('.matchText .postChange .content', newRes).text(element['new']);
					$('.matchText .postChange .pre', newRes).html(element.pre_text);
					$('.matchText .postChange .post', newRes).html(element.post_text);
                } else {
                    $('.matchText', newRes).html(element.text);
                }
                $('table', $results).append(newRes);
            }
            // a single-match document can be the last
            $('table tr:last', $results).find('.allOfTheDoc').remove();
        };

        /**
         * Running UI elements
         * @param {Boolean} newSearch true for performing a new search from scratch
         */
        var setRunningState = function(newSearch) {
            if (newSearch) {
                $results.html(emptyResults.html());
                $results.find('table').append(modelLoading.clone());
            } else {
                $('#loading td').prepend(modelLoading.find('img').clone());
            }
        };

        var batchSearch = function (params) {
            params = $.extend( {b_start: 0,
                                really_checked_docs: 0,
                                view: '/@@batchSearch'}, params);
            b_start = params.b_start;
            really_checked_docs = params.really_checked_docs;
            lastCalledView = params.view;
            var formData = $form.serializeArray();

            formData.push({
                name: 'b_start:int',
                value: b_start
            });
            formData.push({
                name: 'b_size:int',
                value: b_size
            });
            formData.push({
                name: 'really_checked_docs:int',
                value: really_checked_docs
            });
            formData.push({
                name: 'flags:int',
                value: flags || 0
            });
            $.ajax({
                dataType: "json",
                type: 'POST',
                url: portal_url + params.view,
                data: formData,
                success: function(results) {
                    var data = results.results;
                    if (data===null) {
                        // we have finished
                        running = false;
                        $('#loading').remove();
                        commandPauseButton.hide();
                        commandSearchButton.show();
                        checkNoResultsFound();
                    } else {
                        showResults(results);
                        if (running) {
                            batchSearch({b_start: b_start+b_size,
                                         really_checked_docs: really_checked_docs,
                                         view: params.view});
                        }
                    }
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    $('#loading').remove();
                    $("#results").find('table').append('<tr id="serverError"><td colspan="3">' + $main.data('i18n-messages-server-error') +  '</td></tr>');
                    commandPauseButton.trigger('click');
                }
            });
        };

        commandSearchButton.click(function(event) {
            event.preventDefault();
            var params = {};

            if ($searchQuery.val() && !running) {
                commandPauseButton.show();
                commandContinueButton.hide();
                commandSearchButton.hide();
                running = true;

                lastSearchQuery = $searchQuery.val();
                lastReplaceQuery = $replaceQuery.val();
                lastReplaceType = $replaceTypes.filter(':checked').val();
                $results.show();
                setRunningState(true);

                // loading flags
                flags = 0;
                $.each($('.flag :checkbox:checked'), function() {
                    flags = flags | $(this).val();
                    lastFlags = flags;
                });

                if ($replaceQuery.val() || lastReplaceType) {
                    $('#cellCommands').append(selectAllCommand.clone(true));
                    params.view = '/@@batchReplace';
                    $results.find('table').before($changeCommands);
                    $changeCommands.append(commandModifySelected);
                    $('#modifySelected').click(submitSelected);
                } else {
                    $('#cellCommands').empty();
                    $('#changeCommands').hide();
                }
                batchSearch(params);
            }
        });

        commandPauseButton.click(function(event) {
            event.preventDefault();
            if (running) {
                commandContinueButton.show();
                running = false;
                checkNoResultsFound();
                commandPauseButton.hide();
                commandContinueButton.show();
                commandSearchButton.show();
                $('#loading img').remove();
            }
        });

        commandContinueButton.click(function(event) {
            event.preventDefault();
            var params = {b_start: b_start,
                          really_checked_docs: really_checked_docs,
                          view: lastCalledView};
            if (!running) {
                running = true;
                setRunningState(false);
                batchSearch(params);
                commandContinueButton.hide();
                commandPauseButton.show();
                commandSearchButton.show();
            }
        });

    });
})(jQuery);
