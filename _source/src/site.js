// Contact and quote requests are emailed through FormSubmit (no account, no server).
// Set the address that should receive them; left empty, forms only show the thank-you message.
var SCHNOCK_FORM_ENDPOINT = 'https://formsubmit.co/ajax/schnock.resto@gmail.com'

//-- Messages in the page language (the site exists in fr, en, es, it, zh, ja)
var SCHNOCK_LANG = (document.documentElement.lang || 'fr').slice(0, 2)
var SCHNOCK_TEXTS = {
	fr: { required: 'Ce champ est obligatoire.', email: 'Veuillez saisir un email valide.', min: 'Veuillez saisir une valeur supérieure ou égale à {0}.', max: 'Veuillez saisir une valeur inférieure ou égale à {0}.', failed: "L'envoi n'a pas fonctionné. Appelez-nous au 01 47 64 86 04." },
	en: { required: 'This field is required.', email: 'Please enter a valid email address.', min: 'Please enter a value of at least {0}.', max: 'Please enter a value no greater than {0}.', failed: 'Your message could not be sent. Please call us on +33 1 47 64 86 04.' },
	es: { required: 'Este campo es obligatorio.', email: 'Introduzca un correo electrónico válido.', min: 'Introduzca un valor igual o superior a {0}.', max: 'Introduzca un valor igual o inferior a {0}.', failed: 'No se pudo enviar. Llámenos al +33 1 47 64 86 04.' },
	it: { required: 'Questo campo è obbligatorio.', email: 'Inserite un indirizzo email valido.', min: 'Inserite un valore pari o superiore a {0}.', max: 'Inserite un valore pari o inferiore a {0}.', failed: "L'invio non è riuscito. Chiamateci al +33 1 47 64 86 04." },
	zh: { required: '此项为必填项。', email: '请输入有效的电子邮箱。', min: '请输入不小于 {0} 的数值。', max: '请输入不大于 {0} 的数值。', failed: '发送失败，请致电 +33 1 47 64 86 04。' },
	ja: { required: 'この項目は必須です。', email: '有効なメールアドレスを入力してください。', min: '{0} 以上の値を入力してください。', max: '{0} 以下の値を入力してください。', failed: '送信できませんでした。お電話（+33 1 47 64 86 04）でご連絡ください。' },
}
var SCHNOCK_TEXT = SCHNOCK_TEXTS[SCHNOCK_LANG] || SCHNOCK_TEXTS.fr
if (window.jQuery && $.validator) {
	$.extend($.validator.messages, {
		required: SCHNOCK_TEXT.required,
		email: SCHNOCK_TEXT.email,
		min: $.validator.format(SCHNOCK_TEXT.min),
		max: $.validator.format(SCHNOCK_TEXT.max),
	})
}

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
			alert(SCHNOCK_TEXT.failed)
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

//-- Fish & Chips video: loads and plays (muted, looped) only once it is on screen
document.querySelectorAll('video[data-src]').forEach(function (video) {
	function start() {
		if (!video.src) video.src = video.getAttribute('data-src')
		var p = video.play()
		if (p && p.catch) p.catch(function () {})
	}
	if (!('IntersectionObserver' in window)) return start()
	new IntersectionObserver(function (entries) {
		entries.forEach(function (e) {
			if (e.isIntersecting) start()
			else if (video.src) video.pause()
		})
	}).observe(video)
})
