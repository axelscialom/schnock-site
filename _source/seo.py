#!/usr/bin/env python3
"""Réglages d'indexation Google, à lancer en dernier (après build.py puis i18n.py build).

    python3 _source/seo.py

- Pages légales : lang, balise canonique, lien de retour vers le site (maillage).
- Anciennes adresses de l'ancien site Zenchef : une page de redirection immédiate
  (meta refresh 0 + canonique), que Google traite comme une redirection permanente.
  GitHub Pages ne permet pas les vraies 301 ; c'est l'équivalent accepté par Google.
- 404.html : vraie page « introuvable » (plus de renvoi caché vers l'accueil, que
  Google classe en « soft 404 »), avec liens vers les pages principales.
- sitemap.xml : ajoute <lastmod>.

Pour rediriger une nouvelle ancienne adresse, l'ajouter dans REDIRECTS ci-dessous.
Le script est idempotent.
"""
import datetime
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.schnock-restaurant.fr'
LANGS = ['en', 'es', 'it', 'zh', 'ja']                     # langues publiées hors FR
OLD_LANGS = ['de', 'nl', 'pt', 'ru', 'ko', 'ar', 'da', 'sv', 'no', 'el', 'cs', 'fr']  # langues Zenchef non reprises
PAGES = ['menus-carte', 'photos', 'informations-contact', 'privatisation']
LEGAL = ['mentions-legales', 'politique-de-confidentialite', 'politique-cookies', 'accessibilite']

# ancienne adresse -> nouvelle adresse (chemins, avec / final)
REDIRECTS = {
    '/accueil/': '/',
    '/home/': '/',
    '/menus/': '/menus-carte/',
    '/menu/': '/menus-carte/',
    '/carte/': '/menus-carte/',
    '/la-carte/': '/menus-carte/',
    '/nos-menus/': '/menus-carte/',
    '/galerie/': '/photos/',
    '/galerie-photos/': '/photos/',
    '/contact/': '/informations-contact/',
    '/informations/': '/informations-contact/',
    '/infos-pratiques/': '/informations-contact/',
    '/reservation/': '/informations-contact/',
    '/reserver/': '/informations-contact/',
    '/evenements/': '/privatisation/',
    '/privatisations/': '/privatisation/',
    '/privatisation-evenements/': '/privatisation/',
    '/groupes/': '/privatisation/',
    '/cgu/': '/mentions-legales/',
    '/confidentialite/': '/politique-de-confidentialite/',
    '/cookies/': '/politique-cookies/',
}
# adresses exactes relevées dans Search Console (export du 2026-11-12) : slugs traduits de Zenchef
_EXACT = {
    '/': ['/unsere-restaurants/', '/onze-restaurants/', '/nl/onze-restaurants/', '/vores-restauranter/',
          '/reserver-une-table/', '/da/bestil-et-bord/', '/ru/zakazat-stolik/', '/el/kleiste-ena-trapezi/',
          '/de/einen-tisch-reservieren/', '/cs/rezervovat-tabulku/', '/sv/boka-bord/', '/nl/boek-een-tafel/'],
    '/en/': ['/our-restaurants/', '/en/book-a-table/'],
    '/es/': ['/nuestros-restaurantes/', '/es/reservar-una-mesa/'],
    '/it/': ['/i-nostri-ristoranti/', '/it/prenotare-un-tavolo/'],
    '/menus-carte/': ['/menús/', '/menus-karte/', '/sv/menyer/', '/no/menyer/', '/da/menuer/'],
    '/es/menus-carte/': ['/es/menús/'],
    '/photos/': ['/bilder/', '/fotografie/', '/foton/', '/foto/', '/fotos/', '/fotografias/'],
    '/es/photos/': ['/es/fotografias/'],
    '/informations-contact/': ['/adress-kontakt/', '/kontaktadresse/', '/adresse-kontakt/', '/adresa-kontakt/',
                               '/adres-contact/', '/endereco-contacto/', '/kontaktinformationen/',
                               '/dirección-contacto/', '/direccion-de-contacto/'],
    '/en/informations-contact/': ['/address-contact/'],
    '/it/informations-contact/': ['/informazioni-contatti/'],
    '/es/informations-contact/': ['/es/dirección-contacto/', '/es/direccion-de-contacto/'],
    '/politique-cookies/': ['/zh/cookie-policy/', '/el/cookie-policy/', '/no/cookie-policy/', '/ru/cookie-policy/',
                            '/ja/cookie-policy/', '/en/cookie-policy/', '/es/politica-cookies/', '/nl/cookie-beleid/'],
    '/accessibilite/': ['/no/tilgjengelighet/', '/it/accessibilita/'],
    '/politique-de-confidentialite/': ['/el/politiki-aporritou/', '/cs/zasady-ochrony-soukromi/'],
}
for _new, _olds in _EXACT.items():
    for _old in _olds:
        REDIRECTS[_old] = _new
