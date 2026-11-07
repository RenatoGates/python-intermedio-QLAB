# MCP bcrp en Claude Code · caso «prompt»

Sesión nueva de `claude -p` con `--model haiku`, solo el servidor `bcrp` de `.mcp.json` (`--strict-mcp-config --tools "" --allowedTools mcp__bcrp`). Generado por `probar_en_claude_code.py`.

## Pedido

```text
/mcp__bcrp__informe "inflación de alimentos y tasa de referencia, 2021-2026"
```

**Servidores MCP:** bcrp (connected), fetch (connected)  
**Herramientas disponibles:** mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie, mcp__fetch__fetch

### → Llama a `mcp__bcrp__buscar_series`

```json
{
 "texto": "inflación alimentos",
 "frecuencia": "Mensual"
}
```

#### ← Respuesta de la herramienta

```json
{"result":[{"codigo":"PN01313PM","nombre":"Índice de precios Lima Metropolitana (var% mensual) - IPC Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN09816PM","nombre":"Índice de precios Lima Metropolitana (var% mensual) - IPC Alimentos y Energía","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1991","actualizada":"2026-10-08"},{"codigo":"PN09819PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Energía","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1992","actualizada":"2026-10-08"},{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01276PM","nombre":"Índice de precios Lima Metropolitana (var% mensual) - IPC Sin Alimentos y Energía","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01314PM","nombre":"Índice de precios Lima Metropolitana (var% mensual) - IPC sin Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01277PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Sin Alimentos y Energía","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN09823PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC sin Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN39445PM","nombre":"Índice de precios Lima Metropolitana (índice Dic.2021 = 100) - IPC Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1992","actualizada":"2026-10-08"},{"codigo":"PN39521PM","nombre":"Índice de precios Lima Metropolitana (índice Dic.2021 = 100) - IPC Alimentos y Energía","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1991","actualizada":"2026-10-08"}]}
```

### → Llama a `mcp__bcrp__buscar_series`

```json
{
 "texto": "tasa de referencia",
 "frecuencia": "Mensual"
}
```

### → Llama a `mcp__bcrp__buscar_series`

```json
{
 "texto": "ipc total variación 12 meses",
 "frecuencia": "Mensual"
}
```

#### ← Respuesta de la herramienta

```json
{"result":[]}
```

#### ← Respuesta de la herramienta

```json
{"result":[{"codigo":"PD04722MM","nombre":"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria","categoria":"Tasas de interés","frecuencia":"Mensual","inicio":"Ene-2004","actualizada":"2026-10-15"},{"codigo":"PN07809NM","nombre":"Tasas de interés activas y pasivas promedio de las empresas bancarias en MN (términos efectivos anuales) - Activas - Preferencial Corporativa a 90 días","categoria":"Tasas de interés","frecuencia":"Mensual","inicio":"Ene-2011","actualizada":"2026-10-23"},{"codigo":"PN07829NM","nombre":"Tasas de interés activas y pasivas promedio de las empresas bancarias en ME (términos efectivos anuales) - Activas - Preferencial Corporativa a 90 días","categoria":"Tasas de interés","frecuencia":"Mensual","inicio":"Ene-2011","actualizada":"2026-10-23"}]}
```

### Claude

Encontré las dos series principales. Ahora traigo los resúmenes, la correlación y, como control, el IPC total.

### → Llama a `mcp__bcrp__resumen`

```json
{
 "codigo": "PN09822PM",
 "desde": "2021-01",
 "hasta": "2026-10"
}
```

### → Llama a `mcp__bcrp__resumen`

```json
{
 "codigo": "PD04722MM",
 "desde": "2021-01",
 "hasta": "2026-10"
}
```

#### ← Respuesta de la herramienta

```json
{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","frecuencia":"Mensual","desde":"2021-01","hasta":"2026-10","n":70,"primero":{"periodo":"2021-01","valor":3.6479},"ultimo":{"periodo":"2026-10","valor":5.2841},"cambio":1.6362,"variacion_pct":44.8535,"promedio":5.5041,"maximo":{"periodo":"2023-02","valor":13.1637},"minimo":{"periodo":"2025-03","valor":0.5904},"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10","web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN09822PM/html","nota":"La serie ya está en %: «cambio» está en puntos porcentuales."}
```

### → Llama a `mcp__bcrp__resumen`

```json
{
 "codigo": "PN01273PM",
 "desde": "2021-01",
 "hasta": "2026-10"
}
```

#### ← Respuesta de la herramienta

