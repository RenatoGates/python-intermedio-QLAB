import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parent
DATOS = RAIZ / "data"
COLOR = "#1f4e79"
ESCALA = "Blues"

st.set_page_config(
    page_title="Acceso financiero en el Perú",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def cargar():
    panel = pd.read_csv(DATOS / "panel_departamental.csv", dtype={"ccdd": str})
    nacional = pd.read_csv(DATOS / "nacional.csv")
    with open(DATOS / "peru_departamental_simple.geojson", encoding="utf-8") as f:
        geo = json.load(f)
    for feat in geo["features"]:
        feat["properties"]["ccdd"] = str(feat["properties"]["FIRST_IDDP"]).zfill(2)
        feat["id"] = feat["properties"]["ccdd"]
    return panel, nacional, geo


panel, nacional, geo = cargar()
nac = nacional.set_index("indicador")["valor"].to_dict()

INDICADORES = {
    "Puntos de atención por 100 mil adultos": ("puntos_21", "puntos_26", "{:,.0f}"),
    "Cajeros corresponsales por 100 mil adultos": ("corresp_21", "corresp_26", "{:,.0f}"),
    "Cajeros automáticos por 100 mil adultos": ("atm_21", "atm_26", "{:,.0f}"),
    "Oficinas por 100 mil adultos": ("oficinas_21", "oficinas_26", "{:,.0f}"),
    "Adultos con cuenta (%)": ("cuentas_pct_20", "cuentas_pct_25", "{:.1f}"),
    "Deudores sobre población adulta (%)": ("deudores_pct_21", "deudores_pct_26", "{:.1f}"),
}

st.title("De la agencia al bodeguero")
st.subheader("Cómo se redistribuyó el acceso financiero en el Perú, 2021–2026")
st.markdown(
    "**Pregunta:** ¿dónde está la brecha de acceso financiero en el Perú y cómo cambió "
    "entre 2021 y 2026? · **Cobertura:** los 25 departamentos · "
    "**Fuente:** SBS, *Reporte de Indicadores de Inclusión Financiera* (junio 2026) e INEI."
)

# ── Controles ─────────────────────────────────────────────────────────────────
st.sidebar.header("Controles")
nombre_ind = st.sidebar.selectbox("Indicador", list(INDICADORES), index=0)
col_ini, col_fin, fmt = INDICADORES[nombre_ind]
anio = st.sidebar.radio("Año del mapa", ["2021", "2026", "Variación"], index=1, horizontal=True)
deps = st.sidebar.multiselect(
    "Departamentos a comparar",
    sorted(panel["departamento"]),
    default=["HUANCAVELICA", "LIMA", "AREQUIPA", "CUSCO"],
)
solo_crecieron = st.sidebar.checkbox("Mostrar solo los que crecieron", value=False)
st.sidebar.caption("Los controles afectan al mapa, a los gráficos y a la tabla.")

d = panel.copy()
d["valor_ini"], d["valor_fin"] = d[col_ini], d[col_fin]
d["variacion"] = d["valor_fin"] - d["valor_ini"]
d["variacion_pct"] = (100 * (d["valor_fin"] / d["valor_ini"] - 1)).round(1)
if solo_crecieron:
    d = d[d["variacion"] > 0]

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown("### Los cuatro números que resumen el cambio")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Adultos con cuenta", f"{nac['cuentas_pct_25']:.1f} %",
          f"{nac['cuentas_pct_25'] - nac['cuentas_pct_20']:+.1f} pp desde 2020")
k2.metric("Puntos de atención por 100 mil adultos", f"{nac['puntos_26']:,.0f}",
          f"{100 * (nac['puntos_26'] / nac['puntos_21'] - 1):+.1f} % desde 2021")
k3.metric("La red que son corresponsales", f"{nac['share_corresp_26']:.1f} %",
          f"{nac['share_corresp_26'] - nac['share_corresp_21']:+.1f} pp")
k4.metric("Brecha entre el mejor y el peor departamento", f"{nac['brecha_26']:.1f}x",
          f"{nac['brecha_26'] - nac['brecha_21']:+.1f}x desde 2021", delta_color="inverse")

st.divider()

# ── Mapa + ranking ────────────────────────────────────────────────────────────
izq, der = st.columns([1, 1])

with izq:
    if anio == "Variación":
        col, titulo, escala, centro = "variacion", f"Cambio 2021–2026 · {nombre_ind}", "RdBu", 0
    else:
        col = "valor_ini" if anio == "2021" else "valor_fin"
        titulo, escala, centro = f"{nombre_ind} · {anio}", ESCALA, None
    st.markdown(f"**{titulo}**")
    fig = px.choropleth(
        d, geojson=geo, locations="ccdd", color=col,
        color_continuous_scale=escala, color_continuous_midpoint=centro,
        hover_name="departamento",
        hover_data={"ccdd": False, col: ":,.1f"},
        labels={col: nombre_ind},
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=470,
                      coloraxis_colorbar=dict(title=None, thickness=12))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Unión por código de ubigeo, nunca por nombre. Lima (15) y Callao (07) van separados.")

