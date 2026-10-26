# Tarea 2 — De documentos y audio a texto estructurado

**Pregunta guía:** ¿se pueden convertir documentos escaneados y entrevistas en audio en un archivo de texto estructurado y buscable?

**Respuesta corta:** sí, con modelos abiertos y en una laptop sin GPU, siempre que se revise lo que el modelo no sabe que hizo mal.
El texto impreso y las frases leídas salen casi perfectos; la letra a mano, las fotos difíciles y el audio débil o en quechua necesitan revisión humana.

**Autor:** Renato Gates Rojas (@RenatoGates)

**Dashboard público:** _pendiente de desplegar en Streamlit Cloud (`tarea_2/app.py`)_

## Corpus

| Corpus | Contenido | Fuente | Licencia |
|---|---|---|---|
| A — documentos | 35 documentos: 14 impresos (8 páginas de una resolución del MINJUS + 6 fotos de impresos), 12 fotos, 9 manuscritos. Se descartó 1 foto ilegible. | Capturas propias en Lima; Resolución Directoral N.º 4378-2025-JUS/DGTAIPD-DPDP | Propia (uso académico autorizado); documento público del Estado peruano |
| B — audio | 60 clips, 40,9 min, 3 multihablante: 40 frases de OpenSLR 73 (español peruano), 12 de FLEURS (inglés), 6 entrevistas de Wikimedia Commons (español, inglés y quechua de Huaylas), 1 entrevista simulada y 1 reunión de trabajo propia | OpenSLR, Hugging Face, Wikimedia Commons, grabación propia | CC BY-SA 4.0, CC BY 4.0, propia con consentimiento |

La atribución archivo por archivo está en `datos/fuentes.csv`. Las imágenes y los audios no se versionan.
Los textos publicados están seudonimizados; la tabla de equivalencias no se publica.

## Hallazgos

1. **La confianza del modelo no mide su exactitud.** PaddleOCR da una confianza mediana de 0,97 a los manuscritos, pero lee
   "CALDOPGALLINA" con 0,98. El CER contra transcripciones hechas a mano es de 15 % en una pizarra y 18 % en una foto con tachones,
   frente a menos de 1 % en una página impresa leída en el mismo orden que su capa de texto.
2. **El VAD evita que Whisper invente en el silencio, pero no evita los bucles.** En frases leídas en estudio el WER global es 1,9 %.
   En audio débil o en un idioma que no conoce, Whisper repite el mismo segmento: "y" doce veces seguidas en una entrevista en quechua,
   la misma frase cuatro veces al final de la reunión de trabajo.

## Limitaciones

1. **Recorte por tiempo de cómputo.** Todo corrió en CPU (Intel Core i7-1355U, sin GPU): el OCR tomó 19,7 min y el ASR 48,5 min para
   40,9 min de audio. Por eso no se compararon modelos alternativos ni se armó un set de casos difíciles.
2. **Pocas referencias y auditoría no independiente.** El CER se calculó en 10 documentos (8 de un mismo PDF) y el WER en 10 frases
   leídas, el caso fácil. La auditoría de la extracción LLM (96,7 % de campos correctos en 20 casos) la prellenó el mismo modelo
   que extrajo y falta confirmarla a mano. Además, `man_04_pizarra_menu_2.jpg` contiene la foto de un letrero de tienda, no un
   manuscrito, y queda pendiente reclasificarla.

## Archivos

| Archivo | Qué es |
|---|---|
| `01_extraccion.ipynb` | Parte 1: OCR, ASR, diarización, seudonimización, descartes, gráficos y exportación |
| `02_evaluacion.ipynb` | Parte 2: CER, WER, extracción LLM, auditoría y tabla final |
| `app.py` | Parte 3: dashboard en Streamlit |
| `datos/documentos.csv`, `datos/transcripciones.csv` | Texto extraído, una fila por documento o clip |
| `datos/asr/` | Transcripciones seudonimizadas en SRT, TXT y CSV |
| `datos/extraccion_llm.csv`, `datos/auditoria_llm.csv` | Extracción estructurada y su auditoría |
| `datos/ejemplos/` | Copia ligera de los CSV que lee el dashboard (menos de 200 KB) |

## Ejecutar en local

El dashboard solo necesita los CSV de `datos/ejemplos/`:

```bash
cd tarea_2
pip install -r requirements.txt
streamlit run app.py
```

Los notebooks necesitan el entorno del curso (PaddleOCR, faster-whisper, pyannote) y el módulo `voz.py` de la sesión 13,
además de las imágenes y los audios en `documentos/` y `audios/`:

```bash
uv sync --group docai --group audio      # en el repositorio del curso
uv pip install plotly pypdf kaleido
jupyter nbconvert --to notebook --execute --inplace 01_extraccion.ipynb
jupyter nbconvert --to notebook --execute --inplace 02_evaluacion.ipynb
```
