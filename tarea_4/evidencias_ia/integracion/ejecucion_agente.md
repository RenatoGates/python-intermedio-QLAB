# Parte 3 · Ejecución del agente de investigación

Una sola sesión de `claude -p --model opus` arrancada en `tarea_4/`, con el servidor `bcrp` de `.mcp.json`, las skills de `tarea_4/.claude/skills/` y las herramientas Skill, Bash, Read, Write, Edit, Glob, Grep, ListMcpResourcesTool, ReadMcpResourceTool. Antes se borraron las bases procesadas de `salidas/`. Generado por `ejecutar_agente.py`; el pedido completo está en `pedido_agente.md`.

## Pedido

```text
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
   `informes/calculos_exposicion.py` y que lea 
… (recortado)
```

**Modelo:** claude-opus-5-5  
**Directorio:** `~\Documentos\GitHub\python-intermedio-QLAB\tarea_4`  
**Servidores MCP:** bcrp (connected), fetch (connected)  
**Herramientas:** Bash, Edit, Glob, Grep, ListMcpResourcesTool, Read, ReadMcpResourceTool, Skill, Write, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__graficar_series, mcp__bcrp__resumen, mcp__bcrp__serie, mcp__fetch__fetch

### Claude

**Plan**
1. Con el MCP `bcrp`: ubico con `buscar_series` la inflación de alimentos y bebidas de Lima, la inflación total a 12 meses y la tasa de referencia, y leo sus fichas si hay dudas.
2. Saco `resumen` de cada serie desde 2021-01 hasta el último mes de 2026, `correlacion` sin rezago y con rezago 6, y el gráfico `bcrp_inflacion_tasa_2021_2026`. Reviso la ficha de PD04722MM frente a sus datos desde 2003.
3. Cargo y sigo cada SKILL.md: `limpiando-enaho`, que valida y genera `salidas/indicadores.csv` (si falla, me detengo); `graficando-enaho`, con alimentos y pobreza por tipo_hogar_area; y `mapeando-enaho`, con pobreza_hogares_am.
4. Leo `salidas/indicadores.csv` y `salidas/validacion.txt`: cortes por tipo de hogar, por tipo × área y por tipo × tamaño, con `n_muestral`, para marcar las celdas con menos de 100 hogares.
5. Escribo y corro `informes/calculos_exposicion.py`, que lee el CSV de la ENAHO y el de `figuras/` y calcula part_alimentos × inflación de alimentos / 100 por tipo de hogar y área.
6. Redacto `informes/informe_final.md` con la estructura pedida y cito código y periodo en cada cifra del BCRP, y base y ponderador en cada cifra de la ENAHO, en lenguaje de asociación y no de causalidad.

### → Llama a `mcp__bcrp__buscar_series`

```json
{
 "texto": "alimentos y bebidas 12 meses",
 "frecuencia": "Mensual"
}
```

#### ← Resultado

```text
{"result":[{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN09823PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC sin Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN09824PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Subyacente Sin Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01285PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC No Transables Sin Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"}]}
```

### → Llama a `mcp__bcrp__buscar_series`

```json
{
 "texto": "ipc 12 meses",
 "frecuencia": "Mensual"
}
```

#### ← Resultado

```text
{"result":[{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1950","actualizada":"2026-10-08"},{"codigo":"PN09821PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Importado","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1992","actualizada":"2026-10-08"},{"codigo":"PN01279PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Subyacente","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01281PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Transables","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01283PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC No Transables","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN09820PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC No Subyacente","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1992","actualizada":"2026-10-08"},{"codigo":"PN09830PM","nombre":"Inflación de socios comerciales - IPC Externo Multilateral (var% 12 meses)","categoria":"Tipo de cambio real","frecuencia":"Mensual","inicio":"Ene-1996","actualizada":"2026-10-08"},{"codigo":"PN09819PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Energía","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1992","actualizada":"2026-10-08"},{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01277PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Sin Alimentos y Energía","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"}]}
```

### → Llama a `mcp__bcrp__buscar_series`

```json
{
 "texto": "tasa de referencia",
 "frecuencia": "Mensual"
}
```

#### ← Resultado

```text
{"result":[{"codigo":"PD04722MM","nombre":"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria","categoria":"Tasas de interés","frecuencia":"Mensual","inicio":"Ene-2004","actualizada":"2026-10-15"},{"codigo":"PN07809NM","nombre":"Tasas de interés activas y pasivas promedio de las empresas bancarias en MN (términos efectivos anuales) - Activas - Preferencial Corporativa a 90 días","categoria":"Tasas de interés","frecuencia":"Mensual","inicio":"Ene-2011","actualizada":"2026-10-23"},{"codigo":"PN07829NM","nombre":"Tasas de interés activas y pasivas promedio de las empresas bancarias en ME (términos efectivos anuales) - Activas - Preferencial Corporativa a 90 días","categoria":"Tasas de interés","frecuencia":"Mensual","inicio":"Ene-2011","actualizada":"2026-10-23"}]}
```

### → Llama a `ReadMcpResourceTool`

```json
{
 "server": "bcrp",
 "uri": "bcrp://serie/PD04722MM"
}
```

#### ← Resultado

```text
{"contents":[{"uri":"bcrp://serie/PD04722MM","mimeType":"application/json","text":"{\n \"codigo\": \"PD04722MM\",\n \"nombre\": \"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria\",\n \"categoria\": \"Tasas de interés\",\n \"frecuencia\": \"Mensual\",\n \"inicio\": \"Ene-2004\",\n \"actualizada\": \"2026-10-15\",\n \"grupo\": \"Tasas de interés del Banco Central de Reserva\",\n \"origen_de_los_datos\": \"BCRP\",\n \"area_que_publica\": \"Departamento de Estadísticas Monetarias\",\n \"web\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PD04722MM/html\",\n \"api\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/{desde}/{hasta}\",\n \"catalogo\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata\"\n}"}]}
```

### → Llama a `ReadMcpResourceTool`

```json
{
 "server": "bcrp",
 "uri": "bcrp://serie/PN09822PM"
}
```

#### ← Resultado

```text
{"contents":[{"uri":"bcrp://serie/PN09822PM","mimeType":"application/json","text":"{\n \"codigo\": \"PN09822PM\",\n \"nombre\": \"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas\",\n \"categoria\": \"Inflación\",\n \"frecuencia\": \"Mensual\",\n \"inicio\": \"Ene-1993\",\n \"actualizada\": \"2026-10-08\",\n \"grupo\": \"Índice de precios Lima Metropolitana (var% 12 meses)\",\n \"origen_de_los_datos\": \"INEI\",\n \"area_que_publica\": \"Departamento de Estadísticas de Precios\",\n \"web\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN09822PM/html\",\n \"api\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/{desde}/{hasta}\",\n \"catalogo\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata\"\n}"}]}
```

### → Llama a `ReadMcpResourceTool`

```json
{
 "server": "bcrp",
 "uri": "bcrp://serie/PN01273PM"
}
```

#### ← Resultado

```text
{"contents":[{"uri":"bcrp://serie/PN01273PM","mimeType":"application/json","text":"{\n \"codigo\": \"PN01273PM\",\n \"nombre\": \"Índice de precios Lima Metropolitana (var% 12 meses) - IPC\",\n \"categoria\": \"Inflación\",\n \"frecuencia\": \"Mensual\",\n \"inicio\": \"Ene-1950\",\n \"actualizada\": \"2026-10-08\",\n \"grupo\": \"Índice de precios Lima Metropolitana (var% 12 meses)\",\n \"origen_de_los_datos\": \"INEI\",\n \"area_que_publica\": \"Departamento de Estadísticas de Precios\",\n \"web\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN01273PM/html\",\n \"api\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/{desde}/{hasta}\",\n \"catalogo\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata\"\n}"}]}
```

### → Llama a `mcp__bcrp__resumen`

```json
{
 "codigo": "PN09822PM",
 "desde": "2021-01",
 "hasta": "2026-12"
}
```

#### ← Resultado

```text
{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","frecuencia":"Mensual","desde":"2021-01","hasta":"2026-12","n":70,"primero":{"periodo":"2021-01","valor":3.6479},"ultimo":{"periodo":"2026-10","valor":5.2841},"cambio":1.6362,"variacion_pct":44.8535,"promedio":5.5041,"maximo":{"periodo":"2023-02","valor":13.1637},"minimo":{"periodo":"2025-03","valor":0.5904},"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-12","web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN09822PM/html","nota":"La serie ya está en %: «cambio» está en puntos porcentuales."}
```

### → Llama a `mcp__bcrp__resumen`

```json
{
 "codigo": "PN01273PM",
 "desde": "2021-01",
 "hasta": "2026-12"
}
```

#### ← Resultado

