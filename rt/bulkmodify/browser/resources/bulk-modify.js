/**
 * Bulk Modify - JavaScript Code
 */

(function($){
    $(document).ready(function() {

		var $main = $('#bulkModify');
		if ($main.length==0) {
			// quick way to exit: do not try to do nothing if we are not in the right template
			return;
		}

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
		var commandModifySelected = $($('#modelModifySelectedButton').text());
		commandModifySelected.attr('value', $main.data('i18n-modify-selected'));

		// Models
		var $modelDataRow = $($('#modelDataRow').text());
		var $modelDataRowNoResults = $($('#modelDataRowNoResults').text());
		$modelDataRowNoResults.find('td').text($main.data('i18n-no-results-found'));
		
		var flags = 0;
		var b_size = 20;
		var emptyResults = $results.clone();
		
		// Temp vars
		var running = false;
		var lastSearchQuery, lastReplaceQuery, lastFlags, lastReplaceType;

		var markDone = function(element, info) {
			element.html('<td colspan="3" class="substitutionMsg substitutionDone"><strong>' + $main.data('i18n-messages-done') + '!</strong></td>');
		}
		var markError = function(element, info) {
			element.html('<td colspan="3" class="substitutionMsg substitutionError"><strong>' + $main.data('i18n-messages-error') + ': ' + info.message +  '</strong></td>');
		}

		var checkNoResultsFound = function() {
			if ($("#results").find('td').length===0) {
				$("#results").find('table').append($modelDataRowNoResults.clone());
			}
		}

		var submitSelected = function(event) {
			event.preventDefault();
			var allCheckbox = $('.selectCommand:checked');
			var submittedCount = 0;

			if (allCheckbox.length>0) {
				var callServerSideChange = function() {
					var ids = [];
					var checkbox = $(allCheckbox.get(submittedCount));
					var sameContentCheckBox = $('.selectCommand:checked[data-uid=' + checkbox.data('uid') + ']');

					// now grouping changes to the same content in the same request
					if (sameContentCheckBox.length>1) {
						sameContentCheckBox.each(function () {
							ids.push($(this).val());
						});
						// skipping other check for the same content
						submittedCount = submittedCount+sameContentCheckBox.length-1;
					} else {
						ids = [checkbox.val()];
					}
					
		            $.ajax({
						dataType: "json",
						type: 'POST',
						url: portal_url + '/@@replaceText',
						traditional: true,
						data: {'id:list': ids, searchQuery: lastSearchQuery, replaceQuery: lastReplaceQuery, 'flags:int': lastFlags, replace_type: lastReplaceType},
						success: function(data) {
							
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
						error: function(jqXHR, textStatus, errorThrown) {
							sameContentCheckBox.each(function() {
								markError($(this).closest('tr'), textStatus)
							});
							submittedCount++;
							if (submittedCount<allCheckbox.length) {
								callServerSideChange();
							}
						}
					});				
				}
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

		var showResults = function(data) {
			var lastId = 0;
			var lastElement = null;

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
					newRes.addClass('even')
				} else {
					newRes.addClass('odd')
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
					$label.before('<img alt="" src="' + portal_url + '/' + element.icon + '" />&nbsp;')
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
		}

		var batchSearch = function (params) {
			params = $.extend( {b_start: 0,
								view: '/@@batchSearch'}, params);
	
			formData = $form.serializeArray();
			formData.push({
				name: 'b_start:int',
				value: params.b_start
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
				success: function(data) {
					if (data===null) {
						// we have finished
						$('#loading').remove();
						commandPauseButton.hide();
						commandSearchButton.show();
						checkNoResultsFound();
					} else {
						showResults(data);
						$results.show();
						if (running) {
							batchSearch({b_start: params.b_start+b_size, view: params.view})
						}
					}
				}
			});
        }

        commandSearchButton.click(function(event) {
            event.preventDefault();
            var counter = 0;
			var formData = null;
			var params = {};

            if ($searchQuery.val()) {
				commandPauseButton.show();
				commandSearchButton.hide();
				running = true;

				lastSearchQuery = $searchQuery.val();
				lastReplaceType = $replaceTypes.filter(':checked').val();
				$results.html(emptyResults.html());
				$results.prepend('<div id="loading"><img alt="Loading..." title="Loading..." src="' + portal_url + '/++resource++rt.bulkmodify.resources/ajax-load.gif" /></div>');

				// loading flags
				flags = 0;
				$.each($('.flag :checkbox:checked'), function() {
					flags = flags | $(this).val();
					lastFlags = flags;
				});

				if ($replaceQuery.val() || lastReplaceType) {
					$('#cellCommands').append(selectAllCommand.clone(true));
					params.view = '/@@batchReplace';
					$results.find('table').before(commandModifySelected);
					$('#modifySelected').click(submitSelected);
				} else {
					$('#cellCommands').empty();
				}
				batchSearch(params);
			}
        });

        commandPauseButton.click(function(event) {
			event.preventDefault();
			running = false;
			checkNoResultsFound();
			commandPauseButton.hide();
			commandSearchButton.show();
			$('#loading').remove();
		});

    });
})(jQuery)
