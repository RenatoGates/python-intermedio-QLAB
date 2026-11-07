"""Gráficos de barras de la ENAHO a partir de las bases limpias (versión tarea_4).

    uv run .claude/skills/graficando-enaho/scripts/graficar.py --corte area --indicador pobreza     # desde tarea_4/

Cortes de hogar (base hogar, factor07 × mieperho, la de la cifra oficial):
  area, departamento, tipo_hogar (con o sin adultos mayores de 65+), tipo_hogar_area (tipo de hogar × área)
Cortes de persona (base persona, facpob07, cifra secundaria): sexo, edad
Indicadores: pobreza, extrema, alimentos (participación de los alimentos en el gasto; solo cortes de hogar)

Guarda figuras/<indicador>_<corte>_<año>.png y, al lado, el .csv con las cifras graficadas.
"""

import argparse
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Paleta de referencia de la skill dataviz (validada con validate_palette.js)
SUPERFICIE, TINTA, TINTA_2, GRILLA = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
SERIE = ["#2a78d6", "#eb6834", "#1baf7a"]                              # categórica, slots 1 a 3
ORDINAL = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]     # rampa ordinal azul (grupos de edad)
BINS_EDAD = [-1, 14, 24, 44, 64, 200]
ETIQUETAS_EDAD = ["0 a 14", "15 a 24", "25 a 44", "45 a 64", "65 a más"]
DEPARTAMENTOS = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho", "06": "Cajamarca",
    "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco", "11": "Ica", "12": "Junín",
    "13": "La Libertad", "14": "Lambayeque", "15": "Lima", "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua",
    "19": "Pasco", "20": "Piura", "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali",
}
TIPOS_HOGAR = ["Sin adultos mayores", "Con adultos mayores y menores de 65", "Solo adultos mayores"]
CORTES_HOGAR = {"area", "departamento", "tipo_hogar", "tipo_hogar_area"}
INDICADORES = {   # nombre, columna, unidad, cómo se agrega
    "pobreza": ("Pobreza monetaria", "pobre", "% de personas", "pct"),
    "extrema": ("Pobreza extrema", "pobre_extremo", "% de personas", "pct"),
    "alimentos": ("Participación de los alimentos en el gasto", "part_alimentos", "% del gasto del hogar", "media"),
}
DESCRIPCION_CORTE = {"area": "según área de residencia", "departamento": "por departamento",
                     "tipo_hogar": "según presencia de adultos mayores (65+) en el hogar",
                     "tipo_hogar_area": "según presencia de adultos mayores (65+) y área",
                     "sexo": "según sexo", "edad": "según grupo de edad"}


def raiz() -> Path:
    return Path(__file__).resolve().parents[4]       # .claude/skills/graficando-enaho/scripts -> tarea_4


def agregar(df: pd.DataFrame, por, columna: str, peso: str, como: str) -> pd.DataFrame:
    g = df.assign(_w=df[peso], _x=df[peso] * df[columna].astype(float)).groupby(por, observed=True)
    t = pd.DataFrame({"valor": g["_x"].sum() / g["_w"].sum(), "n_muestral": g.size()})
    if como == "pct":
        t["valor"] *= 100
    return t


def preparar(corte: str, hogares: pd.DataFrame | None, personas: pd.DataFrame | None):
    """Devuelve (base, columna o columnas del corte, peso, texto de la base)."""
    if corte in CORTES_HOGAR:
        h = hogares.assign(area=hogares.urbano.map({True: "Urbano", False: "Rural"}),
                           dep=hogares.departamento.map(DEPARTAMENTOS),
                           tipo=pd.Categorical(hogares.tipo_hogar_am, TIPOS_HOGAR, ordered=True))
        por = {"area": "area", "departamento": "dep", "tipo_hogar": "tipo", "tipo_hogar_area": ["tipo", "area"]}[corte]
        return h, por, "peso_personas", "Base hogar ponderada con factor07 × mieperho (la de la cifra oficial)"
    p = personas.assign(sexo=personas.p207.map({1: "Hombres", 2: "Mujeres"}),
                        edad=pd.cut(personas.p208a, BINS_EDAD, labels=ETIQUETAS_EDAD))
    return p, corte, "facpob07", "Base persona ponderada con facpob07 (secundaria: no es la base de la cifra oficial)"


