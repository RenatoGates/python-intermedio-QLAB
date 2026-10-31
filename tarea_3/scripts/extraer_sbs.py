"""Extrae los cuadros departamentales del Reporte de Indicadores de Inclusión Financiera (SBS)."""

import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd
import pdfplumber

DEPARTAMENTOS = {
    "AMAZONAS": "01", "ANCASH": "02", "APURIMAC": "03", "AREQUIPA": "04",
    "AYACUCHO": "05", "CAJAMARCA": "06", "CALLAO": "07", "CUSCO": "08",
    "HUANCAVELICA": "09", "HUANUCO": "10", "ICA": "11", "JUNIN": "12",
    "LA LIBERTAD": "13", "LAMBAYEQUE": "14", "LIMA": "15", "LORETO": "16",
    "MADRE DE DIOS": "17", "MOQUEGUA": "18", "PASCO": "19", "PIURA": "20",
    "PUNO": "21", "SAN MARTIN": "22", "TACNA": "23", "TUMBES": "24",
    "UCAYALI": "25",
}
NUM = re.compile(r"-?\d[\d,]*\.?\d*")


def clave(texto: str) -> str:
    d = unicodedata.normalize("NFD", texto)
    return " ".join("".join(c for c in d if unicodedata.category(c) != "Mn").upper().split())


def numeros(resto: str) -> list[float]:
    return [float(m.group().replace(",", "")) for m in NUM.finditer(resto)]


def fila_departamento(linea: str) -> tuple[str, list[float]] | None:
    """Separa el nombre del departamento de sus cifras, tolerando el nombre repetido."""
    texto = linea.strip()
    if not texto:
        return None
    corte = NUM.search(texto)
    if not corte:
        return None
    nombre, resto = texto[: corte.start()], texto[corte.start():]
    k = clave(nombre)
    if k.startswith("NACIONAL"):
        return "NACIONAL", numeros(resto)
    for dep in DEPARTAMENTOS:
        if k.startswith(dep):
            return dep, numeros(resto)
    return None


def tabla(pdf, pagina: int, columnas: list[str]) -> pd.DataFrame:
    filas = []
    for linea in (pdf.pages[pagina - 1].extract_text() or "").split("\n"):
        par = fila_departamento(linea)
        if not par:
            continue
        dep, vals = par
        if len(vals) < len(columnas):
            continue
        filas.append([dep] + vals[: len(columnas)])
    df = pd.DataFrame(filas, columns=["departamento"] + columnas).drop_duplicates("departamento")
    df["ccdd"] = df["departamento"].map(DEPARTAMENTOS)
    return df


COLS_RED = [
    "oficinas_21", "oficinas_26", "atm_21", "atm_26",
    "corresp_21", "corresp_26", "puntos_21", "puntos_26",
    "canales_km2_21", "canales_km2_26",
]
COLS_USO = ["deudores_pct_21", "deudores_pct_26"]
COLS_CUENTAS = ["cuentas_pct_20", "cuentas_pct_25"]


def main() -> int:
    pdf_path = Path(sys.argv[1] if len(sys.argv) > 1 else "ciif_jn2026.pdf")
    salida = Path("datos")
    salida.mkdir(exist_ok=True)

    with pdfplumber.open(pdf_path) as pdf:
        red = tabla(pdf, 12, COLS_RED)
        infra = tabla(pdf, 15, COLS_RED)

        # p25 trae dos tablas lado a lado: deudores a la izquierda, cuentas a la derecha
        filas_uso = []
        for linea in (pdf.pages[24].extract_text() or "").split("\n"):
            par = fila_departamento(linea)
            if par and len(par[1]) >= 4:
                filas_uso.append([par[0]] + par[1][:4])
        uso = pd.DataFrame(
            filas_uso, columns=["departamento"] + COLS_USO + COLS_CUENTAS
        ).drop_duplicates("departamento")
        uso["ccdd"] = uso["departamento"].map(DEPARTAMENTOS)

    for nombre, df in [("red", red), ("infraestructura", infra), ("uso", uso)]:
        n_dep = df["ccdd"].notna().sum()
        print(f"{nombre:16s} {len(df):3d} filas | {n_dep} departamentos | nacional: "
              f"{'sí' if (df['departamento'] == 'NACIONAL').any() else 'NO'}")
        df.to_csv(salida / f"sbs_{nombre}.csv", index=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
