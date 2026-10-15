# Gera a versão em inglês (/en/) a partir das páginas em português e
# coloca o seletor de idioma + hreflang nas duas versões.
# Roda sozinho no fim do tools/build.py.
import re, os, json, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en import EN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://isadoracamargo.com.br'
SLUGS = ['novo-traco', 'orquestra-novo-traco', 'nt-records', 'nt-sessions', 'latinjazz-brazil',
         'anju-mace', 'aquarie', 'be-brave', 'funnel-builder']
IDS = {'projetos': 'projects', 'sobre': 'about', 'contato': 'contact'}

FLAG_BR = '<span class="flag flag--br" aria-hidden="true"></span>'
FLAG_US = '<span class="flag flag--us" aria-hidden="true"></span>'

def switcher(lang, pt_href, en_href):
    cur = FLAG_BR if lang == 'pt' else FLAG_US
    label = 'Idioma: Português (Brasil)' if lang == 'pt' else 'Language: English'
    pt_cur = ' aria-current="true"' if lang == 'pt' else ''
    en_cur = ' aria-current="true"' if lang == 'en' else ''
    return (f'<details class="lang">\n'
            f'          <summary aria-label="{label}">{cur}</summary>\n'
            f'          <div class="lang-menu">\n'
            f'            <a href="{pt_href}" hreflang="pt-BR" lang="pt-BR"{pt_cur}>{FLAG_BR}Português</a>\n'
            f'            <a href="{en_href}" hreflang="en" lang="en"{en_cur}>{FLAG_US}English</a>\n'
            f'          </div>\n'
            f'        </details>')

def alternates(pt_url, en_url):
    return (f'  <link rel="alternate" hreflang="pt-BR" href="{pt_url}">\n'
            f'  <link rel="alternate" hreflang="en" href="{en_url}">\n'
            f'  <link rel="alternate" hreflang="x-default" href="{pt_url}">\n')

def clean(h):
    h = re.sub(r'\s*<details class="lang">.*?</details>', '', h, flags=re.S)
    h = re.sub(r'  <link rel="alternate" hreflang="[^"]+" href="[^"]+">\n', '', h)
    return h

def decorate(h, lang, pt_href, en_href, pt_url, en_url):
    h = clean(h)
    h = h.replace('  <link rel="canonical"', alternates(pt_url, en_url) + '  <link rel="canonical"', 1)
    # seletor no fim do menu do topo
    h = re.sub(r'(<header class="topbar">.*?<nav>.*?)(\n      </nav>)',
               lambda m: m.group(1) + '\n        ' + switcher(lang, pt_href, en_href) + m.group(2),
               h, count=1, flags=re.S)
    return h

missing = set()
LOOKS_PT = re.compile(r'[ãõçáéíóúâêô]|\b(de|da|do|em|para|com|uma|um|os|as|que)\b', re.I)

def tr(s):
    return EN.get(s)

def translate_text(h):
    # protege <script> e <style>
    keep = []
    def stash(m):
        keep.append(m.group(0)); return f'\x00{len(keep)-1}\x00'
    h = re.sub(r'<(script|style)\b.*?</\1>', stash, h, flags=re.S)
    def txt(m):
        raw = m.group(1)
        core = raw.strip()
        if not core or not re.search(r'[A-Za-zÀ-ú]', core):
            return m.group(0)
        t = tr(core) or tr(html.unescape(core))
        if t is None:
            if LOOKS_PT.search(html.unescape(core)): missing.add(core)
            return m.group(0)
        lead = raw[:len(raw) - len(raw.lstrip())]
        trail = raw[len(raw.rstrip()):]
        return '>' + lead + t + trail + '<'
    h = re.sub(r'>([^<>]+)<', txt, h)
    def attr(m):
        name, val = m.group(1), m.group(2)
        un = html.unescape(val)
        t = tr(un)
        if t is None:
            if name != 'content' and LOOKS_PT.search(un): missing.add(un)
            return m.group(0)
        return f' {name}="{html.escape(html.unescape(t), quote=True)}"'
    h = re.sub(r' (alt|aria-label|title|data-cursor|content)="([^"]*)"', attr, h)
    return re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], h)

