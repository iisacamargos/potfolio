# Otimização de imagens: para cada <img> JPG/PNG das páginas em português,
# gera versões WebP (tamanho original + 1200px de largura) e troca a tag por
# <picture> com srcset, para o navegador baixar o arquivo mais leve que serve.
# Roda no tools/build.py antes do i18n.py (a versão em inglês herda tudo).
import os, re, glob
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMALL = 1200  # largura da versão menor (celular / telas comuns)

def webp(src_rel, width=None):
    """Gera (se faltar) e devolve o caminho relativo do WebP."""
    base, _ = os.path.splitext(src_rel)
    out = f'{base}-{width}.webp' if width else f'{base}.webp'
    dst = os.path.join(ROOT, 'assets/img', out)
    if not os.path.exists(dst):
        im = Image.open(os.path.join(ROOT, 'assets/img', src_rel))
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        if width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(dst, 'WEBP', quality=80, method=6)
    return out

def sizes_for(tag, ctx):
    g = ctx.rfind('<div class="media-grid')
    if g != -1 and ctx.rfind('</div>') < g:
        return '(max-width: 700px) 100vw, 50vw'
    tile = ctx.rfind('<a class="work-tile')
    if tile != -1 and 'work-tile--feature' not in ctx[tile:tile + 60]:
        return '(max-width: 700px) 100vw, 50vw'
    return '(max-width: 1728px) 100vw, 1728px'

def process(path):
    h = open(path).read()
    out, pos = [], 0
    for m in re.finditer(r'<img\b[^>]*\bsrc="((?:\.\./)?assets/img/([^"]+\.(?:jpg|png)))"[^>]*>', h):
        start = m.start()
        # já otimizada (dentro de <picture> com webp)?
        before = h[max(0, start - 400):start]
        if before.rstrip().endswith('>') and re.search(r'<source type="image/webp"[^>]*>\s*$', before):
            continue
        prefix = m.group(1)[:-len(m.group(2))]
        rel = m.group(2)
        w = Image.open(os.path.join(ROOT, 'assets/img', rel)).width
        full = webp(rel)
        if w > SMALL + 100:
            small = webp(rel, SMALL)
            srcset = f'{prefix}{small} {SMALL}w, {prefix}{full} {w}w'
        else:
            srcset = f'{prefix}{full} {w}w'
        ctx = h[max(0, start - 600):start]
        tag = m.group(0)
        if 'loading="lazy"' in tag and 'decoding=' not in tag:
            tag = tag.replace('<img ', '<img decoding="async" ', 1)
        pic = (f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes_for(tag, ctx)}">'
               f'{tag}</picture>')
        out.append(h[pos:start]); out.append(pic); pos = m.end()
    out.append(h[pos:])
    new = ''.join(out)
    if new != h:
        open(path, 'w').write(new)

for p in [os.path.join(ROOT, 'index.html')] + sorted(glob.glob(os.path.join(ROOT, 'projetos/*.html'))):
    process(p)
