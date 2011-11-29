$(document).ready(function(){  
/*
 * 		Contact Form Validation
 */

	$('#contactform').submit(function() {
	
		// Disable the submit button
		$('#contactform input[type=submit]')
			.attr('value', 'Sending message')
			.attr('disabled', 'disabled');
	
		// AJAX POST request
		$.post(
			$(this).attr('action'),
			{
				name:$('#name').val(),
				email:$('#email').val(),
				message:$('#message').val()
			},
			function(errors) {
				// No errors
				if (errors == null) {
					$('#contactform')
						.hide()
						.html('<h3>Thank you</h3><p>Your message has been sent.</p>')
						.show();
				}
	
				// Errors
				else {
					// Re-enable the submit button
					$('#contactform input[type=submit]')
						.removeAttr('disabled')
						.attr('value', 'Send your Question');
	
					// Technical server problem, the email could not be sent
					if (errors.server != null) {
						alert(errors.server);
						return false;
					}
	
					// Empty the errorbox and reset the error alerts
					$('#contactform .errorbox').html('<ul></ul>').show();
					$('#contactform li').removeClass('alert');
	
					// Loop over the errors, mark the corresponding input fields,
					// and add the error messages to the errorbox.
					for (field in errors) {
						if (errors[field] != null) {
							$('#' + field).parent('li').addClass('alert');
							$('#contactform .errorbox ul').append('<li>' + errors[field] + '</li>');
						}
					}
				}
			},
			'json'
		);
	
		// Prevent non-AJAX form submission
		return false;
	});

});