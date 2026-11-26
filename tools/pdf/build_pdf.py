# Portfólio impresso: PDF A4 retrato, com margens espelhadas para encadernação
# (frente = encadernação à esquerda, verso = à direita). Usa os assets do site.
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

# ---------- componentes ----------
def fig(src, cap='', cls='', fit=False):
    st = '' if fit else f' style="aspect-ratio:{ratio(src)}"'
    c = f'<figcaption>{esc(cap)}</figcaption>' if cap else ''
    return f'<figure class="fig {cls}"><img src="{src}"{st} alt="">{c}</figure>'

def meta(items):
    return '<dl class="meta">' + ''.join(f'<dt>{k}</dt><dd>{esc(v)}</dd>' for k, v in items) + '</dl>'

def palette(items):
    out = ''
    for c in items:
        hx = c['hex']
        codes = f'<span>HEX #{hx}</span><span>RGB {rgb(hx)}</span>'
        if c.get('cmyk'): codes += f'<span>CMYK {c["cmyk"]}</span>'
        if c.get('pantone'): codes += f'<span>PANTONE {c["pantone"]}</span>'
        edge = ' chip--edge' if lum(hx) > 0.8 else ''
        out += (f'<div class="chip-wrap"><div class="chip{edge}" style="background:#{hx}"></div>'
                f'<b>{esc(c["name"])}</b><div class="codes">{codes}</div></div>')
    cols = 4 if len(items) in (4, 7, 8) else 3 if len(items) in (3, 5, 6) else len(items)
    return f'<div class="palette" style="--cols:{cols}">{out}</div>'

def typeset(items):
    out = ''
    for t in items:
        if t.get('svg'): spec = f'<img class="type-svg" src="{A}type/{t["svg"]}.svg" alt="">'
        else: spec = f'<p class="type-live" style="font-family:{t["live"]};font-weight:{t.get("w", 500)}">{esc(t.get("sample", t["family"]))}</p>'
        out += (f'<div class="type-row"><div class="type-spec">{spec}</div>'
                f'<dl><dt>Família</dt><dd>{esc(t["family"])}</dd><dt>Uso</dt><dd>{esc(t["use"])}</dd><dt>Pesos</dt><dd>{esc(t["weights"])}</dd></dl></div>')
    return f'<div class="types">{out}</div>'

# ---------- páginas-modelo ----------
def opener(num, name, lede, items, img):
    page(f'''<div class="open-head">
        <span class="open-num">{num}</span>
        <h2 class="open-name">{name}</h2>
        <p class="open-lede">{esc(lede)}</p>
        {meta(items)}
      </div>
      <div class="open-img"><img src="{img}" alt=""></div>''', 'p-open', (num, name.replace('<br>', ' ')))

def concept(num, name, label, statement, body, visual):
    page(f'''<div class="txt">
        <span class="kicker">{label}</span>
        <p class="statement">{statement}</p>
        <div class="body">{body}</div>
      </div>
      <div class="visual">{visual}</div>''', 'p-concept', (num, name))

def tile(src, bg, cls=''):
    return f'<div class="tile" style="background:#{bg}"><img class="{cls}" src="{src}" alt=""></div>'

def system(num, name, intro, pal, types):
    page(f'''<span class="kicker">Sistema visual</span>
      <p class="lead">{intro}</p>
      <div class="sys-block"><span class="label">Paleta</span>{palette(pal)}</div>
      <div class="sys-block"><span class="label">Tipografia</span>{typeset(types)}</div>''', 'p-system', (num, name))

def one(num, name, src, label='', text='', cap=''):
    t = f'<div class="txt"><span class="kicker">{label}</span><p class="lead">{text}</p></div>' if label else ''
    page(f'{t}<div class="one">{fig(src, cap)}</div>', 'p-one', (num, name))

def stack(num, name, a, b, label='', text=''):
    t = f'<div class="txt"><span class="kicker">{label}</span><p class="lead">{text}</p></div>' if label else ''
    page(f'{t}<div class="stack">{fig(*a, cls="fig--169", fit=True)}{fig(*b, cls="fig--169", fit=True)}</div>', 'p-stack', (num, name))

def grid4(num, name, imgs, label, text, shape='sq'):
    page(f'''<div class="txt"><span class="kicker">{label}</span><p class="lead">{text}</p></div>
      <div class="grid4 grid4--{shape}">{''.join(fig(i, fit=True) for i in imgs)}</div>''', 'p-grid4', (num, name))

