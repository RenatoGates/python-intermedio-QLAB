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
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

TAREA = Path(__file__).resolve().parents[2]
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


def ejecutar(prompt: str, internas: list[str], modelo: str) -> tuple[list[dict], float]:
    cmd = [shutil.which("claude"), "-p", prompt, "--model", modelo, "--output-format", "stream-json", "--verbose",
           "--no-session-persistence", "--strict-mcp-config", "--mcp-config", str(TAREA / ".mcp.json"),
           "--tools", ",".join(internas), "--allowedTools", "mcp__bcrp", *internas]
    t = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=TAREA, timeout=900)
    eventos = [json.loads(l) for l in proc.stdout.splitlines() if l.strip().startswith("{")]
    if proc.returncode:
        eventos.append({"type": "error", "stderr": proc.stderr[-2000:]})
    return eventos, round(time.time() - t, 1)


def _anonimizar(texto: str) -> str:
    return texto.replace(str(Path.home()), "~").replace(str(Path.home()).replace("\\", "/"), "~")


def a_markdown(nombre: str, prompt: str, internas: list[str], eventos: list[dict], segundos: float,
               modelo: str) -> str:
    md = [f"# MCP bcrp en Claude Code · caso «{nombre}»", "",
          f"Sesión nueva de `claude -p` con `--model {modelo}`, solo el servidor `bcrp` de `.mcp.json` "
          f"(`--strict-mcp-config --tools \"{','.join(internas)}\" --allowedTools mcp__bcrp {' '.join(internas)}`). "
          "Generado por `probar_en_claude_code.py`.", "", "## Pedido", "", "```text", prompt, "```", ""]
    for e in eventos:
        if e["type"] == "system" and e.get("subtype") == "init":
            servidores = ", ".join(f"{s['name']} ({s['status']})" for s in e.get("mcp_servers", []))
            herramientas = ", ".join(e.get("tools", []))
            md += [f"**Servidores MCP:** {servidores}  ", f"**Herramientas disponibles:** {herramientas}", ""]
        elif e["type"] == "assistant":
            for b in e["message"]["content"]:
                if b["type"] == "text" and b["text"].strip():
                    md += ["### Claude", "", b["text"].strip(), ""]
                elif b["type"] == "tool_use":
                    md += [f"### → Llama a `{b['name']}`", "", "```json",
                           json.dumps(b["input"], ensure_ascii=False, indent=1), "```", ""]
        elif e["type"] == "user":
            contenido = e.get("message", {}).get("content", [])
            for b in contenido if isinstance(contenido, list) else []:
                if b.get("type") == "tool_result":
                    c = b.get("content")
                    texto = c if isinstance(c, str) else "\n".join(x.get("text", "") for x in c or [])
                    error = " (error)" if b.get("is_error") else ""
                    md += [f"#### ← Respuesta de la herramienta{error}", "", "```json",
                           texto if len(texto) < 2500 else texto[:2500] + "\n… (recortado)", "```", ""]
        elif e["type"] == "result":
            md += ["## Resultado", "", f"- Turnos: {e.get('num_turns')}", f"- Segundos: {segundos}",
                   f"- Costo informado por Claude Code: US$ {e.get('total_cost_usd', 0):.4f}",
                   f"- ¿Terminó con error?: {e.get('is_error')}", ""]
        elif e["type"] == "error":
            md += ["## Error de la ejecución", "", "```text", e["stderr"], "```", ""]
    return _anonimizar("\n".join(md))


if __name__ == "__main__":
    modelo = sys.argv[1] if len(sys.argv) > 1 else "haiku"
    for nombre in sys.argv[2:] or CASOS:
        prompt, internas = CASOS[nombre]
        eventos, segundos = ejecutar(prompt, internas, modelo)
        destino = SALIDA / f"claude_code_{nombre}.md"
        destino.write_text(a_markdown(nombre, prompt, internas, eventos, segundos, modelo), encoding="utf-8")
        usadas = [b["name"] for e in eventos if e["type"] == "assistant"
                  for b in e["message"]["content"] if b["type"] == "tool_use"]
        print(f"{nombre}: {segundos} s, herramientas {usadas} -> {destino.name}")
