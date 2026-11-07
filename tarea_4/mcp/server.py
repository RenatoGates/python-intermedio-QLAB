"""Servidor MCP del BCRP para la tarea 4: busca, descarga, resume y compara series oficiales.

    uv run pytest -q                                             # 8 pruebas del profesor + 2 propias (desde tarea_4/)
    uv run mcp/server.py                                         # el servidor, por stdio
    claude mcp add --scope project bcrp -- uv run mcp/server.py  # conectarlo a Claude Code

Las cuentas las hace Python, no el modelo: así cada cifra sale de una llamada que se puede repetir.
"""
import calendar
import json
import re
import time
import unicodedata
from datetime import date, datetime
from functools import cache
from pathlib import Path

import httpx
import pandas as pd
from fastmcp import FastMCP
from fastmcp.exceptions import ResourceError, ToolError

AQUI = Path(__file__).parent
CATALOGO = AQUI.parent / "datos" / "catalogo_bcrp.csv"     # tarea_4/datos/, que git ignora
URL_CATALOGO = "https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata"
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
WEB = "https://estadisticas.bcrp.gob.pe/estadisticas/series"
SOLO_LECTURA = {"readOnlyHint": True, "openWorldHint": True}
INTENTOS, ESPERA = 4, 2                                     # reintentos ante la página HTML de bloqueo: 2, 4 y 8 s

mcp = FastMCP("bcrp", instructions=(
    "Series oficiales del Banco Central de Reserva del Perú (BCRP). Primero busca el código con buscar_series; "
    "luego usa resumen para variaciones, promedios y extremos, serie para los datos, correlacion para comparar "
    "dos series y graficar_series para un gráfico. La ficha de una serie está en el recurso bcrp://serie/{codigo}. "
    "No calcules a mano: cita "
    "siempre el código de la serie, el periodo y la fuente. Si una herramienta falla, dilo; no estimes."))


def _sin_tildes(s):
    return unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode()


@cache
def catalogo():
    """El catálogo oficial: 17 mil series en unos 7 MB. Se baja una vez y queda en datos/."""
    if not CATALOGO.exists():
        CATALOGO.parent.mkdir(exist_ok=True)
        r = httpx.get(URL_CATALOGO, timeout=120)
        r.raise_for_status()
        CATALOGO.write_text(r.content.decode("latin-1"), encoding="utf-8")
    df = pd.read_csv(CATALOGO, sep=";", dtype=str).fillna("")
    df = df.rename(columns={"Código de serie": "codigo", "Categoría de serie": "categoria", "Grupo de serie": "grupo",
                            "Nombre de serie": "nombre", "Frecuencia": "frecuencia",
                            "Fecha de actualización": "actualizada", "Fecha de inicio": "inicio",
                            "Fuente": "origen", "Área que publica": "area"})
    df["texto"] = (df.categoria + " " + df.grupo + " " + df.nombre).map(_sin_tildes)
    return df


def _ficha(codigo):
    fila = catalogo().query("codigo == @codigo")
    if fila.empty:
        raise ToolError(f"No existe el código de serie {codigo!r}. Búsquenlo con buscar_series.")
    f = fila.iloc[0]
    return {"codigo": f.codigo, "nombre": f"{f.grupo} - {f.nombre}", "categoria": f.categoria,
            "frecuencia": f.frecuencia, "inicio": f.inicio, "actualizada": f.actualizada}


@mcp.tool(annotations=SOLO_LECTURA)
def buscar_series(texto: str, frecuencia: str | None = None, limite: int = 10) -> list[dict]:
    """Busca series del BCRP por palabras: todas deben aparecer en la categoría, el grupo o el nombre.

    Ejemplos: "ipc 12 meses", "tipo de cambio interbancario venta", "reservas internacionales netas",
    "tasa de referencia", "cobre precio". frecuencia: "Diaria", "Mensual", "Trimestral" o "Anual".
    Devuelve el código, el nombre completo, la frecuencia y desde cuándo hay datos. Si no hay resultados,
    prueben con menos palabras.
    """
    df = catalogo()
    m = pd.Series(True, index=df.index)
    for palabra in _sin_tildes(texto).split():
        m &= df.texto.str.contains(re.escape(palabra))
    if frecuencia:
        m &= df.frecuencia.str.lower() == frecuencia.lower()
    # primero las series vigentes y, entre ellas, las de nombre más corto (las más generales)
    sel = df[m]
    orden = sel.assign(vieja=sel.actualizada < "2025", largo=(sel.grupo + sel.nombre).str.len())
    return [_ficha(c) for c in orden.sort_values(["vieja", "largo"]).head(limite).codigo]


