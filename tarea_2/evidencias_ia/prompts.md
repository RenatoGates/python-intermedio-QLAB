# Evidencias del uso de IA — Tarea 2

Asistente: **Claude Opus 5.5** vía Claude Code (CLI), y **Claude Opus 5** vía chat
para el diseño del corpus y la redacción de los prompts.

Las capturas de pantalla (`01.png`, `02.png`, ...) documentan los momentos clave.
Abajo van los prompts completos tal como se enviaron.

---

## 1. Recolección y clasificación del corpus (chat)

Sesión de ida y vuelta para decidir fuentes y licencias. Decisiones tomadas:

- **Corpus B**: usar OpenSLR 73 y las entrevistas de Wikimedia Commons que el
  propio enunciado nombra, en lugar de descargar de YouTube. Motivo: la licencia
  estándar de YouTube no permite redistribución y la rúbrica exige atribución.
- **Descartes por datos personales**: se excluyeron una foto de un cartel con
  contraseña de WiFi, una receta médica (número de historia clínica, diagnóstico
  CIE-10 y medicamentos) y una página de un libro con derechos de autor.
- **Censuras aplicadas**: DNI en la boleta de Tottus (dos apariciones), QR de
  pago, teléfonos en los menús de El Edén, nombre y firma en una hoja manuscrita,
  nombre completo en el diploma.
- **Descarte por ámbito**: una foto tomada fuera del Perú.
- **Orientación**: dos manuscritos venían rotados 90°. Se enderezaron, porque el
  pipeline corre con `use_doc_orientation_classify=False` y una página de lado
  habría dado un CER malo por la rotación y no por la letra.

## 2. Parte 1 — `01_extraccion.ipynb` (Claude Code)

Prompt enviado:

```
Contexto: estoy haciendo la Tarea 2 del curso de Ciencia de Datos con Python
(UP 2026-II), issue d2cml-ai/Data-Science-Python#190. Trabajo en la rama
parte-1-extraccion. El corpus YA está recolectado y clasificado. No descargues
ni agregues material nuevo.

Material disponible en tarea_2/ (todo gitignoreado, no lo subas a Git):
  documentos/impresos/     imp_01_resolucion_minjus_4378_2025.pdf (8 páginas) + 6 jpg
  documentos/fotos/        13 jpg (fotos con sombra, inclinación, poca luz)
  documentos/manuscritos/  9 jpg (pizarras de tiza, pancartas, hojas de cuaderno)
  audios/aud_01_reunion_laboral.mp4   489 s, 2 hablantes, grabación propia
  audios/entrevistas/      6 ogg de Wikimedia Commons + atribucion.csv
  audios/es_peru/          40 wav de OpenSLR 73 + transcripciones.csv + 
                           entrevista_simulada.wav (106 s, 16 turnos) +
                           entrevista_simulada.csv (verdad de diarización)
  audios/en_fleurs/        12 wav en inglés
  datos/fuentes.csv        89 filas con id, modalidad, fuente_url, licencia, acceso

Usa el módulo voz.py del curso. Expone: SR, Transcriptor, cargar_audio,
tramos_de_voz, diarizar, a_texto, a_srt, a_tabla, seudonimizar, dispositivo().
Impórtalo con sys.path, no lo copies.

TAREA: crea tarea_2/01_extraccion.ipynb con estas 8 secciones, en este orden.

1. Primera celda: fecha de ejecución, resumen de fuentes y licencias leído de
   fuentes.csv, y las versiones de paddleocr, transformers, faster-whisper y torch.
2. OCR de los 28 documentos con PaddleOCR. Rasteriza el PDF a PNG con PyMuPDF a
   200 dpi. Modelo: PaddleOCR(engine="transformers",
   use_doc_orientation_classify=False, use_doc_unwarping=False,
   use_textline_orientation=False). Guarda texto y confianza mediana.
3. ASR. vad_filter=True SIEMPRE. faster-whisper para todos los clips.
   Diarización en agustino_2.ogg, entrevista_simulada.wav y
   aud_01_reunion_laboral.mp4. Exporta CSV, SRT y TXT.
4. Seudonimización con voz.seudonimizar(). Reporta entidades reemplazadas.
5. Deduplica por hash. Descarta ilegibles y audios sin voz, con motivos.
6. Tres gráficos Plotly Express con títulos que sean conclusiones analíticas.
7. Los 3 textos más largos y más cortos, y los 3 clips más largos y más cortos.
8. Exporta datos/documentos.csv y datos/transcripciones.csv con las columnas
   exactas del enunciado. Llena texto_referencia donde ya lo tenemos gratis:
   los 40 clips de OpenSLR y las 8 páginas del PDF del MINJUS (pypdf).

Reglas: kernel del entorno uv del curso; comentarios mínimos en el código;
rutas relativas; ejecuta el notebook completo y guárdalo CON outputs; no
commitees documentos/ ni audios/; commits descriptivos por sección.
```

### Hallazgo durante la ejecución

PaddleOCR corría entre 102 y 337 segundos por imagen, contra los ~6 s/página que
el profesor midió en CPU. El asistente perfiló el modelo y encontró que el
detector PP-OCRv6 tiene **7 millones de pesos subnormales**, que la CPU procesa en
un modo degradado. Activando `torch.set_flush_denormal(True)` el forward bajó de
38,7 s a 8,0 s, y el documento más lento de 337 s a 26 s, sin cambiar el texto ni
la confianza. No ocurre en Mac, por eso no aparece en el notebook de clase.

## 3. Parte 2 — `02_evaluacion.ipynb` (Claude Code)

Prompt enviado: ver `prompt_parte2.txt` en esta misma carpeta.

El LLM de la sección de extracción estructurada es el propio asistente
(Claude Opus 5.5); el prompt exacto y la fecha quedan documentados dentro del
notebook, junto al CSV `extraccion_llm.csv`.

## 4. Correcciones que la IA necesitó

Registro de momentos en que el asistente se equivocó o hubo que corregirlo:

1. **Fecha de entrega**: al leer el issue se interpretó la fecha límite como
   25 de noviembre. Era el 26 de octubre. Se detectó porque los compañeros ya
   estaban publicando sus entregas.
2. **OCR alternativo**: la primera recomendación fue Tesseract. Se cambió a
   PaddleOCR-VL porque Tesseract exige instalar un binario de Windows y
   configurar el PATH, y el VL ya estaba instalado con el grupo `docai`.
3. **PaddleOCR en CPU**: ver el hallazgo de los pesos subnormales arriba.
