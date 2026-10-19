# Clasificación de titulares de noticias peruanas

**Dashboard:** _(pendiente: aquí va el enlace de Streamlit Cloud)_
**Modelo:** [gates1179/distilbeto-titulares-peru](https://huggingface.co/gates1179/distilbeto-titulares-peru) en Hugging Face Hub

## Pregunta

¿Puede un Transformer ligero en español, entrenado en CPU con menos de 300 titulares etiquetados por un LLM, clasificar el tema de titulares de noticias peruanas mejor que un modelo zero-shot que no recibe ningún ejemplo?

Las categorías son cuatro y fijas: `politica`, `economia`, `deportes` y `ciencia_tecnologia`.

## Datos

- **Fuente.** El archivo por sección de El Comercio (`elcomercio.pe/archivo/<sección>/`) para política, economía, deporte-total y tecnología, descargado el 18 de octubre de 2026. El `robots.txt` del sitio permite esas rutas. El scraping se hizo con un User-Agent descriptivo, pausas de 1 a 2 segundos y como máximo un reintento por pedido.
- **Limpieza.** De 400 notas descargadas se quitó 1 duplicada y se descartaron 15 de secciones ajenas a las cuatro categorías (opinión, ecdata y otras). Las 384 URLs restantes respondieron 200. Los titulares van del 6 al 18 de octubre de 2026.
- **Etiquetas.** Cada nota trae una etiqueta débil, la sección donde la publicó el medio. Para entrenar, un LLM (Claude Opus 5.5) etiquetó los 384 titulares en 14 lotes de 27 o 28, viendo solo el texto del titular. Una persona auditó 20 casos al azar (5 por categoría) y estuvo de acuerdo con el LLM en los 20.

Archivos: `datos/noticias.csv` (titulares con su etiqueta por sección), `datos/etiquetas_llm.csv` (etiqueta del LLM y lote) y `datos/auditoria_humana.csv` (los 20 casos auditados).

## Hallazgos

1. **El fine-tune supera al zero-shot por unos 20 puntos de F1 macro.** Sobre los mismos 40 titulares del conjunto de test, DistilBETO ajustado obtiene 0,925 y el zero-shot (mDeBERTa-v3, multilingüe) 0,726. El intervalo del 95 % por bootstrap pareado para la diferencia va de +0,07 a +0,36, así que no es ruido. En el test completo (58 titulares), el fine-tune acierta 54 (F1 macro 0,929). El entrenamiento tomó 5,7 minutos en un portátil sin GPU.
2. **El zero-shot falla donde el tema no está nombrado.** Clasificó como `politica` los 5 titulares del rally Caminos del Inca, que hablan de etapas y liderato sin decir qué deporte es. El fine-tune acertó los cinco, porque había visto 7 titulares de la misma carrera en el entrenamiento.
3. **La sección del medio y el tema del titular coinciden en el 96,4 % de los casos** (370 de 384; kappa de Cohen 0,951). Deportes coincide siempre. Las 14 diferencias son casos de frontera, como la filtración de datos de una aseguradora publicada en economía pero que trata de ciberseguridad, o notas sobre Trump y la inteligencia artificial publicadas en tecnología pero que tratan de un gobierno.
4. **Los titulares son cortos.** El 95 % tiene 24 palabras o menos, y el más largo ocupa 47 tokens del modelo, por lo que basta una longitud máxima de entrada de 64.

## Limitaciones

- **Una sola semana larga y un solo medio.** Todo viene de El Comercio y de 13 días (deportes cubre solo 5). La coyuntura pesa: 16 titulares tratan del debate de las facultades legislativas en el Senado y 15 del Torneo Clausura. Parte de la ventaja del fine-tune se debe a que vio esos mismos eventos en el entrenamiento; con titulares de otras semanas u otros medios, la distancia con el zero-shot probablemente se acorte.
- **Las métricas miden acuerdo con el LLM, no con una verdad.** La auditoría de 20 casos coincidió en los 20, pero con esa muestra la tasa real de acierto del LLM podría ser tan baja como 83 % (intervalo del 95 %).
- **Test pequeño.** Con 58 titulares de test, y 40 para la comparación, un solo error mueve el F1 macro entre 2 y 3 puntos.
- **El esquema de categorías no es exhaustivo ni excluyente.** Los videojuegos, por ejemplo, quedan en `ciencia_tecnologia` a falta de una categoría de entretenimiento, y un titular sobre regulación de la IA es a la vez tecnología y política.
- **Etiquetado no del todo ciego.** En los lotes, cada titular llevaba su número de fila, y el CSV está ordenado por sección. Las etiquetas se decidieron por el texto, pero un procedimiento estricto usaría identificadores al azar.
- **El clasificador del dashboard siempre elige una de las cuatro categorías**, aunque el titular sea de otro tema.

## Cómo correr el proyecto

Requiere Python 3.11 o 3.12 (`numpy==1.26.4` no tiene versiones para 3.13 en adelante). Desde la raíz del repositorio:

```bash
pip install -r tarea_1/requirements.txt
```

El archivo instala la versión de torch solo para CPU desde el índice de PyTorch, sin las dependencias de CUDA.

**Notebooks** (abrirlos con la carpeta `tarea_1/` como directorio de trabajo):

1. `01_recoleccion.ipynb`: scraping, limpieza, mapeo de secciones y gráficos (unos 11 minutos). Al volver a correrlo se descarga el archivo de ese día y se sobrescribe `datos/noticias.csv` con titulares distintos.
2. `02_clasificacion.ipynb`: comparación de etiquetas, auditoría, split, zero-shot, fine-tune y métricas (unos 13 minutos en CPU). Guarda el modelo en `modelo/`. La celda de subida a Hugging Face tiene `SUBIR_A_HF = True`: si se corre el notebook completo, publica el modelo otra vez; para evitarlo, hay que cambiarlo a `False`.

**Dashboard**, desde la raíz del repositorio:

```bash
streamlit run tarea_1/app.py
```

Descarga el modelo desde Hugging Face la primera vez que se clasifica un titular. El archivo `.streamlit/config.toml` de la raíz desactiva el vigilante de archivos de Streamlit, que si no importa todos los submódulos de `transformers` y llena el registro de errores.

**Despliegue en Streamlit Community Cloud:** archivo principal `tarea_1/app.py`; en *Advanced settings*, Python 3.11.

## Estructura

```
tarea_1/
├── 01_recoleccion.ipynb      Parte 1: recolección de titulares
├── 02_clasificacion.ipynb    Parte 2: etiquetado, fine-tune y evaluación
├── app.py                    Parte 3: dashboard en Streamlit
├── requirements.txt
├── datos/
│   ├── noticias.csv
│   ├── etiquetas_llm.csv
│   └── auditoria_humana.csv
└── modelo/                   configuración, tokenizer y tarjeta (los pesos están en Hugging Face)
```
