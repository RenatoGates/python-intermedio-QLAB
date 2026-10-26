import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE = Path(__file__).parent
DATOS = BASE / "datos" / "ejemplos"
ORIGEN = {"entrevistas": "entrevista (Commons)", "es_peru": "OpenSLR 73", "en_fleurs": "FLEURS", "audios": "grabación propia"}
COLORES = {"impreso": "#2a78d6", "foto": "#eb6834", "manuscrito": "#1baf7a", "OpenSLR 73": "#2a78d6",
           "FLEURS": "#eb6834", "entrevista (Commons)": "#1baf7a", "grabación propia": "#eda100"}
ORDEN = ["impreso", "foto", "manuscrito", "OpenSLR 73", "FLEURS", "entrevista (Commons)", "grabación propia"]

st.set_page_config(page_title="Documentos y audio a texto", layout="wide")


@st.cache_data
def cargar():
    documentos = pd.read_csv(DATOS / "documentos.csv", keep_default_na=False)
    transcripciones = pd.read_csv(DATOS / "transcripciones.csv", keep_default_na=False)
    extraccion = pd.read_csv(DATOS / "extraccion_llm.csv")
    extraccion["campos"] = extraccion["campos_json"].map(json.loads)
    cer = pd.read_csv(DATOS / "metricas_cer.csv")
    wer = pd.read_csv(DATOS / "metricas_wer.csv")
    auditoria = pd.read_csv(DATOS / "auditoria_llm.csv")
    transcripciones["origen"] = transcripciones["archivo_audio"].str.split("/").str[-2].map(ORIGEN)
    textos = pd.concat([
        documentos.assign(modalidad="documento", texto=documentos["texto_ocr"], modelo=documentos["modelo_ocr"]),
        transcripciones.assign(modalidad="audio", tipo=transcripciones["origen"], texto=transcripciones["texto_asr"],
                               modelo=transcripciones["modelo_asr"]),
    ], ignore_index=True)[["id", "modalidad", "tipo", "modelo", "texto", "texto_referencia"]]
    textos["modelo"] = textos["modelo"].str.split(" · ").str[0]
    textos["caracteres"] = textos["texto"].str.len()
    textos["tema_llm"] = textos["id"].map(extraccion.set_index("id")["campos"].map(lambda c: c.get("tema")))
    return documentos, transcripciones, extraccion.set_index("id"), cer, wer, auditoria, textos


documentos, transcripciones, extraccion, cer, wer, auditoria, textos = cargar()
acuerdo = auditoria[["tema_ok", "resumen_ok", "especifico_ok"]].to_numpy().mean()

st.title("De documentos y audio a texto buscable")
st.caption(f"{len(documentos)} documentos leídos con PaddleOCR y {len(transcripciones)} clips transcritos con "
           "faster-whisper, todo en CPU. Texto seudonimizado; las imágenes y los audios no están en el repositorio.")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Documentos", len(documentos), border=True)
col2.metric("Minutos transcritos", f"{transcripciones['duracion_seg'].sum() / 60:.1f}", border=True)
col3.metric("CER mediano", f"{cer['cer'].median():.1%}", border=True,
            help="10 documentos. Las 8 páginas del PDF están infladas por el orden de sellos y notas al pie; "
                 "los 2 transcritos a mano dan 15 % y 18 %.")
col4.metric("WER mediano", f"{wer['wer'].median():.1%}", border=True,
            help="10 frases leídas de OpenSLR 73, sin marcas de hablante.")
col5.metric("Acuerdo LLM-humano", f"{acuerdo:.0%}", border=True,
            help="Campos correctos en 20 casos auditados (revisión prellenada, pendiente de confirmar por una persona).")

with st.sidebar:
    st.header("Filtros")
    tipos = [t for t in ORDEN if t in set(textos["tipo"])]
    elegidos = st.multiselect("Tipo de documento u origen del audio", tipos, default=tipos)
    modelos = sorted(textos["modelo"].unique())
    elegidos_modelo = st.multiselect("Modelo", modelos, default=modelos)
    st.caption("Los filtros se aplican al buscador, a los gráficos y a la tabla.")

buscar, explorar_docs, explorar_audios = st.tabs(["Buscar en el corpus", "Explorar documentos", "Explorar audios"])

