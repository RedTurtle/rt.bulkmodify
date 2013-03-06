/**
 * Bulk Modify - JavaScript Code
 */

(function($){
    $(document).ready(function() {

        var $searchQuery = $('#searchQuery');
		var $replaceQuery = $('#replaceQuery');
		var $form = $('#bulkSearchForm');
		var $results = $('#results');
		var $model = $($('#model').text());
		var flags = 0;
		var b_size = 20;
		var emptyResults = $results.clone();
		var running = false;

		var showResults = function(data) {
			var lastId = 0;
			var lastElement = null;
			for (var i=0;i<data.length;i++) {
				var element = data[i];
				if (lastElement===element.id) {
					lastId = lastId+1;
				}
				lastElement = element.id;
				var newRes = $model.clone();
				if (i % 2 === 0) {
					newRes.addClass('even')
				} else {
					newRes.addClass('odd')
				}
				if ($replaceQuery.val()) {
					// match id for server side changes (is uid-xxx)
					$(':checkbox', newRes).attr('value', element.id+'-'+lastId);
				} else {
					$(':checkbox', newRes).remove();
				}
				// document title and URL
				$('.matchDocument', newRes).html('<strong>' + element.title + '</strong><br />');
				$('.matchDocument', newRes).append($('<a href="' + element.url + '" rel="external">' + element.url + '</a>'));
				// text!
				if (element.diff) {
					$('.matchText', newRes).html('<div class="pre"></div> <div class="post"></div>');
					$('.matchText .pre', newRes).text(element.diff[lastId*2]);
					$('.matchText .post', newRes).text(element.diff[lastId*2+1]);
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

        $('#searchButton').click(function(event) {
            event.preventDefault();
            var counter = 0;
			var formData = null;
			var params = {};
			$('#pauseButton').show();
			$('#searchButton').hide();
			running = true;
            if ($searchQuery.val()) {
				$results.html(emptyResults.html());
				$results.prepend('<div id="loading"><img alt="Loading..." title="Loading..." src="' + portal_url + '/++resource++rt.bulkmodify.resources/ajax-load.gif" /></div>');
				// loading flags
				flags = 0;
				$.each($('.flag :checkbox:checked'), function() {
					flags = flags | $(this).val();
				});
				
				if ($replaceQuery.val()) {
					
					params.view = '/@@batchReplace';
				}
				batchSearch(params);
			}
        });

        $('#pauseButton').click(function(event) {
			event.preventDefault();
			running = false;
			$('#pauseButton').hide();
			$('#searchButton').show();
			$('#loading').remove();
		});

    });
})(jQuery)
