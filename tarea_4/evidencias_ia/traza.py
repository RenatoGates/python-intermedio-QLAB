"""Corre `claude -p` en una sesión nueva y pasa su traza (stream-json) a Markdown legible.

Lo usan los scripts de evidencias_ia/*/ para dejar constancia de qué herramientas, skills y servidores MCP usó
Claude, con qué argumentos, qué recibió y qué respondió. Las rutas de la carpeta personal se reemplazan por «~».
"""
import json
import shutil
import subprocess
import time
from pathlib import Path

TAREA = Path(__file__).resolve().parents[1]
RECORTE = 2500


def ejecutar(prompt: str, opciones: list[str], modelo: str, cwd: Path = TAREA,
             timeout: int = 1800) -> tuple[list[dict], float]:
    cmd = [shutil.which("claude"), "-p", prompt, "--model", modelo, "--output-format", "stream-json", "--verbose",
           "--no-session-persistence", *opciones]
    t = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=cwd, timeout=timeout)
    eventos = [json.loads(l) for l in proc.stdout.splitlines() if l.strip().startswith("{")]
    if proc.returncode:
        eventos.append({"type": "error", "stderr": proc.stderr[-2000:]})
    return eventos, round(time.time() - t, 1)


def anonimizar(texto: str) -> str:
    casa = str(Path.home())
    for forma in (casa, casa.replace("\\", "/"), casa.replace("\\", "\\\\"), "/c/Users/" + Path.home().name):
        texto = texto.replace(forma, "~")
    return texto


def _bloque(texto: str, lenguaje: str = "text") -> list[str]:
    texto = texto if len(texto) < RECORTE else texto[:RECORTE] + "\n… (recortado)"
    return [f"```{lenguaje}", texto.replace("```", "ˋˋˋ"), "```", ""]


def usadas(eventos: list[dict]) -> list[str]:
    """Las herramientas que llamó Claude, en orden; las skills como Skill(nombre)."""
    out = []
    for e in eventos:
        if e["type"] == "assistant":
            for b in e["message"]["content"]:
                if b["type"] == "tool_use":
                    out.append(f"Skill({b['input'].get('skill')})" if b["name"] == "Skill" else b["name"])
    return out


def a_markdown(titulo: str, descripcion: str, prompt: str, eventos: list[dict], segundos: float) -> str:
    md = [f"# {titulo}", "", descripcion, "", "## Pedido", "", *_bloque(prompt)]
    for e in eventos:
        if e["type"] == "system" and e.get("subtype") == "init":
            servidores = ", ".join(f"{s['name']} ({s['status']})" for s in e.get("mcp_servers", [])) or "ninguno"
            md += [f"**Modelo:** {e.get('model')}  ", f"**Directorio:** `{anonimizar(e.get('cwd', ''))}`  ",
                   f"**Servidores MCP:** {servidores}  ", f"**Herramientas:** {', '.join(e.get('tools', []))}", ""]
        elif e["type"] == "assistant":
            for b in e["message"]["content"]:
                if b["type"] == "text" and b["text"].strip():
                    md += ["### Claude", "", b["text"].strip(), ""]
                elif b["type"] == "tool_use":
                    md += [f"### → Llama a `{b['name']}`", "", *_bloque(json.dumps(b["input"], ensure_ascii=False,
                                                                                   indent=1), "json")]
        elif e["type"] == "user":
            contenido = e.get("message", {}).get("content", [])
            if isinstance(contenido, str):
                contenido = [{"type": "text", "text": contenido}]
            for b in contenido:
                if b.get("type") == "tool_result":
                    c = b.get("content")
                    texto = c if isinstance(c, str) else "\n".join(x.get("text", "") for x in c or [])
                    md += [f"#### ← Resultado{' (error)' if b.get('is_error') else ''}", "", *_bloque(texto)]
                elif b.get("type") == "text" and b["text"].strip():
                    md += ["#### ← Contenido que Claude Code inyecta (p. ej., el SKILL.md al cargar una skill)", "",
                           *_bloque(b["text"].strip()[:900] + ("\n… (recortado)" if len(b["text"]) > 900 else ""))]
        elif e["type"] == "result":
            md += ["## Resultado", "", f"- Herramientas, en orden: {', '.join(usadas(eventos)) or 'ninguna'}",
                   f"- Turnos: {e.get('num_turns')}", f"- Segundos: {segundos}",
                   f"- Costo informado por Claude Code: US$ {e.get('total_cost_usd', 0):.4f}",
                   f"- ¿Terminó con error?: {e.get('is_error')}", ""]
        elif e["type"] == "error":
            md += ["## Error de la ejecución", "", *_bloque(e["stderr"])]
    return anonimizar("\n".join(md))
