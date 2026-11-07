# Tarea 4 · Agente de investigación socioeconómica con MCP y Skills

**Pregunta de investigación:** ¿Están más expuestos a la inflación los hogares con adultos mayores? Pobreza y
estructura de los hogares con miembros de 65 años o más (ENAHO 2024, módulos 34 y 02) frente a la inflación de
alimentos y la tasa de referencia del BCRP, 2021-2026.

**Informe:** [`informes/informe_final.md`](informes/informe_final.md) · **Enunciado:**
[issue #201](https://github.com/d2cml-ai/Data-Science-Python/issues/201) del curso Python Intermedio (QLAB / UP).

<!-- resumen:inicio -->
| Componente | Resultado |
|---|---|
| Pruebas del MCP (`uv run pytest -q`) | 10 passed de 10 ([salida](evidencias_ia/mcp/pruebas.txt)) |
| Validación ENAHO 2024, base hogar `factor07 × mieperho` | pobreza 27.58 % · urbana 24.81 % · rural 39.30 % · 108,664 residentes habituales · 25/25 unidades territoriales · 15 de 15 comprobaciones esenciales ([validacion.txt](salidas/validacion.txt)) |
| Evaluación (Haiku, 10 preguntas) | sin MCP/Skills 1/10 · con MCP/Skills 10/10 ([resultados.csv](evaluacion/resultados.csv)) |
| Agente de investigación (una sesión, opus) | 5 herramientas MCP y 3 skills en 5.9 min ([traza](evidencias_ia/integracion/ejecucion_agente.md)) |
<!-- resumen:fin -->

> **Importante:** Claude Code se arranca **dentro de `tarea_4/`**. Ahí están `.mcp.json` y las skills de la tarea.
> Desde la raíz del repo se cargan las skills homónimas de la sesión 16, que ponderan distinto
> ([evidencia](evidencias_ia/skills/claude_code_desde_la_raiz.md)).

## 1. Objetivo del proyecto

Construir un agente que responda preguntas sobre la realidad socioeconómica del Perú con datos oficiales y cálculos
que se pueden repetir, no con lo que el modelo recuerda. Claude Code coordina dos componentes propios:

- un **servidor MCP del BCRP** que busca, descarga, resume, correlaciona y grafica las 17 mil series del Banco
  Central;
- tres **Skills de la ENAHO 2024** del INEI que limpian y validan los microdatos, grafican y mapean.

El proyecto se evalúa de dos formas: con la pregunta de investigación, resuelta en una sola ejecución del agente, y
con 10 preguntas verificables que Claude responde con y sin esos componentes.

## 2. Arquitectura general del agente

```text
                        Claude Code, arrancado en tarea_4/
            (lee .mcp.json y .claude/skills/; Haiku, Sonnet u Opus)
                 │                                    │
     MCP por stdio (uv run mcp/server.py)      Skills (SKILL.md + scripts con uv run)
                 │                                    │
   ┌─────────────┴──────────────┐     ┌───────────────┴──────────────────────────────┐
   │ mcp/server.py (FastMCP 4)  │     │ limpiando-enaho → salidas/hogares_2024.parquet │
   │  buscar_series             │     │                   salidas/personas_2024.parquet│
   │  serie · resumen           │     │                   salidas/indicadores.csv      │
   │  correlacion               │     │                   salidas/validacion.txt       │
   │  graficar_series → figuras/│     │ graficando-enaho → figuras/*.png + .csv        │
   │  recurso bcrp://serie/{c}  │     │ mapeando-enaho   → mapas/*.png + .csv          │
   │  prompt informe(tema)      │     │ (si falta la base, corren antes limpiando)     │
   └─────────────┬──────────────┘     └───────────────┬──────────────────────────────┘
                 │                                    │
     API de estadisticas.bcrp.gob.pe        datos/ (ignorado por git): .dta del INEI,
     (catálogo en datos/catalogo_bcrp.csv)  GeoJSON departamental, catálogo del BCRP
                 └──────────────┬─────────────────────┘
                                ▼
           informes/informe_final.md  (+ informes/verificar_informe.py)
```

Toda cifra sale de una llamada o un script que se puede volver a correr: el modelo no hace cuentas. El MCP calcula
variaciones, promedios y correlaciones en Python. Las Skills ponderan con los factores de expansión y se detienen si
una validación esencial falla.

## 3. Herramientas MCP

Servidor [`mcp/server.py`](mcp/server.py), hecho con FastMCP 4.1 a partir del proyecto de la sesión 04 (TODO 1 a 5).

| Componente | Qué hace | Cuándo lo usa el agente |
|---|---|---|
| `buscar_series(texto, frecuencia, limite)` | Busca en el catálogo de 17 mil series por palabras | Primero, para encontrar el código |
| `serie(codigo, desde, hasta)` | Datos periodo a periodo y la URL de la fuente. Convierte fechas al formato de la API según la frecuencia, lee meses «Sep» y días «Set», salta «n.d.», reintenta si la API responde la página de bloqueo y guarda en memoria lo bajado | Para citar un dato puntual |
| `resumen(codigo, desde, hasta)` | Primero, último, cambio, variación %, promedio, máximo y mínimo; avisa si la serie ya está en % | Para cualquier cifra derivada |
| **`correlacion(codigo_a, codigo_b, desde, hasta, rezago)`** (propia) | Alinea dos series de la misma frecuencia, admite rezago y devuelve r de Pearson, pares, brecha media y en cuántos periodos a > b, con fuentes y la advertencia de que no es causalidad | Para comparar la inflación de alimentos con la total o con la tasa de referencia |
| **`graficar_series(codigos, desde, hasta, nombre_archivo)`** (propia) | Grafica 1 a 3 series en un solo eje con los datos que baja el servidor y guarda PNG y CSV en `figuras/` | Para el gráfico del BCRP del informe |
| Recurso `bcrp://serie/{codigo}` | Ficha del catálogo: nombre, grupo, frecuencia, inicio, quién la produce y enlaces web y API | Para saber qué mide una serie |
| Prompt `informe(tema)` | Pide un informe que cite código, periodo y fuente de cada cifra, sin cuentas a mano ni causalidad | `/mcp__bcrp__informe <tema>` |

Pruebas: [`mcp/test_server.py`](mcp/test_server.py) es el del profesor sin cambios (mismo blob de git) y
[`mcp/test_mios.py`](mcp/test_mios.py) agrega dos: `correlacion` contra un cálculo independiente con numpy (con y sin
rezago, y el error con frecuencias distintas) y la ficha real del recurso. Las dos se probaron con mutantes del
servidor: cada una falla cuando se rompe lo que prueba.

## 4. Las tres Skills

En [`.claude/skills/`](.claude/skills/), adaptadas de las de la sesión 16 (no reescritas). Se activan por lenguaje
natural y se coordinan: si graficando o mapeando no encuentran la base procesada, terminan con código 3 y su
SKILL.md manda correr antes `limpiando-enaho`.

| Skill | Qué hace | Salidas |
|---|---|---|
| [`limpiando-enaho`](.claude/skills/limpiando-enaho/SKILL.md) | Lee `sumaria-2024.dta` (por nombre exacto, nunca la `-12g`) y `enaho01-2024-200.dta`; normaliza columnas; filtra residentes habituales; une personas y hogares con `validate="m:1"`; construye pobreza, departamento, área, tipo de hogar según adultos mayores, tamaño y participación de los alimentos en el gasto (8 grupos del do-file oficial del INEI); valida 15 condiciones esenciales y se detiene con código 2 si alguna falla | `salidas/hogares_2024.parquet`, `salidas/personas_2024.parquet`, [`salidas/indicadores.csv`](salidas/indicadores.csv), [`salidas/validacion.txt`](salidas/validacion.txt) |
| [`graficando-enaho`](.claude/skills/graficando-enaho/SKILL.md) | Barras ponderadas de pobreza, pobreza extrema o participación de alimentos por área, departamento, tipo de hogar, tipo de hogar × área, sexo o edad, con título analítico calculado, unidad, fuente, base y tamaño de muestra | [`figuras/`](figuras/) |
| [`mapeando-enaho`](.claude/skills/mapeando-enaho/SKILL.md) | Coropleta por departamento: une `ubigeo[:2]` con `FIRST_IDDP` (1:1), exige 25 unidades con dato y Lima y Callao separados, y compara con la referencia de la sesión 16 | [`mapas/`](mapas/) |

**Ponderación.** La cifra oficial es la base hogar ponderada con `factor07 × mieperho`, la que publica el INEI y
contra la que se valida (27.6 %, urbana 24.8 %, rural 39.3 %). La base persona con `facpob07` aparece en
`validacion.txt` como línea secundaria rotulada y solo se usa para cortes por sexo y edad. Las skills de la sesión
16, en la raíz del repo, grafican con `facpob07`. Cada SKILL.md de esta carpeta dice cuál versión es y en qué
difiere.

## 5. Fuentes y enlaces para descargar los datos

| Fuente | Datos | Enlace |
|---|---|---|
| INEI | ENAHO 2024, módulo 34 (sumaria) | https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip |
| INEI | ENAHO 2024, módulo 02 (miembros del hogar) | https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip |
| Repositorio del curso | Límites departamentales (GeoJSON) | https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson |
| BCRP | Catálogo de series (se baja solo) | https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata |
| BCRP | Series: `PN09822PM` (IPC alimentos y bebidas, Lima, var. % 12 meses), `PN01273PM` (IPC, var. % 12 meses), `PD04722MM` (tasa de referencia) y las de la evaluación | https://estadisticas.bcrp.gob.pe/estadisticas/series/ |

Los zip del INEI se descomprimen en `datos/` tal como vienen (`datos/966-Modulo34/966-Modulo34/sumaria-2024.dta`,
etc.); `limpiar.py` busca los archivos por nombre dentro de `datos/`. El GeoJSON y el catálogo se descargan solos la
primera vez. `datos/` está en `.gitignore`.

## 6. Instalación con `uv`

```bash
git clone https://github.com/RenatoGates/python-intermedio-QLAB
cd python-intermedio-QLAB/tarea_4
uv sync                        # Python 3.11+, FastMCP 4, pandas, pyarrow, geopandas, matplotlib, pytest
```

Hace falta [Claude Code](https://claude.com/claude-code) con la sesión iniciada y, para el MCP `fetch`, `uvx`.
No se usan claves de API: el BCRP y el INEI son públicos.

## 7. Conectar el MCP a Claude Code

`.mcp.json` ya está en el repo. Para recrearlo desde `tarea_4/`:

```bash
claude mcp add --scope project bcrp -- uv run mcp/server.py
claude mcp add --scope project fetch -- uvx mcp-server-fetch
claude mcp add --transport http fastmcp-docs https://gofastmcp.com/mcp   # documentación de FastMCP 4 (opcional)
```

Luego, **dentro de `tarea_4/`**, `claude`, aprobar los servidores de `.mcp.json` y revisar con `/mcp` que `bcrp`
esté conectado. Prueba rápida: `@bcrp:bcrp://serie/PD04722MM ¿qué mide esta serie?` o
`/mcp__bcrp__informe inflación de alimentos`.

## 8. Reproducir el procesamiento y las pruebas

Todo desde `tarea_4/`:

```bash
uv run pytest -q                                                              # 10 pruebas del MCP
uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024         # limpieza y validación ENAHO
uv run .claude/skills/graficando-enaho/scripts/graficar.py --corte tipo_hogar_area --indicador alimentos
uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza
uv run evidencias_ia/integracion/ejecutar_agente.py                          # Parte 3: el agente en una sesión
uv run informes/verificar_informe.py                                         # verificación independiente de cifras
uv run evaluacion/verdades.py                                                # respuestas esperadas (antes de evaluar)
uv run evaluacion/evaluar.py --modelo haiku --paralelo 2                     # Parte 4: memoria vs mcp_skills
uv run evaluacion/comparar.py                                                # comparacion.md y este resumen
```

## 9. Resultados de la evaluación

10 preguntas (4 del BCRP tomadas del archivo del profesor, 4 de la ENAHO y 2 que combinan ambas), cada una en una
sesión nueva de `claude -p` con Haiku, en dos modos: `memoria` (sin herramientas) y `mcp_skills` (MCP `bcrp` y las
herramientas que usan las Skills). Las respuestas esperadas las calculó
[`evaluacion/verdades.py`](evaluacion/verdades.py) antes de evaluar: las del BCRP directamente en
estadisticas.bcrp.gob.pe (API y tabla HTML, sin el MCP) y las de la ENAHO con un cálculo directo desde los `.dta`.
Las sesiones corren en una copia aislada de `tarea_4/`, sin `.git` ni archivos con las respuestas, para que el modo
con herramientas no pueda leer la clave. Cada sesión quedó guardada en
[`evidencias_ia/evaluacion/sesiones/`](evidencias_ia/evaluacion/sesiones/).

<!-- evaluacion:inicio -->
| Modo | Correctas | Se equivoca | No sabe (null) | Con errores registrados | Segundos promedio | Segundos mediana | Turnos promedio | Costo total US$ |
|---|---|---|---|---|---|---|---|---|
| Sin MCP ni Skills (memoria) | 1 de 10 | 0 | 9 | 0 | 4.7 | 4.8 | 2.0 | 0.0081 |
| Con MCP y Skills (mcp_skills) | 10 de 10 | 0 | 0 | 2 | 19.0 | 18.8 | 6.3 | 0.053 |

| Tipo | Sin MCP ni Skills (memoria) | Con MCP y Skills (mcp_skills) |
|---|---|---|
| BCRP | 0 de 4 | 4 de 4 |
| Combinada | 0 de 2 | 2 de 2 |
| ENAHO | 1 de 4 | 4 de 4 |
<!-- evaluacion:fin -->

Detalle por pregunta, errores y herramientas de cada modo: [`evaluacion/comparacion.md`](evaluacion/comparacion.md)
y [`evaluacion/resultados.csv`](evaluacion/resultados.csv).

## 10. Limitaciones y problemas encontrados

<!-- limitaciones:inicio -->
**De la investigación** (el detalle está en la sección 6 del informe):

- **Dos fuentes, dos escalas.** La ENAHO es un corte nacional de 2024; el IPC del BCRP es de Lima Metropolitana y va
  de 2021 a 2026. La «exposición» aplica la estructura de gasto de 2024 a la inflación de otros meses: es una
  aproximación de primer orden, no la inflación que vive cada hogar. Las correlaciones entre series agregadas
  describen co-movimiento, no causalidad.
- **Sin intervalos de confianza.** La ENAHO es una muestra y las skills no calculan errores estándar con el diseño
  muestral. Las diferencias menores a un punto no deben leerse como reales. Las celdas con menos de 100 hogares se
  marcan como no confiables en el informe y en los pies de los gráficos.
- **El control por tamaño es parcial.** Compara tipos de hogar dentro de cada tamaño o dentro de cada área, no las
  dos cosas a la vez. El tipo de hogar se define con los residentes habituales del módulo 02 y el tamaño con
  `mieperho` de la sumaria, que no coinciden en todos los hogares; de ahí salen celdas raras como hogares de «1
  persona» con adultos mayores y menores de 65.
- **Gasto en alimentos.** La participación es nominal y sigue los 8 grupos del do-file del INEI, que incluyen
  autoconsumo y donaciones. Mide peso en el presupuesto, no exposición a precios de mercado, y puede sobrestimar la
  exposición en lo rural. La sumaria 2024 no trae `gru52hd2`, una de las variables del do-file (se toma como 0 y se
  avisa en `validacion.txt`).

**De los datos y las herramientas:**

- **El catálogo del BCRP no siempre dice la verdad sobre las series.** La ficha de `PD04722MM` dice que empieza en
  Ene-2004, pero la API y la tabla HTML traen datos desde 2003-09 (el agente lo encontró y `verificar_informe.py` lo
  confirmó). La «fecha de fin» del catálogo está atrasada en las series mensuales y la «unidad de medida» viene vacía
  en todas, así que la ficha del recurso no la incluye: la unidad va en el nombre del grupo.
- **La API del BCRP responde igual a dos problemas distintos.** Un código inexistente y el bloqueo por pedidos
  seguidos devuelven la misma página HTML con HTTP 200. El servidor valida el código contra el catálogo antes de
  llamar a la API y reintenta con espera; si el bloqueo dura más, la herramienta falla con un mensaje que lo dice.
- **Las dos sumarias del módulo 34.** `sumaria-2024-12g.dta` tiene la misma pobreza y los mismos factores que
  `sumaria-2024.dta`, pero otra agregación del gasto. `limpiar.py` exige el nombre exacto, y si alguien la renombra,
  la comprobación de gasto lo detecta y detiene el proceso (probado).
- **Skills duplicadas en el repo.** Las de la sesión 16 (raíz) y las de esta tarea se llaman igual. Claude Code
  carga las del directorio donde arranca: por eso hay que abrirlo dentro de `tarea_4/`.
- **Recursos MCP en modo `-p`.** Con `--tools ""`, Claude Code apaga también `ReadMcpResourceTool`, y la mención
  `@bcrp:bcrp://…` no adjunta el recurso por sí sola. El primer intento falló por eso; la evidencia guarda los dos
  intentos. En la evaluación, ninguno de los dos modos puede leer recursos.
- **FastMCP 4 y el modelo.** El modelo tiende a escribir FastMCP 2: prompts con `PromptMessage`, campos en
  camelCase. Se consultó la documentación de `gofastmcp.com/mcp` antes de escribir el servidor. El MCP
  `fastmcp-docs` solo queda disponible en una sesión nueva, así que en la de desarrollo se llamó con un cliente
  FastMCP.

**De la evaluación:**

- **La primera corrida tenía la clave de respuestas a la vista.** Corrió dentro de `tarea_4/`, y en una pregunta la
  sesión con herramientas encontró `evaluacion/verdades.py`. No lo usó, pero también podría haber leído
  `preguntas.csv` o el historial de git, y esa corrida no guardaba qué archivos se leyeron. Se repitió todo en una
  copia aislada que no tiene esos archivos; la primera corrida se conserva en
  [`evidencias_ia/evaluacion/`](evidencias_ia/evaluacion/) y sus diferencias se comentan en `comparacion.md`. Las
  respuestas esperadas no se tocaron.
- Hay una sola corrida válida por modo con Haiku, así que no se mide la variabilidad entre corridas.
- El modo `mcp_skills` puede leer `salidas/indicadores.csv`, que es la salida de una skill: eso forma parte de lo que
  se evalúa. El modo `memoria` no puede leer nada.
- Las respuestas esperadas de la ENAHO, salvo la pobreza nacional y la rural que publica el INEI, salen de un
  cálculo propio. Es independiente de las skills, pero no es una cifra oficial publicada.
- Las combinadas usan una fórmula definida en la propia pregunta.

**Del proceso:** `gh` no está instalado en esta máquina, así que el PR se abre desde el enlace de comparación de
GitHub.
<!-- limitaciones:fin -->

## 11. Ejemplo de una ejecución completa

Interactivo, que es como se usa:

```bash
cd python-intermedio-QLAB/tarea_4      # SIEMPRE dentro de tarea_4/
claude                                 # aprobar bcrp y fetch de .mcp.json la primera vez
```

y pegar el pedido de [`evidencias_ia/integracion/pedido_agente.md`](evidencias_ia/integracion/pedido_agente.md)
(la pregunta, el plan y las reglas). La ejecución documentada se hizo sin intervención, con el mismo pedido:

```bash
cd tarea_4
claude -p "$(cat evidencias_ia/integracion/pedido_agente.md)" --model opus \
  --strict-mcp-config --mcp-config .mcp.json \
  --tools "Skill,Bash,Read,Write,Edit,Glob,Grep,ListMcpResourcesTool,ReadMcpResourceTool" \
  --allowedTools mcp__bcrp Skill Bash Read Write Edit Glob Grep ListMcpResourcesTool ReadMcpResourceTool \
  --output-format stream-json --verbose --no-session-persistence
```

`evidencias_ia/integracion/ejecutar_agente.py` hace exactamente eso, borra antes las bases procesadas para que la
cadena de skills corra completa y guarda la traza. Qué pasó en esa ejecución:

<!-- ejecucion:inicio -->
- Modelo: opus; duración: 5.9 min; turnos: 50; costo informado por Claude Code: US$ 1.94; terminó con error: False.
- Herramientas MCP usadas: `mcp__bcrp__buscar_series`, `mcp__bcrp__correlacion`, `mcp__bcrp__graficar_series`, `mcp__bcrp__resumen`, `mcp__bcrp__serie`.
- Skills usadas: `graficando-enaho`, `limpiando-enaho`, `mapeando-enaho`.
- Recursos MCP leídos: `bcrp://serie/PD04722MM`, `bcrp://serie/PN09822PM`, `bcrp://serie/PN01273PM`.
- Resultado: [`informes/informe_final.md`](informes/informe_final.md), con la verificación independiente de cifras al final. Traza completa: [`ejecucion_agente.md`](evidencias_ia/integracion/ejecucion_agente.md); bitácora: [`bitacora.json`](evidencias_ia/integracion/bitacora.json).
<!-- ejecucion:fin -->

## 12. Evidencias del uso de inteligencia artificial

Todo el proyecto se desarrolló con Claude Code. En [`evidencias_ia/`](evidencias_ia/):

| Carpeta | Contenido |
|---|---|
| [`mcp/`](evidencias_ia/mcp/) | La conversación de desarrollo del servidor (Partes 0 y 1), la salida de pytest y tres sesiones de Claude Code usando las herramientas, el recurso y el prompt |
| [`skills/`](evidencias_ia/skills/) | La conversación de la Parte 2 y sesiones que muestran activación por lenguaje natural, coordinación (mapa sin base → limpieza → mapa), invocación directa y qué versión de las skills carga cada directorio |
| [`integracion/`](evidencias_ia/integracion/) | La conversación de la Parte 3, el pedido, la traza completa de la ejecución del agente y su bitácora (herramientas MCP y skills usadas) |
| [`evaluacion/`](evidencias_ia/evaluacion/) | La conversación de la Parte 4, la traza de cada una de las 20 sesiones de la evaluación (`sesiones/`), la salida de `evaluar.py` y la primera corrida, descartada por falta de aislamiento |

Las conversaciones se exportaron de `~/.claude/projects/` a Markdown con
[`evidencias_ia/exportar_conversacion.py`](evidencias_ia/exportar_conversacion.py), que reemplaza la carpeta
personal por `~`, quita el correo y omite imágenes y bloques de razonamiento interno. Antes de cada commit se buscó
en `evidencias_ia/` cualquier token, clave o dato personal.