def translate_jsonld(h, url_map):
    def walk(o):
        if isinstance(o, dict):
            return {k: (url_map(v) if k in ('url', 'item') and isinstance(v, str)
                        else 'en' if k == 'inLanguage' and v == 'pt-BR'
                        else walk(v)) for k, v in o.items()}
        if isinstance(o, list): return [walk(v) for v in o]
        if isinstance(o, str): return EN.get(o, o)
        return o
    def blk(m):
        data = walk(json.loads(m.group(1)))
        return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n  </script>'
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', blk, h, flags=re.S)

def pt_to_en_url(u):
    if u == BASE + '/': return BASE + '/en/'
    return u.replace(BASE + '/projetos/', BASE + '/en/projects/')

def common_en(h):
    h = h.replace('<html lang="pt-BR">', '<html lang="en">')
    h = h.replace('<meta property="og:locale" content="pt_BR">',
                  '<meta property="og:locale" content="en_US">\n  <meta property="og:locale:alternate" content="pt_BR">')
    h = re.sub(r'(rel="canonical" href=")([^"]+)"', lambda m: m.group(1) + pt_to_en_url(m.group(2)) + '"', h)
    h = re.sub(r'(property="og:url" content=")([^"]+)"', lambda m: m.group(1) + pt_to_en_url(m.group(2)) + '"', h)
    for pt, en in IDS.items():
        h = h.replace(f'id="{pt}"', f'id="{en}"').replace(f'#{pt}"', f'#{en}"')
    h = translate_jsonld(h, pt_to_en_url)
    return translate_text(h)

def main():
    os.makedirs(f'{ROOT}/en/projects', exist_ok=True)
    # home
    p = f'{ROOT}/index.html'
    h = clean(open(p).read())
    pt = decorate(h, 'pt', './', 'en/', BASE + '/', BASE + '/en/')
    open(p, 'w').write(pt)
    en = common_en(h)
    en = re.sub(r'(?<![\w/.])assets/', '../assets/', en)
    en = en.replace('href="favicon.ico"', 'href="../favicon.ico"')
    en = en.replace('href="projetos/', 'href="projects/')
    en = decorate(en, 'en', '../', './', BASE + '/', BASE + '/en/')
    open(f'{ROOT}/en/index.html', 'w').write(en)
    # cases
    for s in SLUGS:
        p = f'{ROOT}/projetos/{s}.html'
        h = clean(open(p).read())
        pt_url, en_url = f'{BASE}/projetos/{s}.html', f'{BASE}/en/projects/{s}.html'
        open(p, 'w').write(decorate(h, 'pt', f'{s}.html', f'../en/projects/{s}.html', pt_url, en_url))
        en = common_en(h)
        en = en.replace('../assets/', '../../assets/').replace('"../favicon.ico"', '"../../favicon.ico"')
        en = decorate(en, 'en', f'../../projetos/{s}.html', f'{s}.html', pt_url, en_url)
        open(f'{ROOT}/en/projects/{s}.html', 'w').write(en)
    # sitemap com as duas línguas
    urls = [('', 'en/')] + [(f'projetos/{s}.html', f'en/projects/{s}.html') for s in SLUGS]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for a, b in urls:
        for loc in (a, b):
            out += ['  <url>', f'    <loc>{BASE}/{loc}</loc>',
                    f'    <xhtml:link rel="alternate" hreflang="pt-BR" href="{BASE}/{a}"/>',
                    f'    <xhtml:link rel="alternate" hreflang="en" href="{BASE}/{b}"/>',
                    '  </url>']
    out.append('</urlset>')
    open(f'{ROOT}/sitemap.xml', 'w').write('\n'.join(out) + '\n')
    if missing:
        print('SEM TRADUÇÃO:'); [print('  ', m) for m in sorted(missing)]
    else:
        print('ok, tudo traduzido')

main()
