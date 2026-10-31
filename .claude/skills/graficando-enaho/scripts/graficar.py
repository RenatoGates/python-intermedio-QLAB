"""Gráficos de barras de la pobreza monetaria a partir de la base limpia de la ENAHO."""

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

COLOR = "#b1491f"
FUENTE = "Fuente: INEI, ENAHO {anio}"
BINS_EDAD = [0, 14, 24, 44, 64, 200]
ETIQUETAS_EDAD = ["0 a 14", "15 a 24", "25 a 44", "45 a 64", "65 a más"]


def raiz_repo() -> Path:
    return Path(__file__).resolve().parents[4]


def pobreza_por(base: pd.DataFrame, columna: str, peso: str) -> pd.Series:
    g = base.assign(_w=base[peso], _p=base[peso] * base["pobre"]).groupby(columna, observed=True)
    return 100 * g["_p"].sum() / g["_w"].sum()


def preparar(base: pd.DataFrame, corte: str) -> tuple[pd.DataFrame, str, str, bool]:
    if corte == "area":
        base = base.assign(_cat=base["urbano"].map({True: "Urbano", False: "Rural"}))
        return base, "Pobreza monetaria según área de residencia", "_cat", True
    if corte == "sexo":
        base = base.assign(_cat=base["p207"].map({1: "Hombres", 2: "Mujeres"}))
        return base, "Pobreza monetaria según sexo", "_cat", True
    if corte == "edad":
        base = base.assign(
            _cat=pd.cut(base["p208a"], bins=BINS_EDAD, labels=ETIQUETAS_EDAD, right=True)
        )
        return base, "Pobreza monetaria según grupo de edad", "_cat", False
    if corte == "departamento":
        return base, "Pobreza monetaria por departamento", "departamento", True
    raise ValueError(f"Corte desconocido: {corte}")


def graficar(serie: pd.Series, titulo: str, anio: int, destino: Path) -> None:
    alto = max(3.2, 0.52 * len(serie) + 1.8)
    fig, eje = plt.subplots(figsize=(8.2, alto))
    eje.barh(serie.index.astype(str), serie.values, color=COLOR, height=0.62)
    eje.set_xlim(0, max(serie.values) * 1.18)
    eje.invert_yaxis()
    for y, v in enumerate(serie.values):
        eje.text(v + max(serie.values) * 0.015, y, f"{v:.1f} %", va="center", fontsize=9.5)
    eje.set_xlabel("% de personas")
    eje.set_title(f"{titulo}, {anio}", loc="left", fontsize=13, fontweight="bold", pad=12)
    for lado in ("top", "right"):
        eje.spines[lado].set_visible(False)
    eje.spines["left"].set_color("#999999")
    eje.spines["bottom"].set_color("#999999")
    eje.tick_params(length=0)
    eje.grid(axis="x", color="#dddddd", linewidth=0.7)
    eje.set_axisbelow(True)
    fig.text(0.01, 0.015, FUENTE.format(anio=anio), fontsize=8, color="#666666")
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=200)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corte", default="area", choices=["area", "sexo", "edad", "departamento"])
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--base", default=None)
    ap.add_argument("--figuras", default=None)
    args = ap.parse_args()

    raiz = raiz_repo()
    ruta = Path(args.base) if args.base else raiz / "salidas" / f"personas_{args.anio}.parquet"
    if not ruta.exists():
        print(
            f"No existe {ruta}. Usa primero la skill limpiando-enaho.",
            file=sys.stderr,
        )
        return 1

    base = pd.read_parquet(ruta)
    peso = "facpob07" if "facpob07" in base.columns else "factor07"
    base, titulo, columna, ordenar_por_valor = preparar(base, args.corte)

    serie = pobreza_por(base, columna, peso).dropna()
    serie = serie.sort_values(ascending=False) if ordenar_por_valor else serie

    figuras = Path(args.figuras) if args.figuras else raiz / "figuras"
    destino = figuras / f"pobreza_{args.corte}_{args.anio}.png"
    graficar(serie, titulo, args.anio, destino)

    print(f"{titulo}, {args.anio} (ponderado con {peso})")
    for k, v in serie.items():
        print(f"  {k}: {v:.1f} %")
    print(f"\nGuardado en {destino.relative_to(raiz)} a 200 dpi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
