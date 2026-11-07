---
name: mapeando-enaho
description: Hace un mapa coroplético por departamento del Perú con la ENAHO 2024 del INEI - pobreza monetaria, pobreza en hogares con adultos mayores (65+) o porcentaje de personas que viven con adultos mayores - uniendo la base limpia con los límites departamentales por código de ubigeo. Úsala cuando pidan un mapa, un coropleta o visualizar la pobreza del INEI por departamento, región o territorio. Si no existe la base procesada, usa antes limpiando-enaho. Versión de la tarea 4.
argument-hint: [pobreza|pobreza_hogares_am|personas_en_hogares_am]
---

# Mapear la ENAHO · versión tarea_4

> **Cuál versión es esta.** Hay otra `mapeando-enaho` en la raíz del repo (sesión 16) que pondera con `facpob07`.
> Esta pondera con **`factor07 × mieperho`** (base hogar), que es la base con la que se hizo la tabla de referencia
> de la sesión 16 y la que publica el INEI. Para usar esta versión se arranca `claude` dentro de `tarea_4/`.

1. **Si no existe `salidas/hogares_2024.parquet`, usa primero la skill `limpiando-enaho`** y espera a que termine
   sin error. Sin base validada no hay mapa. El script también lo detecta: termina con código 3 y dice qué correr.

2. Elige el indicador. **Solo estos valores exactos**; `$0` trae texto libre, nunca lo pases tal cual al script.

   | Si piden… | `--indicador` |
   |---|---|
   | pobreza monetaria por departamento (por defecto) | `pobreza` |
   | pobreza de los hogares con adultos mayores | `pobreza_hogares_am` |
   | dónde viven más personas con adultos mayores en su hogar | `personas_en_hogares_am` |

3. Desde `tarea_4/`, corre:

   ```bash
   uv run ${CLAUDE_SKILL_DIR}/scripts/mapear.py --indicador pobreza --anio 2024
   ```

4. El script imprime los extremos, la comparación con la referencia y avisos de muestra chica, y guarda
   `mapas/<indicador>_departamento_2024.png` con un `.csv` al lado. **Reporta las cifras que imprimió** y la ruta.

5. Si el script se detiene (código 2) porque faltan departamentos o porque la pobreza se aleja de la referencia,
   **no rellenes a mano ni unas por nombre**: el problema está en la limpieza o en el código de ubigeo. Vuelve a
   `limpiando-enaho` y reporta el error.

## Reglas que el script ya aplica

- Une **por código**: `ubigeo[:2]` de la base contra `FIRST_IDDP` del GeoJSON, ambos como texto de dos dígitos, con
  `validate="1:1"`. **Nunca por nombre**: «APURIMAC» no es «Apurímac». Los nombres con tilde solo rotulan.
- Exige **25 unidades territoriales, todas con dato**, con **Lima (15) y Callao (07) separados**.
- Con `pobreza`, compara contra `referencias/pobreza_departamento_2024.csv` (sesión 16) y se detiene si algún
  departamento difiere en más de 0.1 puntos.
- Escala **secuencial azul de claro a oscuro, desde 0** (rampa de la skill `dataviz`), nunca arcoíris; leyenda con
  la unidad, «(% de personas)».
- Título analítico con el mínimo y el máximo; rótulos solo en esos dos departamentos.
- Avisa en el pie si algún departamento tiene menos de 100 hogares en la muestra.
- PNG a 200 dpi en `mapas/`.

## Los límites departamentales

El script busca `datos/peru_departamental_simple.geojson` y, si no está, lo descarga de:

```
https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson
```

y lo guarda en `datos/` para que la segunda corrida no necesite internet.
