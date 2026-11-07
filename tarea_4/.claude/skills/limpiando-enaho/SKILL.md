---
name: limpiando-enaho
description: Limpia y valida los módulos 34 (sumaria) y 02 (miembros) de la ENAHO del INEI y arma las bases de hogares y de personas con pobreza monetaria, departamento, área urbana o rural, gasto en alimentos y presencia de adultos mayores (65+), ponderadas con factor07 × mieperho. Úsala cuando pidan limpiar, unir, validar o analizar la ENAHO, o calcular pobreza, pobreza extrema, gasto en alimentos u hogares con adultos mayores por departamento, área, sexo o edad, y siempre antes de graficar o mapear si no existe la base procesada. Versión de la tarea 4.
argument-hint: [año]
---

# Limpiar la ENAHO · versión tarea_4

> **Cuál versión es esta.** El repo tiene dos juegos de skills con el mismo nombre: los de la sesión 16, en
> `.claude/skills/` de la raíz, y estos, en `tarea_4/.claude/skills/`. Claude Code carga los del directorio desde
> donde arranca, así que **para la tarea 4 se arranca `claude` dentro de `tarea_4/`**, que es también donde está
> `.mcp.json`.
>
> **En qué difieren.** Aquí la cifra oficial sale de la **base hogar ponderada con `factor07 × mieperho`**, que es
> la que publica el INEI y la que pide el issue. La base persona con `facpob07` (la que usan los gráficos y el mapa
> de la sesión 16) queda como cifra secundaria, solo para cortes por atributos de la persona (sexo, edad). Las dos
> son correctas y difieren en una décima: son bases distintas, no un error.

1. Si `datos/` no tiene `sumaria-2024.dta` y `enaho01-2024-200.dta`, pide al usuario bajar y descomprimir en
   `datos/` los zip del INEI (código 966 = ENAHO 2024):
   - `https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip`
   - `https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip`

   El módulo 34 trae **dos sumarias**. Se usa `sumaria-2024.dta`, **nunca `sumaria-2024-12g.dta`**: el script busca
   el nombre exacto y no elige por patrón ni por tamaño.

2. Desde `tarea_4/`, corre exactamente:

   ```bash
   uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio 2024
   ```

   Cambia `2024` solo si el usuario pidió otro año y `$0` es un **número de cuatro dígitos**. `$0` trae el texto
   libre del pedido: nunca lo pases tal cual.

3. **Si el script termina con error, detente.** Reporta las líneas `[FALLA]` de `salidas/validacion.txt` y el
   mensaje de error. No ajustes cifras ni sigas con gráficos o mapas: el script ya borró las bases para que nadie
   las use.

4. Responde con las cifras de `salidas/validacion.txt` y `salidas/indicadores.csv`, sin recalcularlas. Si hace falta
   una cifra que no está ahí, calcúlala con pandas desde las bases y **ponderada**:
   - corte de hogar (área, departamento, tipo de hogar, gasto): `salidas/hogares_2024.parquet`, peso `peso_personas`;
   - atributo de la persona (sexo, edad): `salidas/personas_2024.parquet`, peso `facpob07`, y dilo.

   Un porcentaje es `100 * peso[condición].sum() / peso.sum()`; nunca `condición.mean()` ni contar filas.

5. Antes de usar una variable que no está en las bases, lee `reference.md`.

## Lo que el script decide y no se discute

| Paso | Decisión |
|---|---|
| Leer | `read_stata(convert_categoricals=False)`; llaves `conglome`, `vivienda`, `hogar`, `codperso` como texto |
| Normalizar | columnas a minúscula y sin tildes; `aÑo` pasa a `anio` |
| Filtrar | residentes habituales: `((p204 == 1) & (p205 == 2)) \| ((p204 == 2) & (p206 == 1))` |
| Unir | `personas.merge(hogares, on=["conglome", "vivienda", "hogar"], validate="m:1")` |
| Construir | `departamento = ubigeo[:2]` · `urbano = estrato <= 5` · `pobre = pobreza <= 2` · adulto mayor = `p208a >= 65` |
| Tipo de hogar | según sus residentes: sin adultos mayores, con adultos mayores y menores de 65, solo adultos mayores |
| Gasto | 8 grupos del do-file oficial del INEI (`ConstVarGasto`); alimentos / total = participación de los alimentos |
| Ponderar | oficial: `factor07 × mieperho` (base hogar) · secundaria: `facpob07` (base persona) |
| Guardar | `salidas/hogares_2024.parquet`, `salidas/personas_2024.parquet`, `salidas/indicadores.csv`, `salidas/validacion.txt` |

## Validaciones

**Esenciales** (si una falla, el script termina con código 2 y no deja bases):

| Comprobación | Referencia |
|---|---|
| Pobreza monetaria nacional, base hogar | 27.6 % ± 0.1 pp |
| Pobreza urbana / rural, base hogar | 24.8 % / 39.3 % ± 0.1 pp |
| Residentes habituales | 108,664 |
| Unidades territoriales | 25 códigos, del 01 al 25 (Lima 15 y Callao 07 separados) |
| Llaves | texto de largo fijo (sin perder ceros) y únicas en hogares y en personas |
| Unión | no pierde ni duplica residentes; todo hogar tiene residentes |
| Factores de expansión | `factor07` y `facpob07` positivos y sin vacíos |
| Gasto | los 8 grupos del INEI suman `gashog2d` en todos los hogares |

**Informativas**: pobreza extrema contra el 5.5 % del INEI, población expandida con cada factor, la pobreza que se
obtendría sin ponderar y las variables del do-file que no trae la sumaria del año.

La cifra secundaria con `facpob07` aparece en `validacion.txt` en su propio bloque, rotulada como secundaria. No se
valida contra el 27.6 %: es otra base.
