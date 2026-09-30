#!/usr/bin/env python3
"""Atualiza a seção de anúncios da página criptografada casa-jambo.html.

Uso:
  python3 tools/update_ads.py --password SENHA --searched AAAA-MM-DD [--add novos.json] FILE [FILE ...]

novos.json: lista de objetos {portal, price (int, reais), url, code, date_portal (AAAA-MM-DD ou ""), confirmed (bool)}.
Anúncios cuja url já existe são ignorados. Os novos recebem added=--searched e new=true.
Todos os FILEs precisam ter sido criptografados com a mesma senha e o mesmo salt.
"""
import argparse, base64, json, os, re, sys
from collections import Counter
from datetime import date, timedelta
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

EUR = 5.91
PRE = re.compile(r'var P=\{salt:"([^"]+)",iv:"([^"]+)",ct:"([^"]+)",iter:(\d+)\}')
DATA = re.compile(r'<script type="application/json" id="ads-data">(.*?)</script>', re.S)

def brl(v, tag='pt'): return 'R$ ' + (f'{v:,}' if tag == 'en' else f'{v:,}'.replace(',', '.'))
def eur(v, tag='pt'):
    x = f'{round(v / EUR, -3):,.0f}'
    return '≈ €' + x if tag == 'en' else '≈ ' + x.replace(',', '.') + ' €'
MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def fd(s, tag):
    if not s: return '—'
    y, m, d = s.split('-')
    if tag == 'en': return f'{int(d)} {MON[int(m)-1]} {y}'
    return f'{d}/{m}/{y}' if tag == 'pt' else f'{d}.{m}.{y}'

T = {
 'pt': dict(h='Anúncios', th=('Portal', 'Preço', 'Atualizado no portal', 'Código', ''), open='Abrir ↗',
   n='{n} anúncios', search='Última busca na internet: <strong>{d}</strong> · verificado diariamente',
   hi='mais alto', lo='mais baixo', cur='atual', new='recém-adicionado · {d}',
   k1='Preço atual', k2='Faixa anunciada', k3='Área anunciada', diff='diferença de {v}', k3v='terreno / construída',
   notes='<ul><li><strong>Negociação:</strong> o menor preço já anunciado foi <strong>{lo}</strong>. Bom ponto de partida para a proposta.</li><li>Os 760 m² vêm da planta topográfica (a matrícula não tem área; o cadastro diz 565,50 m²), e os 349 m² construídos não batem com os 391 m² do cadastro.</li><li class="muted" style="font-size:13px">* Preço não confirmado (o portal bloqueia leitura automática). Datas “—” não aparecem no anúncio.</li></ul>'),
 'de': dict(h='Inserate', th=('Portal', 'Preis', 'Aktualisiert im Portal', 'Code', ''), open='Öffnen ↗',
   n='{n} Inserate', search='Letzte Internetsuche: <strong>{d}</strong> · täglich geprüft',
   hi='am höchsten', lo='am niedrigsten', cur='aktuell', new='neu hinzugefügt · {d}',
   k1='Aktueller Preis', k2='Inserierte Spanne', k3='Inserierte Fläche', diff='Differenz {v}', k3v='Grundstück / Wohnfläche',
   notes='<ul><li><strong>Verhandlung:</strong> Der niedrigste bisher inserierte Preis war <strong>{lo}</strong>. Guter Ausgangspunkt für das Angebot.</li><li>Die 760 m² stammen aus dem Vermessungsplan (Grundbuch ohne Fläche; Kataster 565,50 m²), und die 349 m² Wohnfläche passen nicht zu den 391 m² im Kataster.</li><li class="muted" style="font-size:13px">* Preis nicht bestätigt (Portal blockiert automatisches Auslesen). Daten „—“ stehen nicht im Inserat.</li></ul>'),
 'en': dict(h='Listings', th=('Portal', 'Price', 'Updated on portal', 'Code', ''), open='Open ↗',
   n='{n} listings', search='Last internet search: <strong>{d}</strong> · checked daily',
   hi='highest', lo='lowest', cur='current', new='recently added · {d}',
   k1='Current price', k2='Listed range', k3='Listed area', diff='difference {v}', k3v='plot / built',
   notes='<ul><li><strong>Negotiation:</strong> the lowest price listed so far was <strong>{lo}</strong>. A good starting point for an offer.</li><li>The 760 m² come from the survey plan (the land register has no area; the city record says 565.50 m²), and the 349 m² built area doesn\'t match the 391 m² in the city record.</li><li class="muted" style="font-size:13px">* Price not confirmed (the portal blocks automated reading). Dates "—" are not shown in the listing.</li></ul>'),
}

