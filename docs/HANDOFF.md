# Estado del proyecto y cómo continuar

Última actualización: 2026-10-06.

## Qué se pidió

El usuario quiere una sección de opinión en Market Hub (https://themarkethub.app/opinion/):

- artículos generados con IA a partir de las noticias del portal y de otras fuentes, de todo tipo;
- en un repo aparte del portal;
- que se actualice con una skill de Claude Code: él dice "actualízalo" y cuántos artículos quiere,
  y se añaden;
- con una portada en cada artículo, generada en la propia skill, en local y con Claude Code (sin
  Hugging Face ni otro servicio de imágenes), cada una de un estilo distinto, como si las subieran
  usuarios distintos;
- con comentarios de los lectores en cada artículo, tipo Reddit (se puede responder a un
  comentario), que piden estar logueado para escribir y no para leer.

## Dónde estamos

| Hecho | Pendiente |
|---|---|
| Formato de artículo (un Markdown con sus datos arriba) y su validador: `src/marketopinion/articles.py`, `make check`. 11 tests en verde | |
| Publicación: `make publish` escribe en el Firestore del portal (`opinion/{slug}` y `opinion_state/front`) con la sesión de `gcloud` del usuario; `make preview` los deja donde los lee un portal en local. **Los seis primeros están publicados** (2026-10-06) y se ven en https://themarkethub.app/opinion/ | |
| Skill `update-opinion` (`.claude/skills/update-opinion/SKILL.md`): ver qué hay, reunir material, elegir, escribir, comprobar, publicar, commitear y contar | Probarla en una sesión nueva (los seis primeros se escribieron en la sesión que la creó) |
| **Seis artículos iniciales** (2026-10-06), todos a partir de noticias del portal y de sus documentos: el mercado laboral parado (Analysis), el consumidor que gasta lo que no ingresa (Column), la previsión de AbbVie y sus cargos por compras de I+D (Explainer), la escisión de Vylor y sus seis acuerdos (Explainer), el adelanto de resultados de Apollo y la cifra anualizada (Column) y leer el 8-K antes que el titular (Column) | |
| Repo en GitHub (`alejandrorodriguezalvarez884-dot/market-hub-opinion`), submódulo del workspace `market-hub` | |
| **Portadas** (2026-10-06): cada artículo tiene la suya. El dibujo es código (`covers/src/<slug>.svg` o `.html`), `make covers` lo convierte en `covers/<slug>.jpg` (1200x675) con el Chrome local (`covers/render.mjs`, `playwright-core`), `make check` exige que exista y la línea `cover:` (el texto alternativo), y `make publish` la sube a `opinion_covers/{slug}` solo si es nueva o cambió. Las seis primeras: papel recortado (escisión), plano técnico (AbbVie), risografía a dos tintas (Apollo), cartel constructivista (8-K), pixel art (consumidor), tinta y aguada (empleo) | **Publicadas el 2026-10-06** y comprobadas en https://themarkethub.app/opinion/ (las seis cargan). Pendiente: probar el paso de portadas de la skill en una sesión nueva |

## Cómo está hecho

- **El portal lee, este repo escribe.** El portal (`market-hub-landing`, `src/markethub/opinion.py`)
  sirve la lista, cada artículo y los comentarios. Aquí no hay servicio ni web: solo los
  artículos, el validador y la publicación. Publicar no pide redesplegar el portal.
- **Los comentarios son del portal**, no de este repo: se guardan en su base de datos
  (`opinion_comments`), con su login.
- **Qué puede y qué no puede decir un artículo** está en `CLAUDE.md` y en la skill: opina, no
  aconseja; los hechos son de las fuentes que enlaza. `make check` para lo más evidente (frases de
  consejo, menos de dos fuentes, longitud, HTML en el texto) y no sustituye a leerlo.
- **Las portadas** viajan como bytes en un documento de Firestore cada una (por eso el tope de
  600 KB). La tarjeta del artículo lleva `cover: {alt, v}`; `v` es el hash de la imagen, va en la
  dirección que pide el navegador y así una portada redibujada se vuelve a pedir. Ningún servicio
  de imágenes: quien escribe el artículo dibuja la portada a mano, como código.
- **El primer tag** de un artículo dice a qué afecta: `Macro`, `Markets` o uno de los sectores del
  portal.
- Un artículo que se borra de `articles/` sale de la lista al volver a publicar; su documento en
  Firestore se queda (un enlace directo seguiría abriendo).

## Siguientes pasos

1. Usar la skill en una sesión nueva: `/update-opinion 3`, y ver que el ciclo entero funciona.
2. Decidir si los artículos llevan alguna indicación de que están escritos con IA (el usuario
   prefirió no decir en la web cómo está hecha; el Reglamento europeo de IA lo pide para texto
   que informa al público, salvo revisión humana con responsabilidad editorial).
