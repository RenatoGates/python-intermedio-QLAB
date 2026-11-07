"""Limpieza de la ENAHO para la tarea 4: módulos 34 (sumaria) y 02 (miembros).

    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024        # desde tarea_4/

VERSIÓN TAREA 4. Difiere de la de la sesión 16 (raíz del repo) en la ponderación: aquí la cifra oficial sale de la
base hogar ponderada con factor07 × mieperho, que es la que publica el INEI (27.6 %, urbana 24.8 %, rural 39.3 %).
La base persona con facpob07 (27.53 %, 24.7 %, 39.4 %) queda como cifra secundaria, solo para cortes por atributos
de la persona (sexo, edad).

Salidas en tarea_4/salidas/:
  hogares_<año>.parquet   una fila por hogar: pobreza, territorio, gasto por grupos y estructura por edad
  personas_<año>.parquet  una fila por residente habitual, con las variables de su hogar
  indicadores.csv         indicadores ponderados (los que usan gráficos, mapa e informe)
  validacion.txt          comprobaciones; si una esencial falla, el script termina con error y no deja bases
"""

import argparse
import sys
import unicodedata
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]
LLAVES_PERSONA = LLAVES_HOGAR + ["codperso"]
EDAD_ADULTO_MAYOR = 65
TOLERANCIA = 0.1                     # puntos porcentuales
REFERENCIAS = {                      # issue #201 y cifras publicadas por el INEI, base hogar
    2024: {"pobreza_nacional": 27.6, "pobreza_urbana": 24.8, "pobreza_rural": 39.3, "residentes": 108_664,
           "unidades_territoriales": 25, "pobreza_extrema": 5.5},
}
DEPARTAMENTOS = {                    # código de ubigeo (2 dígitos) -> nombre; Lima (15) y Callao (07) separados
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho", "06": "Cajamarca",
    "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco", "11": "Ica", "12": "Junín",
    "13": "La Libertad", "14": "Lambayeque", "15": "Lima", "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua",
    "19": "Pasco", "20": "Piura", "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali",
}
TIPOS_HOGAR = ["Sin adultos mayores", "Con adultos mayores y menores de 65", "Solo adultos mayores"]
TAMANOS = ["1 persona", "2 personas", "3 a 4 personas", "5 o más personas"]   # según mieperho
# Gasto por los 8 grupos de la canasta, en soles nominales del año. Copiado del do-file oficial del INEI
# 01.ConstrVarGastoIngreso2014-2024.do (ConstVarGasto-Metodologia actualizada.zip, en el módulo 34), sin deflactar.
GRUPOS_GASTO = {
    "g1_alimentos": "gru11hd gru12hd1 gru12hd2 gru13hd1 gru13hd2 gru13hd3 g05hd g05hd1 g05hd2 g05hd3 g05hd4 g05hd5 "
                    "g05hd6 ig06hd sg23 sig24 gru14hd gru14hd1 gru14hd2 gru14hd3 gru14hd4 gru14hd5 sg25 sig26 sg27 sig28",
    "g2_vestido": "gru21hd gru22hd1 gru22hd2 gru23hd1 gru23hd2 gru23hd3 gru24hd",
    "g3_vivienda": "gru31hd gru32hd1 gru32hd2 gru33hd1 gru33hd2 gru33hd3 gru34hd",
    "g4_muebles": "gru41hd gru42hd1 gru42hd2 gru43hd1 gru43hd2 gru43hd3 gru44hd sg421 sg42d1 sg423 sg42d3",
    "g5_salud": "gru51hd gru52hd1 gru52hd2 gru53hd1 gru53hd2 gru53hd3 gru54hd",
    "g6_transporte": "gru61hd gru62hd1 gru62hd2 gru63hd1 gru63hd2 gru63hd3 gru64hd g07hd ig08hd sg422 sg42d2",
    "g7_esparcimiento": "gru71hd gru72hd1 gru72hd2 gru73hd1 gru73hd2 gru73hd3 gru74hd sg42 sg42d",
    "g8_otros": "gru81hd gru82hd1 gru82hd2 gru83hd1 gru83hd2 gru83hd3 gru84hd",
}
COLUMNAS_M02 = LLAVES_PERSONA + ["p203", "p204", "p205", "p206", "p207", "p208a", "facpob07"]


