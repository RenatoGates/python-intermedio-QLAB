"""¿Inventa cifras Claude? Las mismas 10 preguntas sin herramientas y con el MCP y las Skills, contra la cifra oficial.

    uv run evaluacion/evaluar.py --paralelo 2                     # desde tarea_4/: memoria y mcp_skills, con Haiku
    uv run evaluacion/evaluar.py --modos memoria mcp_skills web --modelo sonnet

Adaptado de sessions/04-mcp-claude-code/proyecto/evaluar.py para la tarea 4:
- el modo con herramientas se llama mcp_skills y tiene, además del MCP bcrp, lo que las Skills necesitan;
- cada llamada es una sesión nueva de `claude -p` que corre con cwd = tarea_4/ (ahí están .mcp.json y las skills,
  y `uv run mcp/server.py` resuelve);
- la traza sale en stream-json, de donde se leen las herramientas usadas y los errores;
- las preguntas combinadas solo cuentan como correctas si la cifra está en tolerancia Y la fuente cita a la vez la
  ENAHO (o el INEI) y el BCRP.
Escribe evaluacion/resultados.csv.
"""
import argparse
import json
import re
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).parent
TAREA = AQUI.parent
ESQUEMA = {"type": "object", "required": ["valor", "fuente"],
           "properties": {"valor": {"type": ["number", "null"]}, "unidad": {"type": "string"},
                          "fuente": {"type": "string"}}}
INSTRUCCION = ("Responde con un solo número en «valor», en la unidad que pide la pregunta. Si no puedes saberlo "
               "con certeza, pon valor null: no estimes. En «fuente» di de dónde sale la cifra; si combinas varias "
               "fuentes, nómbralas todas.\n\n")
CON_HERRAMIENTAS = ["Bash", "Read", "Write", "Glob", "Skill"]
MODOS = {   # la tabla de comparacion.md describe exactamente estas opciones
    "memoria": ["--tools", "", "--strict-mcp-config"],
    "mcp_skills": ["--tools", ",".join(CON_HERRAMIENTAS), "--strict-mcp-config", "--mcp-config",
                   str(TAREA / ".mcp.json"), "--allowedTools", "mcp__bcrp", *CON_HERRAMIENTAS],
    "web": ["--tools", "WebSearch,WebFetch", "--allowedTools", "WebSearch,WebFetch", "--strict-mcp-config"],
}


def _leer_traza(stdout: str) -> tuple[dict, list[str], list[str]]:
    """El evento final, las herramientas usadas en orden y los errores de herramientas."""
    eventos = [json.loads(l) for l in stdout.splitlines() if l.strip().startswith("{")]
    final = next((e for e in reversed(eventos) if e.get("type") == "result"), {})
    nombres, usadas, errores = {}, [], []
    for e in eventos:
        contenido = e.get("message", {}).get("content", []) if e.get("type") in ("assistant", "user") else []
        for b in contenido if isinstance(contenido, list) else []:
            if b.get("type") == "tool_use":
                nombre = f"Skill({b['input'].get('skill')})" if b["name"] == "Skill" else b["name"]
                nombres[b["id"]] = nombre
                usadas.append(nombre)
            elif b.get("type") == "tool_result" and b.get("is_error"):
                c = b.get("content")
                texto = c if isinstance(c, str) else " ".join(x.get("text", "") for x in c or [])
                errores.append(f"{nombres.get(b.get('tool_use_id'), '?')}: {texto.strip()[:160]}")
    return final, usadas, errores


def preguntar(pregunta: str, modo: str, modelo: str) -> dict:
    cmd = [shutil.which("claude"), "-p", INSTRUCCION + pregunta, "--output-format", "stream-json", "--verbose",
           "--json-schema", json.dumps(ESQUEMA), "--no-session-persistence", "--model", modelo, *MODOS[modo]]
    t = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=900, cwd=TAREA)
        final, usadas, errores = _leer_traza(proc.stdout)
        if proc.returncode:
            errores.append(f"claude terminó con código {proc.returncode}: {proc.stderr.strip()[-200:]}")
    except subprocess.TimeoutExpired:
        final, usadas, errores = {}, [], ["sin respuesta en 900 s"]
    if final.get("is_error"):
        errores.append(f"resultado con error: {final.get('subtype')}")
    for d in final.get("permission_denials") or []:
        errores.append(f"permiso denegado: {d.get('tool_name')}")
    r = final.get("structured_output") or {}
    if not r:
        errores.append("sin respuesta estructurada")
    return {"respuesta_generada": r.get("valor"), "unidad_generada": r.get("unidad", ""),
            "fuente": r.get("fuente", final.get("result", "")), "herramientas_usadas": " > ".join(usadas),
            "segundos": round(time.time() - t, 1), "turnos": final.get("num_turns"),
            "costo_usd": final.get("total_cost_usd"), "errores": " | ".join(errores)}


def calificar(valor, q) -> str:
    if valor is None:
        return "no sabe"
    if abs(valor - q.verdad) > q.tolerancia:
        return "se equivoca"
    return "acierta"


def calificar_fuente(resultado: str, q, fuente: str) -> str:
    if resultado == "acierta" and q.tipo == "combinada" and not (
            re.search(r"ENAHO|INEI", fuente or "", re.I) and re.search(r"BCRP", fuente or "", re.I)):
        return "se equivoca (fuente incompleta)"
    return resultado


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--modos", nargs="+", default=["memoria", "mcp_skills"], choices=list(MODOS))
    p.add_argument("--modelo", default="haiku")
    p.add_argument("--preguntas", default=str(AQUI / "preguntas.csv"))
    p.add_argument("--salida", default=str(AQUI / "resultados.csv"))
    p.add_argument("--paralelo", type=int, default=2)
    a = p.parse_args()
    if "mcp_skills" in a.modos and not (TAREA / ".mcp.json").exists():
        raise SystemExit("Falta .mcp.json en tarea_4/. Conecten su servidor: claude mcp add --scope project bcrp -- "
                         "uv run mcp/server.py")

    preguntas = pd.read_csv(a.preguntas)
    casos = [(q, m) for q in preguntas.itertuples() for m in a.modos]
    print(f"{len(casos)} llamadas a claude -p con {a.modelo}, {a.paralelo} en paralelo...")
    with ThreadPoolExecutor(a.paralelo) as ex:
        respuestas = list(ex.map(lambda c: preguntar(c[0].pregunta, c[1], a.modelo), casos))

    filas = []
    for (q, m), r in zip(casos, respuestas):
        resultado = calificar_fuente(calificar(r["respuesta_generada"], q), q, r["fuente"])
        filas.append({"id": q.id, "tipo": q.tipo, "modo": m, "pregunta": q.pregunta, "respuesta_esperada": q.verdad,
                      "tolerancia": q.tolerancia, **r, "correcto": resultado == "acierta", "resultado": resultado})
    res = pd.DataFrame(filas)
    res.to_csv(a.salida, index=False, encoding="utf-8")

    print("\n" + res.pivot(index="id", columns="modo", values="respuesta_generada").to_string())
    tabla = res.groupby("modo").resultado.value_counts().unstack(fill_value=0)
    tabla["segundos"] = res.groupby("modo").segundos.mean().round(1)
    print("\n" + tabla.to_string())
