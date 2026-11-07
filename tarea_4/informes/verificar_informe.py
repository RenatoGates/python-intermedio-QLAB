"""Verifica cifras del informe por un camino independiente y escribe la sección 8 de informes/informe_final.md.

    uv run informes/verificar_informe.py          # desde tarea_4/

Para cada afirmación: la busca en el texto del informe, la recalcula sin pasar por el MCP ni por las Skills y anota
la diferencia.
- BCRP: la tabla HTML pública de estadisticas.bcrp.gob.pe (la que vería una persona en el navegador), contrastada
  con el JSON de la API del mismo sitio (funciones de evaluacion/verdades.py, que no usan mcp/server.py).
- ENAHO: cálculo directo desde los .dta con factores de expansión, escrito aquí y no en limpiar.py.
Si el informe cambia de redacción y una afirmación ya no se encuentra, la tabla lo dice; no se rellena a mano.
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).parent
TAREA = AQUI.parent
sys.path.insert(0, str(TAREA / "evaluacion"))
from verdades import ALIMENTOS, DATOS, K, bcrp  # noqa: E402

INFORME = AQUI / "informe_final.md"
MESES = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6, "Jul": 7, "Ago": 8, "Sep": 9, "Set": 9,
         "Oct": 10, "Nov": 11, "Dic": 12}


def periodo(nombre_api: str) -> str:
    m = re.fullmatch(r"([A-Za-z]{3})\.(\d{4})", nombre_api)
    return f"{m[2]}-{MESES[m[1]]:02d}"


def enaho_directo() -> pd.DataFrame:
    """Una fila por hogar con lo necesario, calculado desde los .dta sin pasar por las skills."""
    s = pd.read_stata(DATOS / "966-Modulo34/966-Modulo34/sumaria-2024.dta", convert_categoricals=False)
    p = pd.read_stata(DATOS / "966-Modulo02/966-Modulo02/enaho01-2024-200.dta", convert_categoricals=False,
                      columns=K + ["p204", "p205", "p206", "p208a"])
    s.columns = s.columns.str.lower()
    res = p[((p.p204 == 1) & (p.p205 == 2)) | ((p.p204 == 2) & (p.p206 == 1))]
    edad = res.assign(am=res.p208a >= 65).groupby(K).agg(n=("am", "size"), am=("am", "sum")).reset_index()
    h = s.merge(edad, on=K, how="left", validate="1:1")
    h["w"] = h.factor07 * h.mieperho
    h["pobre"] = h.pobreza <= 2
    h["rural"] = h.estrato > 5
    h["solo_am"] = (h.am == h.n) & (h.n > 0)
    h["sin_am"] = h.am == 0
    h["part"] = 100 * h[[c for c in ALIMENTOS if c in h.columns]].fillna(0).sum(axis=1) / h.gashog2d
    return h


def pct(h: pd.DataFrame, cond: pd.Series) -> float:
    return float(100 * h.w[cond].sum() / h.w.sum())


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    texto = INFORME.read_text(encoding="utf-8")

    alim = bcrp("PN09822PM", "M", "2021-1", "2026-10")          # [(nombre, valor API, valor HTML)]
    total = bcrp("PN01273PM", "M", "2021-1", "2026-10")
    tasa_inicio = bcrp("PD04722MM", "M", "2003-1", "2004-3")
    html_alim = pd.Series({periodo(n): v for n, _, v in alim})
    html_total = pd.Series({periodo(n): v for n, _, v in total})
    h = enaho_directo()
    rural_solo = h[h.rural & h.solo_am]
    uno = h.mieperho == 1

    WEB = "tabla HTML de estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/{}/html"
    afirmaciones = [   # (fuente, afirmación, regex con un grupo sobre el informe, valor calculado, tolerancia, cómo)
        ("BCRP", "Inflación de alimentos y bebidas de Lima a 12 meses, 2026-10 (PN09822PM)",
         r"\(PN09822PM, ([\d.]+) %\)", html_alim["2026-10"], 0.005, WEB.format("PN09822PM") + ", fila Oct26"),
        ("BCRP", f"Máximo de PN09822PM entre 2021-01 y 2026-10 (en {html_alim.idxmax()})",
         r"\| PN09822PM alimentos y bebidas \|[^\n]*?\| ([\d.]+) % \(2023-02\)", html_alim.max(), 0.005,
         WEB.format("PN09822PM") + ", máximo de las 70 filas"),
        ("BCRP", "Correlación de alimentos con la inflación total, sin rezago, 2021-01 a 2026-10",
         r"Sin rezago, r = ([\d.]+) \(fuerte", float(np.corrcoef(html_alim, html_total.reindex(html_alim.index))[0, 1]),
         0.002, "r de Pearson con numpy sobre las tablas HTML de PN09822PM y PN01273PM (valores a 2 decimales)"),
        ("BCRP", "Primer mes con dato de la tasa de referencia PD04722MM (la ficha dice Ene-2004)",
         r"devuelve datos desde \*\*(\d{4}-\d{2})\*\*", periodo(tasa_inicio[0][0]), None,
         WEB.format("PD04722MM") + " pedida desde 2003-1: primera fila"),
        ("ENAHO", "Pobreza en hogares de solo adultos mayores (nacional)",
         r"\| Solo adultos mayores \| ([\d.]+) % \| [\d.]+ % \| [\d.]+ \|", pct(h[h.solo_am], h.pobre[h.solo_am]),
         0.05, "cálculo directo desde los .dta, factor07 × mieperho"),
        ("ENAHO", "Personas por hogar en hogares de solo adultos mayores (mieperho medio)",
         r"\| Solo adultos mayores \| [\d.]+ % \| [\d.]+ % \| ([\d.]+) \|",
         float(np.average(h.mieperho[h.solo_am], weights=h.factor07[h.solo_am])), 0.005,
         "cálculo directo desde los .dta, promedio de mieperho ponderado con factor07"),
        ("ENAHO", "Pobreza en hogares unipersonales de un adulto mayor (control por tamaño)",
         r"\| 1 persona \| [\d.]+ % \(n = [\d,]+\) \| [^|]+\| ([\d.]+) % \(n",
         pct(h[uno & h.solo_am], h.pobre[uno & h.solo_am]), 0.05,
         "cálculo directo desde los .dta: mieperho = 1 y residente de 65+, factor07 × mieperho"),
        ("ENAHO", "Pobreza en hogares unipersonales sin adultos mayores (control por tamaño)",
         r"\| 1 persona \| ([\d.]+) % \(n = ", pct(h[uno & h.sin_am], h.pobre[uno & h.sin_am]), 0.05,
         "cálculo directo desde los .dta: mieperho = 1 y ningún residente de 65+, factor07 × mieperho"),
        ("Combinada", "Contribución de los alimentos a la inflación de hogares rurales de solo adultos mayores, 2026-10",
         r"\| Rural \| Solo adultos mayores \| [\d.]+ % \| ([\d.]+) pp",
         float(np.average(rural_solo.part, weights=rural_solo.w)) * html_alim["2026-10"] / 100, 0.005,
         "participación de alimentos directa de los .dta (factor07 × mieperho) × PN09822PM de la tabla HTML / 100"),
    ]

    filas, n_ok = [], 0
    for fuente, que, patron, calculado, tol, como in afirmaciones:
        m = re.search(patron, texto)
        if not m:
            filas.append((fuente, que, "no encontrada", calculado, como, "—", "no se pudo comparar"))
            continue
        en_informe = m.group(1)
        if tol is None:
            ok, dif = en_informe == calculado, "—" if en_informe == calculado else "distinto"
            calc = calculado
        else:
            d = float(en_informe) - calculado
            ok, dif, calc = abs(d) <= tol, f"{d:+.4f}", f"{calculado:.4f}"
        n_ok += ok
        filas.append((fuente, que, en_informe, calc, como, dif, "sí" if ok else "NO"))

    tabla = ["| # | Fuente | Afirmación del informe | Valor en el informe | Valor calculado | Fuente o procedimiento "
             "de verificación | Diferencia | ¿Coincide? |", "|---|---|---|---|---|---|---|---|"]
    tabla += [f"| {i} | {f} | {q} | {v} | {c} | {como} | {d} | {ok} |"
              for i, (f, q, v, c, como, d, ok) in enumerate(filas, 1)]
    seccion = "\n".join([
        "Generada por `informes/verificar_informe.py`, que no usa el MCP ni las Skills: las cifras del BCRP se "
        "comprueban en la tabla HTML pública de estadisticas.bcrp.gob.pe (contrastada con el JSON de la API del "
        "mismo sitio) y las de la ENAHO con un cálculo directo desde los `.dta`. «Valor calculado» va con 4 "
        "decimales; la tolerancia es medio punto del último decimal que muestra el informe (0.002 para r, porque "
        "la tabla HTML redondea a 2 decimales).", "", *tabla, "",
        f"**{n_ok} de {len(filas)} afirmaciones coinciden.** Diferencias: el informe redondea; el r recalculado con "
        "valores a 2 decimales difiere del de `correlacion` (que usa la precisión completa de la API) en el cuarto "
        "decimal."])
    nuevo = re.sub(r"(<!-- verificacion:inicio -->).*?(<!-- verificacion:fin -->)",
                   lambda m: f"{m.group(1)}\n{seccion}\n{m.group(2)}", texto, flags=re.S)
    INFORME.write_text(nuevo, encoding="utf-8")
    print("\n".join(tabla))
    print(f"\n{n_ok} de {len(filas)} coinciden. Sección 8 de {INFORME.relative_to(TAREA)} actualizada.")
    return 0 if n_ok == len(filas) else 1


if __name__ == "__main__":
    raise SystemExit(main())
