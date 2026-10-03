#!/usr/bin/env python3
"""Gera os PNGs (1080x1350) dos posts do @dicas.ti a partir de um JSON.

Uso:  python3 tools/build.py posts/AAAA-MM-DD.json
Saída: AAAA-MM-DD/*.png  (na raiz do repositório)

Formato do JSON:
{
  "data": "2026-10-01",            # data de publicação
  "dia_semana": "Quinta",          # nome do dia (pt-BR)
  "jornal": {                      # post das 9h: "Bom dia, T.I."
    "noticias": [                  # 3 a 4 notícias
      {"tag": "IA · Regulação", "manchete_curta": "...", "titulo": "...",
       "lead": "...", "bullets": ["...", "..."],
       "box_titulo": "Por que importa", "box": "..."}
    ],
    "agenda": [{"quando": "HOJE", "texto": "... pode ter <b>negrito</b>"}]  # 1 a 3 itens
  },
  "leve": {                        # post das 15h
    "layout": "bingo" | "lista" | "versus",
    "titulo": "Bingo do", "titulo_destaque": "suporte", "subtitulo": "...",
    "canto": "Edição suporte técnico",
    # bingo:  "celulas": [8 frases], "centro": "Já reiniciou?", "centro_selo": "Essa todo mundo já ouviu" (opcional)
    # lista:  "itens": [3 a 6 frases]            (ranking / "coisas que...")
    # versus: "esquerda": {"rotulo": "...", "itens": [...]}, "direita": {...}
    "cta": "Quantas você marcou? Comenta aí.", "cta2": "Marca quem fecha a cartela"
  },
  # OU, no lugar de "leve", um carrossel educativo "dica" (seg/qua/sex):
  "dica": {
    "tag": "Linux",                     # área: Linux, Redes, Segurança, Windows, Cloud, MikroTik...
    "titulo": "7 comandos pra", "titulo_destaque": "investigar um servidor Linux",
    "subtitulo": "O kit básico de quem trabalha com segurança.",
    "itens": [                          # 4 a 8 itens, 2 por slide; "codigo" é opcional
      {"titulo": "Portas abertas", "codigo": "ss -tulpn", "texto": "Lista quem está escutando em cada porta."}
    ],
    "resumo": "Frase curta com o recado final."
  },
  "legendas": {"jornal": "...", "leve": "..."}   # ou "dica": "..."
}

Também gera 2 stories 1080x1920 (…-story-jornal.png e …-story-tarde.png) com a capa
do post e o selo "Post novo", para agendar como Story ~10 min depois de cada post.
"""
import json, sys, pathlib, subprocess, html
ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTDIR = pathlib.Path('/tmp/dicas-ti-fonts')
BG, CARD, LINE, TXT, SUB, MUTED = '#0E1411', '#17201B', '#26312A', '#F1F4EE', '#C9D1C8', '#9AA59C'
AMB, GRN, CYA = '#F2B544', '#8EE35C', '#5CC8E3'

def fonts():
    pk = {'space-grotesk': 'fontsource-space-grotesk', 'ibm-plex-sans': 'fontsource-ibm-plex-sans', 'ibm-plex-mono': 'fontsource-ibm-plex-mono'}
    FONTDIR.mkdir(exist_ok=True)
    for stem, pkg in pk.items():
        if not list(FONTDIR.glob(f'{pkg}*/files')):
            subprocess.run(['npm', 'pack', f'@fontsource/{stem}', '--silent'], cwd=FONTDIR, check=True)
            tgz = sorted(FONTDIR.glob(f'{pkg}-*.tgz'))[-1]
            subprocess.run(['tar', 'xzf', tgz.name], cwd=FONTDIR, check=True)
            (FONTDIR / 'package').rename(FONTDIR / tgz.name[:-4])
    css = ''
    for fam, stem, pkg, ws in [('Space Grotesk', 'space-grotesk', 'fontsource-space-grotesk', (500, 700)),
                               ('IBM Plex Sans', 'ibm-plex-sans', 'fontsource-ibm-plex-sans', (400, 500, 600, 700)),
                               ('IBM Plex Mono', 'ibm-plex-mono', 'fontsource-ibm-plex-mono', (400, 500))]:
        d = sorted(FONTDIR.glob(f'{pkg}-*/files'))[-1]
        for w in ws:
            css += f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('file://{d}/{stem}-latin-{w}-normal.woff2') format('woff2');}}\n"
    return css