```text
{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","frecuencia":"Mensual","desde":"2021-01","hasta":"2026-12","n":70,"primero":{"periodo":"2021-01","valor":2.6755},"ultimo":{"periodo":"2026-10","valor":5.251},"cambio":2.5755,"variacion_pct":96.2593,"promedio":4.3147,"maximo":{"periodo":"2022-06","valor":8.8126},"minimo":{"periodo":"2025-08","valor":1.1063},"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2021-1/2026-12","web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN01273PM/html","nota":"La serie ya está en %: «cambio» está en puntos porcentuales."}
```

### → Llama a `mcp__bcrp__resumen`

```json
{
 "codigo": "PD04722MM",
 "desde": "2021-01",
 "hasta": "2026-12"
}
```

#### ← Resultado

```text
{"codigo":"PD04722MM","nombre":"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria","frecuencia":"Mensual","desde":"2021-01","hasta":"2026-12","n":70,"primero":{"periodo":"2021-01","valor":0.25},"ultimo":{"periodo":"2026-10","valor":4.25},"cambio":4,"variacion_pct":1600,"promedio":4.7286,"maximo":{"periodo":"2023-01","valor":7.75},"minimo":{"periodo":"2021-01","valor":0.25},"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2021-1/2026-12","web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PD04722MM/html","nota":"La serie ya está en %: «cambio» está en puntos porcentuales."}
```

### → Llama a `mcp__bcrp__correlacion`

```json
{
 "codigo_a": "PN09822PM",
 "codigo_b": "PN01273PM",
 "desde": "2021-01",
 "hasta": "2026-10"
}
```

#### ← Resultado

```text
{"serie_a":{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","n_datos":70,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10"},"serie_b":{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","n_datos":70,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2021-1/2026-10"},"frecuencia":"Mensual","desde":"2021-01","hasta":"2026-10","rezago":0,"periodo_comun":{"primero":"2021-01","ultimo":"2026-10"},"n_pares":70,"r":0.9719,"fuerza":"fuerte y positiva","brecha_media":1.1894,"periodos_a_mayor_que_b":48,"advertencia":"Correlación descriptiva entre dos series agregadas: no demuestra causalidad.","fuentes":["https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10","https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2021-1/2026-10"]}
```

### → Llama a `mcp__bcrp__correlacion`

```json
{
 "codigo_a": "PN09822PM",
 "codigo_b": "PN01273PM",
 "desde": "2021-01",
 "hasta": "2026-10",
 "rezago": 6
}
```

#### ← Resultado

```text
{"serie_a":{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","n_datos":70,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10"},"serie_b":{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","n_datos":70,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2021-1/2026-10"},"frecuencia":"Mensual","desde":"2021-01","hasta":"2026-10","rezago":6,"periodo_comun":{"primero":"2021-01","ultimo":"2026-04"},"n_pares":64,"r":0.648,"fuerza":"moderada y positiva","brecha_media":1.1784,"periodos_a_mayor_que_b":32,"advertencia":"Correlación descriptiva entre dos series agregadas: no demuestra causalidad.","fuentes":["https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10","https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2021-1/2026-10"]}
```

### → Llama a `mcp__bcrp__correlacion`

```json
{
 "codigo_a": "PN09822PM",
 "codigo_b": "PD04722MM",
 "desde": "2021-01",
 "hasta": "2026-10"
}
```

#### ← Resultado

```text
{"serie_a":{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","n_datos":70,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10"},"serie_b":{"codigo":"PD04722MM","nombre":"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria","n_datos":70,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2021-1/2026-10"},"frecuencia":"Mensual","desde":"2021-01","hasta":"2026-10","rezago":0,"periodo_comun":{"primero":"2021-01","ultimo":"2026-10"},"n_pares":70,"r":0.4422,"fuerza":"moderada y positiva","brecha_media":0.7755,"periodos_a_mayor_que_b":35,"advertencia":"Correlación descriptiva entre dos series agregadas: no demuestra causalidad.","fuentes":["https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10","https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2021-1/2026-10"]}
```

### → Llama a `mcp__bcrp__correlacion`

```json
{
 "codigo_a": "PN09822PM",
 "codigo_b": "PD04722MM",
 "desde": "2021-01",
 "hasta": "2026-10",
 "rezago": 6
}
```

#### ← Resultado

```text
{"serie_a":{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","n_datos":70,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10"},"serie_b":{"codigo":"PD04722MM","nombre":"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria","n_datos":70,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2021-1/2026-10"},"frecuencia":"Mensual","desde":"2021-01","hasta":"2026-10","rezago":6,"periodo_comun":{"primero":"2021-01","ultimo":"2026-04"},"n_pares":64,"r":0.7611,"fuerza":"fuerte y positiva","brecha_media":0.5028,"periodos_a_mayor_que_b":35,"advertencia":"Correlación descriptiva entre dos series agregadas: no demuestra causalidad.","fuentes":["https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10","https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2021-1/2026-10"]}
```

### → Llama a `mcp__bcrp__graficar_series`

```json
{
 "codigos": [
  "PN09822PM",
  "PN01273PM",
  "PD04722MM"
 ],
 "desde": "2021-01",
 "hasta": "2026-10",
 "nombre_archivo": "bcrp_inflacion_tasa_2021_2026"
}
```

#### ← Resultado

```text
{"png":"figuras/bcrp_inflacion_tasa_2021_2026.png","csv":"figuras/bcrp_inflacion_tasa_2021_2026.csv","series":[{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","n":70,"ultimo":{"periodo":"2026-10","valor":5.2841},"maximo":{"periodo":"2023-02","valor":13.1637}},{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","n":70,"ultimo":{"periodo":"2026-10","valor":5.251},"maximo":{"periodo":"2022-06","valor":8.8126}},{"codigo":"PD04722MM","nombre":"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria","n":70,"ultimo":{"periodo":"2026-10","valor":4.25},"maximo":{"periodo":"2023-01","valor":7.75}}],"fuentes":["https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10","https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2021-1/2026-10","https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2021-1/2026-10"]}
```

### → Llama a `mcp__bcrp__resumen`

```json
{
 "codigo": "PD04722MM",
 "desde": "2003-01",
 "hasta": "2026-10"
}
```

#### ← Resultado

```text
{"codigo":"PD04722MM","nombre":"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria","frecuencia":"Mensual","desde":"2003-01","hasta":"2026-10","n":278,"primero":{"periodo":"2003-09","valor":2.75},"ultimo":{"periodo":"2026-10","valor":4.25},"cambio":1.5,"variacion_pct":54.5455,"promedio":3.804,"maximo":{"periodo":"2023-01","valor":7.75},"minimo":{"periodo":"2020-04","valor":0.25},"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2003-1/2026-10","web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PD04722MM/html","nota":"La serie ya está en %: «cambio» está en puntos porcentuales."}
```

### Claude

The ficha says the series starts in Ene-2004, but the data begins in 2003-09. I'll check the first months directly.

### → Llama a `mcp__bcrp__serie`

```json
{
 "codigo": "PD04722MM",
 "desde": "2003-01",
 "hasta": "2004-02"
}
```

### → Llama a `Glob`

```json
{
 "pattern": ".claude/skills/*/SKILL.md"
}
```

#### ← Resultado

```text
.claude\skills\limpiando-enaho\SKILL.md
.claude\skills\graficando-enaho\SKILL.md
.claude\skills\mapeando-enaho\SKILL.md
```

#### ← Resultado

```text
{"codigo":"PD04722MM","nombre":"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria","frecuencia":"Mensual","desde":"2003-01","hasta":"2004-02","n":6,"datos":[{"periodo":"2003-09","valor":2.75},{"periodo":"2003-10","valor":2.75},{"periodo":"2003-11","valor":2.5},{"periodo":"2003-12","valor":2.5},{"periodo":"2004-01","valor":2.5},{"periodo":"2004-02","valor":2.5}],"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2003-1/2004-2","web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PD04722MM/html"}
```

### → Llama a `Skill`

```json
{
 "skill": "limpiando-enaho"
}
```

#### ← Resultado

```text
Launching skill: limpiando-enaho
```

#### ← Contenido que Claude Code inyecta (p. ej., el SKILL.md al cargar una skill)

```text
Base directory for this skill: ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\limpiando-enaho

# Limpiar la ENAHO · versión tarea_4

> **Cuál versión es esta.** El repo tiene dos juegos de skills con el mismo nombre: los de la sesión 16, en
> `.claude/skills/` de la raíz, y estos, en `tarea_4/.claude/skills/`. Claude Code carga los del directorio desde
> donde arranca, así que **para la tarea 4 se arranca `claude` dentro de `tarea_4/`**, que es también donde está
> `.mcp.json`.
>
> **En qué difieren.** Aquí la cifra oficial sale de la **base hogar ponderada con `factor07 × mieperho`**, que es
> la que publica el INEI y la que pide el issue. La base persona con `facpob07` (la que usan los gráficos y el mapa
> de la sesión 16) queda como cifra secundaria, solo para cortes por atributos de la persona (sexo, edad). Las dos
> son correctas y difieren en una déc
… (recortado)
```

