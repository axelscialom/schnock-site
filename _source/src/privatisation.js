//-- Quote request form (same behaviour as the contact form)
if ($('#devis-form').length > 0) {
	$('#devis-form').validate({
		errorPlacement: function (error, element) {
			error.insertAfter(element)
		},
		submitHandler: function (form) {
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