# ---------- dados compartilhados ----------
UNIVERS = dict(family='Univers Next Pro', svg='univers', use='Títulos e mistura de pesos na mesma palavra', weights='Ultra Light a Extra Black')
ROSLINDALE = dict(family='Roslindale Display Narrow', svg='roslindale', use='Títulos editoriais', weights='Light, Regular, Medium, SemiBold')
MARGEM = dict(family='Margem', svg='margem', use='Texto corrido e detalhes', weights='Medium, Bold, Extra Bold, Black')
NT = dict(cd=dict(name='Cloud Dancer', hex='F0EFEB', pantone='11-4201 TCX'), ms=dict(name='My Soul', hex='020305', pantone='19-4010 TCX'),
          ot=dict(name='Orange Tiger', hex='F96714', pantone='16-1358 TCX'), rp=dict(name='Red Pink', hex='FB2A54'),
          tb=dict(name='Tropical Breeze', hex='87CDE7', pantone='13-4307 TCX'), ft=dict(name='First Tree', hex='00733C', pantone='18-6031 TCX'),
          il=dict(name='Illuminating', hex='F6EA60', pantone='13-0647 TCX'))
PROJ = [('01', 'Novo Traço', 'Identidade visual · Sistema de marca'), ('02', 'Orquestra Novo Traço', 'Símbolo · Submarca'),
        ('03', 'NT Records', 'Submarca · Gravadora'), ('04', 'NT Sessions', 'Identidade · Capas · Cenografia'),
        ('05', 'ANJU MACE', 'Identidade visual · Símbolos'), ('06', 'Aquarie', 'Identidade visual · Ilustração'),
        ('07', 'Zouti', 'Sistema de templates'), ('08', 'Be Brave Lab', 'Símbolo · Identidade visual'),
        ('09', 'Funnel Builder', 'Marca · Sistema de lançamento')]
START = {}

# ================= CAPA (frente) =================
page('''<span class="cover-year">2026</span>
  <div class="cover-title"><h1>Portfólio</h1><p>Isadora Camargo</p></div>
  <span class="cover-site">isadoracamargo.com.br</span>''', 'p-cover')
# índice (verso)
page('__INDEX__', 'p-index')

# ================= 01 NOVO TRAÇO (6) =================
n, nm = '01', 'Novo Traço'; START[n] = len(pages) + 1
opener(n, nm, 'Uma marca-mãe para um grupo de arte e música: a expressividade brasileira traduzida em traço, cor e contraste.',
       [('Cliente', 'Novo Traço'), ('Ano', '2025 — 2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Identidade, sistema de marca, submarcas e guidelines')],
       A + 'novo-traco/nt-ecobag.jpg')
concept(n, nm, 'Conceito', 'Contrastes e expressividade.',
        '<p>A identidade nasce da expressividade como linguagem vital do povo brasileiro. Erudito e popular, tradição e ruptura, dor e celebração: os contrastes refletem a miscigenação cultural que gera conexão real.</p>'
        '<p>O desafio: reunir educação, música ao vivo, orquestra e gravadora sob uma mesma voz, sem apagar a personalidade de cada projeto.</p>',
        tile(A + 'novo-traco/logo-print.png', 'FFFFFF', 'h60'))
one(n, nm, V + 'novo-traco-making-2.jpg', 'Feito à mão',
    'Os traços nasceram de uma dinâmica com a equipe no Rio de Janeiro: cada pessoa traçou com marcador, pincel e tinta, e esse material virou a base gráfica da identidade.',
    'Captação dos traços com a equipe')
system(n, nm, 'Uma paleta ampla de propósito, em que cada submarca escolhe suas cores, e uma paleta tipográfica que dá voz a cada segmento.',
       [NT[k] for k in ('cd', 'ms', 'ot', 'rp', 'tb', 'ft', 'il')], [UNIVERS, ROSLINDALE, MARGEM])
one(n, nm, A + 'novo-traco/nt-poster.jpg', cap='Cartaz-manifesto com os traços e as assinaturas da equipe')
stack(n, nm, (A + 'novo-traco/nt-livro.jpg', 'Box de livros com o propósito da marca'), (A + 'novo-traco/nt-cartazes.jpg', 'Cartazes NT Academy e NT Music Sessions'),
      'Aplicações', 'O sistema sustenta toda a comunicação do grupo. Como diretora de arte, coordeno três designers e desenvolvo os guidelines da marca.')