### → Llama a `Bash`

```json
{
 "command": "cd \"~/Documentos/GitHub/python-intermedio-QLAB/tarea_4\" && ls datos/ && uv run ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024; echo \"EXIT=$?\"",
 "description": "Run ENAHO cleaning and validation script",
 "timeout": 600000
}
```

#### ← Resultado

```text
966-Modulo02
966-Modulo34
catalogo_bcrp.csv
peru_departamental_simple.geojson
ENAHO 2024 · validación de la limpieza (versión tarea_4)
Generado por .claude/skills/limpiando-enaho/scripts/limpiar.py. Ninguna cifra está escrita a mano.

Archivos
  sumaria : datos/966-Modulo34/966-Modulo34/sumaria-2024.dta (33,691 hogares)
  miembros: datos/966-Modulo02/966-Modulo02/enaho01-2024-200.dta (117,721 filas)
  otras sumarias en datos/, que no se usan: sumaria-2024-12g.dta

CIFRA OFICIAL · base hogar (sumaria), ponderada con factor07 × mieperho
  [OK]    Pobreza monetaria nacional    27.58 %   referencia  27.6 %   diferencia -0.02 pp (tolerancia ±0.1)
  [OK]    Pobreza urbana                24.81 %   referencia  24.8 %   diferencia +0.01 pp (tolerancia ±0.1)
  [OK]    Pobreza rural                 39.30 %   referencia  39.3 %   diferencia +0.00 pp (tolerancia ±0.1)
  [OK]    Residentes habituales       108,664     referencia 108,664
  [OK]    Unidades territoriales           25     referencia 25 (códigos 01 a 25; Lima 15 y Callao 07 separados)

Integridad de la limpieza (esenciales)
  [OK]    la llave conglome es texto de largo fijo (6 caracteres): conserva los ceros iniciales
  [OK]    la llave vivienda es texto de largo fijo (3 caracteres): conserva los ceros iniciales
  [OK]    la llave hogar es texto de largo fijo (2 caracteres): conserva los ceros iniciales
  [OK]    llaves de hogar únicas en la sumaria
  [OK]    llaves de persona únicas en el módulo 02
  [OK]    la unión m:1 personas-hogares conserva las 108,664 filas, sin perder ni duplicar
  [OK]    todos los hogares de la sumaria tienen residentes en el módulo 02 (0 sin ellos)
  [OK]    factor07 positivo y sin vacíos en todos los hogares
  [OK]    facpob07 positivo y sin vacíos en todos los residentes
  [OK]    los 8 grupos de gasto del INEI suman gashog2d en todos los hogares (diferencia máxima 0.014 soles)

Cifra secundaria · base persona (módulo 02 unido a la sumaria), ponderada con facpob07
  No es la cifra contra la que se valida: pondera personas, no hogares por su tamaño, y por eso
  difiere en una décima. Se usa solo para cortes por atributos de la persona (sexo, edad).
  Pobreza nacional 27.53 % · urbana 24.7 % · rural 39.4 % · extrema 5.50 %

Informativas (no detienen el proceso)
  [OK]    población expandida: 34,482,700 con factor07 × mieperho y 34,147,768 con facpob07 (difieren menos de 1 %)
  [OK]    pobreza extrema base hogar 5.50 % (INEI 5.5 %)
  Sin pondera
… (recortado)
```

### Claude

The validation passed all 15 essential checks. Next, `graficando-enaho`.

### → Llama a `Skill`

```json
{
 "skill": "graficando-enaho"
}
```

#### ← Resultado

```text
Launching skill: graficando-enaho
```

#### ← Contenido que Claude Code inyecta (p. ej., el SKILL.md al cargar una skill)

```text
Base directory for this skill: ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\graficando-enaho

# Graficar la ENAHO · versión tarea_4

> **Cuál versión es esta.** Hay otra `graficando-enaho` en la raíz del repo (sesión 16) que pondera todo con
> `facpob07`. Esta usa la **base hogar con `factor07 × mieperho`**, la de la cifra oficial, para los cortes de hogar,
> y `facpob07` solo para sexo y edad, rotulado en el pie del gráfico. Para usar esta versión se arranca `claude`
> dentro de `tarea_4/`.

1. **Si no existe `salidas/hogares_2024.parquet` (o `salidas/personas_2024.parquet` para sexo y edad), usa primero
   la skill `limpiando-enaho`** y espera a que termine sin error. Sin base validada no hay gráfico. El script
   también lo detecta: termina con código 3 y dice qué correr.

2. Elige el corte y el indicador según el pedido. **Solo estos valores exactos*
… (recortado)
```

### → Llama a `Bash`

```json
{
 "command": "cd \"~/Documentos/GitHub/python-intermedio-QLAB/tarea_4\" && uv run ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills/graficando-enaho/scripts/graficar.py --corte tipo_hogar_area --indicador alimentos --anio 2024; echo \"EXIT=$?\"; uv run ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills/graficando-enaho/scripts/graficar.py --corte tipo_hogar_area --indicador pobreza --anio 2024; echo \"EXIT=$?\"",
 "description": "Graph food share and poverty by household type and area",
 "timeout": 300000
}
```

#### ← Resultado

```text
Participación de los alimentos en el gasto según presencia de adultos mayores (65+) y área, 2024 (% del gasto del hogar)
  Base hogar ponderada con factor07 × mieperho (la de la cifra oficial)
  Sin adultos mayores · Rural: 58.6 % (n = 7,803)
  Sin adultos mayores · Urbano: 44.8 % (n = 15,489)
  Con adultos mayores y menores de 65 · Rural: 58.7 % (n = 1,618)
  Con adultos mayores y menores de 65 · Urbano: 41.0 % (n = 4,312)
  Solo adultos mayores · Rural: 58.1 % (n = 2,239)
  Solo adultos mayores · Urbano: 39.9 % (n = 2,230)
  Perú: 46.6 %

Guardado en figuras/alimentos_tipo_hogar_area_2024.png (200 dpi) y las cifras en figuras/alimentos_tipo_hogar_area_2024.csv
EXIT=0
Pobreza monetaria según presencia de adultos mayores (65+) y área, 2024 (% de personas)
  Base hogar ponderada con factor07 × mieperho (la de la cifra oficial)
  Sin adultos mayores · Rural: 39.3 % (n = 7,803)
  Sin adultos mayores · Urbano: 25.0 % (n = 15,489)
  Con adultos mayores y menores de 65 · Rural: 43.2 % (n = 1,618)
  Con adultos mayores y menores de 65 · Urbano: 26.1 % (n = 4,312)
  Solo adultos mayores · Rural: 32.8 % (n = 2,239)
  Solo adultos mayores · Urbano: 13.8 % (n = 2,230)
  Perú: 27.6 %

Guardado en figuras/pobreza_tipo_hogar_area_2024.png (200 dpi) y las cifras en figuras/pobreza_tipo_hogar_area_2024.csv
EXIT=0
```

### → Llama a `Skill`

```json
{
 "skill": "mapeando-enaho"
}
```

#### ← Resultado

```text
Launching skill: mapeando-enaho
```

#### ← Contenido que Claude Code inyecta (p. ej., el SKILL.md al cargar una skill)

```text
Base directory for this skill: ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\mapeando-enaho

# Mapear la ENAHO · versión tarea_4

> **Cuál versión es esta.** Hay otra `mapeando-enaho` en la raíz del repo (sesión 16) que pondera con `facpob07`.
> Esta pondera con **`factor07 × mieperho`** (base hogar), que es la base con la que se hizo la tabla de referencia
> de la sesión 16 y la que publica el INEI. Para usar esta versión se arranca `claude` dentro de `tarea_4/`.

1. **Si no existe `salidas/hogares_2024.parquet`, usa primero la skill `limpiando-enaho`** y espera a que termine
   sin error. Sin base validada no hay mapa. El script también lo detecta: termina con código 3 y dice qué correr.

2. Elige el indicador. **Solo estos valores exactos**; `$0` trae texto libre, nunca lo pases tal cual al script.

   | Si piden… | `--indicador` |
   |---|---|
   | po
… (recortado)
```

### → Llama a `Bash`

```json
{
 "command": "cd \"~/Documentos/GitHub/python-intermedio-QLAB/tarea_4\" && uv run ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza_hogares_am --anio 2024; echo \"EXIT=$?\"",
 "description": "Map poverty in households with older adults by department",
 "timeout": 300000
}
```

#### ← Resultado

```text
Pobreza monetaria en hogares con adultos mayores (65+) por departamento, 2024 (base hogar, factor07 × mieperho)
  25 unidades territoriales unidas por código, ninguna sin dato
  más alto : Cajamarca 49.4 %, Loreto 43.8 %, Puno 43.1 %
  más bajo : Ica 2.8 %, Madre de Dios 3.8 %, Arequipa 13.5 %

Guardado en mapas/pobreza_hogares_am_departamento_2024.png (200 dpi) y las cifras en mapas/pobreza_hogares_am_departamento_2024.csv
EXIT=0
```