G = "font-family:'Space Grotesk',sans-serif;font-weight:700"
SUN = lambda s, sw=2: f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
ARROW = '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M13 6l6 6-6 6"/></svg>'
def frame(inner):
    return f'<div style="width:1080px;height:1350px;box-sizing:border-box;padding:88px;background:{BG};display:flex;flex-direction:column;justify-content:space-between;color:{TXT}">{inner}</div>'
def tag(t, c=MUTED): return f'<div style="font-size:26px;font-weight:600;letter-spacing:4px;text-transform:uppercase;color:{c}">{t}</div>'
def dmy(d): y, m, dd = d.split('-'); return f'{dd}/{m}/{y}'

def jornal(spec):
    J, n = spec['jornal'], len(spec['jornal']['noticias'])
    tot = n + 2
    date = f"{spec['dia_semana']} · {dmy(spec['data'])}"
    head = f'<div style="display:flex;justify-content:space-between;align-items:center"><div style="display:flex;align-items:center;gap:14px;color:{AMB}">{SUN(44)}<span style="{G};font-size:30px;letter-spacing:3px;text-transform:uppercase">Bom dia, T.I.</span></div><div style="font-size:26px;color:{MUTED}">{spec["dia_semana"][:3]} · {dmy(spec["data"])}</div></div>'
    foot = lambda i: f'<div style="display:flex;justify-content:space-between;font-size:28px;color:{MUTED}"><div style="{G};color:{TXT}">@dicas.ti</div><div>{i}/{tot}</div></div>'
    pages = []
    items = ''.join(f'<div style="display:flex;gap:28px;align-items:baseline;padding:22px 0;border-top:2px solid {LINE}"><div style="width:64px;flex-shrink:0;{G};font-size:34px;color:{AMB}">0{i}</div><div style="display:flex;flex-direction:column;gap:6px"><div style="font-size:22px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:{MUTED}">{x["tag"].split(" · ")[0]}</div><div style="font-size:36px;font-weight:500;line-height:1.3">{x["manchete_curta"]}</div></div></div>' for i, x in enumerate(J['noticias'], 1))
    pages.append(frame(f'''<div style="display:flex;justify-content:space-between;align-items:center"><div style="{G};font-size:34px">@dicas.ti</div><div style="padding:12px 24px;border:2px solid {AMB};border-radius:999px;font-size:26px;font-weight:600;color:{AMB}">{date}</div></div>
<div style="display:flex;flex-direction:column;gap:28px"><div style="color:{AMB}">{SUN(92, 1.6)}</div>
<h1 style="margin:0;{G};font-size:150px;line-height:.95;letter-spacing:-5px">Bom dia, <span style="color:{AMB}">T.I.</span></h1>
<p style="margin:0;font-size:36px;line-height:1.4;color:{SUB}">O que rolou em tecnologia pra você começar {"o" if spec["dia_semana"].lower() in ("sábado","domingo") else "a"} {spec["dia_semana"].lower()} bem informado.</p>
<div style="display:flex;flex-direction:column;margin-top:12px">{items}</div></div>
<div style="display:flex;justify-content:space-between;align-items:center;font-size:28px;color:{MUTED}"><div>1/{tot}</div><div style="display:flex;align-items:center;gap:14px;color:{TXT};font-weight:600">Arrasta para o lado {ARROW}</div></div>'''))
    for i, x in enumerate(J['noticias'], 2):
        bl = ''.join(f'<div style="display:flex;gap:18px"><span style="color:{AMB};font-weight:700">→</span><span>{b}</span></div>' for b in x['bullets'])
        pages.append(frame(f'''{head}<div style="display:flex;flex-direction:column;gap:36px">{tag(x["tag"])}
<h2 style="margin:0;{G};font-size:70px;line-height:1.06;letter-spacing:-1.5px">{x["titulo"]}</h2>
<p style="margin:0;font-size:33px;line-height:1.45;color:{SUB}">{x["lead"]}</p>
<div style="display:flex;flex-direction:column;gap:18px;font-size:32px;line-height:1.4">{bl}</div>
<div style="padding:30px 36px;border:2px solid {AMB};border-radius:22px;display:flex;flex-direction:column;gap:8px"><div style="font-size:24px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:{AMB}">{x.get("box_titulo","Por que importa")}</div><div style="font-size:31px;line-height:1.4">{x["box"]}</div></div></div>{foot(i)}'''))
    ag = ''.join(f'<div style="padding:36px 40px;background:{CARD};border-radius:24px;display:flex;gap:36px;align-items:center"><div style="{G};font-size:56px;color:{AMB};white-space:nowrap">{a["quando"]}</div><div style="font-size:33px;line-height:1.4">{a["texto"]}</div></div>' for a in J['agenda'])
    pages.append(frame(f'''{head}<div style="display:flex;flex-direction:column;gap:40px">{tag("Fica de olho")}
<h2 style="margin:0;{G};font-size:84px;line-height:1.05;letter-spacing:-2px">Agenda da semana</h2><div style="display:flex;flex-direction:column;gap:22px">{ag}</div></div>
<div style="padding:36px 40px;border:2px solid {AMB};border-radius:24px;display:flex;justify-content:space-between;align-items:center;gap:24px"><div style="font-size:32px;line-height:1.35">Qual dessas notícias te pegou mais? Conta nos comentários.</div><div style="{G};font-size:34px;color:{AMB};white-space:nowrap">{tot}/{tot}</div></div>'''))
    return pages