# ---------------------------------------------------------------------------------------------------------------
# Fechas: lo que escribe el usuario, lo que pide la API y lo que devuelve
# ---------------------------------------------------------------------------------------------------------------

FORMATOS = "«2025-01» (mes), «2025-01-15» (día), «2025-T1» (trimestre) o «2025» (año)"
MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8,
         "sep": 9, "set": 9, "oct": 10, "nov": 11, "dic": 12}     # setiembre: «Sep» en mensuales, «Set» en diarias
PLURAL = {"Diaria": "diarias", "Mensual": "mensuales", "Trimestral": "trimestrales", "Anual": "anuales"}
FRECUENCIA_PANDAS = {"Diaria": "D", "Mensual": "M", "Trimestral": "Q", "Anual": "Y"}


def _a_api(fecha: str, frecuencia: str, fin: bool) -> tuple[str, tuple[int, int, int]]:
    """Pasa una fecha del usuario al formato de la API para esa frecuencia, y una clave para ordenarla.

    La API pide 2025-1 en mensuales y trimestrales (el número es el mes o el trimestre), 2025-01-15 en diarias y
    2025 en anuales. Si la fecha es más gruesa que la frecuencia, se toma el inicio del intervalo para «desde» y el
    final para «hasta»: «2025» como hasta de una serie mensual es diciembre de 2025.
    """
    texto = str(fecha).strip()
    trimestre = mes = dia = None
    if m := re.fullmatch(r"(\d{4})", texto):
        anio = int(m[1])
    elif m := re.fullmatch(r"(\d{4})-[TtQq]([1-4])", texto):
        anio, trimestre = int(m[1]), int(m[2])
    elif m := re.fullmatch(r"(\d{4})-(\d{1,2})", texto):
        anio, mes = int(m[1]), int(m[2])
    elif m := re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", texto):
        anio, mes, dia = int(m[1]), int(m[2]), int(m[3])
    else:
        raise ToolError(f"No entiendo la fecha {fecha!r}. Usen {FORMATOS}.")
    if mes is not None and not 1 <= mes <= 12:
        raise ToolError(f"Mes fuera de rango en {fecha!r}. Usen {FORMATOS}.")
    if dia is not None:
        try:
            date(anio, mes, dia)
        except ValueError:
            raise ToolError(f"La fecha {fecha!r} no existe.") from None

    if mes is not None:
        mes_ini = mes_fin = mes
    elif trimestre is not None:
        mes_ini, mes_fin = 3 * trimestre - 2, 3 * trimestre
    else:
        mes_ini, mes_fin = 1, 12
    mes_k = mes_fin if fin else mes_ini
    if dia is None:
        dia = calendar.monthrange(anio, mes_k)[1] if fin else 1
    clave = (anio, mes_k, dia)

    if frecuencia == "Anual":
        return str(anio), clave
    if frecuencia == "Mensual":
        return f"{anio}-{mes_k}", clave
    if frecuencia == "Trimestral":
        return f"{anio}-{(mes_k - 1) // 3 + 1}", clave
    if frecuencia == "Diaria":
        return f"{anio}-{mes_k:02d}-{dia:02d}", clave
    raise ToolError(f"Frecuencia no soportada: {frecuencia!r}.")


def _anio(aa: str) -> int:
    return datetime.strptime(aa, "%y").year       # 69-99 son 19xx; 00-68, 20xx


def _periodo(nombre: str) -> str:
    """'Ene.2025' -> '2025-01', '01.Oct.26' -> '2026-10-01', 'T1.25' -> '2025-T1', '2025' -> '2025'."""
    n = nombre.strip()
    if m := re.fullmatch(r"([A-Za-z]{3})\.(\d{4})", n):                  # mensual
        return f"{m[2]}-{MESES[m[1].lower()]:02d}"
    if m := re.fullmatch(r"(\d{1,2})\.([A-Za-z]{3})\.(\d{2})", n):       # diaria
        return date(_anio(m[3]), MESES[m[2].lower()], int(m[1])).isoformat()
    if m := re.fullmatch(r"T([1-4])\.(\d{2})", n):                       # trimestral
        return f"{_anio(m[2])}-T{m[1]}"
    if re.fullmatch(r"\d{4}", n):                                         # anual
        return n
    raise ValueError(n)


