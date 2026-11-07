"""Exporta la conversación de desarrollo con Claude Code (~/.claude/projects/<proyecto>/<sesión>.jsonl) a Markdown.

    uv run evidencias_ia/exportar_conversacion.py <ruta al .jsonl> [--ocultar texto ...]      # desde tarea_4/

--ocultar recibe cadenas que hay que borrar y que no pueden escribirse en este script porque se publica (por
ejemplo, la parte local del correo del autor); se reemplazan por «[omitido]».

Reparte la conversación según los mensajes del usuario: el primero y el segundo (lectura, Partes 0 y 1) van a mcp/,
el tercero (Parte 2) a skills/ y el cuarto (Partes 3 y 4) se parte en dos en el primer paso de la evaluación
(cuando se escribe evaluacion/verdades.py): lo anterior va a integracion/ y lo demás a evaluacion/.

Qué se omite y qué se oculta:
- los bloques de razonamiento interno, las imágenes (se reemplazan por «[imagen]») y los eventos internos de Claude
  Code (pedidos a la API, instantáneas de archivos);
- los avisos <system-reminder> que agrega el sistema a los mensajes;
- la carpeta personal (se reemplaza por «~»), el usuario de Windows, el correo y cualquier cadena con forma de token
  o clave. Al final se busca de nuevo y el script falla si queda algo.
"""
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).parent
CASA = Path.home()
USUARIO = CASA.name
PARTES = [   # (carpeta, archivo, título)
    ("mcp", "conversacion_01_lectura_y_plan.md", "Lectura del issue y plan de la Parte 1"),
    ("mcp", "conversacion_02_partes_0_y_1.md", "Partes 0 y 1: estructura y servidor MCP del BCRP"),
    ("skills", "conversacion_03_parte_2.md", "Parte 2: Skills de la ENAHO"),
    ("integracion", "conversacion_04_parte_3.md", "Parte 3: agente de investigación e informe"),
    ("evaluacion", "conversacion_05_parte_4.md", "Parte 4: evaluación, README y entrega"),
]
CORTE_EVALUACION = "evaluacion/verdades.py"
SECRETOS = [r"sk-ant-[A-Za-z0-9_-]{10,}", r"gh[pousr]_[A-Za-z0-9]{20,}", r"(?i)bearer\s+[A-Za-z0-9._-]{20,}",
            r"(?i)(api[_-]?key|token|password|contraseña)\s*[:=]\s*['\"]?[A-Za-z0-9._-]{16,}",
            r"(?<![\w.@])[A-Za-z0-9._%+-]{3,}@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.(com|pe|org|net|edu|io|dev)\b"]


OCULTAR: list[str] = []


def limpiar(texto: str) -> str:
    for cadena in OCULTAR:
        texto = re.sub(re.escape(cadena), "[omitido]", texto, flags=re.I)
    texto = re.sub(r"<system-reminder>.*?</system-reminder>", "", texto, flags=re.S)
    texto = re.sub(r"</?pasted_content[^>]*>", "", texto)
    for forma in (str(CASA), str(CASA).replace("\\", "/"), str(CASA).replace("\\", "\\\\"), f"/c/Users/{USUARIO}",
                  f"/C/Users/{USUARIO}", f"C--Users-{USUARIO}", f"c--Users-{USUARIO}"):
        texto = texto.replace(forma, "~")
    texto = re.sub(rf"\b{re.escape(USUARIO)}\b", "usuario", texto)
    texto = re.sub(r"(?<![\w.])[A-Za-z0-9._%+-]+@(gmail|hotmail|outlook|yahoo)\.[a-z.]+", "[correo omitido]", texto)
    for patron in SECRETOS[:4]:
        texto = re.sub(patron, "[secreto omitido]", texto)
    return texto.strip()


def recortar(texto: str, n: int) -> str:
    return texto if len(texto) <= n else texto[:n] + f"\n… (recortado: {len(texto) - n:,} caracteres más)"


def bloque(texto: str, lenguaje: str = "text") -> str:
    return f"```{lenguaje}\n{texto.replace('```', 'ˋˋˋ')}\n```"


def resultado_texto(contenido) -> str:
    if isinstance(contenido, str):
        return contenido
    partes = []
    for b in contenido or []:
        partes.append(b.get("text", "") if b.get("type") == "text" else f"[{b.get('type', 'bloque')}]".replace(
            "[image]", "[imagen]"))
    return "\n".join(partes)


