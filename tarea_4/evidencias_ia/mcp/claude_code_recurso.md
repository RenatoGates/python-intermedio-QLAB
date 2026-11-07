# MCP bcrp en Claude Code · caso «recurso»

Sesión nueva de `claude -p` con `--model haiku`, solo el servidor `bcrp` de `.mcp.json` (`--strict-mcp-config --tools "ListMcpResourcesTool,ReadMcpResourceTool" --allowedTools mcp__bcrp ListMcpResourcesTool ReadMcpResourceTool`). Generado por `probar_en_claude_code.py`.

## Pedido

```text
@bcrp:bcrp://serie/PD04722MM ¿Qué mide esta serie, desde cuándo hay datos, quién la publica y dónde la puedo ver en la web del BCRP? Responde con lo que dice su ficha.
```

**Servidores MCP:** bcrp (connected), fetch (connected)  
**Herramientas disponibles:** ListMcpResourcesTool, ReadMcpResourceTool, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie, mcp__fetch__fetch

### → Llama a `ReadMcpResourceTool`

```json
{
 "server": "bcrp",
 "uri": "bcrp://serie/PD04722MM"
}
```

#### ← Respuesta de la herramienta

```json
{"contents":[{"uri":"bcrp://serie/PD04722MM","mimeType":"application/json","text":"{\n \"codigo\": \"PD04722MM\",\n \"nombre\": \"Tasas de interés del Banco Central de Reserva - Tasa de Referencia de la Política Monetaria\",\n \"categoria\": \"Tasas de interés\",\n \"frecuencia\": \"Mensual\",\n \"inicio\": \"Ene-2004\",\n \"actualizada\": \"2026-10-15\",\n \"grupo\": \"Tasas de interés del Banco Central de Reserva\",\n \"origen_de_los_datos\": \"BCRP\",\n \"area_que_publica\": \"Departamento de Estadísticas Monetarias\",\n \"web\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PD04722MM/html\",\n \"api\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04722MM/json/{desde}/{hasta}\",\n \"catalogo\": \"https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata\"\n}"}]}
```

### Claude

**PD04722MM** según su ficha en el BCRP:

- **Qué mide:** la tasa de referencia de la política monetaria del Banco Central de Reserva del Perú. La ficha solo da el nombre ("Tasa de Referencia de la Política Monetaria") y no incluye una descripción más detallada.
- **Desde cuándo hay datos:** desde enero de 2004 (Ene-2004). Es una serie mensual y se actualizó por última vez el 2026-10-15.
- **Quién la publica:** el origen de los datos es el BCRP. El área que la publica es el Departamento de Estadísticas Monetarias. Pertenece a la categoría Tasas de interés, dentro del grupo "Tasas de interés del Banco Central de Reserva".
- **Dónde verla:** en la web de estadísticas del BCRP, en https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PD04722MM/html. El catálogo general de series está en https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata.

## Resultado

- Turnos: 2
- Segundos: 8.5
- Costo informado por Claude Code: US$ 0.0022
- ¿Terminó con error?: False
