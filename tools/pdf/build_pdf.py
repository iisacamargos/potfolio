# Portfólio impresso (PDF A4 paisagem) a partir dos mesmos assets do site.
# Gera print/portfolio.html; tools/pdf/render.mjs transforma em PDF.
# Uso: python3 tools/pdf/build_pdf.py && node tools/pdf/render.mjs
import os, html as H
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = '../assets/img/'
V = '../assets/video/'

def esc(s): return H.escape(s, quote=False)

def lum(hx):
    r, g, b = (int(hx[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def on(hx): return '#1a1a1a' if lum(hx) > 0.35 else '#f4f1ea'

def rgb(hx): return ' '.join(str(int(hx[i:i+2], 16)) for i in (0, 2, 4))

# ---------- componentes ----------
pages = []          # (html, folio?) ; folio = (num, nome) ou None
def page(body, cls='', folio=None, style=''):
    pages.append((body, cls, folio, style))

def palette(items, cmyk=False):
    out = ''
    for c in items:
        hx = c['hex']
        codes = f'<span>HEX #{hx}</span><span>RGB {rgb(hx)}</span>'
        if c.get('cmyk'): codes += f'<span>CMYK {c["cmyk"]}</span>'
        if c.get('pantone'): codes += f'<span>PANTONE {c["pantone"]}</span>'
        edge = ' chip--edge' if lum(hx) > 0.75 else ''
        out += (f'<div class="chip{edge}" style="background:#{hx};color:{on(hx)}">'
                f'<b>{esc(c["name"])}</b><div class="codes">{codes}</div></div>')
    return f'<div class="palette">{out}</div>'

def typeset(items):
    out = ''
    for t in items:
        if t.get('svg'):
            spec = f'<img class="type-svg" src="{A}type/{t["svg"]}.svg" alt="">'
        else:
            spec = f'<p class="type-live" style="font-family:{t["live"]};font-weight:{t.get("w", 500)}">{esc(t.get("sample", t["family"]))}</p>'
        out += (f'<div class="type-row"><div class="type-spec">{spec}</div>'
                f'<dl><dt>Família</dt><dd>{esc(t["family"])}</dd><dt>Uso</dt><dd>{esc(t["use"])}</dd>'
                f'<dt>Pesos</dt><dd>{esc(t["weights"])}</dd></dl></div>')
    return f'<div class="types">{out}</div>'

def meta(items):
    return '<dl class="meta">' + ''.join(f'<dt>{k}</dt><dd>{esc(v)}</dd>' for k, v in items) + '</dl>'

def fig(src, cap='', cls='', pos=''):
    st = f' style="object-position:{pos}"' if pos else ''
    c = f'<figcaption>{esc(cap)}</figcaption>' if cap else ''
    return f'<figure class="fig {cls}"><img src="{src}"{st} alt="">{c}</figure>'

# ---------- páginas-modelo ----------
def opener(num, name, client_line, lede, items, img, color, ink=None, pos='center'):
    ink = ink or on(color)
    page(f'''
      <div class="open-panel" style="background:#{color};color:{ink}">
        <span class="open-num">{num}</span>
        <div>
          <h2 class="open-name">{name}</h2>
          <p class="open-lede">{esc(lede)}</p>
          {meta(items)}
        </div>
      </div>
      <div class="open-img"><img src="{img}" style="object-position:{pos}" alt=""></div>''', 'p-open')

def concept(num, name, label, statement, body, right, folio=True):
    page(f'''
      <div class="concept-text">
        <span class="kicker">{label}</span>
        <p class="statement">{statement}</p>
        <div class="body">{body}</div>
      </div>
      <div class="concept-right">{right}</div>''', 'p-concept', (num, name))

def system(num, name, intro, pal, types, cmyk=False):
    page(f'''
      <div class="sys-head"><span class="kicker">Sistema visual</span><p class="sys-intro">{intro}</p></div>
      <div class="sys-block sys-block--pal"><span class="kicker kicker--sm">Paleta</span>{palette(pal)}</div>
      <div class="sys-block"><span class="kicker kicker--sm">Tipografia</span>{typeset(types)}</div>''', 'p-system', (num, name))

def full(src, cap='', pos='center', dark=True):
    page(fig(src, cap, 'fig--full', pos), 'p-full')

def duo(num, name, a, b, text=''):
    t = f'<p class="strip-text">{text}</p>' if text else ''
    page(f'{t}<div class="row row--2">{fig(*a)}{fig(*b)}</div>', 'p-grid', (num, name))

def stack(num, name, a, b, text='', label=''):
    k = f'<span class="kicker">{label}</span>' if label else ''
    page(f'''<div class="side">{k}<p class="side-text">{text}</p></div>
      <div class="stack">{fig(*a)}{fig(*b)}</div>''', 'p-stack', (num, name))

def quad(num, name, imgs, label, text, cls='q-square'):
    page(f'''<div class="side"><span class="kicker">{label}</span><p class="side-text">{text}</p></div>
      <div class="quad {cls}">{''.join(fig(*i) for i in imgs)}</div>''', 'p-quad', (num, name))

def row4(num, name, imgs, label, text):
    page(f'''<div class="row4-head"><span class="kicker">{label}</span><p class="side-text">{text}</p></div>
      <div class="row4">{''.join(fig(*i) for i in imgs)}</div>''', 'p-row4', (num, name))

def feature(num, name, src, label, text, pos='center', cap=''):
    page(f'''<div class="feat-img">{fig(src, cap, 'fig--fill', pos)}</div>
      <div class="side"><span class="kicker">{label}</span><p class="side-text">{text}</p></div>''', 'p-feature', (num, name))

# ---------- dados compartilhados ----------
UNIVERS = dict(family='Univers Next Pro', svg='univers', use='Títulos e mistura de pesos na mesma palavra', weights='Ultra Light a Extra Black')
ROSLINDALE = dict(family='Roslindale Display Narrow', svg='roslindale', use='Títulos editoriais', weights='Light, Regular, Medium, SemiBold')
MARGEM = dict(family='Margem', svg='margem', use='Texto corrido e detalhes', weights='Medium, Bold, Extra Bold, Black')
NT = dict(cd=dict(name='Cloud Dancer', hex='F0EFEB', pantone='11-4201 TCX'), ms=dict(name='My Soul', hex='020305', pantone='19-4010 TCX'),
          ot=dict(name='Orange Tiger', hex='F96714', pantone='16-1358 TCX'), rp=dict(name='Red Pink', hex='FB2A54'),
          tb=dict(name='Tropical Breeze', hex='87CDE7', pantone='13-4307 TCX'), ft=dict(name='First Tree', hex='00733C', pantone='18-6031 TCX'),
          il=dict(name='Illuminating', hex='F6EA60', pantone='13-0647 TCX'))

PROJ = [('01', 'Novo Traço', 'Identidade visual · Sistema de marca'),
        ('02', 'Orquestra Novo Traço', 'Símbolo · Submarca'),
        ('03', 'NT Records', 'Submarca · Gravadora · Merch'),
        ('04', 'NT Sessions', 'Identidade · Capas · Cenografia'),
        ('05', 'ANJU MACE', 'Identidade visual · Símbolos'),
        ('06', 'Aquarie', 'Identidade visual · Ilustração'),
        ('07', 'Zouti', 'Sistema de templates · Social'),
        ('08', 'Be Brave Lab', 'Símbolo · Identidade visual'),
        ('09', 'Funnel Builder', 'Marca · Sistema de lançamento')]
START = {}

# ================= CAPA =================
page(f'''
  <div class="cover-top"><span>Portfólio</span><span>2026</span></div>
  <h1 class="cover-name">Isadora<br>Camargo</h1>
  <div class="cover-foot">
    <p>Designer · Identidade visual, sistemas de marca e direção de arte</p>
    <p>São Paulo, SP</p>
  </div>''', 'p-cover')

# índice (preenchido depois, quando as páginas já foram contadas)
page('__INDEX__', 'p-index')

# ================= 01 NOVO TRAÇO =================
n, nm = '01', 'Novo Traço'; START[n] = len(pages) + 1
opener(n, nm, '', 'Uma marca-mãe para um grupo de arte e música: a expressividade brasileira traduzida em traço, cor e contraste.',
       [('Cliente', 'Novo Traço'), ('Ano', '2025 — 2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Identidade, sistema de marca, submarcas, guidelines e digital')],
       A + 'novo-traco/nt-ecobag.jpg', 'F6EA60', pos='center 40%')
concept(n, nm, 'Conceito', 'Contrastes e expressividade.',
        '<p>A identidade nasce da expressividade como linguagem vital do povo brasileiro, onde a arte é ferramenta de sobrevivência, comunicação e identidade. Erudito e popular, tradição e ruptura, dor e celebração: os contrastes refletem a miscigenação cultural que gera impacto emocional e conexão real.</p>'
        '<p>O desafio era reunir projetos muito diferentes — educação, música ao vivo, orquestra e gravadora — sob uma mesma voz, sem apagar a personalidade de cada um.</p>',
        fig(V + 'novo-traco-logo.jpg', 'Assinatura manuscrita Novo Traço', 'fig--fill'))
feature(n, nm, V + 'novo-traco-making-1.jpg', 'Feito à mão',
        'Os traços da marca não foram desenhados no computador. Nasceram de uma dinâmica com a equipe no Rio de Janeiro: cada pessoa traçou com marcador, pincel e tinta, e esse material virou a base gráfica da identidade. Uma expressividade genuína, impossível de simular digitalmente.',
        cap='Dinâmica dos traços com a equipe, Rio de Janeiro')
duo(n, nm, (V + 'novo-traco-making-2.jpg', 'Captação dos traços: marcador e pincel sobre papel'), (A + 'novo-traco/nt-poster.jpg', 'Cartaz-manifesto com os traços, desenhos e assinaturas da equipe'),
    'Do gesto ao sistema: cada submarca escolhe suas cores dentro da paleta e ganha um traço próprio.')
system(n, nm, 'Uma paleta ampla de propósito e uma paleta tipográfica: cada segmento de comunicação tem sua voz, e a Univers permite misturar pesos dentro da mesma palavra.',
       [NT[k] for k in ('cd', 'ms', 'ot', 'rp', 'tb', 'ft', 'il')], [UNIVERS, ROSLINDALE, MARGEM])
full(A + 'novo-traco/nt-livro.jpg')
stack(n, nm, (A + 'novo-traco/nt-cartazes.jpg', 'Cartazes NT Academy e NT Music Sessions'), (A + 'novo-traco/nt-stories.jpg', 'Stories de agenda de shows'),
      'O sistema hoje sustenta toda a comunicação do grupo, dos eventos ao digital. Como diretora de arte, coordeno um time de três designers e desenvolvo os manuais e guidelines que mantêm a marca consistente entre equipes e parceiros.', 'Aplicações')

# ================= 02 ORQUESTRA =================
n, nm = '02', 'Orquestra Novo Traço'; START[n] = len(pages) + 1
opener(n, 'Orquestra<br>Novo Traço', '', 'Uma orquestra que toca com artistas da música urbana, com identidade nascida da partitura e do traço da marca-mãe.',
       [('Cliente', 'Novo Traço'), ('Ano', '2025 — 2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Símbolo, identidade, eventos e vestuário')],
       A + 'novo-traco/orq-mockup.jpg', 'F0EFEB')
concept(n, nm, 'Conceito', 'Uma partitura: clareza, elegância e respiro.',
        '<p>A identidade deriva da marca-mãe, com mais espaço em branco e predominância do preto sobre fundo claro, numa leitura que remete à partitura musical.</p>'
        '<p>O símbolo nasceu da observação: a equipe já chamava a orquestra de “ONT”, e a sigla foi adotada oficialmente. As letras se apoiam fisicamente umas nas outras, como os instrumentos de uma orquestra, em que nenhum atua isolado.</p>',
        fig(V + 'orquestra-simbolo.jpg', 'Símbolo ONT', 'fig--fill', 'center'))
system(n, nm, 'Três cores e duas famílias: a Roslindale traz o refinamento de um programa de concerto; a Margem organiza as informações.',
       [NT['ms'], NT['cd'], NT['il']], [dict(ROSLINDALE, use='Títulos e nomes'), MARGEM])
full(V + 'orquestra-evento.jpg')
duo(n, nm, (A + 'novo-traco/orq-moletom-branco.jpg', 'Símbolo bordado no peito'), (A + 'novo-traco/orq-moletom-preto.jpg', 'Símbolo em escala nas costas'),
    'O traço feito à mão permanece no logotipo, no símbolo e nas aplicações: unidade com o grupo e caráter autoral.')
full(A + 'novo-traco/orq-foto.jpg', pos='center 40%')

# ================= 03 NT RECORDS =================
n, nm = '03', 'NT Records'; START[n] = len(pages) + 1
opener(n, nm, '', 'A gravadora do grupo: o traço da marca-mãe ganha tinta spray, textura urbana e um grid que dá solidez.',
       [('Cliente', 'Novo Traço'), ('Ano', '2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Símbolo, identidade, papelaria, merch e digital')],
       A + 'novo-traco/rec-camiseta.jpg', '003AE7', pos='center 35%')
concept(n, nm, 'Conceito', 'Do pincel à tinta spray. Do traço livre ao grid.',
        '<p><i>Existir para que a música que nasceu no palco e no estúdio da Novo Traço continue acessível depois da luz apagar.</i></p>'
        '<p>A gravadora mantém o traço do grupo, mas troca o pincel pela tinta spray, para ganhar urbanidade e textura. Linhas retas funcionam como grid estruturante e trazem a seriedade de uma marca sólida.</p>',
        fig(V + 'nt-records-logo.jpg', 'Símbolo e traço circular em spray', 'fig--fill'))
full(A + 'novo-traco/rec-linhas.jpg')
system(n, nm, 'Uma paleta enxuta de preto, azul e branco equilibra autoridade e confiança e deixa o spray como protagonista. A Univers, da marca-mãe, é usada com mais rigor e menos contraste de pesos.',
       [NT['ms'], dict(name='Azul Records', hex='003AE7'), NT['cd']], [dict(UNIVERS, use='Toda a comunicação: títulos, créditos e texto')])
full(A + 'novo-traco/rec-papelaria.jpg')
duo(n, nm, (A + 'novo-traco/rec-cartao.jpg', 'Cartão de visita com textura de carimbo'), (A + 'novo-traco/rec-placa.jpg', 'Placa de 1 milhão de streams'),
    'Papelaria e reconhecimento: o símbolo assina com discrição, o spray entra como textura.')
duo(n, nm, (A + 'novo-traco/rec-estampa.jpg', 'Estampa: disco pintado em spray'), (A + 'novo-traco/rec-hoodie-preto.jpg', 'Hoodie com manchas de spray'),
    'Merch: o disco pintado vira estampa grande; o hoodie e a garrafa assinam só com o símbolo e o traço.')
full(A + 'novo-traco/rec-tote-1.jpg')
full(A + 'novo-traco/rec-posts.jpg')

# ================= 04 NT SESSIONS =================
n, nm = '04', 'NT Sessions'; START[n] = len(pages) + 1
opener(n, nm, '', 'A orquestra encontra a música urbana: sessões gravadas, EPs e um show esgotado no Theatro Municipal do Rio.',
       [('Cliente', 'Novo Traço'), ('Ano', '2026'), ('Papel', 'Direção de arte'), ('Escopo', 'Identidade, capas, motion, cenografia em LED e digital')],
       A + 'nt-sessions/live-teatro-vermelho.jpg', 'F6EA60')
concept(n, nm, 'Identidade', 'Um selo feito à mão que assina sem disputar espaço com o artista.',
        '<p>Cada edição é uma collab entre a Orquestra Novo Traço e um artista urbano: o repertório ganha arranjos para orquestra, é gravado em sessão e vira EP. Já passaram L7NNON e Papatinho, MC Pedrinho e Froid.</p>'
        '<p>O logo nasce do mesmo gesto da marca-mãe: N e t pintados à mão, presos num quadro como um carimbo, com SESSIONS numa faixa sólida.</p>',
        f'<div class="logo-tile" style="background:#F6EA60"><img src="{A}nt-sessions/logo.svg" alt=""></div>')
system(n, nm, 'Capas em preto e branco com grão, recortes de colagem, contorno amarelo e um traço à mão que atravessa a composição: cada artista ganha seu universo, e a coleção se reconhece de longe.',
       [NT['il'], NT['ms'], NT['cd'], NT['tb']], [dict(UNIVERS, use='Logo, nomes de artistas e informações das capas')])
quad(n, nm, [(A + 'nt-sessions/pedrinho-rua.jpg',), (A + 'nt-sessions/pedrinho-violino.jpg',), (A + 'nt-sessions/pedrinho-tv.jpg',), (A + 'nt-sessions/pedrinho-sorriso.jpg',)],
     'Capas · MC Pedrinho', 'Quatro faixas do funk de MC Pedrinho com a orquestra. As capas misturam a rua e a sala de concerto: carros populares e a batuta do maestro, o violino no lugar do microfone, a TV de tubo e a multidão do baile.')
quad(n, nm, [(A + 'nt-sessions/froid-sol.jpg',), (A + 'nt-sessions/froid-partitura.jpg',), (A + 'nt-sessions/froid-espelho.jpg',), (A + 'nt-sessions/froid-janela.jpg',)],
     'Capas · Froid', 'Na edição com Froid, o grão e o alto contraste ficam mais densos e introspectivos: o perfil contra pinceladas amarelas, a partitura refletida nas lentes, o violino entre cacos de espelho.')
feature(n, nm, V + 'nts-testeira.jpg', 'NT Sessions Live',
        'No palco do Theatro Municipal, a identidade virou cenografia: testeira, painéis de LED e telão animados com os traços à mão, num sistema de amarelo e azul sobre preto que conversa com a arquitetura do teatro.<br><br><b class="big-num">15 min</b>para esgotar os ingressos.',
        cap='Testeira animada de palco')
full(A + 'nt-sessions/live-lanternas.jpg')
duo(n, nm, (A + 'nt-sessions/live-palco.jpg', 'L7NNON e Papatinho com a orquestra'), (A + 'nt-sessions/live-papatinho.jpg', 'Símbolo em LED na mesa de produção'))
full(A + 'nt-sessions/live-teatro-dourado.jpg')

# ================= 05 ANJU MACE =================
n, nm = '05', 'ANJU MACE'; START[n] = len(pages) + 1
opener(n, nm, '', 'Uma identidade para o fitness feminino construída sobre o equilíbrio entre força e leveza, técnica e sensibilidade.',
       [('Cliente', 'ANJU MACE'), ('Ano', '2025'), ('Papel', 'Direção de arte e coordenação da equipe'), ('Escopo', 'Identidade, símbolos, brandbook, aplicações e digital')],
       A + 'anju-mace/01-capa.jpg', '7A8569', ink='#F5F5DD')
logos = ''.join(f'<div class="logo-cell" style="background:#{bg}"><img src="{A}anju-mace/logos/{f}.svg" alt=""></div>'
                for f, bg in [('horizontal-grafite', 'F5F5DD'), ('vertical-grafite', 'E6E6AD'), ('empilhada-salvia', '262626'), ('horizontal-amarelo', '7A8569')])
concept(n, nm, 'Conceito', 'Força e leveza. O refinamento está na disciplina.',
        '<p>O fitness feminino costuma se comunicar pelo excesso: cores saturadas, promessas rápidas, estética de esforço. A marca precisava falar de precisão técnica e resultado duradouro com a calma de uma marca de luxo consciente.</p>'
        '<p>A assinatura em caixa-alta, com espaçamento generoso e contraste de peso entre ANJU e MACE, equilibra autoridade e respiro. Horizontal, vertical e empilhada são extensões da mesma assinatura.</p>',
        f'<div class="logo-grid">{logos}</div>')
syms = [('alvo', 'Excelência como auto-respeito', 'Um alvo: precisão, foco, disciplina e domínio técnico.'),
        ('elo', 'Mudança real e duradoura', 'Um elo entre passado e futuro: transformação que permanece.'),
        ('mola', 'Inteligência feminina', 'Uma mola que impulsiona: influência, liderança e inspiração.'),
        ('bolha', 'Conhecimento é libertação', 'A saída de uma bolha: quebrar padrões e criar o próprio caminho.'),
        ('orbitas', 'Funcionalidade e beleza', 'Órbitas em equilíbrio: harmonia entre forma e função.')]
page(f'''<div class="sym-head"><span class="kicker">Símbolos</span><p class="side-text">Cinco símbolos de traço fino traduzem os pilares da marca em forma. Juntos, funcionam como um alfabeto gráfico para embalagens, conteúdo e produto digital.</p></div>
  <div class="syms">{''.join(f'<div class="sym"><img src="{A}anju-mace/simbolos/{s}.svg" alt=""><b>{t}</b><p>{d}</p></div>' for s, t, d in syms)}</div>''', 'p-syms', (n, nm))
system(n, nm, 'Neutros naturais — creme, oliva e sálvia — comunicam calma e autocuidado; o grafite ancora e o amarelo suave injeta energia controlada. Lexend assina com precisão; Outfit suaviza o texto.',
       [dict(name='Preto Grafite', hex='262626', cmyk='72 65 64 69'), dict(name='Verde Oliva', hex='7A8569', cmyk='54 36 62 10'),
        dict(name='Verde Sálvia', hex='9EAB87', cmyk='41 23 53 1'), dict(name='Creme Neutro', hex='F5F5DD', cmyk='3 1 15 0'),
        dict(name='Amarelo Suave', hex='E6E6AD', cmyk='11 3 39 0')],
       [dict(family='Lexend', live="'Lexend'", w=300, sample='ANJU MACE', use='Logotipo e títulos', weights='Thin, Light, Bold, Black'),
        dict(family='Outfit', live="'Outfit'", w=400, sample='Força e leveza', use='Textos, interface e apoio', weights='Light, Regular, Medium')])
full(A + 'anju-mace/06-simbolos.jpg')
duo(n, nm, (A + 'anju-mace/07-aplicacoes.jpg', 'Vestuário, embalagem e redes'), (A + 'anju-mace/08-app.jpg', 'Aplicativo de treino'),
    'A assinatura vertical vira estampa, os símbolos viram padrão, e a paleta natural mantém tudo reconhecível mesmo sem o logo.')
feature(n, nm, A + 'anju-mace/09-site.jpg', 'Resultado',
        'A identidade foi lançada junto com o aplicativo de treino, hoje no ar. A cliente disse que ninguém nunca tinha entendido a essência dela tão bem, e as alunas se identificaram de imediato com a nova marca.',
        cap='Site e produto digital')

# ================= 06 AQUARIE =================
n, nm = '06', 'Aquarie'; START[n] = len(pages) + 1
opener(n, nm, '', 'Moda praia de Santa Catarina com o verão do sul da Itália como referência: serifas elegantes, gravura e uma paleta de sol, mar e areia.',
       [('Cliente', 'Aquarie Beach & Swimwear'), ('Ano', '2025'), ('Papel', 'Designer de marca'), ('Escopo', 'Identidade, ilustrações, tipografia e aplicações')],
       A + 'aquarie/06-ecobag.jpg', '055E89')
concept(n, nm, 'Conceito', 'Um verão mediterrâneo clássico, longe do óbvio tropical.',
        '<p>Num mercado em que o beachwear segue a mesma estética tropical, a marca precisava de um toque mais sofisticado. A referência veio das praias do sul da Itália: listras de guarda-sóis, padronagens e ilustrações clássicas.</p>'
        '<p>O logotipo em serifa de alto contraste ganha curvas que lembram o movimento da água, como na barra do A e na cauda do Q.</p>',
        f'<div class="logo-tile" style="background:#F1EBDF"><img class="w70" src="{A}aquarie/logo.svg" alt=""></div>')
feature(n, nm, A + 'aquarie/02-detalhe.jpg', 'Desenho de letra',
        'A cauda do Q se estende como uma onda e conduz o olhar pela palavra. O detalhe vira elemento gráfico autônomo, recortado pela borda nas etiquetas e nas peças.',
        cap='Detalhe do logotipo: a curva da água')
page(f'''<div class="side"><span class="kicker">Ilustrações</span><p class="side-text">Um conjunto em traço de gravura, numa única cor, constrói o universo da marca: concha, cavalo-marinho, barco, coqueiro, guarda-sol, cadeira e a janela para o mar. Funcionam sozinhas, como símbolo, ou juntas, como padrão.</p></div>
  <div class="illu">{fig(A + 'aquarie/03-ilustracoes.jpg', '', 'illu-main')}{fig(A + 'aquarie/concha.jpg')}{fig(A + 'aquarie/cavalo-marinho.jpg')}{fig(A + 'aquarie/janela.jpg')}</div>''', 'p-illu', (n, nm))
system(n, nm, 'A areia como base, o amarelo do sol, o verde-água, o azul profundo do oceano e o vermelho coral nas listras. Royale Couture Serif dá o tom de alfaiataria; Lato sustenta os textos.',
       [dict(name='Areia', hex='F1EBDF'), dict(name='Sol', hex='EDC07C'), dict(name='Verde-água', hex='84C1BC'), dict(name='Azul Oceano', hex='055E89'), dict(name='Vermelho Coral', hex='C53D30')],
       [dict(family='Royale Couture Serif', svg='royale', use='Pequenos detalhes e assinaturas', weights='Regular'),
        dict(family='Lato', live="'Lato'", w=300, sample='Beach & Swimwear', use='Textos e títulos', weights='Light, Regular')])
duo(n, nm, (A + 'aquarie/05-tags.jpg', 'Etiquetas: logotipo vertical e concha recortada'), (A + 'aquarie/07-instagram.jpg', 'Instagram: a concha basta para reconhecer a marca'))

# ================= 07 ZOUTI =================
n, nm = '07', 'Zouti'; START[n] = len(pages) + 1
opener(n, nm, '', 'Um sistema de templates para redes sociais que transforma funcionalidades de produto em posts com cara de lançamento.',
       [('Cliente', 'Zouti'), ('Papel', 'Design'), ('Escopo', 'Templates de redes sociais, sistema visual e cenas de produto')],
       A + 'zouti/capa.jpg', '141414', ink='#E4FF00')
concept(n, nm, 'Sistema', 'O produto vira a imagem.',
        '<p>Checkout, parcelamento, área de membros, app, reembolsos, pixel, integrações: muitas funcionalidades para comunicar, todas soando como a mesma marca, e replicáveis pelo time com rapidez.</p>'
        '<p>Regras fixas: fundo quase preto, superfícies em vidro fosco, uma luz verde-limão que entra pela borda, etiqueta em caixa-alta espaçada e título em Space Grotesk com degradê do branco ao cinza. No lugar de ilustrações genéricas, as interfaces reais do produto.</p>',
        f'<div class="logo-tile" style="background:#141414"><img class="w40" src="{A}zouti/logo.svg" alt=""></div>')
system(n, nm, 'Uma escala de verdes sobre grafite: a luz é a única cor. Space Grotesk nos títulos e etiquetas; Inter no texto de apoio e na interface.',
       [dict(name='Verde Zouti', hex='E4FF00'), dict(name='Verde Lima', hex='BCCF1C'), dict(name='Verde Claro', hex='D7DF75'), dict(name='Grafite', hex='141414'), dict(name='Branco', hex='FFFFFF')],
       [dict(family='Space Grotesk', live="'Space Grotesk'", w=400, sample='Parcelamento Inteligente', use='Títulos e etiquetas', weights='Regular, Medium'),
        dict(family='Inter', live="'Inter'", w=300, sample='Suas vendas na palma da mão', use='Textos de apoio e interface', weights='Light, Medium, Semi Bold, Bold')])
row4(n, nm, [(A + 'zouti/parcelamento.jpg',), (A + 'zouti/taxas.jpg',), (A + 'zouti/app-vendas.jpg',), (A + 'zouti/mobile.jpg',)],
     'Templates', 'Cada post apresenta uma única ideia.<small>Funcionalidade nomeada na etiqueta, uma cena de produto, uma luz.</small>')
row4(n, nm, [(A + 'zouti/area-membros.jpg',), (A + 'zouti/reembolso.jpg',), (A + 'zouti/pixel.jpg',), (A + 'zouti/metricas.jpg',)],
     'Templates', 'O feed inteiro se reconhece como Zouti.<small>Regras claras de cor, luz e composição: novas funcionalidades entram sem reinventar o layout.</small>')

# ================= 08 BE BRAVE =================
n, nm = '08', 'Be Brave Lab'; START[n] = len(pages) + 1
opener(n, nm, '', 'Uma identidade com coragem de sobra para uma agência audiovisual que disputa atenção em segundos.',
       [('Cliente', 'Be Brave Lab'), ('Segmento', 'Agência audiovisual'), ('Papel', 'Design de marca'), ('Escopo', 'Símbolo, identidade, tipografia e aplicações')],
       A + 'be-brave/caixa.jpg', 'FA4C05')
concept(n, nm, 'Conceito', 'Duas formas que se abrem como asas: impulso.',
        '<p>Num ambiente viral, a marca precisava ser reconhecível em thumbnails, vinhetas e redes, e comunicar coragem, presença e confiança.</p>'
        '<p>Duas formas espelhadas se encontram no centro e se abrem como asas, a imagem de quem avança sem pedir licença.</p>',
        f'<div class="logo-tile" style="background:#EFEFEF"><img class="w70" src="{A}be-brave/logo.svg" alt=""></div>')
feature(n, nm, A + 'be-brave/construcao.jpg', 'Construção',
        'O símbolo é construído sobre um grid de círculos e linhas paralelas. A geometria rigorosa garante que ele funcione do ícone de perfil à animação 3D.',
        cap='Grid de construção do símbolo')
system(n, nm, 'O laranja é a assinatura: energia e urgência. O azul profundo é o contraponto. A Monument Extended transmite escala e ambição e conversa com as formas do símbolo.',
       [dict(name='Laranja Brave', hex='FA4C05'), dict(name='Azul Profundo', hex='0D0B9D'), dict(name='Off-white', hex='EFEFEF'), dict(name='Preto', hex='0F0F0F')],
       [dict(family='PP Monument Extended', svg='monument', use='Títulos, thumbnails e motion', weights='Regular, Black'),
        dict(family='Helvetica Neue LT Pro', svg='helvetica', use='Texto corrido e informações', weights='45 Light, 55 Roman, 65 Medium, 75 Bold')])
full(A + 'be-brave/3d.jpg')
duo(n, nm, (A + 'be-brave/foto.jpg', 'Halftone e dither: a estética audiovisual na linguagem gráfica'), (A + 'be-brave/garrafas.jpg', 'Garrafas com símbolo e assinatura'))

# ================= 09 FUNNEL BUILDER =================
n, nm = '09', 'Funnel Builder'; START[n] = len(pages) + 1
opener(n, nm, '', 'Marca e sistema visual de lançamento para formar a primeira geração de construtores de funis de venda do Brasil.',
       [('Cliente', 'Bilhon'), ('Ano', '2024 — 2025'), ('Papel', 'Head de Design: marca e direção do lançamento'), ('Escopo', 'Símbolo, ícone, sistema visual, páginas e criativos')],
       A + 'funnel-builder/logo-3d.jpg', '002D51', pos='center 45%')
page(f'''<div class="side"><span class="kicker">Conceito</span><p class="statement statement--sm">Um F desenhado a partir de um funil.</p>
    <p class="side-text">O símbolo parte de um triângulo invertido. A construção sobre diagonais paralelas dá a sensação de movimento e fluxo: a mesma ideia de um cliente que avança etapa por etapa. Em 3D, com reflexos em azul-petróleo, virou o protagonista da campanha.</p></div>
  <div class="stack stack--h">{fig(A + 'funnel-builder/construcao.jpg', 'Construção sobre diagonais paralelas')}{fig(A + 'funnel-builder/icone.jpg', 'Ícone do aplicativo')}</div>''', 'p-stack', (n, nm))
system(n, nm, 'Um sistema escuro, com luz azul e acentos em amarelo, organiza página de vendas, bônus, criativos e app no mesmo grid: o time produziu em escala sem perder consistência.',
       [dict(name='Preto Profundo', hex='030A09'), dict(name='Grafite', hex='0E0F0F'), dict(name='Azul Noturno', hex='002D51'), dict(name='Azul Luz', hex='5BBED9'), dict(name='Amarelo Bônus', hex='FFDE37'), dict(name='Branco Gelo', hex='F0F2F8')],
       [dict(family='Inter', live="'Inter'", w=700, sample='Funnel Builder', use='Marca, títulos e interface', weights='Regular, Medium, SemiBold, Bold'),
        dict(family='Aspekta', svg='aspekta', use='Títulos de página e chamadas', weights='400, 500, 600')])
page(f'''<div class="row4-head"><span class="kicker">Resultado</span><p class="side-text"><b class="big-num">R$ 30 mi</b> em faturamento no lançamento.<small>Com um time interno de três pessoas e designers freelancers sob a minha liderança.</small></p></div>
  <div class="row4">{fig(A + 'funnel-builder/mobile.jpg')}{fig(A + 'funnel-builder/funis.jpg')}{fig(A + 'funnel-builder/bonus.jpg')}{fig(A + 'funnel-builder/logo-3d.jpg')}</div>''', 'p-row4', (n, nm))

# ================= CONTRACAPA =================
page('''
  <div class="cover-top"><span>Obrigada</span><span>2026</span></div>
  <h1 class="cover-name cover-name--sm">Vamos<br>conversar?</h1>
  <div class="contact">
    <div><span class="kicker kicker--sm">WhatsApp</span><p>+55 19 97116-3478</p></div>
    <div><span class="kicker kicker--sm">Portfólio</span><p>isadoracamargo.com.br</p></div>
    <div><span class="kicker kicker--sm">LinkedIn</span><p>in/isadora-camargo-86a217266</p></div>
    <div><span class="kicker kicker--sm">Instagram</span><p>@isaccamargo__</p></div>
  </div>''', 'p-cover p-back')

# ---------- índice ----------
idx = ''.join(f'<li><span class="i-num">{n}</span><span class="i-name">{nm}</span><span class="i-tags">{t}</span><span class="i-page">{START[n]:02d}</span></li>' for n, nm, t in PROJ)
pages[1] = (f'''<div class="idx-left"><span class="kicker">Índice</span>
  <dl class="meta meta--ink"><dt>Base</dt><dd>São Paulo, SP</dd><dt>Hoje</dt><dd>Diretora de Arte, Novo Traço</dd><dt>Foco</dt><dd>Identidade visual, sistemas de marca e direção de arte</dd></dl>
  <p class="idx-note">Uma seleção de identidades e sistemas visuais: o conceito por trás de cada marca, a construção técnica e as aplicações.</p></div>
  <ol class="idx">{idx}</ol>''', 'p-index', None, '')

# ---------- HTML ----------
body = ''
for i, (b, cls, folio, st) in enumerate(pages, 1):
    f = ''
    if folio:
        f = f'<footer class="folio"><span>Isadora Camargo — Portfólio 2026</span><span>{folio[0]} · {folio[1]}</span><span>{i:02d}</span></footer>'
    body += f'<section class="page {cls}"{f" style={chr(34)}{st}{chr(34)}" if st else ""}>{b}{f}</section>\n'

css = open(os.path.join(os.path.dirname(__file__), 'print.css')).read()
out = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Isadora Camargo — Portfólio 2026</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Lexend:wght@300;600&family=Outfit:wght@400&family=Space+Grotesk:wght@400;500&family=Inter:wght@300;700&family=Lato:wght@300&display=block" rel="stylesheet">
<style>{css}</style></head><body>
{body}</body></html>'''
os.makedirs(os.path.join(ROOT, 'print'), exist_ok=True)
open(os.path.join(ROOT, 'print/portfolio.html'), 'w').write(out)
print(len(pages), 'páginas')