with der:
    st.markdown(f"**Variación 2021–2026 · {nombre_ind}**")
    orden = d.sort_values("variacion_pct")
    fig2 = go.Figure(go.Bar(
        x=orden["variacion_pct"], y=orden["departamento"], orientation="h",
        marker_color=["#c0392b" if v < 0 else COLOR for v in orden["variacion_pct"]],
        text=[f"{v:+.0f} %" for v in orden["variacion_pct"]], textposition="outside",
        hovertemplate="%{y}: %{x:+.1f} %<extra></extra>",
    ))
    fig2.update_layout(
        height=470, margin=dict(l=0, r=30, t=10, b=0),
        xaxis_title="variación porcentual", yaxis_title=None,
        plot_bgcolor="white", showlegend=False,
    )
    fig2.update_xaxes(gridcolor="#eeeeee", zerolinecolor="#999999")
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("En rojo los departamentos donde la red se contrajo.")

st.divider()

# ── Dispersión + composición ──────────────────────────────────────────────────
izq2, der2 = st.columns([1, 1])

with izq2:
    st.markdown("**Más puntos de atención no significa más gente bancarizada**")
    fig3 = px.scatter(
        panel, x="puntos_26", y="cuentas_pct_25", text="departamento",
        size="corresp_26", color="var_cuentas_pp", color_continuous_scale=ESCALA,
        labels={"puntos_26": "Puntos de atención por 100 mil adultos (2026)",
                "cuentas_pct_25": "Adultos con cuenta (%, 2025)",
                "var_cuentas_pp": "Cambio en pp"},
    )
    fig3.update_traces(textposition="top center", textfont_size=8)
    fig3.update_layout(height=430, margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor="white")
    fig3.update_xaxes(gridcolor="#eeeeee")
    fig3.update_yaxes(gridcolor="#eeeeee")
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("El tamaño del punto es el número de corresponsales por 100 mil adultos.")

with der2:
    st.markdown("**Cómo está compuesta la red, 2026**")
    comp = panel.nlargest(12, "puntos_26").sort_values("puntos_26")
    fig4 = go.Figure()
    for col_c, nombre_c, color_c in [
        ("corresp_26", "Cajeros corresponsales", COLOR),
        ("atm_26", "Cajeros automáticos", "#6ba3d6"),
        ("oficinas_26", "Oficinas", "#c9dced"),
    ]:
        fig4.add_bar(y=comp["departamento"], x=comp[col_c], name=nombre_c,
                     orientation="h", marker_color=color_c)
    fig4.update_layout(
        barmode="stack", height=430, margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title="por cada 100 mil adultos", yaxis_title=None,
        plot_bgcolor="white", legend=dict(orientation="h", y=-0.18),
    )
    fig4.update_xaxes(gridcolor="#eeeeee")
    st.plotly_chart(fig4, use_container_width=True)
    st.caption("Los 12 departamentos con más puntos de atención.")

st.divider()

# ── Comparación seleccionada ──────────────────────────────────────────────────
if deps:
    st.markdown(f"**Departamentos seleccionados · {nombre_ind}**")
    sel = panel[panel["departamento"].isin(deps)].copy()
    largo = pd.concat([
        sel[["departamento", col_ini]].rename(columns={col_ini: "valor"}).assign(anio="2021"),
        sel[["departamento", col_fin]].rename(columns={col_fin: "valor"}).assign(anio="2026"),
    ])
    fig5 = px.bar(largo, x="departamento", y="valor", color="anio", barmode="group",
                  color_discrete_sequence=["#c9dced", COLOR], text_auto=".0f",
                  labels={"valor": nombre_ind, "anio": "Año", "departamento": ""})
    fig5.update_layout(height=330, margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor="white")
    fig5.update_yaxes(gridcolor="#eeeeee", rangemode="tozero")
    st.plotly_chart(fig5, use_container_width=True)

# ── Tabla ─────────────────────────────────────────────────────────────────────
st.markdown("### Los datos")
tabla = d[[
    "departamento", "puntos_21", "puntos_26", "variacion_pct",
    "corresp_26", "share_corresp_26", "cuentas_pct_20", "cuentas_pct_25", "var_cuentas_pp",
]].rename(columns={
    "departamento": "Departamento", "puntos_21": "Puntos 2021", "puntos_26": "Puntos 2026",
    "variacion_pct": "Var. %", "corresp_26": "Corresponsales 2026",
    "share_corresp_26": "% corresponsales", "cuentas_pct_20": "Cuentas 2020 (%)",
    "cuentas_pct_25": "Cuentas 2025 (%)", "var_cuentas_pp": "Var. cuentas (pp)",
}).sort_values("Var. %", ascending=False)
st.dataframe(tabla, use_container_width=True, hide_index=True)
st.download_button("Descargar en CSV", tabla.to_csv(index=False).encode("utf-8"),
                   "acceso_financiero_peru.csv", "text/csv")

st.divider()

# ── Hallazgos, metodología, límites ───────────────────────────────────────────
t1, t2, t3 = st.tabs(["Hallazgos", "Metodología y fuentes", "Limitaciones"])

