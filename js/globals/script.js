//-------------------------------------
//	FUNCTIONS
//-------------------------------------
//-- Calculate Navigation Width
const calculate_nav_width = () => {
	// Ensure DOM elements exist before calculating
	if (!d.q('.homelink') || !d.q('nav')) {
		// Elements not ready yet
		return
	}
	
	// Update homelink width
	const homelinkEl = d.q('.homelink')
	
	// Check if homelink is properly styled (should not be block-level spanning full width)
	const homelinkDisplay = window.getComputedStyle(homelinkEl).display
	const homelinkFloat = window.getComputedStyle(homelinkEl).float
	const homelinkPosition = window.getComputedStyle(homelinkEl).position
	
	// If homelink is display:block and not floated/positioned, it's not ready yet
	if (homelinkDisplay === 'block' && homelinkFloat === 'none' && homelinkPosition === 'static') {
		nav_width = 0
		return
	}
	
	homelink_width = homelinkEl.scrollWidth
	
	// Additional safety check - if homelink is taking full window width, something's wrong
	if (homelink_width >= window.innerWidth - 10) {
		nav_width = 0
		return
	}
	
	if (nav_horizontal_right_left) {
		let nav_padding_side =
			parseInt(getComputedStyle(d.q('nav')).paddingLeft) + parseInt(getComputedStyle(d.q('nav')).paddingRight)

		let btn_margin = 0
		let btn_border = 0
		let number_of_btns = 0
		nav_btns_width = 0
		
		if (d.q('nav .buttons-wrap-header .btn')) {
			number_of_btns = d.qAll('nav .buttons-wrap-header .btn').length
			btn_margin = parseInt(getComputedStyle(d.q('nav .buttons-wrap-header .btn')).marginRight) || 0
			btn_border = parseInt(window.getComputedStyle(d.q('nav .buttons-wrap-header .btn'), null).borderLeftWidth) * 2 || 0
			for (let n = 0; n < number_of_btns; n++) {
				nav_btns_width = nav_btns_width + d.qAll('nav .buttons-wrap-header .btn')[n].scrollWidth
			}
		}

		nav_btns_width = nav_btns_width + btn_border * 2 * number_of_btns + btn_margin * number_of_btns
		nav_dropdown_lang_width = 0
		
		if (template != 15 && d.q('.drodown-wrap--lang')) {
			nav_dropdown_lang_width = d.q('.drodown-wrap--lang').scrollWidth || 0
		}

		let nav_items_width = 0
		if (document.getElementsByClassName('nav__items')[0]) {
			let navElement = document.getElementsByClassName('nav__items')[0]
			nav_items_width = navElement.scrollWidth || 0
		}

		nav_width =
			homelink_width +
			nav_items_width +
			nav_btns_width +
			nav_dropdown_lang_width +
			nav_padding_side +
			20
	}
}

//-- Adjust navigation widths when content overflows
const adjust_nav_widths = () => {
	let window_width = window.innerWidth
	
	if (nav_horizontal_left) {
		if (nav_width >= window_width) {
			d.q('.nav .nav-items-wrap').style.width = 'calc(100% - ' + d.q('.nav .nav__buttons').scrollWidth + 'px)'
			d.q('.nav .homelink').style.width = '100%'
		} else {
			d.q('.nav .nav-items-wrap').style.width = 'auto'
			d.q('.nav .homelink').style.width = 'auto'
		}
	}

	if (nav_horizontal_right) {
		if (nav_width >= window_width) {
			d.q('.nav .homelink').style.width = 'calc(100% - ' + d.q('.nav .nav__buttons').scrollWidth + 'px)'
		} else {
			d.q('.nav .homelink').style.width = 'auto'
		}
	}

	if (nav_horizontal_center) {
		let nav_height = d.q('nav').offsetHeight
		if (nav_height >= nav_height_max) {
			d.q('.nav--buttons-only .homelink').style.width =
				'calc(100% - ' +
				d.q('.nav--buttons-only .nav__buttons').scrollWidth +
				'px - ' +
				d.q('.nav--buttons-only .buttons-wrap-header').scrollWidth +
				'px - 24px)'
		} else {
			d.q('.nav--buttons-only .homelink').style.width = 'auto'
		}
	}
}

