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
    # bingo:  "celulas": [8 frases], "centro": "Já reiniciou?"
    # lista:  "itens": [3 a 6 frases]            (ranking / "coisas que...")
    # versus: "esquerda": {"rotulo": "...", "itens": [...]}, "direita": {...}
    "cta": "Quantas você marcou? Comenta aí.", "cta2": "Marca quem fecha a cartela"
  }
}
"""
import json, sys, pathlib, subprocess, html
ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTDIR = pathlib.Path('/tmp/dicas-ti-fonts')
BG, CARD, LINE, TXT, SUB, MUTED = '#0E1411', '#17201B', '#26312A', '#F1F4EE', '#C9D1C8', '#9AA59C'
AMB, GRN = '#F2B544', '#8EE35C'

def fonts():
    pk = {'space-grotesk': 'fontsource-space-grotesk', 'ibm-plex-sans': 'fontsource-ibm-plex-sans'}
    FONTDIR.mkdir(exist_ok=True)
    for stem, pkg in pk.items():
        if not list(FONTDIR.glob(f'{pkg}*/files')):
            subprocess.run(['npm', 'pack', f'@fontsource/{stem}', '--silent'], cwd=FONTDIR, check=True)
            tgz = sorted(FONTDIR.glob(f'{pkg}-*.tgz'))[-1]
            subprocess.run(['tar', 'xzf', tgz.name], cwd=FONTDIR, check=True)
            (FONTDIR / 'package').rename(FONTDIR / tgz.name[:-4])
    css = ''
    for fam, stem, pkg, ws in [('Space Grotesk', 'space-grotesk', 'fontsource-space-grotesk', (500, 700)),
                               ('IBM Plex Sans', 'ibm-plex-sans', 'fontsource-ibm-plex-sans', (400, 500, 600, 700))]:
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
<p style="margin:0;font-size:36px;line-height:1.4;color:{SUB}">O que rolou em tecnologia pra você começar a {spec["dia_semana"].lower()} bem informado.</p>
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
        cell = lambda c: (f'<div style="height:262px;background:{GRN};color:{BG};border-radius:22px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;text-align:center;padding:20px;box-sizing:border-box"><div style="font-size:22px;font-weight:600;letter-spacing:3px">GRÁTIS</div><div style="{G};font-size:44px;line-height:1.05">{L["centro"]}</div></div>' if c == '__C__' else
                          f'<div style="height:262px;background:{CARD};border:2px solid {LINE};border-radius:22px;display:flex;align-items:center;justify-content:center;text-align:center;padding:24px;box-sizing:border-box;font-size:31px;font-weight:500;line-height:1.3">“{c}”</div>')
        body = f'<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px">{"".join(cell(c) for c in cs)}</div>'
    elif lay == 'lista':
        body = '<div style="display:flex;flex-direction:column;gap:18px">' + ''.join(f'<div style="padding:30px 36px;background:{CARD};border-radius:22px;display:flex;gap:30px;align-items:center"><div style="{G};font-size:48px;color:{GRN};width:70px;flex-shrink:0">{i}</div><div style="font-size:34px;line-height:1.35;font-weight:500">{t}</div></div>' for i, t in enumerate(L['itens'], 1)) + '</div>'
    elif lay == 'versus':
        col = lambda s, hi: f'<div style="padding:36px;background:{CARD if not hi else BG};border:2px solid {GRN if hi else LINE};border-radius:24px;display:flex;flex-direction:column;gap:24px"><div style="{G};font-size:44px;color:{GRN if hi else TXT}">{s["rotulo"]}</div>' + ''.join(f'<div style="font-size:34px;line-height:1.35;color:{SUB}">{t}</div>' for t in s['itens']) + '</div>'
        body = f'<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px">{col(L["esquerda"], False)}{col(L["direita"], True)}</div>'
    else:
        raise SystemExit(f'layout desconhecido: {lay}')
    bottom = f'<div style="display:flex;justify-content:space-between;align-items:center;gap:24px;font-size:32px"><div style="font-weight:600">{L.get("cta","")}</div><div style="color:{MUTED};font-size:28px">{L.get("cta2","")}</div></div>'
    return [frame(top + title + body + bottom)]

def main():
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = ROOT / spec['data']; out.mkdir(exist_ok=True)
    tag_ = spec['data'][8:10] + spec['data'][5:7]
    css = fonts()
    jobs = [(f'dicas-ti-{tag_}-jornal-{i:02d}.png', p) for i, p in enumerate(jornal(spec), 1)] + [(f'dicas-ti-{tag_}-leve.png', leve(spec)[0])]
    from playwright.sync_api import sync_playwright
    tmp = pathlib.Path('/tmp/dicas-ti-render.html')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for name, body in jobs:
            tmp.write_text(f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><style>{css}body{{margin:0;background:{BG};font-family:'IBM Plex Sans',sans-serif}}</style></head><body>{body}</body></html>")
            pg.goto(f'file://{tmp}'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
            over = pg.evaluate('(()=>{const r=document.body.firstElementChild;return [...r.querySelectorAll("*")].some(e=>e.getBoundingClientRect().bottom>1350.5||e.getBoundingClientRect().right>1080.5)})()')
            pg.screenshot(path=str(out / name), clip={'x': 0, 'y': 0, 'width': 1080, 'height': 1350})
            print(('ESTOURO ' if over else 'ok      ') + str(out / name))
        b.close()

if __name__ == '__main__':
    main()
