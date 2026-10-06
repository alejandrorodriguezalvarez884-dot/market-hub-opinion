# Estado del proyecto y cómo continuar

Última actualización: 2026-10-06.

## Qué se pidió

El usuario quiere una sección de opinión en Market Hub (https://themarkethub.app/opinion/):

- artículos generados con IA a partir de las noticias del portal y de otras fuentes, de todo tipo;
- en un repo aparte del portal;
- que se actualice con una skill de Claude Code: él dice "actualízalo" y cuántos artículos quiere,
  y se añaden;
- con comentarios de los lectores en cada artículo, tipo Reddit (se puede responder a un
  comentario), que piden estar logueado para escribir y no para leer.

## Dónde estamos

| Hecho | Pendiente |
|---|---|
| Formato de artículo (un Markdown con sus datos arriba) y su validador: `src/marketopinion/articles.py`, `make check`. 10 tests en verde | |
| Publicación: `make publish` escribe en el Firestore del portal (`opinion/{slug}` y `opinion_state/front`) con la sesión de `gcloud` del usuario; `make preview` los deja donde los lee un portal en local | **No se ha publicado nada todavía**: falta el visto bueno del usuario y desplegar el portal con la pestaña |
| Skill `update-opinion` (`.claude/skills/update-opinion/SKILL.md`): ver qué hay, reunir material, elegir, escribir, comprobar, publicar, commitear y contar | Probarla en una sesión nueva (los seis primeros se escribieron en la sesión que la creó) |
| **Seis artículos iniciales** (2026-10-06), todos a partir de noticias del portal y de sus documentos: el mercado laboral parado (Analysis), el consumidor que gasta lo que no ingresa (Column), la previsión de AbbVie y sus cargos por compras de I+D (Explainer), la escisión de Vylor y sus seis acuerdos (Explainer), el adelanto de resultados de Apollo y la cifra anualizada (Column) y leer el 8-K antes que el titular (Column) | |
| Repo creado en local, con su commit inicial | **Crear el repo en GitHub** (lo tiene que hacer el usuario, o dar permiso a la cuenta con sesión en el equipo) y añadirlo como submódulo del workspace `market-hub` |

## Cómo está hecho

- **El portal lee, este repo escribe.** El portal (`market-hub-landing`, `src/markethub/opinion.py`)
  sirve la lista, cada artículo y los comentarios. Aquí no hay servicio ni web: solo los
  artículos, el validador y la publicación. Publicar no pide redesplegar el portal.
- **Los comentarios son del portal**, no de este repo: se guardan en su base de datos
  (`opinion_comments`), con su login.
- **Qué puede y qué no puede decir un artículo** está en `CLAUDE.md` y en la skill: opina, no
  aconseja; los hechos son de las fuentes que enlaza. `make check` para lo más evidente (frases de
  consejo, menos de dos fuentes, longitud, HTML en el texto) y no sustituye a leerlo.
- **El primer tag** de un artículo dice a qué afecta: `Macro`, `Markets` o uno de los sectores del
  portal.
- Un artículo que se borra de `articles/` sale de la lista al volver a publicar; su documento en
  Firestore se queda (un enlace directo seguiría abriendo).

## Siguientes pasos

1. Que el usuario lea los seis artículos (en local: `make preview` y abrir el portal).
2. Desplegar el portal y `make publish` aquí.
3. Crear el repo en GitHub, `git remote add origin …`, `git push -u origin main`, y en el
   workspace `git submodule add -b main <url> market-hub-opinion`.