# ================= 02 ORQUESTRA (4) =================
n, nm = '02', 'Orquestra Novo Traço'; START[n] = len(pages) + 1
opener(n, 'Orquestra<br>Novo Traço', 'Uma orquestra que toca com artistas da música urbana, com identidade nascida da partitura.',
       [('Cliente', 'Novo Traço'), ('Ano', '2025 — 2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Símbolo, identidade, eventos e vestuário')],
       A + 'novo-traco/orq-mockup.jpg')
concept(n, nm, 'Conceito', 'Uma partitura: clareza, elegância e respiro.',
        '<p>A equipe já chamava a orquestra de “ONT”, e a sigla virou símbolo. As letras se apoiam umas nas outras, como os instrumentos de uma orquestra, em que nenhum atua isolado.</p>',
        fig(A + 'novo-traco/orq-logo.jpg', fit=True, cls='fig--tile'))
system(n, nm, 'Mais espaço em branco e preto sobre fundo claro. A Roslindale traz o refinamento de um programa de concerto.',
       [NT['ms'], NT['cd'], NT['il']], [dict(ROSLINDALE, use='Títulos e nomes'), MARGEM])
stack(n, nm, (V + 'orquestra-evento.jpg', 'Post do evento com L7NNON'), (A + 'novo-traco/orq-moletom-preto.jpg', 'Símbolo em escala no vestuário'))

# ================= 03 NT RECORDS (6) =================
n, nm = '03', 'NT Records'; START[n] = len(pages) + 1
opener(n, nm, 'A gravadora do grupo: o traço da marca-mãe ganha tinta spray, textura urbana e um grid que dá solidez.',
       [('Cliente', 'Novo Traço'), ('Ano', '2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Símbolo, identidade, papelaria, merch e digital')],
       A + 'novo-traco/rec-camiseta.jpg')
concept(n, nm, 'Conceito', 'Do pincel à tinta spray. Do traço livre ao grid.',
        '<p>A gravadora troca o pincel pela tinta spray, para ganhar urbanidade e textura. Linhas retas funcionam como grid estruturante e trazem a seriedade de uma marca sólida.</p>',
        fig(V + 'nt-records-logo.jpg', fit=True, cls='fig--tile'))
one(n, nm, A + 'novo-traco/rec-linhas.jpg', 'Princípios', 'Linhas organizam; traços expressam. A tensão entre o grid e o gesto é a marca.', 'Guia de marca: Linhas e Traços')
system(n, nm, 'Preto, azul e branco: autoridade e confiança, com o spray como protagonista. A Univers da marca-mãe, com mais rigor.',
       [NT['ms'], dict(name='Azul Records', hex='003AE7'), NT['cd']], [dict(UNIVERS, use='Toda a comunicação')])
one(n, nm, A + 'novo-traco/rec-papelaria.jpg', cap='Papelaria')
stack(n, nm, (A + 'novo-traco/rec-tote-1.jpg', 'Ecobag'), (A + 'novo-traco/rec-posts.jpg', 'Posts'),
      'Merch e digital', 'O disco pintado vira estampa; o símbolo assina com discrição.')

# ================= 04 NT SESSIONS (6) =================
n, nm = '04', 'NT Sessions'; START[n] = len(pages) + 1
opener(n, nm, 'A orquestra encontra a música urbana: sessões gravadas, EPs e um show esgotado no Theatro Municipal do Rio.',
       [('Cliente', 'Novo Traço'), ('Ano', '2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Identidade, capas, motion e cenografia em LED')],
       A + 'nt-sessions/live-teatro-vermelho.jpg')
concept(n, nm, 'Identidade', 'Um selo feito à mão que assina sem disputar espaço com o artista.',
        '<p>Cada edição é uma collab entre a orquestra e um artista urbano: L7NNON e Papatinho, MC Pedrinho, Froid. O logo é um carimbo — N e t pintados à mão dentro de um quadro.</p>',
        tile(A + 'nt-sessions/logo.svg', 'FFFFFF', 'h70'))
system(n, nm, 'Preto e branco com grão, colagem, contorno amarelo e um traço à mão atravessando a composição.',
       [NT['il'], NT['ms'], NT['cd'], NT['tb']], [dict(UNIVERS, use='Logo, artistas e informações')])