def render(tag, data):
    t, ads = T[tag], data['ads']
    prices = [a['price'] for a in ads]
    cur = Counter(prices).most_common(1)[0][0]
    lo, hi = min(prices), max(prices)
    today = date.fromisoformat(data['last_search'])
    stat = lambda k, v, s: f'<div class="stat"><div class="k">{k}</div><div class="v">{v}</div><div class="muted" style="font-size:13px">{s}</div></div>'
    rng = f'{brl(lo, tag)} – {brl(hi, tag)}' if lo != hi else brl(lo, tag)
    key = '<div class="grid">' + stat(t['k1'], brl(cur, tag), eur(cur, tag)) + stat(t['k2'], rng, t['diff'].format(v=brl(hi - lo, tag))) + stat(t['k3'], '760 m² / 349 m²', t['k3v']) + '</div>'
    rows = []
    order = sorted(ads, key=lambda a: (not a.get('new'), a['added']), reverse=False)
    for a in sorted(ads, key=lambda a: (0 if a.get('new') and today - date.fromisoformat(a['added']) <= timedelta(days=14) else 1)):
        pills = []
        if a.get('new') and today - date.fromisoformat(a['added']) <= timedelta(days=14):
            pills.append(('ok', t['new'].format(d=fd(a['added'], tag))))
        if a['price'] == hi and hi != lo: pills.append(('bad', t['hi']))
        elif a['price'] == lo and hi != lo: pills.append(('ok', t['lo']))
        elif a['price'] == cur: pills.append(('warn', t['cur']))
        p = ''.join(f' <span class="pill {c}">{x}</span>' for c, x in pills)
        star = '' if a.get('confirmed', True) else '*'
        rows.append(f'<tr><td>{a["portal"]}</td><td class="num"><strong>{brl(a["price"], tag)}{star}</strong><div class="muted" style="font-size:12px;font-weight:400">{eur(a["price"], tag)}</div></td>'
                    f'<td>{fd(a.get("date_portal", ""), tag)}</td><td>{a.get("code", "")}{p}</td><td><a href="{a["url"]}" target="_blank" rel="noopener">{t["open"]}</a></td></tr>')
    th = ''.join('<th' + (' class="num"' if i == 1 else '') + '>' + x + '</th>' for i, x in enumerate(t['th']))
    sub = t['n'].format(n=len(ads)) + ' · ' + t['search'].format(d=fd(data['last_search'], tag))
    return (f'<section id="{tag}-anuncios">\n  <h2>{t["h"]}</h2>\n  <p class="muted">{sub}</p>\n  {key}\n'
            f'  <div class="table-wrap"><table><tr>{th}</tr>{"".join(rows)}</table></div>\n  {t["notes"].format(lo=brl(lo, tag))}\n</section>\n')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--password', required=True); ap.add_argument('--searched', required=True)
    ap.add_argument('--add'); ap.add_argument('--init'); ap.add_argument('files', nargs='+')
    o = ap.parse_args()
    src = open(o.files[0], encoding='utf-8').read(); m = PRE.search(src)
    d = base64.b64decode
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=d(m.group(1)), iterations=int(m.group(4))).derive(o.password.encode())
    A = AESGCM(key); body = A.decrypt(d(m.group(2)), d(m.group(3)), None).decode()
    dm = DATA.search(body)
    if o.init: data = json.load(open(o.init))
    elif dm: data = json.loads(dm.group(1))
    else: sys.exit('sem dados de anúncios; use --init')
    data['last_search'] = o.searched
    added = []
    if o.add:
        known = {a['url'].split('?')[0] for a in data['ads']}
        for a in json.load(open(o.add)):
            if a['url'].split('?')[0] in known: continue
            a.update(added=o.searched, new=True); data['ads'].append(a); added.append(a); known.add(a['url'].split('?')[0])
    for tag in ('pt', 'de', 'en'):
        if f'<section id="{tag}-anuncios">' not in body: continue
        i = body.index(f'<section id="{tag}-anuncios">'); j = body.index('</section>', i) + len('</section>\n')
        body = body[:i] + render(tag, data) + body[j:]
    blob = '<script type="application/json" id="ads-data">' + json.dumps(data, ensure_ascii=False) + '</script>'
    body = DATA.sub(lambda _: blob, body) if DATA.search(body) else body + blob
    iv = os.urandom(12); ct = A.encrypt(iv, body.encode(), None); b = lambda x: base64.b64encode(x).decode()
    for p in o.files:
        s = open(p, encoding='utf-8').read()
        assert PRE.search(s).group(1) == m.group(1), f'{p}: salt diferente'
        s = re.sub(r'(var P=\{salt:"[^"]+",)iv:"[^"]+",ct:"[^"]+"', lambda mm: mm.group(1) + f'iv:"{b(iv)}",ct:"{b(ct)}"', s, count=1)
        open(p, 'w', encoding='utf-8').write(s)
    print(json.dumps({'total': len(data['ads']), 'added': [a['url'] for a in added], 'last_search': o.searched}, ensure_ascii=False))

if __name__ == '__main__': main()
