---
name: graficando-enaho
description: Hace gráficos de barras de la pobreza monetaria de la ENAHO por área urbana o rural, sexo, grupo de edad o departamento, ponderando con el factor de expansión. Úsala cuando pidan graficar, comparar o visualizar la pobreza de la ENAHO del INEI.
argument-hint: [area|sexo|edad|departamento]
---

# Graficar la ENAHO

1. **Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`.**
   Sin base limpia no hay gráfico.

2. Corre exactamente:

   ```bash
   uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --corte area --anio 2024
   ```

   Cortes válidos: `area` (urbano/rural), `sexo`, `edad`, `departamento`.
   Reemplaza `area` por el corte que pidió el usuario **solo si es uno de esos cuatro
   valores exactos**. `$0` trae el texto libre del pedido, no un corte: nunca lo pases
   tal cual al script.

3. El script imprime las cifras y guarda el PNG. Reporta las cifras que imprimió,
   no las recalcules, y menciona la ruta de la figura.

4. Si el usuario pide un corte que no está en la lista, lee
   `.claude/skills/limpiando-enaho/reference.md` para ver qué variables existen
   antes de proponer nada.

## Reglas que el script ya aplica

- Pondera siempre con **`facpob07`**. Nunca cuenta filas ni promedia la columna `pobreza`.
- Barras **desde cero**, ordenadas de mayor a menor. La excepción es `edad`, que va en
  orden de grupo etario porque es una escala ordinal y reordenarla haría ilegible el gráfico.
- **Un solo color** (`#b1491f`) y el valor escrito al final de cada barra.
- El título dice **qué y cuándo**: «Pobreza monetaria según área de residencia, 2024».
- Nota al pie: **«Fuente: INEI, ENAHO 2024»**.
- PNG a **200 dpi** en `figuras/`.

## Cifras de control, ENAHO 2024

Hay **dos bases** y dan cifras ligeramente distintas. Este script usa la de personas.

| Corte | Con personas y `facpob07` (lo que hace este script) | Con la sumaria y `factor07 × mieperho` (la cifra que publica el INEI) |
|---|---|---|
| Urbano | **24.7 %** | 24.8 % |
| Rural | **39.4 %** | 39.3 % |
| Nacional | **27.53 %** | 27.58 % |

La diferencia de una décima es normal y **no es un error**: la sumaria pondera hogares
por su tamaño y la base de personas pondera personas. Si el gráfico de área da 24.7 % y
39.4 %, está correcto.

Preocúpate solo si la diferencia pasa de medio punto; ahí sí vuelve a `limpiando-enaho`
y revisa `salidas/validacion.txt`.
