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
    ink = ink or on(color)
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

def bleed(src, pos='center'):
    page(f'<img class="bleed-img" src="{src}" style="object-position:{pos}" alt="">', 'p-bleed')

def spread(src, pos_y='center'):
    """Uma imagem atravessando a página dupla (verso + frente seguinte)."""
    pad_to_verso()
    for side in ('left', 'right'):
        page(f'<img class="spread-img spread-img--{side}" src="{src}" style="object-position:{side} {pos_y}" alt="">', 'p-bleed')

def spread_band(src):
    """Foto panorâmica numa faixa que atravessa a página dupla, com branco acima e abaixo."""
    pad_to_verso()
    for side in ('left', 'right'):
        page(f'<img class="band-img band-img--{side}" src="{src}" alt="">', 'p-bleed p-band')

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
        ('03', 'NT Records', 'Submarca · Gravadora'), ('04', 'NT Sessions', 'Identidade · Capas · Cenografia'), ('05', 'LatinJazz Brazil', 'Logotipo · Colagem · Motion'),
        ('06', 'ANJU MACE', 'Identidade visual · Símbolos'), ('07', 'Aquarie', 'Identidade visual · Ilustração'),
        ('08', 'Zouti', 'Sistema de templates'), ('09', 'Be Brave Lab', 'Símbolo · Identidade visual'),
        ('10', 'Funnel Builder', 'Marca · Sistema de lançamento')]
START = {}

# ================= CAPA + ÍNDICE =================
page('''<span class="cover-year">2026</span>
  <div class="cover-title"><h1>Portfólio</h1><p>Isadora Camargo</p></div>
  <span class="cover-site">isadoracamargo.com.br</span>''', 'p-cover')
page('', 'p-blank')
page('__INDEX__', 'p-index')

# ================= 01 NOVO TRAÇO =================
project('01', 'Novo Traço', extra=[V + 'novo-traco-making-2.jpg'])
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
logo_page('A assinatura manuscrita saiu da própria dinâmica: um gesto único, com a energia do pincel preservada.', tile(A + 'novo-traco/logo-print.png', 'FFFFFF', 'h60'))
one(A + 'novo-traco/nt-poster.jpg', 'Do gesto ao sistema', 'O material vira cartaz-manifesto: traços, desenhos e as assinaturas da equipe.')
color_page('Uma paleta ampla de propósito. Cada submarca escolhe suas cores dentro dela e ganha um traço próprio: variedade sem perder a unidade.',
           [NT[k] for k in ('cd', 'ms', 'ot', 'rp', 'tb', 'ft', 'il')])
type_page('Uma paleta tipográfica: cada segmento de comunicação tem sua voz. A Univers permite misturar pesos dentro da mesma palavra.', [UNIVERS, ROSLINDALE, MARGEM])
one(A + 'novo-traco/nt-livro.jpg', 'Aplicações', 'Box de livros com o propósito da marca na capa.')
one(A + 'novo-traco/nt-cartazes.jpg', cap='Cartazes NT Academy e NT Music Sessions')
one(A + 'novo-traco/nt-stories.jpg', cap='Stories de agenda de shows')
text_page('Vestuário', 'A marca vestida por quem faz a música.',
          '<p>A assinatura manuscrita vai para moletons, bonés, camisetas e ecobags, usados pela equipe, pelos músicos e pelos artistas convidados nas sessões e nos bastidores.</p>')
bleed(A + 'novo-traco/nt-moletom-2.jpg')
one(A + 'novo-traco/nt-sessao-moletom.jpg', cap='Sessão com a orquestra')
bleed(A + 'novo-traco/nt-camiseta-pb.jpg')
one(A + 'novo-traco/nt-moletom-1.jpg', cap='Moletom e boné Novo Traço')
stack((A + 'novo-traco/nt-camiseta-marrom.jpg', 'Camiseta'), (A + 'novo-traco/nt-ecobag-vermelha.jpg', 'Ecobag'))
text_page('Resultado', 'Um sistema que sustenta toda a comunicação do grupo.',
          '<p>Dos eventos ao digital, cada novo projeto nasce dentro dele. Como diretora de arte, coordeno um time de três designers e desenvolvo os manuais e guidelines que mantêm a marca consistente.</p>')