//-- Display Burger icon
const display_burger_icon = () => {
	let window_width = window.innerWidth
	
	if (nav_horizontal_right_left) {
		// Determine if burger menu should show based on window width first
		let should_show_burger = false
		
		// Fixed mobile breakpoint
		if (window_width <= 768) {
			// Mobile - always show burger
			should_show_burger = true
		} else if (window_width <= 1024) {
			// Tablet range - calculate to see if nav fits
			// Temporarily show nav items to get accurate measurement
			let navItems = d.q('.nav__items')
			let langDropdown = d.q('.drodown-wrap--lang')
			let wasHidden = false
			
			if (navItems && navItems.style.display === 'none') {
				navItems.style.display = 'flex'
				wasHidden = true
			}
			if (langDropdown && langDropdown.style.display === 'none') {
				langDropdown.style.display = 'flex'
			}
			
			// Calculate with items visible
			calculate_nav_width()
			
			// Hide again if calculation shows we need burger
			if (nav_width === 0) {
				// Measurement failed, if nav was hidden before, keep it hidden
				should_show_burger = wasHidden
			} else if (wasHidden || nav_width + 50 > window_width) {
				should_show_burger = true
			}
		} else {
			// Desktop (> 1024px) - only show burger if content really doesn't fit
			// Temporarily show nav items to measure
			let navItems = d.q('.nav__items')
			let langDropdown = d.q('.drodown-wrap--lang')
			
			if (navItems && navItems.style.display === 'none') {
				navItems.style.display = 'flex'
			}
			if (langDropdown && langDropdown.style.display === 'none') {
				langDropdown.style.display = 'flex'
			}
			
			// Calculate with items visible
			calculate_nav_width()
			
			// For desktop, be more conservative - only show burger if really needed
			if (nav_width === 0) {
				// Measurement failed, default to showing full nav on desktop
				should_show_burger = false
			} else if (nav_width > window_width - 20) {
				should_show_burger = true
			} else {
				should_show_burger = false
			}
		}
		
		if (should_show_burger) {
			// Show burger menu
			if (d.q('.nav__items')) d.q('.nav__items').style.display = 'none'
			if (d.q('.drodown-wrap--lang')) d.q('.drodown-wrap--lang').style.display = 'none'
			if (window_width <= 768 && d.q('nav .buttons-wrap-header')) d.q('nav .buttons-wrap-header').style.display = 'none'
			if (d.q('.burger-button')) d.q('.burger-button').classList.add('show')
		} else {
			// Hide burger menu
			if (d.q('.nav__items')) d.q('.nav__items').style.display = 'flex'
			if (d.q('.drodown-wrap--lang')) d.q('.drodown-wrap--lang').style.display = 'flex'
			if (d.q('nav .buttons-wrap-header')) d.q('nav .buttons-wrap-header').style.display = 'flex'
			if (d.q('.burger-button')) d.q('.burger-button').classList.remove('show')
			remove_burger_menu()
		}
	}

	if (nav_horizontal_center) {
		let nav_height = d.q('nav').offsetHeight

		if (nav_height >= nav_height_max) {
			d.q('.nav--buttons-only').style.top = '0'
			d.q('nav').style.top = '-100%'
			d.q('.burger-button').classList.add('show')
		} else {
			d.q('nav').style.top = '0'
			d.q('.nav--buttons-only').style.top = '-100%'
			d.q('.burger-button').classList.remove('show')
			remove_burger_menu()
		}
	}

	//-- If no logo and title too long
	setTimeout(function () {
		adjust_nav_widths()
	}, 100)
}

