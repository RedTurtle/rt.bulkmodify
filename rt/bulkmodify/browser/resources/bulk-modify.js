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
        var emptyResults = $results.clone();

        // Temp vars
        var running = false;
        var lastSearchQuery, lastReplaceQuery, lastFlags, lastReplaceType, lastCalledView;

        var markDone = function (element, info) {
            var content_link = element.find('a[rel=external]').remove();
            element.html('<td colspan="3" class="substitutionMsg substitutionDone"><strong>' + $main.data('i18n-messages-done') + '</strong> - </td>');
            content_link.text($main.data('i18n-messages-view-content'));
            element.find('td').append(content_link);
        };
        var markError = function (element, info) {
            var content_link = element.find('a[rel=external]').remove();
            element.html('<td colspan="3" class="substitutionMsg substitutionError"><strong>' + $main.data('i18n-messages-error') + ': ' + info.message +  '</strong> - </td>');
            content_link.text($main.data('i18n-messages-view-content'));
            element.find('td').append(content_link);
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
                            for (var j=0; j<data.length; j++) {
                                var serverMessage = data[j];
                                if (serverMessage.status && serverMessage.status==='OK') {
                                    markDone($(sameContentCheckBox[j]).closest('tr'), serverMessage);
                                } else {
                                    markError($(sameContentCheckBox[j]).closest('tr'), serverMessage);
                                }                                
                            }

                            submittedCount++;
                            if (submittedCount<allCheckbox.length) {
                                callServerSideChange();
                            }
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                            sameContentCheckBox.each(function() {
                                markError($(this).closest('tr'), textStatus);
                            });
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
            var data = results.results

            if (results.total_documents_count) {
                $('.totalDocuments').text(' / ' + results.total_documents_count);
            }
            $('.currentDocument').text(b_start);

            for (var i=0;i<data.length;i++) {
                var element = data[i];

                if (lastElement===element.id) {
                    lastId = lastId+1;
                } else {
                    lastElement = element.id;
                    lastId = 0;
                }
                var newRes = $modelDataRow.clone();
                if (i % 2 === 0) {
                    newRes.addClass('even');
                } else {
                    newRes.addClass('odd');
                }
                if ($replaceQuery.val() || $replaceTypes.filter(':checked').val()) {
                    // match id for server side changes (is uid-xxx)
                    $(':checkbox', newRes).attr('value', element.id+'-'+lastId).attr("data-uid", element.uid).attr("id", element.uid);
                } else {
                    $(':checkbox', newRes).remove();
                }
                // document title and URL
                var $label = $('<label>' + element.title + '</label>');
                $('.matchDocument', newRes).append($label);
                newRes.find('label').attr('for', element.uid);
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
                    $('.matchText', newRes).html('<div class="pre"></div><div class="post"></div>');
                    $('.matchText .pre', newRes).text(element.old);
                    $('.matchText .post', newRes).text(element['new']);
                } else {
                    $('.matchText', newRes).html(element.text);
                }
                $('table', $results).append(newRes);
            }
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
                                view: '/@@batchSearch'}, params);
            b_start = params.b_start;
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
                            batchSearch({b_start: b_start+b_size, view: params.view});
                        }
                    }
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    $('#loading').remove();
                    $("#results").find('table').append('<tr id="serverError"><td colspan="3">' + $main.data('i18n-message-server-error') +  '</td></tr>');
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
            var params = {b_start: b_start, view: lastCalledView};
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