### → Llama a `Bash`

```json
{
 "command": "cd \"~/Documentos/GitHub/python-intermedio-QLAB/tarea_4\" && cat salidas/indicadores.csv | head -5 && echo ---- && cut -d, -f1 salidas/indicadores.csv | sort | uniq -c && echo ---- && cat mapas/pobreza_hogares_am_departamento_2024.csv && echo ---- && head -5 figuras/bcrp_inflacion_tasa_2021_2026.csv && tail -3 figuras/bcrp_inflacion_tasa_2021_2026.csv && echo ---- && cat figuras/alimentos_tipo_hogar_area_2024.csv && ls informes/ 2>/dev/null",
 "description": "Inspect indicators, map and BCRP CSVs"
}
```

#### ← Resultado

```text
indicador,corte,grupo,valor,unidad,ponderador,n_muestral
pobreza,nacional,Perú,27.5795,% de personas,factor07 × mieperho,33691
pobreza_extrema,nacional,Perú,5.5045,% de personas,factor07 × mieperho,33691
pobreza,area,Urbano,24.807,% de personas,factor07 × mieperho,22031
pobreza,area,Rural,39.3028,% de personas,factor07 × mieperho,11660
----
      1 am_vive_solo
      9 gasto_pc_mensual
      3 hogares
      1 hogares_con_am
      1 indicador
     10 mieperho_medio
     22 part_alimentos
      3 personas
     25 personas_en_hogares_am
     51 pobreza
     10 pobreza_extrema
     25 pobreza_hogares_am
      3 rural
----
ccdd,departamento,valor,n_muestral
01,Amazonas,21.3538,378
02,Áncash,26.8081,463
03,Apurímac,28.5323,323
04,Arequipa,13.5117,423
05,Ayacucho,28.2764,386
06,Cajamarca,49.4445,470
07,Callao,28.1785,361
08,Cusco,16.9996,411
09,Huancavelica,36.5933,333
10,Huánuco,39.4076,369
11,Ica,2.8351,439
12,Junín,14.2025,466
13,La Libertad,24.0201,514
14,Lambayeque,14.34,462
15,Lima,26.0,1641
16,Loreto,43.7514,371
17,Madre de Dios,3.7553,100
18,Moquegua,17.1826,298
19,Pasco,40.9239,214
20,Piura,33.6685,464
21,Puno,43.1215,386
22,San Martín,24.5795,339
23,Tacna,32.7388,330
24,Tumbes,27.6518,222
25,Ucayali,26.1268,236
----
periodo,PN09822PM,PN01273PM,PD04722MM
2021-01,3.647883,2.675545,0.25
2021-02,2.709591,2.401342,0.25
2021-03,2.662516,2.598185,0.25
2021-04,1.998537,2.383698,0.25
2026-08,3.947585,4.437809,4.25
2026-09,3.992037,4.548655,4.25
2026-10,5.284086,5.251005,4.25
----
tipo,area,valor,n_muestral
Sin adultos mayores,Rural,58.6044,7803
Sin adultos mayores,Urbano,44.8026,15489
Con adultos mayores y menores de 65,Rural,58.6808,1618
Con adultos mayores y menores de 65,Urbano,41.0438,4312
Solo adultos mayores,Rural,58.1431,2239
Solo adultos mayores,Urbano,39.8708,2230
```

### → Llama a `Grep`

```json
{
 "pattern": "tipo_hogar|^hogares|^rural|^personas,|^mieperho|^part_alimentos|^pobreza_extrema|^am_vive|^hogares_con_am|^gasto_pc",
 "path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\salidas\\indicadores.csv",
 "output_mode": "content"
}
```

#### ← Resultado

```text
3:pobreza_extrema,nacional,Perú,5.5045,% de personas,factor07 × mieperho,33691
31:pobreza,tipo_hogar_am,Con adultos mayores y menores de 65,28.3717,% de personas,factor07 × mieperho,5930
32:pobreza_extrema,tipo_hogar_am,Con adultos mayores y menores de 65,5.3606,% de personas,factor07 × mieperho,5930
33:part_alimentos,tipo_hogar_am,Con adultos mayores y menores de 65,43.4124,% del gasto del hogar,factor07 × mieperho,5930
34:gasto_pc_mensual,tipo_hogar_am,Con adultos mayores y menores de 65,770.1944,soles corrientes por persona al mes,factor07 × mieperho,5930
35:mieperho_medio,tipo_hogar_am,Con adultos mayores y menores de 65,3.7858,personas por hogar,factor07,5930
36:hogares,tipo_hogar_am,Con adultos mayores y menores de 65,18.8731,% de hogares,factor07,5930
37:personas,tipo_hogar_am,Con adultos mayores y menores de 65,21.4683,% de personas,factor07 × mieperho,5930
38:rural,tipo_hogar_am,Con adultos mayores y menores de 65,13.4301,% de personas,factor07 × mieperho,5930
39:pobreza,tipo_hogar_am,Sin adultos mayores,27.8543,% de personas,factor07 × mieperho,23292
40:pobreza_extrema,tipo_hogar_am,Sin adultos mayores,5.5796,% de personas,factor07 × mieperho,23292
41:part_alimentos,tipo_hogar_am,Sin adultos mayores,47.5286,% del gasto del hogar,factor07 × mieperho,23292
42:gasto_pc_mensual,tipo_hogar_am,Sin adultos mayores,761.9594,soles corrientes por persona al mes,factor07 × mieperho,23292
43:mieperho_medio,tipo_hogar_am,Sin adultos mayores,3.5239,personas por hogar,factor07,23292
44:hogares,tipo_hogar_am,Sin adultos mayores,69.3732,% de hogares,factor07,23292
45:personas,tipo_hogar_am,Sin adultos mayores,73.4522,% de personas,factor07 × mieperho,23292
46:rural,tipo_hogar_am,Sin adultos mayores,19.751,% de personas,factor07 × mieperho,23292
47:pobreza,tipo_hogar_am,Solo adultos mayores,20.2572,% de personas,factor07 × mieperho,4469
48:pobreza_extrema,tipo_hogar_am,Solo adultos mayores,5.0271,% de personas,factor07 × mieperho,4469
49:part_alimentos,tipo_hogar_am,Solo adultos mayores,46.1133,% del gasto del hogar,factor07 × mieperho,4469
50:gasto_pc_mensual,tipo_hogar_am,Solo adultos mayores,977.1416,soles corrientes por persona al mes,factor07 × mieperho,4469
51:mieperho_medio,tipo_hogar_am,Solo adultos mayores,1.4383,personas por hogar,factor07,4469
52:hogares,tipo_hogar_am,Solo adultos mayores,11.7536,% de hogares,factor07,4469
53:personas,tipo_hogar_am,Solo adultos mayores,5.0795,% de personas,factor07 × mieperho,4469
54:rural,tipo_hogar_am,Solo adultos may
… (recortado)
```

### → Llama a `Grep`

```json
{
 "pattern": "tamano|tipo_hogar_am\\b|def tipo|n_am|n_res",
 "path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\limpiando-enaho\\scripts\\limpiar.py",
 "output_mode": "content",
 "-C": 2
}
```

#### ← Resultado

