// Contact and quote requests are emailed through FormSubmit (no account, no server).
// Set the address that should receive them; left empty, forms only show the thank-you message.
var SCHNOCK_FORM_ENDPOINT = 'https://formsubmit.co/ajax/schnock.resto@gmail.com'

function schnockSendForm(form, subject, done) {
	var data = {}
	$(form).serializeArray().forEach(function (field) {
		data[field.name] = field.value
	})
	data._subject = subject + ' - ' + (data.firstname || '') + ' ' + (data.lastname || '')
	data._template = 'table'
	data._captcha = 'false'
	if (!SCHNOCK_FORM_ENDPOINT) {
		done()
		return
	}
	$.ajax({
		url: SCHNOCK_FORM_ENDPOINT,
		method: 'POST',
		data: data,
		dataType: 'json',
		headers: { Accept: 'application/json' },
	})
		.done(done)
		.fail(function () {
			alert("L'envoi n'a pas fonctionné. Appelez-nous au 01 47 64 86 04.")
		})
}

//-- Slow zoom on the hero photo (the photo moves to its own layer so only it scales)
document.querySelectorAll('.hero-picture').forEach(function (hero) {
	var bg = hero.style.backgroundImage
	if (!bg) return
	var layer = document.createElement('div')
	layer.className = 'hero-picture__zoom'
	layer.style.backgroundImage = bg
	hero.style.backgroundImage = 'none'
	hero.insertBefore(layer, hero.firstChild)
})
