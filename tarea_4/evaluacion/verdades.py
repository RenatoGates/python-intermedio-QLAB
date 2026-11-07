"""Arma evaluacion/preguntas.csv: 10 preguntas con su respuesta esperada calculada, no escrita a mano.

    uv run evaluacion/verdades.py          # desde tarea_4/; se corre ANTES de evaluar.py y no se toca después

La verdad sale por caminos independientes del sistema que se evalúa:
- BCRP: estadisticas.bcrp.gob.pe directamente, sin el MCP bcrp. Se lee el JSON de la API (precisión completa) y la
  tabla HTML pública de la misma serie (redondeada), y se exige que coincidan. Las 4 preguntas son del archivo del
  profesor (sessions/04-mcp-claude-code/proyecto/preguntas.csv); se informa si su cifra cambió.
- ENAHO: cálculo directo desde los .dta con factores de expansión, con código propio (no usa limpiar.py).
- Combinadas: el producto de las dos anteriores, con la fórmula en el texto de la pregunta.
"""
import re
import sys
import time
from pathlib import Path

import httpx
import numpy as np
import pandas as pd

AQUI = Path(__file__).parent
TAREA = AQUI.parent
DATOS = TAREA / "datos"
SITIO = "https://estadisticas.bcrp.gob.pe/estadisticas/series"
PLURAL = {"M": "mensuales", "D": "diarias"}
K = ["conglome", "vivienda", "hogar"]
# Gasto en alimentos (grupo 1) según el do-file oficial del INEI 01.ConstrVarGastoIngreso2014-2024.do
ALIMENTOS = ("gru11hd gru12hd1 gru12hd2 gru13hd1 gru13hd2 gru13hd3 g05hd g05hd1 g05hd2 g05hd3 g05hd4 g05hd5 g05hd6 "
             "ig06hd sg23 sig24 gru14hd gru14hd1 gru14hd2 gru14hd3 gru14hd4 gru14hd5 sg25 sig26 sg27 sig28").split()
PROFESOR = {   # id: (verdad en el archivo del profesor, serie, frecuencia, periodo de la API)
    "ipc_set26": (4.5487, "PN01273PM", "M", "2026-9"),
    "ipc_dic25": (1.5088, "PN01273PM", "M", "2025-12"),
    "referencia_set26": (4.25, "PD04722MM", "M", "2026-9"),
    "tc_15oct26": (3.4282, "PD04638PD", "D", "2026-10-15"),
}


def _get(url: str) -> httpx.Response:
    for intento in range(5):
        r = httpx.get(url, timeout=60)
        if r.status_code == 200 and "Incapsula" not in r.text[:600]:
            return r
        time.sleep(2 * 2 ** intento)
    raise RuntimeError(f"estadisticas.bcrp.gob.pe no respondió con datos: {url}")


def bcrp(codigo: str, frec: str, desde: str, hasta: str) -> list[tuple[str, float, float]]:
    """[(periodo, valor de la API JSON, valor de la tabla HTML)] del sitio del BCRP, sin pasar por el MCP."""
    api = _get(f"{SITIO}/api/{codigo}/json/{desde}/{hasta}").json()["periods"]
    time.sleep(1.5)
    html = _get(f"{SITIO}/{PLURAL[frec]}/resultados/{codigo}/html/{desde}/{hasta}/").text
    filas = re.findall(r'class="periodo">\s*<b>([^<]+)</b>\s*</td>\s*<td class="dato">\s*([-0-9.]+)', html)
    time.sleep(1.5)
    if len(api) != len(filas):
        raise RuntimeError(f"{codigo}: la API trae {len(api)} periodos y la tabla HTML {len(filas)}")
    out = []
    for p, (etiqueta, dato) in zip(api, filas):
        v_api, v_html = float(p["values"][0]), float(dato)
        decimales = len(dato.split(".")[1]) if "." in dato else 0
        if abs(round(v_api, decimales) - v_html) > 10 ** -decimales / 2 + 1e-9:
            raise RuntimeError(f"{codigo} {p['name']}: API {v_api} y HTML {v_html} no coinciden")
        out.append((p["name"], v_api, v_html))
    return out


