# Evaluación · sin MCP ni Skills frente a con MCP y Skills

Generado por `evaluacion/comparar.py` a partir de `resultados.csv`; ninguna cifra está escrita a mano.

## Diseño

10 preguntas con respuesta verificable en [`preguntas.csv`](preguntas.csv): 4 del BCRP, 4 de la ENAHO, 2 que combinan ambas. Las del BCRP son cuatro del archivo del profesor; su respuesta esperada se volvió a tomar de estadisticas.bcrp.gob.pe (API JSON y tabla HTML, sin pasar por el MCP). Las de la ENAHO salen de un cálculo directo desde los `.dta` con factores de expansión, con código distinto al de las Skills. Las combinadas multiplican una cifra de cada fuente. Todo lo calculó `verdades.py` antes de correr la evaluación.

**Criterio de acierto:** el valor está dentro de la tolerancia de la pregunta. Si responde `null` cuenta como «no sabe». En las combinadas, además, la fuente tiene que citar la ENAHO (o el INEI) y el BCRP; si no, cuenta como «se equivoca (fuente incompleta)».

Instrucción común a ambos modos (antes de cada pregunta):

```text
Responde con un solo número en «valor», en la unidad que pide la pregunta. Si no puedes saberlo con certeza, pon valor null: no estimes. En «fuente» di de dónde sale la cifra; si combinas varias fuentes, nómbralas todas.
```

| Pregunta | Tipo | Esperada | Tolerancia | Unidad | De dónde sale la respuesta esperada |
|---|---|---|---|---|---|
| ipc_set26 | bcrp | 4.5487 | 0.05 | % | BCRP, serie PN01273PM, estadisticas.bcrp.gob.pe (API JSON y tabla HTML: 4.55) |
| ipc_dic25 | bcrp | 1.5088 | 0.05 | % | BCRP, serie PN01273PM, estadisticas.bcrp.gob.pe (API JSON y tabla HTML: 1.51) |
| referencia_set26 | bcrp | 4.25 | 0.01 | % | BCRP, serie PD04722MM, estadisticas.bcrp.gob.pe (API JSON y tabla HTML: 4.25) |
| tc_15oct26 | bcrp | 3.4282 | 0.002 | S/ por US$ | BCRP, serie PD04638PD, estadisticas.bcrp.gob.pe (API JSON y tabla HTML: 3.428) |
| enaho_pobreza_nacional | enaho | 27.5795 | 0.1 | % | INEI, ENAHO 2024 (módulos 34 y 02); cálculo directo en evaluacion/verdades.py, ponderado con factor07 × mieperho |
| enaho_pobreza_rural | enaho | 39.3028 | 0.1 | % | INEI, ENAHO 2024 (módulos 34 y 02); cálculo directo en evaluacion/verdades.py, ponderado con factor07 × mieperho |
| enaho_pobreza_solo_am | enaho | 20.2572 | 0.1 | % | INEI, ENAHO 2024 (módulos 34 y 02); cálculo directo en evaluacion/verdades.py, ponderado con factor07 × mieperho |
| enaho_hogares_con_am | enaho | 30.6268 | 0.1 | % | INEI, ENAHO 2024 (módulos 34 y 02); cálculo directo en evaluacion/verdades.py, ponderado con factor07 |
| comb_exposicion_rural_oct26 | combinada | 3.0951 | 0.1 | puntos porcentuales | INEI, ENAHO 2024 (módulos 34 y 02); cálculo directo en evaluacion/verdades.py (participación rural 58.5741 %) × BCRP PN09822PM 2026-10 (5.2841 %) / 100 |
| comb_exposicion_solo_am_2025 | combinada | 0.6734 | 0.1 | puntos porcentuales | INEI, ENAHO 2024 (módulos 34 y 02); cálculo directo en evaluacion/verdades.py (participación 46.1133 %) × BCRP PN09822PM promedio 2025 (1.4603 %) / 100 |

## Qué herramientas tiene cada modo

