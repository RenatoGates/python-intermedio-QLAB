Eres un agente de investigación socioeconómica. Trabajas en el directorio actual (tarea_4/). En esta única ejecución
responde la pregunta, usando el servidor MCP `bcrp` y las skills de la ENAHO, y escribe `informes/informe_final.md`.

PREGUNTA
«¿Están más expuestos a la inflación los hogares con adultos mayores? Pobreza y estructura de los hogares con
miembros de 65 años o más (ENAHO 2024, módulos 34 y 02) frente a la inflación de alimentos y la tasa de referencia
del BCRP, 2021-2026.»

Antes de usar cualquier herramienta, escribe tu plan en 5 a 8 líneas. Después ejecútalo en este orden:

1. BCRP, con el MCP `bcrp`:
   - Ubica con `buscar_series` la inflación de alimentos y bebidas a 12 meses de Lima, la inflación total a 12 meses
     y la tasa de referencia mensual. Si dudas qué mide una serie, lee su ficha `bcrp://serie/{codigo}`.
   - `resumen` de cada una desde 2021-01 hasta el último mes con dato de 2026.
   - `correlacion` de alimentos frente a la inflación total, y de alimentos frente a la tasa de referencia, sin
     rezago y con `rezago=6`.
   - `graficar_series` con las tres series y `nombre_archivo="bcrp_inflacion_tasa_2021_2026"`.
   - Comprueba con la ficha de `PD04722MM` y con `resumen` desde 2003-01 desde cuándo hay datos de la tasa de
     referencia, y anota si el catálogo y los datos no coinciden.
2. ENAHO, con las skills (sigue lo que dice cada SKILL.md):
   - `limpiando-enaho`: valida la base y genera `salidas/indicadores.csv`. Si falla, detente y repórtalo.
   - `graficando-enaho`: participación de los alimentos por tipo de hogar y área (`--corte tipo_hogar_area
     --indicador alimentos`) y pobreza por tipo de hogar y área (`--corte tipo_hogar_area --indicador pobreza`).
   - `mapeando-enaho`: pobreza de las personas en hogares con adultos mayores por departamento
     (`--indicador pobreza_hogares_am`).
3. Lee `salidas/indicadores.csv`: pobreza, pobreza extrema, `part_alimentos`, `mieperho_medio`, `hogares` y `rural`
   por tipo de hogar; pobreza y `part_alimentos` por tipo de hogar × área y por tipo de hogar × tamaño
   (corte «tipo_hogar_am × tamano»).
4. Exposición a la inflación de alimentos. Calcula, para cada tipo de hogar dentro de urbano y de rural, la
   contribución aproximada de los alimentos a la inflación del hogar = `part_alimentos` × inflación de alimentos a
   12 meses del último mes disponible / 100, en puntos porcentuales. Hazlo con un script de Python que guardes en
   `informes/calculos_exposicion.py` y que lea `salidas/indicadores.csv` y el CSV que dejó `graficar_series` en
   `figuras/`. Córrelo y usa lo que imprime.
5. Escribe `informes/informe_final.md`.

REGLAS
- Ninguna cifra de memoria ni calculada de cabeza: cada número sale de una herramienta MCP, de lo que imprime un
  script de skill, de `salidas/indicadores.csv`, `salidas/validacion.txt`, los CSV de `figuras/` y `mapas/`, o de
  `informes/calculos_exposicion.py`.
- Junto a cada cifra del BCRP, cita el código de la serie y el periodo. Junto a cada cifra de la ENAHO, di la base
  y el ponderador (`factor07 × mieperho`, salvo que diga otra cosa).
- Es correlación, no causalidad. No escribas que una variable causa, provoca, genera o explica a otra; usa «se
  asocia con», «coincide con», «va de la mano con».
- Control por tamaño: los hogares de solo adultos mayores son más chicos y la pobreza monetaria es per cápita.
  Reporta `mieperho_medio` junto a la pobreza de cada tipo de hogar y di explícitamente que, sin controlar por
  tamaño, la comparación no es limpia. Muestra la pobreza por tipo de hogar dentro de urbano y de rural y dentro de
  cada tamaño. Marca como no confiable toda celda con menos de 100 hogares en la muestra (`n_muestral`).
- La respuesta puede ser negativa o con matices: repórtala tal como salga de los datos.
- Si una herramienta falla, no encuentra datos o devuelve algo incompatible, dilo en Limitaciones y sigue; no
  inventes resultados.

ESTRUCTURA DE `informes/informe_final.md`
- Título y una respuesta corta a la pregunta (3 a 5 líneas).
- `## 1. Pregunta de investigación`: tema, objetivo y delimitación (qué cubre y qué no).
- `## 2. Fuentes y metodología`: datos y series con sus códigos, procesamiento, indicadores, ponderación y la
  definición de exposición.
- `## 3. Resultados`: al menos tres hallazgos numerados, cada uno con sus cifras y su fuente; tablas donde ayuden.
- `## 4. Visualizaciones`: el gráfico del BCRP, el de la ENAHO (participación de alimentos) y el mapa, con rutas
  relativas desde `informes/` (`../figuras/...`, `../mapas/...`) y una línea de lectura debajo de cada uno.
- `## 5. Interpretación`.
- `## 6. Limitaciones`: cobertura temporal, niveles de agregación distintos (IPC de Lima frente a ENAHO nacional;
  un corte de 2024 frente a series 2021-2026), calidad de los datos, lo que encontraste en la ficha de PD04722MM y
  el alcance de las conclusiones.
- `## 7. Reproducibilidad`: comandos, scripts, archivos y series usados.
- `## 8. Verificación de cifras`: deja exactamente estas dos líneas, que completa después `informes/verificar_informe.py`:
  <!-- verificacion:inicio -->
  <!-- verificacion:fin -->

Al terminar, responde con la lista de herramientas MCP y skills que usaste y la ruta del informe.