# Zenchef publiait chaque page avec un slug traduit, dans ~18 langues, avec ou sans préfixe
# de langue (/fotos/, /es/fotos/, /cs/nase-restaurace/…). Google en découvre au fil de l'eau :
# on redirige toute la grille (slug x préfixe) plutôt que d'attendre les 404 une par une.
SLUGS = {
    'home': ['nos-restaurants', 'our-restaurants', 'unsere-restaurants', 'nuestros-restaurantes',
             'i-nostri-ristoranti', 'onze-restaurants', 'os-nossos-restaurantes', 'nossos-restaurantes',
             'vores-restauranter', 'våra-restauranger', 'vara-restauranger', 'våre-restauranter',
             'vare-restauranter', 'naše-restaurace', 'nase-restaurace', 'nasze-restauracje',
             'nashi-restorany', 'ta-estiatoria-mas', 'ta-estiatoriá-mas', 'accueil', 'home', 'inicio', 'startseite',
             'reserver-une-table', 'book-a-table', 'einen-tisch-reservieren', 'tisch-reservieren',
             'reservar-una-mesa', 'reservar-uma-mesa', 'prenotare-un-tavolo', 'boek-een-tafel',
             'boka-bord', 'bestil-et-bord', 'bestill-et-bord', 'zakazat-stolik', 'kleiste-ena-trapezi',
             'rezervovat-tabulku', 'rezervovat-stul', 'zarezerwuj-stolik', 'reservation', 'reserver', 'booking'],
    'menus-carte': ['menus', 'menu', 'menús', 'menues', 'menus-karte', 'menu-karte', 'speisekarte', 'karte',
                    'menus-carta', 'menu-carta', 'carta', 'menus-y-carta', 'menu-e-carta', 'menu-kaart',
                    'menus-kaart', 'menukaart', 'kaart', 'ementas', 'menus-e-carta', 'cardapio', 'cardápio',
                    'menyer', 'meny', 'menuer', 'menukort', 'menyu', 'menou', 'menoú', 'jidelni-listek',
                    'jídelní-lístek', 'nabidka', 'karta', 'carte', 'la-carte', 'nos-menus', 'our-menus'],
    'photos': ['fotos', 'foto', 'fotografie', 'fotografias', 'fotografías', 'fotografia', 'fotografies',
               'fotografii', 'bilder', 'billeder', 'foton', 'fotky', 'zdjecia', 'zdjęcia', 'galerie', 'gallery',
               'galeria', 'galleria', 'galerij', 'pictures', 'images'],
    'informations-contact': ['address-contact', 'adresse-kontakt', 'adress-kontakt', 'kontaktadresse',
                             'adresa-kontakt', 'adres-contact', 'adres-kontakt', 'endereco-contacto',
                             'endereço-contacto', 'endereco-contato', 'kontaktinformationen', 'informazioni-contatti',
                             'indirizzo-contatto', 'indirizzo-contatti', 'direccion-de-contacto',
                             'dirección-de-contacto', 'direccion-contacto', 'dirección-contacto',
                             'adresse-contact', 'adresse-og-kontakt', 'adress-och-kontakt', 'adresa-kontakty',
                             'adresa-a-kontakt', 'dieuthynsi-epikoinonia', 'contact', 'contacto', 'contato',
                             'contatti', 'kontakt', 'informations', 'infos-pratiques', 'acces', 'access'],
    'privatisation': ['privatisations', 'evenements', 'events', 'eventos', 'eventi', 'groupes', 'groups',
                      'privatisation-evenements', 'private-events', 'privatization'],
    'politique-cookies': ['cookie-policy', 'cookies-policy', 'cookies', 'politica-cookies', 'politica-de-cookies',
                          'política-de-cookies', 'politica-dei-cookie', 'cookie-richtlinie', 'cookie-richtlinien',
                          'cookie-beleid', 'cookiebeleid', 'cookiepolitik', 'cookie-politik', 'cookiepolicy',
                          'zasady-cookies', 'zasady-pouzivani-cookies', 'politika-cookie', 'politiki-cookies'],
    'politique-de-confidentialite': ['privacy-policy', 'privacy', 'datenschutz', 'datenschutzerklarung',
                                     'datenschutzrichtlinie', 'politica-de-privacidad', 'política-de-privacidad',
                                     'politica-de-privacidade', 'informativa-sulla-privacy', 'privacybeleid',
                                     'privatlivspolitik', 'integritetspolicy', 'personvernerklaering',
                                     'personvern', 'politika-konfidencialnosti', 'politiki-aporritou',
                                     'zasady-ochrony-soukromi', 'polityka-prywatnosci', 'confidentialite'],
    'accessibilite': ['accessibility', 'barrierefreiheit', 'accesibilidad', 'acessibilidade', 'accessibilita',
                      'accessibilità', 'toegankelijkheid', 'tilgaengelighed', 'tilgængelighed', 'tillganglighet',
                      'tillgänglighet', 'tilgjengelighet', 'pristupnost', 'přístupnost', 'dostupnost',
                      'dostepnosc', 'prosvasimotita'],
    'mentions-legales': ['legal-notice', 'legal-notices', 'imprint', 'impressum', 'aviso-legal', 'note-legali',
                         'wettelijke-vermeldingen', 'juridisk-meddelelse', 'juridiska-meddelanden',
                         'juridisk-informasjon', 'pravni-upozorneni', 'nota-prawna', 'cgu', 'cgv'],
}
ALL_PREFIXES = [''] + LANGS + OLD_LANGS + ['pl']
_ROOT_LANG = {'our-restaurants': 'en', 'book-a-table': 'en', 'address-contact': 'en', 'our-menus': 'en',
              'nuestros-restaurantes': 'es', 'reservar-una-mesa': 'es', 'direccion-de-contacto': 'es',
              'dirección-de-contacto': 'es', 'fotografias': 'es', 'fotografías': 'es',
              'i-nostri-ristoranti': 'it', 'prenotare-un-tavolo': 'it', 'informazioni-contatti': 'it'}