```text
166-    residentes = ((m02.p204 == 1) & (m02.p205 == 2)) | ((m02.p204 == 2) & (m02.p206 == 1))
167-    personas = m02.loc[residentes].copy()
168:    n_residentes = len(personas)
169-    personas["adulto_mayor"] = personas.p208a >= EDAD_ADULTO_MAYOR
170-
--
172-    comp = (personas.assign(menor_18=personas.p208a < 18)
173-            .groupby(LLAVES_HOGAR)
174:            .agg(n_residentes=("codperso", "size"), n_am=("adulto_mayor", "sum"), n_menores_18=("menor_18", "sum"))
175-            .reset_index())
176-    jefes = personas.loc[personas.p203 == 1, LLAVES_HOGAR + ["adulto_mayor"]].rename(columns={"adulto_mayor": "jefe_am"})
177-    comp = comp.merge(jefes, on=LLAVES_HOGAR, how="left", validate="1:1")
178-    comp["jefe_am"] = comp.jefe_am.fillna(False).astype(bool)
179:    comp["tipo_hogar_am"] = np.select(
180:        [comp.n_am == 0, comp.n_am < comp.n_residentes], TIPOS_HOGAR[:2], default=TIPOS_HOGAR[2])
181:    comp["am_vive_solo"] = (comp.n_residentes == 1) & (comp.n_am == 1)
182-
183-    # ------------------------------------------------------------------------------------------ base hogar
--
189-
190-    hogares = sumaria.merge(comp, on=LLAVES_HOGAR, how="left", validate="1:1", indicator=True)
191:    hogares_sin_residentes = int((hogares._merge != "both").sum())
192-    hogares = hogares.drop(columns="_merge")
193-    hogares["departamento"] = hogares.ubigeo.str.zfill(6).str[:2]
--
198-    hogares["part_alimentos"] = 100 * hogares.g1_alimentos / hogares.g0_total
199-    hogares["gasto_pc_mensual"] = hogares.g0_total / (12 * hogares.mieperho)
200:    hogares["tamano_hogar"] = pd.cut(hogares.mieperho, [0, 1, 2, 4, np.inf], labels=TAMANOS).astype(str)
201-
202-    # ---------------------------------------------------------------------------------------- base persona
203-    cols_hogar = ["pobreza", "pobre", "pobre_extremo", "mieperho", "factor07", "peso_personas", "ubigeo",
204:                  "departamento", "estrato", "urbano", "dominio", "tipo_hogar_am", "n_am", "part_alimentos"]
205-    base = personas.merge(hogares[LLAVES_HOGAR + cols_hogar], on=LLAVES_HOGAR, how="inner", validate="m:1")
206:    chequear(esenciales, len(base) == n_residentes and not base.duplicated(LLAVES_PERSONA).any(),
207:             f"la unión m:1 personas-hogares conserva las {n_residentes:,} filas, sin perder ni duplicar")
208:    chequear(esenciales, hogares_sin_residentes == 0, "todos los hogares de la sumaria tienen residentes en el "
209:             f"módulo 02 
… (recortado)
```

### → Llama a `Grep`

```json
{
 "pattern": ",area,|nacional",
 "path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\salidas\\indicadores.csv",
 "output_mode": "content"
}
```

#### ← Resultado

```text
2:pobreza,nacional,Perú,27.5795,% de personas,factor07 × mieperho,33691
3:pobreza_extrema,nacional,Perú,5.5045,% de personas,factor07 × mieperho,33691
4:pobreza,area,Urbano,24.807,% de personas,factor07 × mieperho,22031
5:pobreza,area,Rural,39.3028,% de personas,factor07 × mieperho,11660
109:mieperho_medio,nacional,Perú,3.3282,personas por hogar,factor07,33691
110:hogares_con_am,nacional,Perú,30.6268,% de hogares,factor07,33691
112:part_alimentos,nacional,Perú,46.573,% del gasto del hogar,factor07 × mieperho,33691
```

### → Llama a `Grep`

```json
{
 "pattern": "mieperho",
 "path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\limpiando-enaho\\reference.md",
 "output_mode": "content",
 "-C": 1
}
```

#### ← Resultado

```text
14-| `dominio` | 1 a 8. Lima Metropolitana es `dominio == 8`. |
15:| `mieperho` | Miembros del hogar según la sumaria. |
16-| `factor07` | Factor de expansión del hogar. Úsalo solo para cifras **de hogares** («% de hogares»). |
17:| `peso_personas` | `factor07 × mieperho`. **El peso de la cifra oficial** («% de personas»). |
18-| `pobreza` | 1 pobre extremo · 2 pobre no extremo · 3 no pobre. **Códigos, no una escala**: nunca promedies. |
19-| `pobre`, `pobre_extremo` | `pobreza <= 2` y `pobreza == 1`. |
20:| `n_residentes` | Residentes habituales del hogar en el módulo 02. Coincide con `mieperho` en la gran mayoría de hogares, no en todos. |
21-| `n_am`, `n_menores_18` | Residentes de 65 años o más y menores de 18. |
--
27-| `part_alimentos` | `100 × g1_alimentos / g0_total`: % del gasto del hogar que va a alimentos. Mide **exposición** a la inflación de alimentos. |
28:| `gasto_pc_mensual` | `g0_total / (12 × mieperho)`, soles corrientes por persona al mes. |
29-
```

### → Llama a `Bash`

```json
{
 "command": "cd \"~/Documentos/GitHub/python-intermedio-QLAB/tarea_4\" && ls informes/ figuras/ mapas/ 2>&1; cat pyproject.toml 2>/dev/null | head -30",
 "description": "List report, figure and map folders"
}
```

#### ← Resultado

```text
figuras/:
alimentos_tipo_hogar_2024.csv
alimentos_tipo_hogar_2024.png
alimentos_tipo_hogar_area_2024.csv
alimentos_tipo_hogar_area_2024.png
bcrp_inflacion_tasa_2021_2026.csv
bcrp_inflacion_tasa_2021_2026.png
pobreza_area_2024.csv
pobreza_area_2024.png
pobreza_departamento_2024.csv
pobreza_departamento_2024.png
pobreza_edad_2024.csv
pobreza_edad_2024.png
pobreza_sexo_2024.csv
pobreza_sexo_2024.png
pobreza_tipo_hogar_2024.csv
pobreza_tipo_hogar_2024.png
pobreza_tipo_hogar_area_2024.csv
pobreza_tipo_hogar_area_2024.png

informes/:

mapas/:
personas_en_hogares_am_departamento_2024.csv
personas_en_hogares_am_departamento_2024.png
pobreza_departamento_2024.csv
pobreza_departamento_2024.png
pobreza_hogares_am_departamento_2024.csv
pobreza_hogares_am_departamento_2024.png
[project]
name = "tarea-4-agente-investigacion"
version = "0.1.0"
description = "Agente de investigación socioeconómica: MCP del BCRP y Skills de la ENAHO 2024"
requires-python = ">=3.11"
dependencies = [
    "fastmcp>=4,<5",
    "geopandas>=1.2.0",
    "httpx",
    "matplotlib>=3.11.2",
    "pandas",
    "pyarrow>=26.0.1",
]

[dependency-groups]
dev = ["pytest"]

[tool.pytest.ini_options]
testpaths = ["mcp"]
```

