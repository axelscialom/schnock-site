#!/usr/bin/env python3
"""Rebuild schnock-restaurant.fr as a static site, keeping the Zenchef template look."""
import os, re, shutil, subprocess, hashlib, json

S = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(S, 'dl')
MIRROR = os.path.join(S, 'mirror', 'www.schnock-restaurant.fr')
TAC = os.path.join(S, 'tac')
OUT = os.path.join(S, 'site')
IMGCACHE = os.path.join(S, 'imgcache')

PAGES = {  # output dir -> raw html
    '': 'home_.html',
    'menus-carte': 'home_menus-carte_.html',
    'photos': 'home_photos_.html',
    'informations-contact': 'home_informations-contact_.html',
}
LEGAL = ['mentions-legales', 'politique-de-confidentialite', 'politique-cookies', 'accessibilite']

IMG_RE = re.compile(r"https://(?:ugc\.zenchef\.com|www\.schnock-restaurant\.fr/i)/[^'\"\s)]+?\.(?:jpe?g|png|webp|gif)", re.I)


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def relativize(s, depth):
    """Root-relative links -> relative, so the site works on any host or sub-path (GitHub Pages preview)."""
    prefix = '../' * depth
    s = re.sub(r'(href|src)="/(?!/)', lambda m: '%s="%s' % (m.group(1), prefix or './'), s)
    s = re.sub(r"url\((['\"]?)/(?!/)", lambda m: 'url(' + m.group(1) + prefix, s)
    return s


def absolute_jsonld(s):
    return re.sub(r'(<script[^>]*application/ld\+json[^>]*>)(.*?)(</script>)',
                  lambda m: m.group(1) + m.group(2).replace('"/images/', '"https://www.schnock-restaurant.fr/images/') + m.group(3), s, flags=re.S)


def optimise_images():
    from PIL import Image, ImageOps
    d = os.path.join(OUT, 'images')
    for f in os.listdir(d):
        p = os.path.join(d, f)
        if not f.endswith(('.jpg', '.jpeg')) or os.path.getsize(p) < 400_000:
            continue
        im = ImageOps.exif_transpose(Image.open(p)).convert('RGB')
        im.thumbnail((2000, 2000))
        im.save(p, 'JPEG', quality=82, optimize=True, progressive=True)


def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)


# ---------- assets ----------
def copy_assets():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for root, _, files in os.walk(MIRROR):
        rel = os.path.relpath(root, MIRROR)
        if not (rel.startswith('css') or rel.startswith('js') or rel.startswith('img')):
            continue
        os.makedirs(os.path.join(OUT, rel), exist_ok=True)
        for f in files:
            shutil.copy(os.path.join(root, f), os.path.join(OUT, rel, f.split('?')[0]))
    # Google Fonts import back to the live Google URL
    style = os.path.join(OUT, 'css/css_11/314f6c/_default_/_default_/main.css')
    s = read(style)
    s = sub1(r"@import url\([^\n]*fonts\.googleapis\.com[^\n]*\);",
               "@import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:ital,wght@0,300;0,600;0,700;1,300;1,600;1,700&family=Yeseva+One&display=swap');", s)
    write(style, s)
    # tarteaucitron companion files
    dst = os.path.join(OUT, 'js/libs/tarteaucitron')
    for f in ['lang/tarteaucitron.fr.js', 'tarteaucitron.services.js', 'css/tarteaucitron.css', 'advertising.js', 'tarteaucitron.js']:
        os.makedirs(os.path.dirname(os.path.join(dst, f)), exist_ok=True)
        shutil.copy(os.path.join(TAC, f), os.path.join(dst, f))
    # contact form: post to our own form endpoint instead of Zenchef's /contact-form.php
    sj = os.path.join(OUT, 'js/globals/script.js')
    s = read(sj)
    old = """			var options = {
				target: '#contact-form', // target element(s) to be updated with server response
				beforeSubmit: function (formData, jqForm, options) {
					var queryString = $.param(formData)
					return true
				},
				success: function (data) {
					$('.step2').toggleClass('hidden')
					// Send a google analytics event
					$(window).trigger('contact-form-sent')
				},
				url: '/contact-form.php',
			}
			$(form).ajaxSubmit(options)
			return false"""
    new = """			schnockSendForm(form, 'Message depuis le site', function () {
				$(form).find('.input--small, .input--full, #send').hide()
				$(form).find('.step2').removeClass('hidden')
				// Send a google analytics event
				$(window).trigger('contact-form-sent')
			})
			return false"""
    assert old in s, 'contact form block not found'
    s = s.replace(old, new)
    write(sj, s)
    shutil.copy(os.path.join(S, 'src/site.js'), os.path.join(OUT, 'js/site.js'))
    shutil.copy(os.path.join(S, 'src/site.css'), os.path.join(OUT, 'css/site.css'))
    os.remove(os.path.join(OUT, 'js/globals/getRestoIdKonamiCode.js'))


