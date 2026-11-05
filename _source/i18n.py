#!/usr/bin/env python3
"""Translated versions of the site: /en/, /es/, /it/, /zh/, /ja/.

French stays the main language at the root. This script runs on the published
site (after build.py): it reads each French page, swaps every visible string for
its translation from i18n/<lang>.json, rewrites the links for the deeper folder,
and adds the language switcher and hreflang tags to every version.

    python3 _source/i18n.py extract   # list the French strings to translate
    python3 _source/i18n.py build     # write the translated pages (fails on a missing string)
"""
import json, os, posixpath, re, sys

S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.dirname(S)
SITE = 'https://www.schnock-restaurant.fr/'
PAGES = ['', 'menus-carte/', 'photos/', 'privatisation/', 'informations-contact/']
LANGS = ['fr', 'en', 'es', 'it', 'zh', 'ja']
LABEL = {'fr': 'FR', 'en': 'EN', 'es': 'ES', 'it': 'IT', 'zh': '中文', 'ja': '日本語'}
HREFLANG = {'fr': 'fr', 'en': 'en', 'es': 'es', 'it': 'it', 'zh': 'zh-Hans', 'ja': 'ja'}
STAFF_NAME = {'en': 'anglais', 'es': 'espagnol', 'it': 'italien', 'zh': 'chinois', 'ja': 'japonais'}
OG_LOCALE = {'fr': 'fr_FR', 'en': 'en_GB', 'es': 'es_ES', 'it': 'it_IT', 'zh': 'zh_CN', 'ja': 'ja_JP'}
TRANSLATED_ATTRS = ('alt', 'title', 'placeholder', 'aria-label')
TOKEN = re.compile(r'<!--.*?-->|<script\b.*?</script>|<style\b.*?</style>|<[^>]+>|[^<]+', re.S | re.I)
LETTER = re.compile(r'[^\W\d_]', re.U)


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def page_file(page, lang='fr'):
    return os.path.join(ROOT, '' if lang == 'fr' else lang, page, 'index.html')


def page_url(page, lang='fr'):
    return SITE + ('' if lang == 'fr' else lang + '/') + page


# ---------- strings ----------
PRICE = re.compile(r'^\d+,\d\d EUR$')


def translatable(s):
    return bool(LETTER.search(s)) and not PRICE.match(norm(s))


def tag_strings(tag):
    """(attribute, value) pairs of a tag that carry visible or indexed text."""
    out = []
    for m in re.finditer(r'\s([\w:-]+)="([^"]*)"', tag):
        name, val = m.group(1), m.group(2)
        if name in TRANSLATED_ATTRS or name.startswith('data-msg'):
            out.append((name, m))
        elif name == 'value' and re.search(r'type="submit"', tag):
            out.append((name, m))
        elif name == 'content' and re.search(r'(name="description"|property="og:(title|description)")', tag):
            out.append((name, m))
    return out


def ld_strings(data, found):
    if isinstance(data, dict):
        for k, v in data.items():
            if k in ('name', 'text', 'description') and isinstance(v, str):
                found.append(v)
            else:
                ld_strings(v, found)
    elif isinstance(data, list):
        for v in data:
            ld_strings(v, found)


def body_strings(html):
    found = []
    for m in TOKEN.finditer(html):
        t = m.group(0)
        if t.startswith('<!--'):
            continue
        if t[:7].lower() == '<script':
            if 'application/ld+json' in t[:80]:
                ld_strings(json.loads(re.sub(r'^<script[^>]*>|</script>$', '', t)), found)
            continue
        if t[:6].lower() == '<style':
            continue
        if t.startswith('<'):
            found += [mm.group(2) for _, mm in tag_strings(t)]
        else:
            found.append(t)
    return [norm(s) for s in found if translatable(s)]


def extract():
    seen, order = {}, []
    for page in PAGES:
        for s in body_strings(strip_switcher(read(page_file(page)))):
            if s not in seen:
                seen[s] = page or 'accueil'
                order.append(s)
    keep = set(json.load(open(os.path.join(S, 'i18n', 'keep.json'), encoding='utf-8')))
    todo = [s for s in order if s not in keep]
    write(os.path.join(S, 'i18n', 'strings.fr.json'), json.dumps(todo, ensure_ascii=False, indent=1) + '\n')
    tables = load_tables()
    for lang in LANGS[1:]:
        missing = [s for s in todo if s not in tables[lang]]
        print('%s: %d strings, %d missing' % (lang, len(todo), len(missing)))
    print('French strings written to i18n/strings.fr.json')


# ---------- translation ----------
class Missing(Exception):
    pass


def load_tables():
    """i18n/t-*.json: lists of [fr, en, es, it, zh, ja] rows, one row per French string."""
    tables = {l: {} for l in LANGS[1:]}
    for f in sorted(os.listdir(os.path.join(S, 'i18n'))):
        if f.startswith('t-') and f.endswith('.json'):
            for row in json.load(open(os.path.join(S, 'i18n', f), encoding='utf-8')):
                assert len(row) == len(LANGS), 'bad row in %s: %s' % (f, row[0])
                for l, t in zip(LANGS[1:], row[1:]):
                    tables[l][norm(row[0])] = t
    return tables


