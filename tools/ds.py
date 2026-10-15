# Componentes padrão do sistema: paleta (.cs) e tipografia (.ts)
import re, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rgb(h):
    h=h.lstrip('#');return ' '.join(str(int(h[i:i+2],16)) for i in (0,2,4))
def colors(brand,items,note='HEX · RGB',cols=None):
    """items: dicts name, hex, [cmyk], [pantone], [pair=(name,hex,pantone)]"""
    lis=''
    for c in items:
        hx=c['hex'].upper().lstrip('#')
        st=f'--c:#{hx}'
        pair=c.get('pair')
        if pair: st+=f';--c2:#{pair[1].upper().lstrip("#")}'
        codes=f'<dt>HEX</dt><dd>#{hx}</dd><dt>RGB</dt><dd>{rgb(hx)}</dd>'
        if c.get('cmyk'): codes+=f'<dt>CMYK</dt><dd>{c["cmyk"]}</dd>'
        if c.get('pantone'): codes+=f'<dt>Pantone</dt><dd>{c["pantone"]}</dd>'
        pr=''
        if pair:
            p2=pair[1].upper().lstrip('#')
            pr=f'\n          <p class="cs-pair"><i style="--c:#{p2}"></i><span>Par: {pair[0]}<br>#{p2}{" · "+pair[2] if len(pair)>2 and pair[2] else ""}</span></p>'
        lis+=f'''
        <li class="cs-item{' cs-item--pair' if pair else ''}">
          <div class="cs-chip" style="{st}"></div>
          <p class="cs-name">{c['name']}</p>
          <dl class="cs-codes">{codes}</dl>{pr}
        </li>'''
    n=len(items)
    unit='pares' if any(c.get('pair') for c in items) else 'cores'
    return f'''
    <div class="ds" role="group" aria-label="Paleta de cores da {brand}">
      <div class="ds-head"><span class="caps">Paleta</span><span class="caps">{n:02d} {unit} · {note}</span></div>
      <ul class="cs" style="--n:{cols or min(n,6)}">{lis}
      </ul>
    </div>
'''
def _svg(name,label):
    s=open(f'{ROOT}/assets/img/type/{name}.svg').read().strip()
    s=re.sub(r'<svg width="[\d.]+" height="[\d.]+"',f'<svg class="ts-svg" role="img" aria-label="{label}"',s,1)
    s=s.replace(' fill="none"','',1)
    return s.replace('\n','')
def types(brand,items):
    """items: dicts family, use, style, weights, and svg=name or live=css font-family"""
    rows=''
    for t in items:
        if t.get('svg'): spec=_svg(t['svg'],f'Nome da fonte {t["family"]} escrito nela mesma')
        else: spec=f'<p class="ts-live" style="font-family:{t["live"]};font-weight:{t.get("w",400)}">{t.get("sample",t["family"])}</p>'
        rows+=f'''
      <div class="ts-row">
        <div class="ts-spec">{spec}</div>
        <dl class="ts-meta">
          <div><dt>Família</dt><dd>{t['family']}</dd></div>
          <div><dt>Uso</dt><dd>{t['use']}</dd></div>
          <div><dt>Estilo</dt><dd>{t['style']}</dd></div>
          <div><dt>Pesos</dt><dd>{t['weights']}</dd></div>
        </dl>
      </div>'''
    n=len(items)
    return f'''
    <div class="ds" role="group" aria-label="Tipografia da {brand}">
      <div class="ds-head"><span class="caps">Tipografia</span><span class="caps">{n:02d} {'famílias' if n>1 else 'família'}</span></div>{rows}
    </div>
'''

# ---------- dados das marcas ----------
NT_PAIRS=[
 dict(name='Cloud Dancer',hex='F0EFEB',pantone='11-4201 TCX',pair=('My Soul','020305','19-4010 TCX')),
 dict(name='Orange Tiger',hex='F96714',pantone='16-1358 TCX',pair=('My Soul','020305','19-4010 TCX')),
 dict(name='Red Pink',hex='FB2A54',pair=('Rose Quartz','F6CAC9','13-1520 TCX')),
 dict(name='Tropical Breeze',hex='87CDE7',pantone='13-4307 TCX',pair=('Ocean Spray','02547A','7706 C')),
 dict(name='Wild Lime',hex='C2D363',pantone='13-0540 TCX',pair=('First Tree','00733C','18-6031 TCX')),
 dict(name='Illuminating',hex='F6EA60',pantone='13-0647 TCX',pair=('Buttercup','FEE13B','12-0752 TCX')),
]
UNIVERS=dict(family='Univers Next Pro',svg='univers',use='Títulos, destaques e mistura de pesos na mesma palavra',style='Grotesca',weights='Ultra Light, Thin, Light, Regular, Medium, Bold, Heavy, Black, Extra Black')
ROSLINDALE=dict(family='Roslindale Display Narrow',svg='roslindale',use='Títulos editoriais',style='Serifa display estreita',weights='Light, Regular, Medium, SemiBold')
MARGEM=dict(family='Margem',svg='margem',use='Texto corrido e pequenos detalhes',style='Sem serifa',weights='Medium, Bold, Extra Bold, Black')

NT_COLORS=[
 dict(name='Cloud Dancer',hex='F0EFEB',pantone='11-4201 TCX'),
 dict(name='My Soul',hex='020305',pantone='19-4010 TCX'),
 dict(name='Orange Tiger',hex='F96714',pantone='16-1358 TCX'),
 dict(name='Red Pink',hex='FB2A54'),
 dict(name='Tropical Breeze',hex='87CDE7',pantone='13-4307 TCX'),
 dict(name='First Tree',hex='00733C',pantone='18-6031 TCX'),
 dict(name='Illuminating',hex='F6EA60',pantone='13-0647 TCX'),
]

# ---------- Recorte vertical (4:5) para celular ----------
# Desligado a pedido: as imagens aparecem iguais no celular e no desktop.
# (Formato: {'pasta/imagem.jpg': centro_x} gera uma versão 4:5 para celular.)
MOBILE = {}
# vídeos horizontais com o assunto no centro: no celular viram 4:5 (object-fit)
MOBILE_VIDEO = set()

def mcrop(src):
    """Gera assets/img/<nome>-m.jpg (4:5) se ainda não existe; devolve o caminho relativo."""
    from PIL import Image
    fx = MOBILE[src]
    base, ext = os.path.splitext(src)
    out = f'{base}-m.jpg'
    dst = f'{ROOT}/assets/img/{out}'
    if not os.path.exists(dst):
        im = Image.open(f'{ROOT}/assets/img/{src}').convert('RGB')
        w, h = im.size
        cw = round(h * 4 / 5)
        x = min(max(round(w * fx - cw / 2), 0), w - cw)
        im.crop((x, 0, x + cw, h)).save(dst, quality=82, optimize=True, progressive=True)
    return out

def picture(src, w, h, alt, attrs, prefix='../assets/img/'):
    """<img> ou <picture> com a versão 4:5 para celular."""
    tag = f'<img src="{prefix}{src}" width="{w}" height="{h}"{attrs} alt="{alt}">'
    if src not in MOBILE:
        return tag
    m = mcrop(src)
    return f'<picture><source media="(max-width: 700px)" srcset="{prefix}{m}" width="{round(h*4/5)}" height="{h}">{tag}</picture>'
