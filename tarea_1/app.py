from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

BASE = Path(__file__).parent
RUTA_NOTICIAS = BASE / "datos" / "noticias.csv"
MODELO_HF = "gates1179/distilbeto-titulares-peru"
CATEGORIAS = {"politica": "Política", "economia": "Economía", "deportes": "Deportes",
              "ciencia_tecnologia": "Ciencia y tecnología"}
COLORES = {"Política": "#2a78d6", "Economía": "#eb6834", "Deportes": "#1baf7a", "Ciencia y tecnología": "#eda100"}
ORDEN = list(CATEGORIAS.values())

st.set_page_config(page_title="Titulares peruanos", layout="wide")


@st.cache_data
def cargar_noticias():
    noticias = pd.read_csv(RUTA_NOTICIAS, encoding="utf-8-sig", parse_dates=["fecha"])
    noticias["categoria"] = noticias["etiqueta"].map(CATEGORIAS)
    noticias["palabras"] = noticias["titular"].str.split().str.len()
    return noticias


@st.cache_resource(show_spinner="Descargando el modelo desde Hugging Face (solo la primera vez)…")
def cargar_modelo():
    tokenizer = AutoTokenizer.from_pretrained(MODELO_HF)
    modelo = AutoModelForSequenceClassification.from_pretrained(MODELO_HF)
    modelo.eval()
    return tokenizer, modelo


def predecir(titular):
    tokenizer, modelo = cargar_modelo()
    entradas = tokenizer(titular, truncation=True, max_length=64, return_tensors="pt")
    with torch.inference_mode():
        probabilidades = torch.softmax(modelo(**entradas).logits, dim=-1)[0]
    return (pd.DataFrame({"label": [modelo.config.id2label[i] for i in range(len(probabilidades))],
                          "score": probabilidades.tolist()})
              .sort_values("score", ascending=False, ignore_index=True))


noticias = cargar_noticias()
primer_dia, ultimo_dia = noticias["fecha"].min().date(), noticias["fecha"].max().date()

st.title("Titulares de noticias peruanas")
st.caption(f"{len(noticias)} titulares de El Comercio publicados entre el {primer_dia:%d/%m} y el "
           f"{ultimo_dia:%d/%m/%Y}, y un clasificador DistilBETO entrenado con etiquetas de un LLM.")

with st.sidebar:
    st.header("Filtros")
    elegidas = st.multiselect("Categoría (según la sección del medio)", ORDEN, default=ORDEN)
    rango = st.date_input("Rango de fechas", value=(primer_dia, ultimo_dia), min_value=primer_dia,
                          max_value=ultimo_dia, format="DD/MM/YYYY")
    desde, hasta = (rango[0], rango[-1]) if rango else (primer_dia, ultimo_dia)
    st.caption("Los filtros se aplican a los indicadores, el gráfico y la tabla de la pestaña «Explorar».")

datos = noticias[noticias["categoria"].isin(elegidas) & noticias["fecha"].dt.date.between(desde, hasta)]

explorar, clasificar = st.tabs(["Explorar los titulares", "Clasificar un titular nuevo"])

with explorar:
    if datos.empty:
        st.info("No hay titulares con estos filtros. Prueba con otra categoría o un rango de fechas más amplio.")
    else:
        frecuencia = datos["categoria"].value_counts()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Titulares", len(datos), delta=f"{len(datos) / len(noticias):.0%} del total",
                    delta_color="off", border=True)
        col2.metric("Días con publicaciones", datos["fecha"].dt.date.nunique(), border=True)
        col3.metric("Categoría más frecuente", frecuencia.index[0],
                    delta=f"{frecuencia.iloc[0] / len(datos):.0%} de lo filtrado", delta_color="off", border=True)
        col4.metric("Palabras por titular (mediana)", f"{datos['palabras'].median():.0f}", border=True)

        por_dia = (datos.groupby([datos["fecha"].dt.date.rename("dia"), "categoria"]).size()
                        .reset_index(name="titulares"))
        totales = por_dia.groupby("dia")["titulares"].sum()
        fig = px.bar(por_dia, x="dia", y="titulares", color="categoria", color_discrete_map=COLORES,
                     category_orders={"categoria": ORDEN},
                     title=f"El día con más titulares es el {totales.idxmax():%d/%m}, con {totales.max()}",
                     labels={"dia": "Día de publicación", "titulares": "Titulares", "categoria": "Categoría"})
        fig.update_traces(marker_line_width=1, marker_line_color="rgba(252,252,251,0.9)",
                          hovertemplate="%{x|%d/%m}: %{y} titulares<extra>%{fullData.name}</extra>")
        fig.update_layout(bargap=0.3, legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, title=None),
                          title=dict(subtitle=dict(text="Titulares publicados por día y categoría")),
                          margin=dict(t=110))
        fig.update_xaxes(dtick=86400000, tickformat="%d/%m")
        st.plotly_chart(fig)

        st.subheader("Titulares filtrados")
        tabla = datos.sort_values("fecha", ascending=False)
        st.dataframe(tabla[["fecha", "categoria", "titular", "bajada", "seccion_original", "url"]], hide_index=True,
                     column_config={
                         "fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
                         "categoria": "Categoría",
                         "titular": st.column_config.TextColumn("Titular", width="large"),
                         "bajada": "Bajada",
                         "seccion_original": "Sección original",
                         "url": st.column_config.LinkColumn("Nota", display_text="Abrir"),
                     })
        descarga = tabla[["titular", "bajada", "medio", "seccion_original", "url", "fecha", "etiqueta"]]
        st.download_button("Descargar estos titulares (CSV)", on_click="ignore", mime="text/csv",
                           file_name="titulares_filtrados.csv",
                           data=descarga.assign(fecha=descarga["fecha"].dt.date)
                                        .to_csv(index=False).encode("utf-8-sig"))

with clasificar:
    st.write("Escribe un titular y el modelo lo asigna a una de las cuatro categorías, con su confianza. "
             f"El modelo es [{MODELO_HF}](https://huggingface.co/{MODELO_HF}), entrenado en la Parte 2.")
    titular = st.text_input("Titular", placeholder="Ej.: El BCR mantiene su tasa de referencia en 4,25 %")

    if titular.strip():
        resultado = predecir(titular.strip())
        resultado["categoria"] = resultado["label"].map(CATEGORIAS)
        mejor = resultado.iloc[0]
        st.metric("Categoría predicha", mejor["categoria"], delta=f"confianza: {mejor['score']:.0%}",
                  delta_color="off", border=True)
        if mejor["score"] < 0.5:
            st.warning("Confianza baja: el titular podría no encajar bien en ninguna de las cuatro categorías.")

        fig = px.bar(resultado, x="score", y="categoria", orientation="h", color="categoria",
                     color_discrete_map=COLORES, category_orders={"categoria": ORDEN},
                     labels={"score": "Probabilidad", "categoria": ""}, text_auto=".0%")
        fig.update_layout(showlegend=False, height=260, margin=dict(t=10, b=10), xaxis_range=[0, 1],
                          xaxis_tickformat=".0%")
        st.plotly_chart(fig)
        st.caption("El modelo solo conoce estas cuatro categorías: un titular de otro tema igual recibirá una de "
                   "ellas. Se entrenó con titulares de El Comercio de octubre de 2026.")