@cache
def _bajar(codigo: str, desde: str, hasta: str) -> tuple[tuple[str, float], ...]:
    """Pide la serie a la API y la devuelve como pares (periodo, valor), sin los «n.d.».

    Si la API responde la página HTML de bloqueo en vez de JSON, espera y reintenta. Lo que baja bien queda en
    memoria (functools.cache no guarda los errores, así que un fallo se vuelve a intentar en la siguiente llamada).
    """
    url = f"{API}/{codigo}/json/{desde}/{hasta}"
    for intento in range(INTENTOS):
        try:
            r = httpx.get(url, timeout=60)
            r.raise_for_status()
            cuerpo = r.json()
            break
        except (httpx.HTTPError, ValueError):
            if intento == INTENTOS - 1:
                raise ToolError(f"El BCRP no respondió con datos para {codigo} tras {INTENTOS} intentos ({url}). "
                                "La API limita los pedidos seguidos: esperen unos segundos y reintenten.") from None
            time.sleep(ESPERA * 2 ** intento)
    pares = []
    for p in cuerpo.get("periods") or []:
        try:
            valor = float(p["values"][0])
        except (KeyError, IndexError, TypeError, ValueError):
            continue                                                     # «n.d.» o vacío
        try:
            pares.append((_periodo(p["name"]), valor))
        except (KeyError, ValueError):
            raise ToolError(f"La API devolvió un periodo con formato inesperado: {p.get('name')!r}.") from None
    return tuple(pares)


def _web(codigo, frecuencia):
    return f"{WEB}/{PLURAL[frecuencia]}/resultados/{codigo}/html"


def _r(x, nd=4):
    return None if x is None or pd.isna(x) else round(float(x), nd)


# ---------------------------------------------------------------------------------------------------------------
# TODO 1 · serie
# ---------------------------------------------------------------------------------------------------------------

@mcp.tool(annotations=SOLO_LECTURA)
def serie(codigo: str, desde: str, hasta: str) -> dict:
    """Descarga los datos de una serie del BCRP entre dos fechas, con la URL de la fuente.

    Úsala cuando necesites los valores periodo a periodo, por ejemplo para citar el dato de un mes o graficar.
    Para variaciones, promedios, máximos o mínimos usa resumen, y para comparar dos series usa correlacion:
    no hagas esas cuentas a mano.

    Args:
        codigo: código del BCRP, por ejemplo "PN01273PM" (búscalo con buscar_series).
        desde: inicio, en «2025-01» (mes), «2025-01-15» (día), «2025-T1» (trimestre) o «2025» (año).
        hasta: fin, en el mismo formato. Se adapta a la frecuencia de la serie.
    """
    f = _ficha(str(codigo).strip().upper())
    d, clave_d = _a_api(desde, f["frecuencia"], fin=False)
    h, clave_h = _a_api(hasta, f["frecuencia"], fin=True)
    if clave_d > clave_h:
        raise ToolError(f"«desde» ({desde}) es posterior a «hasta» ({hasta}).")
    datos = [{"periodo": p, "valor": round(v, 6)} for p, v in _bajar(f["codigo"], d, h)]
    r = {"codigo": f["codigo"], "nombre": f["nombre"], "frecuencia": f["frecuencia"], "desde": desde,
         "hasta": hasta, "n": len(datos), "datos": datos, "fuente": f"{API}/{f['codigo']}/json/{d}/{h}",
         "web": _web(f["codigo"], f["frecuencia"])}
    if not datos:
        r["nota"] = (f"El BCRP no tiene datos de {f['codigo']} entre {desde} y {hasta}. La serie empieza en "
                     f"{f['inicio']} y se actualizó el {f['actualizada']}.")
    return r


# ---------------------------------------------------------------------------------------------------------------
# TODO 2 · resumen
# ---------------------------------------------------------------------------------------------------------------

