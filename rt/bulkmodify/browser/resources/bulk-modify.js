/**
 * Bulk Modify - JavaScript Code
 */

(function($){
    $(document).ready(function() {

        var $searchQuery = $('#searchQuery');
		var $form = $('#bulkSearchForm');
		var $results = $('#results');
		var $model = $($('#model').text());
		var flags = 0;
		var b_size = 20;
		var emptyResults = $results.clone();

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
				// match id for server side changes (is uid-xxx)
				$(':checkbox', newRes).attr('value', element.id+'-'+lastId);
				// document title and URL
				$('.matchDocument', newRes).html('<strong>' + element.title + '</strong><br />');
				$('.matchDocument', newRes).append($('<a href="' + element.url + '" rel="external">' + element.url + '</a>'));
				// text!
				$('.matchText', newRes).html(element.text);
				$('table', $results).append(newRes);
			}
		}

		var batchSearch = function (params) {
			params = $.extend( {b_start: 0}, params);
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
				url: portal_url + '/@@batchSearch',
				data: formData,
				success: function(data) {
					if (data===null) {
						// we have finished
						$('#loading').remove();
					} else {
						showResults(data);
						$results.show();
						batchSearch({b_start: params.b_start+b_size})
					}
				}
			});
        }

        $('#searchButton').click(function(event) {
            var counter = 0;
			var formData = null;
            event.preventDefault();
            if ($searchQuery.val()) {
				$results.html(emptyResults.html());
				$results.append('<img id="loading" alt="Loading..." title="Loading..." src="' + portal_url + '/++resource++rt.bulkmodify.resources/ajax-load.gif" />');
				// loading flags
				flags = 0;
				$.each($('.flag :checkbox:checked'), function() {
					flags = flags | $(this).val();
				});
				batchSearch();
			}

        });

    });
})(jQuery)
