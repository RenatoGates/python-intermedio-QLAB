# Variables de las bases limpias de la ENAHO · versión tarea_4

Dos bases, una por unidad de análisis. Elige la del corte: **hogar** para todo lo que describe al hogar (pobreza
oficial, área, departamento, tipo de hogar, gasto) y **persona** solo para atributos de la persona (sexo, edad).

## `salidas/hogares_<año>.parquet` · una fila por hogar (33,691 en 2024)

| Columna | Qué es |
|---|---|
| `conglome`, `vivienda`, `hogar` | Llaves del hogar, **texto** de largo fijo (`conglome` = «015009»; como número perdería el cero). |
| `ubigeo` | Seis dígitos como texto: departamento (2) + provincia (2) + distrito (2). |
| `departamento` | `ubigeo[:2]`. Lima es `15` y Callao `07`, separados. Se une al mapa con `FIRST_IDDP`. |
| `estrato`, `urbano` | Estrato 1 a 5 urbano, 6 a 8 rural; `urbano = estrato <= 5`. |
| `dominio` | 1 a 8. Lima Metropolitana es `dominio == 8`. |
| `mieperho` | Miembros del hogar según la sumaria. |
| `factor07` | Factor de expansión del hogar. Úsalo solo para cifras **de hogares** («% de hogares»). |
| `peso_personas` | `factor07 × mieperho`. **El peso de la cifra oficial** («% de personas»). |
| `pobreza` | 1 pobre extremo · 2 pobre no extremo · 3 no pobre. **Códigos, no una escala**: nunca promedies. |
| `pobre`, `pobre_extremo` | `pobreza <= 2` y `pobreza == 1`. |
| `n_residentes` | Residentes habituales del hogar en el módulo 02. Coincide con `mieperho` en la gran mayoría de hogares, no en todos. |
| `n_am`, `n_menores_18` | Residentes de 65 años o más y menores de 18. |
| `jefe_am` | El jefe del hogar (`p203 == 1`) tiene 65 años o más. |
| `tipo_hogar_am` | «Sin adultos mayores», «Con adultos mayores y menores de 65» o «Solo adultos mayores». |
| `am_vive_solo` | Hogar de una sola persona, de 65 años o más. |
| `g1_alimentos` … `g8_otros` | Gasto anual por grupo de la canasta, en soles corrientes, según el do-file del INEI. |
| `g0_total` | Suma de los 8 grupos. Es igual a `gashog2d` (el script lo comprueba). |
| `part_alimentos` | `100 × g1_alimentos / g0_total`: % del gasto del hogar que va a alimentos. Mide **exposición** a la inflación de alimentos. |
| `gasto_pc_mensual` | `g0_total / (12 × mieperho)`, soles corrientes por persona al mes. |

## `salidas/personas_<año>.parquet` · una fila por residente habitual (108,664 en 2024)

Las llaves del hogar, `codperso` y las columnas del hogar de arriba (`pobreza`, `pobre`, `peso_personas`,
`departamento`, `urbano`, `tipo_hogar_am`, `part_alimentos`…), más:

| Columna | Qué es |
|---|---|
| `p203` | Parentesco con el jefe del hogar (1 = jefe). |
| `p207` | Sexo: 1 hombre, 2 mujer. |
| `p208a` | Edad en años cumplidos. |
| `adulto_mayor` | `p208a >= 65`. |
| `facpob07` | Factor de expansión de la persona. **Peso de la base persona (secundaria)**. |

## `salidas/indicadores.csv`

Una fila por cifra: `indicador, corte, grupo, valor, unidad, ponderador, n_muestral`. La columna `ponderador` dice
con qué base salió cada cifra; `n_muestral` es el número de hogares (o personas) de la muestra detrás de ella.

| `indicador` | Cortes |
|---|---|
| `pobreza`, `pobreza_extrema` | nacional, area, departamento, tipo_hogar_am, tipo_hogar_am × area, edad_persona (facpob07) |
| `part_alimentos`, `gasto_pc_mensual` | nacional, tipo_hogar_am, tipo_hogar_am × area |
| `hogares`, `personas`, `rural` | tipo_hogar_am: qué parte de los hogares, de las personas y de lo rural le toca a cada tipo |
| `hogares_con_am`, `am_vive_solo` | nacional |
| `personas_en_hogares_am`, `pobreza_hogares_am` | departamento |

## Factores de expansión

Ninguna cifra se reporta sin ponderar. Un porcentaje es `100 * peso[condición].sum() / peso.sum()`; un promedio,
`np.average(x, weights=peso)`. Nunca `condición.mean()` ni contar filas: sin ponderar, la pobreza de la muestra de
hogares sale muy por debajo de la oficial (la cifra exacta está en `validacion.txt`).

## Si falta una variable

No está en estas bases: hay que agregarla en `scripts/limpiar.py` desde el módulo del INEI, no calcularla al vuelo.

| Módulo | Tema |
|---|---|
| 01 | Características de la vivienda |
| 02 | Características de los miembros del hogar |
| 03 | Educación |
| 04 | Salud |
| 05 | Empleo e ingresos |
| 34 | Sumaria: gasto, ingreso y pobreza por hogar |