|  | memoria | mcp_skills |
|---|---|---|
| Opciones de `claude -p` | `--tools "" --strict-mcp-config` | `--tools Bash,Read,Write,Glob,Skill --strict-mcp-config --mcp-config {copia}/.mcp.json --allowedTools mcp__bcrp Bash Read Write Glob Skill` |
| Directorio de trabajo | copia aislada de `tarea_4/` ({copia}) | la misma: sin `.git`, sin `evidencias_ia/` y sin `preguntas*.csv`, `resultados*.csv`, `verdades.py` ni `comparacion.md`; con el código, los datos y las salidas de las skills |
| Herramientas internas de Claude Code | ninguna (`--tools ""`) | Bash, Read, Write, Glob, Skill |
| Servidor MCP `bcrp` (5 herramientas, 1 recurso, 1 prompt) | no | sí (el `.mcp.json` de la copia, `--allowedTools mcp__bcrp`) |
| MCP `fetch` de `.mcp.json` | no | cargado pero no permitido (fuera de `--allowedTools`) |
| Otros MCP del usuario (conectores de claude.ai) | no (`--strict-mcp-config`) | no (`--strict-mcp-config`) |
| Skills de `tarea_4/.claude/skills/` | no (sin la herramienta Skill) | sí |
| `ReadMcpResourceTool` / `ListMcpResourcesTool` (leer `bcrp://serie/{codigo}`) | no | no: `--tools` las deja fuera, así que el recurso no se puede leer en esta evaluación |
| Leer archivos del repo (`salidas/`, `datos/`) | no | sí, con Read, Bash y Glob |
| Búsqueda web | no | no |
| Modelo, instrucción y sesión | Haiku, la misma instrucción, sesión nueva por pregunta (`--no-session-persistence`), cwd en la copia aislada | igual |

El modo `memoria` no puede leer archivos: no tiene herramientas, no hay `CLAUDE.md` y la memoria automática del directorio está vacía. El modo `mcp_skills` sí lee archivos, y por eso las 20 sesiones corren en una copia aislada de `tarea_4/` que no tiene la clave de respuestas ni el historial de git; puede leer `salidas/indicadores.csv`, que es la salida de la skill `limpiando-enaho` y forma parte de lo que se evalúa. La columna `toco_archivos_de_evaluacion` de `resultados.csv` marca cualquier sesión que haya intentado leer archivos de la evaluación.

## Resultados por modo

| Modo | Correctas | Se equivoca | No sabe (null) | Con errores registrados | Segundos promedio | Segundos mediana | Turnos promedio | Costo total US$ |
|---|---|---|---|---|---|---|---|---|
| Sin MCP ni Skills (memoria) | 1 de 10 | 0 | 9 | 0 | 4.7 | 4.8 | 2.0 | 0.0081 |
| Con MCP y Skills (mcp_skills) | 10 de 10 | 0 | 0 | 2 | 19.0 | 18.8 | 6.3 | 0.053 |

### Por tipo de pregunta

| Tipo | Sin MCP ni Skills (memoria) | Con MCP y Skills (mcp_skills) |
|---|---|---|
| BCRP | 0 de 4 | 4 de 4 |
| Combinada | 0 de 2 | 2 de 2 |
| ENAHO | 1 de 4 | 4 de 4 |

### Por pregunta

| Pregunta | Tipo | Esperada | memoria: respuesta | memoria: resultado | memoria: s | mcp_skills: respuesta | mcp_skills: resultado | mcp_skills: s |
|---|---|---|---|---|---|---|---|---|
| ipc_set26 | bcrp | 4.5487 ± 0.05 | — | no sabe | 5 | 4.55 | acierta | 14.1 |
| ipc_dic25 | bcrp | 1.5088 ± 0.05 | — | no sabe | 4.3 | 1.5088 | acierta | 10.8 |
| referencia_set26 | bcrp | 4.25 ± 0.01 | — | no sabe | 4 | 4.25 | acierta | 10 |
| tc_15oct26 | bcrp | 3.4282 ± 0.002 | — | no sabe | 4.6 | 3.42821 | acierta | 11 |
| enaho_pobreza_nacional | enaho | 27.5795 ± 0.1 | 27.6 | acierta | 4.8 | 27.6 | acierta | 28.3 |
| enaho_pobreza_rural | enaho | 39.3028 ± 0.1 | — | no sabe | 5.5 | 39.3 | acierta | 34.8 |
| enaho_pobreza_solo_am | enaho | 20.2572 ± 0.1 | — | no sabe | 5.1 | 20.2572 | acierta | 21.2 |
| enaho_hogares_con_am | enaho | 30.6268 ± 0.1 | — | no sabe | 3.9 | 30.63 | acierta | 20.9 |
| comb_exposicion_rural_oct26 | combinada | 3.0951 ± 0.1 | — | no sabe | 5.1 | 3.095 | acierta | 22 |
| comb_exposicion_solo_am_2025 | combinada | 0.6734 ± 0.1 | — | no sabe | 4.7 | 0.67 | acierta | 16.6 |