# ================= 02 ORQUESTRA =================
project('02', 'Orquestra Novo Traço', 'Orquestra<br>Novo Traço', extra=[V + 'orquestra-logo.jpg'])
divider('02', 'Orquestra Novo Traço', 'F0EFEB'); START['02'] = len(pages)
opener('Uma orquestra que toca com artistas da música urbana, com identidade nascida da partitura.',
       [('Cliente', 'Novo Traço'), ('Ano', '2025 — 2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Símbolo, identidade, eventos e vestuário')],
       A + 'novo-traco/orq-mockup.jpg')
text_page('Conceito', 'Uma partitura: clareza, elegância e respiro.',
          '<p>A identidade deriva da marca-mãe, com mais espaço em branco e predominância do preto sobre fundo claro.</p>')
logo_page('A equipe já chamava a orquestra de “ONT”, e a sigla virou símbolo. As letras se apoiam umas nas outras, como os instrumentos de uma orquestra, em que nenhum atua isolado.',
          fig(A + 'novo-traco/orq-logo.jpg', fit=True, cls='fig--tile'), 'Símbolo')
bleed(V + 'orquestra-simbolo.jpg', '62% center')
color_page('Três cores: o preto da tinta, o branco do papel e o amarelo como acento.', [NT['ms'], NT['cd'], NT['il']])
type_page('A Roslindale traz o refinamento de um programa de concerto; a Margem organiza as informações.', [dict(ROSLINDALE, use='Títulos e nomes'), MARGEM])
one(V + 'orquestra-evento.jpg', 'Aplicações', 'Post do evento: Orquestra NT convida L7NNON.')
text_page('Vestuário', 'O símbolo veste a orquestra.',
          '<p>Nos ensaios, nas sessões e nos bastidores, os músicos usam o moletom ONT: o símbolo no peito, a assinatura “orquestra Novo traço” logo abaixo. A identidade sai do papel e passa a fazer parte do grupo.</p>')
bleed(A + 'novo-traco/orq-retrato-violino.jpg')
stack((A + 'novo-traco/orq-moletom-branco.jpg', 'Símbolo bordado no peito'), (A + 'novo-traco/orq-moletom-preto.jpg', 'Símbolo em escala nas costas'))
bleed(A + 'novo-traco/orq-retrato-1.jpg', 'left center')
bleed(A + 'novo-traco/orq-retrato-2.jpg')
one(A + 'novo-traco/orq-batuta.jpg', 'Detalhe', 'O símbolo no peito do maestro, a batuta na mão.')
spread(A + 'novo-traco/orq-grupo-costas.jpg')
bleed(A + 'novo-traco/orq-violinistas.jpg')
one(A + 'novo-traco/orq-bastidores.jpg', 'Bastidores', 'Gravação de sessão: a marca presente em cada detalhe da produção.')
spread_band(A + 'novo-traco/orq-grupo-panorama.jpg')
spread(A + 'novo-traco/orq-sessao.jpg')
one(A + 'novo-traco/orq-foto.jpg', cap='Ensaio')

# ================= 03 NT RECORDS =================
project('03', 'NT Records', extra=[A + 'novo-traco/rec-hoodie-preto.jpg', A + 'novo-traco/rec-garrafa-inox.jpg'])
divider('03', 'NT Records', '003AE7'); START['03'] = len(pages)
opener('A gravadora do grupo: o traço da marca-mãe ganha tinta spray, textura urbana e um grid que dá solidez.',
       [('Cliente', 'Novo Traço'), ('Ano', '2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Símbolo, identidade, papelaria, merch e digital')],
       A + 'novo-traco/rec-camiseta.jpg')
text_page('Conceito', 'Do pincel à tinta spray. Do traço livre ao grid.',
          '<p><i>Existir para que a música que nasceu no palco e no estúdio continue acessível depois da luz apagar.</i></p><p>O spray traz urbanidade e textura; as linhas retas, a seriedade de uma marca sólida.</p>')
