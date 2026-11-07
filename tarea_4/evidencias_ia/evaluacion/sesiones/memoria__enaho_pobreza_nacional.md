# Evaluación · enaho_pobreza_nacional · modo memoria

Sesión nueva de `claude -p --model haiku` en la copia aislada de tarea_4/, con las opciones del modo `memoria` (ver evaluacion/comparacion.md). Respuesta esperada: 27.5795 ± 0.1.

## Pedido

```text
Responde con un solo número en «valor», en la unidad que pide la pregunta. Si no puedes saberlo con certeza, pon valor null: no estimes. En «fuente» di de dónde sale la cifra; si combinas varias fuentes, nómbralas todas.

Según la ENAHO 2024 del INEI, ¿qué porcentaje de la población del Perú estaba en situación de pobreza monetaria en 2024, en %?
```

**Modelo:** claude-haiku-5-5  
**Directorio:** `<copia>/tarea_4`  
**Servidores MCP:** ninguno  
**Herramientas:** StructuredOutput

### → Llama a `StructuredOutput`

```json
{
 "valor": 27.6,
 "unidad": "%",
 "fuente": "INEI, Encuesta Nacional de Hogares (ENAHO) 2024, nota de prensa sobre pobreza monetaria 2024 (cifra de incidencia de pobreza monetaria). Cifra citada de memoria; no pude verificarla contra el sitio del INEI en esta sesión, ya que no tengo acceso a internet."
}
```

#### ← Resultado

```text
Structured output provided successfully
```

## Resultado

- Herramientas, en orden: StructuredOutput
- Turnos: 2
- Segundos: 4.8
- Costo informado por Claude Code: US$ 0.0008
- ¿Terminó con error?: False