//-- Display Burger menu
const display_burger_menu = () => {
	if (nav_vertical) {
		d.q('.nav-vertical').classList.toggle('show')
		d.q('body').classList.toggle('overlay')
	} else {
		d.q('.burger-menu').classList.toggle('show')
	}
	d.q('.burger-button').classList.toggle('active')
	d.q('body').classList.toggle('burger-menu-enable')

	// Update aria-expanded for accessibility
	const burgerBtn = d.q('.burger-button')
	if (burgerBtn) {
		const isExpanded = burgerBtn.classList.contains('active')
		burgerBtn.setAttribute('aria-expanded', isExpanded ? 'true' : 'false')
	}
}

//-- Remove Burger menu
const remove_burger_menu = () => {
	if (nav_vertical) {
		d.q('.nav-vertical').classList.remove('show')
		d.q('body').classList.remove('overlay')
	} else {
		d.q('.burger-menu').classList.remove('show')
	}
	d.q('.burger-button').classList.remove('active')
	d.q('body').classList.remove('burger-menu-enable')

	// Update aria-expanded for accessibility
	const burgerBtn = d.q('.burger-button')
	if (burgerBtn) {
		burgerBtn.setAttribute('aria-expanded', 'false')
	}
}

//-- Remove buttons on nav for tiny screen
const remove_buttons_menu = () => {
	let window_width = window.innerWidth
	// Check if buttons should be removed for mobile view

	// Use a fixed breakpoint for consistency
	if (window_width <= 480) {
		// Hiding buttons (mobile width exceeded)
		if (nav_horizontal_right_left) d.q('.buttons-wrap-header').style.display = 'none'
		if (nav_vertical) d.q('header .buttons-wrap-header').style.display = 'none'
		if (nav_horizontal_center)
			for (let n = 0; n < d.qAll('.nav--buttons-only .btn').length; n++)
				d.qAll('.nav--buttons-only .btn')[n].style.display = 'none'
	} else {
		if (nav_horizontal_right_left) {
			if (window_width <= 768 && d.q('.burger-button') && d.q('.burger-button').classList.contains('show')) {
				d.q('nav .buttons-wrap-header').style.display = 'none'
			} else {
				d.q('nav .buttons-wrap-header').style.display = 'flex'
			}
		}
		if (nav_vertical) d.q('header .buttons-wrap-header').style.display = 'flex'
		if (nav_horizontal_center)
			for (let n = 0; n < d.qAll('.nav--buttons-only .btn').length; n++)
				d.qAll('.nav--buttons-only .btn')[n].style.display = 'flex'
	}
}

//-- Dropdown Burger Menu
const display_burger_dropdown = (param) => {
	param.offsetParent.classList.toggle('visible')

	// Update aria-expanded for accessibility
	const isExpanded = param.offsetParent.classList.contains('visible')
	param.setAttribute('aria-expanded', isExpanded ? 'true' : 'false')
}

//-- Sticky nav menu
const sticky_menu_nav = () => {
	let nav_height = d.q('nav').offsetHeight
	if (nav_height >= nav_height_max) {
		let nav_height = d.q('.nav--buttons-only').offsetHeight
		d.q('.menu-nav').style.top = nav_height + 'px'
	} else {
		let nav_height = d.q('.hello').offsetHeight
		d.q('.menu-nav').style.top = nav_height + 'px'
	}
}

//-- Menu active item
const menu_active_item = () => {
	for (let n = 0; n < d.qAll('.menu-nav__item').length; n++) {
		d.qAll('.menu-nav__item')[0].classList.add('active')
		d.qAll('.menu-nav__item')[n].onclick = function (e) {
			for (let j = 0; j < d.qAll('.menu-nav__item').length; j++) {
				d.qAll('.menu-nav__item')[j].classList.remove('active')
			}
			this.classList.add('active')
		}
	}
}