# ---------- images ----------
img_map = {}


def local_img(url):
    if url in img_map:
        return img_map[url]
    name = url.rsplit('/', 1)[1]
    m = re.search(r'/i/schnock-([^/]+)/', url)
    if m and not m.group(1)[0].isdigit():
        name = m.group(1) + '-' + name
    name = name.lower()
    os.makedirs(IMGCACHE, exist_ok=True)
    cache = os.path.join(IMGCACHE, hashlib.sha1(url.encode()).hexdigest())
    if not os.path.exists(cache):
        subprocess.run(['curl', '-sSfL', '-A', 'Mozilla/5.0', '-o', cache, url], check=True)
    os.makedirs(os.path.join(OUT, 'images'), exist_ok=True)
    shutil.copy(cache, os.path.join(OUT, 'images', name))
    img_map[url] = '/images/' + name
    return img_map[url]


# ---------- html ----------
PRIV_NAV = """	<!-- Privatisation -->
	<li class="nav__item nav__item--privatisation">
		<a title="Privatisation" href="/privatisation/">Privatisation</a>
	</li>

	<!-- Contact -->
	<li class="nav__item nav__item--contact">"""
PRIV_BURGER = """			<!-- Privatisation -->
			<li class="burger-menu__item burger-menu__item--privatisation">
				<a title="Privatisation" href="/privatisation/">Privatisation</a>
			</li>

			<!-- Contact -->
			<li class="burger-menu__item burger-menu__item--contact">"""


def sub1(pattern, repl, s, flags=re.S, count=0, must=True):
    n = len(re.findall(pattern, s, flags))
    if must and n == 0:
        raise SystemExit('pattern not found: ' + pattern[:80])
    return re.sub(pattern, repl, s, count=count, flags=flags)