grid4(n, nm, [A + 'nt-sessions/pedrinho-rua.jpg', A + 'nt-sessions/pedrinho-violino.jpg', A + 'nt-sessions/pedrinho-tv.jpg', A + 'nt-sessions/pedrinho-sorriso.jpg'],
      'Capas · MC Pedrinho', 'A rua e a sala de concerto: carros populares e a batuta, o violino no lugar do microfone.')
grid4(n, nm, [A + 'nt-sessions/froid-sol.jpg', A + 'nt-sessions/froid-partitura.jpg', A + 'nt-sessions/froid-espelho.jpg', A + 'nt-sessions/froid-janela.jpg'],
      'Capas · Froid', 'Grão e alto contraste mais densos e introspectivos.')
stack(n, nm, (V + 'nts-testeira.jpg', 'Testeira animada de palco'), (A + 'nt-sessions/live-lanternas.jpg', 'Theatro Municipal do Rio'),
      'Ao vivo', 'A identidade virou cenografia em LED. Ingressos esgotados em menos de 15 minutos.')

# ================= 05 ANJU MACE (6) =================
n, nm = '05', 'ANJU MACE'; START[n] = len(pages) + 1
opener(n, nm, 'Uma identidade para o fitness feminino construída sobre o equilíbrio entre força e leveza.',
       [('Cliente', 'ANJU MACE'), ('Ano', '2025'), ('Papel', 'Direção de arte e coordenação da equipe'), ('Escopo', 'Identidade, símbolos, brandbook e digital')],
       A + 'anju-mace/01-capa.jpg')
logos = ''.join(f'<div class="logo-cell" style="background:#{bg}"><img src="{A}anju-mace/logos/{f}.svg" alt=""></div>'
                for f, bg in [('horizontal-grafite', 'F5F5DD'), ('vertical-grafite', 'FFFFFF'), ('empilhada-salvia', '262626'), ('horizontal-amarelo', '7A8569')])
concept(n, nm, 'Conceito', 'Força e leveza. O refinamento está na disciplina.',
        '<p>Contra o excesso do fitness — cores saturadas, promessas rápidas —, a calma de uma marca de luxo consciente. Caixa-alta espaçada e contraste de peso entre ANJU e MACE.</p>',
        f'<div class="logo-grid">{logos}</div>')
syms = [('alvo', 'Excelência como auto-respeito', 'Precisão, foco, disciplina e domínio técnico.'),
        ('elo', 'Mudança real e duradoura', 'Transformação consciente que permanece.'),
        ('mola', 'Inteligência feminina', 'Influência, liderança e inspiração coletiva.'),
        ('bolha', 'Conhecimento é libertação', 'Quebrar padrões e criar o próprio caminho.'),
        ('orbitas', 'Funcionalidade e beleza', 'Harmonia entre forma e função.')]
page(f'''<span class="kicker">Símbolos</span><p class="lead">Cinco símbolos de traço fino traduzem os pilares da marca: um alfabeto gráfico para embalagens, conteúdo e produto.</p>
  <div class="syms">{''.join(f'<div class="sym"><img src="{A}anju-mace/simbolos/{s}.svg" alt=""><div><b>{t}</b><p>{d}</p></div></div>' for s, t, d in syms)}</div>''', 'p-syms', (n, nm))
system(n, nm, 'Neutros naturais para calma e autocuidado; grafite para ancorar; amarelo suave para energia controlada.',
       [dict(name='Preto Grafite', hex='262626', cmyk='72 65 64 69'), dict(name='Verde Oliva', hex='7A8569', cmyk='54 36 62 10'),
        dict(name='Verde Sálvia', hex='9EAB87', cmyk='41 23 53 1'), dict(name='Creme Neutro', hex='F5F5DD', cmyk='3 1 15 0'),
        dict(name='Amarelo Suave', hex='E6E6AD', cmyk='11 3 39 0')],
       [dict(family='Lexend', live="'Lexend'", w=300, sample='ANJU MACE', use='Logotipo e títulos', weights='Thin, Light, Bold, Black'),
        dict(family='Outfit', live="'Outfit'", w=400, sample='Força e leveza', use='Textos e interface', weights='Light, Regular, Medium')])
one(n, nm, A + 'anju-mace/06-simbolos.jpg', cap='Símbolos aplicados')
stack(n, nm, (A + 'anju-mace/07-aplicacoes.jpg', 'Vestuário, embalagem e redes'), (A + 'anju-mace/09-site.jpg', 'Site e aplicativo'),
      'Resultado', 'Lançada com o aplicativo de treino. As alunas se identificaram de imediato com a nova marca.')

