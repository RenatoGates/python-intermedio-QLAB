# Evaluación de las skills · tres pedidos con y sin skills

Fecha de la corrida: **31 de octubre de 2026** · Claude Code 2.1.296 · modelo `claude-opus-5-5` ·
Windows 11 · Python 3.14, pandas 3.1.0, geopandas 1.2.0, matplotlib 3.11.2.

## Cómo se corrió

Cada pedido se corrió desde la raíz del repo, con skills y sin skills, en dos rondas.

**Ronda A: los comandos tal como estaban planeados.** Hubo que corregir uno. En
`claude -p --disallowedTools Skill "<pedido>"`, la opción `--disallowedTools` acepta varios
valores y toma cada palabra del pedido como el nombre de una herramienta a bloquear (`«¿Cuál»`,
`«fue»`, `«la»`…). Claude termina sin prompt y sale con
`Error: Input must be provided either through stdin or as a prompt argument`. El error original
está en `evaluacion/ronda_a/*_sintaxis_original.err`. La forma que funciona pone el pedido antes
de la opción.

**Ronda B: con permiso para correr `uv run`.** En modo `-p` nadie puede aprobar comandos. En la
ronda A las skills se activaron, pero ningún script llegó a correr, así que no hubo cifra
calculada ni figura. La ronda B repite los seis comandos dándole permiso solo a `uv run` y a la
edición de archivos.

```bash
# Ronda A
claude -p "<pedido>"
claude -p "<pedido>" --disallowedTools Skill

# Ronda B
claude -p "<pedido>" --permission-mode acceptEdits --allowedTools "Bash(uv run:*)" "PowerShell(uv run:*)"
claude -p "<pedido>" --disallowedTools Skill --permission-mode acceptEdits --allowedTools "Bash(uv run:*)" "PowerShell(uv run:*)"
```

- **Antes de cada corrida se borró `salidas/personas_2024.parquet`.** Ese archivo no se versiona,
  así que cada corrida parte del estado de un clon recién bajado. Por eso las skills de gráfico y
  de mapa tienen que encadenar con `limpiando-enaho`, y la corrida sin skills no puede aprovechar
  una base ya limpia.
- **Qué skills se activaron sale del transcript de cada sesión, no del texto de la respuesta.**
  Cada llamada a una herramienta está en `*.traza.txt`.
- **Los archivos de cada corrida están en `evaluacion/ronda_a/` y `evaluacion/ronda_b/`.** Para
  cada pedido hay una respuesta (`<pedido>_<con|sin>_skills.txt`), un registro de errores
  (`.err`) y la traza (`.traza.txt`).

> **Ojo con «sin skills».** `--disallowedTools Skill` quita la herramienta que carga las
> skills, pero `.claude/skills/` sigue en el repo. En **las seis** corridas sin skills Claude
> buscó en el repo, leyó los `SKILL.md` como archivos comunes (en los pedidos 2 y 3, también los
> scripts) y siguió las mismas instrucciones. Esta comparación mide si la skill se activa sola, no qué hace Claude sin
> conocer el procedimiento. Además, el README y `referencias/` ya traen las respuestas esperadas,
> como el 18.5 % de Cusco.

---

## Pedido 1 · «¿Cuál fue la pobreza en Cusco en 2024?»

**Esperado:** 18.5 % (tabla del INEI en `referencias/pobreza_departamento_2024.csv`).

| | A · con skills | A · sin skills | B · con skills | B · sin skills |
|---|---|---|---|---|
| Skills que se activaron | `limpiando-enaho` | ninguna; leyó su `SKILL.md` a mano | `limpiando-enaho` | ninguna; leyó su `SKILL.md` a mano |
| ¿Corrió los scripts? | No: `uv run` denegado 3 veces | No: denegado | Sí: `limpiar.py` y un cálculo sobre el parquet | Sí: `limpiar.py` y un script propio |
| Cifra que dio | 18.5 %, copiada del CSV del INEI (lo dijo) | 18.5 %, copiada del CSV del INEI (lo dijo) | **18.54 %** | **18.54 %** |
| ¿Ponderó con `facpob07`? | No calculó | No calculó | Sí | Sí |
| ¿Filtró residentes habituales? | No calculó | No calculó | Sí, usó el parquet de `limpiar.py` (108,664 personas) | Sí, el mismo parquet |
| Llamadas a herramientas · tiempo | 9 · 36 s | 9 · 23 s | 5 · 27 s | 9 · 50 s |

**Qué pasó.** En la ronda B las dos versiones calcularon con los microdatos y llegaron al mismo
número. También reportaron 2.15 % de pobreza extrema, unos 256 mil pobres y que la cifra sale de
3,777 personas encuestadas, con la advertencia de usarla junto al intervalo de confianza del
INEI. En la ronda A ninguna inventó una cifra: las dos aclararon que el 18.5 % era el oficial y
que no lo habían calculado.

