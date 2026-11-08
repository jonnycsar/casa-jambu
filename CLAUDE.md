# Casa Jambú — notas para o Claude

`casa-jambo.html` é criptografado (AES-GCM, PBKDF2). A senha não fica neste repositório público; peça ao usuário ou use a da tarefa agendada "Novos anúncios Casa Jambú".

A mesma página existe em dois lugares, e toda mudança vai para os dois:
- este repositório (`casa-jambo.html`, commit + push em `main`);
- o artefato "Casa Jambú": https://claude.ai/artifact/M2NjHm8sVB1jadrpXZYUDQ (ler com a ferramenta Artifact, aplicar a mesma mudança no arquivo salvo e republicar na mesma url).

## Modelo 3D (conectado)

A fonte única do modelo 3D é o artefato "Casa Jambú 3D": https://claude.ai/artifact/AAZcf4vsE6qzfQ126aEuRV
A página mostra uma cópia dele na seção "Planta 3D e áreas" (aba "Documentação e pendências", primeira seção logo abaixo da capa, antes da Galeria; nomes dos cômodos desligados por padrão (botão "Nomes"); ids `pt-/de-/en-planta3d`, `<template id="p3d-src">`).

Sempre que o modelo 3D mudar:
1. Publique a mudança no artefato "Casa Jambú 3D" (edite o modelo lá, nunca direto na página).
2. Leia esse artefato com Artifact (`action: "read"`, `path: "index.html"`).
3. Rode `python3 tools/sync_3d.py --password SENHA --model <arquivo salvo> casa-jambo.html <arquivo salvo do artefato Casa Jambú>`.
4. Commit + push, e republique o artefato "Casa Jambú".

Se as medidas mudarem, atualize também os números da seção (áreas, tabela) nos três idiomas.
A tarefa diária também roda o passo 2–4, então a página nunca fica mais de um dia desatualizada.

## Vídeo da galeria

O vídeo da visita fica fora do HTML, em `casa-jambo-video.enc.mp4`: são 12 bytes de IV + o MP4 criptografado com a mesma chave da página (o nome termina em .mp4 só porque o artefato não serve outros tipos binários). A galeria baixa e decifra o arquivo ao abrir o vídeo. Ao republicar o artefato "Casa Jambú", ele precisa continuar como arquivo de apoio (`files: {"casa-jambo-video.enc.mp4": ...}`); se for omitido num republish, o arquivo já publicado é mantido.

## Numeração das seções (Hero, S1, S2…)

Os números aparecem via CSS no `<style>` logo antes de `<div class="hero">` (dentro do conteúdo criptografado): uma regra `#pt-x>h2::before,#de-x>h2::before,#en-x>h2::before{content:"Sn"}` por seção, na ordem da página. Ao criar, remover ou mover uma seção, atualize essas regras para a numeração continuar sequencial.

## Abas dos lotes vizinhos

Na seção Área do terreno, os lotes do mapa (`a.lotlink[data-lot]`) abrem as abas `.lotbox` logo abaixo. O clique é tratado pelo `<script>` com `function sel(box,n)` que fica fora do conteúdo criptografado, logo após `<div id="app" hidden></div>` (nos dois arquivos: repositório e artefato).

## Fotos da galeria (visitas de 30/08 e 03/10)

As 111 fotos novas ficam fora do HTML, criptografadas com a mesma chave da página (12 bytes de IV + AES-GCM, como o vídeo): `casa-jambo-miniaturas.enc.jpg` (pacote com as miniaturas: uint32 N, N tamanhos uint32, depois os JPEGs) e `casa-jambo-foto-000.enc.jpg` … `110` (versão grande, aberta no visualizador). Os botões ficam dentro do conteúdo criptografado, depois de `<!--poco-fotos-->`, nos três idiomas, e o `<script>` de `wireGallery` (fora do conteúdo criptografado) baixa e decifra os arquivos sob demanda. Ao republicar o artefato "Casa Jambú", todos esses arquivos precisam continuar publicados (se omitidos num republish, os já publicados são mantidos).