logo_page('O símbolo NT dentro de um quadro, envolvido por um traço circular de spray — o disco — e assinado “by Novo Traço”.', fig(V + 'nt-records-logo.jpg', fit=True, cls='fig--tile'))
one(A + 'novo-traco/rec-linhas.jpg', 'Princípios', 'Linhas organizam; traços expressam. A tensão entre o grid e o gesto é a marca.')
color_page('Preto, azul e branco: autoridade e confiança, com o spray como protagonista.', [NT['ms'], dict(name='Azul Records', hex='003AE7'), NT['cd']])
type_page('A Univers da marca-mãe, usada com mais rigor e menos contraste de pesos.', [dict(UNIVERS, use='Toda a comunicação: títulos, créditos e texto')])
one(A + 'novo-traco/rec-papelaria.jpg', 'Papelaria', 'Carta, envelope, pasta e caderno.')
stack((A + 'novo-traco/rec-cartao.jpg', 'Cartão de visita'), (A + 'novo-traco/rec-placa.jpg', 'Placa de 1 milhão de streams'))
bleed(A + 'novo-traco/rec-estampa.jpg')
mosaic('m2', [A + 'novo-traco/rec-hoodie-azul-frente.jpg', A + 'novo-traco/rec-hoodie-azul-costas.jpg'])
one(A + 'novo-traco/rec-tote-1.jpg', 'Merch', 'O disco pintado vira estampa; o símbolo assina com discrição.')
one(A + 'novo-traco/rec-posts.jpg', cap='Posts')

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
type_page('A Univers organiza logo, nomes de artistas e informações das capas.', [dict(UNIVERS, use='Logo, artistas e informações')])
text_page('Capas', 'Cada artista ganha seu universo; a coleção se reconhece de longe.',
          '<p>Fotografia em preto e branco com grão, recortes de colagem, um contorno amarelo e um traço à mão que atravessa a composição.</p>')
covers = [('pedrinho-rua', 'MC Pedrinho', 'A rua e a batuta do maestro'), ('pedrinho-violino', 'MC Pedrinho', 'O violino no lugar do microfone'),
          ('pedrinho-tv', 'MC Pedrinho', 'A TV de tubo e a multidão do baile'), ('pedrinho-sorriso', 'MC Pedrinho', 'Retrato com contorno amarelo'),
          ('froid-sol', 'Froid', 'O perfil contra pinceladas amarelas'), ('froid-partitura', 'Froid', 'A partitura refletida nas lentes'),
          ('froid-espelho', 'Froid', 'Violino entre cacos de espelho'), ('froid-janela', 'Froid', 'Uma janela suspensa nas nuvens')]
for i, (f, t, s) in enumerate(covers):
    cover(A + f'nt-sessions/{f}.jpg', t, s, 'top' if i % 2 == 0 else 'mid')
page(f'''{head_txt('Coleção', 'Oito capas, uma linguagem.')}
  <div class="covers-all">{''.join(f'<img src="{A}nt-sessions/{f}.jpg" alt="">' for f, _, _ in covers)}</div>''', 'p-covers', fol())
spread(A + 'nt-sessions/live-teatro-dourado.jpg')
text_page('Ao vivo', 'Ingressos esgotados em menos de 15 minutos.',
          '<p>Na estreia ao vivo, no Theatro Municipal do Rio de Janeiro, a identidade virou cenografia: testeira, painéis de LED e telão animados com os traços à mão, num sistema de amarelo e azul sobre preto que conversa com a arquitetura do teatro.</p>')
one(V + 'nts-testeira.jpg', 'Cenografia', 'Testeira animada de palco.')
bleed(A + 'nt-sessions/live-l7nnon.jpg')
one(A + 'nt-sessions/live-lanternas.jpg', cap='A plateia acende as lanternas')

# ================= 05 LATINJAZZ BRAZIL =================
project('05', 'LatinJazz Brazil', 'LatinJazz<br>Brazil', extra=[])
divider('05', 'LatinJazz Brazil', '00733C', '#F6EA60'); START['05'] = len(pages)
opener('Uma sonoridade que também pertence ao Brasil: Tropicália, colagem e um logo desenhado à mão para um projeto da Novo Traço.',
       [('Cliente', 'Novo Traço'), ('Papel', 'Direção de arte'), ('Escopo', 'Logotipo, identidade visual, motion e aplicações')],
       A + 'latinjazz/banners.jpg')
