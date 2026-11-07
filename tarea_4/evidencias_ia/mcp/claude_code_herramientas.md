# MCP bcrp en Claude Code · caso «herramientas»

Sesión nueva de `claude -p` con `--model haiku`, solo el servidor `bcrp` de `.mcp.json` (`--strict-mcp-config --tools "" --allowedTools mcp__bcrp`). Generado por `probar_en_claude_code.py`.

## Pedido

```text
¿Estuvo la inflación de alimentos y bebidas de Lima Metropolitana (var% 12 meses) por encima de la inflación total entre enero de 2021 y octubre de 2026? Dime en cuántos meses y con qué brecha media, y si se mueven juntas. Cita el código de cada serie, el periodo y la fuente.
```

**Servidores MCP:** bcrp (connected), fetch (connected)  
**Herramientas disponibles:** mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie, mcp__fetch__fetch

### → Llama a `mcp__bcrp__buscar_series`

```json
{
 "texto": "inflación alimentos bebidas Lima Metropolitana 12 meses",
 "frecuencia": "Mensual"
}
```

#### ← Respuesta de la herramienta

```json
{"result":[{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN09823PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC sin Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN09824PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Subyacente Sin Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01285PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC No Transables Sin Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"}]}
```

### → Llama a `mcp__bcrp__buscar_series`

```json
{
 "texto": "ipc total Lima Metropolitana 12 meses",
 "frecuencia": "Mensual"
}
```

#### ← Respuesta de la herramienta

```json
{"result":[]}
```

### → Llama a `mcp__bcrp__buscar_series`

```json
{
 "texto": "índice de precios Lima Metropolitana var% 12 meses",
 "frecuencia": "Mensual",
 "limite": 20
}
```

#### ← Respuesta de la herramienta