def enaho() -> dict[str, float]:
    s = pd.read_stata(DATOS / "966-Modulo34/966-Modulo34/sumaria-2024.dta", convert_categoricals=False)
    p = pd.read_stata(DATOS / "966-Modulo02/966-Modulo02/enaho01-2024-200.dta", convert_categoricals=False,
                      columns=K + ["p204", "p205", "p206", "p208a"])
    s.columns = s.columns.str.lower()
    res = p[((p.p204 == 1) & (p.p205 == 2)) | ((p.p204 == 2) & (p.p206 == 1))]
    edad = res.assign(am=res.p208a >= 65).groupby(K).agg(n=("am", "size"), am=("am", "sum")).reset_index()
    h = s.merge(edad, on=K, how="left", validate="1:1")
    w, f = h.factor07 * h.mieperho, h.factor07
    pobre, rural = h.pobreza <= 2, h.estrato > 5
    solo_am = (h.am == h.n) & (h.n > 0)
    alim = h[[c for c in ALIMENTOS if c in h.columns]].fillna(0).sum(axis=1)
    part = 100 * alim / h.gashog2d
    return {
        "pobreza_nacional": 100 * w[pobre].sum() / w.sum(),
        "pobreza_rural": 100 * w[pobre & rural].sum() / w[rural].sum(),
        "pobreza_solo_am": 100 * w[pobre & solo_am].sum() / w[solo_am].sum(),
        "hogares_con_am": 100 * f[h.am > 0].sum() / f.sum(),
        "part_alimentos_rural": float(np.average(part[rural], weights=w[rural])),
        "part_alimentos_solo_am": float(np.average(part[solo_am], weights=w[solo_am])),
    }


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    profesor = pd.read_csv(AQUI / "preguntas_profesor.csv").set_index("id")
    filas, notas = [], []

    for qid, (v_prof, codigo, frec, periodo) in PROFESOR.items():
        (_, v_api, v_html), = bcrp(codigo, frec, periodo, periodo)
        q = profesor.loc[qid]
        cambio = "igual que en el archivo del profesor" if abs(v_api - v_prof) < 1e-3 else \
            f"el archivo del profesor decía {v_prof}"
        notas.append(f"{qid}: API {v_api:.4f}, tabla HTML {v_html} ({cambio})")
        filas.append({"id": qid, "tipo": "bcrp", "pregunta": q.pregunta, "verdad": round(v_api, 4),
                      "tolerancia": q.tolerancia, "unidad": "%" if codigo != "PD04638PD" else "S/ por US$",
                      "fuente": f"BCRP, serie {codigo}, estadisticas.bcrp.gob.pe (API JSON y tabla HTML: {v_html})",
                      "periodo": q.periodo})

    e = enaho()
    base = "INEI, ENAHO 2024 (módulos 34 y 02); cálculo directo en evaluacion/verdades.py"
    for qid, clave, texto, tol in [
        ("enaho_pobreza_nacional", "pobreza_nacional",
         "Según la ENAHO 2024 del INEI, ¿qué porcentaje de la población del Perú estaba en situación de pobreza "
         "monetaria en 2024, en %?", 0.1),
        ("enaho_pobreza_rural", "pobreza_rural",
         "Según la ENAHO 2024 del INEI, ¿qué porcentaje de la población del área rural del Perú estaba en situación "
         "de pobreza monetaria en 2024, en %?", 0.1),
        ("enaho_pobreza_solo_am", "pobreza_solo_am",
         "Según la ENAHO 2024 del INEI, ¿qué porcentaje de las personas que viven en hogares donde todos los "
         "residentes habituales tienen 65 años o más estaba en pobreza monetaria? Pondera con factor07 × mieperho; "
         "en %.", 0.1),
        ("enaho_hogares_con_am", "hogares_con_am",
         "Según la ENAHO 2024 del INEI, ¿qué porcentaje de los hogares del Perú tiene al menos un residente "
         "habitual de 65 años o más? Pondera los hogares con factor07; en %.", 0.1),
    ]:
        filas.append({"id": qid, "tipo": "enaho", "pregunta": texto, "verdad": round(float(e[clave]), 4),
                      "tolerancia": tol, "unidad": "%", "fuente": f"{base}, ponderado con "
                      f"{'factor07' if clave == 'hogares_con_am' else 'factor07 × mieperho'}", "periodo": "2024"})

    (_, alim_oct26, _), = bcrp("PN09822PM", "M", "2026-10", "2026-10")
    alim_2025 = float(np.mean([v for _, v, _ in bcrp("PN09822PM", "M", "2025-1", "2025-12")]))
    notas.append(f"PN09822PM 2026-10: {alim_oct26:.4f}; promedio 2025: {alim_2025:.4f}")
    filas += [
        {"id": "comb_exposicion_rural_oct26", "tipo": "combinada",
         "pregunta": "Contribución aproximada de los alimentos a la inflación de un hogar rural peruano: multiplica la "
                     "participación promedio de los alimentos en el gasto de los hogares rurales del Perú (ENAHO 2024 "
                     "del INEI, % del gasto, ponderado con factor07 × mieperho) por la inflación de alimentos y "
                     "bebidas de Lima Metropolitana a 12 meses de octubre de 2026 (BCRP, %) y divide entre 100. "
                     "¿Cuántos puntos porcentuales da?",
         "verdad": round(float(e["part_alimentos_rural"] * alim_oct26 / 100), 4), "tolerancia": 0.1,
         "unidad": "puntos porcentuales",
         "fuente": f"{base} (participación rural {e['part_alimentos_rural']:.4f} %) × BCRP PN09822PM 2026-10 "
                   f"({alim_oct26:.4f} %) / 100", "periodo": "2024 y 2026-10"},
        {"id": "comb_exposicion_solo_am_2025", "tipo": "combinada",
         "pregunta": "Contribución aproximada de los alimentos a la inflación de los hogares conformados solo por "
                     "adultos mayores de 65 años o más: multiplica su participación promedio de los alimentos en el "
                     "gasto (ENAHO 2024 del INEI, % del gasto, ponderado con factor07 × mieperho) por el promedio de "
                     "enero a diciembre de 2025 de la inflación de alimentos y bebidas de Lima Metropolitana a 12 "
                     "meses (BCRP, %) y divide entre 100. ¿Cuántos puntos porcentuales da?",
         "verdad": round(float(e["part_alimentos_solo_am"] * alim_2025 / 100), 4), "tolerancia": 0.1,
         "unidad": "puntos porcentuales",
         "fuente": f"{base} (participación {e['part_alimentos_solo_am']:.4f} %) × BCRP PN09822PM promedio 2025 "
                   f"({alim_2025:.4f} %) / 100", "periodo": "2024 y 2025"},
    ]
    pd.DataFrame(filas).to_csv(AQUI / "preguntas.csv", index=False, encoding="utf-8")
    print(pd.DataFrame(filas)[["id", "tipo", "verdad", "tolerancia"]].to_string(index=False))
    print("\n" + "\n".join(notas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