text_page('Conceito', 'Encontros e atravessamentos culturais.',
          '<p>O conceito nasce do reconhecimento de uma sonoridade que pertence ao Brasil. Cores vibrantes inspiradas na Tropicália, texturas, traços e composições expressivas traduzem essa afirmação.</p>'
          '<p>Assim como o próprio Latin Jazz, o universo visual explora contrastes, ritmos e camadas gráficas: uma estética viva, diversa e em constante movimento.</p>')
logo_page('Desenhado à mão, com traços orgânicos que refletem expressividade, movimento e dinamismo — e o losango da bandeira no lugar de destaque.',
          tile(A + 'latinjazz/logo.svg', 'FFFFFF', 'h70'))
one(A + 'latinjazz/variacoes.png', 'Variações', 'Para a animação, as letras se recombinam em figuras de musicistas, rostos, notas musicais e outros símbolos.')
bleed(V + 'latinjazz-colagem.jpg', '50% center')
color_page('Amarelo, verde, rosa, azul, branco e preto em contraste, como camadas de uma mesma colagem. As cores vêm do sistema da Novo Traço.',
           [NT['il'], NT['ft'], NT['rp'], NT['tb'], NT['cd'], NT['ms']])
type_page('A Univers organiza datas, nomes e informações; a Margem traz simpatia, leveza e brasilidade.',
          [dict(UNIVERS, use='Títulos, datas e nomes de artistas'), dict(MARGEM, use='Textos e apoio')])
spread_band(V + 'latinjazz-faixa.jpg')
one(A + 'latinjazz/cartaz.jpg', 'Aplicações', 'Cartaz em colagem: raios de sol, dançarinos e o trompete.')
one(A + 'latinjazz/revista.jpg', cap='Revista')
spread(A + 'latinjazz/vinil.jpg')
bleed(A + 'latinjazz/cartazes.jpg')
text_page('Uma marca Novo Traço', 'Um vocabulário próprio, pensado para se mexer.',
          '<p>O LatinJazz Brazil compartilha com a marca-mãe as cores, a Univers, a Margem e o gesto feito à mão, mas ganha colagem, raios de sol e papel amassado — feitos para as redes, os telões e a rua.</p>')

# ================= 05 ANJU MACE =================
project('06', 'ANJU MACE', extra=[A + 'anju-mace/02-assinatura.jpg'])
divider('06', 'ANJU MACE', '7A8569', '#F5F5DD'); START['06'] = len(pages)
opener('Uma identidade para o fitness feminino construída sobre o equilíbrio entre força e leveza.',
       [('Cliente', 'ANJU MACE'), ('Ano', '2025'), ('Papel', 'Direção de arte e coordenação da equipe'), ('Escopo', 'Identidade, símbolos, brandbook e digital')],
       A + 'anju-mace/01-capa.jpg')
text_page('Conceito', 'Força e leveza. O refinamento está na disciplina.',
          '<p>Contra o excesso do fitness — cores saturadas, promessas rápidas, estética de esforço —, a calma e a sofisticação de uma marca de luxo consciente.</p>')
logos = ''.join(f'<div class="logo-cell" style="background:#{bg}"><img src="{A}anju-mace/logos/{f}.svg" alt=""></div>'
                for f, bg in [('horizontal-grafite', 'F5F5DD'), ('vertical-grafite', 'FFFFFF'), ('empilhada-salvia', '262626'), ('horizontal-amarelo', '7A8569')])
logo_page('Caixa-alta com espaçamento generoso e contraste de peso entre ANJU e MACE. Horizontal, vertical e empilhada são extensões da mesma assinatura.', f'<div class="logo-grid">{logos}</div>')
syms = [('alvo', 'Excelência como auto-respeito', 'Um alvo: precisão, foco, disciplina e domínio técnico.'),
        ('elo', 'Mudança real e duradoura', 'Um elo entre passado e futuro: transformação que permanece.'),
        ('mola', 'Inteligência feminina', 'Uma mola que impulsiona: influência, liderança e inspiração.'),
        ('bolha', 'Conhecimento é libertação', 'A saída de uma bolha: quebrar padrões e criar o próprio caminho.'),
        ('orbitas', 'Funcionalidade e beleza', 'Órbitas em equilíbrio: harmonia entre forma e função.')]