@mcp.tool(annotations=SOLO_LECTURA)
def resumen(codigo: str, desde: str, hasta: str) -> dict:
    """Resume una serie del BCRP en un periodo: primero, último, cambio, variación %, promedio, máximo y mínimo.

    Úsala para cualquier cifra derivada (cuánto subió, el promedio, el pico) en vez de calcularla a mano.
    cambio = último - primero, en las unidades de la serie. variacion_pct = cambio / primero * 100.
    Si la serie ya es una tasa o un porcentaje (inflación, tasa de referencia), lo que suele preguntarse es
    cambio, en puntos porcentuales; variacion_pct sería la variación relativa de esa tasa.

    Args:
        codigo: código del BCRP, por ejemplo "PN01273PM".
        desde: inicio, en «2025-01», «2025-01-15», «2025-T1» o «2025».
        hasta: fin, en el mismo formato.
    """
    s = serie(codigo, desde, hasta)
    if not s["datos"]:
        raise ToolError(s["nota"])
    df = pd.DataFrame(s["datos"])
    primero, ultimo = df.iloc[0], df.iloc[-1]
    cambio = ultimo.valor - primero.valor
    punto = lambda fila: {"periodo": fila.periodo, "valor": _r(fila.valor)}
    r = {"codigo": s["codigo"], "nombre": s["nombre"], "frecuencia": s["frecuencia"], "desde": desde,
         "hasta": hasta, "n": len(df), "primero": punto(primero), "ultimo": punto(ultimo), "cambio": _r(cambio),
         "variacion_pct": None if primero.valor == 0 else _r(cambio / primero.valor * 100),
         "promedio": _r(df.valor.mean()), "maximo": punto(df.loc[df.valor.idxmax()]),
         "minimo": punto(df.loc[df.valor.idxmin()]), "fuente": s["fuente"], "web": s["web"]}
    if re.search(r"%|tasa", s["nombre"], re.IGNORECASE):
        r["nota"] = "La serie ya está en %: «cambio» está en puntos porcentuales."
    return r


# ---------------------------------------------------------------------------------------------------------------
# TODO 3 · herramienta propia: correlacion
# ---------------------------------------------------------------------------------------------------------------

def _como_serie(s: dict) -> pd.Series:
    """Los datos de serie() como pd.Series con índice de periodos de pandas, para alinear y desplazar fechas."""
    if s["frecuencia"] == "Trimestral":
        idx = [pd.Period(year=int(p[:4]), quarter=int(p[-1]), freq="Q") for p in (d["periodo"] for d in s["datos"])]
    else:
        idx = [pd.Period(d["periodo"], freq=FRECUENCIA_PANDAS[s["frecuencia"]]) for d in s["datos"]]
    return pd.Series([d["valor"] for d in s["datos"]], index=pd.PeriodIndex(idx), dtype=float)


def _texto(p: pd.Period, frecuencia: str) -> str:
    return {"Diaria": lambda: p.strftime("%Y-%m-%d"), "Mensual": lambda: p.strftime("%Y-%m"),
            "Trimestral": lambda: f"{p.year}-T{p.quarter}", "Anual": lambda: str(p.year)}[frecuencia]()


def _fuerza(r):
    if r is None:
        return "no definida: una de las series no varía en el periodo"
    nivel = "débil" if abs(r) < 0.3 else "moderada" if abs(r) < 0.7 else "fuerte"
    return f"{nivel} y {'positiva' if r > 0 else 'negativa' if r < 0 else 'nula'}"