### Preguntas que mejoraron o empeoraron

| Pregunta | Cambio | memoria | mcp_skills |
|---|---|---|---|
| ipc_set26 | mejoró con MCP y Skills | no sabe | acierta |
| ipc_dic25 | mejoró con MCP y Skills | no sabe | acierta |
| referencia_set26 | mejoró con MCP y Skills | no sabe | acierta |
| tc_15oct26 | mejoró con MCP y Skills | no sabe | acierta |
| enaho_pobreza_rural | mejoró con MCP y Skills | no sabe | acierta |
| enaho_pobreza_solo_am | mejoró con MCP y Skills | no sabe | acierta |
| enaho_hogares_con_am | mejoró con MCP y Skills | no sabe | acierta |
| comb_exposicion_rural_oct26 | mejoró con MCP y Skills | no sabe | acierta |
| comb_exposicion_solo_am_2025 | mejoró con MCP y Skills | no sabe | acierta |

### Herramientas efectivamente usadas en `mcp_skills`

| Pregunta | MCP bcrp | Skills | Bash/Read/Glob/Write |
|---|---|---|---|
| ipc_set26 | 2 | — | 0 |
| ipc_dic25 | 2 | — | 0 |
| referencia_set26 | 2 | — | 0 |
| tc_15oct26 | 2 | — | 0 |
| enaho_pobreza_nacional | 0 | — | 5 |
| enaho_pobreza_rural | 2 | — | 6 |
| enaho_pobreza_solo_am | 0 | — | 4 |
| enaho_hogares_con_am | 0 | — | 4 |
| comb_exposicion_rural_oct26 | 2 | — | 3 |
| comb_exposicion_solo_am_2025 | 3 | — | 2 |

## Errores y respuestas fallidas

| Modo | Pregunta | Resultado | Qué pasó |
|---|---|---|---|
| memoria | ipc_set26 | no sabe | esperada 4.5487, respondió —; fuente: No he podido consultar ninguna fuente en esta sesión: no tengo acceso a internet ni a bases de datos. Mi conocimiento llega hasta junio de 2026, así que no teng |
| memoria | ipc_dic25 | no sabe | esperada 1.5088, respondió —; fuente: No he podido consultar ninguna fuente desde esta sesión: solo tengo acceso a la herramienta de salida estructurada, sin búsqueda web ni acceso a datos del INEI. |
| memoria | referencia_set26 | no sabe | esperada 4.25, respondió —; fuente: Sin fuente verificable. No tengo acceso a internet ni a la web del BCRP (bcrp.gob.pe) en esta sesión, y mi conocimiento llega solo hasta junio de 2026, antes de |
| memoria | tc_15oct26 | no sabe | esperada 3.4282, respondió —; fuente: No tengo acceso a internet ni a la base de datos del BCRP en esta sesión, y mi conocimiento llega hasta junio de 2026, así que no puedo verificar el tipo de cam |
| memoria | enaho_pobreza_rural | no sabe | esperada 39.3028, respondió —; fuente: No pude verificar la cifra. En esta sesión no tengo acceso a internet ni a los documentos del INEI, y no tengo el dato de la ENAHO 2024 sobre pobreza monetaria  |
| memoria | enaho_pobreza_solo_am | no sabe | esperada 20.2572, respondió —; fuente: No se calculó la cifra. En esta sesión solo tengo acceso a la herramienta de salida estructurada, así que no puedo leer en el directorio de trabajo (tarea_4) lo |
| memoria | enaho_hogares_con_am | no sabe | esperada 30.6268, respondió —; fuente: No disponible. No tengo acceso a los microdatos de la ENAHO 2024 del INEI ni a internet desde esta sesión, y no puedo ponderar los hogares con factor07 sin ello |
| memoria | comb_exposicion_rural_oct26 | no sabe | esperada 3.0951, respondió —; fuente: No se pudo calcular: no tengo acceso a las fuentes necesarias. (1) Participación promedio de los alimentos en el gasto de los hogares rurales, ENAHO 2024 (INEI) |
| memoria | comb_exposicion_solo_am_2025 | no sabe | esperada 0.6734, respondió —; fuente: No se pudo calcular. No tengo acceso a internet ni a herramientas para abrir archivos en esta sesión, así que no puedo obtener ni procesar los microdatos de la  |