def translator(lang, tables):
    table = tables[lang]
    keep = set(json.load(open(os.path.join(S, 'i18n', 'keep.json'), encoding='utf-8')))
    missing = set()

    def tr(s):
        key = norm(s)
        if not translatable(key) or key in keep:
            return s
        if key not in table:
            missing.add(key)
            return s
        lead = s[:len(s) - len(s.lstrip())]
        trail = s[len(s.rstrip()):]
        return lead + table[key] + trail
    tr.missing = missing
    return tr


def translate_ld(data, tr):
    if isinstance(data, dict):
        return {k: (tr(v) if k in ('name', 'text', 'description') and isinstance(v, str) else translate_ld(v, tr)) for k, v in data.items()}
    if isinstance(data, list):
        return [translate_ld(v, tr) for v in data]
    return data


def translate_html(html, tr):
    out = []
    for m in TOKEN.finditer(html):
        t = m.group(0)
        if t.startswith('<!--') or t[:6].lower() == '<style':
            out.append(t)
        elif t[:7].lower() == '<script':
            if 'application/ld+json' in t[:80]:
                head = re.match(r'<script[^>]*>', t).group(0)
                data = json.loads(t[len(head):-len('</script>')])
                t = head + '\n' + json.dumps(translate_ld(data, tr), ensure_ascii=False, indent=1) + '\n</script>'
            out.append(t)
        elif t.startswith('<'):
            for name, mm in reversed(tag_strings(t)):
                t = t[:mm.start(2)] + tr(mm.group(2)) + t[mm.end(2):]
            out.append(t)
        else:
            out.append(tr(t))
    return ''.join(out)


# ---------- links ----------
URL_ATTR = re.compile(r'''((?:href|src)=")([^"]*)(")|(url\(['"]?)([^'")]*)(['"]?\))''')


def localise_links(html, page, lang):
    """Relative links of a French page, rewritten for the same page in /<lang>/."""
    src_dir = '/' + page
    dst_dir = '/' + lang + '/' + page

    def fix(url):
        if not url or re.match(r'^([a-z][a-z0-9+.-]*:|#|//)', url, re.I):
            return url
        path, sep, frag = url.partition('#')
        path, qsep, query = path.partition('?')
        absolute = posixpath.normpath(posixpath.join(src_dir, path)) if path else src_dir.rstrip('/') or '/'
        if path.endswith('/') or path in ('', '.', './'):
            absolute = absolute.rstrip('/') + '/'
        if absolute.lstrip('/') in PAGES:
            absolute = '/' + lang + absolute
        rel = posixpath.relpath(absolute, dst_dir)
        if absolute.endswith('/'):
            rel = rel.rstrip('/') + '/' if rel != '.' else './'
        return rel + (qsep + query) + (sep + frag)

    def repl(m):
        if m.group(1):
            return m.group(1) + fix(m.group(2)) + m.group(3)
        return m.group(4) + fix(m.group(5)) + m.group(6)
    return URL_ATTR.sub(repl, html)


# ---------- language switcher & head ----------
def rel_link(page, from_lang, to_lang):
    here = '/' + ('' if from_lang == 'fr' else from_lang + '/') + page
    there = '/' + ('' if to_lang == 'fr' else to_lang + '/') + page
    rel = posixpath.relpath(there, here)
    return './' if rel == '.' else rel + '/'


def switcher(page, lang):
    items = ''.join('\n\t\t\t\t\t<li><a href="%s" hreflang="%s" lang="%s">%s</a></li>' % (rel_link(page, lang, l), HREFLANG[l], HREFLANG[l], LABEL[l])
                    for l in LANGS if l != lang)
    nav = ('<!-- Language -->\n\t\t\t<div class="dropdown-wrap drodown-wrap--lang" data-i18n="switcher">\n'
           '\t\t\t\t<span>%s <i class="fa fa-angle-down" aria-hidden="true"></i></span>\n'
           '\t\t\t\t<ul class="dropdown">%s\n\t\t\t\t</ul>\n\t\t\t</div>\n\t\t\t<!-- /Language -->') % (LABEL[lang], items)
    burger = ('<!-- Language -->\n\t\t<ul class="language-list" data-i18n="switcher">%s\n\t\t</ul>\n\t\t<!-- /Language -->') % ''.join(
        '\n\t\t\t<li><a class="btn-circle%s" href="%s" hreflang="%s" lang="%s">%s</a></li>' % (
            ' btn--std' if l == lang else ' btn--light', rel_link(page, lang, l), HREFLANG[l], HREFLANG[l], LABEL[l]) for l in LANGS)
    return nav, burger


