# MCP bcrp en Claude Code · caso «recurso», primer intento: sin las herramientas internas para leer recursos

Sesión nueva de `claude -p` con `--model haiku`, solo el servidor `bcrp` de `.mcp.json` (`--strict-mcp-config --tools "" --allowedTools mcp__bcrp`). Generado por `probar_en_claude_code.py`.

## Pedido

```text
@bcrp:bcrp://serie/PD04722MM ¿Qué mide esta serie, desde cuándo hay datos, quién la publica y dónde la puedo ver en la web del BCRP?
```

**Servidores MCP:** bcrp (connected), fetch (connected)  
**Herramientas disponibles:** mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie, mcp__fetch__fetch

### → Llama a `mcp__bcrp__buscar_series`

```json
{
 "texto": "tasa de referencia",
 "limite": 10
}
```

#### ← Respuesta de la herramienta

```json
{"result":[{"codigo":"PD12301MD","nombre":"Tasas de interés - Tasa de Referencia de la Política Monetaria","categoria":"Tasas de interés","frecuencia":"Diaria","inicio":"2003-09-05","actualizada":"2026-10-23"},{"codigo":"PD04722MM","nombre":"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria","categoria":"Tasas de interés","frecuencia":"Mensual","inicio":"Ene-2004","actualizada":"2026-10-15"},{"codigo":"PN07809NM","nombre":"Tasas de interés activas y pasivas promedio de las empresas bancarias en MN (términos efectivos anuales) - Activas - Preferencial Corporativa a 90 días","categoria":"Tasas de interés","frecuencia":"Mensual","inicio":"Ene-2011","actualizada":"2026-10-23"},{"codigo":"PN07829NM","nombre":"Tasas de interés activas y pasivas promedio de las empresas bancarias en ME (términos efectivos anuales) - Activas - Preferencial Corporativa a 90 días","categoria":"Tasas de interés","frecuencia":"Mensual","inicio":"Ene-2011","actualizada":"2026-10-23"}]}
```

### → Llama a `mcp__bcrp__resumen`

```json
{
 "codigo": "PD04722MM",
 "desde": "2000-01",
 "hasta": "2026-11"
}
```

#### ← Respuesta de la herramienta

```json
{"codigo":"PD04722MM","nombre":"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria","frecuencia":"Mensual","desde":"2000-01","hasta":"2026-11","n":278,"primero":{"periodo":"2003-09","valor":2.75},"ultimo":{"periodo":"2026-10","valor":4.25},"cambio":1.5,"variacion_pct":54.5455,"promedio":3.804,"maximo":{"periodo":"2023-01","valor":7.75},"minimo":{"periodo":"2020-04","valor":0.25},"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2000-1/2026-11","web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PD04722MM/html","nota":"La serie ya está en %: «cambio» está en puntos porcentuales."}
```

### → Llama a `mcp__bcrp__serie`

```json
{
 "codigo": "PD04722MM",
 "desde": "2003-01",
 "hasta": "2004-03"
}
```

#### ← Respuesta de la herramienta

```json
{"codigo":"PD04722MM","nombre":"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria","frecuencia":"Mensual","desde":"2003-01","hasta":"2004-03","n":7,"datos":[{"periodo":"2003-09","valor":2.75},{"periodo":"2003-10","valor":2.75},{"periodo":"2003-11","valor":2.5},{"periodo":"2003-12","valor":2.5},{"periodo":"2004-01","valor":2.5},{"periodo":"2004-02","valor":2.5},{"periodo":"2004-03","valor":2.5}],"fuente":"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2003-1/2004-3","web":"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PD04722MM/html"}
```

### Claude

**PD04722MM** es la **tasa de referencia de la política monetaria** del Banco Central de Reserva del Perú (BCRP), en porcentaje anual. Es la tasa de interés que el BCRP fija como guía para sus operaciones de política monetaria, y es el principal instrumento con el que controla la inflación.

- **Desde cuándo hay datos:** la serie mensual tiene su primer dato en **setiembre de 2003** (2,75 %), según la API. El buscador la lista desde "Ene-2004", pero los datos que devuelve la API empiezan antes. Tomo como válido el dato de la API. La serie diaria equivalente, PD12301MD, empieza el 5 de setiembre de 2003.
- **Último dato disponible:** octubre de 2026, en **4,25 %**. Actualizada el 15 de octubre de 2026 según el buscador.
- **Rango observado (2003-2026):** promedio de 3,80 %, máximo de 7,75 % en enero de 2023 y mínimo de 0,25 % en abril de 2020.
- **Quién la publica:** el Banco Central de Reserva del Perú, a través de su portal de Estadísticas (BCRP).
- **Dónde verla en la web:** https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PD04722MM/html

Fuente de la API usada: https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/2000-1/2026-11

No pude leer directamente el recurso `bcrp://serie/PD04722MM` porque no tengo una herramienta para abrir recursos. Obtuve la misma información con las herramientas de búsqueda y de datos.

## Resultado

- Turnos: 4
- Segundos: 12.7
- Costo informado por Claude Code: US$ 0.0018
- ¿Terminó con error?: False
