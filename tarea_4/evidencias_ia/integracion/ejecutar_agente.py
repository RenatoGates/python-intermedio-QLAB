"""Parte 3: corre el agente de investigación en UNA sesión de Claude Code y guarda la traza.

    uv run evidencias_ia/integracion/ejecutar_agente.py            # desde tarea_4/, con Opus
    uv run evidencias_ia/integracion/ejecutar_agente.py sonnet

Equivale a abrir `claude` dentro de tarea_4/ y pegar el contenido de pedido_agente.md. La sesión tiene el servidor
bcrp de .mcp.json, las skills de tarea_4/.claude/skills/ y las herramientas que necesitan (Skill, Bash, Read, Write,
Edit, Glob, Grep y el lector de recursos MCP). Antes borra las bases procesadas de salidas/ para que la cadena
limpiando -> graficando -> mapeando corra completa. Deja la traza en ejecucion_agente.md y un resumen en
bitacora.json (herramientas MCP y skills usadas, en orden).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from traza import TAREA, a_markdown, ejecutar, usadas  # noqa: E402

AQUI = Path(__file__).parent
HERRAMIENTAS = ["Skill", "Bash", "Read", "Write", "Edit", "Glob", "Grep", "ListMcpResourcesTool",
                "ReadMcpResourceTool"]

if __name__ == "__main__":
    modelo = sys.argv[1] if len(sys.argv) > 1 else "opus"
    pedido = (AQUI / "pedido_agente.md").read_text(encoding="utf-8")
    for p in (TAREA / "salidas").glob("*.parquet"):
        p.unlink()
    opciones = ["--strict-mcp-config", "--mcp-config", str(TAREA / ".mcp.json"), "--tools", ",".join(HERRAMIENTAS),
                "--allowedTools", "mcp__bcrp", *HERRAMIENTAS]
    eventos, segundos = ejecutar(pedido, opciones, modelo, timeout=3600)
    descripcion = (f"Una sola sesión de `claude -p --model {modelo}` arrancada en `tarea_4/`, con el servidor `bcrp` "
                   "de `.mcp.json`, las skills de `tarea_4/.claude/skills/` y las herramientas "
                   f"{', '.join(HERRAMIENTAS)}. Antes se borraron las bases procesadas de `salidas/`. "
                   "Generado por `ejecutar_agente.py`; el pedido completo está en `pedido_agente.md`.")
    (AQUI / "ejecucion_agente.md").write_text(
        a_markdown("Parte 3 · Ejecución del agente de investigación", descripcion, pedido, eventos, segundos),
        encoding="utf-8")
    orden = usadas(eventos)
    final = next((e for e in eventos if e["type"] == "result"), {})
    bitacora = {
        "modelo": modelo, "segundos": segundos, "turnos": final.get("num_turns"),
        "costo_usd": final.get("total_cost_usd"), "termino_con_error": final.get("is_error"),
        "herramientas_mcp": sorted({h for h in orden if h.startswith("mcp__")}),
        "skills": sorted({h[6:-1] for h in orden if h.startswith("Skill(")}),
        "recursos_leidos": [b["input"] for e in eventos if e["type"] == "assistant" for b in e["message"]["content"]
                            if b["type"] == "tool_use" and b["name"] == "ReadMcpResourceTool"],
        "orden_de_llamadas": orden,
    }
    (AQUI / "bitacora.json").write_text(json.dumps(bitacora, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in bitacora.items() if k != "orden_de_llamadas"}, ensure_ascii=False, indent=1))
    print("Informe:", "sí" if (TAREA / "informes" / "informe_final.md").exists() else "NO se escribió")
