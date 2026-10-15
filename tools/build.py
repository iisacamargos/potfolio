# Gera as páginas dos cases (projetos/*.html) e, no fim, a versão em inglês.
# Uso: python3 tools/build.py
import json, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(os.path.dirname(HERE))
from ds import *
BASE='https://isadoracamargo.com.br'
def head(slug,title,desc,ogimg,ogw,ogh,ogalt,keywords,fonts=''):
    ld=[{"@context":"https://schema.org","@type":"CreativeWork","name":title+" — Identidade visual","headline":title+" — Identidade visual","description":desc,"image":f"{BASE}/{ogimg}","url":f"{BASE}/projetos/{slug}.html","inLanguage":"pt-BR","creator":{"@type":"Person","name":"Isadora Camargo","url":BASE+"/"},"keywords":keywords,"genre":"Identidade visual"},
        {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Isadora Camargo","item":BASE+"/"},{"@type":"ListItem","position":2,"name":title,"item":f"{BASE}/projetos/{slug}.html"}]}]
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — Isadora Camargo</title>
  <meta name="description" content="{desc}">
  <meta name="author" content="Isadora Camargo">
  <meta name="theme-color" content="#e8e4dc">
  <link rel="canonical" href="{BASE}/projetos/{slug}.html">

  <meta property="og:type" content="website">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:site_name" content="Isadora Camargo">
  <meta property="og:title" content="{title} — Isadora Camargo">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{BASE}/projetos/{slug}.html">
  <meta property="og:image" content="{BASE}/{ogimg}">
  <meta property="og:image:width" content="{ogw}">
  <meta property="og:image:height" content="{ogh}">
  <meta property="og:image:alt" content="{ogalt}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title} — Isadora Camargo">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{BASE}/{ogimg}">

  <link rel="icon" href="../favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="../assets/meta/favicon-32.png">
  <link rel="apple-touch-icon" href="../assets/meta/apple-touch-icon.png">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter+Tight:wght@500;700{fonts}&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../assets/css/style.css">
  <script type="application/ld+json">
{json.dumps(ld,ensure_ascii=False,indent=2)}
  </script>
</head>
<body>

  <header class="topbar">
    <div class="wrap">
      <a href="../">Isadora Camargo</a>
      <span>Designer · Identidade visual e branding</span>
      <nav>
        <a href="../#projetos">Projetos</a>
        <a href="../#sobre">Sobre</a>
        <a href="../#contato">Contato</a>
      </nav>
    </div>
  </header>

  <main class="wrap">
'''
def foot(nextslug,nextname):
    return f'''
    <a class="case-next" href="{nextslug}.html" data-cursor="Próximo">
      <span class="caps">Próximo projeto</span>
      <strong>{nextname} →</strong>
    </a>

  </main>

  <footer class="footer">
    <div class="wrap">
      <span>© 2026 Isadora Camargo</span>
      <span class="footer-links">
        <a href="https://www.instagram.com/isaccamargo__/" target="_blank" rel="me noopener">Instagram</a>
        <a href="https://www.linkedin.com/in/isadora-camargo-86a217266/" target="_blank" rel="me noopener">LinkedIn</a>
        <a href="mailto:isadoracamar@outlook.com">E-mail</a>
        <a href="https://wa.me/5519971163478" target="_blank" rel="noopener">WhatsApp</a>
      </span>
      <span>São Paulo, SP</span>
    </div>
  </footer>

  <script src="../assets/js/cursor.js" defer></script>
  <script src="../assets/js/vendor/lenis.min.js" defer></script>
  <script src="../assets/js/scroll.js" defer></script>
</body>
</html>
'''
def casehead(title,lede,facts):
    f=''.join(f'\n        <div><dt>{k}</dt><dd>{v}</dd></div>' for k,v in facts)
    return f'''
    <section class="case-head">
      <a class="case-back" href="../#projetos">← Todos os projetos</a>
      <h1 class="case-title">{title}</h1>
      <p class="case-lede">{lede}</p>

      <dl class="case-facts">{f}
      </dl>
    </section>
'''
n=[0]
def sec(title,body,cls='section-body prose'):
    n[0]+=1
    return f'''
    <section class="section section-grid">
      <span class="section-num">{n[0]:02d}</span>
      <h2 class="section-title">{title}</h2>
      <div class="{cls}">
        {body}
      </div>
    </section>
'''
def img(src,w,h,alt,bleed=True,lazy=True):
    c='media media--bleed' if bleed else 'media'
    return f'''
    <figure class="{c}">
      {picture(src,w,h,alt,' loading="lazy"' if lazy else ' fetchpriority="high"')}
    </figure>
'''
def vid(name,w,h,label,bleed=True,band=None,cls=''):
    c='media media--bleed' if bleed else 'media'
    if name in MOBILE_VIDEO: c+=' media--mcrop'
    if cls: c+=' '+cls
    st=''
    if band: c+=' media--band'; st=f' style="--band:{band}"'
    return f'''
    <figure class="{c}"{st}>
      <video class="autoplay" width="{w}" height="{h}" muted loop playsinline preload="none" poster="../assets/video/{name}.jpg" aria-label="{label}">
        <source src="../assets/video/{name}.webm" type="video/webm">
        <source src="../assets/video/{name}.mp4" type="video/mp4">
      </video>
    </figure>
'''
def grid(items):
    s='\n    <div class="media-grid">'
    for src,w,h,alt in items:
        s+='\n      <figure class="media">'+picture(src,w,h,alt,' loading="lazy"')+'</figure>'
    return s+'\n    </div>\n'
def sub(name,kicker):
    return f'''
    <div class="sub-head">
      <span class="caps">{kicker}</span>
      <h2 class="sub-title">{name}</h2>
    </div>
'''


# ============ NOVO TRAÇO ============
n[0]=0
h=head('novo-traco','Novo Traço','Identidade visual da Novo Traço, grupo de arte e música brasileiro: traços feitos à mão, uma paleta vibrante e uma paleta tipográfica. Projeto de Isadora Camargo.','assets/img/novo-traco/nt-ecobag.jpg',1920,1280,'Ecobag azul com a assinatura manuscrita Novo Traço e as palavras Arte, Música, Emoção, Alegria','identidade visual, sistema de marca, branding, música, cultura, direção de arte')
h+=casehead('Novo Traço','Uma marca-mãe para um grupo de arte e música: a expressividade brasileira traduzida em traço, cor e contraste.',
 [('Cliente','Novo Traço'),('Ano','2025 — 2026'),('Papel','Direção de arte'),('Escopo','Identidade visual, sistema de marca, submarcas, guidelines e digital')])
h+=vid('novo-traco-logo',1920,1080,'Animação do logo Novo Traço: traços à mão, palavras e desenhos em amarelo surgem e a assinatura manuscrita NOVO TRAÇO se escreve em branco sobre fundo escuro')
h+=sec('Contexto e desafio','''<p>A Novo Traço é um grupo de arte e cultura que reúne educação, música ao vivo e produção musical: NT Academy, NT Music Sessions, Jazz Proibidão, a <a class="link" href="orquestra-novo-traco.html">Orquestra Novo Traço</a> e a gravadora <a class="link" href="nt-records.html">NT Records</a>. Seu propósito é despertar e nutrir o espírito humano e impulsionar a prosperidade social através da potência da arte.</p>
        <p>O desafio era construir um sistema que reunisse projetos muito diferentes sob uma mesma voz, sem apagar a personalidade de cada um: do erudito da orquestra à urbanidade da gravadora.</p>''')
h+=sec('Conceito','''<p>Contrastes e expressividade. A identidade nasce da expressividade como linguagem vital do povo brasileiro, onde a arte é ferramenta de sobrevivência, comunicação e identidade. Seus contrastes, entre erudito e popular, tradição e ruptura, dor e celebração, refletem a miscigenação cultural que gera impacto emocional e conexão real.</p>''')
h+=sec('Feito à mão','<p>Os traços da marca não foram desenhados no computador. Eles nasceram de uma dinâmica com a equipe da Novo Traço no Rio de Janeiro: cada pessoa traçou com marcador, pincel e tinta, e esse material virou a base gráfica da identidade. É o que garante a expressividade genuína, impossível de simular digitalmente, e faz da marca algo construído pelas próprias pessoas que a vivem.</p>')
h+=vid('novo-traco-making-1',1920,1080,'Bastidores da dinâmica dos traços: mãos da equipe desenhando com marcador sobre papel, numa calçada à beira-mar no Rio de Janeiro')
h+=img('novo-traco/nt-poster.jpg',1684,1263,'Cartaz Novo Traço com um traço amarelo em zigue-zague, a assinatura manuscrita, desenhos de sol, pássaros e três telhados com coração, cifrão e nota musical, e assinaturas da equipe')
h+=sec('Cores e traços','''<p>As cores vivas funcionam como linguagem direta, refletindo a intensidade que atravessa a música, a arte e as ruas do Brasil. Os traços são feitos à mão, com tinta, e trazem para a identidade uma expressividade genuína, impossível de simular digitalmente.</p>
        <p>A paleta é ampla de propósito: cada submarca e cada projeto escolhe suas cores dentro dela e ganha um traço próprio, o que dá variedade ao sistema sem quebrar a unidade.</p>''')
h+=colors('Novo Traço',NT_COLORS,'HEX · RGB · Pantone',cols=4)
h+=vid('novo-traco-making-2',1920,1080,'Bastidores em preto e branco: marcador e pincel com tinta preta desenhando traços ondulados sobre papel')
h+=sec('Tipografia','''<p>Uma paleta tipográfica dá a cada segmento de comunicação sua própria voz. A Univers, com pesos do Ultra Light ao Extra Black, permite misturar pesos dentro da mesma palavra. A Roslindale Narrow traz o refinamento editorial dos títulos, e a Margem assume o texto corrido e os pequenos detalhes.</p>''')
h+=types('Novo Traço',[UNIVERS,ROSLINDALE,MARGEM])
h+=img('novo-traco/nt-livro.jpg',1920,939,'Box de livros com o propósito da Novo Traço na capa, um traço vermelho em espiral e lombadas com nomes de artistas em Univers')
h+=img('novo-traco/nt-cartazes.jpg',1920,1080,'Cartazes da NT Academy, com violoncelo em preto e branco e traço amarelo, e da NT Music Sessions, com cantora no palco e traço vermelho')
h+=img('novo-traco/nt-stories.jpg',1920,1133,'Dois stories de shows com data, nome do artista na vertical e local em serifa: Zé Ibarra na Casa Light e Josiel Konrad no Circo Voador')
h+=vid('novo-traco-agenda',1920,1080,'Post animado da agenda de fevereiro de 2026 da Novo Traço com traço laranja, mostrado no feed do Instagram')
h+=img('novo-traco/nt-ecobag.jpg',1920,1280,'Pessoa caminhando com ecobag azul estampada com a assinatura manuscrita Novo Traço e as palavras Arte, Música, Emoção, Alegria')
h+=sec('Resultado','''<p>O sistema hoje sustenta toda a comunicação do grupo, dos eventos ao digital, e cada novo projeto nasce dentro dele. Como diretora de arte, coordeno um time de três designers e desenvolvo os manuais e guidelines que mantêm a marca consistente entre equipes e parceiros.</p>''')
h+=foot('orquestra-novo-traco','Orquestra Novo Traço')
open('projetos/novo-traco.html','w').write(h)


# ============ ORQUESTRA ============
n[0]=0
h=head('orquestra-novo-traco','Orquestra Novo Traço','Identidade visual da Orquestra Novo Traço, submarca do grupo Novo Traço: o símbolo ONT, espaço em branco e a estética de uma partitura. Projeto de Isadora Camargo.','assets/img/novo-traco/orq-mockup.jpg',1920,1440,'Cartões de visita da Orquestra Novo Traço em amarelo e creme com o símbolo ONT','identidade visual, submarca, orquestra, música, direção de arte')
h+=casehead('Orquestra<br>Novo Traço','Uma orquestra que toca com artistas da música urbana, com identidade nascida da partitura e do traço da marca-mãe.',
 [('Cliente','Novo Traço'),('Ano','2025 — 2026'),('Papel','Direção de arte'),('Escopo','Símbolo, identidade visual, eventos e vestuário')])
h+=vid('orquestra-simbolo',1920,1080,'Animação da assinatura orquestra Novo traço que se transforma no símbolo ONT e cresce até ocupar a tela')
h+=sec('Diretrizes visuais','''<p>A identidade da orquestra deriva diretamente da marca-mãe, com adaptações pontuais para o contexto. Há uma valorização maior do espaço em branco, com predominância de preto sobre fundo claro, numa leitura visual que remete a uma partitura musical: clareza, elegância e respiro.</p>
        <p>O símbolo nasceu da observação: a equipe já chamava a orquestra de "ONT" espontaneamente, e a sigla foi adotada oficialmente. As letras se apoiam fisicamente umas nas outras, como os instrumentos de uma orquestra, em que nenhum atua isolado.</p>''')
h+=colors('Orquestra Novo Traço',[
 dict(name='My Soul',hex='020305',pantone='19-4010 TCX'),
 dict(name='Cloud Dancer',hex='F0EFEB',pantone='11-4201 TCX'),
 dict(name='Illuminating',hex='F6EA60',pantone='13-0647 TCX')],'HEX · RGB · Pantone')
h+=types('Orquestra Novo Traço',[dict(ROSLINDALE,use='Títulos e nomes, com o refinamento de um programa de concerto'),MARGEM])
h+=vid('orquestra-evento',1920,1080,'Post animado do evento: Orquestra NT convida L7NNON, 07.12, sábado, na Casa Light, com traço amarelo passando pelos três cartazes')
h+=img('novo-traco/orq-mockup.jpg',1920,1440,'Cartões de visita da Orquestra Novo Traço em amarelo e creme, com o símbolo ONT e nomes da equipe em serifa')
h+=grid([('novo-traco/orq-moletom-branco.jpg',1920,1080,'Moletom branco com o símbolo ONT bordado no peito'),('novo-traco/orq-moletom-preto.jpg',1920,1080,'Moletom preto com o símbolo ONT grande nas costas')])
h+=img('novo-traco/orq-foto.jpg',1920,1193,'Músico de moletom preto com o símbolo ONT nas costas, em um ensaio com violino')
h+=vid('orquestra-logo',1920,1080,'Animação do símbolo ONT sendo traçado à mão e formando a assinatura orquestra Novo traço')
h+=sec('No ecossistema','<p>A Orquestra é uma das submarcas do grupo <a class="link" href="novo-traco.html">Novo Traço</a>. O traço feito à mão permanece como elemento central no logotipo, no símbolo e nas aplicações, o que garante a unidade com o resto do grupo e preserva o caráter autoral da marca.</p>')
h+=foot('nt-records','NT Records')
open('projetos/orquestra-novo-traco.html','w').write(h)

# ============ NT RECORDS ============
n[0]=0
h=head('nt-records','NT Records','Identidade visual da NT Records, gravadora do grupo Novo Traço: traço em tinta spray, grid de linhas retas e uma paleta de preto, azul e branco. Projeto de Isadora Camargo.','assets/img/novo-traco/rec-cartao.jpg',1920,1080,'Cartão de visita da NT Records com textura de carimbo','identidade visual, submarca, gravadora, música, direção de arte')
h+=casehead('NT Records','A gravadora do grupo Novo Traço: o traço da marca-mãe ganha tinta spray, textura urbana e um grid que dá solidez.',
 [('Cliente','Novo Traço'),('Ano','2026'),('Papel','Direção de arte'),('Escopo','Símbolo, identidade visual, papelaria, merch e digital')])
h+=vid('nt-records-logo',1920,1080,'Animação do logo NT Records: o símbolo aparece e um traço circular de tinta spray se desenha ao redor, com a assinatura by Novo Traço')
h+=sec('Propósito e linguagem','''<p>Existir para que a música que nasceu no palco e no estúdio da Novo Traço continue acessível depois da luz apagar, na escala que o tempo longo exige.</p>
        <p>A gravadora mantém o traço do grupo, mas troca o pincel e a caneta pela tinta spray, para ganhar urbanidade e textura. Linhas retas funcionam como grid estruturante e trazem a seriedade de uma marca sólida.</p>''')
h+=img('novo-traco/rec-proposito.jpg',1920,1080,'Retrato de um violoncelista em luz baixa com o propósito da NT Records ao lado')
h+=img('novo-traco/rec-linhas.jpg',1920,1080,'Página do guia com os princípios Linhas, um grid de linhas retas, e Traços, um círculo de tinta spray')
h+=vid('nt-records-apresentacao',1920,1370,'Animação de apresentação da NT Records: um disco com a arte em spray gira sobre o grid de linhas retas')
h+=sec('Cor e tipografia','''<p>Uma paleta enxuta, de preto, azul e branco, equilibra autoridade e confiança, e deixa o traço de spray como protagonista. A Univers Next Pro sustenta toda a tipografia: a mesma família da marca-mãe, usada aqui com mais rigor e menos contraste de pesos.</p>''')
h+=colors('NT Records',[dict(name='My Soul',hex='020305'),dict(name='Azul Records',hex='003AE7'),dict(name='Cloud Dancer',hex='F0EFEB')])
h+=types('NT Records',[dict(UNIVERS,use='Toda a comunicação: títulos, créditos e texto')])
h+=img('novo-traco/rec-placa.jpg',1920,1080,'Placa emoldurada da NT Records em reconhecimento a um milhão de streams do artista Froid, sobre foto de show')
h+=img('novo-traco/rec-papelaria.jpg',1920,1080,'Papelaria da NT Records: pasta com carta timbrada, envelope e caderno com o símbolo')
h+=grid([('novo-traco/rec-garrafa.jpg',1920,1080,'Garrafa preta da NT Records com traço branco em spray'),('novo-traco/rec-cartao.jpg',1920,1080,'Cartão de visita da NT Records com textura de carimbo')])
h+=sec('Merch','<p>A linha de produtos leva o traço de spray para o vestuário e os acessórios. O disco pintado vira estampa grande nas costas da camiseta e na ecobag, enquanto o hoodie e a garrafa assinam com mais discrição, só com o símbolo e o traço.</p>')
h+=img('novo-traco/rec-camiseta.jpg',1920,1072,'Homem de costas vestindo camiseta branca com o disco pintado em spray, o símbolo NT Records, 2026, Brasil e a assinatura Novo Traço')
h+=img('novo-traco/rec-estampa.jpg',1920,1648,'Estampa da camiseta em detalhe: disco com traços de spray em preto, símbolo NT Records entre 20 e 26, Brasil e a assinatura Novo Traço')
h+=grid([('novo-traco/rec-hoodie-azul-frente.jpg',958,1072,'Modelo de frente vestindo hoodie azul lavado com o logo NT Records no peito'),('novo-traco/rec-hoodie-azul-costas.jpg',958,1072,'Modelo de costas vestindo o hoodie azul lavado da NT Records')])
h+=img('novo-traco/rec-tote-1.jpg',1920,1072,'Ecobag creme com traços de spray em preto e o logo NT Records, carregada no ombro diante de uma parede de concreto com sombras diagonais')
h+=img('novo-traco/rec-hoodie-preto.jpg',1920,1072,'Hoodie preto com manchas de spray brancas e o logo NT Records em branco no peito')
h+=grid([('novo-traco/rec-tote-2.jpg',1920,1072,'Ecobag com três discos pintados em spray e o logo NT Records, no ombro diante de uma parede de concreto'),('novo-traco/rec-garrafa-inox.jpg',1920,1072,'Garrafa de inox com traço de spray branco, a assinatura Novo Traço e o logo NT Records')])
h+='''
    <figure class="media media--bleed media--screen">
      <img src="../assets/img/novo-traco/rec-posts.jpg" width="1920" height="1080" loading="lazy" alt="Três posts da NT Records sobre uma mão ao fundo: um azul com a frase Um mundo sem música é como um corpo sem alma, um com discos pintados com spray, animado, e um com trompetista e o título De onde vem o jazz?">
      <video class="autoplay media-screen" style="--x:36.59%;--y:20.14%;--w:26.85%;--h:59.77%" width="1080" height="1350" muted loop playsinline preload="none" poster="../assets/video/nt-records-social.jpg" aria-label="Post animado da NT Records: discos com traços de spray em preto e branco se sucedem sobre o grid">
        <source src="../assets/video/nt-records-social.webm" type="video/webm">
        <source src="../assets/video/nt-records-social.mp4" type="video/mp4">
      </video>
    </figure>
'''
h+=sec('No ecossistema','<p>A NT Records é a submarca do grupo <a class="link" href="novo-traco.html">Novo Traço</a> dedicada a lançar e manter vivo o catálogo dos artistas. Ela herda o traço do grupo e o assina com "by Novo Traço", mas tem voz própria, mais urbana e mais institucional ao mesmo tempo.</p>')
h+=foot('latinjazz-brazil','LatinJazz Brazil')
open('projetos/nt-records.html','w').write(h)


# ============ LATINJAZZ ============
n[0]=0
h=head('latinjazz-brazil','LatinJazz Brazil','Identidade visual do LatinJazz Brazil, projeto da Novo Traço: logo desenhado à mão, cores da Tropicália e colagens em movimento. Projeto de Isadora Camargo.','assets/img/latinjazz/banners.jpg',1920,1221,'Banners do LatinJazz Brazil pendurados entre colunas do Theatro Municipal, com raios verdes e amarelos, um trompetista e a data do show','identidade visual, motion, jazz, música, colagem, Tropicália')
h+=casehead('LatinJazz<br>Brazil','Uma sonoridade que também pertence ao Brasil: Tropicália, colagem e um logo desenhado à mão para um projeto da Novo Traço.',
 [('Cliente','Novo Traço'),('Papel','Direção de arte'),('Escopo','Logotipo, identidade visual, motion e aplicações')])
h+=vid('latinjazz-colagem',1920,1080,'Colagem animada: o logotipo em papel preto amassado sobre raios verdes e amarelos, com traço de pincel amarelo')
h+=sec('Conceito','''<p>O conceito visual do LatinJazz Brazil nasce do reconhecimento de uma sonoridade que pertence ao Brasil. A identidade traduz essa afirmação por meio de cores vibrantes inspiradas na Tropicália, texturas, traços e composições expressivas que refletem a energia brasileira.</p>
        <p>Assim como o próprio Latin Jazz é construído por encontros e atravessamentos culturais, o universo visual explora contrastes, ritmos e diferentes camadas gráficas para criar uma estética viva, diversa e em constante movimento.</p>''')
h+=sec('Logo','''<p>Logo desenhado à mão, com traços orgânicos que refletem expressividade, movimento e dinamismo. Suas variações para animação exploram elementos abstratos inspirados no universo da música, como figuras de musicistas, rostos, notas musicais e outros símbolos.</p>''')
h+=vid('latinjazz-logo-bg',1920,1080,'Animação do logotipo LatinJazz Brazil: as letras se montam até formar LATIN JAZZ com o losango da bandeira brasileira',bleed=False,cls='media--logo')
# no celular, no lugar do vídeo, o logo em SVG
k=h.rfind('      </video>\n')+len('      </video>\n')
h=h[:k]+'      <img class="logo-still" src="../assets/img/latinjazz/logo.svg" width="302" height="498" alt="Logotipo LatinJazz Brazil: LATIN e JAZZ em letras recortadas, com o losango da bandeira e a palavra BRAZIL">\n'+h[k:]
h+=img('latinjazz/variacoes.png',1232,760,'Grade de variações do logo para animação: letras do LATIN JAZZ recombinadas com pontos e o losango da bandeira, formando pequenos rostos, figuras e símbolos',bleed=False)
h+=sec('Cores','''<p>A paleta é construída a partir de cores vibrantes que dialogam com o universo tropical, expressivo e plural do Brasil. Amarelo, verde, rosa, azul, branco e preto convivem em contraste, como camadas de uma mesma colagem.</p>
        <p>As cores vêm direto do sistema da <a class="link" href="novo-traco.html">Novo Traço</a>, marca-mãe do projeto, o que mantém a conexão entre os dois universos.</p>''')
h+=colors('LatinJazz Brazil',[
 dict(name='Illuminating',hex='F6EA60',pantone='13-0647 TCX'),
 dict(name='First Tree',hex='00733C',pantone='18-6031 TCX'),
 dict(name='Red Pink',hex='FB2A54'),
 dict(name='Tropical Breeze',hex='87CDE7',pantone='13-4307 TCX'),
 dict(name='Cloud Dancer',hex='F0EFEB',pantone='11-4201 TCX'),
 dict(name='My Soul',hex='020305',pantone='19-4010 TCX')],'HEX · RGB · Pantone')
h+=vid('latinjazz-faixa',1920,490,'Faixa animada com raios de sol que alternam entre verde e amarelo e vermelho e azul-claro')
h+=sec('Tipografia','''<p>A Univers traz versatilidade por meio da sua ampla variedade de pesos, e organiza datas, nomes e informações com clareza. Já a Margem adiciona simpatia, leveza e brasilidade aos textos.</p>''')
h+=types('LatinJazz Brazil',[dict(UNIVERS,use='Títulos, datas e nomes de artistas'),dict(MARGEM,use='Textos e apoio')])
h+=img('latinjazz/cartaz.jpg',1920,1594,'Cartaz em colagem com fundo verde e traços amarelos: uma dançarina de tranças, um homem dançando de camisa rosa e um trompetista de óculos escuros')
h+=img('latinjazz/revista.jpg',1920,957,'Revista aberta com a colagem dos dançarinos na página esquerda e, na direita, texto com traço amarelo, o selo LatinJazz e a silhueta de uma cidade em laranja')
h+=img('latinjazz/vinil.jpg',1920,1286,'Capa de disco de vinil amarela e rosa com um saxofonista na praia, o logo LatinJazz Brazil, traços pretos de pincel e etiquetas de código de barras')
h+=img('latinjazz/cartazes.jpg',1920,1905,'Dois cartazes com raios verdes e amarelos, um saxofonista e uma trompetista de costas, colados em um muro sob casarões coloniais com céu azul')
h+=img('latinjazz/banners.jpg',1920,1221,'Banners do LatinJazz Brazil pendurados entre colunas do Theatro Municipal: o logo sobre raios verdes e amarelos, o trompetista Dudu Santana e a data 30 de setembro às 19h')
h+=sec('Uma marca Novo Traço','''<p>O LatinJazz Brazil é um projeto da <a class="link" href="novo-traco.html">Novo Traço</a>. Ele compartilha com a marca-mãe as cores, a Univers, a Margem e o gesto feito à mão, mas ganha um vocabulário próprio de colagem, raios de sol e papel amassado, pensado para se mexer nas redes, nos telões e na rua.</p>''')
h+=foot('anju-mace','ANJU MACE')
open('projetos/latinjazz-brazil.html','w').write(h)

# ============ BE BRAVE ============
n[0]=0
h=head('be-brave','Be Brave Lab','Identidade visual da Be Brave Lab, agência audiovisual: um símbolo geométrico em forma de asas, laranja vibrante e tipografia extended. Projeto de Isadora Camargo.','assets/img/be-brave/caixa.jpg',1920,1080,'Caixa laranja com a assinatura Be Brave Lab e o símbolo em branco','identidade visual, branding, agência audiovisual, símbolo, direção de arte')
h+=casehead('Be Brave Lab','Uma identidade com coragem de sobra para uma agência audiovisual que disputa atenção em segundos.',
 [('Cliente','Be Brave Lab'),('Segmento','Agência audiovisual'),('Papel','Design de marca'),('Escopo','Símbolo, identidade visual, tipografia e aplicações')])
h+='''
    <div class="logo-hero">
      <img src="../assets/img/be-brave/logo.svg" width="666" height="226" fetchpriority="high" alt="Logotipo Be Brave Lab em laranja: símbolo em forma de asas sobre a palavra BE BRAVE LAB em letras extended">
    </div>
'''
h+=sec('Contexto e desafio','''<p>A Be Brave Lab é uma agência audiovisual que cria conteúdo para marcas e criadores num ambiente viral, onde a atenção é disputada em segundos. A marca precisava ser imediatamente reconhecível em thumbnails, vinhetas e redes, e comunicar coragem, presença e confiança.</p>''')
h+=sec('Símbolo','''<p>O símbolo é construído sobre um grid de círculos e linhas paralelas. Duas formas espelhadas se encontram no centro e se abrem como asas, uma imagem de impulso e de quem avança sem pedir licença. A geometria rigorosa garante que ele funcione do ícone de perfil à animação 3D.</p>''')
h+=img('be-brave/construcao.jpg',1920,1080,'Construção geométrica do símbolo Be Brave Lab com círculos, linhas paralelas e diagonais')
h+=img('be-brave/3d.jpg',1920,1080,'Símbolo Be Brave Lab em vidro 3D sobre fundo preto')
h+=sec('Tipografia','''<p>A Monument Extended é bold, geométrica e altamente impactante. Seu caráter extended transmite escala, ambição e autoridade, amplia o impacto em thumbnails, títulos e motion graphics e conversa com as formas do símbolo. A Helvetica Neue completa o sistema no texto corrido, com legibilidade e hierarquia clara.</p>''')
h+=types('Be Brave Lab',[
 dict(family='PP Monument Extended',svg='monument',use='Títulos, thumbnails e motion graphics',style='Grotesca extended',weights='Regular, Black'),
 dict(family='Helvetica Neue LT Pro',svg='helvetica',use='Texto corrido e informações',style='Neogrotesca',weights='45 Light, 55 Roman, 65 Medium, 75 Bold')])
h+=sec('Cor','''<p>O laranja é a assinatura da marca: energia e urgência. O azul profundo entra como contraponto, e o preto e o off-white sustentam o sistema com sobriedade.</p>''')
h+=colors('Be Brave Lab',[dict(name='Laranja Brave',hex='FA4C05'),dict(name='Azul Profundo',hex='0D0B9D'),dict(name='Off-white',hex='EFEFEF'),dict(name='Preto',hex='0F0F0F')])
h+=sec('Aplicações','''<p>A estética audiovisual entra na própria linguagem gráfica: fotos com movimento tratadas em halftone e dither, retículas em laranja e azul, e o símbolo ocupando superfícies inteiras.</p>''')
h+=img('be-brave/foto.jpg',1920,1080,'Cinegrafista em movimento em foto preto e branco com retículas de pixels em laranja e azul')
h+=img('be-brave/caixa.jpg',1920,1080,'Caixa laranja com a assinatura Be Brave Lab e o símbolo em branco, sobre concreto com sombra dura')
h+=img('be-brave/garrafas.jpg',1920,1080,'Três garrafas de alumínio com o símbolo e a assinatura Be Brave Lab em branco')
h+=img('be-brave/instagram.jpg',1920,1080,'Perfil da Be Brave no Instagram com o símbolo branco em fundo laranja como foto de perfil')
h+=foot('funnel-builder','Funnel Builder')
open('projetos/be-brave.html','w').write(h)

# ============ FUNNEL BUILDER ============
n[0]=0
h=head('funnel-builder','Funnel Builder','Marca e sistema visual de lançamento do Funnel Builder, formação em funis de venda que faturou R$ 30 milhões. Projeto de Isadora Camargo.','assets/img/funnel-builder/logo-3d.jpg',1080,1350,'Símbolo Funnel Builder em 3D, um F em forma de funil com reflexos azuis','identidade visual, branding, lançamento digital, sistema visual, direção de arte',fonts='&family=Inter:wght@500;700')
h+=casehead('Funnel Builder','Uma marca e um sistema visual de lançamento para formar a primeira geração de construtores de funis de venda do Brasil.',
 [('Cliente','Bilhon'),('Ano','2024 — 2025'),('Papel','Head de Design: marca e direção do lançamento'),('Escopo','Símbolo, ícone, sistema visual, páginas e criativos')])
h+=grid([('funnel-builder/logo-3d.jpg',1080,1350,'Símbolo Funnel Builder em 3D com reflexos azuis sobre um fluxograma de funil de vendas'),('funnel-builder/construcao.jpg',1080,1350,'Construção geométrica do símbolo: linhas paralelas inclinadas e círculos formando o F')])
h+=sec('Contexto e desafio','''<p>O Funnel Builder é uma formação para profissionais que constroem funis de venda no mercado digital. Fui responsável por criar a marca e dirigir o design do lançamento: um volume grande de peças, páginas e criativos produzidos em pouco tempo, que precisavam ser reconhecidos como uma coisa só.</p>''')
h+=sec('Conceito','''<p>O símbolo é um F desenhado a partir de um triângulo invertido: a forma de um funil. A construção sobre diagonais paralelas dá a sensação de movimento e fluxo, a mesma ideia de um cliente que avança etapa por etapa. Em 3D, com reflexos em azul-petróleo, o símbolo virou o protagonista da campanha.</p>''')
h+=sec('Sistema de lançamento','''<p>Um sistema escuro, com luz azul e acentos em amarelo, organiza tudo: página de vendas, bônus, criativos para redes e o ícone do aplicativo. Os cards de funis e bônus seguem o mesmo grid e o mesmo tratamento, o que permitiu ao time produzir em escala sem perder consistência.</p>''')
h+=colors('Funnel Builder',[dict(name='Preto Profundo',hex='030A09'),dict(name='Grafite',hex='0E0F0F'),dict(name='Azul Noturno',hex='002D51'),dict(name='Azul Luz',hex='5BBED9'),dict(name='Amarelo Bônus',hex='FFDE37'),dict(name='Branco Gelo',hex='F0F2F8')])
h+=types('Funnel Builder',[
 dict(family='Inter',live="'Inter', sans-serif",w=700,sample='Funnel Builder',use='Marca, títulos e interface',style='Sem serifa',weights='Regular, Medium, SemiBold, Bold'),
 dict(family='Aspekta',svg='aspekta',use='Títulos de página e chamadas',style='Sem serifa geométrica',weights='400, 500, 600')])
h+=grid([('funnel-builder/mobile.jpg',1080,1350,'Página de vendas do Funnel Builder no celular, com o símbolo no topo'),('funnel-builder/icone.jpg',1080,1350,'Ícone de aplicativo do Funnel Builder com gradiente azul-petróleo')])
h+=grid([('funnel-builder/funis.jpg',1083,1350,'Cards de modelos de funil com prévias de páginas e brilho azul'),('funnel-builder/bonus.jpg',1083,1350,'Cards de bônus da formação com brilho amarelo')])
h+=sec('Resultado','''<div class="results">
          <div><span class="result-num">R$ 30 mi</span><span class="caps">faturamento do lançamento</span></div>
        </div>
        <div class="prose"><p>A marca e o sistema visual sustentaram um lançamento que faturou R$ 30 milhões, com um time interno de três pessoas e designers freelancers sob a minha liderança.</p></div>''',cls='section-body')
h+=foot('novo-traco','Novo Traço')
open('projetos/funnel-builder.html','w').write(h)

# versão em inglês + seletor de idioma
import runpy
runpy.run_path(os.path.join(HERE, 'i18n.py'))