def transform(s):
    s = IMG_RE.sub(lambda m: local_img(m.group(0)), s)
    s = sub1(r'[ \t]*<link rel="alternate" hreflang="[^"]+" href="[^"]+" />\n', '', s)
    s = sub1(r'<div class="dropdown-wrap drodown-wrap--lang.*?</ul>\s*</div>', '', s)
    s = sub1(r'<!-- Language -->\s*<ul class="language-list">.*?</ul>', '', s)
    s = sub1(r'<script src="/js/globals/getRestoIdKonamiCode\.js\?v=26"></script>\n', '', s)
    s = re.sub(r'(src|href)="(/[^"]+?)\?v=\d+"', r'\1="\2"', s)
    s = re.sub(r'(src|href)="//', r'\1="https://', s)
    s = sub1(r'— Création de site internet restaurant avec\s*<a [^>]*zcf-link">Zenchef<span class="sr-only">[^<]*</span></a>', '', s)
    s = s.replace('<meta property="og:site_name" content="Zenchef" />', '<meta property="og:site_name" content="Schnock" />')
    s = sub1(r'\t<!-- Contact -->\n\t<li class="nav__item nav__item--contact">', PRIV_NAV, s)
    s = sub1(r'\t\t\t<!-- Contact -->\n\t\t\t<li class="burger-menu__item burger-menu__item--contact">', PRIV_BURGER, s)
    # lunch formula price confirmed by axel on 2026-10-27 (Zenchef showed 25 €)
    s = s.replace('<span class="menu__price">25,00 EUR</span>', '<span class="menu__price">32,00 EUR</span>')
    # Zenchef form plumbing
    s = re.sub(r'\s*<input type="hidden" name="(restaurant_public_id|lang|token)"[^>]*>', '', s)
    # file names shown as photo captions
    s = re.sub(r'\s*<div class="album-photo__caption">\s*<p class="album-photo__title">[^<]*\.(?:jpe?g|png)</p>\s*</div>', '', s, flags=re.I)
    s = re.sub(r'(alt|title)="Schnock [^"]*\.(?:jpe?g|png)"', r'\1="Schnock"', s, flags=re.I)
    # our own small additions
    s = s.replace('<link rel="stylesheet" href="/css/css_11/314f6c/_default_/_default_/main.css" media="print" onload="this.media=\'all\'">',
                  '<link rel="stylesheet" href="/css/css_11/314f6c/_default_/_default_/main.css" media="print" onload="this.media=\'all\'">\n\t<link rel="stylesheet" href="/css/site.css">', 1)
    s = sub1(r'(<script src="/js/globals/script\.js"></script>)', r'<script src="/js/site.js"></script>\n\1', s, count=1)
    s = sub1(r'(<div class="footer__btns">.*?Réserver\s*</a>)',
             r'\1' + '\n\t\t\t\t\t<a class="btn btn--std btn--small btn--privatisation" href="/privatisation/">Privatiser</a>', s, count=1)
    return s


# ---------- SEO ----------
SITE = 'https://www.schnock-restaurant.fr/'
SEO = {
    '': ("Schnock | Restaurant cuisine de marché & comptoir à vins, Paris 17e (Pereire)",
         "Schnock, cuisine de marché et comptoir à vins au 31 rue Guillaume Tell, Paris 17e, à deux pas de la place Pereire. Déjeuner, dîner, after-work et privatisation. Réservez en ligne."),
    'menus-carte': ("Carte & menus | Schnock, restaurant Paris 17e",
                    "La carte de Schnock : cuisine de marché de saison, formule déjeuner et vins de dégustation. Restaurant 31 rue Guillaume Tell, Paris 17e (Pereire)."),
    'photos': ("Photos du restaurant | Schnock, Paris 17e",
               "Salles, salons privatisables, façade et plats de Schnock, restaurant de cuisine de marché à Paris 17e, place Pereire."),
    'informations-contact': ("Accès & contact | Schnock, 31 rue Guillaume Tell, Paris 17e",
                             "Venir chez Schnock : 31 rue Guillaume Tell, 75017 Paris, métro Pereire, voiturier. Horaires, téléphone 01 47 64 86 04 et formulaire de contact."),
    'privatisation': ("Privatisation restaurant Paris 17e | Schnock, salons de 10 à 100 personnes",
                      "Privatisez Schnock à Paris 17e (Pereire) : salons de 10 à 35 personnes, restaurant entier jusqu'à 60 assis ou 100 debout. Menus de groupe dès 32 €, after-work, accords mets & vins. Devis sous 24h."),
}

ALBUM_ALT = {
    'privatisez-votre-salle-pour-vos-vnements': 'Salle du restaurant Schnock, Paris 17e',
    'schnock-notre-extrieur': 'Façade du restaurant Schnock, rue Guillaume Tell, Paris 17e',
    'nos-plats': 'Plat de saison du restaurant Schnock',
}

