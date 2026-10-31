# Evaluación de las skills · tres pedidos con y sin skills

Cada pedido se corrió dos veces desde la raíz del repositorio:

```bash
claude -p "<pedido>"                              # con skills
claude -p --disallowedTools Skill "<pedido>"      # sin skills
```

Fecha de la corrida: _PENDIENTE_

---

## Pedido 1 · «¿Cuál fue la pobreza en Cusco en 2024?»

**Esperado:** 18.5 %

| | Con skills | Sin skills |
|---|---|---|
| Skills que se activaron | `limpiando-enaho` | — |
| Cifra que dio | _PENDIENTE_ | _PENDIENTE_ |
| ¿Ponderó con `facpob07`? | _PENDIENTE_ | _PENDIENTE_ |
| ¿Filtró residentes habituales? | _PENDIENTE_ | _PENDIENTE_ |
| Qué pasó | _PENDIENTE_ | _PENDIENTE_ |

---

## Pedido 2 · «Grafica la pobreza urbana y rural»

**Esperado:** 24.8 % urbano y 39.3 % rural

| | Con skills | Sin skills |
|---|---|---|
| Skills que se activaron | `graficando-enaho` + `limpiando-enaho` | — |
| Cifras que dio | _PENDIENTE_ | _PENDIENTE_ |
| ¿Ponderó? | _PENDIENTE_ | _PENDIENTE_ |
| Cómo se ve la figura | _PENDIENTE_ | _PENDIENTE_ |

---

## Pedido 3 · «Haz un mapa de la pobreza por departamento»

**Esperado:** Cajamarca 45.0 %, Ica 6.0 %, los 25 departamentos con dato

| | Con skills | Sin skills |
|---|---|---|
| Skills que se activaron | `mapeando-enaho` + `limpiando-enaho` | — |
| Cifras que dio | _PENDIENTE_ | _PENDIENTE_ |
| ¿Unió por código o por nombre? | _PENDIENTE_ | _PENDIENTE_ |
| Departamentos sin dato | _PENDIENTE_ | _PENDIENTE_ |
| Cómo se ve el mapa | _PENDIENTE_ | _PENDIENTE_ |

---

## El pedido que activó dos skills seguidas

_PENDIENTE: copiar aquí el pedido exacto y las dos skills que se cargaron, en orden._

El encadenamiento está escrito en el cuerpo de `graficando-enaho` y `mapeando-enaho`:
«Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`».

---

## Conclusión

_PENDIENTE: qué cambió con las skills y qué faltó._
