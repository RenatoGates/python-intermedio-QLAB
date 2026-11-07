"""Prueba las tres skills de la ENAHO dentro de Claude Code: activación por lenguaje natural, coordinación e
invocación directa.

    uv run evidencias_ia/skills/probar_skills.py                       # desde tarea_4/, todos los casos con Sonnet
    uv run evidencias_ia/skills/probar_skills.py haiku coordinacion    # un modelo y algunos casos

Cada caso es una sesión nueva de `claude -p` sin servidores MCP y con solo las herramientas que las skills necesitan
(Skill, Bash, Read, Glob). El caso «coordinacion» borra antes las bases procesadas de salidas/, para comprobar que
Claude corre limpiando-enaho antes de mapeando-enaho. El caso «desde_la_raiz» arranca en la raíz del repo para
mostrar que ahí se cargan las skills de la sesión 16, no las de tarea_4. Guarda una traza Markdown por caso.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from traza import TAREA, a_markdown, ejecutar, usadas  # noqa: E402

SALIDA = Path(__file__).parent
HERRAMIENTAS = ["--strict-mcp-config", "--tools", "Skill,Bash,Read,Glob", "--allowedTools", "Skill", "Bash", "Read",
                "Glob"]
PREGUNTA_VERSION = ("Usa la skill limpiando-enaho, pero no ejecutes ningún comando. Solo dime la ruta de «Base "
                    "directory» que te da la skill y con qué factor de expansión dice que se calcula la cifra oficial.")
CASOS = {   # nombre: (pedido, directorio de trabajo, borrar las bases antes)
    "coordinacion": ("Haz un mapa de la pobreza monetaria por departamento con ENAHO 2024.", TAREA, True),
    "lenguaje_natural": ("¿Los hogares donde viven adultos mayores gastan una parte mayor de su presupuesto en "
                         "alimentos? Compáralo con un gráfico, separando urbano y rural.", TAREA, False),
    "invocacion_directa": ("/limpiando-enaho 2024", TAREA, False),
    "desde_tarea_4": (PREGUNTA_VERSION, TAREA, False),
    "desde_la_raiz": (PREGUNTA_VERSION, TAREA.parent, False),
}


if __name__ == "__main__":
    modelo = sys.argv[1] if len(sys.argv) > 1 else "sonnet"
    for nombre in sys.argv[2:] or CASOS:
        prompt, cwd, borrar = CASOS[nombre]
        if borrar:
            for p in (TAREA / "salidas").glob("*.parquet"):
                p.unlink()
        antes = sorted(p.name for p in (TAREA / "salidas").glob("*.parquet"))
        eventos, segundos = ejecutar(prompt, HERRAMIENTAS, modelo, cwd=cwd)
        descripcion = (f"Sesión nueva de `claude -p --model {modelo}` arrancada en `{cwd.relative_to(TAREA.parent)}/`, "
                       "sin servidores MCP y con las herramientas Skill, Bash, Read y Glob. Bases procesadas en "
                       f"`salidas/` al empezar: {', '.join(antes) or 'ninguna'}. Generado por `probar_skills.py`.")
        destino = SALIDA / f"claude_code_{nombre}.md"
        destino.write_text(a_markdown(f"Skills de la ENAHO en Claude Code · caso «{nombre}»", descripcion, prompt,
                                      eventos, segundos), encoding="utf-8")
        print(f"{nombre}: {segundos} s, {usadas(eventos)} -> {destino.name}")