def entrada_herramienta(nombre: str, entrada: dict) -> str:
    e = dict(entrada)
    for campo in ("content", "new_string", "old_string"):
        if isinstance(e.get(campo), str) and len(e[campo]) > 1500:
            e[campo] = e[campo][:1500] + f"… (recortado; el archivo completo está en el repo)"
    return recortar(json.dumps(e, ensure_ascii=False, indent=1), 4000)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    argumentos = sys.argv[1:]
    origen = Path(argumentos[0])
    if "--ocultar" in argumentos:
        OCULTAR.extend(argumentos[argumentos.index("--ocultar") + 1:])
    eventos = [json.loads(l) for l in origen.read_text(encoding="utf-8").splitlines() if l.strip()]
    eventos = [e for e in eventos if e.get("type") in ("user", "assistant") and not e.get("isSidechain")]

    md_por_parte, parte, turno_usuario = {i: [] for i in range(len(PARTES))}, 0, 0
    for e in eventos:
        contenido = e["message"].get("content")
        contenido = [{"type": "text", "text": contenido}] if isinstance(contenido, str) else contenido or []
        es_pedido = e["type"] == "user" and not e.get("isMeta") and any(
            b.get("type") == "text" and limpiar(b["text"]) for b in contenido)
        if es_pedido:
            turno_usuario += 1
            parte = min(turno_usuario - 1, 3)
        salida = md_por_parte[parte]
        for b in contenido:
            t = b.get("type")
            if t == "text" and e["type"] == "user":
                texto = limpiar(b["text"])
                if not texto:
                    continue
                if e.get("isMeta"):
                    salida.append(f"<details><summary>Contenido inyectado por Claude Code (skill o comando)"
                                  f"</summary>\n\n{bloque(recortar(texto, 1200))}\n</details>\n")
                else:
                    salida.append(f"## Usuario · {e.get('timestamp', '')[:16].replace('T', ' ')} UTC\n\n{texto}\n")
            elif t == "text":
                if limpiar(b["text"]):
                    salida.append(f"### Claude\n\n{limpiar(b['text'])}\n")
            elif t == "tool_use":
                if parte == 3 and CORTE_EVALUACION in json.dumps(b.get("input", {})):
                    parte = 4
                    salida = md_por_parte[parte]
                salida.append(f"**→ {b['name']}**\n\n{bloque(limpiar(entrada_herramienta(b['name'], b['input'])), 'json')}\n")
            elif t == "tool_result":
                texto = limpiar(recortar(resultado_texto(b.get("content")), 2500))
                estado = " (error)" if b.get("is_error") else ""
                salida.append(f"<details><summary>← Resultado{estado}</summary>\n\n{bloque(texto)}\n</details>\n")
            # thinking, redacted_thinking e imágenes sueltas se omiten a propósito

    escritos = []
    for i, (carpeta, archivo, titulo) in enumerate(PARTES):
        cuerpo = "\n".join(md_por_parte[i])
        cabecera = (f"# Conversación con Claude Code · {titulo}\n\nExportada de la sesión `{origen.stem}` con "
                    "`evidencias_ia/exportar_conversacion.py`. Se muestran los mensajes del usuario, las respuestas "
                    "de Claude, cada herramienta con sus argumentos y su resultado (recortados si son largos). Se "
                    "omiten el razonamiento interno, las imágenes y los avisos del sistema; la carpeta personal "
                    "aparece como «~».\n\n")
        destino = AQUI / carpeta / archivo
        destino.parent.mkdir(exist_ok=True)
        destino.write_text(cabecera + cuerpo + "\n", encoding="utf-8")
        escritos.append(destino)

    problemas = []
    for p in AQUI.rglob("*.md"):
        texto = p.read_text(encoding="utf-8")
        for patron in SECRETOS:
            for m in re.finditer(patron, texto):
                if not m.group(0).endswith(("@anthropic.com", "noreply@anthropic.com")):
                    problemas.append(f"{p.relative_to(AQUI)}: {m.group(0)[:40]}")
        if str(CASA) in texto or f"Users\\{USUARIO}" in texto or f"Users/{USUARIO}" in texto or re.search(
                rf"\b{re.escape(USUARIO)}\b", texto):
            problemas.append(f"{p.relative_to(AQUI)}: ruta o usuario personal")
        for cadena in OCULTAR:
            if cadena.lower() in texto.lower():
                problemas.append(f"{p.relative_to(AQUI)}: una cadena de --ocultar")
    for d in escritos:
        print(f"{d.relative_to(AQUI)}: {d.stat().st_size / 1024:.0f} KB")
    if problemas:
        print("QUEDAN DATOS SENSIBLES:\n  " + "\n  ".join(sorted(set(problemas))), file=sys.stderr)
        return 1
    print("Revisión: sin tokens, claves, correos ni rutas personales en evidencias_ia/*.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
