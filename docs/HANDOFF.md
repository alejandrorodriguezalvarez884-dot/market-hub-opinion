# Estado del proyecto y cómo continuar

Última actualización: 2026-10-16.

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
  comentario), que piden estar logueado para escribir y no para leer;
- desde el 2026-10-13, entre uno y cinco artículos nuevos cada día, escritos y publicados solos
  por el mantenimiento diario del workspace.

## Dónde estamos

| Hecho | Pendiente |
|---|---|
| **Un explicativo sobre el CPI de septiembre, antes de que saliera** (2026-10-14, pedido por el usuario para enlazarlo desde el hilo de X de la cuenta `@the_market_hub_`): *Today's CPI is expected to jump on gasoline. Read the part that moves slowly* (`todays-cpi-is-expected-to-jump-on-gasoline-read-the-part-that-moves-slowly`, Explainer). Lo esperado (resumen de Kiplinger), agosto según el BLS, la subida de la Fed de septiembre y su reunión del 27-28 de octubre; pone a prueba el Counterpoint del 8 de octubre. Portada: póster serigrafiado (un surtidor enorme y una tortuga con una casa a cuestas). Ojo: en el portal el slug de un artículo va **sin la fecha**; un enlace interno es `/opinion/article/?slug=<slug sin fecha>` | Se escribió antes del dato (12:30 UTC): si el usuario lo pide, una corrección o una nota al final con el resultado |
| Formato de artículo (un Markdown con sus datos arriba) y su validador: `src/marketopinion/articles.py`, `make check`. 11 tests en verde | |
| Publicación: `make publish` escribe en el Firestore del portal (`opinion/{slug}` y `opinion_state/front`) con la sesión de `gcloud` del usuario; `make preview` los deja donde los lee un portal en local. **Hay doce publicados** (seis el 2026-10-06, tres el 2026-10-08, tres el 2026-10-13) y se ven en https://themarkethub.app/opinion/ | |
| Skill `update-opinion` (`.claude/skills/update-opinion/SKILL.md`): ver qué hay, reunir material, elegir, escribir, comprobar, publicar, commitear y contar | **Probada en una sesión nueva el 2026-10-08** (`/update-opinion 3`): el ciclo entero funcionó sin tocar la skill |
| **Seis artículos iniciales** (2026-10-06), todos a partir de noticias del portal y de sus documentos: el mercado laboral parado (Analysis), el consumidor que gasta lo que no ingresa (Column), la previsión de AbbVie y sus cargos por compras de I+D (Explainer), la escisión de Vylor y sus seis acuerdos (Explainer), el adelanto de resultados de Apollo y la cifra anualizada (Column) y leer el 8-K antes que el titular (Column) | |
| **Tres artículos más** (2026-10-08): las actas de la Fed de septiembre, que sube tipos donde no está la inflación (Counterpoint, Macro); la pérdida de 3.000 a 4.000 millones de Chevron al salir de Hess Midstream, que es un precio y va a partidas especiales (Column, Energy); y la deuda vieja de Digital Realty al 2,99 % de media frente al 5,125 % de su bono nuevo en euros (Analysis, Real Estate). Además de la noticia del portal y su documento, cada uno usa otro documento primario: el informe de empleo del BLS, el 10-Q de Hess Midstream y el 10-Q de Digital Realty | |
| **Artículos de lectores** (2026-10-08): el portal deja que un usuario con sesión envíe un artículo a revisión (`market-hub-landing`, `submissions.py`): lo guarda en un bucket, sin publicar nada y sin avisar a nadie (el usuario decidió no recibir correo: `make inbox` dice qué hay). Aquí, `src/marketopinion/inbox.py` y `make inbox`, `make fetch ID=`, `make mark ID= STATUS= SLUG=` lo traen como borrador a `inbox/` (sin commitear), y dicen a su autor qué fue de él. Un artículo gana la línea opcional `author:` (el nombre con el que firmó el lector), que el portal muestra como "By ...". 15 tests en verde | El portal lo lleva desplegado desde el 2026-10-08 (`market-hub-00028-dkp`) y el bucket existe, vacío. **Sin estrenar**: probar el ciclo con un envío de verdad: `make inbox`, `make fetch`, publicar, `make mark` |
| **Artículos diarios** (2026-10-13): la tarea programada `market-hub-maintenance` de la app de Claude del usuario (08:00, en su Mac) sigue la skill `maintenance` del workspace (`market-hub/.claude/skills/maintenance/`, tarea `tasks/opinion.md`), que usa `update-opinion` para escribir, publicar y commitear entre uno y cinco artículos, sin revisión previa. No publica artículos de lectores: solo cuenta los que esperan. Cada día sustituye el texto de esta fila | **Última tanda: 2026-10-13, tres artículos; hay doce en total.** La encuesta de finanzas de las familias de la Fed (SCF 2025): las familias parecen sólidas por lo que tienen y apuradas por lo que ganan, con un 19,6 % que se retrasó en algún pago (Analysis, Macro; portada de tiza en pizarra). El informe de Prudential en Japón sobre 146 vendedores: el sistema de retribución pagaba el contrato nuevo y menos del 5 % el servicio posterior (Column, Financial Services; portada de formas Bauhaus). Los bonos subordinados de Sysco para comprar Jetro Restaurant Depot: deuda a 30 años que puede aplazar intereses diez años, y lo que cuesta ese derecho (Explainer, Consumer Defensive; portada de sello de correos grabado). Buzón de lectores: 0. Ojo: `make covers` volvió a renderizar seis portadas antiguas (bytes distintos) tras un clon nuevo; se restauraron con `git checkout` antes de publicar |
| **Artículos pedidos a mano** (fuera de la tanda diaria; esta fila guarda el último): 2026-10-16, tres a la vez. "Money left the chips for the dull stocks. The bond rally is a different story" (Analysis, Markets): del 5 al 15 de octubre SMH −11,8 % y XLP +7,0 %, XLV +5,9 %, XLU +4,2 %; el software solo tuvo un buen día (IGV −0,1 % en el tramo); la bajada del 10 años (5,31 % → 5,09 %) es casi toda de rentabilidad real (breakeven 2,36 % → 2,32 %, FRED), y la duda sobre los bonos es porque los plazos cortos no bajan. Portada: cartel art déco (puerta giratoria). "Bond traders call this inflation temporary because they expect the Fed to fight it" (Column, Macro): CPI 3,7 % y PPI +1,3 % en el mes (6,3 % anual), breakeven tranquilo en 2,32 %, y FedWatch (InvestmentNews, 15 oct) con un 33,8 % de subida en octubre y ~94 % de al menos una antes de diciembre; transitoria porque se espera que la Fed actúe. Portada: cómic de dos viñetas (el invitado que se queda). "Micron is not waiting for the market to catch up. Memory multiples close from the other side" (Column, Technology): ~6 veces el BPA guiado; en 2018 (4,6x) y 2022 (7,4x) el PER bajo en el pico acertó y se cerró por la caída del beneficio, no por la subida del precio. Sigue al de ASML del 14, con otro argumento. Portada: punto de cruz (montaña rusa). Hay dieciocho publicados | |
| Repo en GitHub (`alejandrorodriguezalvarez884-dot/market-hub-opinion`), submódulo del workspace `market-hub` | |
| **Portadas** (2026-10-06): cada artículo tiene la suya. El dibujo es código (`covers/src/<slug>.svg` o `.html`), `make covers` lo convierte en `covers/<slug>.jpg` (1200x675) con el Chrome local (`covers/render.mjs`, `playwright-core`), `make check` exige que exista y la línea `cover:` (el texto alternativo), y `make publish` la sube a `opinion_covers/{slug}` solo si es nueva o cambió. Las seis primeras: papel recortado (escisión), plano técnico (AbbVie), risografía a dos tintas (Apollo), cartel constructivista (8-K), pixel art (consumidor), tinta y aguada (empleo). Las tres del 2026-10-08: linograbado a dos tintas (Fed), bodegón plano de un tique de caja con su sello (Chevron) y diagrama isométrico hecho con un script (Digital Realty) | **Publicadas el 2026-10-06** y comprobadas en https://themarkethub.app/opinion/ (las seis cargan). El paso de portadas de la skill, probado en una sesión nueva el 2026-10-08 (dos pasadas en dos de las tres) |

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

1. Decidir si los artículos llevan alguna indicación de que están escritos con IA (el usuario
   prefirió no decir en la web cómo está hecha; el Reglamento europeo de IA lo pide para texto
   que informa al público, salvo revisión humana con responsabilidad editorial).
