# python-intermedio-QLAB

Tareas del curso de Ciencia de Datos con Python (QLAB / UP 2026-II) — Renato Gates Rojas ([@RenatoGates](https://github.com/RenatoGates)).

| Carpeta | Qué hay |
|---|---|
| [`tarea_1/`](tarea_1) | Clasificación de noticias peruanas: scraping, etiquetado con LLM, fine-tuning de DistilBETO y dashboard |
| [`tarea_2/`](tarea_2) | De documentos y audio a texto: OCR con PaddleOCR, ASR con faster-whisper, diarización y dashboard |
| [`.claude/skills/`](.claude/skills) | Sesión 16: tres skills que limpian, grafican y mapean la ENAHO |

---

# Sesión 16 · Skills que limpian, grafican y mapean la ENAHO

Tres skills de Claude Code que viven en el repositorio. Cualquiera clona, baja dos zip del
INEI y pide «un mapa de la pobreza por departamento»: Claude encadena las skills y obtiene
la cifra oficial.

| Skill | Entra | Sale |
|---|---|---|
| [`limpiando-enaho`](.claude/skills/limpiando-enaho) | Módulos 34 y 02 de la ENAHO | `salidas/personas_2024.parquet` y `salidas/validacion.txt` |
| [`graficando-enaho`](.claude/skills/graficando-enaho) | La base limpia y un corte | `figuras/pobreza_<corte>_2024.png` |
| [`mapeando-enaho`](.claude/skills/mapeando-enaho) | La base limpia y los límites departamentales | `mapas/pobreza_departamento.png` |

Las dos últimas dicen en su cuerpo: «Si no existe `salidas/personas_2024.parquet`, usa
primero la skill `limpiando-enaho`». Por eso un solo pedido activa dos skills seguidas.

## 1. Bajar los datos

Los microdatos no se versionan: `datos/` está en el `.gitignore`. Bájalos del portal del
INEI, donde **966** es el código de la ENAHO 2024, y descomprímelos en `datos/`:

| Archivo | Tamaño | Enlace |
|---|---|---|
| Módulo 34 · sumaria (una fila por hogar) | 16 MB | https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip |
| Módulo 02 · miembros (una fila por persona) | 6 MB | https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip |

```powershell
mkdir datos
curl -L -o datos/966-Modulo34.zip https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip
curl -L -o datos/966-Modulo02.zip https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip
```

No hace falta descomprimirlos a mano: `limpiar.py` lo hace solo. El GeoJSON de los
límites departamentales se descarga la primera vez que corre el mapa y queda cacheado
en `datos/`.

## 2. Instalar

```bash
uv sync
```

Instala pandas, pyarrow, geopandas y matplotlib desde `pyproject.toml`.

## 3. Correr todo

```bash
uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024
uv run .claude/skills/graficando-enaho/scripts/graficar.py --corte area
uv run .claude/skills/graficando-enaho/scripts/graficar.py --corte sexo
uv run .claude/skills/graficando-enaho/scripts/graficar.py --corte edad
uv run .claude/skills/mapeando-enaho/scripts/mapear.py --anio 2024
```

O, desde Claude Code abierto en la raíz del repo, en lenguaje normal:

```
¿Cuál fue la pobreza en Cusco en 2024?
Grafica la pobreza urbana y rural
Haz un mapa de la pobreza por departamento
```

## 4. Qué debe salir

`salidas/validacion.txt` se detiene si alguna de estas no se cumple:

| Cifra | Valor |
|---|---|
| Pobreza monetaria nacional | 27.6 % (27.58 % con la sumaria, 27.53 % con personas) |
| Pobreza extrema | 5.5 % |
| Hogares en la sumaria | 33,691 |
| Residentes habituales | 108,664 de 117,721 filas del módulo 02 |
| Urbano / rural | 24.8 % / 39.3 % |
| Cusco | 18.5 % |
| Departamentos con dato en el mapa | 25 de 25 |

La pobreza oficial de los 25 departamentos está en
[`referencias/pobreza_departamento_2024.csv`](referencias/pobreza_departamento_2024.csv);
`mapear.py` compara contra ella e imprime la diferencia máxima.

## 5. Las trampas que las skills resuelven

| Trampa | Qué pasa si no se cuida |
|---|---|
| Ceros a la izquierda | `conglome` «015009» y `ubigeo` «010101» como número pierden el cero y la unión falla |
| La columna `aÑo` | Llega con eñe y tilde; hay que normalizar los nombres antes de usarlos |
| No todos son residentes | 117,721 filas en el módulo 02, pero solo 108,664 residentes habituales |
| Uniones que duplican | Sin `validate="m:1"` un hogar repetido multiplica personas sin avisar |
| Encuestas no son personas | 33,691 hogares representan 34.5 millones de personas con su factor |
| `pobreza` es un código | 1, 2 y 3 son categorías: pobre es `pobreza <= 2`, nunca un promedio |
| Unir el mapa por nombre | «APURIMAC» no es «Apurímac»: se une `ubigeo[:2]` con `FIRST_IDDP` |

## 6. Evaluación

[`evaluacion.md`](evaluacion.md) tiene los tres pedidos corridos con y sin skills, con
`claude -p` y `claude -p --disallowedTools Skill`, y qué cambió en cada caso.

## Estructura

```text
.claude/skills/
  limpiando-enaho/    SKILL.md · reference.md · scripts/limpiar.py
  graficando-enaho/   SKILL.md · scripts/graficar.py
  mapeando-enaho/     SKILL.md · scripts/mapear.py
datos/                (no se versiona)
salidas/              personas_2024.parquet · validacion.txt
figuras/              pobreza_area_2024.png · pobreza_sexo_2024.png · pobreza_edad_2024.png
mapas/                pobreza_departamento.png
referencias/          pobreza_departamento_2024.csv
evaluacion.md · pyproject.toml
```

Fuente de los datos: INEI, Encuesta Nacional de Hogares (ENAHO) 2024.
