# dicas-ti-midia

Imagens e gerador dos posts diários do Instagram **@dicas.ti**. As imagens ficam públicas aqui para o Metricool puxar pelo link `raw.githubusercontent.com`.

## Rotina diária
| Horário | Post | Formato |
|---|---|---|
| 09h00 | **Bom dia, T.I.**: jornal matinal com 3 a 4 notícias de tecnologia, eventos e lançamentos | Carrossel: capa + 1 slide por notícia + agenda |
| 09h10 | Story "Post novo" com a capa do jornal | Story 1080×1920 (`…-story-jornal.png`) |
| 15h00 | **Seg/Qua/Sex: Dica prática**, um carrossel educativo e "salvável" (comandos, configs, checklists) | Carrossel `dica` (capa + 2 itens por slide + resumo) |
| 15h00 | **Ter/Qui/Sáb/Dom: Post leve**, com humor de T.I. e engajamento | Imagem única (`bingo`, `lista` ou `versus`) |
| 15h10 | Story "Post novo" com a capa do post da tarde | Story 1080×1920 (`…-story-tarde.png`) |

Por que isso: nas métricas de set/2026, os posts práticos (ex.: comandos Linux) tiveram muitos salvamentos e compartilhamentos, e o alcance só aparece nos dias com post. Então a prioridade é **constância + conteúdo salvável**.

## Estrutura
- `posts/AAAA-MM-DD.json`: conteúdo do dia (formato descrito em `tools/build.py`). O `2026-10-01.json` é o exemplo de referência.
- `AAAA-MM-DD/`: PNGs 1080×1350 gerados.
- `tools/build.py`: gera os PNGs (`python3 tools/build.py posts/AAAA-MM-DD.json`). Ele avisa `ESTOURO` se algum texto passar da borda.
- `historico.md`: um registro por dia com as notícias e o tema leve já usados, para não repetir.

## Regras de conteúdo
- As notícias precisam ser verdadeiras, recentes (últimos 3 dias) e confirmadas em pelo menos 2 fontes confiáveis. Nada de números inventados.
- Mistura boa: IA, segurança/cibersegurança, mercado/lançamentos, e algo de redes/infra quando houver. Tom direto, em pt-BR.
- A agenda traz eventos de tecnologia reais e próximos (Brasil de preferência), com datas confirmadas.
- Dica prática: tema útil e concreto (Linux, redes, MikroTik, Windows, segurança, cloud, ferramentas), com comandos/configs **corretos e testáveis**, de 4 a 8 itens. Nada genérico.
- Hashtags: 5 a 7 por legenda, **todas com `#`** (sem palavras soltas no fim da legenda).
- O post leve precisa ser original: nada de templates de meme com imagem de terceiros, personagens ou marcas. Os layouts alternam para variar.
- Nunca repetir notícia ou tema leve que já esteja em `historico.md`.
- Link de mídia no Metricool: `https://raw.githubusercontent.com/thiagoyuri14/dicas-ti-midia/main/AAAA-MM-DD/<arquivo>.png`
