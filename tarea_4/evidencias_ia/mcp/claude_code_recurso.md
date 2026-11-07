# MCP bcrp en Claude Code · caso «recurso»

Sesión nueva de `claude -p --model haiku` arrancada en `tarea_4/`, solo con el servidor `bcrp` de `.mcp.json` (`--strict-mcp-config --tools "ListMcpResourcesTool,ReadMcpResourceTool" --allowedTools mcp__bcrp ListMcpResourcesTool ReadMcpResourceTool`). Generado por `probar_en_claude_code.py`.

## Pedido

```text
@bcrp:bcrp://serie/PD04722MM ¿Qué mide esta serie, desde cuándo hay datos, quién la publica y dónde la puedo ver en la web del BCRP? Responde con lo que dice su ficha.
```

**Modelo:** claude-haiku-5-5  
**Directorio:** `~\Documentos\GitHub\python-intermedio-QLAB\tarea_4`  
**Servidores MCP:** bcrp (connected), fetch (connected)  
**Herramientas:** ListMcpResourcesTool, ReadMcpResourceTool, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__resumen, mcp__bcrp__serie, mcp__fetch__fetch

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

### Claude

**PD04722MM** es la *Tasa de Referencia de la Política Monetaria*, del grupo "Tasas de interés del Banco Central de Reserva", categoría "Tasas de interés". Su frecuencia es mensual.

- **Qué mide:** la ficha solo dice el nombre de la serie. No incluye una descripción más detallada, así que no puedo citar de la ficha cómo se define la tasa.
- **Desde cuándo hay datos:** desde enero de 2004 (Ene-2004). La ficha indica que se actualizó por última vez el 2026-10-15.
- **Quién la publica:** el BCRP. El área que publica es el Departamento de Estadísticas Monetarias, y el origen de los datos es BCRP.
- **Dónde verla:** en la versión web del portal de estadísticas, en https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PD04722MM/html. El catálogo general de series está en https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata.

## Resultado

- Herramientas, en orden: ReadMcpResourceTool
- Turnos: 2
- Segundos: 8.6
- Costo informado por Claude Code: US$ 0.0011
- ¿Terminó con error?: False
