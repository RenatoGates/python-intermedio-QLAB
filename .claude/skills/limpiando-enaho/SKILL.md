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
   uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio $0
   ```

   Si no se pasó año, usa 2024.

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

| Cifra | Valor |
|---|---|
| Pobreza monetaria | 27.6 % (27.58 % con la sumaria, 27.53 % con personas) |
| Pobreza extrema | 5.5 % |
| Hogares en la sumaria | 33,691 |
| Residentes habituales | 108,664 de 117,721 filas |
| Urbano / rural | 24.8 % / 39.3 % |
