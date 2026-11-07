# Variables de la ENAHO que están en la base limpia

Una fila por persona residente habitual. Archivo: `salidas/personas_<año>.parquet`.

## Llaves

| Columna | Qué es |
|---|---|
| `conglome`, `vivienda`, `hogar` | Identifican al hogar. Son **texto**: `conglome` llega como «015009» y como número pierde el cero. |
| `codperso` | Identifica a la persona dentro del hogar. |

## Factores de expansión

| Columna | Úsalo para |
|---|---|
| `facpob07` | Cifras de **personas**. Es el que usa esta base. |
| `factor07` | Cifras de **hogares**, en la sumaria. Para personas va multiplicado por `mieperho`. |

Ninguna cifra se reporta sin ponderar. Un porcentaje se calcula como
`100 * peso[condición].sum() / peso.sum()`, nunca como `condición.mean()`.

## Pobreza

| Columna | Valores |
|---|---|
| `pobreza` | 1 pobre extremo · 2 pobre no extremo · 3 no pobre. **Son códigos, no una escala**: nunca promedies. |
| `pobre` | `pobreza <= 2` |
| `pobre_extremo` | `pobreza == 1` |

## Geografía

| Columna | Qué es |
|---|---|
| `ubigeo` | Seis dígitos como texto: departamento (2) + provincia (2) + distrito (2). |
| `departamento` | `ubigeo[:2]`. Lima es `15` y Callao `07`, separados. |
| `estrato` | 1 a 5 urbano, 6 a 8 rural. |
| `urbano` | `estrato <= 5` |
| `dominio` | 1 a 8. Lima Metropolitana es `dominio == 8` (28.2 % de pobreza en 2024). |

## Personas

| Columna | Qué es |
|---|---|
| `p203` | Parentesco con el jefe de hogar. |
| `p204`, `p205`, `p206` | Residencia. El filtro de residentes habituales ya está aplicado. |
| `p207` | Sexo: 1 hombre, 2 mujer. |
| `p208a` | Edad en años cumplidos. |
| `mieperho` | Miembros del hogar, viene de la sumaria. |

## Si falta una variable

No está en esta base: hay que volver al módulo del INEI y agregarla en
`scripts/limpiar.py`, no calcularla al vuelo. Los módulos útiles:

| Módulo | Tema |
|---|---|
| 01 | Características de la vivienda |
| 02 | Características de los miembros del hogar |
| 03 | Educación |
| 04 | Salud |
| 05 | Empleo e ingresos |
| 34 | Sumaria: gasto, ingreso y pobreza por hogar |