def titular(tabla: pd.DataFrame, corte: str, nombre: str) -> str:
    """Un título que dice lo que muestra el gráfico, calculado con las cifras, no escrito a mano."""
    if corte == "tipo_hogar_area":
        t = tabla.valor.unstack()
        brecha = (t["Rural"] - t["Urbano"])
        return (f"{nombre}: la brecha rural-urbana va de {brecha.min():.1f} a {brecha.max():.1f} puntos "
                "según el tipo de hogar")
    s = tabla.valor
    alto, bajo = s.idxmax(), s.idxmin()
    if corte == "departamento":
        return f"{nombre}: de {s[bajo]:.1f} % en {bajo} a {s[alto]:.1f} % en {alto}"
    return f"{nombre}: {s[alto]:.1f} % en «{alto}» y {s[bajo]:.1f} % en «{bajo}», {s[alto] - s[bajo]:.1f} puntos de diferencia"


def estilo(eje):
    eje.set_facecolor(SUPERFICIE)
    for lado in ("top", "right", "bottom"):
        eje.spines[lado].set_visible(False)
    eje.spines["left"].set_color(GRILLA)
    eje.tick_params(length=0, colors=TINTA_2, labelsize=9.5)
    eje.grid(axis="x", color=GRILLA, linewidth=0.8, linestyle="-")
    eje.set_axisbelow(True)


