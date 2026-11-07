"""Mapa coroplético de la ENAHO por departamento (versión tarea_4).

    uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza       # desde tarea_4/

Indicadores, todos con la base hogar ponderada con factor07 × mieperho (la de la cifra oficial):
  pobreza                  pobreza monetaria (% de personas); se compara con la referencia de la sesión 16
  pobreza_hogares_am       pobreza monetaria de las personas que viven en hogares con adultos mayores (65+)
  personas_en_hogares_am   % de personas que viven en un hogar con al menos un adulto mayor

Une por código, nunca por nombre: ubigeo[:2] de la base contra FIRST_IDDP del GeoJSON. Exige 25 unidades, todas
con dato, con Lima (15) y Callao (07) separados. Guarda mapas/<indicador>_departamento_<año>.png y su .csv.
"""

import argparse
import sys
import textwrap
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

GEOJSON_URL = ("https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/"
               "sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson")
N_DEPARTAMENTOS = 25
TOLERANCIA_REFERENCIA = 0.1          # puntos: la referencia viene redondeada a un decimal
N_MINIMO = 100                       # hogares en la muestra por departamento; por debajo, se avisa
SUPERFICIE, TINTA, TINTA_2 = "#fcfcfb", "#0b0b0b", "#52514e"
AZUL = LinearSegmentedColormap.from_list("azul", [   # rampa secuencial de la skill dataviz, pasos 100 a 700
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf",
    "#1c5cab", "#184f95", "#104281", "#0d366b"])
DEPARTAMENTOS = {   # solo para rotular: la unión es por código
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho", "06": "Cajamarca",
    "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco", "11": "Ica", "12": "Junín",
    "13": "La Libertad", "14": "Lambayeque", "15": "Lima", "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua",
    "19": "Pasco", "20": "Piura", "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali",
}
INDICADORES = {   # título y unidad de la leyenda
    "pobreza": ("Pobreza monetaria", "Pobreza monetaria (% de personas)"),
    "pobreza_hogares_am": ("Pobreza monetaria en hogares con adultos mayores (65+)",
                           "Pobreza en hogares con adultos mayores (% de personas)"),
    "personas_en_hogares_am": ("Personas que viven en un hogar con adultos mayores (65+)",
                               "Personas en hogares con adultos mayores (% de personas)"),
}


def raiz() -> Path:
    return Path(__file__).resolve().parents[4]       # .claude/skills/mapeando-enaho/scripts -> tarea_4


def cargar_geojson(datos: Path) -> gpd.GeoDataFrame:
    local = datos / "peru_departamental_simple.geojson"
    gdf = gpd.read_file(local if local.exists() else GEOJSON_URL)
    if not local.exists():
        datos.mkdir(parents=True, exist_ok=True)
        gdf.to_file(local, driver="GeoJSON")
    gdf["ccdd"] = gdf["FIRST_IDDP"].astype(str).str.strip().str.zfill(2)
    return gdf


