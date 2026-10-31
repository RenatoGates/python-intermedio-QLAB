"""Pipeline de limpieza de la ENAHO: módulos 34 (sumaria) y 02 (miembros)."""

import argparse
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]
LLAVES_PERSONA = LLAVES_HOGAR + ["codperso"]
POBREZA_OFICIAL = {2024: 27.6}
EXTREMA_OFICIAL = {2024: 5.5}
TOLERANCIA = 0.1


def raiz_repo() -> Path:
    return Path(__file__).resolve().parents[4]


def sin_tildes(texto: str) -> str:
    desc = unicodedata.normalize("NFD", texto)
    return "".join(c for c in desc if unicodedata.category(c) != "Mn")


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    nuevos = {}
    for col in df.columns:
        limpio = sin_tildes(str(col)).lower().strip()
        nuevos[col] = "anio" if limpio == "ano" else limpio
    return df.rename(columns=nuevos)


def descomprimir(datos: Path) -> None:
    for z in sorted(datos.glob("*.zip")):
        with zipfile.ZipFile(z) as zf:
            zf.extractall(datos / z.stem)


def buscar_dta(datos: Path, patron: str) -> Path:
    rx = re.compile(patron, re.IGNORECASE)
    candidatos = [p for p in datos.rglob("*.dta") if rx.search(p.name)]
    if not candidatos:
        raise FileNotFoundError(
            f"No encontré ningún .dta que coincida con '{patron}' dentro de {datos}. "
            "Baja los zip del INEI (966-Modulo34.zip y 966-Modulo02.zip) a esa carpeta."
        )
    return max(candidatos, key=lambda p: p.stat().st_size)


def leer(ruta: Path, llaves: list[str]) -> pd.DataFrame:
    df = pd.read_stata(ruta, convert_categoricals=False)
    df = normalizar_columnas(df)
    for k in llaves:
        if k in df.columns:
            df[k] = df[k].astype(str).str.strip()
    if "ubigeo" in df.columns:
        df["ubigeo"] = df["ubigeo"].astype(str).str.strip().str.zfill(6)
    return df