//-- Menu active item • Summary
const menu_active_item_summary = () => {
	for (let n = 0; n < d.qAll('.menu-nav__item--home').length; n++) {
		d.qAll('.menu-wrap')[0].classList.add('active')
		// Calculate height after a small delay to ensure content is rendered
		setTimeout(() => {
			if (d.q('.menus-wrapper') && d.qAll('.menu-wrap')[0]) {
				d.q('.menus-wrapper').style.height = d.qAll('.menu-wrap')[0].offsetHeight + 'px'
			}
		}, 100)
		d.qAll('.menu-nav__item--home')[0].classList.add('active')

		d.qAll('.menu-nav__item--home')[n].onclick = function (e) {
			for (let j = 0; j < d.qAll('.menu-wrap').length; j++) {
				d.qAll('.menu-wrap')[j].classList.remove('active')

				if (this.dataset.anchor == d.qAll('.menu-wrap')[j].getAttribute('id')) {
					d.qAll('.menu-wrap')[j].classList.add('active')
					d.q('.menus-wrapper').style.height = d.qAll('.menu-wrap')[j].offsetHeight + 'px'
				}
			}

			for (let j = 0; j < d.qAll('.menu-nav__item--home').length; j++) {
				d.qAll('.menu-nav__item--home')[j].classList.remove('active')
			}

			this.classList.add('active')
		}
	}
}

//-- Contact form with accessible error handling (WCAG 3.3.1, 3.3.3)
if ($('#contact-form').length > 0) {
	$('#contact-form').validate({
		// Use custom error placement for accessibility
		errorPlacement: function (error, element) {
			var errorId = element.attr('id') + '-error'
			var errorContainer = $('#' + errorId)
			if (errorContainer.length > 0) {
				errorContainer.text(error.text())
			}
		},
		// Add aria-invalid when field is invalid
		highlight: function (element) {
			$(element).attr('aria-invalid', 'true')
		},
		// Remove aria-invalid when field is valid
		unhighlight: function (element) {
			$(element).attr('aria-invalid', 'false')
			var errorId = $(element).attr('id') + '-error'
			$('#' + errorId).text('')
		},
		// Announce errors to screen readers on form submit
		invalidHandler: function (event, validator) {
			var errorCount = validator.numberOfInvalids()
			if (errorCount > 0) {
				var errorSummary = $('#contact-form-errors')
				var message = errorCount === 1
					? '1 error found. Please correct the highlighted field.'
					: errorCount + ' errors found. Please correct the highlighted fields.'
				errorSummary.text(message)
				// Focus first invalid field
				$(validator.errorList[0].element).focus()
			}
		},
		submitHandler: function (form) {
			// Clear error summary on successful submit
			$('#contact-form-errors').text('')
			schnockSendForm(form, 'Message depuis le site', function () {
				$(form).find('.input--small, .input--full, #send').hide()
				$(form).find('.step2').removeClass('hidden')
				// Send a google analytics event
				$(window).trigger('contact-form-sent')
			})
			return false
		},
	})
}

//-- Fancybox
$('[data-fancybox].iframe--widget').fancybox({
	buttons: [],
	touch: false,
	beforeLoad: function () {
		if (!$('.fancybox-iframe').parent().hasClass('iframe-wrapper')) {
			$('.fancybox-iframe').wrap('<div class="iframe-wrapper"/>')
		}
	},
})

$('[data-fancybox].iframe--contact').fancybox({
	buttons: [],
	touch: false,
	beforeLoad: function () {
		if (!$('.fancybox-iframe').parent().hasClass('iframe-wrapper')) {
			$('.fancybox-iframe').wrap('<div class="iframe-wrapper"/>')
		}
	},
})

$('[data-fancybox]:not(.iframe--widget):not(.iframe--menus)').fancybox({
	iframe: {
		css: {
			height: '450px',
		},
	},
	buttons: ['close'],
	beforeLoad: function () {
		if (!$('.fancybox-iframe').parent().hasClass('iframe-wrapper')) {
			$('.fancybox-iframe').wrap('<div class="iframe-wrapper"/>')
		}
	},
})

function bindEvent(element, eventName, eventHandler) {
	if (element.addEventListener) {
		element.addEventListener(eventName, eventHandler, false)
	} else if (element.attachEvent) {
		element.attachEvent('on' + eventName, eventHandler)
	}
}