with t1:
    st.markdown(f"""
**1 · El acceso físico se estancó, pero la bancarización saltó.**
Los puntos de atención por cada 100 mil adultos pasaron de {nac['puntos_21']:,.0f} a
{nac['puntos_26']:,.0f}, una caída de {abs(100 * (nac['puntos_26'] / nac['puntos_21'] - 1)):.1f} %.
En el mismo periodo la proporción de adultos con alguna cuenta subió de
{nac['cuentas_pct_20']:.1f} % a {nac['cuentas_pct_25']:.1f} %, **{nac['cuentas_pct_25'] - nac['cuentas_pct_20']:+.1f} puntos
porcentuales**. La inclusión avanzó sin más infraestructura: el canal digital hizo el trabajo.

**2 · La brecha se cerró por redistribución, no por crecimiento.**
Huancavelica multiplicó su red por 3.6 ({panel.loc[panel.departamento == 'HUANCAVELICA', 'puntos_21'].iloc[0]:,.0f}
a {panel.loc[panel.departamento == 'HUANCAVELICA', 'puntos_26'].iloc[0]:,.0f} puntos por 100 mil adultos) y Madre de Dios
por 2.8. Al mismo tiempo Arequipa perdió 35 %, Lima 26 % y Callao 23 %. La razón entre el
departamento mejor y peor servido bajó de **{nac['brecha_21']:.1f}x a {nac['brecha_26']:.1f}x**.

**3 · Las oficinas cierran y el bodeguero sostiene la red.**
Las oficinas por 100 mil adultos cayeron de {nac['oficinas_21']:.0f} a {nac['oficinas_26']:.0f} y los cajeros
automáticos de {nac['atm_21']:.0f} a {nac['atm_26']:.0f}. Hoy los cajeros corresponsales son el
**{nac['share_corresp_26']:.1f} %** de todos los puntos de atención del país, y en algunos departamentos
superan el 97 %. El punto de acceso financiero típico del peruano ya no es una agencia: es una bodega.

*Dato de titular:* Cusco pasó de 30.1 % a 60.9 % de adultos con cuenta, **+30.9 puntos en cinco años**,
el mayor salto del país.
""")

with t2:
    st.markdown("""
**Fuente primaria.** Superintendencia de Banca, Seguros y AFP (SBS),
*Perú: Reporte de Indicadores de Inclusión Financiera de los Sistemas Financiero, de Seguros y de
Pensiones*, edición a junio de 2026. Es una publicación estadística pública y semestral.
Los cuadros usados son los de disponibilidad de la red de atención por departamento (pág. 11),
infraestructura de atención por departamento (pág. 14) e indicadores de uso por departamento (pág. 24).

**Fuentes secundarias de la SBS.** Anexo 10 y Reporte 30 para la red de atención; Reporte
Crediticio Consolidado para deudores; INEI, proyecciones de población adulta por departamento
2021–2026; e INEI, Encuesta Nacional de Hogares (ENAHO) para la tenencia de cuentas.

**Procesamiento.** Los cuadros se extraen del PDF con `pdfplumber`, se reconocen las filas por
nombre de departamento, se normalizan tildes y se asigna el código de ubigeo de dos dígitos.
El mapa une por ese código contra los límites departamentales, nunca por nombre.
Todo el pipeline está en `scripts/` y se reproduce con un comando.

**Definiciones.** Un *punto de atención* es la suma de oficinas, cajeros automáticos, cajeros
corresponsales y establecimientos con operaciones básicas (EOB). La disponibilidad cuenta cada
cajero o establecimiento tantas veces como entidades operan a través de él; la infraestructura
lo cuenta una sola vez. Este tablero usa la **disponibilidad**, que es la que mide la oferta
efectiva que ve una persona.
""")

with t3:
    st.markdown("""
- **Dos cortes, no una serie.** El reporte compara junio 2021 con junio 2026. No hay puntos
  intermedios, así que no se puede saber si el cambio fue gradual o de golpe.
- **Las fechas no coinciden entre indicadores.** La red de atención es a junio de cada año,
  los deudores también, pero la tenencia de cuentas viene de la ENAHO y corresponde a diciembre
  de 2020 y 2025. Las comparaciones entre ambos bloques son aproximadas.
- **Denominador proyectado.** La población adulta por departamento son proyecciones del INEI,
  no un censo. En departamentos con migración fuerte el denominador puede estar desactualizado.
- **Disponibilidad no es uso.** Un corresponsal puede existir y no operar. El reporte mide
  presencia, no transacciones.
- **Correlación, no causalidad.** Que la bancarización suba mientras la red se estanca sugiere
  que el canal digital explica el avance, pero estos datos no lo prueban: haría falta la serie
  de operaciones de banca móvil y billeteras.
- **El promedio departamental esconde el interior.** Un departamento puede tener buena cobertura
  gracias a su capital y seguir teniendo distritos sin ningún punto de atención.
""")

st.caption(
    "Datos: SBS, Reporte de Indicadores de Inclusión Financiera (junio 2026); INEI. "
    "Elaboración propia · Renato Gates Rojas"
)