page(f'''{head_txt('Símbolos', 'Cinco símbolos de traço fino traduzem os pilares da marca: um alfabeto gráfico para embalagens, conteúdo e produto.')}
  <div class="syms">{''.join(f'<div class="sym"><img src="{A}anju-mace/simbolos/{s}.svg" alt=""><div><b>{t}</b><p>{d}</p></div></div>' for s, t, d in syms)}</div>''', 'p-syms', fol())
one(A + 'anju-mace/06-simbolos.jpg', cap='Os símbolos aplicados')
color_page('Neutros naturais para calma e autocuidado; grafite para ancorar; amarelo suave para energia controlada. Nada é decorativo.',
           [dict(name='Preto Grafite', hex='262626', cmyk='72 65 64 69'), dict(name='Verde Oliva', hex='7A8569', cmyk='54 36 62 10'),
            dict(name='Verde Sálvia', hex='9EAB87', cmyk='41 23 53 1'), dict(name='Creme Neutro', hex='F5F5DD', cmyk='3 1 15 0'),
            dict(name='Amarelo Suave', hex='E6E6AD', cmyk='11 3 39 0')])
type_page('Lexend assina com desenho preciso e espaçamento generoso; Outfit suaviza o texto sem perder o minimalismo.',
          [dict(family='Lexend', live="'Lexend'", w=300, use='Logotipo e títulos', weights='Thin, Light, Bold, Black'),
           dict(family='Outfit', live="'Outfit'", w=400, use='Textos, interface e apoio', weights='Light, Regular, Medium')])
one(A + 'anju-mace/07-aplicacoes.jpg', 'Touchpoints', 'A assinatura vertical vira estampa; os símbolos viram padrão.')
one(A + 'anju-mace/08-app.jpg', cap='Aplicativo de treino')
one(A + 'anju-mace/09-site.jpg', cap='Site')
text_page('Resultado', '“Ninguém nunca tinha entendido a minha essência tão bem.”',
          '<p>A identidade foi lançada junto com o aplicativo de treino, hoje no ar, e as alunas se identificaram de imediato com a nova marca.</p>')

# ================= 06 AQUARIE =================
project('07', 'Aquarie', extra=[A + 'aquarie/01-capa.jpg'])
divider('07', 'Aquarie', '055E89'); START['07'] = len(pages)
opener('Moda praia de Santa Catarina com o verão do sul da Itália como referência.',
       [('Cliente', 'Aquarie Beach & Swimwear'), ('Ano', '2025'), ('Papel', 'Designer de marca'), ('Escopo', 'Identidade, ilustrações e aplicações')],
       A + 'aquarie/06-ecobag.jpg')
text_page('Conceito', 'Um verão mediterrâneo, longe do óbvio tropical.',
          '<p>Num mercado em que o beachwear segue a mesma estética tropical, a referência veio das praias do sul da Itália: listras de guarda-sóis, padronagens e gravuras clássicas.</p>')
logo_page('Serifa de alto contraste com curvas que lembram o movimento da água, na barra do A e na cauda do Q.', tile(A + 'aquarie/logo.svg', 'F1EBDF', 'w75'))
one(A + 'aquarie/02-detalhe.jpg', 'Desenho de letra', 'A cauda do Q se estende como uma onda e vira elemento gráfico autônomo.')
one(A + 'aquarie/03-ilustracoes.jpg', 'Ilustrações', 'Traço de gravura em uma única cor: sozinhas, como símbolo; juntas, como padrão.')
mosaic('m3v', [A + 'aquarie/cavalo-marinho.jpg', A + 'aquarie/concha.jpg', A + 'aquarie/janela.jpg'])
color_page('Areia como base, o amarelo do sol, o verde-água, o azul do oceano e o coral das listras.',
           [dict(name='Areia', hex='F1EBDF'), dict(name='Sol', hex='EDC07C'), dict(name='Verde-água', hex='84C1BC'), dict(name='Azul Oceano', hex='055E89'), dict(name='Vermelho Coral', hex='C53D30')])
