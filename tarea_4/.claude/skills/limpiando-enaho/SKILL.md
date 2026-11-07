---
name: limpiando-enaho
description: Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO del INEI y arma una base de personas con pobreza y factor de expansión. Úsala cuando pidan limpiar, unir o analizar la ENAHO, o calcular pobreza monetaria, pobreza extrema o número de personas por departamento, región, área urbana o rural, sexo o edad.
argument-hint: [año]
---

# Limpiar la ENAHO

1. Si no hay zip ni `.dta` en `datos/`, pide al usuario bajarlos del INEI antes de seguir.
   El código de la ENAHO 2024 es **966**:
   - `https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip`
   - `https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip`

2. Corre exactamente:

   ```bash
   uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio 2024
   ```

   Cambia `2024` solo si el usuario pidió otro año y `$0` es un **número de cuatro
   dígitos**. `$0` trae el texto libre del pedido, no un año: nunca lo pases tal cual.

3. Lee `salidas/validacion.txt`. **Si la pobreza difiere del INEI en más de 0.1 puntos, detente**
   y reporta la diferencia en vez de seguir con el análisis.

4. Responde con `salidas/personas_$0.parquet`. **Toda cifra va ponderada con `facpob07`**:
   nunca cuentes filas ni promedies la columna `pobreza`.

5. Antes de usar una variable que no está en la base, lee `reference.md`.

## Lo que el script decide y no se discute

| Paso | Decisión |
|---|---|
| Leer | `read_stata(convert_categoricals=False)`; llaves como texto |
| Normalizar | columnas a minúscula sin tildes; `aÑo` pasa a `anio` |
| Filtrar | residentes habituales: `(p204==1 & p205==2) | (p204==2 & p206==1)` |
| Unir | `personas.merge(sumaria, on=["conglome","vivienda","hogar"], validate="m:1")` |
| Construir | `departamento = ubigeo[:2]` · `urbano = estrato <= 5` · `pobre = pobreza <= 2` |
| Validar | llaves únicas · ninguna fila perdida · pobreza a menos de 0.1 puntos del INEI |
| Guardar | `salidas/personas_<año>.parquet` y `salidas/validacion.txt` |

## Cifras de control, ENAHO 2024

Hay dos bases y dan cifras que difieren por una décima. **Las dos son correctas**: la
sumaria pondera hogares por su tamaño y la base de personas pondera personas.

| Cifra | Sumaria (`factor07 × mieperho`) | Personas (`facpob07`) |
|---|---|---|
| Pobreza monetaria | 27.58 % | 27.53 % |
| Pobreza extrema | 5.50 % | 5.50 % |
| Urbano / rural | 24.8 % / 39.3 % | 24.7 % / 39.4 % |

La cifra que publica el INEI es **27.6 %**, la de la sumaria redondeada. El script
calcula las dos y valida ambas contra ella con una tolerancia de 0.1 puntos.

| Cifra | Valor |
|---|---|
| Hogares en la sumaria | 33,691 |
| Residentes habituales | 108,664 de 117,721 filas |
| Cusco | 18.5 % |