<!-- conclusiones:inicio -->
## Conclusiones

1. **Con MCP y Skills, 10 de 10 correctas; sin ellos, 1 de 10.** Sin herramientas, Haiku casi nunca inventó: respondió `null` en 9 preguntas y se equivocó en 0. Acertó de memoria solo `enaho_pobreza_nacional`, una cifra publicada y muy difundida. La mejora del modo `mcp_skills` no es corregir errores, sino pasar de «no sé» a una cifra con fuente.
2. **Por tipo de pregunta** en `mcp_skills`: BCRP 4 de 4, ENAHO 4 de 4, combinadas 2 de 2. En las del BCRP, 4 de 4 sesiones resolvieron con `buscar_series` y `serie` del MCP; las cifras salen con más decimales o redondeadas, pero dentro de la tolerancia.
3. **Las Skills se usaron por sus salidas, no por la herramienta Skill.** Ninguna de las 10 sesiones invocó una skill (`Skill` aparece en 0). En 4 de las 6 preguntas de la ENAHO y combinadas, Haiku leyó con Bash lo que las skills ya habían dejado validado (`salidas/indicadores.csv`, `salidas/hogares_2024.parquet`, los CSV de `figuras/`) y desde ahí respondió. En 2 (`enaho_pobreza_nacional`, `enaho_pobreza_rural`) calculó directamente desde los `.dta` con `factor07 × mieperho`, sin las skills, y acertó. Las salidas validadas de las skills hicieron la mayor parte del trabajo, pero esta evaluación no prueba que el modelo sepa activar las skills cuando faltan; eso lo muestran las sesiones de `evidencias_ia/skills/`.
4. **Tiempo y costo.** `mcp_skills` tardó 19.0 s en promedio, frente a 4.7 s de `memoria`, y costó US$ 0.0530 contra US$ 0.0081 las 10 preguntas. Las de la ENAHO y las combinadas son las más lentas (24.0 s en promedio) porque el modelo explora archivos antes de calcular.
5. **El modelo buscó la cifra «oficial» fuera de los datos.** En 2 preguntas de la ENAHO (`enaho_pobreza_nacional`, `enaho_pobreza_rural`) intentó primero `mcp__fetch__fetch` sobre la web del INEI. `fetch` está en `.mcp.json` pero fuera de `--allowedTools`, así que se denegó; queda en la columna `errores` y luego respondió con los datos locales.
6. **Primera corrida, descartada por falta de aislamiento.** Dentro de `tarea_4/`, con la clave de respuestas a la vista, dio 9 de 10 con MCP y Skills y 1 de 10 sin ellos. Cambió `enaho_pobreza_nacional`: en esa corrida la sesión buscó la cifra publicada, encontró `evaluacion/verdades.py`, decidió no usarlo y respondió `null`. La corrida válida es la de la copia aislada. Su control de acceso marcó al principio 6 sesiones por un falso positivo (la carpeta temporal se llama «evaluacion_tarea4_…» y las URL del BCRP llevan «/resultados/»). Corregido y recalculado sobre las trazas guardadas, da 0 de 20 sesiones que tocaron archivos con respuestas, evidencias o git.
7. **Cuándo vale la pena.** Para cifras puntuales y recientes del BCRP, un MCP que baja la serie oficial basta y es rápido. Para la ENAHO, lo que hace la diferencia es tener una base validada y ponderada: el modelo, solo, no conoce cifras como la pobreza de los hogares de solo adultos mayores, y sin la limpieza correcta (residentes, `factor07 × mieperho`) un cálculo improvisado puede dar otra cifra. Con una sola corrida por modo y con Haiku, estas conclusiones son indicativas, no una medición de la variabilidad.
<!-- conclusiones:fin -->