type_page('Royale Couture Serif para o tom de alfaiataria; Lato, limpa e legível, no texto.',
          [dict(family='Royale Couture Serif', svg='royale', use='Pequenos detalhes e assinaturas', weights='Regular'),
           dict(family='Lato', live="'Lato'", w=300, use='Textos e títulos', weights='Light, Regular')])
one(A + 'aquarie/05-tags.jpg', 'Aplicações', 'Logotipo vertical e concha recortada pela borda.')
one(A + 'aquarie/07-instagram.jpg', cap='Instagram')

# ================= 07 ZOUTI =================
project('08', 'Zouti', extra=[A + 'zouti/mobile.jpg'])
divider('08', 'Zouti', '141414', '#E4FF00'); START['08'] = len(pages)
opener('Templates de redes sociais que transformam funcionalidades de produto em posts com cara de lançamento.',
       [('Cliente', 'Zouti'), ('Papel', 'Design'), ('Escopo', 'Templates, sistema visual e cenas de produto')], A + 'zouti/capa.jpg')
text_page('Conceito', 'O produto vira a imagem.',
          '<p>Fundo quase preto, vidro fosco, uma luz verde-limão pela borda e a interface real do produto no lugar de ilustrações genéricas. Regras fixas, replicáveis pelo time.</p>')
logo_page('Um Z formado por duas faixas diagonais em verde-limão.', tile(A + 'zouti/logo.svg', '141414', 'w35'))
color_page('Uma escala de verdes sobre grafite: a luz é a única cor.',
           [dict(name='Verde Zouti', hex='E4FF00'), dict(name='Verde Lima', hex='BCCF1C'), dict(name='Verde Claro', hex='D7DF75'), dict(name='Grafite', hex='141414'), dict(name='Branco', hex='FFFFFF')])
type_page('Space Grotesk nos títulos, com degradê do branco ao cinza; Inter no apoio e na interface.',
          [dict(family='Space Grotesk', live="'Space Grotesk'", w=400, use='Títulos e etiquetas', weights='Regular, Medium'),
           dict(family='Inter', live="'Inter'", w=300, use='Textos de apoio e interface', weights='Light, Medium, Semi Bold, Bold')])
mosaic('m4', [A + 'zouti/parcelamento.jpg', A + 'zouti/taxas.jpg', A + 'zouti/app-vendas.jpg', A + 'zouti/pixel.jpg'])
mosaic('m4', [A + 'zouti/area-membros.jpg', A + 'zouti/reembolso.jpg', A + 'zouti/metricas.jpg', A + 'zouti/integracoes.jpg'])

# ================= 08 BE BRAVE =================
project('09', 'Be Brave Lab', extra=[A + 'be-brave/logo-laranja.jpg'])
divider('09', 'Be Brave Lab', 'FA4C05'); START['09'] = len(pages)
opener('Uma identidade com coragem de sobra para uma agência audiovisual que disputa atenção em segundos.',
       [('Cliente', 'Be Brave Lab'), ('Segmento', 'Agência audiovisual'), ('Papel', 'Design de marca'), ('Escopo', 'Símbolo, identidade e aplicações')],
       A + 'be-brave/caixa.jpg')
text_page('Conceito', 'Duas formas que se abrem como asas: impulso.',
          '<p>A marca precisava ser reconhecível em thumbnails, vinhetas e redes, e comunicar coragem, presença e confiança — a imagem de quem avança sem pedir licença.</p>')
logo_page('Símbolo em forma de asas sobre BE BRAVE LAB em letras extended.', tile(A + 'be-brave/logo.svg', 'FFFFFF', 'w75'))
one(A + 'be-brave/construcao.jpg', 'Construção', 'Um grid de círculos e linhas paralelas: do ícone de perfil à animação 3D.')
bleed(A + 'be-brave/3d.jpg', '55% center')
color_page('O laranja é a assinatura: energia e urgência. O azul profundo é o contraponto.',
           [dict(name='Laranja Brave', hex='FA4C05'), dict(name='Azul Profundo', hex='0D0B9D'), dict(name='Off-white', hex='EFEFEF'), dict(name='Preto', hex='0F0F0F')])