@mcp.tool(annotations=SOLO_LECTURA)
def correlacion(codigo_a: str, codigo_b: str, desde: str, hasta: str, rezago: int = 0) -> dict:
    """Compara dos series del BCRP de la misma frecuencia: correlación de Pearson y brecha media entre ellas.

    Úsala cuando la pregunta sea si dos indicadores se mueven juntos o cuál estuvo por encima del otro. Por
    ejemplo, la inflación de alimentos (PN09822PM) frente a la inflación total (PN01273PM), o la tasa de
    referencia (PD04722MM) frente a la inflación de alimentos. Alinea los periodos y descarta los que no están en
    las dos series. Devuelve r, el número de pares, la brecha media a - b (en las unidades de las series; en
    puntos porcentuales si son tasas) y en cuántos periodos a estuvo por encima de b, con las fuentes de ambas.
    Fuerza de r por convención: |r| < 0.3 débil, < 0.7 moderada, si no fuerte.
    Una correlación describe co-movimiento: no demuestra que una serie cause la otra.

    Args:
        codigo_a: primera serie, por ejemplo "PN09822PM".
        codigo_b: segunda serie, de la misma frecuencia, por ejemplo "PD04722MM".
        desde: inicio, en «2025-01», «2025-01-15», «2025-T1» o «2025». Vale para las dos series.
        hasta: fin, en el mismo formato.
        rezago: k compara a en el periodo t con b en t + k (k > 0: b se mueve k periodos después que a). En series
            diarias son días calendario. Las dos series se leen dentro de [desde, hasta], así que se pierden k pares.
    """
    fa = _ficha(str(codigo_a).strip().upper())
    fb = _ficha(str(codigo_b).strip().upper())
    if fa["frecuencia"] != fb["frecuencia"]:
        raise ToolError(f"{fa['codigo']} es {fa['frecuencia']} y {fb['codigo']} es {fb['frecuencia']}: correlacion "
                        "necesita dos series de la misma frecuencia. Busquen la otra versión con buscar_series.")
    sa, sb = serie(fa["codigo"], desde, hasta), serie(fb["codigo"], desde, hasta)
    a, b = _como_serie(sa), _como_serie(sb)
    b_desplazada = pd.Series(b.values, index=b.index - rezago)        # el valor de b en t + k queda en t
    pares = pd.concat({"a": a, "b": b_desplazada}, axis=1, join="inner").dropna()
    if len(pares) < 3:
        raise ToolError(f"Solo hay {len(pares)} periodos comunes entre {fa['codigo']} y {fb['codigo']} en "
                        f"{desde}-{hasta} con rezago {rezago}: hacen falta al menos 3.")
    r = pares.a.corr(pares.b)
    r = None if pd.isna(r) else _r(r)
    frec = fa["frecuencia"]
    return {
        "serie_a": {"codigo": fa["codigo"], "nombre": fa["nombre"], "n_datos": len(a), "fuente": sa["fuente"]},
        "serie_b": {"codigo": fb["codigo"], "nombre": fb["nombre"], "n_datos": len(b), "fuente": sb["fuente"]},
        "frecuencia": frec, "desde": desde, "hasta": hasta, "rezago": rezago,
        "periodo_comun": {"primero": _texto(pares.index[0], frec), "ultimo": _texto(pares.index[-1], frec)},
        "n_pares": len(pares), "r": r, "fuerza": _fuerza(r),
        "brecha_media": _r((pares.a - pares.b).mean()),
        "periodos_a_mayor_que_b": int((pares.a > pares.b).sum()),
        "advertencia": "Correlación descriptiva entre dos series agregadas: no demuestra causalidad.",
        "fuentes": [sa["fuente"], sb["fuente"]],
    }


# ---------------------------------------------------------------------------------------------------------------
# Herramienta propia 2 · graficar_series: el gráfico sale de los datos que baja el servidor, no de cifras copiadas
# ---------------------------------------------------------------------------------------------------------------

FIGURAS = AQUI.parent / "figuras"
SUPERFICIE, TINTA, TINTA_2, GRILLA = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
SERIES_COLOR = ["#2a78d6", "#eb6834", "#1baf7a"]   # paleta categórica validada (skill dataviz), slots 1 a 3