def tabla_departamental(h: pd.DataFrame, indicador: str) -> pd.DataFrame:
    if indicador == "pobreza_hogares_am":
        h, cond = h[h.n_am > 0], "pobre"
    elif indicador == "personas_en_hogares_am":
        h, cond = h.assign(con_am=h.n_am > 0), "con_am"
    else:
        cond = "pobre"
    g = h.assign(_w=h.peso_personas, _x=h.peso_personas * h[cond]).groupby("departamento")
    return pd.DataFrame({"valor": 100 * g._x.sum() / g._w.sum(), "n_muestral": g.size()}).rename_axis("ccdd").reset_index()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--indicador", default="pobreza", choices=list(INDICADORES))
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--salidas", default=None)
    ap.add_argument("--mapas", default=None)
    args = ap.parse_args()

    base_dir = raiz()
    salidas = Path(args.salidas) if args.salidas else base_dir / "salidas"
    ruta = salidas / f"hogares_{args.anio}.parquet"
    if not ruta.exists():
        print(f"No existe {ruta}. Usa primero la skill limpiando-enaho: "
              f"uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio {args.anio}", file=sys.stderr)
        return 3

    tabla = tabla_departamental(pd.read_parquet(ruta), args.indicador)
    gdf = cargar_geojson(base_dir / "datos")
    mapa = gdf.merge(tabla, on="ccdd", how="left", validate="1:1")
    sin_dato = mapa.loc[mapa.valor.isna(), "ccdd"].tolist()
    if len(mapa) != N_DEPARTAMENTOS or sin_dato or set(tabla.ccdd) != set(gdf.ccdd):
        print(f"ERROR: el GeoJSON trae {len(mapa)} polígonos (se esperan {N_DEPARTAMENTOS}); sin dato tras la unión "
              f"por código: {sin_dato}; códigos solo en la base: {sorted(set(tabla.ccdd) - set(gdf.ccdd))}. No se "
              "rellena a mano ni se une por nombre: revisen la limpieza.", file=sys.stderr)
        return 2

    nombre, leyenda = INDICADORES[args.indicador]
    comparacion = None
    if args.indicador == "pobreza":
        ref_csv = Path(__file__).resolve().parents[1] / "referencias" / f"pobreza_departamento_{args.anio}.csv"
        if ref_csv.exists():
            ref = pd.read_csv(ref_csv, dtype={"ccdd": str})
            comparacion = tabla.merge(ref, on="ccdd", validate="1:1", suffixes=("", "_ref"))
            comparacion["diferencia"] = comparacion.valor - comparacion.pobreza_pct
            peor = comparacion.diferencia.abs().max()
            if len(comparacion) != N_DEPARTAMENTOS or peor > TOLERANCIA_REFERENCIA:
                print(f"ERROR: la pobreza departamental difiere hasta {peor:.2f} puntos de la referencia de la sesión "
                      f"16 ({ref_csv.name}); tolerancia {TOLERANCIA_REFERENCIA}.", file=sys.stderr)
                return 2

    # --------------------------------------------------------------------------------------------------- mapa
    mapa["etiqueta"] = mapa.ccdd.map(DEPARTAMENTOS)
    alto, bajo = mapa.loc[mapa.valor.idxmax()], mapa.loc[mapa.valor.idxmin()]
    titulo = textwrap.wrap(f"{nombre}: de {bajo.valor:.1f} % en {bajo.etiqueta} a {alto.valor:.1f} % en "
                           f"{alto.etiqueta}", 58)
    subtitulo = f"Por departamento, Perú {args.anio} (% de personas)"
    pocos = mapa[mapa.n_muestral < N_MINIMO]
    pie = (f"Fuente: INEI, ENAHO {args.anio} (módulos 34 y 02); límites departamentales del repositorio del curso. "
           "Base hogar ponderada con factor07 × mieperho. Unión por código: ubigeo[:2] = FIRST_IDDP; Lima (15) y "
           f"Callao (07) separados. Muestra por departamento: {int(mapa.n_muestral.min()):,} a "
           f"{int(mapa.n_muestral.max()):,} hogares.")
    if len(pocos):
        pie += f" Menos de {N_MINIMO} hogares en: {', '.join(pocos.etiqueta)}; léanse con cautela."
    pie = textwrap.wrap(pie, 105)

    fig = plt.figure(figsize=(7.4, 9.4), facecolor=SUPERFICIE)
    cab = (0.16 + 0.27 * len(titulo) + 0.32) / 9.4
    eje = fig.add_axes((0.02, (0.2 + 0.15 * len(pie)) / 9.4, 0.8, 1 - cab - (0.25 + 0.15 * len(pie)) / 9.4))
    vmax = float(-(-mapa.valor.max() // 5) * 5)                   # hasta el múltiplo de 5 superior
    mapa.plot(column="valor", cmap=AZUL, vmin=0, vmax=vmax, linewidth=0.5, edgecolor=SUPERFICIE, ax=eje)
    eje.set_axis_off()
    # etiquetas selectivas: los dos extremos
    for fila in (alto, bajo):
        p = fila.geometry.representative_point()
        eje.annotate(f"{fila.etiqueta}\n{fila.valor:.1f} %", (p.x, p.y), xytext=(p.x + 1.6, p.y + 0.4),
                     fontsize=8.5, color=TINTA, ha="left",
                     arrowprops={"arrowstyle": "-", "color": TINTA_2, "linewidth": 0.7},
                     bbox={"facecolor": SUPERFICIE, "edgecolor": "none", "pad": 1.2})
    barra = fig.add_axes((0.83, 0.3, 0.025, 0.4))
    sm = plt.cm.ScalarMappable(cmap=AZUL, norm=plt.Normalize(0, vmax))
    cb = fig.colorbar(sm, cax=barra)
    cb.set_label(leyenda, color=TINTA_2, fontsize=9)
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=TINTA_2, labelsize=8.5, length=0)
    fig.text(0.02, 1 - 0.16 / 9.4, "\n".join(titulo), va="top", fontsize=12.5, fontweight="bold", color=TINTA,
             linespacing=1.25)
    fig.text(0.02, 1 - (0.2 + 0.27 * len(titulo)) / 9.4, subtitulo, va="top", fontsize=10, color=TINTA_2)
    fig.text(0.02, 0.08 / 9.4, "\n".join(pie), va="bottom", fontsize=7.4, color=TINTA_2, linespacing=1.3)

    mapas = Path(args.mapas) if args.mapas else base_dir / "mapas"
    mapas.mkdir(parents=True, exist_ok=True)
    destino = mapas / f"{args.indicador}_departamento_{args.anio}.png"
    fig.savefig(destino, dpi=200, facecolor=SUPERFICIE)
    plt.close(fig)
    salida_csv = mapa[["ccdd", "etiqueta", "valor", "n_muestral"]].rename(columns={"etiqueta": "departamento"})
    salida_csv.sort_values("ccdd").round(4).to_csv(destino.with_suffix(".csv"), index=False, encoding="utf-8")

    orden = mapa.sort_values("valor", ascending=False)
    listar = lambda sub: ", ".join(f"{n} {v:.1f} %" for n, v in zip(sub.etiqueta, sub.valor))
    print(f"{nombre} por departamento, {args.anio} (base hogar, factor07 × mieperho)")
    print(f"  {len(mapa)} unidades territoriales unidas por código, ninguna sin dato")
    print(f"  más alto : {listar(orden.head(3))}")
    print(f"  más bajo : {listar(orden.tail(3).iloc[::-1])}")
    if comparacion is not None:
        print(f"  contra la referencia de la sesión 16: diferencia máxima {comparacion.diferencia.abs().max():.3f} "
              f"puntos, mediana {comparacion.diferencia.abs().median():.3f} (tolerancia {TOLERANCIA_REFERENCIA})")
    if len(pocos):
        print(f"  aviso: menos de {N_MINIMO} hogares en la muestra en {listar(pocos)}")
    rel = destino.relative_to(base_dir).as_posix()
    print(f"\nGuardado en {rel} (200 dpi) y las cifras en {Path(rel).with_suffix('.csv').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