HOURS = [('Monday', '12:00', '15:00'), ('Monday', '19:00', '23:59'), ('Tuesday', '12:00', '15:00'), ('Tuesday', '19:00', '23:59'),
         ('Wednesday', '12:00', '15:00'), ('Wednesday', '18:00', '23:59'), ('Thursday', '12:00', '15:00'), ('Thursday', '19:00', '23:59'),
         ('Friday', '12:00', '15:00'), ('Friday', '19:00', '23:59'), ('Saturday', '19:00', '22:00'), ('Sunday', '12:00', '15:00')]

RESTAURANT_LD = {
    '@context': 'https://schema.org',
    '@type': 'Restaurant',
    '@id': SITE + '#restaurant',
    'name': 'Schnock',
    'description': "Cuisine de marché bien menée, bien sourcée, et comptoir de vins et dégustation convivial, dans un lieu aux pierres brutes à deux pas de la place Pereire.",
    'url': SITE,
    'telephone': '+33147648604',
    'image': [SITE + 'images/f575044403b6723af9c8185455a098eb.website.jpg', SITE + 'images/privatisation-schnock-grande-table.jpg'],
    'logo': SITE + 'images/9695f03cc97badd7b621b3dff5662d18.png',
    'address': {'@type': 'PostalAddress', 'streetAddress': '31 rue Guillaume Tell', 'postalCode': '75017',
                'addressLocality': 'Paris', 'addressRegion': 'Île-de-France', 'addressCountry': 'FR'},
    'geo': {'@type': 'GeoCoordinates', 'latitude': 48.8848837, 'longitude': 2.2951489},
    'hasMap': 'https://www.google.com/maps/dir/?api=1&destination=Schnock+31+Rue+Guillaume+Tell+75017+Paris',
    'servesCuisine': ['Française', 'Cuisine de marché', 'Bistrot'],
    'priceRange': '€€',
    'acceptsReservations': True,
    'hasMenu': SITE + 'menus-carte/',
    'paymentAccepted': 'Apple Pay, Amex, Mastercard, Visa, Carte Bleue',
    'amenityFeature': [{'@type': 'LocationFeatureSpecification', 'name': n, 'value': True}
                       for n in ['Privatisation', 'Voiturier', 'Wifi', 'Accès PMR']],
    'sameAs': ['https://www.instagram.com/schnock_restaurant/'],
    'openingHoursSpecification': [{'@type': 'OpeningHoursSpecification', 'dayOfWeek': d, 'opens': o, 'closes': c} for d, o, c in HOURS],
    'potentialAction': {'@type': 'ReserveAction',
                        'target': {'@type': 'EntryPoint', 'urlTemplate': 'https://bookings.zenchef.com/results?rid=376115&lang=fr',
                                   'inLanguage': 'fr', 'actionPlatform': ['http://schema.org/DesktopWebPlatform', 'http://schema.org/MobileWebPlatform']},
                        'result': {'@type': 'FoodEstablishmentReservation', 'name': 'Réserver une table'}},
}


def ld_script(data, id_=None):
    return '<script%s type="application/ld+json">\n%s\n</script>' % (
        ' id="%s"' % id_ if id_ else '', json.dumps(data, ensure_ascii=False, indent=1))


def set_head(s, page):
    title, desc = SEO[page]
    url = SITE + (page + '/' if page else '')
    s = sub1(r'<title>.*?</title>', lambda m: '<title>%s</title>' % title, s, count=1)
    s = sub1(r'<meta name="description" content="[^"]*" />', lambda m: '<meta name="description" content="%s" />' % desc, s, count=1)
    s = sub1(r'<meta property="og:description" content="[^"]*" />', lambda m: '<meta property="og:description" content="%s" />' % desc, s, count=1)
    s = sub1(r'<meta property="og:title" content="[^"]*" />', lambda m: '<meta property="og:title" content="%s" />' % title, s, count=1)
    s = sub1(r'<link rel="canonical" href="[^"]*" />', lambda m: '<link rel="canonical" href="%s" />' % url, s, count=1)
    s = sub1(r'<meta property="og:url" content="[^"]*" />', lambda m: '<meta property="og:url" content="%s" />' % url, s, count=1)
    s = s.replace('<meta property="og:image" content="/images/', '<meta property="og:image" content="%simages/' % SITE)
    s = s.replace('<link rel="shortcut icon" href="/images/', '<link rel="icon" href="/images/')
    s = sub1(r'<script id="restaurantJsonLd" type="application/ld\+json">.*?</script>', lambda m: ld_script(RESTAURANT_LD, 'restaurantJsonLd'), s, count=1)
    return s