```json
{"codigo":"PD04722MM","nombre":"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria","frecuencia":"Mensual","desde":"2021-01","hasta":"2026-10","n":70,"primero":{"periodo":"2021-01","valor":0.25},"ultimo":{"periodo":"2026-10","valor":4.25},"cambio":4,"variacion_pct":1600,"promedio":4.7286,"maximo":{"periodo":"2023-01","valor":7.75},"minimo":{"periodo":"2021-01","valor":0.25},"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2021-1/2026-10","web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PD04722MM/html","nota":"La serie ya está en %: «cambio» está en puntos porcentuales."}
```

#### ← Respuesta de la herramienta

```json
{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","frecuencia":"Mensual","desde":"2021-01","hasta":"2026-10","n":70,"primero":{"periodo":"2021-01","valor":2.6755},"ultimo":{"periodo":"2026-10","valor":5.251},"cambio":2.5755,"variacion_pct":96.2593,"promedio":4.3147,"maximo":{"periodo":"2022-06","valor":8.8126},"minimo":{"periodo":"2025-08","valor":1.1063},"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2021-1/2026-10","web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN01273PM/html","nota":"La serie ya está en %: «cambio» está en puntos porcentuales."}
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

#### ← Respuesta de la herramienta

```json
{"serie_a":{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","n_datos":70,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10"},"serie_b":{"codigo":"PD04722MM","nombre":"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria","n_datos":70,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2021-1/2026-10"},"frecuencia":"Mensual","desde":"2021-01","hasta":"2026-10","rezago":0,"periodo_comun":{"primero":"2021-01","ultimo":"2026-10"},"n_pares":70,"r":0.4422,"fuerza":"moderada y positiva","brecha_media":0.7755,"periodos_a_mayor_que_b":35,"advertencia":"Correlación descriptiva entre dos series agregadas: no demuestra causalidad.","fuentes":["https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10","https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2021-1/2026-10"]}
```

### Claude

# Informe: inflación de alimentos y tasa de referencia en el Perú, 2021–2026

**Periodo:** enero 2021 a octubre 2026 (70 meses). Las cifras son de las herramientas del BCRP; no hay datos faltantes en las series usadas.

**Inflación de alimentos (IPC Alimentos y Bebidas, Lima Metropolitana, var. % 12 meses)**
- Serie `PN09822PM`. Pasó de 3,65 % en enero de 2021 a 5,28 % en octubre de 2026, un cambio de +1,64 puntos porcentuales.
- Máximo: 13,16 % en febrero de 2023. Mínimo: 0,59 % en marzo de 2025. Promedio del periodo: 5,50 %.
- Fuente: https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10
- Ficha web: https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN09822PM/html

**Tasa de referencia de la política monetaria (BCRP)**
- Serie `PD04722MM`. Pasó de 0,25 % en enero de 2021 a 4,25 % en octubre de 2026, un cambio de +4,00 puntos porcentuales.
- Máximo: 7,75 % en enero de 2023. Promedio del periodo: 4,73 %.
- Fuente: https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2021-1/2026-10
- Ficha web: https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PD04722MM/html

**Referencia: IPC total (var. % 12 meses)**
- Serie `PN01273PM`. Pasó de 2,68 % en enero de 2021 a 5,25 % en octubre de 2026, un cambio de +2,58 puntos porcentuales.
- Máximo: 8,81 % en junio de 2022. Mínimo: 1,11 % en agosto de 2025. Promedio del periodo: 4,31 %.
- Fuente: https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2021-1/2026-10
- Ficha web: https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN01273PM/html
- Nota: `buscar_series` no devolvió esta serie con mi búsqueda, así que usé el código directamente. Su nombre y datos sí se obtuvieron del BCRP.

**Co-movimiento entre inflación de alimentos y tasa de referencia**
- Correlación de Pearson r = 0,44 (moderada y positiva), con 70 pares, sin rezago.
- La inflación de alimentos estuvo por encima de la tasa de referencia en 35 de los 70 meses, con una brecha media de 0,78 puntos porcentuales.
- Esta es una correlación descriptiva entre dos series agregadas. No muestra que una cause a la otra.
- Fuentes: las dos series anteriores.

**Series usadas**

| Código | Nombre | Periodo |
|---|---|---|
| PN09822PM | IPC Alimentos y Bebidas, var. % 12 meses (Lima Metropolitana) | 2021-01 a 2026-10 |
| PD04722MM | Tasa de Referencia de la Política Monetaria (BCRP) | 2021-01 a 2026-10 |
| PN01273PM | IPC, var. % 12 meses (Lima Metropolitana) | 2021-01 a 2026-10 |

No leí las fichas en `bcrp://serie/{codigo}`, porque las descripciones de las herramientas bastaron para identificar las series.

## Resultado

- Turnos: 8
- Segundos: 17.7
- Costo informado por Claude Code: US$ 0.0031
- ¿Terminó con error?: False
