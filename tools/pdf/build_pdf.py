# Portfólio impresso: livro A4 retrato com margens espelhadas para encadernação
# (frente = encadernação à esquerda, verso = à direita), páginas sangradas,
# páginas duplas e mosaicos. Um subtópico por página. Usa os assets do site.
# Uso: python3 tools/pdf/build_pdf.py && node tools/pdf/render.mjs
import os, html as H
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = '../assets/img/'
V = '../assets/video/'

def esc(s): return H.escape(s, quote=False)

def lum(hx):
    r, g, b = (int(hx[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def on(hx): return '#161616' if lum(hx) > 0.35 else '#ffffff'
def rgb(hx): return ' '.join(str(int(hx[i:i+2], 16)) for i in (0, 2, 4))
def ratio(src):
    w, h = Image.open(os.path.join(ROOT, 'print', src)).size
    return f'{w} / {h}'

pages = []   # (corpo, classe, rodapé)
def page(body, cls, folio=None): pages.append((body, cls, folio))
def next_is_verso(): return (len(pages) + 1) % 2 == 0

CUR = {'n': '', 'nm': '', 'extra': [], 'prev': []}   # projeto atual (rodapé e imagens de reserva)
def fol(): return (CUR['n'], CUR['nm'])

def pad_to_verso(prev_first=False):
    """Garante que a próxima página seja um verso (par). Se não for, entra uma
    imagem sangrada de reserva do projeto atual (ou uma página em branco)."""
    if next_is_verso(): return
    pool = (CUR['prev'] or CUR['extra']) if prev_first else (CUR['extra'] or CUR['prev'])
    if pool: bleed(pool.pop(0))
    else: page('', 'p-blank')

# ---------- componentes ----------
def fig(src, cap='', cls='', fit=False):
    st = '' if fit else f' style="aspect-ratio:{ratio(src)}"'
    c = f'<figcaption>{esc(cap)}</figcaption>' if cap else ''
    return f'<figure class="fig {cls}"><img src="{src}"{st} alt="">{c}</figure>'

def meta(items):
    return '<dl class="meta">' + ''.join(f'<dt>{k}</dt><dd>{esc(v)}</dd>' for k, v in items) + '</dl>'

def tile(src, bg, cls=''):
    return f'<div class="tile" style="background:#{bg}"><img class="{cls}" src="{src}" alt=""></div>'

def head_txt(kicker, text, statement=False):
    t = f'<p class="statement">{text}</p>' if statement else f'<p class="lead">{text}</p>'
    return f'<div class="txt"><span class="kicker">{kicker}</span>{t}</div>'

# ---------- páginas ----------
def divider(num, name, color, ink=None):
    """Verso inteiro na cor da marca, de frente para a abertura do projeto."""
    pad_to_verso(prev_first=True)
    color, ink = '161616', '#ffffff'   # neutro e igual para todos os projetos
    page(f'<div class="div-field" style="background:#{color};color:{ink}"><span class="div-num">{num}</span><span class="div-name">{name}</span></div>', 'p-bleed')

def opener(lede, items, img):
    page(f'''<div class="open-head"><span class="open-num">{CUR['n']}</span>
        <h2 class="open-name">{CUR['title']}</h2><p class="open-lede">{esc(lede)}</p>{meta(items)}</div>
      <div class="open-img"><img src="{img}" alt=""></div>''', 'p-open', fol())

def text_page(kicker, statement, body=''):
    b = f'<div class="body">{body}</div>' if body else ''
    page(f'<div class="txt"><span class="kicker">{kicker}</span><p class="statement">{statement}</p>{b}</div>', 'p-text', fol())

def logo_page(text, visual, kicker='Logo'):
    page(f'{head_txt(kicker, text)}<div class="visual visual--big">{visual}</div>', 'p-logo', fol())

def color_page(text, items):
    out = ''
    for c in items:
        hx = c['hex']
        codes = f'<span>HEX #{hx}</span><span>RGB {rgb(hx)}</span>'
        if c.get('cmyk'): codes += f'<span>CMYK {c["cmyk"]}</span>'
        if c.get('pantone'): codes += f'<span>PANTONE {c["pantone"]}</span>'
        edge = ' chip--edge' if lum(hx) > 0.8 else ''
        out += (f'<div class="chip-wrap"><div class="chip{edge}" style="background:#{hx}"></div>'
                f'<b>{esc(c["name"])}</b><div class="codes">{codes}</div></div>')
    n = len(items)
    cols = 2 if n <= 4 else 3
    page(f'{head_txt("Cor", text)}<div class="palette palette--n{n}" style="--cols:{cols}">{out}</div>', 'p-color', fol())

def type_page(text, items):
    out = ''
    for t in items:
        if t.get('svg'):
            spec = f'<img class="type-svg" src="{A}type/{t["svg"]}.svg" alt="">'
            sample = ''
        else:
            st = f'font-family:{t["live"]};font-weight:{t.get("w", 400)}'
            spec = f'<p class="type-live" style="{st}">{esc(t["family"])}</p>'
            sample = f'<p class="type-sample" style="{st}">Aa Bb Cc Dd Ee Ff Gg Hh Ii Jj Kk<br>0123456789 &amp; ?!</p>'
        out += (f'<div class="type-row"><div class="type-spec">{spec}</div>{sample}'
                f'<dl><dt>Uso</dt><dd>{esc(t["use"])}</dd><dt>Pesos</dt><dd>{esc(t["weights"])}</dd></dl></div>')
    page(f'{head_txt("Tipografia", text)}<div class="types">{out}</div>', 'p-type', fol())

def one(src, kicker='', text='', cap=''):
    t = head_txt(kicker, text) if kicker else ''
    page(f'{t}<div class="one">{fig(src, cap)}</div>', 'p-one', fol())

def stack(a, b, kicker='', text=''):
    t = head_txt(kicker, text) if kicker else ''
    page(f'{t}<div class="stack">{fig(*a, cls="fig--169", fit=True)}{fig(*b, cls="fig--169", fit=True)}</div>', 'p-stack', fol())

def grid4(imgs, kicker, text, shape='sq'):
    page(f'{head_txt(kicker, text)}<div class="grid4 grid4--{shape}">{"".join(fig(i, fit=True) for i in imgs)}</div>', 'p-grid4', fol())

MIN_DPI = 150  # abaixo disso a imagem não ocupa a folha inteira: entra com margem

def print_dpi(src, box_w, box_h):
    if src.endswith('.svg'): return 9999  # vetor
    w, h = Image.open(os.path.join(ROOT, 'print', src)).size
    return 25.4 / max(box_w / w, box_h / h)

def bleed(src, pos='center', force=False):
    if not force and print_dpi(src, 210, 297) < MIN_DPI:
        return one(src)
    page(f'<img class="bleed-img" src="{src}" style="object-position:{pos}" alt="">', 'p-bleed')

def spread(src, pos_y='center', force=False):
    """Uma imagem atravessando a página dupla (verso + frente seguinte)."""
    if not force and print_dpi(src, 420, 297) < MIN_DPI:
        return one(src)
    pad_to_verso()
    for side in ('left', 'right'):
        page(f'<img class="spread-img spread-img--{side}" src="{src}" style="object-position:center {pos_y}" alt="">', 'p-bleed')

def spread_band(src):
    """Foto panorâmica numa faixa que atravessa a página dupla, com branco acima e abaixo."""
    pad_to_verso()
    for side in ('left', 'right'):
        page(f'<img class="band-img band-img--{side}" src="{src}" alt="">', 'p-bleed p-band')

def disc(src, cap, mode='mid'):
    """Disco recortado sobre o branco da página: 'mid' centralizado; 'edge' enorme, saindo pela borda externa."""
    c = f'<p class="disc-cap">{esc(cap)}</p>' if cap else ''
    page(f'<img class="disc-img disc-img--{mode}" src="{src}" alt="">{c}', f'p-disc p-disc--{mode}', fol())

def mosaic(kind, imgs, pos=None):
    pos = pos or ['center'] * len(imgs)
    cells = ''.join(f'<img src="{s}" style="object-position:{p}" alt="">' for s, p in zip(imgs, pos))
    page(f'<div class="mosaic mosaic--{kind}">{cells}</div>', 'p-bleed')

def cover(src, title, sub, mode):
    """Uma capa por página: 'top' sangra no topo; 'mid' fica centralizada nas margens."""
    cap = f'<div class="cover-cap"><b>{esc(title)}</b><span>{esc(sub)}</span></div>'
    if mode == 'top':
        page(f'<img class="cover-top-img" src="{src}" alt="">{cap}', 'p-cover-top', fol())
    else:
        page(f'<div class="cover-mid"><img src="{src}" alt="">{cap}</div>', 'p-cover-mid', fol())

def project(n, nm, title=None, extra=()):
    # sobras do projeto anterior entram primeiro, para fechar a página antes da divisória
    CUR.update(n=n, nm=nm, title=title or nm, prev=CUR['extra'], extra=list(extra))

# ---------- dados compartilhados ----------
UNIVERS = dict(family='Univers Next Pro', svg='univers', use='Títulos e mistura de pesos na mesma palavra', weights='Ultra Light, Thin, Light, Regular, Medium, Bold, Heavy, Black, Extra Black')
ROSLINDALE = dict(family='Roslindale Display Narrow', svg='roslindale', use='Títulos editoriais', weights='Light, Regular, Medium, SemiBold')
MARGEM = dict(family='Margem', svg='margem', use='Texto corrido e pequenos detalhes', weights='Medium, Bold, Extra Bold, Black')
NT = dict(cd=dict(name='Cloud Dancer', hex='F0EFEB', pantone='11-4201 TCX'), ms=dict(name='My Soul', hex='020305', pantone='19-4010 TCX'),
          ot=dict(name='Orange Tiger', hex='F96714', pantone='16-1358 TCX'), rp=dict(name='Red Pink', hex='FB2A54'),
          tb=dict(name='Tropical Breeze', hex='87CDE7', pantone='13-4307 TCX'), ft=dict(name='First Tree', hex='00733C', pantone='18-6031 TCX'),
          il=dict(name='Illuminating', hex='F6EA60', pantone='13-0647 TCX'))
PROJ = [('01', 'Novo Traço', 'Identidade visual · Sistema de marca'), ('02', 'Orquestra Novo Traço', 'Símbolo · Submarca'),
        ('03', 'NT Records', 'Submarca · Gravadora'), ('04', 'NT Sessions', 'Identidade · Capas · Cenografia'), ('05', 'LatinJazz Brazil', 'Logotipo · Colagem · Motion'), ('06', 'NT Collection', 'Collab · Vestuário')]
START = {}

# ================= CAPA + ÍNDICE =================
page('''<span class="cover-year">2026</span>
  <div class="cover-title"><h1>Portfólio</h1><p>Isadora Camargo</p></div>
  <span class="cover-site">isadoracamargo.com.br</span>''', 'p-cover')
page('', 'p-blank')
page('__INDEX__', 'p-index')

# ================= 01 NOVO TRAÇO =================
project('01', 'Novo Traço', extra=[])
divider('01', 'Novo Traço', 'F6EA60'); START['01'] = len(pages)
opener('Uma marca-mãe para um grupo de arte e música: a expressividade brasileira traduzida em traço, cor e contraste.',
       [('Cliente', 'Novo Traço'), ('Ano', '2025 — 2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Identidade, sistema de marca, submarcas e guidelines')],
       A + 'novo-traco/nt-ecobag.jpg')
text_page('Conceito', 'Contrastes e expressividade.',
          '<p>A identidade nasce da expressividade como linguagem vital do povo brasileiro, onde a arte é ferramenta de sobrevivência, comunicação e identidade. Erudito e popular, tradição e ruptura, dor e celebração.</p>'
          '<p>O desafio: reunir educação, música ao vivo, orquestra e gravadora sob uma mesma voz, sem apagar a personalidade de cada projeto.</p>')
bleed(A + 'novo-traco/processo-3.jpg')
text_page('Processo criativo', 'Feito à mão, pelas pessoas que vivem a marca.',
          '<p>Os traços não foram desenhados no computador. Nasceram de uma dinâmica com a equipe à beira-mar, no Rio de Janeiro: cada pessoa traçou com marcador, pincel e tinta as palavras que definem o grupo — alegria, música, arte, emoção.</p>'
          '<p>Esse material virou a base gráfica da identidade: uma expressividade genuína, impossível de simular digitalmente.</p>')
mosaic('m3', [A + 'novo-traco/processo-5.jpg', A + 'novo-traco/processo-1.jpg', A + 'novo-traco/processo-4.jpg'], ['center 40%', 'center', 'center'])
spread(A + 'novo-traco/processo-2.jpg')
E = A + 'novo-traco/escritos/'
page(f'<img class="esc-img esc-img--logo" src="{E}novo-traco.svg" alt="">', 'p-esc', fol())
page(f'<img class="esc-img esc-img--words" src="{E}palavras.svg" alt=""><p class="esc-cap">Alegria · Música · Amor · Arte · Dinheiro · Emoção</p>', 'p-esc', fol())
page(f'<img class="esc-img esc-img--year" src="{E}2026.svg" alt="">', 'p-esc', fol())
import os as _os
_sig = sorted(f for f in _os.listdir(_os.path.join(ROOT, 'assets/img/novo-traco/escritos/assinaturas')) if f.endswith('.svg'))
page(f'''{head_txt('Assinaturas', 'Quem traçou a marca.')}
  <div class="sigs">{''.join(f'<img src="{E}assinaturas/{f}" alt="">' for f in _sig)}</div>''', 'p-sigs', fol())
text_page('O quadro', 'Tudo o que foi traçado, numa peça só.',
          '<p>Os traços, os desenhos, as palavras e as assinaturas de cada pessoa da equipe foram reunidos num cartaz-manifesto que virou quadro na sede da Novo Traço.</p>')
bleed(E + 'quadro.svg')
logo_page('A assinatura manuscrita saiu da própria dinâmica: um gesto único, com a energia do pincel preservada.', tile(A + 'novo-traco/escritos/novo-traco.svg', 'FFFFFF', 'h60'))
color_page('Uma paleta ampla de propósito. Cada submarca escolhe suas cores dentro dela e ganha um traço próprio: variedade sem perder a unidade.',
           [NT[k] for k in ('cd', 'ms', 'ot', 'rp', 'tb', 'ft', 'il')])
type_page('Uma paleta tipográfica: cada segmento de comunicação tem sua voz. A Univers permite misturar pesos dentro da mesma palavra.', [UNIVERS, ROSLINDALE, MARGEM])
text_page('Vestuário', 'A marca vestida por quem faz a música.',
          '<p>A assinatura manuscrita vai para moletons, bonés, camisetas e ecobags, usados pela equipe, pelos músicos e pelos artistas convidados nas sessões e nos bastidores.</p>')
bleed(A + 'novo-traco/nt-moletom-2.jpg')
one(A + 'novo-traco/nt-sessao-moletom.jpg', cap='Sessão com a orquestra')
bleed(A + 'novo-traco/nt-camiseta-pb.jpg')
one(A + 'novo-traco/nt-moletom-1.jpg', cap='Moletom e boné Novo Traço')
stack((A + 'novo-traco/nt-camiseta-marrom.jpg', 'Camiseta'), (A + 'novo-traco/nt-ecobag-vermelha.jpg', 'Ecobag'))
bleed(A + 'novo-traco/nt-ecobag-estudio.jpg', '35% center')
text_page('Resultado', 'Um sistema que sustenta toda a comunicação do grupo.',
          '<p>Dos eventos ao digital, cada novo projeto nasce dentro dele. Como diretora de arte, coordeno um time de três designers e desenvolvo os manuais e guidelines que mantêm a marca consistente.</p>')

# ================= 02 ORQUESTRA =================
project('02', 'Orquestra Novo Traço', 'Orquestra<br>Novo Traço', extra=[])
divider('02', 'Orquestra Novo Traço', 'F0EFEB'); START['02'] = len(pages)
opener('Uma orquestra que toca com artistas da música urbana, com identidade nascida da partitura.',
       [('Cliente', 'Novo Traço'), ('Ano', '2025 — 2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Símbolo, identidade, eventos e vestuário')],
       A + 'novo-traco/orq-mockup.jpg')
text_page('Conceito', 'Uma partitura: clareza, elegância e respiro.',
          '<p>A identidade deriva da marca-mãe, com mais espaço em branco e predominância do preto sobre fundo claro.</p>')
logo_page('A equipe já chamava a orquestra de “ONT”, e a sigla virou símbolo. As letras se apoiam umas nas outras, como os instrumentos de uma orquestra, em que nenhum atua isolado.',
          tile(A + 'novo-traco/ont.svg', 'FFFFFF', 'w75'), 'Símbolo')
page(f'''<span class="kicker">Assinaturas</span>
  <div class="lockups"><img class="lk-v" src="{A}novo-traco/orq-logo-vertical.svg" alt=""><img class="lk-h" src="{A}novo-traco/orq-logo.svg" alt=""></div>''', 'p-lockups', fol())
color_page('Três cores: o preto da tinta, o branco do papel e o amarelo como acento.', [NT['ms'], NT['cd'], NT['il']])
one(A + 'novo-traco/orq-cartoes.jpg', 'Papelaria', 'Cartões em creme e amarelo: o símbolo recortado pela borda e os nomes em Roslindale.')
one(A + 'novo-traco/orq-batuta-arte.jpg', 'Digital', 'A batuta do maestro sobre o símbolo: colagem, grão e o amarelo da marca.')
text_page('Vestuário', 'O símbolo veste a orquestra.',
          '<p>Nos ensaios, nas sessões e nos bastidores, os músicos usam o moletom ONT: o símbolo no peito, a assinatura “orquestra Novo traço” logo abaixo. A identidade sai do papel e passa a fazer parte do grupo.</p>')
bleed(A + 'novo-traco/orq-retrato-violino.jpg')
page(f'<img class="mock-img" src="{A}novo-traco/orq-hoodie-costas.webp" alt=""><p class="disc-cap">O símbolo em escala nas costas</p>', 'p-mock', fol())
page(f'<img class="mock-img" src="{A}novo-traco/orq-blusao.webp" alt=""><p class="disc-cap">Assinatura completa no peito</p>', 'p-mock', fol())
bleed(A + 'novo-traco/orq-retrato-1.jpg', 'left center')
bleed(A + 'novo-traco/orq-retrato-2.jpg')
one(A + 'novo-traco/orq-batuta.jpg', 'Detalhe', 'O símbolo no peito do maestro, a batuta na mão.')
one(A + 'novo-traco/orq-bastidores.jpg', 'Bastidores', 'Gravação de sessão: a marca presente em cada detalhe da produção.')
spread(A + 'novo-traco/orq-silhueta.jpg', 'center', force=True)
bleed(A + 'novo-traco/orq-violinistas.jpg')
one(A + 'novo-traco/orq-grupo-costas.jpg', 'O grupo', 'Juntos, os moletons formam a sigla repetida: a orquestra como um só corpo.')
one(A + 'novo-traco/orq-grupo-panorama.jpg', cap='A orquestra completa')

# ================= 03 NT RECORDS =================
project('03', 'NT Records', extra=[A + 'novo-traco/rec-hoodie-preto.jpg', A + 'novo-traco/rec-garrafa-inox.jpg'])
divider('03', 'NT Records', '003AE7'); START['03'] = len(pages)
opener('A gravadora do grupo: o traço da marca-mãe ganha tinta spray, textura urbana e um grid que dá solidez.',
       [('Cliente', 'Novo Traço'), ('Ano', '2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Símbolo, identidade, papelaria, merch e digital')],
       A + 'novo-traco/rec-camiseta.jpg')
text_page('Conceito', 'Do pincel à tinta spray. Do traço livre ao grid.',
          '<p><i>Existir para que a música que nasceu no palco e no estúdio continue acessível depois da luz apagar.</i></p><p>O spray traz urbanidade e textura; as linhas retas, a seriedade de uma marca sólida.</p>')
logo_page('O símbolo NT dentro de um quadro, envolvido por um traço circular de spray — o disco — e assinado “by Novo Traço”.', tile(A + 'novo-traco/rec-logo-vertical.svg', 'FFFFFF', 'h60'))
one(A + 'novo-traco/rec-linhas.jpg', 'Princípios', 'Linhas organizam; traços expressam. A tensão entre o grid e o gesto é a marca.')
disc(A + 'novo-traco/rec-traco-circulo.webp', 'Traço — o círculo de spray que envolve o símbolo', 'mid')
text_page('Discos', 'Spray, pincel e tinta, direto no vinil.',
          '<p>Discos de vinil pintados à mão no ateliê formam o acervo gráfico da gravadora: camadas de tinta branca a pincel, spray preto por cima e o gesto de raspar e arrastar a tinta.</p><p>Cada disco vira estampa, post, capa ou textura, e nenhum se repete. O erro e o respingo fazem parte da marca.</p>')
bleed(A + 'novo-traco/rec-processo-coracao.jpg', '96% center', force=True)
stack((A + 'novo-traco/rec-processo-pincel.jpg', 'Pinceladas sobre o vinil'), (A + 'novo-traco/rec-processo-branco.jpg', 'Base de tinta branca'))
disc(A + 'novo-traco/rec-disco-02.webp', 'Disco 02', 'edge')
disc(A + 'novo-traco/rec-disco-13.webp', 'Disco 13', 'mid')
disc(A + 'novo-traco/rec-disco-06.webp', 'Disco 06', 'edge')
disc(A + 'novo-traco/rec-disco-08.webp', 'Disco 08', 'mid')
disc(A + 'novo-traco/rec-disco-10.webp', 'Disco 10', 'edge')
disc(A + 'novo-traco/rec-disco-12.webp', 'Disco 12', 'mid')
page(f'''{head_txt('Acervo', 'Treze discos, um mesmo gesto.')}
  <div class="discs-all">{''.join(f'<img src="{A}novo-traco/rec-disco-{i:02d}.webp" alt="">' for i in range(1, 14))}</div>''', 'p-discs', fol())
color_page('Preto, azul e branco: autoridade e confiança, com o spray como protagonista.', [NT['ms'], dict(name='Azul Records', hex='003AE7'), NT['cd']])
one(A + 'novo-traco/rec-papelaria.jpg', 'Papelaria', 'Carta, envelope, pasta e caderno.')
stack((A + 'novo-traco/rec-cartao.jpg', 'Cartão de visita'), (A + 'novo-traco/rec-placa.jpg', 'Placa de 1 milhão de streams'))
bleed(A + 'novo-traco/rec-estampa.jpg')
mosaic('m2', [A + 'novo-traco/rec-hoodie-azul-frente.jpg', A + 'novo-traco/rec-hoodie-azul-costas.jpg'])
page(f'<img class="poster-img" src="{A}novo-traco/rec-poster.webp" alt="">', 'p-poster', fol())
one(A + 'novo-traco/rec-tote-1.jpg', 'Merch', 'O disco pintado vira estampa; o símbolo assina com discrição.')
page(f'<img class="mock-img" src="{A}novo-traco/rec-tote-discos.webp" alt=""><p class="disc-cap">Ecobag com os discos</p>', 'p-mock', fol())
one(A + 'novo-traco/rec-hoodie-spray.webp', cap='Hoodie tingido com spray')
text_page('Digital', 'O azul da gravadora, o spray e o disco como linguagem nas redes.')
for f in ('rec-post-jazz', 'rec-post-discos', 'rec-post-frase'):
    page(f'<img class="post-img" src="{A}novo-traco/{f}.jpg" alt="">', 'p-post', fol())

# ================= 04 NT SESSIONS =================
project('04', 'NT Sessions', extra=[A + 'nt-sessions/live-emocao.jpg'])
divider('04', 'NT Sessions', 'F6EA60'); START['04'] = len(pages)
opener('A orquestra encontra a música urbana: sessões gravadas, EPs e um show esgotado no Theatro Municipal do Rio.',
       [('Cliente', 'Novo Traço'), ('Ano', '2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Identidade, capas, motion e cenografia em LED')],
       A + 'nt-sessions/live-teatro-vermelho.jpg')
text_page('Conceito', 'O erudito e a rua no mesmo palco.',
          '<p>Cada edição é uma collab entre a Orquestra Novo Traço e um artista urbano: o repertório ganha arranjos para orquestra, é gravado em sessão e vira EP. Já passaram L7NNON e Papatinho, MC Pedrinho e Froid.</p>')
logo_page('Um carimbo: N e t pintados à mão, presos num quadro, com SESSIONS numa faixa sólida. Assina qualquer capa ou telão sem disputar espaço com o artista.',
          tile(A + 'nt-sessions/logo.svg', 'FFFFFF', 'h70'))
color_page('Amarelo e azul sobre preto e branco: as cores da marca-mãe a serviço do contraste.', [NT['il'], NT['ms'], NT['cd'], NT['tb']])
text_page('Capas', 'Cada artista ganha seu universo; a coleção se reconhece de longe.',
          '<p>Fotografia em preto e branco com grão, recortes de colagem, um contorno amarelo e um traço à mão que atravessa a composição.</p>')
covers = [('pedrinho-rua', 'MC Pedrinho', 'A rua e a batuta do maestro'), ('pedrinho-violino', 'MC Pedrinho', 'O violino no lugar do microfone'),
          ('pedrinho-tv', 'MC Pedrinho', 'A TV de tubo e a multidão do baile'), ('pedrinho-sorriso', 'MC Pedrinho', 'Retrato com contorno amarelo'),
          ('froid-sol', 'Froid', 'O perfil contra pinceladas amarelas'), ('froid-partitura', 'Froid', 'A partitura refletida nas lentes'),
          ('froid-espelho', 'Froid', 'Violino entre cacos de espelho'), ('froid-janela', 'Froid', 'Uma janela suspensa nas nuvens')]
for i, (f, t, s) in enumerate(covers):
    cover(A + f'nt-sessions/{f}.jpg', t, s, 'top' if i % 2 == 0 and f.startswith('pedrinho') else 'mid')
page(f'''{head_txt('Coleção', 'Oito capas, uma linguagem.')}
  <div class="covers-all">{''.join(f'<img src="{A}nt-sessions/{f}.jpg" alt="">' for f, _, _ in covers)}</div>''', 'p-covers', fol())
spread(A + 'nt-sessions/live-teatro-dourado.jpg')
text_page('Ao vivo', 'Ingressos esgotados em menos de 15 minutos.',
          '<p>Na estreia ao vivo, no Theatro Municipal do Rio de Janeiro, a identidade virou cenografia: testeira, painéis de LED e telão animados com os traços à mão, num sistema de amarelo e azul sobre preto que conversa com a arquitetura do teatro.</p>')
spread(A + 'nt-sessions/live-palco.jpg')
bleed(A + 'nt-sessions/live-papatinho.jpg', '40% center')
bleed(A + 'nt-sessions/live-teatro-vermelho.jpg', '55% center')
one(A + 'nt-sessions/live-abraco.jpg', cap='O abraço no fim do show')
bleed(A + 'nt-sessions/live-l7nnon.jpg')
one(A + 'nt-sessions/live-lanternas.jpg', cap='A plateia acende as lanternas')

# ================= 05 LATINJAZZ BRAZIL =================
project('05', 'LatinJazz Brazil', 'LatinJazz<br>Brazil', extra=[A + 'latinjazz/cartaz.jpg'])
divider('05', 'LatinJazz Brazil', '00733C', '#F6EA60'); START['05'] = len(pages)
opener('Uma sonoridade que também pertence ao Brasil: Tropicália, colagem e um logo desenhado à mão para um projeto da Novo Traço.',
       [('Cliente', 'Novo Traço'), ('Papel', 'Direção de arte'), ('Escopo', 'Logotipo, identidade visual, motion e aplicações')],
       A + 'latinjazz/banners.jpg')
text_page('Conceito', 'Encontros e atravessamentos culturais.',
          '<p>O conceito nasce do reconhecimento de uma sonoridade que pertence ao Brasil. Cores vibrantes inspiradas na Tropicália, texturas, traços e composições expressivas traduzem essa afirmação.</p>'
          '<p>Assim como o próprio Latin Jazz, o universo visual explora contrastes, ritmos e camadas gráficas: uma estética viva, diversa e em constante movimento.</p>')
logo_page('Desenhado à mão, com traços orgânicos que refletem expressividade, movimento e dinamismo — e o losango da bandeira no lugar de destaque.',
          tile(A + 'latinjazz/logo-vetor.svg', 'FFFFFF', 'h70'))
page(f'''{head_txt('Iterações', 'Para a animação, as letras se recombinam em figuras de musicistas, rostos, notas musicais e outros símbolos.')}
  <img class="iter-img" src="{A}latinjazz/iteracoes.svg" alt="">''', 'p-iter', fol())
color_page('Amarelo, verde, rosa, azul, branco e preto em contraste, como camadas de uma mesma colagem. As cores vêm do sistema da Novo Traço.',
           [NT['il'], NT['ft'], NT['rp'], NT['tb'], NT['cd'], NT['ms']])
page(f'<img class="mock-img" src="{A}latinjazz/revista-mockup.webp" alt=""><p class="disc-cap">Revista</p>', 'p-mock', fol())
text_page('Aplicações', 'Cartazes que parecem colados no muro.', '<p>Fotografia em duotom, recortes de colagem, raios de sol em verde e amarelo e a textura de tijolo por baixo: cada peça tem a energia de um lambe-lambe.</p>')
bleed(A + 'latinjazz/cartaz-trompete.jpg')
one(A + 'latinjazz/vinil.jpg', cap='Capa de vinil')
bleed(A + 'latinjazz/cartaz-sax.jpg')
spread(A + 'latinjazz/banners-hd.jpg', force=True)
page(f'<img class="poster-img" src="{A}latinjazz/cartaz-dancarinos.webp" alt="">', 'p-poster', fol())
text_page('Uma marca Novo Traço', 'Um vocabulário próprio, pensado para se mexer.',
          '<p>O LatinJazz Brazil compartilha com a marca-mãe as cores, a Univers, a Margem e o gesto feito à mão, mas ganha colagem, raios de sol e papel amassado — feitos para as redes, os telões e a rua.</p>')

# ================= 06 NT COLLECTION =================
project('06', 'NT Collection', extra=[])
divider('06', 'NT Collection', '161616'); START['06'] = len(pages)
opener('Uma coleção-cápsula da Novo Traço com Papatinho: o traço da marca, a tag do produtor e Los Angeles 2026 numa mesma peça.',
       [('Cliente', 'Novo Traço'), ('Ano', '2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Coleção, estampas, etiquetas e ecobags')],
       A + 'nt-collection/moletom-costas.jpg')
text_page('Conceito', 'Duas assinaturas na mesma peça.',
          '<p>A NT Collection leva o universo da Novo Traço para o vestuário em parceria com artistas. Na primeira edição, com Papatinho, o N pintado à mão da marca encontra a tag manuscrita do produtor, a serifa do “Collection” e as informações da cápsula: Los Angeles, CA, 2026.</p>')
logo_page('O N pintado à mão da Novo Traço encontra o “Collection” em serifa: uma assinatura pensada para dividir espaço com a tag de cada artista convidado.', tile(A + 'nt-collection/logo.svg', 'FFFFFF', 'w75'))
color_page('O azul da ecobag, o azul-claro do traço, o amarelo da Novo Traço e o preto e o creme de base.',
           [dict(name='Azul Collection', hex='0E17C2'), dict(name='Azul Tinta', hex='0E008C'), dict(name='Tropical Breeze', hex='87CDE7', pantone='13-4307 TCX'),
            dict(name='Illuminating', hex='F6EA60', pantone='13-0647 TCX'), NT['ms'], dict(name='Creme', hex='F1F0E8')])
text_page('Estampas', 'Cada peça, uma composição.',
          '<p>O N gigante pintado à mão nas costas do moletom; as palavras da Novo Traço sob o traço amarelo na camiseta; a tag do Papatinho em branco sobre o azul da ecobag. Em todas, a mesma assinatura: Los Angeles, CA, 2026.</p>')
page(f'<img class="art-img" src="{A}nt-collection/estampa-moletom.svg" alt=""><p class="esc-cap">Estampa do moletom</p>', 'p-art', fol())
bleed(A + 'nt-collection/moletom-costas.jpg')
one(A + 'nt-collection/papatinho-sofa.jpg', 'Papatinho', 'O moletom da coleção no estúdio, com o símbolo NT Collection no peito.')
page(f'<img class="art-img" src="{A}nt-collection/estampa-camiseta.svg" alt=""><p class="esc-cap">Estampa da camiseta</p>', 'p-art', fol())
bleed(A + 'nt-collection/camisetas.jpg')
page(f'<div class="art-field" style="background:#0E17C2"><img class="art-img" src="{A}nt-collection/estampa-ecobag.svg" alt=""></div>', 'p-bleed', fol())
bleed(A + 'nt-collection/ecobags.jpg')
page(f'<img class="art-img art-img--wide" src="{A}nt-collection/estampa-assinatura.svg" alt=""><p class="esc-cap">Assinatura da cápsula</p>', 'p-art', fol())
bleed(A + 'nt-collection/etiqueta.jpg')

# ================= CONTATO + CONTRACAPA =================
CUR.update(prev=CUR['extra'], extra=[])
page('''<div class="end"><span class="kicker">Contato</span><p class="statement">Obrigada.</p>
  <dl class="meta meta--end"><dt>WhatsApp</dt><dd>+55 19 97116-3478</dd><dt>Site</dt><dd>isadoracamargo.com.br</dd>
  <dt>LinkedIn</dt><dd>in/isadora-camargo-86a217266</dd><dt>Instagram</dt><dd>@isaccamargo__</dd></dl></div>''', 'p-end')
page('<span class="cover-site">isadoracamargo.com.br</span>', 'p-back')
if len(pages) % 2: pages.insert(-1, ('', 'p-blank', None))

# ---------- índice ----------
idx = ''.join(f'<li><span class="i-num">{n}</span><span class="i-name">{nm}<small>{t}</small></span><span class="i-page">{START[n]:02d}</span></li>' for n, nm, t in PROJ)
pages[2] = (f'<span class="kicker">Índice</span><ol class="idx">{idx}</ol>', 'p-index', None)

# ---------- HTML ----------
body = ''
for i, (b, cls, folio) in enumerate(pages, 1):
    side = 'recto' if i % 2 else 'verso'
    f = f'<footer class="folio"><span>{folio[0]} — {folio[1]}</span><span>{i:02d}</span></footer>' if folio else ''
    body += f'<section class="page {side} {cls}">{b}{f}</section>\n'
css = open(os.path.join(os.path.dirname(__file__), 'print.css')).read()
out = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Portfólio — Isadora Camargo</title>
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Lexend:wght@300&family=Outfit:wght@400&family=Space+Grotesk:wght@400&family=Inter:wght@300;700&family=Lato:wght@300&display=block" rel="stylesheet">
<style>{css}</style></head><body>
{body}</body></html>'''
open(os.path.join(ROOT, 'print/portfolio.html'), 'w').write(out)
print(len(pages), 'páginas')
