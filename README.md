# dicas-ti-midia

Imagens e gerador dos posts diários do Instagram **@dicas.ti**. As imagens ficam públicas aqui para o Metricool puxar pelo link `raw.githubusercontent.com`.

## Rotina diária
| Horário | Post | Formato |
|---|---|---|
| 09h | **Bom dia, T.I.**: jornal matinal com 3 a 4 notícias de tecnologia, eventos e lançamentos | Carrossel: capa + 1 slide por notícia + agenda |
| 15h | **Post leve**: humor de T.I. e engajamento | Imagem única (`bingo`, `lista` ou `versus`) |

## Estrutura
- `posts/AAAA-MM-DD.json`: conteúdo do dia (formato descrito em `tools/build.py`). O `2026-10-01.json` é o exemplo de referência.
- `AAAA-MM-DD/`: PNGs 1080×1350 gerados.
- `tools/build.py`: gera os PNGs (`python3 tools/build.py posts/AAAA-MM-DD.json`). Ele avisa `ESTOURO` se algum texto passar da borda.
- `historico.md`: um registro por dia com as notícias e o tema leve já usados, para não repetir.

## Regras de conteúdo
- As notícias precisam ser verdadeiras, recentes (últimos 3 dias) e confirmadas em pelo menos 2 fontes confiáveis. Nada de números inventados.
- Mistura boa: IA, segurança/cibersegurança, mercado/lançamentos, e algo de redes/infra quando houver. Tom direto, em pt-BR.
- A agenda traz eventos de tecnologia reais e próximos (Brasil de preferência), com datas confirmadas.
- O post leve precisa ser original: nada de templates de meme com imagem de terceiros, personagens ou marcas. Os layouts alternam para variar.
- Nunca repetir notícia ou tema leve que já esteja em `historico.md`.
- Link de mídia no Metricool: `https://raw.githubusercontent.com/thiagoyuri14/dicas-ti-midia/main/AAAA-MM-DD/<arquivo>.png`