def improve_photos(s):
    """Descriptive alt text and lazy loading for gallery photos."""
    def album(m):
        alt = ALBUM_ALT.get(m.group(1), 'Restaurant Schnock, Paris 17e')
        return re.sub(r'alt="[^"]*" title="[^"]*"', 'alt="%s" loading="lazy"' % alt, m.group(0))
    return re.sub(r'<div class="album album--gallery" id="([^"]+)">.*?(?=<div class="album album--gallery"|</section>)', album, s, flags=re.S)


def build_pages():
    teaser = read(os.path.join(S, 'src/home-teaser.html'))
    for out, raw in PAGES.items():
        s = transform(read(os.path.join(DL, raw)))
        s = set_head(s, out)
        s = improve_photos(s)
        if out == '':
            s = sub1(r'(?=\t<!-- Useful infos & opening hours -->)', lambda m: teaser, s, count=1)
        write(os.path.join(OUT, out, 'index.html'), s)
    return transform(read(os.path.join(DL, PAGES['informations-contact'])))


def render_menu(m):
    """Group menu in the markup of the Zenchef menus page, so it inherits menus.css."""
    out = ['<section class="s--menus reveal"><div class="menu-wrap page-content page-content--lg reveal-2" id="%s">' % m['id'],
           '\t<div class="menu-title-wrap">',
           '\t\t<h3 class="menu__title h2">%s</h3>' % m['title'],
           '\t\t<p class="menu__descr">%s</p>' % m['descr']]
    if m['prices']:
        out.append('\t\t<p class="menu__prices">%s</p>' % ''.join('<span class="menu__price">%s</span>' % p for p in m['prices']))
    out += ['\t\t<div class="divider-vertical divider--color"></div>', '\t</div>']
    for c in m['categories']:
        out.append('\t<div class="menu-category"><div class="menu-category-title-wrap"><h4 class="menu-category__title h3">%s</h4></div></div>' % c['title'])
        out.append('\t<div class="dishes-wrap">')
        for d in c['dishes']:
            name, price = (d, '') if isinstance(d, str) else d
            price_html = ('<div class="dish-price-wrap"><div class="three-dishes-wrap"><div class="dish-quant">'
                          '<p class="dish__price h4">%s</p></div></div></div>' % price) if price else ''
            out.append('\t\t<div class="dish-no-image"><div class="dish-content-wrap"><div class="dish-title-wrap">'
                       '<p class="dish__title h4">%s</p>%s</div></div></div>' % (name, price_html))
        out.append('\t</div>')
    if m.get('note'):
        out.append('\t<p class="menu__note">%s</p>' % m['note'])
    out.append('</div></section>')
    return '\n'.join(out)