def pct_ponderado(df: pd.DataFrame, condicion: pd.Series, peso: str) -> float:
    w = df[peso]
    total = w.sum()
    return float(100 * w[condicion].sum() / total) if total else float("nan")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--datos", default=None)
    ap.add_argument("--salidas", default=None)
    args = ap.parse_args()

    raiz = raiz_repo()
    datos = Path(args.datos) if args.datos else raiz / "datos"
    salidas = Path(args.salidas) if args.salidas else raiz / "salidas"
    salidas.mkdir(parents=True, exist_ok=True)

    if not datos.exists():
        print(f"Falta la carpeta {datos}.", file=sys.stderr)
        return 1

    descomprimir(datos)
    ruta_sumaria = buscar_dta(datos, r"sumaria")
    ruta_personas = buscar_dta(datos, r"(enaho01[-_]?\d{4}[-_]?200|modulo0?2)")

    sumaria = leer(ruta_sumaria, LLAVES_HOGAR)
    personas = leer(ruta_personas, LLAVES_PERSONA)
    n_personas_crudo = len(personas)
    n_hogares = len(sumaria)

    residentes = (
        (personas["p204"] == 1) & (personas["p205"] == 2)
    ) | ((personas["p204"] == 2) & (personas["p206"] == 1))
    personas = personas.loc[residentes].copy()
    n_residentes = len(personas)

    cols_sumaria = [
        c
        for c in ["pobreza", "mieperho", "factor07", "ubigeo", "estrato", "dominio"]
        if c in sumaria.columns
    ]
    base = personas.merge(
        sumaria[LLAVES_HOGAR + cols_sumaria],
        on=LLAVES_HOGAR,
        how="inner",
        validate="m:1",
        suffixes=("", "_hog"),
    )

    base["departamento"] = base["ubigeo"].str[:2]
    base["urbano"] = base["estrato"] <= 5
    base["pobre"] = base["pobreza"] <= 2
    base["pobre_extremo"] = base["pobreza"] == 1

    peso = "facpob07" if "facpob07" in base.columns else "factor07"

    sumaria["peso_personas"] = sumaria["factor07"] * sumaria["mieperho"]
    pob_sumaria = pct_ponderado(sumaria, sumaria["pobreza"] <= 2, "peso_personas")
    ext_sumaria = pct_ponderado(sumaria, sumaria["pobreza"] == 1, "peso_personas")
    pob_personas = pct_ponderado(base, base["pobre"], peso)
    ext_personas = pct_ponderado(base, base["pobre_extremo"], peso)
    pob_urbano = pct_ponderado(base[base["urbano"]], base.loc[base["urbano"], "pobre"], peso)
    pob_rural = pct_ponderado(base[~base["urbano"]], base.loc[~base["urbano"], "pobre"], peso)

    oficial = POBREZA_OFICIAL.get(args.anio)
    oficial_ext = EXTREMA_OFICIAL.get(args.anio)

    assert not sumaria.duplicated(LLAVES_HOGAR).any(), "Llaves de hogar duplicadas en la sumaria"
    assert not base.duplicated(LLAVES_PERSONA).any(), "Llaves de persona duplicadas tras la unión"
    assert len(base) == n_residentes, (
        f"La unión cambió el número de filas: {n_residentes} residentes -> {len(base)}"
    )
    if oficial is not None:
        assert abs(pob_sumaria - oficial) < TOLERANCIA, (
            f"Pobreza con la sumaria {pob_sumaria:.2f} % difiere del INEI ({oficial} %)"
        )
        assert abs(pob_personas - oficial) < TOLERANCIA, (
            f"Pobreza con personas {pob_personas:.2f} % difiere del INEI ({oficial} %)"
        )

    destino = salidas / f"personas_{args.anio}.parquet"
    base.to_parquet(destino, index=False)

    por_dep = (
        base.assign(_w=base[peso], _p=base[peso] * base["pobre"])
        .groupby("departamento")[["_w", "_p"]]
        .sum()
        .assign(pobreza_pct=lambda d: 100 * d["_p"] / d["_w"])
        .sort_values("pobreza_pct", ascending=False)
    )

    lineas = [
        f"ENAHO {args.anio} · validación de la limpieza",
        "",
        f"Sumaria   : {ruta_sumaria.name} ({n_hogares:,} hogares)",
        f"Miembros  : {ruta_personas.name} ({n_personas_crudo:,} filas)",
        f"Residentes habituales: {n_residentes:,}",
        f"Base final: {len(base):,} filas x {base.shape[1]} columnas -> {destino.name}",
        f"Factor de expansión usado: {peso}",
        "",
        "Pobreza monetaria",
        f"  sumaria (factor07 x mieperho): {pob_sumaria:.2f} %",
        f"  personas ({peso})           : {pob_personas:.2f} %",
        f"  oficial INEI                 : {oficial} %" if oficial else "  oficial INEI: sin referencia",
        "",
        "Pobreza extrema",
        f"  sumaria : {ext_sumaria:.2f} %",
        f"  personas: {ext_personas:.2f} %",
        f"  oficial : {oficial_ext} %" if oficial_ext else "  oficial: sin referencia",
        "",
        f"Urbano (estrato <= 5): {pob_urbano:.1f} %",
        f"Rural  (estrato >  5): {pob_rural:.1f} %",
        "",
        f"Departamentos con dato: {por_dep.shape[0]} de 25",
        "  más pobres : " + ", ".join(f"{i} {v:.1f} %" for i, v in por_dep["pobreza_pct"].head(3).items()),
        "  menos pobres: " + ", ".join(f"{i} {v:.1f} %" for i, v in por_dep["pobreza_pct"].tail(3).items()),
        "",
        "Comprobaciones",
        "  [ok] llaves de hogar únicas en la sumaria",
        "  [ok] llaves de persona únicas tras la unión",
        "  [ok] la unión no perdió ni duplicó filas",
        f"  [ok] pobreza dentro de {TOLERANCIA} puntos de la cifra oficial" if oficial else "",
    ]
    texto = "\n".join(l for l in lineas if l != "")
    (salidas / "validacion.txt").write_text(texto + "\n", encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