```json
{"result":[{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1950","actualizada":"2026-10-08"},{"codigo":"PN09821PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Importado","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1992","actualizada":"2026-10-08"},{"codigo":"PN01279PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Subyacente","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01281PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Transables","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01283PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC No Transables","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN09820PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC No Subyacente","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1992","actualizada":"2026-10-08"},{"codigo":"PN09819PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Energía","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1992","actualizada":"2026-10-08"},{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01277PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Sin Alimentos y Energía","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN09823PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC sin Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01287PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - Índice de Precios al por Mayor","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN09824PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Subyacente Sin Alimentos y Bebidas","categoria":"Inflación","frecuencia":"Mensual","inicio":"Ene-1993","actualizada":"2026-10-08"},{"codigo":"PN01285PM","nombre":"Índ
… (recortado)
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

### → Llama a `mcp__bcrp__serie`

```json
{
 "codigo": "PN09822PM",
 "desde": "2021-01",
 "hasta": "2026-10"
}
```

### → Llama a `mcp__bcrp__serie`

```json
{
 "codigo": "PN01273PM",
 "desde": "2021-01",
 "hasta": "2026-10"
}
```

#### ← Respuesta de la herramienta

```json
{"serie_a":{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","n_datos":70,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10"},"serie_b":{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","n_datos":70,"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2021-1/2026-10"},"frecuencia":"Mensual","desde":"2021-01","hasta":"2026-10","rezago":0,"periodo_comun":{"primero":"2021-01","ultimo":"2026-10"},"n_pares":70,"r":0.9719,"fuerza":"fuerte y positiva","brecha_media":1.1894,"periodos_a_mayor_que_b":48,"advertencia":"Correlación descriptiva entre dos series agregadas: no demuestra causalidad.","fuentes":["https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10","https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2021-1/2026-10"]}
```

#### ← Respuesta de la herramienta

```json
{"codigo":"PN09822PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas","frecuencia":"Mensual","desde":"2021-01","hasta":"2026-10","n":70,"datos":[{"periodo":"2021-01","valor":3.647883},{"periodo":"2021-02","valor":2.709591},{"periodo":"2021-03","valor":2.662516},{"periodo":"2021-04","valor":1.998537},{"periodo":"2021-05","valor":2.063084},{"periodo":"2021-06","valor":3.664199},{"periodo":"2021-07","valor":4.18221},{"periodo":"2021-08","valor":6.104404},{"periodo":"2021-09","valor":6.880188},{"periodo":"2021-10","valor":7.535421},{"periodo":"2021-11","valor":6.701316},{"periodo":"2021-12","valor":7.971768},{"periodo":"2022-01","valor":6.832302},{"periodo":"2022-02","valor":7.895463},{"periodo":"2022-03","valor":9.17079},{"periodo":"2022-04","valor":11.780447},{"periodo":"2022-05","valor":11.128732},{"periodo":"2022-06","valor":11.908077},{"periodo":"2022-07","valor":11.590067},{"periodo":"2022-08","valor":11.442274},{"periodo":"2022-09","valor":11.680472},{"periodo":"2022-10","valor":11.263292},{"periodo":"2022-11","valor":11.972881},{"periodo":"2022-12","valor":12.643878},{"periodo":"2023-01","valor":12.925689},{"periodo":"2023-02","valor":13.163747},{"periodo":"2023-03","valor":12.806134},{"periodo":"2023-04","valor":12.146838},{"periodo":"2023-05","valor":13.071412},{"periodo":"2023-06","valor":10.923059},{"periodo":"2023-07","valor":10.305129},{"periodo":"2023-08","valor":9.676248},{"periodo":"2023-09","valor":8.291618},{"periodo":"2023-10","valor":7.009034},{"periodo":"2023-11","valor":5.600995},{"periodo":"2023-12","valor":4.804398},{"periodo":"2024-01","valor":4.279338},{"periodo":"2024-02","valor":4.443157},{"periodo":"2024-03","valor":3.677233},{"periodo":"2024-04","valor":2.086929},{"periodo":"2024-05","valor":0.835569},{"periodo":"2024-06","valor":1.416042},{"periodo":"2024-07","valor":1.01659},{"periodo":"2024-08","valor":0.959976},{"periodo":"2024-09","valor":0.68766},{"periodo":"2024-10","valor":1.434122},{"periodo":"2024-11","valor":2.091899},{"periodo":"2024-12","valor":1.248148},{"periodo":"2025-01","valor":1.092188},{"periodo":"2025-02","valor":0.614078},{"periodo":"2025-03","valor":0.590405},{"periodo":"2025-04","valor":1.609884},{"periodo":"2025-05","valor":1.866184},{"periodo":"2025-06","valor":1.979161},{"periodo":"2025-07","valor":2.074672},{"periodo":"2025-08","valor":0.911684},{"periodo":"2025-09","valor":1.435211},{"periodo":"2025-10","valor":1.526596},{"periodo":"2025-11","valor":1.779705},
… (recortado)
```

#### ← Respuesta de la herramienta

```json
{"codigo":"PN01273PM","nombre":"Índice de precios Lima Metropolitana (var% 12 meses) - IPC","frecuencia":"Mensual","desde":"2021-01","hasta":"2026-10","n":70,"datos":[{"periodo":"2021-01","valor":2.675545},{"periodo":"2021-02","valor":2.401342},{"periodo":"2021-03","valor":2.598185},{"periodo":"2021-04","valor":2.383698},{"periodo":"2021-05","valor":2.447459},{"periodo":"2021-06","valor":3.254607},{"periodo":"2021-07","valor":3.814599},{"periodo":"2021-08","valor":4.952805},{"periodo":"2021-09","valor":5.229575},{"periodo":"2021-10","valor":5.82601},{"periodo":"2021-11","valor":5.655148},{"periodo":"2021-12","valor":6.430387},{"periodo":"2022-01","valor":5.684917},{"periodo":"2022-02","valor":6.147044},{"periodo":"2022-03","valor":6.824089},{"periodo":"2022-04","valor":7.964653},{"periodo":"2022-05","valor":8.091139},{"periodo":"2022-06","valor":8.812633},{"periodo":"2022-07","valor":8.740835},{"periodo":"2022-08","valor":8.397988},{"periodo":"2022-09","valor":8.529853},{"periodo":"2022-10","valor":8.275195},{"periodo":"2022-11","valor":8.44723},{"periodo":"2022-12","valor":8.459162},{"periodo":"2023-01","valor":8.664267},{"periodo":"2023-02","valor":8.645924},{"periodo":"2023-03","valor":8.400574},{"periodo":"2023-04","valor":7.965046},{"periodo":"2023-05","valor":7.893886},{"periodo":"2023-06","valor":6.461497},{"periodo":"2023-07","valor":5.881601},{"periodo":"2023-08","valor":5.576147},{"periodo":"2023-09","valor":5.044546},{"periodo":"2023-10","valor":4.343081},{"periodo":"2023-11","valor":3.636475},{"periodo":"2023-12","valor":3.237383},{"periodo":"2024-01","valor":3.023922},{"periodo":"2024-02","valor":3.294067},{"periodo":"2024-03","valor":3.045046},{"periodo":"2024-04","valor":2.422076},{"periodo":"2024-05","valor":2.004938},{"periodo":"2024-06","valor":2.285382},{"periodo":"2024-07","valor":2.127664},{"periodo":"2024-08","valor":2.034097},{"periodo":"2024-09","valor":1.775011},{"periodo":"2024-10","valor":2.00918},{"periodo":"2024-11","valor":2.271991},{"periodo":"2024-12","valor":1.966303},{"periodo":"2025-01","valor":1.851583},{"periodo":"2025-02","valor":1.477329},{"periodo":"2025-03","valor":1.27718},{"periodo":"2025-04","valor":1.651834},{"periodo":"2025-05","valor":1.686663},{"periodo":"2025-06","valor":1.693709},{"periodo":"2025-07","valor":1.688801},{"periodo":"2025-08","valor":1.106331},{"periodo":"2025-09","valor":1.358393},{"periodo":"2025-10","valor":1.351775},{"periodo":"2025-11","valor":1.368613},{"periodo":"2025-12","valor":1.5088}
… (recortado)
```

### Claude

**Respuesta corta:** sí, la inflación de alimentos y bebidas estuvo por encima de la inflación total en **48 de los 70 meses** (enero 2021 a octubre 2026). La brecha media fue de **+1,19 puntos porcentuales**, y las dos series se mueven muy juntas (r = 0,97).

**Series y fuente**
- Alimentos y bebidas: **PN09822PM**, "Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas".
- Inflación total: **PN01273PM**, "Índice de precios Lima Metropolitana (var% 12 meses) - IPC".
- Fuente: Banco Central de Reserva del Perú (BCRP), Estadísticas del BCRP. Datos descargados por la API:
  - https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN09822PM/json/2021-1/2026-10
  - https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01273PM/json/2021-1/2026-10

**Resultados**
- Periodo comparado: 2021-01 a 2026-10, 70 pares de datos.
- Meses con alimentos por encima del total: 48 de 70.
- Brecha media (alimentos − total): +1,19 pp.
- Correlación de Pearson: r = 0,97, fuerte y positiva.

**Tendencia**
- En 2022 y 2023 la brecha fue muy amplia. Alimentos llegó a 13,2% en febrero de 2023, mientras el total estuvo en torno a 8,6%.
- Desde mediados de 2024 la brecha se redujo y en varios meses el total quedó por encima. Por ejemplo, en 2024-05 alimentos estuvo en 0,84% y el total en 2,00%.
- En 2026 la inflación de alimentos volvió a subir por encima del total en febrero y marzo, pero entre abril y septiembre quedó por debajo. En octubre de 2026 volvió a superar al total, 5,28% frente a 5,25%, por una diferencia mínima.

Las dos series se mueven juntas, pero la correlación describe solo co-movimiento entre series agregadas; no demuestra que una cause a la otra.

## Resultado

- Turnos: 7
- Segundos: 25.1
- Costo informado por Claude Code: US$ 0.0046
- ¿Terminó con error?: False