def build_privatisation(contact_html):
    body = read(os.path.join(S, 'src/privatisation-body.html'))
    photos = read(os.path.join(OUT, 'photos/index.html'))
    album = re.search(r'(<div class="album__photos grid grid-3-col grid-gap-xs">.*?</div>\s*)</div>\s*<div class="album album--gallery" id="schnock-notre', photos, re.S).group(1)
    menus = json.loads(read(os.path.join(S, 'src/privatisation-menus.json')))
    faq = json.loads(read(os.path.join(S, 'src/faq.json')))
    body = body.replace('{{ALBUM}}', album)
    body = body.replace('{{MENU_NAV}}', '\n'.join(
        '<a class="menu-nav__item anchor-trigger" data-anchor="%s" href="#%s">%s</a>' % (m['id'], m['id'], m['title']) for m in menus))
    body = body.replace('{{MENUS}}', '\n'.join(render_menu(m) for m in menus))
    body = body.replace('{{FAQ}}', '\n'.join(
        '<details class="faq__item"><summary>%s</summary><p>%s</p></details>' % (q, a) for q, a in faq))
    faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}
    body = IMG_RE.sub(lambda m: local_img(m.group(0)), body)
    for f in os.listdir(os.path.join(S, 'src/img')):
        shutil.copy(os.path.join(S, 'src/img', f), os.path.join(OUT, 'images', f))
    s = contact_html
    s = s.replace('<body class="current-page-contact">', '<body class="current-page-privatisation">')
    s = sub1(r'<!-- Hero Picture -->.*?(?=<footer>)', lambda m: body, s, count=1)
    s = set_head(s, 'privatisation')
    s = sub1(r'<meta property="og:image" content="[^"]*" />', lambda m: '<meta property="og:image" content="%simages/privatisation-schnock-grande-table.jpg" />' % SITE, s, count=1)
    s = s.replace('</head>', ld_script(faq_ld) + '\n</head>', 1)
    s = sub1(r'(<script src="/js/site\.js"></script>)', r'\1\n<script src="/js/privatisation.js"></script>', s, count=1)
    write(os.path.join(OUT, 'privatisation', 'index.html'), s)
    shutil.copy(os.path.join(S, 'src/privatisation.js'), os.path.join(OUT, 'js/privatisation.js'))


def build_legal():
    css = os.path.join(S, 'pardot-style.css')
    if not os.path.exists(css):
        subprocess.run(['curl', '-sSfL', '-o', css, 'https://d.zenchef.com/landing-page/pardot-style.css'], check=True)
    shutil.copy(css, os.path.join(OUT, 'css/legal.css'))
    for p in LEGAL:
        s = read(os.path.join(DL, 'home_%s_.html' % p))
        s = s.replace('//d.zenchef.com/landing-page/pardot-style.css', '/css/legal.css')
        if p == 'mentions-legales':
            s = s.replace('Amazon Web Services EMEA SARL (AWS Europe), 4033 Citywest Avenue, Cooldown Commons, County Dublin, IRELAND https://aws.amazon.com',
                          '[Hébergeur à compléter une fois l\'hébergement choisi]')
            s = s.replace('Zenchef - 63 avenue de Villiers 75017 Paris – webmaster{at}zenchef.com', 'LUCCEA (Schnock)')
        write(os.path.join(OUT, p, 'index.html'), s)


def extras():
    write(os.path.join(OUT, 'CNAME'), 'www.schnock-restaurant.fr\n')
    write(os.path.join(OUT, 'robots.txt'), 'User-agent: *\nAllow: /\nSitemap: https://www.schnock-restaurant.fr/sitemap.xml\n')
    urls = ['', 'menus-carte/', 'photos/', 'privatisation/', 'informations-contact/']
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += ''.join('  <url><loc>https://www.schnock-restaurant.fr/%s</loc></url>\n' % u for u in urls)
    sm += '</urlset>\n'
    write(os.path.join(OUT, 'sitemap.xml'), sm)
    for root, _, files in os.walk(OUT):
        for f in files:
            if f.endswith('.html'):
                p = os.path.join(root, f)
                depth = os.path.relpath(p, OUT).count('/')
                write(p, relativize(absolute_jsonld(read(p)), depth))
    optimise_images()
    write(os.path.join(OUT, '404.html'), '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=/"><title>Schnock</title><a href="/">Schnock</a>\n')


if __name__ == '__main__':
    copy_assets()
    contact = build_pages()
    build_privatisation(contact)
    build_legal()
    extras()
    print('images:', len(img_map))
