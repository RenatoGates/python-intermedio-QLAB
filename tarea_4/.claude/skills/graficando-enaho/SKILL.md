---
name: graficando-enaho
description: Hace gráficos de barras ponderados de la ENAHO 2024 del INEI - pobreza monetaria, pobreza extrema o participación de los alimentos en el gasto - por área urbana o rural, departamento, presencia de adultos mayores (65+) en el hogar, sexo o grupo de edad. Úsala cuando pidan graficar, comparar o visualizar la pobreza o el gasto de los hogares de la ENAHO. Si no existe la base procesada, usa antes limpiando-enaho. Versión de la tarea 4.
argument-hint: [area|departamento|tipo_hogar|tipo_hogar_area|sexo|edad]
---

# Graficar la ENAHO · versión tarea_4

> **Cuál versión es esta.** Hay otra `graficando-enaho` en la raíz del repo (sesión 16) que pondera todo con
> `facpob07`. Esta usa la **base hogar con `factor07 × mieperho`**, la de la cifra oficial, para los cortes de hogar,
> y `facpob07` solo para sexo y edad, rotulado en el pie del gráfico. Para usar esta versión se arranca `claude`
> dentro de `tarea_4/`.

1. **Si no existe `salidas/hogares_2024.parquet` (o `salidas/personas_2024.parquet` para sexo y edad), usa primero
   la skill `limpiando-enaho`** y espera a que termine sin error. Sin base validada no hay gráfico. El script
   también lo detecta: termina con código 3 y dice qué correr.

2. Elige el corte y el indicador según el pedido. **Solo estos valores exactos**; `$0` trae texto libre, nunca lo
   pases tal cual al script.

   | Si piden… | `--corte` | Base y peso |
   |---|---|---|
   | urbano y rural, área de residencia | `area` | hogar, `factor07 × mieperho` |
   | departamentos, regiones | `departamento` | hogar, `factor07 × mieperho` |
   | hogares con o sin adultos mayores, adultos mayores de 65 | `tipo_hogar` | hogar, `factor07 × mieperho` |
   | lo anterior separado por área | `tipo_hogar_area` | hogar, `factor07 × mieperho` |
   | hombres y mujeres | `sexo` | persona, `facpob07` |
   | grupos de edad, niños, jóvenes, mayores | `edad` | persona, `facpob07` |

   | Si piden… | `--indicador` |
   |---|---|
   | pobreza monetaria (por defecto) | `pobreza` |
   | pobreza extrema | `extrema` |
   | gasto en alimentos, peso de los alimentos, exposición a la inflación de alimentos | `alimentos` (solo cortes de hogar) |

3. Desde `tarea_4/`, corre:

   ```bash
   uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --corte area --indicador pobreza --anio 2024
   ```

4. El script imprime las cifras, el peso usado y el tamaño de muestra, y guarda `figuras/<indicador>_<corte>_2024.png`
   con un `.csv` al lado. **Reporta las cifras que imprimió, sin recalcularlas**, y menciona la ruta de la figura.

5. Si piden un corte que no está en la tabla, lee `.claude/skills/limpiando-enaho/reference.md` para ver qué
   variables existen antes de proponer nada.

## Reglas que el script ya aplica

- Pondera siempre; nunca cuenta filas ni promedia la columna `pobreza`.
- **Título analítico calculado con las cifras** (qué grupo está más alto y por cuántos puntos), subtítulo con
  indicador, periodo y unidad, y pie con fuente, base de ponderación y tamaño de muestra.
- Barras **desde cero**, de un solo color (azul `#2a78d6`), ordenadas de mayor a menor en `area`, `departamento` y
  `sexo`; `edad` y `tipo_hogar` van en su orden natural, `edad` con una rampa ordinal azul.
- `tipo_hogar_area`: dos series (urbano azul, rural naranja) con leyenda sobre el gráfico y valor en cada barra.
- Línea de referencia con el valor de Perú; las etiquetas tienen fondo para que la línea no las tape.
- Paleta validada con el script de la skill `dataviz`. PNG a 200 dpi en `figuras/`.

## Lo que no hace

No tiene intervalos de confianza: la ENAHO es una muestra y las diferencias pequeñas entre grupos (menos de un punto)
pueden no ser significativas. Dilo al interpretar, sobre todo en cortes con pocos hogares (el `n` está en el pie).
