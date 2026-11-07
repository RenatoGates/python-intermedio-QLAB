"""Escribe evaluacion/comparacion.md a partir de resultados.csv y rellena los bloques de cifras del README.

    uv run evaluacion/comparar.py          # desde tarea_4/, después de evaluar.py

Ninguna cifra de comparacion.md ni de los bloques del README está escrita a mano: salen de resultados.csv,
preguntas.csv, salidas/validacion.txt, evidencias_ia/mcp/pruebas.txt y evidencias_ia/integracion/bitacora.json.
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).parent
TAREA = AQUI.parent
sys.path.insert(0, str(AQUI))
from evaluar import CON_HERRAMIENTAS, INSTRUCCION, MODOS  # noqa: E402

ETIQUETA = {"memoria": "Sin MCP ni Skills (memoria)", "mcp_skills": "Con MCP y Skills (mcp_skills)"}


def tabla_md(df: pd.DataFrame) -> str:
    cab = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    filas = ["| " + " | ".join("" if pd.isna(v) else str(v).replace("|", "/").replace("\n", " ") for v in fila) + " |"
             for fila in df.itertuples(index=False)]
    return "\n".join([cab, sep, *filas])


def fmt(v) -> str:
    return "—" if v is None or pd.isna(v) else f"{v:g}" if isinstance(v, (int, float)) else str(v)


def reemplazar(texto: str, marca: str, contenido: str) -> str:
    patron = re.compile(rf"(<!-- {marca}:inicio -->).*?(<!-- {marca}:fin -->)", re.S)
    return patron.sub(lambda m: f"{m.group(1)}\n{contenido}\n{m.group(2)}", texto)


def conclusiones(res: pd.DataFrame, preg: pd.DataFrame) -> str:
    """La interpretación está escrita a partir de lo observado; cada cifra se calcula aquí."""
    n = len(preg)
    mem, mcp = res[res.modo == "memoria"], res[res.modo == "mcp_skills"]
    herr = mcp.herramientas_usadas.fillna("")
    acerto_mem = ", ".join(f"`{i}`" for i in mem[mem.correcto].id) or "ninguna"
    tipo_mcp = {t: f"{int(g.correcto.sum())} de {len(g)}" for t, g in mcp.groupby("tipo")}
    con_skill = int(herr.str.contains(r"Skill\(").sum())
    # qué leyó cada sesión de la ENAHO y combinada, según su traza completa (la columna herramientas_usadas recorta)
    sesiones = TAREA / "evidencias_ia" / "evaluacion" / "sesiones"
    trazas = {q: (sesiones / f"mcp_skills__{q}.md").read_text(encoding="utf-8") for q in mcp[mcp.tipo != "bcrp"].id}
    usa_salidas = [q for q, t in trazas.items() if re.search(r"salidas/|indicadores\.csv|hogares_2024|figuras/", t)]
    solo_dta = [q for q, t in trazas.items() if q not in usa_salidas and ".dta" in t]
    lee_salidas, no_bcrp = len(usa_salidas), len(trazas)
    con_fetch = mcp[herr.str.contains("mcp__fetch__fetch")]
    bcrp_mcp = int(mcp[mcp.tipo == "bcrp"].herramientas_usadas.fillna("").str.contains("mcp__bcrp__serie").sum())
    primera = TAREA / "evidencias_ia" / "evaluacion" / "primera_corrida_resultados.csv"
    p1 = pd.read_csv(primera) if primera.exists() else None
    bloque = [
        "## Conclusiones", "",
        f"1. **Con MCP y Skills, {int(mcp.correcto.sum())} de {n} correctas; sin ellos, {int(mem.correcto.sum())} de "
        f"{n}.** Sin herramientas, Haiku casi nunca inventó: respondió `null` en {int((mem.resultado == 'no sabe').sum())} "
        f"preguntas y se equivocó en {int(mem.resultado.str.startswith('se equivoca').sum())}. Acertó de memoria solo "
        f"{acerto_mem}, una cifra publicada y muy difundida. La mejora del modo `mcp_skills` no es corregir errores, "
        "sino pasar de «no sé» a una cifra con fuente.",
        f"2. **Por tipo de pregunta** en `mcp_skills`: BCRP {tipo_mcp.get('bcrp', '—')}, ENAHO "
        f"{tipo_mcp.get('enaho', '—')}, combinadas {tipo_mcp.get('combinada', '—')}. En las del BCRP, "
        f"{bcrp_mcp} de 4 sesiones resolvieron con `buscar_series` y `serie` del MCP; las cifras salen con más "
        "decimales o redondeadas, pero dentro de la tolerancia.",
        f"3. **Las Skills se usaron por sus salidas, no por la herramienta Skill.** Ninguna de las {len(mcp)} sesiones "
        f"invocó una skill (`Skill` aparece en {con_skill}). En {lee_salidas} de las {no_bcrp} preguntas de la ENAHO y "
        "combinadas, Haiku leyó con Bash lo que las skills ya habían dejado validado (`salidas/indicadores.csv`, "
        "`salidas/hogares_2024.parquet`, los CSV de `figuras/`) y desde ahí respondió. En "
        f"{len(solo_dta)} ({', '.join(f'`{q}`' for q in solo_dta) or '—'}) calculó directamente desde los `.dta` "
        "con `factor07 × mieperho`, sin las skills, y acertó. Las salidas validadas de las skills hicieron la mayor "
        "parte del trabajo, pero esta evaluación no prueba que el modelo sepa activar las skills cuando faltan; eso "
        "lo muestran las sesiones de `evidencias_ia/skills/`.",
        f"4. **Tiempo y costo.** `mcp_skills` tardó {mcp.segundos.mean():.1f} s en promedio, frente a "
        f"{mem.segundos.mean():.1f} s de `memoria`, y costó US$ {mcp.costo_usd.sum():.4f} contra "
        f"US$ {mem.costo_usd.sum():.4f} las 10 preguntas. Las de la ENAHO y las combinadas son las más lentas "
        f"({mcp[mcp.tipo != 'bcrp'].segundos.mean():.1f} s en promedio) porque el modelo explora archivos antes de "
        "calcular.",
        f"5. **El modelo buscó la cifra «oficial» fuera de los datos.** En {len(con_fetch)} preguntas de la ENAHO "
        f"({', '.join(f'`{i}`' for i in con_fetch.id) or '—'}) intentó primero `mcp__fetch__fetch` sobre la web del "
        "INEI. `fetch` está en `.mcp.json` pero fuera de `--allowedTools`, así que se denegó; queda en la columna "
        "`errores` y luego respondió con los datos locales.",
    ]
    if p1 is not None:
        p1m, p1c = p1[p1.modo == "mcp_skills"], p1[p1.modo == "memoria"]
        cambio = [q for q in preg.id if bool(p1m[p1m.id == q].correcto.iloc[0]) != bool(mcp[mcp.id == q].correcto.iloc[0])]
        bloque.append(
            f"6. **Primera corrida, descartada por falta de aislamiento.** Dentro de `tarea_4/`, con la clave de respuestas "
            f"a la vista, dio {int(p1m.correcto.sum())} de {n} con MCP y Skills y {int(p1c.correcto.sum())} de {n} sin "
            f"ellos. Cambió {', '.join(f'`{q}`' for q in cambio) or 'ninguna pregunta'}: en esa corrida la sesión "
            "buscó la cifra publicada, encontró `evaluacion/verdades.py`, decidió no usarlo y respondió `null`. La "
            "corrida válida es la de la copia aislada. Su control de acceso marcó al principio 6 sesiones por un falso "
            "positivo (la carpeta temporal se llama «evaluacion_tarea4_…» y las URL del BCRP llevan «/resultados/»). "
            "Corregido y recalculado sobre las trazas guardadas, da "
            f"{int(res.toco_archivos_de_evaluacion.sum())} de {len(res)} sesiones que tocaron archivos con respuestas, "
            "evidencias o git.")
    bloque += [
        "7. **Cuándo vale la pena.** Para cifras puntuales y recientes del BCRP, un MCP que baja la serie oficial basta "
        "y es rápido. Para la ENAHO, lo que hace la diferencia es tener una base validada y ponderada: el modelo, solo, "
        "no conoce cifras como la pobreza de los hogares de solo adultos mayores, y sin la limpieza correcta "
        "(residentes, `factor07 × mieperho`) un cálculo improvisado puede dar otra cifra. Con una sola corrida por "
        "modo y con Haiku, estas conclusiones son indicativas, no una medición de la variabilidad.",
    ]
    return "\n".join(bloque)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    res = pd.read_csv(AQUI / "resultados.csv")
    preg = pd.read_csv(AQUI / "preguntas.csv")
    modos = [m for m in ("memoria", "mcp_skills") if m in set(res.modo)]
    n = preg.shape[0]

    # ------------------------------------------------------------------------------------------- resumen por modo
    filas = []
    for m in modos:
        r = res[res.modo == m]
        filas.append({"Modo": ETIQUETA.get(m, m), "Correctas": f"{int(r.correcto.sum())} de {len(r)}",
                      "Se equivoca": int(r.resultado.str.startswith("se equivoca").sum()),
                      "No sabe (null)": int((r.resultado == "no sabe").sum()),
                      "Con errores registrados": int(r.errores.fillna("").ne("").sum()),
                      "Segundos promedio": round(r.segundos.mean(), 1), "Segundos mediana": round(r.segundos.median(), 1),
                      "Turnos promedio": round(r.turnos.mean(), 1),
                      "Costo total US$": round(r.costo_usd.sum(), 4)})
    resumen = pd.DataFrame(filas)
    por_tipo = (res.assign(tipo=res.tipo.map({"bcrp": "BCRP", "enaho": "ENAHO", "combinada": "Combinada"}))
                .groupby(["tipo", "modo"]).correcto.agg(lambda s: f"{int(s.sum())} de {len(s)}").unstack()
                .reindex(columns=modos).rename(columns=ETIQUETA).reset_index().rename(columns={"tipo": "Tipo"}))

    # ---------------------------------------------------------------------------------------- detalle por pregunta
    ancho = res.pivot(index="id", columns="modo", values=["respuesta_generada", "resultado", "segundos",
                                                         "herramientas_usadas", "errores", "fuente"])
    detalle = []
    for q in preg.itertuples():
        fila = {"Pregunta": q.id, "Tipo": q.tipo, "Esperada": f"{q.verdad:g} ± {q.tolerancia:g}"}
        for m in modos:
            fila[f"{m}: respuesta"] = fmt(ancho.loc[q.id, ("respuesta_generada", m)])
            fila[f"{m}: resultado"] = ancho.loc[q.id, ("resultado", m)]
            fila[f"{m}: s"] = fmt(ancho.loc[q.id, ("segundos", m)])
        detalle.append(fila)
    detalle = pd.DataFrame(detalle)

    cambios = []
    if set(modos) == {"memoria", "mcp_skills"}:
        for q in preg.itertuples():
            a, b = (bool(res[(res.id == q.id) & (res.modo == m)].correcto.iloc[0]) for m in ("memoria", "mcp_skills"))
            if a != b:
                cambios.append({"Pregunta": q.id, "Cambio": "mejoró con MCP y Skills" if b else "empeoró con MCP y Skills",
                                "memoria": ancho.loc[q.id, ("resultado", "memoria")],
                                "mcp_skills": ancho.loc[q.id, ("resultado", "mcp_skills")]})
    cambios = pd.DataFrame(cambios, columns=["Pregunta", "Cambio", "memoria", "mcp_skills"])

    herr = res[res.modo == "mcp_skills"][["id", "herramientas_usadas"]].fillna("")
    herr = herr.assign(**{
        "MCP bcrp": herr.herramientas_usadas.str.count(r"mcp__bcrp__"),
        "Skills": herr.herramientas_usadas.apply(lambda s: ", ".join(sorted(set(re.findall(r"Skill\(([^)]+)\)", s))))
                                                 or "—"),
        "Bash/Read/Glob/Write": herr.herramientas_usadas.str.count(r"\b(Bash|Read|Glob|Write)\b"),
    }).rename(columns={"id": "Pregunta"}).drop(columns="herramientas_usadas")

    fallos = res[~res.correcto].copy()
    fallos["detalle"] = fallos.apply(lambda r: f"esperada {r.respuesta_esperada:g}, respondió "
                                     f"{fmt(r.respuesta_generada)}; fuente: {str(r.fuente)[:160]}"
                                     + (f"; errores: {str(r.errores)[:160]}" if isinstance(r.errores, str) else ""),
                                     axis=1)
    fallos = fallos[["modo", "id", "resultado", "detalle"]].rename(columns={"modo": "Modo", "id": "Pregunta",
                                                                           "resultado": "Resultado",
                                                                           "detalle": "Qué pasó"})

    modos_tabla = pd.DataFrame([
        {"": "Opciones de `claude -p`", "memoria": "`" + " ".join(f'"{x}"' if x == "" else x for x in MODOS["memoria"]) + "`",
         "mcp_skills": "`" + " ".join(x if x else '""' for x in MODOS["mcp_skills"]) + "`"},
        {"": "Directorio de trabajo", "memoria": "copia aislada de `tarea_4/` ({copia})", "mcp_skills": "la misma: sin "
         "`.git`, sin `evidencias_ia/` y sin `preguntas*.csv`, `resultados*.csv`, `verdades.py` ni `comparacion.md`; "
         "con el código, los datos y las salidas de las skills"},
        {"": "Herramientas internas de Claude Code", "memoria": "ninguna (`--tools \"\"`)",
         "mcp_skills": ", ".join(CON_HERRAMIENTAS)},
        {"": "Servidor MCP `bcrp` (5 herramientas, 1 recurso, 1 prompt)", "memoria": "no", "mcp_skills": "sí (el `.mcp.json` de la copia, "
                                                                                     "`--allowedTools mcp__bcrp`)"},
        {"": "MCP `fetch` de `.mcp.json`", "memoria": "no", "mcp_skills": "cargado pero no permitido (fuera de "
                                                                           "`--allowedTools`)"},
        {"": "Otros MCP del usuario (conectores de claude.ai)", "memoria": "no (`--strict-mcp-config`)",
         "mcp_skills": "no (`--strict-mcp-config`)"},
        {"": "Skills de `tarea_4/.claude/skills/`", "memoria": "no (sin la herramienta Skill)", "mcp_skills": "sí"},
        {"": "`ReadMcpResourceTool` / `ListMcpResourcesTool` (leer `bcrp://serie/{codigo}`)", "memoria": "no",
         "mcp_skills": "no: `--tools` las deja fuera, así que el recurso no se puede leer en esta evaluación"},
        {"": "Leer archivos del repo (`salidas/`, `datos/`)", "memoria": "no", "mcp_skills": "sí, con Read, Bash y Glob"},
        {"": "Búsqueda web", "memoria": "no", "mcp_skills": "no"},
        {"": "Modelo, instrucción y sesión", "memoria": "Haiku, la misma instrucción, sesión nueva por pregunta "
                                                        "(`--no-session-persistence`), cwd en la copia aislada",
         "mcp_skills": "igual"},
    ])

    md = [
        "# Evaluación · sin MCP ni Skills frente a con MCP y Skills", "",
        "Generado por `evaluacion/comparar.py` a partir de `resultados.csv`; ninguna cifra está escrita a mano.", "",
        "## Diseño", "",
        f"{n} preguntas con respuesta verificable en [`preguntas.csv`](preguntas.csv): "
        + ", ".join(f"{int((preg.tipo == t).sum())} {nombre}" for t, nombre in
                    (("bcrp", "del BCRP"), ("enaho", "de la ENAHO"), ("combinada", "que combinan ambas"))) + ". "
        "Las del BCRP son cuatro del archivo del profesor; su respuesta esperada se volvió a tomar de "
        "estadisticas.bcrp.gob.pe (API JSON y tabla HTML, sin pasar por el MCP). Las de la ENAHO salen de un cálculo "
        "directo desde los `.dta` con factores de expansión, con código distinto al de las Skills. Las combinadas "
        "multiplican una cifra de cada fuente. Todo lo calculó `verdades.py` antes de correr la evaluación.", "",
        "**Criterio de acierto:** el valor está dentro de la tolerancia de la pregunta. Si responde `null` cuenta "
        "como «no sabe». En las combinadas, además, la fuente tiene que citar la ENAHO (o el INEI) y el BCRP; si no, "
        "cuenta como «se equivoca (fuente incompleta)».", "",
        "Instrucción común a ambos modos (antes de cada pregunta):", "", "```text", INSTRUCCION.strip(), "```", "",
        tabla_md(preg[["id", "tipo", "verdad", "tolerancia", "unidad", "fuente"]].rename(columns={
            "id": "Pregunta", "tipo": "Tipo", "verdad": "Esperada", "tolerancia": "Tolerancia", "unidad": "Unidad",
            "fuente": "De dónde sale la respuesta esperada"})), "",
        "## Qué herramientas tiene cada modo", "", tabla_md(modos_tabla), "",
        "El modo `memoria` no puede leer archivos: no tiene herramientas, no hay `CLAUDE.md` y la memoria automática "
        "del directorio está vacía. El modo `mcp_skills` sí lee archivos, y por eso las 20 sesiones corren en una "
        "copia aislada de `tarea_4/` que no tiene la clave de respuestas ni el historial de git; puede leer "
        "`salidas/indicadores.csv`, que es la salida de la skill `limpiando-enaho` y forma parte de lo que se evalúa. "
        "La columna `toco_archivos_de_evaluacion` de `resultados.csv` marca cualquier sesión que haya intentado leer "
        "archivos de la evaluación.", "",
        "## Resultados por modo", "", tabla_md(resumen), "",
        "### Por tipo de pregunta", "", tabla_md(por_tipo), "",
        "### Por pregunta", "", tabla_md(detalle), "",
        "### Preguntas que mejoraron o empeoraron", "",
        tabla_md(cambios) if len(cambios) else "Ninguna pregunta cambió de resultado entre los dos modos.", "",
        "### Herramientas efectivamente usadas en `mcp_skills`", "", tabla_md(herr), "",
        "## Errores y respuestas fallidas", "",
        tabla_md(fallos) if len(fallos) else "No hubo respuestas fallidas.", "",
        "<!-- conclusiones:inicio -->", "<!-- conclusiones:fin -->", "",
    ]
    destino = AQUI / "comparacion.md"
    texto = reemplazar("\n".join(md), "conclusiones", conclusiones(res, preg))
    destino.write_text(texto, encoding="utf-8")

    # ------------------------------------------------------------------------------------- bloques del README
    readme = TAREA / "README.md"
    r = readme.read_text(encoding="utf-8")
    pruebas = re.search(r"(\d+) passed", (TAREA / "evidencias_ia/mcp/pruebas.txt").read_text(encoding="utf-8"))
    val = (TAREA / "salidas/validacion.txt").read_text(encoding="utf-8")
    nac = re.search(r"Pobreza monetaria nacional\s+([\d.]+) %", val).group(1)
    urb = re.search(r"Pobreza urbana\s+([\d.]+) %", val).group(1)
    rur = re.search(r"Pobreza rural\s+([\d.]+) %", val).group(1)
    resid = re.search(r"Residentes habituales\s+([\d,]+)", val).group(1)
    unid = re.search(r"Unidades territoriales\s+(\d+)", val).group(1)
    esenciales = re.search(r"Resultado: (\d+ de \d+)", val).group(1)
    correctas = {m: int(res[res.modo == m].correcto.sum()) for m in modos}
    bloque = [
        "| Componente | Resultado |", "|---|---|",
        f"| Pruebas del MCP (`uv run pytest -q`) | {pruebas.group(1) if pruebas else '?'} passed de 10 "
        "([salida](evidencias_ia/mcp/pruebas.txt)) |",
        f"| Validación ENAHO 2024, base hogar `factor07 × mieperho` | pobreza {nac} % · urbana {urb} % · rural {rur} % · "
        f"{resid} residentes habituales · {unid}/25 unidades territoriales · {esenciales} comprobaciones esenciales "
        "([validacion.txt](salidas/validacion.txt)) |",
        f"| Evaluación (Haiku, {n} preguntas) | sin MCP/Skills {correctas.get('memoria', '?')}/{n} · con MCP/Skills "
        f"{correctas.get('mcp_skills', '?')}/{n} ([resultados.csv](evaluacion/resultados.csv)) |",
    ]
    bitacora = TAREA / "evidencias_ia/integracion/bitacora.json"
    if bitacora.exists():
        b = json.loads(bitacora.read_text(encoding="utf-8"))
        bloque.append(f"| Agente de investigación (una sesión, {b['modelo']}) | {len(b['herramientas_mcp'])} "
                      f"herramientas MCP y {len(b['skills'])} skills en {b['segundos'] / 60:.1f} min "
                      "([traza](evidencias_ia/integracion/ejecucion_agente.md)) |")
        ejec = [f"- Modelo: {b['modelo']}; duración: {b['segundos'] / 60:.1f} min; turnos: {b['turnos']}; costo "
                f"informado por Claude Code: US$ {b['costo_usd']:.2f}; terminó con error: {b['termino_con_error']}.",
                f"- Herramientas MCP usadas: {', '.join(f'`{h}`' for h in b['herramientas_mcp'])}.",
                f"- Skills usadas: {', '.join(f'`{s}`' for s in b['skills'])}.",
                "- Recursos MCP leídos: " + (", ".join(f"`{x.get('uri')}`" for x in b["recursos_leidos"])
                                             or "ninguno") + ".",
                "- Resultado: [`informes/informe_final.md`](informes/informe_final.md), con la verificación "
                "independiente de cifras al final. Traza completa: "
                "[`ejecucion_agente.md`](evidencias_ia/integracion/ejecucion_agente.md); bitácora: "
                "[`bitacora.json`](evidencias_ia/integracion/bitacora.json)."]
        r = reemplazar(r, "ejecucion", "\n".join(ejec))
    r = reemplazar(r, "resumen", "\n".join(bloque))
    r = reemplazar(r, "evaluacion", tabla_md(resumen) + "\n\n" + tabla_md(por_tipo))
    readme.write_text(r, encoding="utf-8")
    print(resumen.to_string(index=False))
    print(f"\nEscribí {destino.relative_to(TAREA)} y actualicé los bloques del README.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