# ================= 06 AQUARIE (6) =================
n, nm = '06', 'Aquarie'; START[n] = len(pages) + 1
opener(n, nm, 'Moda praia de Santa Catarina com o verão do sul da Itália como referência.',
       [('Cliente', 'Aquarie Beach & Swimwear'), ('Ano', '2025'), ('Papel', 'Designer de marca'), ('Escopo', 'Identidade, ilustrações e aplicações')],
       A + 'aquarie/06-ecobag.jpg')
concept(n, nm, 'Conceito', 'Um verão mediterrâneo, longe do óbvio tropical.',
        '<p>Listras de guarda-sóis, padronagens e gravuras clássicas. O logotipo em serifa de alto contraste ganha curvas de água, na barra do A e na cauda do Q.</p>',
        tile(A + 'aquarie/logo.svg', 'F1EBDF', 'w75'))
one(n, nm, A + 'aquarie/02-detalhe.jpg', 'Desenho de letra', 'A cauda do Q se estende como uma onda e vira elemento gráfico autônomo.')
page(f'''<span class="kicker">Ilustrações</span><p class="lead">Traço de gravura em uma única cor: sozinhas, como símbolo; juntas, como padrão.</p>
  <div class="illu">{fig(A + 'aquarie/03-ilustracoes.jpg', cls='illu-main')}<div class="illu-row">{fig(A + 'aquarie/concha.jpg')}{fig(A + 'aquarie/cavalo-marinho.jpg')}{fig(A + 'aquarie/janela.jpg')}</div></div>''', 'p-illu', (n, nm))
system(n, nm, 'Areia, sol, verde-água, oceano e coral. Royale Couture Serif para o tom de alfaiataria; Lato no texto.',
       [dict(name='Areia', hex='F1EBDF'), dict(name='Sol', hex='EDC07C'), dict(name='Verde-água', hex='84C1BC'), dict(name='Azul Oceano', hex='055E89'), dict(name='Vermelho Coral', hex='C53D30')],
       [dict(family='Royale Couture Serif', svg='royale', use='Detalhes e assinaturas', weights='Regular'),
        dict(family='Lato', live="'Lato'", w=300, sample='Beach & Swimwear', use='Textos e títulos', weights='Light, Regular')])
stack(n, nm, (A + 'aquarie/05-tags.jpg', 'Etiquetas'), (A + 'aquarie/07-instagram.jpg', 'Instagram'))

# ================= 07 ZOUTI (4) =================
n, nm = '07', 'Zouti'; START[n] = len(pages) + 1
opener(n, nm, 'Templates de redes sociais que transformam funcionalidades de produto em posts com cara de lançamento.',
       [('Cliente', 'Zouti'), ('Papel', 'Design'), ('Escopo', 'Templates, sistema visual e cenas de produto')],
       A + 'zouti/capa.jpg')
concept(n, nm, 'Sistema', 'O produto vira a imagem.',
        '<p>Fundo quase preto, vidro fosco, uma luz verde-limão pela borda e a interface real do produto no lugar de ilustrações genéricas. Regras fixas, replicáveis pelo time.</p>',
        tile(A + 'zouti/logo.svg', '141414', 'w35'))
system(n, nm, 'A luz é a única cor. Space Grotesk nos títulos; Inter no apoio.',
       [dict(name='Verde Zouti', hex='E4FF00'), dict(name='Verde Lima', hex='BCCF1C'), dict(name='Verde Claro', hex='D7DF75'), dict(name='Grafite', hex='141414'), dict(name='Branco', hex='FFFFFF')],
       [dict(family='Space Grotesk', live="'Space Grotesk'", w=400, sample='Parcelamento', use='Títulos e etiquetas', weights='Regular, Medium'),
        dict(family='Inter', live="'Inter'", w=300, sample='Suas vendas', use='Apoio e interface', weights='Light a Bold')])
grid4(n, nm, [A + 'zouti/parcelamento.jpg', A + 'zouti/taxas.jpg', A + 'zouti/app-vendas.jpg', A + 'zouti/pixel.jpg'],
      'Templates', 'Cada post, uma única ideia.', 'portrait')

# ================= 08 BE BRAVE (4) =================
n, nm = '08', 'Be Brave Lab'; START[n] = len(pages) + 1
opener(n, nm, 'Uma identidade com coragem de sobra para uma agência audiovisual que disputa atenção em segundos.',
       [('Cliente', 'Be Brave Lab'), ('Segmento', 'Agência audiovisual'), ('Papel', 'Design de marca'), ('Escopo', 'Símbolo, identidade e aplicações')],
       A + 'be-brave/caixa.jpg')