### → Llama a `Read`

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\limpiando-enaho\\reference.md"
}
```

#### ← Resultado

```text
1	# Variables de las bases limpias de la ENAHO · versión tarea_4
2	
3	Dos bases, una por unidad de análisis. Elige la del corte: **hogar** para todo lo que describe al hogar (pobreza
4	oficial, área, departamento, tipo de hogar, gasto) y **persona** solo para atributos de la persona (sexo, edad).
5	
6	## `salidas/hogares_<año>.parquet` · una fila por hogar (33,691 en 2024)
7	
8	| Columna | Qué es |
9	|---|---|
10	| `conglome`, `vivienda`, `hogar` | Llaves del hogar, **texto** de largo fijo (`conglome` = «015009»; como número perdería el cero). |
11	| `ubigeo` | Seis dígitos como texto: departamento (2) + provincia (2) + distrito (2). |
12	| `departamento` | `ubigeo[:2]`. Lima es `15` y Callao `07`, separados. Se une al mapa con `FIRST_IDDP`. |
13	| `estrato`, `urbano` | Estrato 1 a 5 urbano, 6 a 8 rural; `urbano = estrato <= 5`. |
14	| `dominio` | 1 a 8. Lima Metropolitana es `dominio == 8`. |
15	| `mieperho` | Miembros del hogar según la sumaria. |
16	| `factor07` | Factor de expansión del hogar. Úsalo solo para cifras **de hogares** («% de hogares»). |
17	| `peso_personas` | `factor07 × mieperho`. **El peso de la cifra oficial** («% de personas»). |
18	| `pobreza` | 1 pobre extremo · 2 pobre no extremo · 3 no pobre. **Códigos, no una escala**: nunca promedies. |
19	| `pobre`, `pobre_extremo` | `pobreza <= 2` y `pobreza == 1`. |
20	| `n_residentes` | Residentes habituales del hogar en el módulo 02. Coincide con `mieperho` en la gran mayoría de hogares, no en todos. |
21	| `n_am`, `n_menores_18` | Residentes de 65 años o más y menores de 18. |
22	| `jefe_am` | El jefe del hogar (`p203 == 1`) tiene 65 años o más. |
23	| `tipo_hogar_am` | «Sin adultos mayores», «Con adultos mayores y menores de 65» o «Solo adultos mayores». |
24	| `am_vive_solo` | Hogar de una sola persona, de 65 años o más. |
25	| `g1_alimentos` … `g8_otros` | Gasto anual por grupo de la canasta, en soles corrientes, según el do-file del INEI. |
26	| `g0_total` | Suma de los 8 grupos. Es igual a `gashog2d` (el script lo comprueba). |
27	| `part_alimentos` | `100 × g1_alimentos / g0_total`: % del gasto del hogar que va a alimentos. Mide **exposición** a la inflación de alimentos. |
28	| `gasto_pc_mensual` | `g0_total / (12 × mieperho)`, soles corrientes por persona al mes. |
29	
30	## `salidas/personas_<año>.parquet` · una fila por residente habitual (108,664 en 2024)
31	
32	Las llaves del hogar, `codperso` y las columnas del hogar de arriba (`pobreza`, `pobre`, `peso_personas`,
33	`departam
… (recortado)
```

### → Llama a `Read`

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\limpiando-enaho\\scripts\\limpiar.py",
 "offset": 305,
 "limit": 40
}
```

#### ← Resultado

```text
305	    # -------------------------------------------------------------------------------------- indicadores
306	    filas = []
307	
308	    def agregar(indicador, corte, grupo, valor, unidad, ponderador, n):
309	        filas.append({"indicador": indicador, "corte": corte, "grupo": grupo, "valor": round(float(valor), 4),
310	                      "unidad": unidad, "ponderador": ponderador, "n_muestral": int(n)})
311	
312	    P, H = "factor07 × mieperho", "factor07"
313	    for clave in ("pobreza_nacional", "pobreza_extrema"):
314	        agregar(clave.replace("_nacional", ""), "nacional", "Perú", oficial[clave], "% de personas", P, n_hogares)
315	    for urb, nombre in ((True, "Urbano"), (False, "Rural")):
316	        m = hogares.urbano == urb
317	        agregar("pobreza", "area", nombre, pct(hogares.pobre[m], w[m]), "% de personas", P, m.sum())
318	    for cod, g in hogares.groupby("departamento"):
319	        agregar("pobreza", "departamento", f"{cod} {DEPARTAMENTOS[cod]}", pct(g.pobre, g.peso_personas),
320	                "% de personas", P, len(g))
321	    # estructura del hogar según la presencia de adultos mayores (65+)
322	    for corte, grupos in (("tipo_hogar_am", hogares.groupby("tipo_hogar_am")),
323	                          ("tipo_hogar_am × area", hogares.groupby(["tipo_hogar_am", "urbano"]))):
324	        for clave, g in grupos:
325	            grupo = clave if isinstance(clave, str) else f"{clave[0]} · {'Urbano' if clave[1] else 'Rural'}"
326	            pw = g.peso_personas
327	            agregar("pobreza", corte, grupo, pct(g.pobre, pw), "% de personas", P, len(g))
328	            agregar("pobreza_extrema", corte, grupo, pct(g.pobre_extremo, pw), "% de personas", P, len(g))
329	            agregar("part_alimentos", corte, grupo, media(g.part_alimentos, pw), "% del gasto del hogar", P, len(g))
330	            agregar("gasto_pc_mensual", corte, grupo, media(g.gasto_pc_mensual, pw), "soles corrientes por persona "
331	                    "al mes", P, len(g))
332	            agregar("mieperho_medio", corte, grupo, media(g.mieperho, g.factor07), "personas por hogar", H, len(g))
333	            if corte == "tipo_hogar_am":
334	                agregar("hogares", corte, grupo, 100 * g.factor07.sum() / w_hog.sum(), "% de hogares", H, len(g))
335	                agregar("personas", corte, grupo, 100 * pw.sum() / w.sum(), "% de personas", P, len(g))
336	                agregar("rural", corte, grupo, pct(~g.urbano, pw), "% de personas", P, len(g)
… (recortado)
```

### → Llama a `Write`

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\informes\\calculos_exposicion.py",
 "content": "\"\"\"Exposición de los hogares a la inflación de alimentos, según la presencia de adultos mayores (65+).\n\nContribución aproximada de los alimentos a la inflación del hogar, en puntos porcentuales:\n\n    contribucion_pp = part_alimentos × inflación de alimentos a 12 meses / 100\n\n- part_alimentos: % del gasto del hogar que va a alimentos (ENAHO 2024, base hogar, factor07 × mieperho), tomado de\n  salidas/indicadores.csv, que generó la skill limpiando-enaho.\n- inflación de alimentos: PN09822PM (IPC Alimentos y Bebidas de Lima Metropolitana, var. % 12 meses), tomada del CSV\n  que dejó la herramienta graficar_series del MCP bcrp en figuras/.\n\nNo descarga nada ni escribe cifras a mano: solo lee esos dos archivos. Desde tarea_4/:\n\n    uv run python informes/calculos_exposicion.py\n\"\"\"\n\nfrom pathlib import Path\n\nimport pandas as pd\n\nRAIZ = Path(__file__).resolve().parents[1]\nINDICADORES = RAIZ / \"salidas\" / \"indicadores.csv\"\nBCRP = RAIZ / \"figuras\" / \"bcrp_inflacion_tasa_2021_2026.csv\"\n\nALIM, TOTAL, TASA = \"PN09822PM\", \"PN01273PM\", \"PD04722MM\"\nTIPOS = [\"Sin adultos mayores\", \"Con adultos mayores y menores de 65\", \"Solo adultos mayores\"]\nTAMANOS = [\"1 persona\", \"2 personas\", \"3 a 4 personas\", \"5 o más personas\"]\nAREAS = [\"Urbano\", \"Rural\"]\nN_MIN = 100  # celdas con menos hogares en la muestra se marcan como no confiables\nBASE = \"sin AM\"  # grupo de comparación: hogares sin adultos mayores\n\n\ndef contribucion(part_alimentos: float, inflacion_alimentos: float) -> float:\n    \"\"\"Puntos porcentuales de inflación del hogar que aportan los alimentos.\"\"\"\n    return part_alimentos * inflacion_alimentos / 100\n\n\ndef valor(ind: pd.DataFrame, indicador: str, corte: str, grupo: str) -> tuple[float, int]:\n    fila = ind[(ind.indicador == indicador) & (ind.corte == corte) & (ind.grupo == grupo)]\n    if len(fila) != 1:\n        raise SystemExit(f\"No encuentro una sola fila para {indicador} / {corte} / {grupo} en {INDICADORES}\")\n    return float(fila.valor.iloc[0]), int(fila.n_muestral.iloc[0])\n\n\ndef corto(tipo: str) -> str:\n    return {\"Sin adultos mayores\": \"sin AM\", \"Con adultos mayores y menores de 65\": \"AM + menores de 65\",\n            \"Solo adultos mayores\": \"solo AM\"}[tipo]\n\n\ndef main() -> None:\n    ind = pd.read_csv(INDICADORES)\n    bcrp =
… (recortado)
```

#### ← Resultado

```text
File created successfully at: ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\informes\calculos_exposicion.py (file state is current in your context — no need to Read it back)
```

### → Llama a `Bash`

```json
{
 "command": "cd \"~/Documentos/GitHub/python-intermedio-QLAB/tarea_4\" && PYTHONIOENCODING=utf-8 uv run python informes/calculos_exposicion.py; echo \"EXIT=$?\"",
 "description": "Run exposure calculation script",
 "timeout": 180000
}
```

#### ← Resultado

```text
====================================================================================================
BCRP · figuras/bcrp_inflacion_tasa_2021_2026.csv (2021-01 a 2026-10, 70 meses)
  Último mes con dato: 2026-10
    PN09822PM inflación de alimentos y bebidas, Lima, 12 meses : 5.28 %
    PN01273PM inflación total, Lima, 12 meses                  : 5.25 %
    PD04722MM tasa de referencia                              : 4.25 %
    brecha alimentos - total en 2026-10                       : +0.03 pp
  Pico de PN09822PM en el periodo: 2023-02 con 13.16 % (brecha alimentos - total ese mes: +4.52 pp)
====================================================================================================
ENAHO 2024 · por tipo de hogar (nacional) · salidas/indicadores.csv, corte tipo_hogar_am
  pobreza, extrema, part_alimentos, personas y rural: factor07 × mieperho · mieperho_medio y hogares: factor07
  tipo de hogar                        pobreza extrema  alim.% mieperho  %hog. %pers. %rural contrib.      n
  Sin adultos mayores                     27.9     5.6    47.5     3.52   69.4   73.5   19.8     2.51 23,292
  Con adultos mayores y menores de 65     28.4     5.4    43.4     3.79   18.9   21.5   13.4     2.29  5,930
  Solo adultos mayores                    20.3     5.0    46.1     1.44   11.8    5.1   34.2     2.44  4,469
  contrib. = part_alimentos × PN09822PM de 2026-10 (5.28 %) / 100, en pp
====================================================================================================
EXPOSICIÓN · tipo de hogar × área · contribución de los alimentos a la inflación del hogar (pp)
  último mes: PN09822PM 2026-10 = 5.28 % · pico: PN09822PM 2023-02 = 13.16 %
  ENAHO: corte «tipo_hogar_am × area», base hogar, factor07 × mieperho (mieperho_medio con factor07)
  --- Urbano
  tipo de hogar                         alim.% contrib.ult contrib.pico  pobreza extrema mieperho      n  confiable
  Sin adultos mayores                     44.8        2.37         5.90     25.0     3.2     3.51 15,489  sí
  Con adultos mayores y menores de 65     41.0        2.17         5.40     26.1     3.2     3.87  4,312  sí
  Solo adultos mayores                    39.9        2.11         5.25     13.8     1.3     1.45  2,230  sí
    AM + menores de 65 - sin AM (Urbano): part_alimentos -3.8 pp · contribución -0.20 pp (2026-10) y -0.49 pp (2023-02) · pobreza +1.0 pp
    solo AM - sin AM (Urbano): part_alimentos -4.9 pp · contribución -0.26 pp (2026-10) y -0.65 
… (recortado)
```

### → Llama a `Read`

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\figuras\\bcrp_inflacion_tasa_2021_2026.png"
}
```

#### ← Resultado

```text

