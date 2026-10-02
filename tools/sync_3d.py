#!/usr/bin/env python3
"""Sincroniza o modelo "Casa Jambú 3D" com a seção "Planta 3D e áreas" da página criptografada.

Fonte única do modelo: o artefato "Casa Jambú 3D"
  https://claude.ai/artifact/AAZcf4vsE6qzfQ126aEuRV
Leia-o com a ferramenta Artifact (action "read", path "index.html") e passe o arquivo salvo em --model.

Uso:
  python3 tools/sync_3d.py --password SENHA --model casa-3d.html FILE [FILE ...]

O script descriptografa cada FILE, troca o conteúdo de <template id="p3d-src"> pelo modelo
(escondendo o bloco de título e a legenda, que a seção da página já mostra) e recriptografa.
Se o modelo embutido já for igual, o arquivo não é alterado.
"""
import argparse, base64, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

PRE = re.compile(r'var P=\{salt:"([^"]+)",iv:"([^"]+)",ct:"([^"]+)",iter:(\d+)\}')
TPL = re.compile(r'<template id="p3d-src">.*?</template>', re.S)
EMBED_CSS = '.titleblock,.legend{display:none!important}\n'


def load_model(path):
    m = open(path, encoding='utf-8').read()
    # A leitura de um artefato pode vir com o esqueleto de publicação; fica só o corpo.
    if '<body>' in m[:4000]:
        m = m.split('<body>', 1)[1]
        m = re.sub(r'</body>\s*</html>\s*$', '', m)
    m = m.strip() + '\n'
    if '</style>' not in m or 'THREE' not in m:
        sys.exit(f'{path}: não parece ser o modelo 3D')
    if '</template>' in m:
        sys.exit(f'{path}: o modelo não pode conter </template>')
    return m.replace('</style>', EMBED_CSS + '</style>', 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--password', required=True)
    ap.add_argument('--model', required=True)
    ap.add_argument('files', nargs='+')
    a = ap.parse_args()
    tpl = '<template id="p3d-src">' + load_model(a.model) + '</template>'
    d, e = base64.b64decode, lambda x: base64.b64encode(x).decode()
    for p in a.files:
        s = open(p, encoding='utf-8').read()
        m = PRE.search(s)
        if not m:
            sys.exit(f'{p}: bloco criptografado não encontrado')
        key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=d(m.group(1)),
                         iterations=int(m.group(4))).derive(a.password.encode())
        body = AESGCM(key).decrypt(d(m.group(2)), d(m.group(3)), None).decode()
        found = TPL.findall(body)
        if len(found) != 1:
            sys.exit(f'{p}: esperava 1 <template id="p3d-src">, achei {len(found)}')
        if found[0] == tpl:
            print(f'{p}: modelo 3D já está atualizado')
            continue
        body = TPL.sub(lambda _: tpl, body)
        iv = os.urandom(12)
        ct = AESGCM(key).encrypt(iv, body.encode(), None)
        s = s[:m.start()] + f'var P={{salt:"{m.group(1)}",iv:"{e(iv)}",ct:"{e(ct)}",iter:{m.group(4)}}}' + s[m.end():]
        open(p, 'w', encoding='utf-8').write(s)
        print(f'{p}: modelo 3D atualizado')


if __name__ == '__main__':
    main()
