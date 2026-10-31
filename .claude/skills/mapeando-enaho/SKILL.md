---
name: mapeando-enaho
description: Hace un mapa coroplético de la pobreza monetaria de la ENAHO por departamento del Perú, uniendo la base limpia con los límites departamentales por código de ubigeo. Úsala cuando pidan un mapa, un coropleta o visualizar la pobreza del INEI por departamento, región o territorio.
argument-hint: [año]
---

# Mapear la ENAHO

1. **Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`.**
   Sin base limpia no hay mapa.

2. Corre exactamente:

   ```bash
   uv run ${CLAUDE_SKILL_DIR}/scripts/mapear.py --anio 2024
   ```

   Cambia `2024` solo si el usuario pidió otro año y `$0` es un **número de cuatro
   dígitos**. `$0` trae el texto libre del pedido, no un año: nunca lo pases tal cual.

3. El script imprime las cifras y guarda `mapas/pobreza_departamento.png`.
   Reporta las cifras que imprimió y menciona la ruta del mapa.

4. Si el script se detiene porque hay departamentos sin dato, **no rellenes a mano
   ni unas por nombre**: el problema está en la limpieza o en el código de ubigeo.
   Vuelve a `limpiando-enaho`.

## Reglas que el script ya aplica

- Une **por código**: `ubigeo[:2]` de la base contra `FIRST_IDDP` del GeoJSON, los dos
  como texto de dos dígitos. **Nunca por nombre**: «APURIMAC» no es «Apurímac».
- Exige **25 departamentos y ninguno sin dato**; si falta uno, se detiene.
- Escala de **un solo color de claro a oscuro** (`Oranges`), **desde 0**. Nunca arcoíris.
- Leyenda con la unidad: **«Pobreza monetaria (% de personas)»**.
- **Lima (15) y Callao (07) van separados**, como polígonos distintos.
- Pondera con **`facpob07`**.
- PNG a **200 dpi** en `mapas/`.

## Los límites departamentales

El script busca `datos/peru_departamental_simple.geojson` y, si no está, lo descarga de:

```
https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson
```

Lo guarda en `datos/` para que la segunda corrida no necesite internet.

## Cifras de control, ENAHO 2024

| Departamento | Pobreza |
|---|---|
| Cajamarca | 45.0 % |
| Loreto | 43.0 % |
| Puno | 39.9 % |
| Moquegua | 11.0 % |
| Ica | 6.0 % |

La tabla completa de los 25 departamentos está en
`referencias/pobreza_departamento_2024.csv`; el script compara contra ella y reporta
la diferencia máxima.
