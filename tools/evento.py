#!/usr/bin/env python3
"""Gera o carrossel de cobertura de evento do @dicas.ti (1080x1350) + story 1080x1920.

Uso:  python3 tools/evento.py posts/AAAA-MM-DD-evento.json
Reaproveita a identidade (cores, fontes, moldura) de tools/build.py.

Formato do JSON:
{
  "data": "2026-10-18", "slug": "segsummit",
  "evento": "SegSummit 2026", "quando": "21/10 · Quarta", "onde": "Distrito Anhembi · SP",
  "capa": {"selo": "Cobertura oficial", "titulo": "Estamos de volta à", "titulo_destaque": "SegSummit",
           "subtitulo": "..."},
  "slides": [
    {"tag": "...", "titulo": "...", "lead": "...",            # opcional
     "numeros": [{"valor": "+200", "rotulo": "expositores"}],  # OU
     "itens": ["...", "..."],                                    # OU
     "box": "..."}                                               # opcional
  ],
  "cta": {"titulo": "...", "texto": "...", "botao": "..."},
  "legenda": "..."
}
"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build as B

COR = '#FF7A59'  # cor de "cobertura de evento"
G = B.G

def paginas(s):
    tot = len(s['slides']) + 2
    head = (f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<div style="{G};font-size:30px;letter-spacing:3px;text-transform:uppercase;color:{COR}">{s["evento"]}</div>'
            f'<div style="{G};font-size:30px">@dicas.ti</div></div>')
    foot = lambda i: (f'<div style="display:flex;justify-content:space-between;align-items:center;font-size:28px;color:{B.MUTED}">'
                      f'<div>{s["quando"]} · {s["onde"]}</div><div>{i}/{tot}</div></div>')
    C = s['capa']
    pin = lambda t, ic: (f'<div style="display:flex;align-items:center;gap:14px;padding:16px 26px;background:{B.CARD};border-radius:999px;font-size:30px;font-weight:600">'
                         f'<span style="color:{COR}">{ic}</span>{t}</div>')
    CAL = '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18"/></svg>'
    MAP = '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>'
    REC = f'<span style="display:inline-block;width:18px;height:18px;border-radius:50%;background:{COR}"></span>'
    pages = [B.frame(
        f'<div style="display:flex;justify-content:space-between;align-items:center"><div style="{G};font-size:34px">@dicas.ti</div>'
        f'<div style="display:flex;align-items:center;gap:12px;padding:12px 24px;border:2px solid {COR};border-radius:999px;font-size:26px;font-weight:600;color:{COR};letter-spacing:2px;text-transform:uppercase">{REC}{C["selo"]}</div></div>'
        f'<div style="display:flex;flex-direction:column;gap:40px">'
        f'<div style="{G};font-size:34px;letter-spacing:4px;text-transform:uppercase;color:{B.MUTED}">{C.get("sobretitulo","")}</div>'
        f'<h1 style="margin:0;{G};font-size:132px;line-height:.98;letter-spacing:-4px">{C["titulo"]} <span style="color:{COR}">{C["titulo_destaque"]}</span></h1>'
        f'<p style="margin:0;font-size:38px;line-height:1.4;color:{B.SUB}">{C["subtitulo"]}</p>'
        f'<div style="display:flex;flex-wrap:wrap;gap:18px">{pin(s["quando"], CAL)}{pin(s["onde"], MAP)}</div></div>'
        f'<div style="display:flex;justify-content:space-between;align-items:center;font-size:28px;color:{B.MUTED}"><div>1/{tot}</div>'
        f'<div style="display:flex;align-items:center;gap:14px;color:{B.TXT};font-weight:600">Arrasta para o lado {B.ARROW}</div></div>')]
    for i, sl in enumerate(s['slides'], 2):
        corpo = ''
        if sl.get('numeros'):
            corpo += '<div style="display:flex;flex-direction:column;gap:20px">' + ''.join(
                f'<div style="padding:34px 40px;background:{B.CARD};border-radius:24px;display:flex;flex-direction:column;gap:12px">'
                f'<div style="{G};font-size:96px;line-height:1;color:{COR};white-space:nowrap">{n["valor"]}</div>'
                f'<div style="font-size:34px;line-height:1.35">{n["rotulo"]}</div></div>' for n in sl['numeros']) + '</div>'
        if sl.get('itens'):
            corpo += '<div style="display:flex;flex-direction:column;gap:22px;font-size:34px;line-height:1.4">' + ''.join(
                f'<div style="display:flex;gap:20px"><span style="color:{COR};font-weight:700">→</span><span>{t}</span></div>' for t in sl['itens']) + '</div>'
        if sl.get('chips'):
            corpo += '<div style="display:flex;flex-wrap:wrap;gap:16px">' + ''.join(
                f'<div style="padding:22px 34px;background:{B.CARD};border:2px solid {B.LINE};border-radius:999px;font-size:36px;font-weight:500">{c}</div>' for c in sl['chips']) + '</div>'
        if sl.get('box'):
            corpo += (f'<div style="padding:30px 36px;border:2px solid {COR};border-radius:22px;display:flex;flex-direction:column;gap:8px">'
                      f'<div style="font-size:24px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:{COR}">{sl.get("box_titulo","Novidade")}</div>'
                      f'<div style="font-size:31px;line-height:1.4">{sl["box"]}</div></div>')
        lead = f'<p style="margin:0;font-size:34px;line-height:1.45;color:{B.SUB}">{sl["lead"]}</p>' if sl.get('lead') else ''
        pages.append(B.frame(f'{head}<div style="display:flex;flex-direction:column;gap:38px">{B.tag(sl["tag"])}'
                             f'<h2 style="margin:0;{G};font-size:76px;line-height:1.05;letter-spacing:-2px">{sl["titulo"]}</h2>{lead}{corpo}</div>{foot(i)}'))
    K = s['cta']
    pages.append(B.frame(
        f'{head}<div style="display:flex;flex-direction:column;gap:40px">{B.tag("Bora junto?")}'
        f'<h2 style="margin:0;{G};font-size:96px;line-height:1.02;letter-spacing:-3px">{K["titulo"]}</h2>'
        f'<p style="margin:0;font-size:36px;line-height:1.45;color:{B.SUB}">{K["texto"]}</p></div>'
        f'<div style="padding:36px 40px;background:{COR};color:{B.BG};border-radius:24px;display:flex;justify-content:space-between;align-items:center;gap:24px">'
        f'<div style="{G};font-size:36px;line-height:1.3">{K["botao"]}</div><div style="{G};font-size:34px;white-space:nowrap">{tot}/{tot}</div></div>'))
    return pages

def main():
    s = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = B.ROOT / s['data']; out.mkdir(exist_ok=True)
    t = s['data'][8:10] + s['data'][5:7]
    pre = f'dicas-ti-{t}-{s["slug"]}'
    jobs = [(f'{pre}-{i:02d}.png', p, 1350) for i, p in enumerate(paginas(s), 1)]
    jobs.append((f'{pre}-story.png', B.story(out / f'{pre}-01.png', s.get('story_rotulo', 'Cobertura confirmada'), COR), 1920))
    css = B.fonts()
    from playwright.sync_api import sync_playwright
    tmp = pathlib.Path('/tmp/dicas-ti-render.html')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        for name, body, H in jobs:
            tmp.write_text(f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><style>{css}body{{margin:0;background:{B.BG};font-family:'IBM Plex Sans',sans-serif}}</style></head><body>{body}</body></html>")
            pg.goto(f'file://{tmp}'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
            over = pg.evaluate('(H)=>{const r=document.body.firstElementChild;return [...r.querySelectorAll("*")].some(e=>e.getBoundingClientRect().bottom>H+0.5||e.getBoundingClientRect().right>1080.5)}', H)
            pg.screenshot(path=str(out / name), clip={'x': 0, 'y': 0, 'width': 1080, 'height': H})
            print(('ESTOURO ' if over else 'ok      ') + str(out / name))
        b.close()

if __name__ == '__main__':
    main()