def _etiqueta(nombre: str) -> str:
    return nombre.split(" - ")[-1].strip()


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True})
def graficar_series(codigos: list[str], desde: str, hasta: str, nombre_archivo: str | None = None) -> dict:
    """Grafica de una a tres series del BCRP en un solo eje y guarda el PNG (y un CSV con los datos) en figuras/.

    Úsala cuando un informe necesite un gráfico de series oficiales: los datos los baja este servidor, así que el
    gráfico no depende de cifras copiadas a mano. Las series deben tener la misma frecuencia y la misma unidad
    (por ejemplo, todas en %): no hace gráficos de doble eje. Ejemplo: codigos=["PN09822PM", "PN01273PM",
    "PD04722MM"], desde="2021-01", hasta="2026-10". Devuelve las rutas, el último dato y el máximo de cada serie y
    las fuentes.

    Args:
        codigos: de 1 a 3 códigos del BCRP de la misma frecuencia.
        desde: inicio, en «2025-01», «2025-01-15», «2025-T1» o «2025».
        hasta: fin, en el mismo formato.
        nombre_archivo: nombre del PNG sin extensión (letras, números, - y _); si falta, se arma con los códigos.
    """
    import textwrap

    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    codigos = [str(c).strip().upper() for c in codigos]
    if not 1 <= len(codigos) <= 3:
        raise ToolError("graficar_series admite de 1 a 3 series: con más, el gráfico deja de leerse.")
    fichas = [_ficha(c) for c in codigos]
    if len({f["frecuencia"] for f in fichas}) > 1:
        raise ToolError("Las series tienen frecuencias distintas: " + ", ".join(f"{f['codigo']} {f['frecuencia']}"
                        for f in fichas) + ". Grafíquenlas por separado.")
    nombre = re.sub(r"[^A-Za-z0-9_-]", "", nombre_archivo or "") or "bcrp_" + "_".join(codigos)
    datos = [serie(c, desde, hasta) for c in codigos]
    if any(not s["datos"] for s in datos):
        raise ToolError("Sin datos en el periodo: " + "; ".join(s["nota"] for s in datos if not s["datos"]))

    tablas = [_como_serie(s) for s in datos]
    frec = fichas[0]["frecuencia"]
    etiquetas = [_etiqueta(s["nombre"]) for s in datos]
    titulo = textwrap.wrap(f"{', '.join(etiquetas)}, {_texto(tablas[0].index[0], frec)} a "
                           f"{_texto(tablas[0].index[-1], frec)}", 78)
    subtitulo = textwrap.wrap("En %. Máximos del periodo: " + "; ".join(
        f"{e} {float(t.max()):.2f} % ({_texto(t.idxmax(), frec)})" for e, t in zip(etiquetas, tablas)) + ".", 112)
    grupos = "; ".join(dict.fromkeys(f["nombre"].rsplit(" - ", 1)[0] for f in fichas))
    pie = textwrap.wrap(f"Fuente: BCRP, estadisticas.bcrp.gob.pe, series {', '.join(codigos)} ({grupos}). Gráfico "
                        "generado por la herramienta graficar_series del MCP bcrp con los datos de la API.", 140)

    # maqueta en pulgadas: cabecera y pie crecen con sus líneas, el eje ocupa el resto
    ancho, alto_eje = 8.6, 3.2
    cabeza = 0.15 + 0.26 * len(titulo) + 0.19 * len(subtitulo) + 0.42      # + fila de leyenda
    pies = 0.42 + 0.14 * len(pie)
    alto_fig = cabeza + alto_eje + pies
    fig = Figure(figsize=(ancho, alto_fig), facecolor=SUPERFICIE)
    FigureCanvasAgg(fig)
    eje = fig.add_axes((0.65 / ancho, pies / alto_fig, (ancho - 0.65 - 2.25) / ancho, alto_eje / alto_fig))
    eje.set_facecolor(SUPERFICIE)
    finales = []
    for e, t, color in zip(etiquetas, tablas, SERIES_COLOR):
        x = t.index.to_timestamp()
        eje.plot(x, t.values, color=color, linewidth=1.6, label=e, solid_capstyle="round")
        eje.plot(x[-1:], t.values[-1:], "o", color=color, markersize=5, markeredgecolor=SUPERFICIE,
                 markeredgewidth=1.2)
        corta = " ".join(e.split()[:3]) if len(e) > 24 else e
        finales.append((x[-1], float(t.values[-1]), corta))
    bajo = min(min(float(t.min()) for t in tablas), 0)
    alto = max(float(t.max()) for t in tablas) * 1.08
    eje.set_ylim(bajo, alto)
    # etiquetas al final de cada línea, con el nombre de la serie; si los últimos valores están cerca, se separan
    # en vertical y un conector fino las une a su punto
    separacion = (alto - bajo) * 0.075
    orden = sorted(range(len(finales)), key=lambda i: finales[i][1])
    pos = {}
    for k, i in enumerate(orden):
        pos[i] = finales[i][1] if k == 0 else max(finales[i][1], pos[orden[k - 1]] + separacion)
    puntos_por_unidad = alto_eje * 72 / (alto - bajo)
    for i, (x_fin, v, corta) in enumerate(finales):
        movida = abs(pos[i] - v) > 1e-9
        eje.annotate(f"{v:.2f} %  {corta}", (x_fin, v), xytext=(14, (pos[i] - v) * puntos_por_unidad),
                     textcoords="offset points", fontsize=8.5, color=TINTA, va="center", annotation_clip=False,
                     arrowprops={"arrowstyle": "-", "color": TINTA_2, "linewidth": 0.6, "shrinkA": 0,
                                 "shrinkB": 3} if movida else None)
    for lado in ("top", "right", "left"):
        eje.spines[lado].set_visible(False)
    eje.spines["bottom"].set_color(GRILLA)
    eje.grid(axis="y", color=GRILLA, linewidth=0.8)
    eje.set_axisbelow(True)
    eje.tick_params(length=0, colors=TINTA_2, labelsize=9)
    eje.set_ylabel("%", color=TINTA_2, fontsize=9)
    eje.legend(loc="lower left", bbox_to_anchor=(0, 1.02), ncol=len(codigos), frameon=False, fontsize=9,
               labelcolor=TINTA, handlelength=1.6, borderaxespad=0)
    y = 1 - 0.15 / alto_fig
    fig.text(0.15 / ancho, y, "\n".join(titulo), va="top", fontsize=12.5, fontweight="bold", color=TINTA,
             linespacing=1.2)
    fig.text(0.15 / ancho, y - (0.26 * len(titulo) + 0.04) / alto_fig, "\n".join(subtitulo), va="top", fontsize=9,
             color=TINTA_2, linespacing=1.3)
    fig.text(0.15 / ancho, 0.06 / alto_fig, "\n".join(pie), va="bottom", fontsize=7.4, color=TINTA_2,
             linespacing=1.3)
    FIGURAS.mkdir(exist_ok=True)
    png, csv = FIGURAS / f"{nombre}.png", FIGURAS / f"{nombre}.csv"
    fig.savefig(png, dpi=200, facecolor=SUPERFICIE)
    pd.concat({c: t for c, t in zip(codigos, tablas)}, axis=1).rename_axis("periodo").rename(
        index=lambda p: _texto(p, frec)).to_csv(csv, encoding="utf-8")
    return {
        "png": png.relative_to(AQUI.parent).as_posix(), "csv": csv.relative_to(AQUI.parent).as_posix(),
        "series": [{"codigo": s["codigo"], "nombre": s["nombre"], "n": len(t),
                    "ultimo": {"periodo": _texto(t.index[-1], frec), "valor": _r(t.iloc[-1])},
                    "maximo": {"periodo": _texto(t.idxmax(), frec), "valor": _r(t.max())}}
                   for s, t in zip(datos, tablas)],
        "fuentes": [s["fuente"] for s in datos],
    }


