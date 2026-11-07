"""Exposición de los hogares a la inflación de alimentos, según la presencia de adultos mayores (65+).

Contribución aproximada de los alimentos a la inflación del hogar, en puntos porcentuales:

    contribucion_pp = part_alimentos × inflación de alimentos a 12 meses / 100

- part_alimentos: % del gasto del hogar que va a alimentos (ENAHO 2024, base hogar, factor07 × mieperho), tomado de
  salidas/indicadores.csv, que generó la skill limpiando-enaho.
- inflación de alimentos: PN09822PM (IPC Alimentos y Bebidas de Lima Metropolitana, var. % 12 meses), tomada del CSV
  que dejó la herramienta graficar_series del MCP bcrp en figuras/.

No descarga nada ni escribe cifras a mano: solo lee esos dos archivos. Desde tarea_4/:

    uv run python informes/calculos_exposicion.py
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
INDICADORES = RAIZ / "salidas" / "indicadores.csv"
BCRP = RAIZ / "figuras" / "bcrp_inflacion_tasa_2021_2026.csv"

ALIM, TOTAL, TASA = "PN09822PM", "PN01273PM", "PD04722MM"
TIPOS = ["Sin adultos mayores", "Con adultos mayores y menores de 65", "Solo adultos mayores"]
TAMANOS = ["1 persona", "2 personas", "3 a 4 personas", "5 o más personas"]
AREAS = ["Urbano", "Rural"]
N_MIN = 100  # celdas con menos hogares en la muestra se marcan como no confiables
BASE = "sin AM"  # grupo de comparación: hogares sin adultos mayores


def contribucion(part_alimentos: float, inflacion_alimentos: float) -> float:
    """Puntos porcentuales de inflación del hogar que aportan los alimentos."""
    return part_alimentos * inflacion_alimentos / 100


def valor(ind: pd.DataFrame, indicador: str, corte: str, grupo: str) -> tuple[float, int]:
    fila = ind[(ind.indicador == indicador) & (ind.corte == corte) & (ind.grupo == grupo)]
    if len(fila) != 1:
        raise SystemExit(f"No encuentro una sola fila para {indicador} / {corte} / {grupo} en {INDICADORES}")
    return float(fila.valor.iloc[0]), int(fila.n_muestral.iloc[0])


def corto(tipo: str) -> str:
    return {"Sin adultos mayores": "sin AM", "Con adultos mayores y menores de 65": "AM + menores de 65",
            "Solo adultos mayores": "solo AM"}[tipo]


def main() -> None:
    ind = pd.read_csv(INDICADORES)
    bcrp = pd.read_csv(BCRP, dtype={"periodo": str})

    # ------------------------------------------------------------------------------------------- BCRP
    con_dato = bcrp.dropna(subset=[ALIM])
    ultimo = con_dato.iloc[-1]
    pico = con_dato.loc[con_dato[ALIM].idxmax()]
    pi_ult, pi_pico = float(ultimo[ALIM]), float(pico[ALIM])
    print("=" * 100)
    print(f"BCRP · {BCRP.relative_to(RAIZ).as_posix()} ({con_dato.periodo.iloc[0]} a {ultimo.periodo}, "
          f"{len(con_dato)} meses)")
    print(f"  Último mes con dato: {ultimo.periodo}")
    print(f"    {ALIM} inflación de alimentos y bebidas, Lima, 12 meses : {pi_ult:.2f} %")
    print(f"    {TOTAL} inflación total, Lima, 12 meses                  : {float(ultimo[TOTAL]):.2f} %")
    print(f"    {TASA} tasa de referencia                              : {float(ultimo[TASA]):.2f} %")
    print(f"    brecha alimentos - total en {ultimo.periodo}                       : "
          f"{pi_ult - float(ultimo[TOTAL]):+.2f} pp")
    print(f"  Pico de {ALIM} en el periodo: {pico.periodo} con {pi_pico:.2f} % "
          f"(brecha alimentos - total ese mes: {pi_pico - float(pico[TOTAL]):+.2f} pp)")

    # ------------------------------------------------------------------------ ENAHO por tipo de hogar
    print("=" * 100)
    print("ENAHO 2024 · por tipo de hogar (nacional) · salidas/indicadores.csv, corte tipo_hogar_am")
    print("  pobreza, extrema, part_alimentos, personas y rural: factor07 × mieperho · mieperho_medio y hogares: "
          "factor07")
    print(f"  {'tipo de hogar':<36}{'pobreza':>8}{'extrema':>8}{'alim.%':>8}{'mieperho':>9}{'%hog.':>7}"
          f"{'%pers.':>7}{'%rural':>7}{'contrib.':>9}{'n':>7}")
    for tipo in TIPOS:
        pob, n = valor(ind, "pobreza", "tipo_hogar_am", tipo)
        ext, _ = valor(ind, "pobreza_extrema", "tipo_hogar_am", tipo)
        alim, _ = valor(ind, "part_alimentos", "tipo_hogar_am", tipo)
        tam, _ = valor(ind, "mieperho_medio", "tipo_hogar_am", tipo)
        hog, _ = valor(ind, "hogares", "tipo_hogar_am", tipo)
        per, _ = valor(ind, "personas", "tipo_hogar_am", tipo)
        rur, _ = valor(ind, "rural", "tipo_hogar_am", tipo)
        print(f"  {tipo:<36}{pob:8.1f}{ext:8.1f}{alim:8.1f}{tam:9.2f}{hog:7.1f}{per:7.1f}{rur:7.1f}"
              f"{contribucion(alim, pi_ult):9.2f}{n:7,}")
    print(f"  contrib. = part_alimentos × {ALIM} de {ultimo.periodo} ({pi_ult:.2f} %) / 100, en pp")

    # ---------------------------------------------------------------- exposición por tipo de hogar y área
    print("=" * 100)
    print(f"EXPOSICIÓN · tipo de hogar × área · contribución de los alimentos a la inflación del hogar (pp)")
    print(f"  último mes: {ALIM} {ultimo.periodo} = {pi_ult:.2f} % · pico: {ALIM} {pico.periodo} = {pi_pico:.2f} %")
    print("  ENAHO: corte «tipo_hogar_am × area», base hogar, factor07 × mieperho (mieperho_medio con factor07)")
    filas = []
    for area in AREAS:
        print(f"  --- {area}")
        print(f"  {'tipo de hogar':<36}{'alim.%':>8}{'contrib.ult':>12}{'contrib.pico':>13}{'pobreza':>9}"
              f"{'extrema':>8}{'mieperho':>9}{'n':>7}  confiable")
        base_area = {}
        for tipo in TIPOS:
            grupo = f"{tipo} · {area}"
            alim, n = valor(ind, "part_alimentos", "tipo_hogar_am × area", grupo)
            pob, _ = valor(ind, "pobreza", "tipo_hogar_am × area", grupo)
            ext, _ = valor(ind, "pobreza_extrema", "tipo_hogar_am × area", grupo)
            tam, _ = valor(ind, "mieperho_medio", "tipo_hogar_am × area", grupo)
            c_ult, c_pico = contribucion(alim, pi_ult), contribucion(alim, pi_pico)
            fila = dict(area=area, tipo=tipo, alim=alim, c_ult=c_ult, c_pico=c_pico, pob=pob, ext=ext, tam=tam, n=n)
            filas.append(fila)
            if tipo == TIPOS[0]:
                base_area = fila
            print(f"  {tipo:<36}{alim:8.1f}{c_ult:12.2f}{c_pico:13.2f}{pob:9.1f}{ext:8.1f}{tam:9.2f}{n:7,}  "
                  f"{'sí' if n >= N_MIN else 'NO (n < 100)'}")
        for fila in filas[-2:]:
            print(f"    {corto(fila['tipo'])} - {BASE} ({area}): part_alimentos {fila['alim'] - base_area['alim']:+.1f} pp"
                  f" · contribución {fila['c_ult'] - base_area['c_ult']:+.2f} pp ({ultimo.periodo}) y "
                  f"{fila['c_pico'] - base_area['c_pico']:+.2f} pp ({pico.periodo}) · pobreza "
                  f"{fila['pob'] - base_area['pob']:+.1f} pp")
    df = pd.DataFrame(filas)
    print("  --- rural - urbano, mismo tipo de hogar")
    for tipo in TIPOS:
        u = df[(df.tipo == tipo) & (df.area == "Urbano")].iloc[0]
        r = df[(df.tipo == tipo) & (df.area == "Rural")].iloc[0]
        print(f"    {corto(tipo):<20} part_alimentos {r.alim - u.alim:+.1f} pp · contribución "
              f"{r.c_ult - u.c_ult:+.2f} pp ({ultimo.periodo}) · pobreza {r.pob - u.pob:+.1f} pp")
    print(f"  rango de la contribución en {ultimo.periodo}: {df.c_ult.min():.2f} pp "
          f"({corto(df.loc[df.c_ult.idxmin(), 'tipo'])}, {df.loc[df.c_ult.idxmin(), 'area']}) a {df.c_ult.max():.2f} pp "
          f"({corto(df.loc[df.c_ult.idxmax(), 'tipo'])}, {df.loc[df.c_ult.idxmax(), 'area']})")

    # ------------------------------------------------------------------------ control por tamaño del hogar
    print("=" * 100)
    print("CONTROL POR TAMAÑO · corte «tipo_hogar_am × tamano» (tamaño = mieperho), base hogar, factor07 × mieperho")
    print(f"  {'tipo de hogar · tamaño':<52}{'pobreza':>8}{'alim.%':>8}{'contrib.ult':>12}{'n':>7}  confiable")
    tam_filas = {}
    for tipo in TIPOS:
        for tam in TAMANOS:
            grupo = f"{tipo} · {tam}"
            pob, n = valor(ind, "pobreza", "tipo_hogar_am × tamano", grupo)
            alim, _ = valor(ind, "part_alimentos", "tipo_hogar_am × tamano", grupo)
            tam_filas[(tipo, tam)] = (pob, alim, n)
            print(f"  {grupo:<52}{pob:8.1f}{alim:8.1f}{contribucion(alim, pi_ult):12.2f}{n:7,}  "
                  f"{'sí' if n >= N_MIN else 'NO (n < 100)'}")
    print(f"  diferencias frente a {BASE} del mismo tamaño (solo celdas con n >= {N_MIN} en ambos grupos):")
    for tam in TAMANOS:
        pob0, alim0, n0 = tam_filas[(TIPOS[0], tam)]
        for tipo in TIPOS[1:]:
            pob, alim, n = tam_filas[(tipo, tam)]
            if min(n, n0) < N_MIN:
                print(f"    {tam:<16} {corto(tipo):<20} se omite: n = {n:,} frente a {n0:,}")
                continue
            print(f"    {tam:<16} {corto(tipo):<20} pobreza {pob - pob0:+.1f} pp · part_alimentos {alim - alim0:+.1f} pp"
                  f" · contribución {contribucion(alim, pi_ult) - contribucion(alim0, pi_ult):+.2f} pp")
    print("=" * 100)


if __name__ == "__main__":
    main()