//-- Listen to message from child window
bindEvent(window, 'message', function (e) {
	if (e.data === 'close-widget') {
		$.fancybox.getInstance().close()
	}
})

//-- Slider
const slider = () => {
	if ($('.slide').length > 0) {
		$('.slide.active').cycle({
			log: false,
			prev: '.nav__btn--prev',
			next: '.nav__btn--next',
			slides: '>div',
		})

		$('.albums li').click(function (e) {
			if (!$(this).hasClass('active')) {
				var slider = $(this).children('a').attr('data-slider')
				$('.albums li.active').removeClass('active')
				$(this).addClass('active')
				$('.slide.active').fadeOut(200, function () {
					$('.slide.active').removeClass('active').cycle('pause')
					$('#' + slider).fadeIn(200, function () {
						if ($('#' + slider).is('.cycle-paused')) {
							$(this).cycle('resume').addClass('active')
						} else {
							$('#' + slider)
								.cycle({
									log: false,
									prev: '.nav__btn--prev',
									next: '.nav__btn--next',
									slides: '>div',
								})
								.addClass('active')
						}
					})
				})
			}
			return false
		})
	}
}

//-------------------------------------
//	MAIN
//-------------------------------------
const main = () => {
	// Initialize navigation measurements first
	initialize_nav_measurements()
	
	// Then check if burger icon should be displayed
	if (nav_horizontal_right_left || nav_horizontal_center) display_burger_icon()
	if (nav_horizontal_center && page_name == 'menus') sticky_menu_nav()
	if (nav_horizontal_right_left || nav_horizontal_center || nav_vertical) remove_buttons_menu()
	if (nav_vertical) d.q('.nav-items-wrap').style.height = 'calc(100% - ' + d.q('.nav__bottom').scrollHeight + 'px)'
	menu_active_item()
	menu_active_item_summary()
	// if ((template_w_slider && (page_name == 'gallery' || page_name == 'custom')) || template == 0)
	slider()

	if (nav_vertical) {
		if (768 >= window.innerWidth) {
			d.q('.header-vertical .homelink').style.width =
				'calc(100% - ' + d.q('.header-vertical .nav__buttons').scrollWidth + 'px)'
		} else {
			d.q('.header-vertical .homelink').style.width = 'auto'
		}
	} else if (nav_inside) {
		if (768 >= window.innerWidth) {
			d.q('.nav-inside .homelink').style.width =
				'calc(100% - ' + d.q('.nav-inside .burger-button').scrollWidth + 'px)'
		} else {
			d.q('.nav-inside .homelink').style.width = 'auto'
		}
	}

	//-- Delete loader (Must be before any external dependency as a fallback safety)
	setTimeout(function () {
		d.q('body').style.overflow = 'initial'
		d.q('.loader-wrap').classList.add('hide')
	}, 400)

	//-- Opening hours active day
	var day = new Date().getDay() || 7
	$('.day' + day).addClass('day-wrap--active')

	//-- Active page
	let nav_item_class = d.q('.nav__item--' + page_name)
	if (page_name != 'home' && nav_item_class) nav_item_class.classList.add('active')

	//-- Smooth scrolling to page anchor on click
	$("a[href*='#']:not([href='#'])").click(function () {
		if (
			location.hostname == this.hostname &&
			this.pathname.replace(/^\//, '') == location.pathname.replace(/^\//, '')
		) {
			let target = $(this.hash)
			let window_width = $(window).width()
			let menu_nav_height = $('.menu-nav').outerHeight()
			let nav_height = !nav_vertical ? $('nav').outerHeight() : $('header').outerHeight()

			//-- Conditions
			if (page_name == 'menus') {
				if (
					(window_width <= 970 && (template == 1 || template == 4)) ||
					(window_width <= 750 && (template == 2 || template == 5))
				) {
					nav_height = nav_height + menu_nav_height
				} else if (
					(window_width <= 1220 && (template == 2 || template == 5)) ||
					(window_width <= 750 && (template == 3 || template == 6)) ||
					(window_width >= 750 && template == 9)
				) {
					nav_height = menu_nav_height
				} else if (
					(window_width >= 1220 && (template == 2 || template == 5)) ||
					(window_width >= 750 && (template == 3 || template == 6))
				) {
					nav_height = 20
				} else if (window_width >= 970 && (template == 1 || template == 4)) {
					nav_height = nav_height
				} else {
					nav_height = nav_height + menu_nav_height
				}
			} else if (template == 0) {
				nav_height = menu_nav_height
			} else if (template == 10) {
				nav_height = menu_nav_height
			} else if (page_name == 'gallery') {
				if (template == 3 || template == 6) {
					nav_height = 20
				} else {
					nav_height = nav_height + 20
				}
			}

			target = target.length ? target : $('[name=' + this.hash.slice(1) + ']')
			if (target.length) {
				$('html, body').animate(
					{
						scrollTop: target.offset().top - nav_height,
					},
					1000
				)
			}
		}
	})

	//-- Smooth scrolling to the top of page
	$('#scroll-top').click(function () {
		$('html, body').animate(
			{
				scrollTop: 0,
			},
			500
		)
	})

	//-- Tootips plugin init
	tippy('.tippy', {
		arrow: false,
		animation: 'shift-away-subtle',
	})

	//-- Add class on nav when you scroll over XXXpx
	$(window).scroll(function () {
		if ($(this).scrollTop() > 100) {
			$('nav').addClass('scroll')
		} else {
			$('nav').removeClass('scroll')
		}
	})

	scrollTo(document.body, 0, 100)
	document.querySelector('body').style.overflow = 'hidden'

	//-- Browser update
	var $buoop = { required: { e: -4, f: -3, o: -3, s: -1, c: -3 }, insecure: true, unsupported: true, api: 2021.05 }

	function $buo_f() {
		var e = document.createElement('script')
		e.src = '//browser-update.org/update.min.js'
		document.body.appendChild(e)
	}
	try {
		document.addEventListener('DOMContentLoaded', $buo_f, false)
	} catch (e) {
		window.attachEvent('onload', $buo_f)
	}
}

//-------------------------------------
//	RESPONSIVE
//-------------------------------------
const responsive = () => {
	// Add debouncing to prevent rapid recalculations
	clearTimeout(window.resizeTimeout)
	window.resizeTimeout = setTimeout(() => {
		// Reset any width constraints before recalculating
		if (nav_horizontal_left) {
			if (d.q('.nav .nav-items-wrap')) d.q('.nav .nav-items-wrap').style.width = 'auto'
			if (d.q('.nav .homelink')) d.q('.nav .homelink').style.width = 'auto'
		}
		if (nav_horizontal_right) {
			if (d.q('.nav .homelink')) d.q('.nav .homelink').style.width = 'auto'
		}
		
		// Recalculate navigation display
		if (nav_horizontal_right_left || nav_horizontal_center) display_burger_icon()
		if (nav_horizontal_center && page_name == 'menus') sticky_menu_nav()
		if (nav_horizontal_right_left || nav_horizontal_center || nav_vertical) remove_buttons_menu()
		if (nav_inside || (nav_vertical && 750 >= window.innerWidth)) remove_burger_menu()
		if (nav_vertical) d.q('.nav-items-wrap').style.height = 'calc(100% - ' + d.q('.nav__bottom').scrollHeight + 'px)'
		
		// Apply width adjustments after navigation state is determined
		adjust_nav_widths()

		if (nav_vertical) {
			if (768 >= window.innerWidth) {
				d.q('.header-vertical .homelink').style.width =
					'calc(100% - ' + d.q('.header-vertical .nav__buttons').scrollWidth + 'px)'
			} else {
				d.q('.header-vertical .homelink').style.width = 'auto'
			}
		} else if (nav_inside) {
			if (768 >= window.innerWidth) {
				d.q('.nav-inside .homelink').style.width =
					'calc(100% - ' + d.q('.nav-inside .burger-button').scrollWidth + 'px)'
			} else {
				d.q('.nav-inside .homelink').style.width = 'auto'
			}
		}

		//-- Resize menus summary on screen resize
		for (let j = 0; j < d.qAll('.menu-wrap').length; j++) {
			if (d.qAll('.menu-wrap')[j].classList.contains('active')) {
				d.q('.menus-wrapper').style.height = d.qAll('.menu-wrap')[j].offsetHeight + 'px'
			}
		}
	}, 150)
}

//-------------------------------------
//	VARIABLES
//-------------------------------------
var d = document
d.q = document.querySelector
d.qAll = document.querySelectorAll

var page_name = d.q('body').className.split('current-page-')[1].split(' ')[0]

var template_w_slider = template == 0 || template == 7 || template == 8 || template == 9

var nav_horizontal_right =
	template == 1 ||
	template == 4 ||
	template == 11 ||
	template == 15 ||
	template == 16 ||
	template == 17 ||
	template == 18 ||
	template == 19
var nav_horizontal_left = template == 7

var nav_horizontal_right_left = nav_horizontal_right + nav_horizontal_left

var nav_horizontal_center = template == 8
var nav_vertical = template == 2 || template == 5 || template == 9
var nav_inside = template == 3 || template == 6

//-- Init variables for nav
var nav_btns_width = 0
var nav_dropdown_lang_width = 0
var homelink_width = 0
var nav_width = 0
var nav_mobile_width = 0
var initial_nav_mobile_width = 0 // Store the initial calculation
var nav_height_max = 0 // For nav_horizontal_center

// Initialize navigation measurements after DOM is ready
const initialize_nav_measurements = () => {
	if (nav_vertical) {
		let header_padding_side =
			parseInt(getComputedStyle(d.q('header')).paddingLeft) + parseInt(getComputedStyle(d.q('header')).paddingRight)

		let number_of_btns = 0
		let btn_margin = 0
		nav_btns_width = 0
		
		if (d.q('header .buttons-wrap-header .btn')) {
			number_of_btns = d.qAll('header .buttons-wrap-header .btn').length
			btn_margin = parseInt(getComputedStyle(d.q('header .buttons-wrap-header .btn')).marginRight) || 0
			for (let n = 0; n < number_of_btns; n++)
				nav_btns_width = nav_btns_width + d.qAll('header .buttons-wrap-header .btn')[n].scrollWidth
			nav_btns_width = nav_btns_width + btn_margin * number_of_btns
		}

		nav_mobile_width = d.q('header .homelink').scrollWidth + nav_btns_width + 54 + header_padding_side
		initial_nav_mobile_width = nav_mobile_width
	}

	if (nav_horizontal_center) {
		var nav_padding =
			parseInt(getComputedStyle(d.q('nav')).paddingTop) + parseInt(getComputedStyle(d.q('nav')).paddingBottom)
		var item_margin =
			parseInt(getComputedStyle(d.q('nav .nav__item')).marginTop) +
			parseInt(getComputedStyle(d.q('nav .nav__item')).marginBottom)

		let nav_btns_width = 0
		let nav_btn_height = 0
		if (d.q('.nav__items .btn')) {
			nav_btn_height = d.q('.nav__items .btn').offsetHeight
			for (let n = 0; n < d.qAll('.nav__items .btn').length; n++)
				nav_btns_width = nav_btns_width + d.qAll('.nav__items .btn')[n].scrollWidth
		}

		nav_height_max =
			(d.q('nav .nav__item').clientHeight + item_margin) * 2 + (nav_btn_height + item_margin) + nav_padding

		// Get homelink width if not already set
		if (homelink_width === 0 && d.q('.homelink')) {
			homelink_width = d.q('.homelink').scrollWidth
		}
		
		nav_mobile_width = homelink_width + nav_btns_width + 80 + 54 + 40
		initial_nav_mobile_width = nav_mobile_width
	}
	
	// For horizontal nav, calculate initial values
	if (nav_horizontal_right_left) {
		calculate_nav_width()
	}
}

// Ensure DOM is ready before running main
if (document.readyState === 'loading') {
	document.addEventListener('DOMContentLoaded', main)
} else {
	// DOM is already ready, call main immediately
	main()
}

window.addEventListener('resize', responsive)

// Recalculate nav width when fonts are loaded
if (document.fonts && document.fonts.ready) {
	document.fonts.ready.then(() => {
		// Reinitialize only if initial_nav_mobile_width wasn't set properly
		if (initial_nav_mobile_width === 0) {
			initialize_nav_measurements()
		}
		if (nav_horizontal_right_left || nav_horizontal_center) {
			setTimeout(() => {
				display_burger_icon()
			}, 100)
		}
	})
}

// Also recalculate on window load (for images and other resources)
window.addEventListener('load', () => {
	// Reinitialize only if initial_nav_mobile_width wasn't set properly
	if (initial_nav_mobile_width === 0) {
		initialize_nav_measurements()
	}
	if (nav_horizontal_right_left || nav_horizontal_center) {
		setTimeout(() => {
			display_burger_icon()
		}, 100)
	}
})

// Additional safeguard - recalculate after a short delay
setTimeout(() => {
	// Final attempt to initialize if still not set
	if (initial_nav_mobile_width === 0) {
		initialize_nav_measurements()
	}
	if (nav_horizontal_right_left || nav_horizontal_center) {
		display_burger_icon()
	}
}, 500)

//-------------------------------------
//	ACCESSIBILITY - Keyboard Navigation
//-------------------------------------

// Focus trap for modal dialogs (burger menu)
const getFocusableElements = (container) => {
	if (!container) return []
	return Array.from(container.querySelectorAll(
		'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
	)).filter(el => el.offsetParent !== null) // Only visible elements
}

const trapFocus = (e, container) => {
	const focusableElements = getFocusableElements(container)
	if (focusableElements.length === 0) return

	const firstElement = focusableElements[0]
	const lastElement = focusableElements[focusableElements.length - 1]

	if (e.shiftKey && document.activeElement === firstElement) {
		// Shift+Tab on first element -> go to last
		e.preventDefault()
		lastElement.focus()
	} else if (!e.shiftKey && document.activeElement === lastElement) {
		// Tab on last element -> go to first
		e.preventDefault()
		firstElement.focus()
	}
}

// Add keyboard support for burger button
document.addEventListener('keydown', function (e) {
	// Handle Enter or Space on burger button
	if (e.target.classList.contains('burger-button')) {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault()
			display_burger_menu()
			// Focus first focusable element in menu after opening
			setTimeout(() => {
				const burgerMenu = d.q('.burger-menu.show') || d.q('.nav-vertical.show')
				if (burgerMenu) {
					const focusable = getFocusableElements(burgerMenu)
					if (focusable.length > 0) {
						focusable[0].focus()
					}
				}
			}, 100)
		}
	}

	// Handle Enter or Space on dropdown icons in burger menu
	if (e.target.classList.contains('fa-angle-down') && e.target.hasAttribute('role')) {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault()
			display_burger_dropdown(e.target)
		}
	}

	// Handle Tab key for focus trap in burger menu
	if (e.key === 'Tab') {
		const burgerMenu = d.q('.burger-menu')
		const navVertical = d.q('.nav-vertical')
		if (burgerMenu && burgerMenu.classList.contains('show')) {
			trapFocus(e, burgerMenu)
		} else if (navVertical && navVertical.classList.contains('show')) {
			trapFocus(e, navVertical)
		}
	}

	// Handle Escape key to close burger menu
	if (e.key === 'Escape') {
		const burgerMenu = d.q('.burger-menu')
		const navVertical = d.q('.nav-vertical')
		if ((burgerMenu && burgerMenu.classList.contains('show')) ||
			(navVertical && navVertical.classList.contains('show'))) {
			remove_burger_menu()
			// Return focus to burger button
			const burgerBtn = d.q('.burger-button')
			if (burgerBtn) {
				burgerBtn.focus()
			}
		}
	}
})
