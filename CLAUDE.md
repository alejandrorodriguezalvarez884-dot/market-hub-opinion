# Instrucciones para agentes

Este repo guarda los artículos de opinión de Market Hub (https://themarkethub.app/opinion/). Lee
primero [docs/HANDOFF.md](docs/HANDOFF.md). Los artículos se escriben con la skill
[`update-opinion`](.claude/skills/update-opinion/SKILL.md), que es la que manda sobre cómo se
escribe uno.

Reglas que no se negocian:
- **Opinar sí, aconsejar no.** Un artículo puede defender una tesis, llevar la contraria o criticar
  una decisión de una empresa o de un banco central. No le dice al lector qué hacer con su dinero:
  nada de comprar, vender o mantener, precios objetivo ni carteras recomendadas. `make check` para
  los casos más claros; el resto es criterio de quien escribe.
- **Los hechos son de las fuentes.** Toda cifra, fecha y cita sale de una fuente que el artículo
  enlaza. No se inventan datos, citas ni fuentes, y no se escribe de memoria sobre lo que pasó: se
  comprueba. La opinión es lo que se construye encima, y se nota cuál es cuál.
- **Nada de textos ajenos.** Se enlaza a la prensa y se resume con palabras propias; no se copia.
- **Un artículo publicado no cambia de dirección.** El slug (el nombre del archivo sin la fecha) no
  se toca. Una corrección se hace en el mismo archivo y se dice al final del texto.
- **Cada artículo lleva su portada, dibujada aquí.** Un SVG o una página HTML en `covers/src/` que
  `make covers` convierte en `covers/<slug>.jpg` con el Chrome de esta máquina. No se usa ningún
  servicio ni modelo de generación de imágenes (ni Hugging Face ni otro) y no se coge ninguna
  imagen de fuera. Cada portada, de un estilo distinto a las anteriores. Sin logotipos, sin caras
  de personas reales, sin flechas de sube o baja.
- **Un artículo de un lector solo se publica cuando el usuario lo dice.** Los lectores los envían
  desde el portal (`/opinion/submit/`); el portal no publica nada: los guarda en un bucket y avisa
  al usuario por correo. Él los revisa y dice cuál sale. Entonces `make fetch ID=<id>` lo trae a
  `inbox/` (que no se commitea) y se termina como cualquier otro, con las mismas reglas: sus
  fuentes, opinar sí y aconsejar no, y su portada dibujada aquí. Se edita lo justo (longitud,
  claridad, erratas) y no se le cambia la tesis. Lleva la línea `author:` con el nombre con el que
  firmó. Tras publicarlo, `make mark` se lo dice a su autor. El correo de quien lo envió no se
  escribe en ningún archivo del repo ni en un commit.
- **Nada de trading** ni conectores de broker, como en el resto del workspace.
- **Nada programado.** Los artículos se escriben cuando el usuario lo pide.
- **Claves solo en `.env` o en el entorno.** Publicar usa la sesión de `gcloud` del usuario.

Convenciones:
- Hablar con el usuario en español. Artículos, código y comentarios en inglés.
- Python 3.12 con `uv`; Node solo para `make covers`. `make check` antes de publicar, siempre.
- Al terminar una tanda de artículos, actualizar "Dónde estamos" en `docs/HANDOFF.md`.
