"""¿Inventa cifras Claude? Las mismas 10 preguntas sin herramientas y con el MCP y las Skills, contra la cifra oficial.

    uv run evaluacion/evaluar.py --paralelo 2                     # desde tarea_4/: memoria y mcp_skills, con Haiku
    uv run evaluacion/evaluar.py --modos memoria mcp_skills web --modelo sonnet

Adaptado de sessions/04-mcp-claude-code/proyecto/evaluar.py para la tarea 4:
- el modo con herramientas se llama mcp_skills y tiene, además del MCP bcrp, lo que las Skills necesitan;
- cada pregunta es una sesión nueva de `claude -p`;
- las sesiones corren en una COPIA AISLADA de tarea_4/ fuera del repo, sin .git, sin evidencias_ia/ y sin los
  archivos con las respuestas (preguntas*.csv, resultados*.csv, verdades.py, comparacion.md), para que el modo con
  herramientas no pueda leer la clave de respuestas. La copia tiene el mismo código, los mismos datos y las salidas
  de las skills, y se borra al terminar;
- la traza sale en stream-json: de ahí se leen las herramientas usadas (con su argumento) y los errores, y cada
  sesión se guarda en evidencias_ia/evaluacion/sesiones/;
- las preguntas combinadas solo cuentan como correctas si la cifra está en tolerancia Y la fuente cita a la vez la
  ENAHO (o el INEI) y el BCRP.
Escribe evaluacion/resultados.csv.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).parent
TAREA = AQUI.parent
sys.path.insert(0, str(TAREA / "evidencias_ia"))
from traza import a_markdown, anonimizar  # noqa: E402

ESQUEMA = {"type": "object", "required": ["valor", "fuente"],
           "properties": {"valor": {"type": ["number", "null"]}, "unidad": {"type": "string"},
                          "fuente": {"type": "string"}}}
INSTRUCCION = ("Responde con un solo número en «valor», en la unidad que pide la pregunta. Si no puedes saberlo "
               "con certeza, pon valor null: no estimes. En «fuente» di de dónde sale la cifra; si combinas varias "
               "fuentes, nómbralas todas.\n\n")
CON_HERRAMIENTAS = ["Bash", "Read", "Write", "Glob", "Skill"]
MODOS = {   # {copia} es la copia aislada de tarea_4/; comparacion.md describe exactamente estas opciones
    "memoria": ["--tools", "", "--strict-mcp-config"],
    "mcp_skills": ["--tools", ",".join(CON_HERRAMIENTAS), "--strict-mcp-config", "--mcp-config", "{copia}/.mcp.json",
                   "--allowedTools", "mcp__bcrp", *CON_HERRAMIENTAS],
    "web": ["--tools", "WebSearch,WebFetch", "--allowedTools", "WebSearch,WebFetch", "--strict-mcp-config"],
}
NO_SE_COPIA = (".venv", "__pycache__", ".pytest_cache", "evidencias_ia", "preguntas*.csv", "resultados*.csv",
               "verdades.py", "comparacion.md")
COPIA_EN_TEXTO = re.compile(r"(~|[A-Za-z]:|/[a-z])[\\/]+(Users[\\/]+[^\\/]+[\\/]+)?AppData[\\/]+Local[\\/]+Temp[\\/]+"
                            r"evaluacion_tarea4_[^\\/\s\"']+[\\/]+tarea_4", re.I)
# archivos con respuestas, evidencias o historial de git, buscados sobre el texto ya limpio: la carpeta temporal se
# llama «evaluacion_tarea4_…» y la web del BCRP tiene «/resultados/» en sus URL, y eso no cuenta
SOSPECHOSO = re.compile(r"preguntas\w*\.csv|resultados\w*\.csv|verdades\.py|comparacion\.md|evidencias_ia|"
                        r"\.git\b|git (show|log|grep)", re.I)


def limpiar(texto: str) -> str:
    """Anonimiza y reemplaza la ruta de la copia temporal por «<copia>/tarea_4»."""
    return COPIA_EN_TEXTO.sub("<copia>/tarea_4", anonimizar(texto))


def preparar_copia() -> Path:
    copia = Path(tempfile.mkdtemp(prefix="evaluacion_tarea4_")) / "tarea_4"
    shutil.copytree(TAREA, copia, ignore=shutil.ignore_patterns(*NO_SE_COPIA))
    subprocess.run([shutil.which("uv"), "sync", "--quiet"], cwd=copia, check=True)
    return copia


def _resumen_entrada(nombre: str, entrada: dict) -> str:
    if nombre == "Bash":
        arg = entrada.get("command", "")
    elif nombre == "Read":
        arg = entrada.get("file_path", "")
    elif nombre == "Glob":
        arg = entrada.get("pattern", "")
    elif nombre == "Skill":
        arg = entrada.get("skill", "")
    else:
        arg = json.dumps(entrada, ensure_ascii=False)
    arg = re.sub(r"\s+", " ", limpiar(str(arg)))
    return f"{nombre}({arg[:90]}{'…' if len(arg) > 90 else ''})"


def _leer_traza(stdout: str) -> tuple[list[dict], dict, list[str], list[str], bool]:
    """Eventos, el evento final, las herramientas usadas (con su argumento), los errores y si tocó archivos de la
    evaluación."""
    eventos = [json.loads(l) for l in stdout.splitlines() if l.strip().startswith("{")]
    final = next((e for e in reversed(eventos) if e.get("type") == "result"), {})
    nombres, usadas, errores, sospechoso = {}, [], [], False
    for e in eventos:
        contenido = e.get("message", {}).get("content", []) if e.get("type") in ("assistant", "user") else []
        for b in contenido if isinstance(contenido, list) else []:
            if b.get("type") == "tool_use":
                nombres[b["id"]] = b["name"]
                if b["name"] != "StructuredOutput":          # es el mecanismo de --json-schema, no una herramienta
                    usadas.append(_resumen_entrada(b["name"], b.get("input", {})))
                    sospechoso |= bool(SOSPECHOSO.search(limpiar(json.dumps(b.get("input", {}), ensure_ascii=False))))
            elif b.get("type") == "tool_result" and b.get("is_error"):
                c = b.get("content")
                texto = c if isinstance(c, str) else " ".join(x.get("text", "") for x in c or [])
                errores.append(f"{nombres.get(b.get('tool_use_id'), '?')}: {texto.strip()[:160]}")
    return eventos, final, usadas, errores, sospechoso


def preguntar(pregunta: str, modo: str, modelo: str, copia: Path) -> dict:
    opciones = [x.replace("{copia}", str(copia)) for x in MODOS[modo]]
    cmd = [shutil.which("claude"), "-p", INSTRUCCION + pregunta, "--output-format", "stream-json", "--verbose",
           "--json-schema", json.dumps(ESQUEMA), "--no-session-persistence", "--model", modelo, *opciones]
    t = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=900, cwd=copia)
        eventos, final, usadas, errores, sospechoso = _leer_traza(proc.stdout)
        if proc.returncode:
            errores.append(f"claude terminó con código {proc.returncode}: {proc.stderr.strip()[-200:]}")
    except subprocess.TimeoutExpired:
        eventos, final, usadas, errores, sospechoso = [], {}, [], ["sin respuesta en 900 s"], False
    if final.get("is_error"):
        errores.append(f"resultado con error: {final.get('subtype')}")
    for d in final.get("permission_denials") or []:
        errores.append(f"permiso denegado: {d.get('tool_name')}")
    r = final.get("structured_output") or {}
    if not r:
        errores.append("sin respuesta estructurada")
    return {"respuesta_generada": r.get("valor"), "unidad_generada": r.get("unidad", ""),
            "fuente": limpiar(str(r.get("fuente", final.get("result", "")))),
            "herramientas_usadas": " > ".join(usadas), "segundos": round(time.time() - t, 1),
            "turnos": final.get("num_turns"), "costo_usd": final.get("total_cost_usd"),
            "errores": limpiar(" | ".join(errores)), "toco_archivos_de_evaluacion": sospechoso, "_eventos": eventos}


def recalcular_banderas(salida: Path) -> None:
    """Recalcula toco_archivos_de_evaluacion desde las trazas guardadas (las entradas de herramientas), sin volver a
    correr las sesiones. Las respuestas y su calificación no cambian."""
    res = pd.read_csv(salida)
    sesiones = TAREA / "evidencias_ia" / "evaluacion" / "sesiones"
    banderas = []
    for r in res.itertuples():
        md = (sesiones / f"{r.modo}__{r.id}.md").read_text(encoding="utf-8")
        entradas = re.findall(r"### → Llama a `[^`]+`\n\n```json\n(.*?)\n```", md, re.S)
        banderas.append(any(SOSPECHOSO.search(e) for e in entradas))
    res["toco_archivos_de_evaluacion"] = banderas
    res.to_csv(salida, index=False, encoding="utf-8")
    print(f"Sesiones que tocaron archivos con respuestas, evidencias o git: {sum(banderas)} de {len(banderas)}")


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
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("--modos", nargs="+", default=["memoria", "mcp_skills"], choices=list(MODOS))
    p.add_argument("--modelo", default="haiku")
    p.add_argument("--preguntas", default=str(AQUI / "preguntas.csv"))
    p.add_argument("--salida", default=str(AQUI / "resultados.csv"))
    p.add_argument("--paralelo", type=int, default=2)
    p.add_argument("--recalcular-banderas", action="store_true",
                   help="solo recalcula toco_archivos_de_evaluacion desde las trazas guardadas")
    a = p.parse_args()
    if a.recalcular_banderas:
        recalcular_banderas(Path(a.salida))
        raise SystemExit(0)
    if "mcp_skills" in a.modos and not (TAREA / ".mcp.json").exists():
        raise SystemExit("Falta .mcp.json en tarea_4/. Conecten su servidor: claude mcp add --scope project bcrp -- "
                         "uv run mcp/server.py")

    preguntas = pd.read_csv(a.preguntas)
    casos = [(q, m) for q in preguntas.itertuples() for m in a.modos]
    copia = preparar_copia()
    print(f"Copia aislada (sin .git ni respuestas): {limpiar(str(copia))}")
    print(f"{len(casos)} llamadas a claude -p con {a.modelo}, {a.paralelo} en paralelo...")
    try:
        with ThreadPoolExecutor(a.paralelo) as ex:
            respuestas = list(ex.map(lambda c: preguntar(c[0].pregunta, c[1], a.modelo, copia), casos))
    finally:
        shutil.rmtree(copia.parent, ignore_errors=True)

    sesiones = TAREA / "evidencias_ia" / "evaluacion" / "sesiones"
    sesiones.mkdir(parents=True, exist_ok=True)
    filas = []
    for (q, m), r in zip(casos, respuestas):
        eventos = r.pop("_eventos")
        (sesiones / f"{m}__{q.id}.md").write_text(limpiar(a_markdown(
            f"Evaluación · {q.id} · modo {m}", f"Sesión nueva de `claude -p --model {a.modelo}` en la copia aislada de "
            f"tarea_4/, con las opciones del modo `{m}` (ver evaluacion/comparacion.md). Respuesta esperada: "
            f"{q.verdad} ± {q.tolerancia}.", INSTRUCCION + q.pregunta, eventos, r["segundos"])), encoding="utf-8")
        resultado = calificar_fuente(calificar(r["respuesta_generada"], q), q, r["fuente"])
        filas.append({"id": q.id, "tipo": q.tipo, "modo": m, "pregunta": q.pregunta, "respuesta_esperada": q.verdad,
                      "tolerancia": q.tolerancia, **r, "correcto": resultado == "acierta", "resultado": resultado})
    res = pd.DataFrame(filas)
    res.to_csv(a.salida, index=False, encoding="utf-8")

    print("\n" + res.pivot(index="id", columns="modo", values="respuesta_generada").to_string())
    tabla = res.groupby("modo").resultado.value_counts().unstack(fill_value=0)
    tabla["segundos"] = res.groupby("modo").segundos.mean().round(1)
    print("\n" + tabla.to_string())
    print(f"\nSesiones que tocaron archivos de la evaluación: {int(res.toco_archivos_de_evaluacion.sum())}")
