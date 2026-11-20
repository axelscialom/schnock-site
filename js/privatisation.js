//-- Quote request form (same behaviour as the contact form)
if ($('#devis-form').length > 0) {
	// No upper limit on guests: a big group must never be blocked (the team answers case by case)
	$('#devis-form [name=guests]').removeAttr('max')
	$('#devis-form').validate({
		errorPlacement: function (error, element) {
			error.insertAfter(element)
		},
		// Tell the visitor next to the button why nothing was sent (errors can be above, off screen)
		invalidHandler: function (event, validator) {
			var $form = $(this)
			var $note = $form.find('.schnock-invalid')
			if (!$note.length) $note = $('<p class="schnock-invalid" role="alert" style="margin:12px 0;padding:10px 14px;background:#fff;color:#a8483b;border-radius:6px;font-weight:600"></p>').insertAfter($form.find('[type=submit]').last())
			$note.text(SCHNOCK_TEXT.invalid + ' (' + validator.numberOfInvalids() + ')')
		},
		submitHandler: function (form) {
			$(form).find('.schnock-invalid').remove()
			schnockSendForm(form, 'Demande de privatisation', function () {
				$(form).find('.input--small, .input--full, #send-devis').hide()
				$(form).find('.step2').removeClass('hidden')
				// Conversion for Google Ads / Analytics (through Tag Manager)
				window.dataLayer = window.dataLayer || []
				window.dataLayer.push({ event: 'generate_lead', form: 'privatisation' })
				$(window).trigger('devis-form-sent')
			})
			return false
		},
	})
}

//-- Group menus as tabs: one menu visible at a time (all stay in the page for search engines)
var $groupMenus = $('.s--privatisation-menus .s--menus')
var showGroupMenu = function (id) {
	$groupMenus.hide().filter(function () {
		return $(this).find('#' + id).length > 0
	}).show()
	$('.s--privatisation-menus .menu-nav__item').removeClass('active').filter('[data-anchor="' + id + '"]').addClass('active')
}
if ($groupMenus.length > 0) {
	showGroupMenu($groupMenus.first().find('.menu-wrap').attr('id'))
	$('a[href^="#menu-"]').on('click', function () {
		showGroupMenu(this.getAttribute('href').slice(1))
	})
}