**Error de la skill:** Claude la llamó con `args: "Calcular la pobreza monetaria de Cusco en 2024"`,
y `$0` tomó la primera palabra. El cuerpo quedó como `--anio Calcular` y
`salidas/personas_Calcular.parquet`. En las dos rondas el modelo lo notó y corrió `--anio 2024`
por su cuenta.

---

## Pedido 2 · «Grafica la pobreza urbana y rural»

**Esperado:** 24.7 % urbano y 39.4 % rural con la base de personas (`facpob07`), que es lo que
grafica el script. El INEI publica 24.8 % y 39.3 %, calculados con la sumaria
(`factor07 × mieperho`). Ver [Problemas encontrados](#problemas-encontrados).

| | A · con skills | A · sin skills | B · con skills | B · sin skills |
|---|---|---|---|---|
| Skills que se activaron | `graficando-enaho` → `limpiando-enaho` | ninguna; leyó los dos `SKILL.md` a mano | `graficando-enaho` → `limpiando-enaho` | ninguna; leyó los dos `SKILL.md` a mano |
| ¿Corrió los scripts? | No: denegado | No: probó `uv run` y `.venv\Scripts\python.exe`, ambos denegados | Sí: `limpiar.py` y `graficar.py --corte area` | Sí: `limpiar.py` y `graficar.py --corte area` |
| Cifras que dio | 24.7 / 39.4, leídas de `validacion.txt` y de la figura anterior | 24.7 / 39.4, leídas de `validacion.txt` y de la figura anterior | **24.7 / 39.4** | **24.7 / 39.4** |
| ¿Ponderó con `facpob07`? | No calculó | No calculó | Sí | Sí |
| Cómo se ve la figura | No la generó | No la generó | Ver abajo | La misma, porque corrió el mismo script |
| Llamadas · tiempo | 9 · 46 s | 16 · 68 s | 10 · 49 s | 14 · 73 s |

**La figura** (`figuras/pobreza_area_2024.png`) es de barras horizontales que parten de 0, en un
solo color (`#b1491f`). Rural va arriba, ordenado de mayor a menor, y cada barra lleva su valor
al final. El título es «Pobreza monetaria según área de residencia, 2024», el eje dice
«% de personas», la nota al pie dice «Fuente: INEI, ENAHO 2024» y la imagen está a 200 dpi.

**Qué pasó.** En las cuatro corridas Claude dijo que 24.7 / 39.4 «no pasa el control» de la
skill, que espera 24.8 / 39.3. En la ronda A, sin poder correr nada, sospechó de la limpieza
(con skills) o del método de ponderación (sin skills). En la ronda B, con y sin skills, rehízo el cálculo con la sumaria, obtuvo 24.8 / 39.3 y concluyó que la base estaba
bien y que la tabla de control usa otro método.

**Error de la skill:** en la ronda B llegaron `args` con texto libre a las dos skills. Eso armó
`--corte Grafica` y `--anio Arma`. Claude usó los valores por defecto (`area`, `2024`).

---

## Pedido 3 · «Haz un mapa de la pobreza por departamento»

**Esperado:** Cajamarca 45.0 %, Ica 5.9 % y los 25 departamentos con dato, ponderando con
`facpob07`. La tabla del INEI da Ica 6.0 %.

| | A · con skills | A · sin skills | B · con skills | B · sin skills |
|---|---|---|---|---|
| Skills que se activaron | `mapeando-enaho` → `limpiando-enaho` | ninguna; leyó los dos `SKILL.md` a mano | `mapeando-enaho` → `limpiando-enaho` | ninguna; leyó los dos `SKILL.md` a mano |
| ¿Corrió los scripts? | No: denegado | No: denegado | Sí: `limpiar.py` y `mapear.py` | Sí: `limpiar.py` y `mapear.py` |
| Cifras que dio | Las de `validacion.txt` anterior | Las de `validacion.txt` anterior | **Cajamarca 45.0 %, Loreto 42.6 %, Puno 40.4 %; Ica 5.9 %, Moquegua 10.9 %, Madre de Dios 11.1 %** | Las mismas |
| ¿Unió por código o por nombre? | No corrió | No corrió | Por código: `ubigeo[:2]` contra `FIRST_IDDP` | Por código (lo dijo) |
| Departamentos sin dato | No corrió | No corrió | Ninguno, 25 de 25 | Ninguno, 25 de 25 |
| Diferencia con la tabla del INEI | — | — | Máxima 0.5 puntos (Puno), mediana 0.1 | La misma |
| Llamadas · tiempo | 9 · 38 s | 15 · 58 s | 7 · 33 s | 11 · 61 s |

**El mapa** (`mapas/pobreza_departamento.png`) es un coroplético en una sola escala (`Oranges`)
que va de claro a oscuro y empieza en 0, con la leyenda «Pobreza monetaria (% de personas)». El
título es «Pobreza monetaria por departamento, 2024», y la nota al pie dice «Fuente: INEI,
ENAHO 2024. Ponderado con facpob07. Lima (15) y Callao (07) van separados.» Cajamarca y Loreto
son los más oscuros, e Ica el más claro. Callao casi no se ve por su tamaño.

---

## El pedido que activó dos skills seguidas

**Dos pedidos lo hicieron, en las dos rondas:**

1. «Grafica la pobreza urbana y rural»: `graficando-enaho` → `limpiando-enaho`.
2. «Haz un mapa de la pobreza por departamento»: `mapeando-enaho` → `limpiando-enaho`.

En los dos casos el orden fue el mismo. Primero se cargó la skill que pide el resultado. Esa
skill buscó `salidas/personas_2024.parquet`, Glob devolvió `No files found`, y entonces se cargó
`limpiando-enaho`. Así se ve en las trazas
(`evaluacion/ronda_b/2_area_con_skills.traza.txt` y `3_mapa_con_skills.traza.txt`):

```
> Skill: {"skill": "graficando-enaho", ...}
> Glob: {"pattern": "salidas/personas_2024.parquet"}
  < 'No files found'
> Skill: {"skill": "limpiando-enaho", ...}
```

El encadenamiento viene del paso 1 de `graficando-enaho` y de `mapeando-enaho`: «Si no existe
`salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`». El pedido de Cusco
activó una sola skill.

## Descriptions

**No se cambió ninguna.** Las tres skills se activaron solas al primer intento en las seis
corridas con skills.

---

## Problemas encontrados

No se corrigieron, porque los dos primeros piden tocar el cuerpo de las skills y no su
description.

1. **`$0` recibe texto libre.** Claude llama a las skills con el pedido como argumento, y `$0` se
   queda con la primera palabra. Así salieron `--anio Calcular` (pedido 1, en las dos rondas),
   `--corte Grafica` y `--anio Arma` (pedido 2, ronda B). El modelo se recuperó siempre, pero por criterio propio. Una solución es que el
   cuerpo diga: «si `$0` no es un año de cuatro dígitos, usa 2024» (y lo equivalente para el
   corte).
2. **La tabla de control de `graficando-enaho` contradice a su propio script.** Pide 24.8 / 39.3,
   pero el script pondera con `facpob07` y da 24.7 / 39.4. Lo verificamos sobre la misma base:
   la sumaria con `factor07 × mieperho` da **24.807 / 39.303** y la base de personas con
   `facpob07` da **24.74 / 39.44**. La limpieza está bien. El problema es que la tabla mezcla
   métodos, y la frase «si no da 24.8 y 39.3, la base está mal limpiada» hizo que el modelo dudara
   de una salida correcta en las cuatro corridas. Conviene poner las dos cifras, como ya hace
   `limpiando-enaho` con el total nacional (27.58 / 27.53). La misma mezcla aparece en la tabla de
   `limpiando-enaho` (urbano/rural) y en la sección 4 del README.
3. **La tabla de `mapeando-enaho` también trae cifras del INEI** (Loreto 43.0, Puno 39.9, Ica 6.0,
   Moquegua 11.0). Con `facpob07` salen 42.6, 40.4, 5.9 y 10.9. El script lo reporta (diferencia
   máxima de 0.5) y no se detiene, así que no causó errores, pero tiene el mismo origen que el
   punto 2.

---

## Conclusión

- **Con skills y permiso para `uv run` (ronda B),** los tres pedidos dieron cifras correctas,
  ponderadas con `facpob07` y solo con residentes habituales. La figura y el mapa cumplen las
  reglas de las skills. Tardaron 27, 49 y 33 s, y el encadenamiento con `limpiando-enaho`
  funcionó solo.
- **Sin la herramienta Skill** las cifras fueron las mismas, porque Claude leyó las skills como
  archivos. Lo que cambió fue el camino: exploró el repo antes de actuar y tardó más (50, 73 y
  61 s, con 9 a 14 llamadas en vez de 5 a 10). En este repo lo que hace correcta la respuesta es
  el procedimiento escrito en `.claude/skills/`, más que la activación automática.
- **Con `claude -p` sin permisos (ronda A),** las skills se activaron y encadenaron, pero no se
  calculó nada. Claude no inventó cifras: dijo de dónde salía cada número y qué no había podido
  comprobar.
- **Pendiente:** para medir qué hace Claude sin las skills de verdad, habría que correr los tres
  pedidos en un clon sin `.claude/skills/` y sin las cifras esperadas en el README y en
  `referencias/`.