class ValidacionFallida(Exception):
    pass


def raiz() -> Path:
    return Path(__file__).resolve().parents[4]       # .claude/skills/limpiando-enaho/scripts -> tarea_4


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    def limpio(col):
        s = "".join(c for c in unicodedata.normalize("NFD", str(col)) if unicodedata.category(c) != "Mn")
        s = s.lower().strip()
        return "anio" if s == "ano" else s
    return df.rename(columns={c: limpio(c) for c in df.columns})


def descomprimir(datos: Path) -> None:
    for z in sorted(datos.glob("*.zip")):
        if not (datos / z.stem).exists():
            with zipfile.ZipFile(z) as zf:
                zf.extractall(datos / z.stem)


def buscar_dta(datos: Path, nombre: str) -> Path:
    """El archivo con ese nombre exacto. No elige por patrón ni por tamaño: en el módulo 34 hay dos sumarias
    (sumaria-2024.dta y sumaria-2024-12g.dta) y solo la primera reproduce las cifras oficiales."""
    todos = list(datos.rglob("*.dta"))
    exactos = [p for p in todos if p.name.lower() == nombre.lower()]
    if len(exactos) == 1:
        return exactos[0]
    parecidos = [p.name for p in todos if p.name.lower().startswith(nombre.split("-")[0].lower())]
    if not exactos:
        raise FileNotFoundError(
            f"No encontré {nombre} dentro de {datos}. Archivos parecidos: {parecidos or 'ninguno'}. "
            "No uso otro en su lugar. Bajen los zip del INEI (966-Modulo34.zip y 966-Modulo02.zip) a datos/.")
    raise FileNotFoundError(f"Hay {len(exactos)} copias de {nombre} en {datos}: {[str(p) for p in exactos]}. "
                            "Dejen una sola.")


def leer(ruta: Path, columnas=None) -> pd.DataFrame:
    df = normalizar_columnas(pd.read_stata(ruta, convert_categoricals=False, columns=columnas))
    for k in LLAVES_PERSONA + ["ubigeo"]:
        if k in df.columns:
            df[k] = df[k].astype(str).str.strip()      # en el .dta ya son texto: así no se pierden ceros iniciales
    return df


def pct(condicion: pd.Series, peso: pd.Series) -> float:
    return float(100 * peso[condicion].sum() / peso.sum())


