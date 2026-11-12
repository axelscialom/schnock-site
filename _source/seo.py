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
OLD_LANGS = ['de', 'nl', 'pt', 'ru', 'ko', 'ar', 'fr']      # langues Zenchef non reprises
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
            raise SystemExit('refus : %s est une vraie page, pas une ancienne adresse' % old)
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