def strip_switcher(html):
    """Drop a switcher left by a previous run, so the script can run again on its own output."""
    html = re.sub(r'<!-- Language -->\s*<div class="[^"]*" data-i18n="switcher">.*?<!-- /Language -->', '<!-- Language -->', html, flags=re.S)
    html = re.sub(r'<!-- Language -->\s*<ul class="[^"]*" data-i18n="switcher">.*?<!-- /Language -->\s*', '', html, flags=re.S)
    return html


def add_switcher(html, page, lang):
    html = strip_switcher(html)
    nav, burger = switcher(page, lang)
    # nav: the "Language" slot after the booking button; burger: before the social links
    html, n1 = re.subn(r'<!-- Language -->(\s*<!-- Toggle Menu -->)', lambda m: nav + m.group(1), html, count=1)
    html, n2 = re.subn(r'(</div>\s*)(\s*<!-- Social media -->)', lambda m: m.group(1) + burger + '\n\n\t\t' + m.group(2).lstrip(), html, count=1)
    assert n1 == 1 and n2 == 1, 'language slots not found in ' + page_file(page, lang)
    return html


def set_head(html, page, lang):
    html = re.sub(r'\n?[ \t]*<link rel="alternate" hreflang="[^"]*" href="[^"]*" />', '', html)
    html = re.sub(r'\n?[ \t]*<meta property="og:locale(:alternate)?" content="[^"]*" />', '', html)
    alts = ''.join('\n<link rel="alternate" hreflang="%s" href="%s" />' % (HREFLANG[l], page_url(page, l)) for l in LANGS)
    alts += '\n<link rel="alternate" hreflang="x-default" href="%s" />' % page_url(page)
    html = re.sub(r'<link rel="canonical" href="[^"]*" />', lambda m: '<link rel="canonical" href="%s" />%s' % (page_url(page, lang), alts), html, count=1)
    html = re.sub(r'<meta property="og:url" content="[^"]*" />', lambda m: '<meta property="og:url" content="%s" />' % page_url(page, lang), html, count=1)
    locales = '\n<meta property="og:locale" content="%s" />' % OG_LOCALE[lang] + ''.join(
        '\n<meta property="og:locale:alternate" content="%s" />' % OG_LOCALE[l] for l in LANGS if l != lang)
    html = re.sub(r'(<meta property="og:type" content="[^"]*" />)', lambda m: m.group(1) + locales, html, count=1)
    if lang != 'fr':
        html = re.sub(r'(<html[^>]*\blang=")fr(")', r'\g<1>%s\2' % HREFLANG[lang], html)
        html = html.replace('window.lang = "fr";', 'window.lang = "%s";' % lang)
        html = html.replace('data-lang="fr"', 'data-lang="%s"' % lang)
        html = re.sub(r'([?&]lang=)fr\b', r'\g<1>%s' % lang, html)
        # booking widget in the visitor's language; legal pages exist only in French
        html = re.sub(r'"inLanguage": "fr"', '"inLanguage": "%s"' % HREFLANG[lang], html)
    return html


def sitemap():
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    for page in PAGES:
        for lang in LANGS:
            sm += '  <url>\n    <loc>%s</loc>\n' % page_url(page, lang)
            sm += ''.join('    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>\n' % (HREFLANG[l], page_url(page, l)) for l in LANGS)
            sm += '    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>\n  </url>\n' % page_url(page)
    write(os.path.join(ROOT, 'sitemap.xml'), sm + '</urlset>\n')


def localise_forms(html, lang):
    """Form answers reach the team in French, with the visitor's language attached."""
    html = re.sub(r'<option( selected)?>([^<]+)</option>', lambda m: '<option value="%s"%s>%s</option>' % (norm(m.group(2)), m.group(1) or '', m.group(2)), html)
    return re.sub(r'(<form\b[^>]*>)', lambda m: m.group(1) + '\n\t<input type="hidden" name="langue" value="%s">' % STAFF_NAME[lang], html)


def build():
    failed = {}
    tables = load_tables()
    for page in PAGES:
        fr = strip_switcher(read(page_file(page)))
        for lang in LANGS[1:]:
            tr = translator(lang, tables)
            html = translate_html(localise_forms(fr, lang), tr)
            html = localise_links(html, page, lang)
            html = set_head(html, page, lang)
            html = add_switcher(html, page, lang)
            if tr.missing:
                failed.setdefault(lang, set()).update(tr.missing)
            write(page_file(page, lang), html)
        write(page_file(page), add_switcher(set_head(fr, page, 'fr'), page, 'fr'))
    sitemap()
    if failed:
        for lang, miss in failed.items():
            print('%s: %d missing strings, e.g. %s' % (lang, len(miss), sorted(miss)[:3]))
        sys.exit(1)
    print('ok: %d pages x %d languages' % (len(PAGES), len(LANGS)))


if __name__ == '__main__':
    {'extract': extract, 'build': build}[sys.argv[1] if len(sys.argv) > 1 else 'build']()