for _page, _slugs in SLUGS.items():
    _is_legal = _page in LEGAL
    for _prefix in ALL_PREFIXES:
        for _slug in _slugs:
            _old = '/%s/' % _slug if not _prefix else '/%s/%s/' % (_prefix, _slug)
            if _old in REDIRECTS:
                continue
            _lang = _prefix if _prefix in LANGS else ('en' if _prefix and _prefix != 'fr' else _ROOT_LANG.get(_slug, ''))
            if _is_legal:
                _new = '/%s/' % _page
            else:
                _base = '/%s' % _lang if _lang else ''
                _new = '%s/' % _base if _page == 'home' else '%s/%s/' % (_base, _page)
            REDIRECTS[_old] = _new
# pages légales traduites par Zenchef : la version française seule existe désormais
for l in LANGS:
    for p in LEGAL:
        REDIRECTS['/%s/%s/' % (l, p)] = '/%s/' % p
# langues de l'ancien site non reprises : vers la version anglaise (le français pour /fr/)
for l in OLD_LANGS:
    base = '' if l == 'fr' else '/en'
    REDIRECTS['/%s/' % l] = base + '/'
    for p in PAGES:
        REDIRECTS['/%s/%s/' % (l, p)] = '%s/%s/' % (base, p)
    for p in LEGAL:
        REDIRECTS['/%s/%s/' % (l, p)] = '/%s/' % p