```

### → Llama a `Read`

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\figuras\\alimentos_tipo_hogar_area_2024.png"
}
```

#### ← Resultado

```text

```

### → Llama a `Read`

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\mapas\\pobreza_hogares_am_departamento_2024.png"
}
```

#### ← Resultado

```text

```

### → Llama a `Read`

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\limpiando-enaho\\scripts\\limpiar.py",
 "offset": 350,
 "limit": 8
}
```

#### ← Resultado

```text
350	    for cod, g in hogares.groupby("departamento"):
351	        nombre, gam = f"{cod} {DEPARTAMENTOS[cod]}", g[g.n_am > 0]
352	        agregar("personas_en_hogares_am", "departamento", nombre, pct(g.n_am > 0, g.peso_personas), "% de personas",
353	                P, len(g))
354	        agregar("pobreza_hogares_am", "departamento", nombre, pct(gam.pobre, gam.peso_personas), "% de personas",
355	                P, len(gam))
356	    # la persona como unidad (base secundaria, facpob07)
357	    for am, nombre in ((True, "65 años o más"), (False, "Menos de 65 años")):
```

### → Llama a `Grep`

```json
{
 "pattern": "^pobreza,departamento",
 "path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\salidas\\indicadores.csv",
 "output_mode": "content"
}
```

#### ← Resultado

```text
6:pobreza,departamento,01 Amazonas,25.7488,% de personas,factor07 × mieperho,1243
7:pobreza,departamento,02 Áncash,22.7746,% de personas,factor07 × mieperho,1393
8:pobreza,departamento,03 Apurímac,23.9587,% de personas,factor07 × mieperho,913
9:pobreza,departamento,04 Arequipa,15.7844,% de personas,factor07 × mieperho,1506
10:pobreza,departamento,05 Ayacucho,32.7633,% de personas,factor07 × mieperho,1160
11:pobreza,departamento,06 Cajamarca,45.0069,% de personas,factor07 × mieperho,1469
12:pobreza,departamento,07 Callao,33.8599,% de personas,factor07 × mieperho,1027
13:pobreza,departamento,08 Cusco,18.5413,% de personas,factor07 × mieperho,1230
14:pobreza,departamento,09 Huancavelica,33.4034,% de personas,factor07 × mieperho,1042
15:pobreza,departamento,10 Huánuco,38.9626,% de personas,factor07 × mieperho,1244
16:pobreza,departamento,11 Ica,6.0142,% de personas,factor07 × mieperho,1500
17:pobreza,departamento,12 Junín,18.4994,% de personas,factor07 × mieperho,1506
18:pobreza,departamento,13 La Libertad,30.1903,% de personas,factor07 × mieperho,1509
19:pobreza,departamento,14 Lambayeque,14.0406,% de personas,factor07 × mieperho,1302
20:pobreza,departamento,15 Lima,27.0689,% de personas,factor07 × mieperho,4544
21:pobreza,departamento,16 Loreto,42.9726,% de personas,factor07 × mieperho,1359
22:pobreza,departamento,17 Madre de Dios,11.1478,% de personas,factor07 × mieperho,603
23:pobreza,departamento,18 Moquegua,10.9682,% de personas,factor07 × mieperho,963
24:pobreza,departamento,19 Pasco,38.972,% de personas,factor07 × mieperho,865
25:pobreza,departamento,20 Piura,31.861,% de personas,factor07 × mieperho,1611
26:pobreza,departamento,21 Puno,39.9381,% de personas,factor07 × mieperho,1123
27:pobreza,departamento,22 San Martín,22.0215,% de personas,factor07 × mieperho,1347
28:pobreza,departamento,23 Tacna,23.989,% de personas,factor07 × mieperho,1271
29:pobreza,departamento,24 Tumbes,26.9012,% de personas,factor07 × mieperho,842
30:pobreza,departamento,25 Ucayali,27.0701,% de personas,factor07 × mieperho,1119
```

### Claude

Tengo todas las cifras. Escribo el informe.

### → Llama a `Write`

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\informes\\informe_final.md",
 "content": "# ¿Están más expuestos a la inflación los hogares con adultos mayores? ENAHO 2024 y series del BCRP, 2021-2026\n\n**Respuesta corta.** No de manera general. La exposición depende del área y no de que haya adultos mayores en el hogar.\nEn la ENAHO 2024 (base hogar, `factor07 × mieperho`), dentro de lo urbano y dentro de lo rural los hogares con adultos\nmayores (65+) gastan en alimentos la misma parte del presupuesto que los hogares sin ellos, o una parte menor. Con la\ninflación de alimentos de 2026-10 (PN09822PM, 5.28 %), los alimentos aportan entre 2.11 pp (hogares urbanos de solo\nadultos mayores) y 3.10 pp (hogares rurales) a la inflación del hogar. La brecha rural-urbana (0.73 a 0.97 pp) es\nmayor que cualquier brecha por tipo de hogar (−0.26 pp como máximo). Hay un matiz: a igual tamaño (1 y 2 personas),\nlos hogares de solo adultos mayores son más pobres (+7.1 y +15.2 pp) y gastan algo más en alimentos (+1.4 y +2.2 pp).\nSu menor pobreza en bruto (20.3 % frente a 27.9 %) va de la mano con su menor tamaño (1.44 personas por hogar).\n\n## 1. Pregunta de investigación\n\n**Tema.** La exposición de los hogares peruanos a la inflación de alimentos según tengan o no miembros de 65 años o más,\ny su relación con la pobreza monetaria y la estructura del hogar.\n\n**Objetivo.** Comparar tres tipos de hogar en pobreza, pobreza extrema, tamaño y peso de los alimentos en el gasto:\n*sin adultos mayores*, *con adultos mayores y menores de 65* y *solo adultos mayores*. Esa estructura de gasto de 2024 se\naplica luego a la inflación de alimentos que mide el BCRP, y se describe cómo se movieron juntas la inflación de\nalimentos, la inflación total y la tasa de referencia entre 2021-01 y 2026-10.\n\n**Delimitación.**\n- Cubre la ENAHO 2024 del INEI (módulo 34, sumaria; módulo 02, miembros del hogar) a nivel nacional, urbano/rural y\n  departamental, y tres series mensuales del BCRP entre 2021-01 y 2026-10.\n- La exposición se mide solo por el peso de los alimentos en el gasto del hogar. No mide cuánto se endeudan o ahorran\n  los hogares, que es el canal por el que la tasa de referencia llega a ellos, ni el uso de pensiones o programas\n  sociales.\n- No estima efectos causales. Las comparaciones son descriptivas y las correlaciones entre series agregadas solo\n  describen co-movimiento.\n- No usa índices de precios regionales: la inflaci
… (recortado)
```

#### ← Resultado

```text
File created successfully at: ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\informes\informe_final.md (file state is current in your context — no need to Read it back)
```

### → Llama a `Grep`

```json
{
 "pattern": "caus|provoc|gener[aóe]|explic|efecto|debido|impact|determin",
 "path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\informes\\informe_final.md",
 "output_mode": "content",
 "-i": true
}
```

#### ← Resultado

```text
3:**Respuesta corta.** No de manera general. La exposición depende del área y no de que haya adultos mayores en el hogar.
28:- No estima efectos causales. Las comparaciones son descriptivas y las correlaciones entre series agregadas solo
96:  seis meses antes que con la del mismo mes. Es co-movimiento entre agregados, no causalidad.
233:1. **No hay un «efecto adulto mayor» sobre la exposición a la inflación de alimentos en los datos de 2024.** El peso de
242:3. **Los hogares multigeneracionales rurales son el grupo más frágil.** Tienen la pobreza (43.2 %) y la pobreza extrema
287:  no dicen nada sobre la causalidad ni sobre los hogares individuales.
322:**Archivos usados y generados:**
```

### → Llama a `Edit`

```json
{
 "replace_all": false,
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\informes\\informe_final.md",
 "old_string": "**Respuesta corta.** No de manera general. La exposición depende del área y no de que haya adultos mayores en el hogar.",
 "new_string": "**Respuesta corta.** No de manera general. La exposición va de la mano con el área y no con que haya adultos mayores en\nel hogar."
}
```

#### ← Resultado

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\informes\informe_final.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

### → Llama a `Edit`

```json
{
 "replace_all": false,
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\informes\\informe_final.md",
 "old_string": "1. **No hay un «efecto adulto mayor» sobre la exposición a la inflación de alimentos en los datos de 2024.** El peso de",
 "new_string": "1. **En los datos de 2024, tener adultos mayores en el hogar no se asocia con una mayor exposición a la inflación de\n   alimentos.** El peso de"
}
```

#### ← Resultado

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\informes\informe_final.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

### → Llama a `Edit`

```json
{
 "replace_all": false,
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\informes\\informe_final.md",
 "old_string": "   (19.6 %) más altas de la tabla por área, y el peso de alimentos más alto (58.7 %). Si una subida de los alimentos\n   golpea a algún tipo de hogar con adultos mayores, es a este. Pero su contribución (3.10 pp en 2026-10) es igual a la\n   de los hogares rurales sin adultos mayores.",
 "new_string": "   (19.6 %) más altas de la tabla por área, y el peso de alimentos más alto (58.7 %). De los hogares con adultos\n   mayores, es el que tiene menos margen ante alimentos más caros. Pero su contribución (3.10 pp en 2026-10) es igual a\n   la de los hogares rurales sin adultos mayores."
}
```

#### ← Resultado

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\informes\informe_final.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

### → Llama a `Edit`

```json
{
 "replace_all": false,
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\informes\\informe_final.md",
 "old_string": "  de equivalencia, lo que de por sí favorece a los hogares chicos.",
 "new_string": "  de equivalencia, una medida que tiende a mostrar menos pobreza en los hogares chicos."
}
```

#### ← Resultado

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\informes\informe_final.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

### → Llama a `Read`

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\informes\\informe_final.md",
 "limit": 14
}
```

