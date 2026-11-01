# De la agencia al bodeguero

**Cómo se redistribuyó el acceso financiero en el Perú, 2021–2026**

Tarea 3 del curso de Ciencia de Datos con Python (QLAB / UP 2026-II) — Renato Gates Rojas
([@RenatoGates](https://github.com/RenatoGates)).

| | |
|---|---|
| **Tablero** | _pendiente_ |
| **LinkedIn** | _pendiente_ |
| **Reel** | [`reel/reel.mp4`](reel) |

## La pregunta

> ¿Dónde está la brecha de acceso financiero en el Perú y cómo cambió entre 2021 y 2026?

**Cobertura:** los 25 departamentos del Perú. **Periodo:** junio 2021 a junio 2026 para la red
de atención y los deudores; diciembre 2020 a diciembre 2025 para la tenencia de cuentas.

## Tres hallazgos

**1 · El acceso físico se estancó, pero la bancarización saltó.**
Los puntos de atención por cada 100 mil adultos pasaron de 1,330 a 1,308: una caída de 1.7 %.
En el mismo periodo la proporción de adultos con alguna cuenta subió de **42.3 % a 59.6 %**,
17.2 puntos porcentuales. La inclusión avanzó sin más infraestructura.

**2 · La brecha se cerró por redistribución, no por crecimiento.**
Huancavelica multiplicó su red por 3.6 (de 720 a 2,573 puntos por 100 mil adultos) y Madre de
Dios por 2.8. Al mismo tiempo Arequipa perdió 35 %, Lima 26 % y Callao 23 %. La razón entre el
departamento mejor y peor servido bajó de **4.0x a 2.9x**.

**3 · Las oficinas cierran y el bodeguero sostiene la red.**
Las oficinas por 100 mil adultos cayeron de 19 a 16 y los cajeros automáticos de 130 a 125.
Hoy los cajeros corresponsales son el **89.2 %** de todos los puntos de atención del país, y en
algunos departamentos superan el 97 %. El punto de acceso financiero típico del peruano ya no
es una agencia: es una bodega.

El mayor salto individual lo dio Cusco, que pasó de 30.1 % a 60.9 % de adultos con cuenta:
**+30.9 puntos en cinco años.**

## Fuentes

| Fuente | Qué aporta | Acceso |
|---|---|---|
| SBS, *Perú: Reporte de Indicadores de Inclusión Financiera*, junio 2026 | Red de atención, infraestructura, distritos con acceso, deudores y tenencia de cuentas, todo por departamento | [Cifras de inclusión financiera](https://www.sbs.gob.pe/inclusion-financiera-principal/cifras-de-inclusion-financiera) · PDF público y semestral |
| SBS, Anexo 10 y Reporte 30 | Insumo de la SBS para la red de atención | Dentro del reporte |
| SBS, Reporte Crediticio Consolidado | Insumo para el número de deudores | Dentro del reporte |
| INEI, proyecciones de población adulta por departamento 2021–2026 | Denominador de todos los indicadores por 100 mil adultos | Dentro del reporte |
| INEI, Encuesta Nacional de Hogares (ENAHO) | Tenencia de cuentas | Dentro del reporte |
| Límites departamentales del Perú (GeoJSON) | Geometría de los 25 departamentos | [Repositorio del curso](https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson) |

Todos los datos son públicos. No se usó información interna de ninguna entidad.

## Metodología

1. **Obtención.** Se descarga el reporte semestral de la SBS en PDF desde su portal de cifras
   de inclusión financiera.
2. **Extracción.** `scripts/extraer_sbs.py` lee los cuadros departamentales con `pdfplumber`,
   reconoce las filas por nombre de departamento, normaliza tildes y asigna el código de ubigeo
   de dos dígitos. Los cuadros usados son los de disponibilidad de la red de atención (pág. 11),
   infraestructura de atención (pág. 14) e indicadores de uso (pág. 24).
3. **Construcción.** `scripts/construir.py` une los tres cuadros, calcula variaciones y
   participaciones, y verifica con asserts que haya 25 departamentos, sin códigos duplicados
   ni celdas vacías.
4. **Visualización.** El tablero une por **código de ubigeo**, nunca por nombre, contra los
   límites departamentales. Lima (15) y Callao (07) van separados.

**Definiciones.** Un *punto de atención* es la suma de oficinas, cajeros automáticos, cajeros
corresponsales y establecimientos con operaciones básicas (EOB). La *disponibilidad* cuenta cada
cajero o establecimiento tantas veces como entidades operan a través de él; la *infraestructura*
lo cuenta una sola vez. El tablero usa la disponibilidad, que mide la oferta efectiva que ve una
persona. Ambas series están en los datos procesados.

## Limitaciones

- **Dos cortes, no una serie.** El reporte compara junio 2021 con junio 2026; no hay puntos
  intermedios, así que no se sabe si el cambio fue gradual o de golpe.
- **Las fechas no coinciden entre bloques.** La red de atención y los deudores son a junio de
  cada año; la tenencia de cuentas viene de la ENAHO y corresponde a diciembre de 2020 y 2025.
- **Denominador proyectado.** La población adulta por departamento son proyecciones del INEI,
  no un censo.
- **Disponibilidad no es uso.** Un corresponsal puede existir y casi no operar.
- **Correlación, no causalidad.** Que la bancarización suba mientras la red se estanca sugiere
  que el canal digital explica el avance, pero estos datos no lo prueban.
- **El promedio departamental esconde el interior.** Un departamento con buena capital puede
  seguir teniendo distritos sin ningún punto de atención.

## Cómo reproducirlo

```bash
cd tarea_3
pip install -r requirements.txt

# 1. Baja el reporte de la SBS a datos/crudos/
#    https://www.sbs.gob.pe/inclusion-financiera-principal/cifras-de-inclusion-financiera
#    (edición a junio de 2026, archivo CIIF-0001-jn2026.pdf)

# 2. Extrae los cuadros departamentales del PDF
python scripts/extraer_sbs.py datos/crudos/CIIF-0001-jn2026.pdf

# 3. Arma el panel y los agregados nacionales
python scripts/construir.py

# 4. Levanta el tablero
streamlit run web/app.py
```

El PDF original no se versiona (`datos/crudos/` está en el `.gitignore`); los CSV procesados sí,
para que el tablero funcione sin tener que descargar nada.

## Estructura

```text
tarea_3/
  README.md
  requirements.txt            pipeline completo
  scripts/
    extraer_sbs.py            PDF de la SBS -> cuadros departamentales en CSV
    construir.py              cuadros -> panel y agregados nacionales
  datos/
    crudos/                   el PDF de la SBS (no se versiona)
    procesados/               sbs_red.csv, sbs_infraestructura.csv, sbs_uso.csv
  web/
    app.py                    el tablero en Streamlit
    requirements.txt          solo lo que necesita el tablero
    data/                     panel_departamental.csv, nacional.csv, GeoJSON
  reel/
    guion.json                guion por escenas, con las cifras verificadas
    reel.mp4  reel.srt  portada.png
```

## Uso de inteligencia artificial

Se usó Claude (Opus 5 y Opus 5.5, vía chat y Claude Code) para escribir el extractor del PDF,
construir el tablero y redactar este README. Las cifras provienen del reporte de la SBS y fueron
verificadas contra el documento original; los hallazgos y su interpretación son propios.

La narración del reel es una voz sintética generada con Qwen3-TTS a partir de una grabación de mi
propia voz, siguiendo el flujo de la sesión 15 del curso. El video lo indica en pantalla.
