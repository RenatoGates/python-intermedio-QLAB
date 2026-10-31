"""Mapa coroplético de la pobreza monetaria por departamento a partir de la base limpia."""

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

GEOJSON_URL = (
    "https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/"
    "sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson"
)
N_DEPARTAMENTOS = 25


def raiz_repo() -> Path:
    return Path(__file__).resolve().parents[4]


def cargar_geojson(datos: Path) -> gpd.GeoDataFrame:
    local = datos / "peru_departamental_simple.geojson"
    gdf = gpd.read_file(local if local.exists() else GEOJSON_URL)
    if not local.exists():
        datos.mkdir(parents=True, exist_ok=True)
        gdf.to_file(local, driver="GeoJSON")
    gdf["ccdd"] = gdf["FIRST_IDDP"].astype(str).str.strip().str.zfill(2)
    return gdf


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--base", default=None)
    ap.add_argument("--mapas", default=None)
    args = ap.parse_args()

    raiz = raiz_repo()
    ruta = Path(args.base) if args.base else raiz / "salidas" / f"personas_{args.anio}.parquet"
    if not ruta.exists():
        print(f"No existe {ruta}. Usa primero la skill limpiando-enaho.", file=sys.stderr)
        return 1

    base = pd.read_parquet(ruta)
    peso = "facpob07" if "facpob07" in base.columns else "factor07"

    tabla = (
        base.assign(_w=base[peso], _p=base[peso] * base["pobre"])
        .groupby("departamento")[["_w", "_p"]]
        .sum()
        .assign(pobreza_pct=lambda d: 100 * d["_p"] / d["_w"])
        .reset_index()
        .rename(columns={"departamento": "ccdd"})
    )
    tabla["ccdd"] = tabla["ccdd"].astype(str).str.zfill(2)

    gdf = cargar_geojson(raiz / "datos")
    mapa = gdf.merge(tabla[["ccdd", "pobreza_pct"]], on="ccdd", how="left", validate="1:1")

    sin_dato = mapa.loc[mapa["pobreza_pct"].isna(), "ccdd"].tolist()
    assert len(mapa) == N_DEPARTAMENTOS, f"El GeoJSON trae {len(mapa)} polígonos, no {N_DEPARTAMENTOS}"
    assert not sin_dato, f"Departamentos sin dato tras la unión por código: {sin_dato}"

    fig, eje = plt.subplots(figsize=(7.2, 8.4))
    mapa.plot(
        column="pobreza_pct",
        cmap="Oranges",
        vmin=0,
        vmax=float(mapa["pobreza_pct"].max()),
        linewidth=0.4,
        edgecolor="#ffffff",
        legend=True,
        legend_kwds={
            "label": "Pobreza monetaria (% de personas)",
            "shrink": 0.55,
            "pad": 0.01,
        },
        ax=eje,
    )
    eje.set_title(
        f"Pobreza monetaria por departamento, {args.anio}",
        loc="left",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    eje.axis("off")
    fig.text(
        0.01,
        0.015,
        f"Fuente: INEI, ENAHO {args.anio}. Ponderado con {peso}. "
        "Lima (15) y Callao (07) van separados.",
        fontsize=8,
        color="#666666",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 1))

    mapas = Path(args.mapas) if args.mapas else raiz / "mapas"
    mapas.mkdir(parents=True, exist_ok=True)
    destino = mapas / "pobreza_departamento.png"
    fig.savefig(destino, dpi=200)
    plt.close(fig)

    etiqueta = next(
        (c for c in ("NOMBDEP", "FIRST_NOMB", "DEPARTAMEN", "NOMBRE") if c in mapa.columns),
        "ccdd",
    )
    orden = mapa.sort_values("pobreza_pct", ascending=False)[[etiqueta, "pobreza_pct"]]

    def listar(sub):
        return ", ".join(f"{n} {v:.1f} %" for n, v in zip(sub[etiqueta], sub["pobreza_pct"]))

    print(f"Pobreza monetaria por departamento, {args.anio} (ponderado con {peso})")
    print(f"  {len(mapa)} departamentos, ninguno sin dato")
    print("  más pobreza  : " + listar(orden.head(3)))
    print("  menos pobreza: " + listar(orden.tail(3).iloc[::-1]))

    ref = raiz / "referencias" / "pobreza_departamento_2024.csv"
    if ref.exists() and args.anio == 2024:
        oficial = pd.read_csv(ref, dtype={"ccdd": str})
        cmp = tabla.merge(oficial, on="ccdd", validate="1:1")
        cmp["dif"] = (cmp["pobreza_pct_x"] - cmp["pobreza_pct_y"]).abs()
        print(f"\nContra la referencia del INEI: diferencia máxima {cmp['dif'].max():.1f} puntos "
              f"(mediana {cmp['dif'].median():.1f})")

    print(f"\nGuardado en {destino.relative_to(raiz)} a 200 dpi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
