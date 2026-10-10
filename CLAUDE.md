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