#### ← Resultado

```text
1	# ¿Están más expuestos a la inflación los hogares con adultos mayores? ENAHO 2024 y series del BCRP, 2021-2026
2	
3	**Respuesta corta.** No de manera general. La exposición va de la mano con el área y no con que haya adultos mayores en
4	el hogar.
5	En la ENAHO 2024 (base hogar, `factor07 × mieperho`), dentro de lo urbano y dentro de lo rural los hogares con adultos
6	mayores (65+) gastan en alimentos la misma parte del presupuesto que los hogares sin ellos, o una parte menor. Con la
7	inflación de alimentos de 2026-10 (PN09822PM, 5.28 %), los alimentos aportan entre 2.11 pp (hogares urbanos de solo
8	adultos mayores) y 3.10 pp (hogares rurales) a la inflación del hogar. La brecha rural-urbana (0.73 a 0.97 pp) es
9	mayor que cualquier brecha por tipo de hogar (−0.26 pp como máximo). Hay un matiz: a igual tamaño (1 y 2 personas),
10	los hogares de solo adultos mayores son más pobres (+7.1 y +15.2 pp) y gastan algo más en alimentos (+1.4 y +2.2 pp).
11	Su menor pobreza en bruto (20.3 % frente a 27.9 %) va de la mano con su menor tamaño (1.44 personas por hogar).
12	
13	## 1. Pregunta de investigación
14	
```

### → Llama a `Edit`

```json
{
 "replace_all": false,
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\informes\\informe_final.md",
 "old_string": "**Respuesta corta.** No de manera general. La exposición va de la mano con el área y no con que haya adultos mayores en\nel hogar.\nEn la ENAHO 2024 (base hogar, `factor07 × mieperho`), dentro de lo urbano y dentro de lo rural los hogares con adultos\nmayores (65+) gastan en alimentos la misma parte del presupuesto que los hogares sin ellos, o una parte menor. Con la\ninflación de alimentos de 2026-10 (PN09822PM, 5.28 %), los alimentos aportan entre 2.11 pp (hogares urbanos de solo\nadultos mayores) y 3.10 pp (hogares rurales) a la inflación del hogar. La brecha rural-urbana (0.73 a 0.97 pp) es\nmayor que cualquier brecha por tipo de hogar (−0.26 pp como máximo). Hay un matiz: a igual tamaño (1 y 2 personas),\nlos hogares de solo adultos mayores son más pobres (+7.1 y +15.2 pp) y gastan algo más en alimentos (+1.4 y +2.2 pp).\nSu menor pobreza en bruto (20.3 % frente a 27.9 %) va de la mano con su menor tamaño (1.44 personas por hogar).",
 "new_string": "**Respuesta corta.** No de manera general: la exposición va de la mano con el área, no con la presencia de adultos mayores.\nCon la inflación de alimentos de 2026-10 (PN09822PM, 5.28 %), los alimentos aportan de 2.11 a 3.10 pp a la inflación\ndel hogar (ENAHO 2024, base hogar, `factor07 × mieperho`). La brecha rural-urbana (0.73 a 0.97 pp) supera la que hay\nentre tipos de hogar dentro de cada área (−0.26 pp como máximo). A igual tamaño (1 y 2 personas), los hogares de solo\nadultos mayores son más pobres (+7.1 y +15.2 pp); su menor pobreza en bruto (20.3 %) va con su menor tamaño (1.44)."
}
```

#### ← Resultado

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\informes\informe_final.md has been updated successfully.
```

### Claude

Terminé el informe, en `informes/informe_final.md`. La validación de la ENAHO aprobó las 15 comprobaciones esenciales (pobreza nacional 27.58 % frente a la referencia de 27.6 %), así que pude seguir con los gráficos, el mapa y el cálculo de exposición.

**Respuesta:** No de manera general. La exposición a la inflación de alimentos va de la mano con el área (urbano o rural), no con que haya adultos mayores en el hogar.
- **Exposición:** con la inflación de alimentos de 2026-10 (PN09822PM, 5.28 %), los alimentos aportan entre 2.11 y 3.10 puntos a la inflación del hogar. La brecha entre rural y urbano (0.73 a 0.97 puntos) es mayor que la que hay entre tipos de hogar dentro de cada área (−0.26 puntos como máximo).
- **Pobreza:** en bruto, los hogares de solo adultos mayores parecen menos pobres (20.3 % frente a 27.9 %). Pero son mucho más chicos (1.44 personas por hogar), y comparados con hogares del mismo tamaño son más pobres: +7.1 puntos en hogares de 1 persona y +15.2 en los de 2.

**Dos cosas que conviene saber:**
- **Ficha de PD04722MM:** la ficha y el catálogo dicen que la tasa de referencia empieza en Ene-2004, pero los datos empiezan en 2003-09. No afecta el periodo 2021-2026; lo anoté en Limitaciones.
- **Celdas no confiables:** tres celdas del corte por tamaño tienen menos de 100 hogares y las marqué así (n = 43, 55 y 4). Salen porque el tipo de hogar se arma con los residentes del módulo 02 y el tamaño con `mieperho`, y esos dos conteos no siempre coinciden.

La sección 8 quedó con las dos líneas de marcador vacías; `informes/verificar_informe.py` todavía no existe en el repo.

**Herramientas MCP (`bcrp`) usadas:**
- `buscar_series` (3 búsquedas)
- Fichas `bcrp://serie/{codigo}` de PD04722MM, PN09822PM y PN01273PM, leídas con `ReadMcpResourceTool`
- `resumen` (PN09822PM, PN01273PM y PD04722MM desde 2021-01; PD04722MM también desde 2003-01)
- `correlacion` (alimentos frente a inflación total y frente a tasa de referencia, con rezago 0 y 6)
- `graficar_series` (`bcrp_inflacion_tasa_2021_2026`)
- `serie` (PD04722MM de 2003-01 a 2004-02)

**Skills usadas:**
- `limpiando-enaho`: `limpiar.py --anio 2024`
- `graficando-enaho`: `--corte tipo_hogar_area` con `--indicador alimentos` y con `--indicador pobreza`
- `mapeando-enaho`: `--indicador pobreza_hogares_am`

**Archivos:**
- Informe: `informes/informe_final.md`
- Script de exposición: `informes/calculos_exposicion.py`

## Resultado

- Herramientas, en orden: mcp__bcrp__buscar_series, mcp__bcrp__buscar_series, mcp__bcrp__buscar_series, ReadMcpResourceTool, ReadMcpResourceTool, ReadMcpResourceTool, mcp__bcrp__resumen, mcp__bcrp__resumen, mcp__bcrp__resumen, mcp__bcrp__correlacion, mcp__bcrp__correlacion, mcp__bcrp__correlacion, mcp__bcrp__correlacion, mcp__bcrp__graficar_series, mcp__bcrp__resumen, mcp__bcrp__serie, Glob, Skill(limpiando-enaho), Bash, Skill(graficando-enaho), Bash, Skill(mapeando-enaho), Bash, Bash, Grep, Grep, Grep, Grep, Bash, Read, Read, Write, Bash, Read, Read, Read, Read, Grep, Write, Grep, Edit, Edit, Edit, Edit, Read, Edit
- Turnos: 50
- Segundos: 356.5
- Costo informado por Claude Code: US$ 1.9395
- ¿Terminó con error?: False
