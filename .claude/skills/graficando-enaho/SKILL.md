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
   uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --corte $0 --anio 2024
   ```

   Cortes: `area` (urbano/rural), `sexo`, `edad`, `departamento`. Si no se pasó corte, usa `area`.

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

| Corte | Valor |
|---|---|
| Urbano | 24.8 % |
| Rural | 39.3 % |
| Nacional | 27.6 % |

Si el gráfico de área no da 24.8 % y 39.3 %, la base está mal limpiada: vuelve a
`limpiando-enaho` y revisa `salidas/validacion.txt`.