def leve(spec):
    L = spec['leve']; lay = L['layout']
    top = f'<div style="display:flex;justify-content:space-between;align-items:center"><div style="{G};font-size:34px">@dicas.ti</div><div style="font-size:26px;color:{MUTED}">{L.get("canto","")}</div></div>'
    title = f'<div style="display:flex;flex-direction:column;gap:14px"><h1 style="margin:0;{G};font-size:100px;line-height:.98;letter-spacing:-3px">{L["titulo"]} <span style="color:{GRN}">{L["titulo_destaque"]}</span></h1><p style="margin:0;font-size:34px;color:{SUB}">{L.get("subtitulo","")}</p></div>'
    if lay == 'bingo':
        cs = L['celulas'][:4] + ['__C__'] + L['celulas'][4:8]
        cell = lambda c: (f'<div style="height:262px;background:{GRN};color:{BG};border-radius:22px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;text-align:center;padding:20px;box-sizing:border-box"><div style="font-size:21px;font-weight:600;letter-spacing:2px;line-height:1.3;text-transform:uppercase">{L.get("centro_selo","GRÁTIS")}</div><div style="{G};font-size:44px;line-height:1.05">{L["centro"]}</div></div>' if c == '__C__' else
                          f'<div style="height:262px;background:{CARD};border:2px solid {LINE};border-radius:22px;display:flex;align-items:center;justify-content:center;text-align:center;padding:24px;box-sizing:border-box;font-size:31px;font-weight:500;line-height:1.3">“{c}”</div>')
        body = f'<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px">{"".join(cell(c) for c in cs)}</div>'
    elif lay == 'lista':
        body = '<div style="display:flex;flex-direction:column;gap:18px">' + ''.join(f'<div style="padding:30px 36px;background:{CARD};border-radius:22px;display:flex;gap:30px;align-items:center"><div style="{G};font-size:48px;color:{GRN};width:70px;flex-shrink:0">{i}</div><div style="font-size:34px;line-height:1.35;font-weight:500">{t}</div></div>' for i, t in enumerate(L['itens'], 1)) + '</div>'
    elif lay == 'versus':
        col = lambda s, hi: f'<div style="padding:36px;background:{CARD if not hi else BG};border:2px solid {GRN if hi else LINE};border-radius:24px;display:flex;flex-direction:column;gap:24px"><div style="{G};font-size:44px;color:{GRN if hi else TXT}">{s["rotulo"]}</div>' + ''.join(f'<div style="font-size:34px;line-height:1.35;color:{SUB}">{t}</div>' for t in s['itens']) + '</div>'
        body = f'<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px">{col(L["esquerda"], False)}{col(L["direita"], True)}</div>'
    else:
        raise SystemExit(f'layout desconhecido: {lay}')
    bottom = f'<div style="display:flex;flex-direction:column;gap:8px;font-size:32px"><div style="font-weight:600">{L.get("cta","")}</div><div style="color:{SUB};font-size:29px">{L.get("cta2","")}</div></div>'
    return [frame(top + title + body + bottom)]