with buscar:
    consulta = st.text_input("Buscar en el texto extraído", placeholder="Ej.: ceviche, datos personales, Perú")
    datos = textos[textos["tipo"].isin(elegidos) & textos["modelo"].isin(elegidos_modelo)]
    if consulta.strip():
        datos = datos[datos["texto"].str.contains(consulta.strip(), case=False, regex=False)]
    st.write(f"**{len(datos)}** textos de {len(textos)}.")

    if datos.empty:
        st.info("Ningún texto coincide. Prueba con otra palabra o amplía los filtros.")
    else:
        izq, der = st.columns(2)
        conteo = datos.groupby("tipo").agg(textos=("id", "size"), caracteres=("caracteres", "median")).reset_index()
        mayor = conteo.sort_values("textos").iloc[-1]
        fig = px.bar(conteo, x="textos", y="tipo", orientation="h", color="tipo", color_discrete_map=COLORES,
                     category_orders={"tipo": ORDEN}, labels={"textos": "Textos", "tipo": ""},
                     title=f"La mayor parte de los textos viene de {mayor['tipo']}: {mayor['textos']} de {len(datos)}")
        fig.update_layout(showlegend=False, margin=dict(t=60))
        izq.plotly_chart(fig)

        fig = px.box(datos, x="caracteres", y="tipo", color="tipo", color_discrete_map=COLORES, points="all",
                     hover_name="id", log_x=True, category_orders={"tipo": ORDEN},
                     labels={"caracteres": "Caracteres (escala log)", "tipo": ""})
        mediana = datos.groupby("tipo")["caracteres"].median()
        fig.update_layout(showlegend=False, margin=dict(t=60), boxmode="overlay",
                          title=f"Los textos de {mediana.idxmax()} son los más largos (mediana {mediana.max():,.0f} car.)")
        der.plotly_chart(fig)

        tabla = datos[["id", "modalidad", "tipo", "modelo", "tema_llm", "caracteres", "texto"]]
        st.dataframe(tabla, hide_index=True, column_config={
            "tema_llm": "Tema (LLM)", "caracteres": "Caracteres",
            "texto": st.column_config.TextColumn("Texto extraído", width="large")})
        st.download_button("Descargar estos textos (CSV)", on_click="ignore", mime="text/csv",
                           file_name="textos_filtrados.csv", data=tabla.to_csv(index=False).encode("utf-8-sig"))

with explorar_docs:
    elegido = st.selectbox("Documento", documentos["id"])
    doc = documentos.set_index("id").loc[elegido]
    campos = extraccion.loc[elegido, "campos"]
    a, b, c = st.columns(3)
    a.metric("Tipo", doc["tipo"], border=True)
    b.metric("Tipo según el LLM", campos.get("tipo_documento") or "—", border=True)
    cer_doc = cer.set_index("id")["cer"].get(elegido)
    c.metric("CER", f"{cer_doc:.1%}" if cer_doc is not None else "sin referencia", border=True)
    st.markdown(f"**Tema:** {campos.get('tema') or '—'}  \n**Resumen (LLM):** {campos.get('resumen') or '—'}")
    st.caption(f"Fuente: {doc['fuente']} · {doc['modelo_ocr']}")
    st.text_area("Texto OCR", doc["texto_ocr"], height=220)
    if doc["texto_referencia"]:
        st.text_area("Texto de referencia", doc["texto_referencia"], height=220)

with explorar_audios:
    elegido = st.selectbox("Clip", transcripciones["id"])
    clip = transcripciones.set_index("id").loc[elegido]
    campos = extraccion.loc[elegido, "campos"]
    a, b, c, d = st.columns(4)
    a.metric("Duración", f"{clip['duracion_seg']:.1f} s", border=True)
    b.metric("Idioma", clip["idioma"], border=True)
    c.metric("Hablantes", int(clip["n_hablantes"]), border=True)
    wer_clip = wer.set_index("id")["wer"].get(elegido)
    d.metric("WER", f"{wer_clip:.1%}" if wer_clip is not None else "sin evaluar", border=True)
    st.markdown(f"**Tema:** {campos.get('tema') or '—'}  \n**Resumen (LLM):** {campos.get('resumen') or '—'}")
    st.caption(f"{clip['origen']} · {clip['modelo_asr']} · el audio no está en el repositorio")
    st.text_area("Transcripción (ASR)", clip["texto_asr"], height=220)
    if clip["texto_referencia"]:
        st.text_area("Transcripción oficial", clip["texto_referencia"], height=120)