def graficar(tabla, corte, indicador, anio, texto_base, nacional, destino):
    """Maqueta en pulgadas: la barra tiene el mismo grosor con 2 o con 25 filas, y el texto se parte en líneas
    en vez de salirse del borde."""
    nombre, _, unidad, _ = INDICADORES[indicador]
    agrupado = corte == "tipo_hogar_area"
    filas = list(tabla.index.get_level_values(0).unique() if agrupado else tabla.index)
    n = int(tabla.n_muestral.sum())
    titulo = textwrap.wrap(titular(tabla, corte, nombre), 76)
    subtitulo = textwrap.wrap(f"{nombre} {DESCRIPCION_CORTE[corte]}, Perú {anio} ({unidad})", 100)
    pie = textwrap.wrap(f"Fuente: INEI, ENAHO {anio} (módulos 34 y 02). {texto_base}. n = {n:,} "
                        f"{'hogares' if corte in CORTES_HOGAR else 'residentes'} en la muestra.", 135)

    ancho, fila_in = 8.6, (0.62 if agrupado else 0.40)
    alto_plot = len(filas) * fila_in + 0.35
    cabeza = 0.16 + 0.25 * len(titulo) + 0.20 * len(subtitulo) + 0.14 + (0.3 if agrupado else 0)   # fila de leyenda
    pies = 0.5 + 0.15 * len(pie) + 0.08
    alto = alto_plot + cabeza + pies
    izquierda = 0.3 + 0.074 * max(len(str(f)) for f in filas)
    fig = plt.figure(figsize=(ancho, alto), facecolor=SUPERFICIE)
    eje = fig.add_axes((izquierda / ancho, pies / alto, 1 - (izquierda + 0.45) / ancho, alto_plot / alto))
    estilo(eje)

    maximo = float(tabla.valor.max())
    y = np.arange(len(filas))
    caja = {"facecolor": SUPERFICIE, "edgecolor": "none", "pad": 0.6}       # la línea de referencia pasa detrás
    if agrupado:
        t = tabla.valor.unstack().reindex(filas)
        for i, (area, color) in enumerate(zip(["Urbano", "Rural"], SERIE)):
            pos = y + (i - 0.5) * 0.36
            eje.barh(pos, t[area], height=0.3, color=color, label=area, zorder=2)
            for yy, v in zip(pos, t[area]):
                eje.text(v + maximo * 0.012, yy, f"{v:.1f} %", va="center", fontsize=9, color=TINTA, bbox=caja,
                         zorder=4)
        eje.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, frameon=False, fontsize=9.5,
                   labelcolor=TINTA, handlelength=1.2, borderaxespad=0.2)   # en una fila sobre el gráfico
    else:
        colores = ORDINAL if corte == "edad" else SERIE[0]
        eje.barh(y, tabla.valor, height=0.5, color=colores, zorder=2)
        for yy, v in zip(y, tabla.valor):
            eje.text(v + maximo * 0.012, yy, f"{v:.1f} %", va="center", fontsize=9.5, color=TINTA, bbox=caja,
                     zorder=4)
    if nacional is not None:
        eje.axvline(nacional, color=TINTA_2, linewidth=1, zorder=3)
        eje.text(nacional + maximo * 0.008, -0.62, f"Perú {nacional:.1f} %", color=TINTA_2, fontsize=8.5,
                 va="center")
    eje.set_yticks(y, [str(f) for f in filas], color=TINTA, fontsize=9.5)
    eje.set_ylim(len(filas) - 0.5, -0.9)
    eje.set_xlim(0, maximo * 1.17)
    eje.set_xlabel(unidad, color=TINTA_2, fontsize=9)

    x0 = 0.15 / ancho
    fig.text(x0, 1 - 0.16 / alto, "\n".join(titulo), va="top", fontsize=12.5, fontweight="bold", color=TINTA,
             linespacing=1.25)
    fig.text(x0, 1 - (0.16 + 0.25 * len(titulo) + 0.06) / alto, "\n".join(subtitulo), va="top", fontsize=10,
             color=TINTA_2, linespacing=1.3)
    fig.text(x0, 0.08 / alto, "\n".join(pie), va="bottom", fontsize=7.6, color=TINTA_2, linespacing=1.3)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=200, facecolor=SUPERFICIE)
    plt.close(fig)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--corte", default="area", choices=sorted(CORTES_HOGAR | {"sexo", "edad"}))
    ap.add_argument("--indicador", default="pobreza", choices=list(INDICADORES))
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--salidas", default=None)
    ap.add_argument("--figuras", default=None)
    args = ap.parse_args()

    if args.indicador == "alimentos" and args.corte not in CORTES_HOGAR:
        print("La participación de los alimentos es un dato del hogar: úsenla con area, departamento, tipo_hogar "
              "o tipo_hogar_area.", file=sys.stderr)
        return 2
    base_dir = raiz()
    salidas = Path(args.salidas) if args.salidas else base_dir / "salidas"
    nombre_base = "hogares" if args.corte in CORTES_HOGAR else "personas"
    ruta = salidas / f"{nombre_base}_{args.anio}.parquet"
    if not ruta.exists():
        print(f"No existe {ruta.relative_to(base_dir) if ruta.is_relative_to(base_dir) else ruta}. Usa primero la "
              f"skill limpiando-enaho: uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio {args.anio}",
              file=sys.stderr)
        return 3

    base = pd.read_parquet(ruta)
    df, por, peso, texto_base = preparar(args.corte, base if nombre_base == "hogares" else None,
                                         base if nombre_base == "personas" else None)
    _, columna, unidad, como = INDICADORES[args.indicador]
    tabla = agregar(df, por, columna, peso, como)
    if args.corte in ("area", "departamento", "sexo"):
        tabla = tabla.sort_values("valor", ascending=False)
    total = agregar(df.assign(_todo="Perú"), "_todo", columna, peso, como).valor.iloc[0]
    nacional = None if args.corte == "tipo_hogar_area" else float(total)

    figuras = Path(args.figuras) if args.figuras else base_dir / "figuras"
    destino = figuras / f"{args.indicador}_{args.corte}_{args.anio}.png"
    graficar(tabla, args.corte, args.indicador, args.anio, texto_base, nacional, destino)
    tabla.round(4).to_csv(destino.with_suffix(".csv"), encoding="utf-8")

    print(f"{INDICADORES[args.indicador][0]} {DESCRIPCION_CORTE[args.corte]}, {args.anio} ({unidad})")
    print(f"  {texto_base}")
    for k, fila in tabla.iterrows():
        etiqueta = " · ".join(k) if isinstance(k, tuple) else k
        print(f"  {etiqueta}: {fila.valor:.1f} % (n = {int(fila.n_muestral):,})")
    print(f"  Perú: {total:.1f} %")
    rel = destino.relative_to(base_dir).as_posix() if destino.is_relative_to(base_dir) else destino
    print(f"\nGuardado en {rel} (200 dpi) y las cifras en {Path(rel).with_suffix('.csv').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
