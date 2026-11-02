"""Genera las seis imágenes de escena y la cama musical del reel."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import soundfile as sf

FONDO, TEXTO, SUAVE, ACENTO = "#1C1A17", "#F7F3EC", "#B8AE9F", "#F08A4B"
W, H, DPI = 900, 520, 100
SALIDA = Path(__file__).parent / "recursos"
DATOS = Path(__file__).resolve().parents[1] / "web" / "data"


def lienzo():
    fig, eje = plt.subplots(figsize=(W / DPI, H / DPI), dpi=DPI)
    fig.patch.set_facecolor(FONDO)
    eje.set_facecolor(FONDO)
    for s in eje.spines.values():
        s.set_visible(False)
    eje.tick_params(colors=SUAVE, labelsize=13, length=0)
    return fig, eje


NOMBRES = {"ANCASH": "Áncash", "APURIMAC": "Apurímac", "HUANUCO": "Huánuco",
           "JUNIN": "Junín", "SAN MARTIN": "San Martín", "MADRE DE DIOS": "Madre de Dios",
           "LA LIBERTAD": "La Libertad"}


def bonito(s):
    return s.map(lambda d: NOMBRES.get(d, d.title()))


def guardar(fig, nombre, left=0.16, right=0.96):
    SALIDA.mkdir(exist_ok=True)
    fig.subplots_adjust(left=left, right=right, top=0.86, bottom=0.12)
    fig.savefig(SALIDA / nombre, dpi=DPI, facecolor=FONDO)
    plt.close(fig)
    print("  ", nombre)


def s1_cuentas():
    fig, eje = lienzo()
    x, y = [0, 1], [42.3, 59.6]
    eje.plot(x, y, color=ACENTO, linewidth=5, marker="o", markersize=16)
    eje.fill_between(x, 0, y, color=ACENTO, alpha=0.13)
    for xi, yi in zip(x, y):
        eje.text(xi, yi + 4.5, f"{yi:.1f} %", color=TEXTO, fontsize=27, fontweight="bold",
                 ha="center")
    eje.set_xticks(x, ["2020", "2025"], color=SUAVE)
    eje.set_xlim(-0.25, 1.25)
    eje.set_ylim(0, 76)
    eje.set_yticks([])
    eje.set_title("Adultos con una cuenta en el sistema financiero", color=TEXTO,
                  fontsize=17, loc="left", pad=16)
    guardar(fig, "escena_1.png")


def s2_puntos():
    fig, eje = lienzo()
    x, y = [0, 1], [1330, 1308]
    eje.plot(x, y, color=SUAVE, linewidth=5, marker="o", markersize=16)
    for xi, yi in zip(x, y):
        eje.text(xi, yi + 55, f"{yi:,}", color=TEXTO, fontsize=27, fontweight="bold", ha="center")
    eje.set_xticks(x, ["jun 2021", "jun 2026"], color=SUAVE)
    eje.set_xlim(-0.25, 1.25)
    eje.set_ylim(0, 1750)
    eje.set_yticks([])
    eje.set_title("Puntos de atención por cada 100 mil adultos", color=TEXTO,
                  fontsize=17, loc="left", pad=16)
    eje.text(0.5, 620, "prácticamente sin cambio", color=SUAVE, fontsize=19, ha="center",
             style="italic")
    guardar(fig, "escena_2.png")


def s3_crecen(panel):
    sub = panel.nlargest(5, "var_puntos_pct").sort_values("var_puntos_pct")
    fig, eje = lienzo()
    eje.barh(bonito(sub["departamento"]), sub["var_puntos_pct"], color=ACENTO, height=0.62)
    for i, v in enumerate(sub["var_puntos_pct"]):
        eje.text(v + 7, i, f"+{v:.0f} %", color=TEXTO, fontsize=19, va="center", fontweight="bold")
    eje.set_xlim(0, sub["var_puntos_pct"].max() * 1.26)
    eje.set_xticks([])
    eje.tick_params(axis="y", colors=TEXTO, labelsize=17)
    eje.set_title("Dónde más creció la red, 2021–2026", color=TEXTO, fontsize=17, loc="left", pad=16)
    guardar(fig, "escena_3.png", left=0.26)


def s4_caen(panel):
    sub = panel.nsmallest(5, "var_puntos_pct").sort_values("var_puntos_pct", ascending=False)
    fig, eje = lienzo()
    eje.barh(bonito(sub["departamento"]), sub["var_puntos_pct"], color="#C0392B", height=0.62)
    for i, v in enumerate(sub["var_puntos_pct"]):
        eje.text(v - 1.8, i, f"{v:.0f} %", color=TEXTO, fontsize=19, va="center",
                 ha="right", fontweight="bold")
    eje.set_xlim(sub["var_puntos_pct"].min() * 1.3, 0)
    eje.set_xticks([])
    eje.tick_params(axis="y", colors=TEXTO, labelsize=17)
    eje.yaxis.tick_right()
    eje.set_title("Dónde se contrajo", color=TEXTO, fontsize=17, loc="left", pad=16)
    guardar(fig, "escena_4.png", left=0.06, right=0.80)


def s5_brecha(panel):
    """Rango entre el departamento mejor y el peor servido, 2021 contra 2026."""
    fig, eje = lienzo()
    for y, (ini, fin, anio, color) in enumerate([
        (panel["puntos_26"].min(), panel["puntos_26"].max(), "jun 2026", ACENTO),
        (panel["puntos_21"].min(), panel["puntos_21"].max(), "jun 2021", SUAVE),
    ]):
        eje.plot([ini, fin], [y, y], color=color, linewidth=9, solid_capstyle="round")
        eje.plot([ini, fin], [y, y], "o", color=color, markersize=15)
        eje.text(ini - 70, y, f"{ini:,.0f}", color=TEXTO, fontsize=16, va="center", ha="right")
        eje.text(fin + 70, y, f"{fin:,.0f}", color=TEXTO, fontsize=16, va="center")
        eje.text((ini + fin) / 2, y + 0.22, f"{fin / ini:.1f}x", color=TEXTO, fontsize=24,
                 ha="center", fontweight="bold")
        eje.text(ini - 70, y - 0.30, anio, color=SUAVE, fontsize=15, va="center", ha="right")
    eje.set_xlim(-250, panel["puntos_21"].max() * 1.14)
    eje.set_ylim(-0.75, 1.65)
    eje.set_xticks([])
    eje.set_yticks([])
    eje.set_title("Distancia entre el departamento mejor y el peor servido", color=TEXTO,
                  fontsize=17, loc="left", pad=16)
    guardar(fig, "escena_5.png", left=0.02, right=0.98)


def s5_composicion(nac):
    fig, eje = lienzo()
    partes = [("Cajeros corresponsales", nac["corresp_26"], ACENTO),
              ("Cajeros automáticos", nac["atm_26"], "#8C7A66"),
              ("Oficinas", nac["oficinas_26"], SUAVE)]
    izq = 0
    for nombre, v, color in partes:
        eje.barh([0], [v], left=izq, color=color, height=0.5, label=f"{nombre}")
        izq += v
    eje.text(nac["corresp_26"] / 2, 0, "89.2 %", color=FONDO, fontsize=38, fontweight="bold",
             ha="center", va="center")
    eje.set_xlim(0, izq)
    eje.set_ylim(-0.75, 0.9)
    eje.set_xticks([])
    eje.set_yticks([])
    eje.legend(loc="lower center", ncol=3, frameon=False, fontsize=13,
               labelcolor=SUAVE, bbox_to_anchor=(0.5, -0.18))
    eje.set_title("De qué está hecha la red de atención, 2026", color=TEXTO,
                  fontsize=17, loc="left", pad=16)
    guardar(fig, "escena_6.png")


def s6_mapa(panel):
    import geopandas as gpd
    gdf = gpd.read_file(DATOS / "peru_departamental_simple.geojson")
    gdf["ccdd"] = gdf["FIRST_IDDP"].astype(str).str.zfill(2)
    mapa = gdf.merge(panel[["ccdd", "puntos_26"]], on="ccdd", how="left", validate="1:1")

    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    fig.patch.set_facecolor(FONDO)
    ejes = fig.subplots(1, 2, width_ratios=[1, 1.25])
    for e in ejes:
        e.set_facecolor(FONDO)

    mapa.plot(column="puntos_26", cmap="Oranges", vmin=0, linewidth=0.5,
              edgecolor=FONDO, ax=ejes[0])
    ejes[0].axis("off")

    top = panel.nlargest(4, "puntos_26").sort_values("puntos_26")
    eje = ejes[1]
    nombres = list(bonito(top["departamento"]))
    eje.barh(range(len(top)), top["puntos_26"], color=ACENTO, height=0.62)
    for i, (v, n) in enumerate(zip(top["puntos_26"], nombres)):
        eje.text(60, i, n, color=FONDO, fontsize=16, va="center", fontweight="bold")
        eje.text(v + 70, i, f"{v:,.0f}", color=TEXTO, fontsize=18, va="center",
                 fontweight="bold")
    eje.set_xlim(0, top["puntos_26"].max() * 1.32)
    eje.set_xticks([])
    eje.set_yticks([])
    for s in eje.spines.values():
        s.set_visible(False)

    fig.suptitle("Puntos de atención por 100 mil adultos, 2026", color=TEXTO,
                 fontsize=17, x=0.03, ha="left", y=0.96)
    SALIDA.mkdir(exist_ok=True)
    fig.subplots_adjust(left=0.0, right=0.90, top=0.84, bottom=0.04, wspace=0.02)
    fig.savefig(SALIDA / "escena_7.png", dpi=DPI, facecolor=FONDO)
    plt.close(fig)
    print("   escena_7.png")


def musica(segundos=75, sr=44100):
    """Cama ambiental generada proceduralmente: sin derechos de terceros."""
    t = np.linspace(0, segundos, int(segundos * sr), endpoint=False)
    # acorde de La menor en novena, muy grave y sin ataque
    notas = [110.0, 164.81, 220.0, 329.63, 440.0]
    pesos = [1.0, 0.5, 0.38, 0.17, 0.09]
    onda = np.zeros_like(t)
    rng = np.random.default_rng(7)
    for f, p in zip(notas, pesos):
        vibrato = 1 + 0.0016 * np.sin(2 * np.pi * 0.11 * t + rng.uniform(0, 6))
        respiracion = 0.82 + 0.18 * np.sin(2 * np.pi * 0.045 * t + rng.uniform(0, 6))
        onda += p * respiracion * np.sin(2 * np.pi * f * vibrato * t)
    # pulso suave cada dos segundos, para que no quede estático
    pulso = np.exp(-((t % 2.0) / 0.22) ** 2) * np.sin(2 * np.pi * 55 * t)
    onda += 0.22 * pulso
    # filtro pasa bajos de un polo: quita el brillo y deja solo el colchón
    a = 0.0022
    y = np.zeros_like(onda)
    acc = 0.0
    for i, v in enumerate(onda):
        acc += a * (v - acc)
        y[i] = acc
    y /= np.abs(y).max()
    entrada = np.minimum(1, t / 2.5)
    salida = np.minimum(1, (segundos - t) / 3.0)
    y = y * entrada * salida * 0.9
    SALIDA.mkdir(exist_ok=True)
    sf.write(SALIDA / "musica.wav", y.astype(np.float32), sr)
    print(f"   musica.wav ({segundos} s)")


if __name__ == "__main__":
    panel = pd.read_csv(DATOS / "panel_departamental.csv", dtype={"ccdd": str})
    nac = pd.read_csv(DATOS / "nacional.csv").set_index("indicador")["valor"].to_dict()
    print("imágenes:")
    s1_cuentas(); s2_puntos(); s3_crecen(panel); s4_caen(panel)
    s5_brecha(panel); s5_composicion(nac); s6_mapa(panel)
    print("música:")
    musica()