def media(x: pd.Series, peso: pd.Series) -> float:
    return float(np.average(x, weights=peso))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")         # la consola de Windows usa cp1252 y rompe las tildes
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--datos", default=None)
    ap.add_argument("--salidas", default=None)
    args = ap.parse_args()

    base_dir = raiz()
    datos = Path(args.datos) if args.datos else base_dir / "datos"
    salidas = Path(args.salidas) if args.salidas else base_dir / "salidas"
    ref = REFERENCIAS.get(args.anio)
    if ref is None:
        print(f"No hay cifras de referencia para {args.anio}: sin ellas no se puede validar.", file=sys.stderr)
        return 1
    if not datos.exists():
        print(f"Falta la carpeta {datos}.", file=sys.stderr)
        return 1
    salidas.mkdir(parents=True, exist_ok=True)

    # Lo que pudo dejar una corrida anterior se borra antes: si esta corrida falla, no queda una base vieja
    # que los gráficos y el mapa tomen por buena.
    destinos = {n: salidas / f"{n}_{args.anio}.parquet" for n in ("hogares", "personas")}
    for p in [*destinos.values(), salidas / "indicadores.csv"]:
        p.unlink(missing_ok=True)

    # ---------------------------------------------------------------------------------------------------- leer
    descomprimir(datos)
    try:
        ruta_s = buscar_dta(datos, f"sumaria-{args.anio}.dta")
        ruta_p = buscar_dta(datos, f"enaho01-{args.anio}-200.dta")
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    otras_sumarias = sorted(p.name for p in datos.rglob("sumaria*.dta") if p != ruta_s)
    sumaria = leer(ruta_s)
    m02 = leer(ruta_p, COLUMNAS_M02)
    n_filas_m02, n_hogares = len(m02), len(sumaria)

    esenciales, informativas = [], []

    def chequear(lista, ok, texto):
        lista.append((bool(ok), texto))

    for k in LLAVES_HOGAR:
        largos = sumaria[k].str.len().unique().tolist() + m02[k].str.len().unique().tolist()
        chequear(esenciales, len(set(largos)) == 1, f"la llave {k} es texto de largo fijo ({largos[0]} caracteres): "
                 "conserva los ceros iniciales")
    chequear(esenciales, not sumaria.duplicated(LLAVES_HOGAR).any(), "llaves de hogar únicas en la sumaria")
    chequear(esenciales, not m02.duplicated(LLAVES_PERSONA).any(), "llaves de persona únicas en el módulo 02")

    # -------------------------------------------------------------------------------- residentes habituales
    residentes = ((m02.p204 == 1) & (m02.p205 == 2)) | ((m02.p204 == 2) & (m02.p206 == 1))
    personas = m02.loc[residentes].copy()
    n_residentes = len(personas)
    personas["adulto_mayor"] = personas.p208a >= EDAD_ADULTO_MAYOR

    # ------------------------------------------------------------- estructura del hogar según edad (residentes)
    comp = (personas.assign(menor_18=personas.p208a < 18)
            .groupby(LLAVES_HOGAR)
            .agg(n_residentes=("codperso", "size"), n_am=("adulto_mayor", "sum"), n_menores_18=("menor_18", "sum"))
            .reset_index())
    jefes = personas.loc[personas.p203 == 1, LLAVES_HOGAR + ["adulto_mayor"]].rename(columns={"adulto_mayor": "jefe_am"})
    comp = comp.merge(jefes, on=LLAVES_HOGAR, how="left", validate="1:1")
    comp["jefe_am"] = comp.jefe_am.fillna(False).astype(bool)
    comp["tipo_hogar_am"] = np.select(
        [comp.n_am == 0, comp.n_am < comp.n_residentes], TIPOS_HOGAR[:2], default=TIPOS_HOGAR[2])
    comp["am_vive_solo"] = (comp.n_residentes == 1) & (comp.n_am == 1)

    # ------------------------------------------------------------------------------------------ base hogar
    faltan_gasto = [v for cols in GRUPOS_GASTO.values() for v in cols.split() if v not in sumaria.columns]
    for g, cols in GRUPOS_GASTO.items():
        sumaria[g] = sumaria[[c for c in cols.split() if c in sumaria.columns]].fillna(0).sum(axis=1)
    sumaria["g0_total"] = sumaria[list(GRUPOS_GASTO)].sum(axis=1)
    dif_gasto = (sumaria.g0_total - sumaria.gashog2d).abs().max()

    hogares = sumaria.merge(comp, on=LLAVES_HOGAR, how="left", validate="1:1", indicator=True)
    hogares_sin_residentes = int((hogares._merge != "both").sum())
    hogares = hogares.drop(columns="_merge")
    hogares["departamento"] = hogares.ubigeo.str.zfill(6).str[:2]
    hogares["urbano"] = hogares.estrato <= 5
    hogares["pobre"] = hogares.pobreza <= 2
    hogares["pobre_extremo"] = hogares.pobreza == 1
    hogares["peso_personas"] = hogares.factor07 * hogares.mieperho        # la ponderación oficial
    hogares["part_alimentos"] = 100 * hogares.g1_alimentos / hogares.g0_total
    hogares["gasto_pc_mensual"] = hogares.g0_total / (12 * hogares.mieperho)
    hogares["tamano_hogar"] = pd.cut(hogares.mieperho, [0, 1, 2, 4, np.inf], labels=TAMANOS).astype(str)

    # ---------------------------------------------------------------------------------------- base persona
    cols_hogar = ["pobreza", "pobre", "pobre_extremo", "mieperho", "factor07", "peso_personas", "ubigeo",
                  "departamento", "estrato", "urbano", "dominio", "tipo_hogar_am", "n_am", "part_alimentos"]
    base = personas.merge(hogares[LLAVES_HOGAR + cols_hogar], on=LLAVES_HOGAR, how="inner", validate="m:1")
    chequear(esenciales, len(base) == n_residentes and not base.duplicated(LLAVES_PERSONA).any(),
             f"la unión m:1 personas-hogares conserva las {n_residentes:,} filas, sin perder ni duplicar")
    chequear(esenciales, hogares_sin_residentes == 0, "todos los hogares de la sumaria tienen residentes en el "
             f"módulo 02 ({hogares_sin_residentes} sin ellos)")

    # ------------------------------------------------------------------------------- factores de expansión
    w, w_hog, w_per = hogares.peso_personas, hogares.factor07, base.facpob07
    chequear(esenciales, w_hog.notna().all() and (w_hog > 0).all(), "factor07 positivo y sin vacíos en todos los hogares")
    chequear(esenciales, w_per.notna().all() and (w_per > 0).all(), "facpob07 positivo y sin vacíos en todos los residentes")
    pob_expandida_hog, pob_expandida_per = w.sum(), w_per.sum()
    chequear(informativas, abs(pob_expandida_hog / pob_expandida_per - 1) < 0.01,
             f"población expandida: {pob_expandida_hog:,.0f} con factor07 × mieperho y {pob_expandida_per:,.0f} "
             "con facpob07 (difieren menos de 1 %)")

    # ---------------------------------------------------------------------------- cifras oficiales (hogar)
    oficial = {
        "pobreza_nacional": pct(hogares.pobre, w),
        "pobreza_urbana": pct(hogares.pobre[hogares.urbano], w[hogares.urbano]),
        "pobreza_rural": pct(hogares.pobre[~hogares.urbano], w[~hogares.urbano]),
        "pobreza_extrema": pct(hogares.pobre_extremo, w),
    }
    codigos = set(hogares.departamento.unique())
    secundaria = {
        "pobreza_nacional": pct(base.pobre, w_per),
        "pobreza_urbana": pct(base.pobre[base.urbano], w_per[base.urbano]),
        "pobreza_rural": pct(base.pobre[~base.urbano], w_per[~base.urbano]),
        "pobreza_extrema": pct(base.pobre_extremo, w_per),
    }
    sin_ponderar = 100 * hogares.pobre.mean()

    filas_oficiales = []
    for clave, etiqueta in [("pobreza_nacional", "Pobreza monetaria nacional"), ("pobreza_urbana", "Pobreza urbana"),
                            ("pobreza_rural", "Pobreza rural")]:
        dif = oficial[clave] - ref[clave]
        ok = abs(round(dif, 2)) <= TOLERANCIA
        filas_oficiales.append((ok, f"{etiqueta:<28}{oficial[clave]:7.2f} %   referencia {ref[clave]:5.1f} %   "
                                    f"diferencia {dif:+.2f} pp (tolerancia ±{TOLERANCIA})"))
    filas_oficiales.append((n_residentes == ref["residentes"],
                            f"{'Residentes habituales':<28}{n_residentes:>7,}     referencia {ref['residentes']:,}"))
    ok_dep = codigos == set(DEPARTAMENTOS) and len(codigos) == ref["unidades_territoriales"]
    filas_oficiales.append((ok_dep, f"{'Unidades territoriales':<28}{len(codigos):>7}     referencia "
                                    f"{ref['unidades_territoriales']} (códigos 01 a 25; Lima 15 y Callao 07 separados)"))
    chequear(esenciales, dif_gasto < 1, "los 8 grupos de gasto del INEI suman gashog2d en todos los hogares "
             f"(diferencia máxima {dif_gasto:.3f} soles)")
    chequear(informativas, abs(round(oficial["pobreza_extrema"] - ref["pobreza_extrema"], 2)) <= TOLERANCIA,
             f"pobreza extrema base hogar {oficial['pobreza_extrema']:.2f} % (INEI {ref['pobreza_extrema']} %)")

    todas = filas_oficiales + esenciales
    n_ok = sum(ok for ok, _ in todas)
    marca = lambda ok: "[OK]   " if ok else "[FALLA]"

    # ------------------------------------------------------------------------------------- validacion.txt
    rel = lambda p: p.relative_to(base_dir).as_posix() if p.is_relative_to(base_dir) else str(p)
    lineas = [
        f"ENAHO {args.anio} · validación de la limpieza (versión tarea_4)",
        "Generado por .claude/skills/limpiando-enaho/scripts/limpiar.py. Ninguna cifra está escrita a mano.",
        "",
        "Archivos",
        f"  sumaria : {rel(ruta_s)} ({n_hogares:,} hogares)",
        f"  miembros: {rel(ruta_p)} ({n_filas_m02:,} filas)",
        f"  otras sumarias en datos/, que no se usan: {', '.join(otras_sumarias) or 'ninguna'}",
        "",
        "CIFRA OFICIAL · base hogar (sumaria), ponderada con factor07 × mieperho",
        *[f"  {marca(ok)} {t}" for ok, t in filas_oficiales],
        "",
        "Integridad de la limpieza (esenciales)",
        *[f"  {marca(ok)} {t}" for ok, t in esenciales],
        "",
        "Cifra secundaria · base persona (módulo 02 unido a la sumaria), ponderada con facpob07",
        "  No es la cifra contra la que se valida: pondera personas, no hogares por su tamaño, y por eso",
        "  difiere en una décima. Se usa solo para cortes por atributos de la persona (sexo, edad).",
        f"  Pobreza nacional {secundaria['pobreza_nacional']:.2f} % · urbana {secundaria['pobreza_urbana']:.1f} % · "
        f"rural {secundaria['pobreza_rural']:.1f} % · extrema {secundaria['pobreza_extrema']:.2f} %",
        "",
        "Informativas (no detienen el proceso)",
        *[f"  {marca(ok)} {t}" for ok, t in informativas],
        f"  Sin ponderar, la pobreza de la muestra de hogares sería {sin_ponderar:.2f} %: por eso toda cifra se pondera.",
        f"  Variables del do-file del INEI que no trae la sumaria {args.anio}: {', '.join(faltan_gasto) or 'ninguna'}"
        " (se toman como 0).",
        "",
        f"Resultado: {n_ok} de {len(todas)} comprobaciones esenciales aprobadas."
        + ("" if n_ok == len(todas) else " PROCESO DETENIDO: no se guardaron las bases."),
    ]
    (salidas / "validacion.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))
    if n_ok != len(todas):
        fallas = [t for ok, t in todas if not ok]
        print("\nERROR: fallaron comprobaciones esenciales:\n  - " + "\n  - ".join(fallas), file=sys.stderr)
        return 2

    # ------------------------------------------------------------------------------------- guardar bases
    cols_hogares = (LLAVES_HOGAR + ["ubigeo", "departamento", "estrato", "urbano", "dominio", "mieperho", "factor07",
                    "peso_personas", "pobreza", "pobre", "pobre_extremo", "n_residentes", "n_am", "n_menores_18",
                    "jefe_am", "tipo_hogar_am", "am_vive_solo", "tamano_hogar", *GRUPOS_GASTO, "g0_total", "gashog2d",
                    "part_alimentos", "gasto_pc_mensual"])
    hogares[cols_hogares].to_parquet(destinos["hogares"], index=False)
    cols_personas = (LLAVES_PERSONA + ["p203", "p207", "p208a", "adulto_mayor", "facpob07"] + cols_hogar)
    base[cols_personas].to_parquet(destinos["personas"], index=False)

    # -------------------------------------------------------------------------------------- indicadores
    filas = []

    def agregar(indicador, corte, grupo, valor, unidad, ponderador, n):
        filas.append({"indicador": indicador, "corte": corte, "grupo": grupo, "valor": round(float(valor), 4),
                      "unidad": unidad, "ponderador": ponderador, "n_muestral": int(n)})

    P, H = "factor07 × mieperho", "factor07"
    for clave in ("pobreza_nacional", "pobreza_extrema"):
        agregar(clave.replace("_nacional", ""), "nacional", "Perú", oficial[clave], "% de personas", P, n_hogares)
    for urb, nombre in ((True, "Urbano"), (False, "Rural")):
        m = hogares.urbano == urb
        agregar("pobreza", "area", nombre, pct(hogares.pobre[m], w[m]), "% de personas", P, m.sum())
    for cod, g in hogares.groupby("departamento"):
        agregar("pobreza", "departamento", f"{cod} {DEPARTAMENTOS[cod]}", pct(g.pobre, g.peso_personas),
                "% de personas", P, len(g))
    # estructura del hogar según la presencia de adultos mayores (65+)
    for corte, grupos in (("tipo_hogar_am", hogares.groupby("tipo_hogar_am")),
                          ("tipo_hogar_am × area", hogares.groupby(["tipo_hogar_am", "urbano"]))):
        for clave, g in grupos:
            grupo = clave if isinstance(clave, str) else f"{clave[0]} · {'Urbano' if clave[1] else 'Rural'}"
            pw = g.peso_personas
            agregar("pobreza", corte, grupo, pct(g.pobre, pw), "% de personas", P, len(g))
            agregar("pobreza_extrema", corte, grupo, pct(g.pobre_extremo, pw), "% de personas", P, len(g))
            agregar("part_alimentos", corte, grupo, media(g.part_alimentos, pw), "% del gasto del hogar", P, len(g))
            agregar("gasto_pc_mensual", corte, grupo, media(g.gasto_pc_mensual, pw), "soles corrientes por persona "
                    "al mes", P, len(g))
            agregar("mieperho_medio", corte, grupo, media(g.mieperho, g.factor07), "personas por hogar", H, len(g))
            if corte == "tipo_hogar_am":
                agregar("hogares", corte, grupo, 100 * g.factor07.sum() / w_hog.sum(), "% de hogares", H, len(g))
                agregar("personas", corte, grupo, 100 * pw.sum() / w.sum(), "% de personas", P, len(g))
                agregar("rural", corte, grupo, pct(~g.urbano, pw), "% de personas", P, len(g))
    # control por tamaño: la pobreza monetaria es per cápita y los hogares de solo adultos mayores son más chicos,
    # así que se compara cada tipo de hogar con hogares del mismo tamaño
    for (tipo, tam), g in hogares.groupby(["tipo_hogar_am", "tamano_hogar"]):
        agregar("pobreza", "tipo_hogar_am × tamano", f"{tipo} · {tam}", pct(g.pobre, g.peso_personas),
                "% de personas", P, len(g))
        agregar("part_alimentos", "tipo_hogar_am × tamano", f"{tipo} · {tam}", media(g.part_alimentos, g.peso_personas),
                "% del gasto del hogar", P, len(g))
    agregar("mieperho_medio", "nacional", "Perú", media(hogares.mieperho, w_hog), "personas por hogar", H, n_hogares)
    con_am = hogares.n_am > 0
    agregar("hogares_con_am", "nacional", "Perú", pct(con_am, w_hog), "% de hogares", H, n_hogares)
    agregar("am_vive_solo", "hogares_con_am", "Perú", pct(hogares.am_vive_solo[con_am], w_hog[con_am]),
            "% de hogares con adultos mayores", H, con_am.sum())
    agregar("part_alimentos", "nacional", "Perú", media(hogares.part_alimentos, w), "% del gasto del hogar", P, n_hogares)
    for cod, g in hogares.groupby("departamento"):
        nombre, gam = f"{cod} {DEPARTAMENTOS[cod]}", g[g.n_am > 0]
        agregar("personas_en_hogares_am", "departamento", nombre, pct(g.n_am > 0, g.peso_personas), "% de personas",
                P, len(g))
        agregar("pobreza_hogares_am", "departamento", nombre, pct(gam.pobre, gam.peso_personas), "% de personas",
                P, len(gam))
    # la persona como unidad (base secundaria, facpob07)
    for am, nombre in ((True, "65 años o más"), (False, "Menos de 65 años")):
        m = base.adulto_mayor == am
        agregar("pobreza", "edad_persona", nombre, pct(base.pobre[m], w_per[m]), "% de personas", "facpob07", m.sum())
    pd.DataFrame(filas).to_csv(salidas / "indicadores.csv", index=False, encoding="utf-8")

    print(f"\nGuardado: {rel(destinos['hogares'])}, {rel(destinos['personas'])}, {rel(salidas / 'indicadores.csv')} "
          f"({len(filas)} indicadores) y {rel(salidas / 'validacion.txt')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