concept(n, nm, 'Conceito', 'Duas formas que se abrem como asas: impulso.',
        '<p>Reconhecível em thumbnails, vinhetas e redes. Formas espelhadas se encontram no centro e se abrem — a imagem de quem avança sem pedir licença.</p>',
        tile(A + 'be-brave/logo.svg', 'FFFFFF', 'w75'))
stack(n, nm, (A + 'be-brave/construcao.jpg', 'Grid de construção'), (A + 'be-brave/3d.jpg', 'Símbolo em 3D'),
      'Construção', 'Um grid de círculos e linhas paralelas: do ícone de perfil à animação 3D.')
system(n, nm, 'Laranja como assinatura, azul profundo como contraponto. Monument Extended para escala e ambição.',
       [dict(name='Laranja Brave', hex='FA4C05'), dict(name='Azul Profundo', hex='0D0B9D'), dict(name='Off-white', hex='EFEFEF'), dict(name='Preto', hex='0F0F0F')],
       [dict(family='PP Monument Extended', svg='monument', use='Títulos, thumbnails e motion', weights='Regular, Black'),
        dict(family='Helvetica Neue LT Pro', svg='helvetica', use='Texto e informações', weights='Light a Bold')])

# ================= 09 FUNNEL BUILDER (4) =================
n, nm = '09', 'Funnel Builder'; START[n] = len(pages) + 1
opener(n, nm, 'Marca e sistema de lançamento para formar construtores de funis de venda.',
       [('Cliente', 'Bilhon'), ('Ano', '2024 — 2025'), ('Papel', 'Head de Design'), ('Escopo', 'Símbolo, ícone, sistema visual e criativos')],
       A + 'funnel-builder/logo-3d.jpg')
page(f'''<div class="txt"><span class="kicker">Conceito</span><p class="statement">Um F desenhado a partir de um funil.</p>
    <div class="body"><p>Um triângulo invertido construído sobre diagonais paralelas: movimento e fluxo, como um cliente que avança etapa por etapa.</p></div></div>
  <div class="duo">{fig(A + 'funnel-builder/construcao.jpg', 'Construção')}{fig(A + 'funnel-builder/icone.jpg', 'Ícone do app')}</div>''', 'p-concept', (n, nm))
system(n, nm, 'Escuro, com luz azul e acentos em amarelo: o time produziu em escala sem perder consistência.',
       [dict(name='Preto Profundo', hex='030A09'), dict(name='Azul Noturno', hex='002D51'), dict(name='Azul Luz', hex='5BBED9'), dict(name='Amarelo Bônus', hex='FFDE37'), dict(name='Grafite', hex='0E0F0F'), dict(name='Branco Gelo', hex='F0F2F8')],
       [dict(family='Inter', live="'Inter'", w=700, sample='Funnel Builder', use='Marca, títulos e interface', weights='Regular a Bold'),
        dict(family='Aspekta', svg='aspekta', use='Títulos de página', weights='400, 500, 600')])
grid4(n, nm, [A + 'funnel-builder/mobile.jpg', A + 'funnel-builder/funis.jpg', A + 'funnel-builder/bonus.jpg', A + 'funnel-builder/logo-3d.jpg'],
      'Resultado', '<b>R$ 30 milhões</b> em faturamento no lançamento, com um time que liderei.', 'portrait')

# ================= CONTATO + CONTRACAPA =================
page('''<div class="end"><span class="kicker">Contato</span><p class="statement">Obrigada.</p>
  <dl class="meta meta--end"><dt>WhatsApp</dt><dd>+55 19 97116-3478</dd><dt>Site</dt><dd>isadoracamargo.com.br</dd>
  <dt>LinkedIn</dt><dd>in/isadora-camargo-86a217266</dd><dt>Instagram</dt><dd>@isaccamargo__</dd></dl></div>''', 'p-end')
page('<span class="cover-site">isadoracamargo.com.br</span>', 'p-back')

# ---------- índice ----------
idx = ''.join(f'<li><span class="i-num">{n}</span><span class="i-name">{nm}<small>{t}</small></span><span class="i-page">{START[n]:02d}</span></li>' for n, nm, t in PROJ)
pages[1] = (f'<span class="kicker">Índice</span><ol class="idx">{idx}</ol>', 'p-index', None)

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
