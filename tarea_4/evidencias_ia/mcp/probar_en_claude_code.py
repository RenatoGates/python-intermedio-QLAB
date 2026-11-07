"""Prueba el MCP bcrp dentro de Claude Code: una herramienta, el recurso con @ y el prompt con /.

    uv run evidencias_ia/mcp/probar_en_claude_code.py                     # desde tarea_4/, los tres casos con Haiku
    uv run evidencias_ia/mcp/probar_en_claude_code.py haiku recurso       # un modelo y algunos casos

Cada caso es una sesión nueva de `claude -p` que solo tiene el servidor bcrp de .mcp.json (sin terminal, sin
archivos, sin web). Guarda la traza de cada caso en Markdown junto a este script: qué herramientas llamó Claude,
con qué argumentos, qué recibió y qué respondió.

En modo -p la mención @bcrp:bcrp://... no adjunta el recurso por sí sola: Claude lo lee con las herramientas
internas ListMcpResourcesTool y ReadMcpResourceTool, que `--tools ""` apaga. Por eso el caso «recurso» las habilita
(claude_code_recurso_sin_lector_de_recursos.md es el primer intento, sin ellas).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from traza import TAREA, a_markdown, ejecutar, usadas  # noqa: E402

SALIDA = Path(__file__).parent
LECTOR_DE_RECURSOS = ["ListMcpResourcesTool", "ReadMcpResourceTool"]
CASOS = {   # nombre: (pedido, herramientas internas de Claude Code que se habilitan además del MCP)
    "herramientas": ("¿Estuvo la inflación de alimentos y bebidas de Lima Metropolitana (var% 12 meses) por encima "
                     "de la inflación total entre enero de 2021 y octubre de 2026? Dime en cuántos meses y con qué "
                     "brecha media, y si se mueven juntas. Cita el código de cada serie, el periodo y la fuente.", []),
    "recurso": ("@bcrp:bcrp://serie/PD04722MM ¿Qué mide esta serie, desde cuándo hay datos, quién la publica y "
                "dónde la puedo ver en la web del BCRP? Responde con lo que dice su ficha.", LECTOR_DE_RECURSOS),
    "prompt": ("/mcp__bcrp__informe \"inflación de alimentos y tasa de referencia, 2021-2026\"", []),
}


if __name__ == "__main__":
    modelo = sys.argv[1] if len(sys.argv) > 1 else "haiku"
    for nombre in sys.argv[2:] or CASOS:
        prompt, internas = CASOS[nombre]
        opciones = ["--strict-mcp-config", "--mcp-config", str(TAREA / ".mcp.json"), "--tools", ",".join(internas),
                    "--allowedTools", "mcp__bcrp", *internas]
        eventos, segundos = ejecutar(prompt, opciones, modelo)
        descripcion = (f"Sesión nueva de `claude -p --model {modelo}` arrancada en `tarea_4/`, solo con el servidor "
                       f"`bcrp` de `.mcp.json` (`--strict-mcp-config --tools \"{','.join(internas)}\" --allowedTools "
                       f"mcp__bcrp {' '.join(internas)}`). Generado por `probar_en_claude_code.py`.")
        destino = SALIDA / f"claude_code_{nombre}.md"
        destino.write_text(a_markdown(f"MCP bcrp en Claude Code · caso «{nombre}»", descripcion, prompt, eventos,
                                      segundos), encoding="utf-8")
        print(f"{nombre}: {segundos} s, {usadas(eventos)} -> {destino.name}")