STUB = '''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Schnock</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={url}">
<script>location.replace("{url}" + location.search + location.hash)</script>
</head>
<body><p>Cette page a déménagé : <a href="{url}">{url}</a></p></body>
</html>
'''

NOT_FOUND = '''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Page introuvable | Schnock</title>
<link rel="icon" href="/favicon.ico">
<style>
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#1d2a3a;color:#f4efe6;font-family:Georgia,serif;text-align:center;padding:16px;box-sizing:border-box}
img{width:140px;height:auto;margin-bottom:24px}
h1{font-weight:normal;font-size:28px;margin:0 0 12px}
p{margin:0 0 24px;opacity:.85}
nav a{display:inline-block;margin:6px 10px;color:#cc9933;text-decoration:none;border-bottom:1px solid #cc9933}
</style>
</head>
<body>
<main>
<img src="/images/logo-schnock-blanc.png" alt="Schnock">
<h1>Cette page n'existe plus</h1>
<p>Le site du Schnock a fait peau neuve. Retrouvez-nous ici :</p>
<nav>
<a href="/">Accueil</a>
<a href="/menus-carte/">Menus &amp; carte</a>
<a href="/privatisation/">Privatisation</a>
<a href="/photos/">Photos</a>
<a href="/informations-contact/">Infos &amp; contact</a>
</nav>
</main>
</body>
</html>
'''

BACK_LINKS = ('<nav class="legal-back" style="margin:0 0 24px"><a href="/">&larr; Schnock, restaurant Paris 17e</a>'
              ' &middot; <a href="/menus-carte/">Menus &amp; carte</a>'
              ' &middot; <a href="/privatisation/">Privatisation</a>'
              ' &middot; <a href="/informations-contact/">Contact</a></nav>')


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def legal_pages():
    for p in LEGAL:
        f = os.path.join(ROOT, p, 'index.html')
        s = open(f, encoding='utf-8').read()
        s = re.sub(r'^<html>', '<html lang="fr">', s, count=1, flags=re.M)
        if 'rel="canonical"' not in s:
            s = s.replace('</title>', '</title>\n    <link rel="canonical" href="%s/%s/" />' % (SITE, p), 1)
        if 'legal-back' not in s:
            s = re.sub(r'(<body[^>]*>\s*<main[^>]*>)', r'\1\n' + BACK_LINKS, s, count=1)
        write(f, s)


def redirects():
    n = 0
    for old, new in REDIRECTS.items():
        f = os.path.join(ROOT, old.strip('/'), 'index.html')
        if os.path.exists(f) and 'http-equiv="refresh"' not in open(f, encoding='utf-8').read():
            continue  # vraie page du site : on n'y touche pas
        target = SITE + new
        assert os.path.exists(os.path.join(ROOT, new.strip('/'), 'index.html')), new
        write(f, STUB.format(url=target))
        n += 1
    return n


def sitemap():
    f = os.path.join(ROOT, 'sitemap.xml')
    s = open(f, encoding='utf-8').read()
    today = datetime.date.today().isoformat()
    s = re.sub(r'\s*<lastmod>[^<]*</lastmod>', '', s)
    s = re.sub(r'(<loc>[^<]+</loc>)', r'\1\n    <lastmod>%s</lastmod>' % today, s)
    write(f, s)


if __name__ == '__main__':
    legal_pages()
    n = redirects()
    write(os.path.join(ROOT, '404.html'), NOT_FOUND)
    sitemap()
    print('ok: %d redirections, pages légales, 404, sitemap' % n)
