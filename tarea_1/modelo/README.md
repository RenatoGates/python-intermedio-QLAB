---
language: es
pipeline_tag: text-classification
base_model: dccuchile/distilbert-base-spanish-uncased
---

# Clasificador de titulares de noticias peruanas

Fine-tune de [dccuchile/distilbert-base-spanish-uncased](https://huggingface.co/dccuchile/distilbert-base-spanish-uncased) que clasifica titulares en cuatro categorías: `politica`, `economia`, `deportes`, `ciencia_tecnologia`.

- Datos: 268 titulares de entrenamiento de El Comercio (Perú), publicados entre el 06/10/2026 y el 18/10/2026.
- Etiquetas: asignadas por un LLM (Claude Opus 5.5) a partir del titular. Una auditoría humana de 20 casos estuvo de acuerdo en 20.
- F1 macro en test (58 titulares): 0.929.

Proyecto académico del curso de Ciencia de Datos con Python (QLAB / UP 2026-II). Limitaciones: un solo medio, una ventana de 13 días y un esquema de cuatro categorías que no siempre son excluyentes.