# ---------------------------------------------------------------------------------------------------------------
# TODO 4 · recurso: la ficha de una serie
# ---------------------------------------------------------------------------------------------------------------

@mcp.resource("bcrp://serie/{codigo}", mime_type="application/json",
              annotations={"readOnlyHint": True, "idempotentHint": True})
def ficha_serie(codigo: str) -> str:
    """Ficha de una serie del BCRP: nombre, categoría, frecuencia, desde cuándo hay datos, quién la produce y enlaces."""
    codigo = codigo.strip().upper()
    fila = catalogo().query("codigo == @codigo")
    if fila.empty:
        raise ResourceError(f"No existe el código de serie {codigo!r}. Búsquenlo con buscar_series.")
    f = fila.iloc[0]
    ficha = {**_ficha(codigo), "grupo": f.grupo, "origen_de_los_datos": f.origen, "area_que_publica": f.area,
             "web": _web(codigo, f.frecuencia), "api": f"{API}/{codigo}/json/{{desde}}/{{hasta}}",
             "catalogo": URL_CATALOGO}
    return json.dumps(ficha, ensure_ascii=False, indent=1)       # con tildes legibles, no í


# ---------------------------------------------------------------------------------------------------------------
# TODO 5 · prompt
# ---------------------------------------------------------------------------------------------------------------

@mcp.prompt
def informe(tema: str) -> str:
    """Pide un informe breve con cifras oficiales del BCRP sobre un tema, citando código, periodo y fuente."""
    return (
        f"Escribe un informe breve sobre «{tema}» en el Perú con series oficiales del BCRP.\n"
        "1. Busca los códigos con buscar_series. Si dudas de qué mide una serie, lee su ficha en "
        "bcrp://serie/{codigo}.\n"
        "2. Saca cada cifra con serie, resumen o correlacion, y el gráfico con graficar_series. No hagas cuentas "
        "a mano.\n"
        "3. Junto a cada cifra cita el código de la serie, el periodo y la URL de la fuente.\n"
        "4. Si comparas dos series, la correlación describe co-movimiento: no la presentes como causa.\n"
        "5. Si una herramienta falla o no hay datos, dilo en el informe en vez de estimar.\n"
        "Cierra con una tabla de las series usadas (código, nombre, periodo)."
    )


if __name__ == "__main__":
    mcp.run()
