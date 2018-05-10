function createFileLink(data) {
	return $('\
	<div class="col-md-4">\
		<div class="alert">\
			<a href="' + data.link + '">' + data.filename + '</a>\
		</div>\
	</div>\
	')
}

function createErrorMessage(message) {
	return $('\
	<div class="col-md-4 m-5">\
		<div class="alert alert-danger">\
			<button type="button" class="close" data-dismiss="alert" aria-label="Close">\
				<span aria-hidden="true">&times;</span>\
			</button>\
			' + message + '\
		</div>\
	</div>\
	')
}

function ajax_submit_form(event) {
	event.preventDefault();
	var wait_block = $('.js-wait-block').fadeIn();

	var $input = $('[name="file"]', this);
	var fd = new FormData;
	fd.append('file', $input.prop('files')[0]);

	$.ajax({
		url: this.action || window.location.pathname,
		method: this.method || 'POST',
		data: fd,
		processData: false,
		contentType: false,
		success: function(response_data) {
			$('.js-file-links-block').html(createFileLink(response_data)).fadeIn();
		},
		error: function(response) {
			console.log(response);
			var message = response.status != 0 ? response.responseText : "Нет связи с сервером.";
			$('.js-alert-block').html(createErrorMessage(message)).fadeIn();
		}
	}).always(function() {
		wait_block.fadeOut();
	});
}

window.addEventListener('load', function() {
	$('form').submit(ajax_submit_form);
	$('[name="file"]').change(function() {
		$('form').submit();
	});
})