BOOK = lambda s: f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>'

def dica(spec):
    D = spec['dica']; its = D['itens']; pares = [its[i:i+2] for i in range(0, len(its), 2)]
    tot = len(pares) + 2
    head = f'<div style="display:flex;justify-content:space-between;align-items:center"><div style="{G};font-size:30px;letter-spacing:3px;text-transform:uppercase;color:{CYA}">Dica prática · {D["tag"]}</div><div style="{G};font-size:30px">@dicas.ti</div></div>'
    foot = lambda i: f'<div style="display:flex;justify-content:space-between;align-items:center;font-size:28px;color:{MUTED}"><div style="display:flex;align-items:center;gap:12px;color:{TXT};font-weight:600"><span style="color:{CYA}">{BOOK(34)}</span>Salva pra consultar depois</div><div>{i}/{tot}</div></div>'
    first = its[0].get('codigo') or its[0]['titulo']
    cover = (
        f'<div style="display:flex;justify-content:space-between;align-items:center"><div style="{G};font-size:34px">@dicas.ti</div>'
        f'<div style="padding:12px 24px;border:2px solid {CYA};border-radius:999px;font-size:26px;font-weight:600;color:{CYA}">Dica prática · {D["tag"]}</div></div>'
        f'<div style="display:flex;flex-direction:column;gap:36px"><h1 style="margin:0;{G};font-size:112px;line-height:1;letter-spacing:-3px">{D["titulo"]} <span style="color:{CYA}">{D["titulo_destaque"]}</span></h1>'
        f'<p style="margin:0;font-size:38px;line-height:1.4;color:{SUB}">{D.get("subtitulo","")}</p>'
        f'<div style="padding:22px 28px;background:{CARD};border-radius:18px;font-family:\'IBM Plex Mono\',monospace;font-size:30px;color:{CYA}">$ {html.escape(first)}<span style="color:{TXT}">▌</span></div></div>'
        f'<div style="display:flex;justify-content:space-between;align-items:center;font-size:28px;color:{MUTED}"><div>1/{tot}</div>'
        f'<div style="display:flex;align-items:center;gap:14px;color:{TXT};font-weight:600">Arrasta para o lado {ARROW}</div></div>'
    )
    pages = [frame(cover)]
    n = 0
    for i, par in enumerate(pares, 2):
        blocks = ''
        for it in par:
            n += 1
            code = (f'<div style="padding:24px 28px;background:#0A0F0C;border:2px solid {LINE};border-radius:16px;font-family:\'IBM Plex Mono\',monospace;font-size:30px;line-height:1.45;color:{CYA};white-space:pre-wrap;word-break:break-word">$ {html.escape(it["codigo"])}</div>'
                    if it.get('codigo') else '')
            blocks += (f'<div style="display:flex;flex-direction:column;gap:20px;padding:40px;background:{CARD};border-radius:26px">'
                       f'<div style="display:flex;gap:22px;align-items:baseline"><div style="{G};font-size:44px;color:{CYA}">{n:02d}</div><div style="{G};font-size:46px;line-height:1.1">{it["titulo"]}</div></div>'
                       f'{code}<div style="font-size:31px;line-height:1.45;color:{SUB}">{it["texto"]}</div></div>')
        pages.append(frame(f'{head}<div style="display:flex;flex-direction:column;gap:28px">{blocks}</div>{foot(i)}'))
    lst = ''.join(f'<div style="display:flex;gap:20px;font-size:32px;line-height:1.35"><span style="color:{CYA};font-weight:700">✓</span><span>{it["titulo"]}</span></div>' for it in its)
    last = (
        f'{head}<div style="display:flex;flex-direction:column;gap:36px">{tag("Resumo")}'
        f'<h2 style="margin:0;{G};font-size:76px;line-height:1.05;letter-spacing:-2px">{D.get("resumo","Pra não esquecer")}</h2>'
        f'<div style="display:flex;flex-direction:column;gap:18px">{lst}</div></div>'
        f'<div style="padding:36px 40px;border:2px solid {CYA};border-radius:24px;display:flex;justify-content:space-between;align-items:center;gap:24px">'
        f'<div style="font-size:32px;line-height:1.35">Salva o post e manda pra quem tá começando na área.</div>'
        f'<div style="{G};font-size:34px;color:{CYA};white-space:nowrap">{tot}/{tot}</div></div>'
    )
    pages.append(frame(last))
    return pages

