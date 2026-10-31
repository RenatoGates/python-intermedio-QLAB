"""Arma el panel departamental y los agregados nacionales a partir de los cuadros extraídos."""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
CRUDOS = RAIZ / "datos" / "procesados"
WEB = RAIZ / "web" / "data"


def main() -> int:
    WEB.mkdir(parents=True, exist_ok=True)
    red = pd.read_csv(CRUDOS / "sbs_red.csv", dtype={"ccdd": str})
    infra = pd.read_csv(CRUDOS / "sbs_infraestructura.csv", dtype={"ccdd": str})
    uso = pd.read_csv(CRUDOS / "sbs_uso.csv", dtype={"ccdd": str})

    nac_r = red[red["departamento"] == "NACIONAL"].iloc[0]
    nac_u = uso[uso["departamento"] == "NACIONAL"].iloc[0]

    red = red[red["ccdd"].notna()]
    uso = uso[uso["ccdd"].notna()]
    infra = infra[infra["ccdd"].notna()].add_prefix("inf_").rename(columns={"inf_ccdd": "ccdd"})

    panel = (
        red.merge(
            uso[["ccdd", "deudores_pct_21", "deudores_pct_26", "cuentas_pct_20", "cuentas_pct_25"]],
            on="ccdd", validate="1:1",
        )
        .merge(infra[["ccdd", "inf_puntos_21", "inf_puntos_26"]], on="ccdd", validate="1:1")
    )
    panel["var_puntos_pct"] = (100 * (panel["puntos_26"] / panel["puntos_21"] - 1)).round(1)
    panel["var_cuentas_pp"] = (panel["cuentas_pct_25"] - panel["cuentas_pct_20"]).round(1)
    panel["var_deudores_pp"] = (panel["deudores_pct_26"] - panel["deudores_pct_21"]).round(1)
    panel["share_corresp_21"] = (100 * panel["corresp_21"] / panel["puntos_21"]).round(1)
    panel["share_corresp_26"] = (100 * panel["corresp_26"] / panel["puntos_26"]).round(1)
    panel = panel.sort_values("ccdd")

    assert len(panel) == 25, f"Se esperaban 25 departamentos, hay {len(panel)}"
    assert panel["ccdd"].is_unique, "Códigos de departamento duplicados"
    assert panel.notna().all().all(), "Hay celdas vacías en el panel"

    nacional = {
        "puntos_21": nac_r["puntos_21"], "puntos_26": nac_r["puntos_26"],
        "oficinas_21": nac_r["oficinas_21"], "oficinas_26": nac_r["oficinas_26"],
        "atm_21": nac_r["atm_21"], "atm_26": nac_r["atm_26"],
        "corresp_21": nac_r["corresp_21"], "corresp_26": nac_r["corresp_26"],
        "cuentas_pct_20": nac_u["cuentas_pct_20"], "cuentas_pct_25": nac_u["cuentas_pct_25"],
        "deudores_pct_21": nac_u["deudores_pct_21"], "deudores_pct_26": nac_u["deudores_pct_26"],
        "share_corresp_21": round(100 * nac_r["corresp_21"] / nac_r["puntos_21"], 1),
        "share_corresp_26": round(100 * nac_r["corresp_26"] / nac_r["puntos_26"], 1),
        "brecha_21": round(panel["puntos_21"].max() / panel["puntos_21"].min(), 1),
        "brecha_26": round(panel["puntos_26"].max() / panel["puntos_26"].min(), 1),
    }

    panel.to_csv(WEB / "panel_departamental.csv", index=False)
    pd.DataFrame({"indicador": list(nacional), "valor": list(nacional.values())}).to_csv(
        WEB / "nacional.csv", index=False
    )

    print(f"panel: {len(panel)} departamentos, {panel.shape[1]} columnas")
    print(f"tenencia de cuentas nacional: {nacional['cuentas_pct_20']:.1f} % -> "
          f"{nacional['cuentas_pct_25']:.1f} %")
    print(f"puntos por 100 mil adultos  : {nacional['puntos_21']:,.0f} -> {nacional['puntos_26']:,.0f}")
    print(f"corresponsales              : {nacional['share_corresp_26']:.1f} % de la red")
    print(f"brecha entre departamentos  : {nacional['brecha_21']}x -> {nacional['brecha_26']}x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