type_page('A Monument Extended transmite escala e ambição e conversa com as formas do símbolo.',
          [dict(family='PP Monument Extended', svg='monument', use='Títulos, thumbnails e motion', weights='Regular, Black'),
           dict(family='Helvetica Neue LT Pro', svg='helvetica', use='Texto corrido e informações', weights='45 Light, 55 Roman, 65 Medium, 75 Bold')])
one(A + 'be-brave/foto.jpg', 'Aplicações', 'Halftone e dither: a estética audiovisual dentro da linguagem gráfica.')
one(A + 'be-brave/garrafas.jpg', cap='Garrafas')
one(A + 'be-brave/instagram.jpg', cap='Instagram')

# ================= 09 FUNNEL BUILDER =================
project('10', 'Funnel Builder', extra=[])
divider('10', 'Funnel Builder', '002D51'); START['10'] = len(pages)
opener('Marca e sistema de lançamento para formar a primeira geração de construtores de funis de venda do Brasil.',
       [('Cliente', 'Bilhon'), ('Ano', '2024 — 2025'), ('Papel', 'Head de Design: marca e direção do lançamento'), ('Escopo', 'Símbolo, ícone, sistema visual e criativos')],
       A + 'funnel-builder/logo-3d.jpg')
text_page('Conceito', 'Um F desenhado a partir de um funil.',
          '<p>Um triângulo invertido sobre diagonais paralelas: movimento e fluxo, como um cliente que avança etapa por etapa.</p>')
page(f'''{head_txt('Construção', 'Diagonais paralelas e círculos definem o F. Em 3D, com reflexos em azul-petróleo, o símbolo virou o protagonista da campanha.')}
  <div class="duo">{fig(A + 'funnel-builder/construcao.jpg', 'Construção')}{fig(A + 'funnel-builder/icone.jpg', 'Ícone do app')}</div>''', 'p-logo', fol())
color_page('Um sistema escuro, com luz azul e acentos em amarelo.',
           [dict(name='Preto Profundo', hex='030A09'), dict(name='Azul Noturno', hex='002D51'), dict(name='Azul Luz', hex='5BBED9'), dict(name='Amarelo Bônus', hex='FFDE37'), dict(name='Grafite', hex='0E0F0F'), dict(name='Branco Gelo', hex='F0F2F8')])
type_page('Inter na marca e na interface; Aspekta nos títulos de página.',
          [dict(family='Inter', live="'Inter'", w=700, use='Marca, títulos e interface', weights='Regular, Medium, SemiBold, Bold'),
           dict(family='Aspekta', svg='aspekta', use='Títulos de página e chamadas', weights='400, 500, 600')])
grid4([A + 'funnel-builder/mobile.jpg', A + 'funnel-builder/funis.jpg', A + 'funnel-builder/bonus.jpg', A + 'funnel-builder/icone.jpg'], 'Aplicações', 'Página de vendas, cards de funis e bônus e o ícone do app no mesmo sistema.', 'portrait')
text_page('Resultado', 'R$ 30 milhões em faturamento no lançamento.',
          '<p>Com um time interno de três pessoas e designers freelancers sob a minha liderança: o sistema permitiu produzir em escala sem perder consistência.</p>')

# ================= CONTATO + CONTRACAPA =================
CUR.update(prev=CUR['extra'], extra=[])
pad_to_verso()   # contato no verso, contracapa na última frente... (livro fecha em página par)
page('''<div class="end"><span class="kicker">Contato</span><p class="statement">Obrigada.</p>
  <dl class="meta meta--end"><dt>WhatsApp</dt><dd>+55 19 97116-3478</dd><dt>Site</dt><dd>isadoracamargo.com.br</dd>
  <dt>LinkedIn</dt><dd>in/isadora-camargo-86a217266</dd><dt>Instagram</dt><dd>@isaccamargo__</dd></dl></div>''', 'p-end')
page('', 'p-blank')
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
