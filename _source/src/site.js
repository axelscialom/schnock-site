// Contact and quote requests are emailed through FormSubmit (no account, no server).
// The hashed key FormSubmit gave for schnock.resto@gmail.com: it hides the address from spam bots
// and stops the repeated activation emails. Left empty, forms only show the thank-you message.
var SCHNOCK_FORM_ENDPOINT = 'https://formsubmit.co/ajax/bd66bd1e31e4cf72497d86a96694b581'

//-- Messages in the page language (the site exists in fr, en, es, it, zh, ja)
var SCHNOCK_LANG = (document.documentElement.lang || 'fr').slice(0, 2)
var SCHNOCK_TEXTS = {
	fr: { invalid: 'Votre demande n\'est pas partie : corrigez les champs signalés en rouge', sending: 'Envoi en cours…', required: 'Ce champ est obligatoire.', email: 'Veuillez saisir un email valide.', min: 'Veuillez saisir une valeur supérieure ou égale à {0}.', max: 'Veuillez saisir une valeur inférieure ou égale à {0}.', failed: "L'envoi n'a pas fonctionné. Envoyez-nous votre demande par email ou appelez-nous :" },
	en: { invalid: 'Your request was not sent: please fix the fields marked in red', sending: 'Sending…', required: 'This field is required.', email: 'Please enter a valid email address.', min: 'Please enter a value of at least {0}.', max: 'Please enter a value no greater than {0}.', failed: 'Your message could not be sent. Please email or call us:' },
	es: { invalid: 'Su solicitud no se ha enviado: corrija los campos marcados en rojo', sending: 'Enviando…', required: 'Este campo es obligatorio.', email: 'Introduzca un correo electrónico válido.', min: 'Introduzca un valor igual o superior a {0}.', max: 'Introduzca un valor igual o inferior a {0}.', failed: 'No se pudo enviar. Escríbanos o llámenos:' },
	it: { invalid: 'La richiesta non è partita: correggete i campi segnalati in rosso', sending: 'Invio in corso…', required: 'Questo campo è obbligatorio.', email: 'Inserite un indirizzo email valido.', min: 'Inserite un valore pari o superiore a {0}.', max: 'Inserite un valore pari o inferiore a {0}.', failed: "L'invio non è riuscito. Scriveteci o chiamateci:" },
	zh: { invalid: '请求未发送：请修改标红的字段', sending: '正在发送…', required: '此项为必填项。', email: '请输入有效的电子邮箱。', min: '请输入不小于 {0} 的数值。', max: '请输入不大于 {0} 的数值。', failed: '发送失败，请发邮件或致电：' },
	ja: { invalid: '送信されていません：赤で示された項目を修正してください', sending: '送信中…', required: 'この項目は必須です。', email: '有効なメールアドレスを入力してください。', min: '{0} 以上の値を入力してください。', max: '{0} 以下の値を入力してください。', failed: '送信できませんでした。メールまたはお電話でご連絡ください：' },
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

// Shown under the form when FormSubmit fails: the visitor can still send the same request by email
function schnockShowFallback(form, data) {
	var to = 'schnock.resto' + '@' + 'gmail.com'
	var lines = []
	Object.keys(data).forEach(function (k) {
		if (k.charAt(0) !== '_' && data[k]) lines.push(k + ' : ' + data[k])
	})
	var href = 'mailto:' + to + '?subject=' + encodeURIComponent(data._subject) + '&body=' + encodeURIComponent(lines.join('\n'))
	var $box = $(form).find('.schnock-fallback')
	if (!$box.length) $box = $('<div class="schnock-fallback" role="alert" style="margin:16px 0;padding:14px 16px;background:#fff;color:#1d2b3a;border-radius:6px;line-height:1.5"></div>').appendTo(form)
	$box.html('')
		.append($('<p style="margin:0 0 10px;color:#1d2b3a"></p>').text(SCHNOCK_TEXT.failed))
		.append($('<a class="btn btn--std" style="margin:0 8px 8px 0;display:inline-block"></a>').attr('href', href).text('✉ ' + to))
		.append($('<a class="btn btn--std" style="margin:0 0 8px;display:inline-block" href="tel:+33147648604"></a>').text('☎ 01 47 64 86 04'))
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
	// Show that something is happening (FormSubmit can take a few seconds) and block double clicks
	var $btn = $(form).find('[type=submit]')
	var label = $btn.val()
	if ($btn.prop('disabled')) return
	$btn.prop('disabled', true).val(SCHNOCK_TEXT.sending || '…')
	var fail = function () {
		$btn.prop('disabled', false).val(label)
		schnockShowFallback(form, data)
	}
	$.ajax({
		url: SCHNOCK_FORM_ENDPOINT,
		method: 'POST',
		data: data,
		dataType: 'json',
		timeout: 20000,
		headers: { Accept: 'application/json' },
	})
		.done(function (res) {
			// FormSubmit answers 200 even when it refuses: check the flag
			if (res && String(res.success) === 'false') return fail()
			$btn.prop('disabled', false).val(label)
			$(form).find('.schnock-fallback').remove()
			done(res)
		})
		.fail(fail)
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