def story(capa_png, rotulo, cor):
    return (f'<div style="width:1080px;height:1920px;box-sizing:border-box;padding:120px 90px;background:{BG};display:flex;flex-direction:column;justify-content:space-between;align-items:center;color:{TXT}">'
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:22px"><div style="padding:14px 30px;background:{cor};color:{BG};border-radius:999px;{G};font-size:34px;letter-spacing:3px;text-transform:uppercase">Post novo</div>'
            f'<div style="{G};font-size:64px;text-align:center;line-height:1.1">{rotulo}</div></div>'
            f'<img src="file://{capa_png}" style="width:810px;height:1013px;border-radius:28px;border:3px solid {cor}">'
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:10px"><div style="font-size:38px;font-weight:600">Toca no perfil e vê completo</div>'
            f'<div style="{G};font-size:40px;color:{cor}">@dicas.ti</div></div></div>')

def main():
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = ROOT / spec['data']; out.mkdir(exist_ok=True)
    tag_ = spec['data'][8:10] + spec['data'][5:7]
    css = fonts()
    jobs = [(f'dicas-ti-{tag_}-jornal-{i:02d}.png', p, 1350) for i, p in enumerate(jornal(spec), 1)]
    if 'dica' in spec:
        jobs += [(f'dicas-ti-{tag_}-dica-{i:02d}.png', p, 1350) for i, p in enumerate(dica(spec), 1)]
        tarde, rot_t, cor_t = f'dicas-ti-{tag_}-dica-01.png', 'Dica prática: salva essa', CYA
    else:
        jobs += [(f'dicas-ti-{tag_}-leve.png', leve(spec)[0], 1350)]
        tarde, rot_t, cor_t = f'dicas-ti-{tag_}-leve.png', 'Hora do café com T.I.', GRN
    jobs += [(f'dicas-ti-{tag_}-story-jornal.png', story(out / f'dicas-ti-{tag_}-jornal-01.png', 'Bom dia, T.I.: as notícias de hoje', AMB), 1920),
             (f'dicas-ti-{tag_}-story-tarde.png', story(out / tarde, rot_t, cor_t), 1920)]
    from playwright.sync_api import sync_playwright
    tmp = pathlib.Path('/tmp/dicas-ti-render.html')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        for name, body, H in jobs:
            tmp.write_text(f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><style>{css}body{{margin:0;background:{BG};font-family:'IBM Plex Sans',sans-serif}}</style></head><body>{body}</body></html>")
            pg.goto(f'file://{tmp}'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
            over = pg.evaluate('(H)=>{const r=document.body.firstElementChild;return [...r.querySelectorAll("*")].some(e=>e.getBoundingClientRect().bottom>H+0.5||e.getBoundingClientRect().right>1080.5)}', H)
            pg.screenshot(path=str(out / name), clip={'x': 0, 'y': 0, 'width': 1080, 'height': H})
            print(('ESTOURO ' if over else 'ok      ') + str(out / name))
        b.close()

if __name__ == '__main__':
    main()
