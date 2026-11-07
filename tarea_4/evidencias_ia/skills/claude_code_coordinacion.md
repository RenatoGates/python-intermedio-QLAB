# Skills de la ENAHO en Claude Code · caso «coordinacion»

Sesión nueva de `claude -p --model sonnet` arrancada en `tarea_4/`, sin servidores MCP y con las herramientas Skill, Bash, Read y Glob. Bases procesadas en `salidas/` al empezar: ninguna. Generado por `probar_skills.py`.

## Pedido

```text
Haz un mapa de la pobreza monetaria por departamento con ENAHO 2024.
```

**Modelo:** claude-sonnet-5-5  
**Directorio:** `~\Documentos\GitHub\python-intermedio-QLAB\tarea_4`  
**Servidores MCP:** ninguno  
**Herramientas:** Bash, Glob, Read, Skill

### → Llama a `Skill`

```json
{
 "skill": "mapeando-enaho"
}
```

#### ← Resultado

```text
Launching skill: mapeando-enaho
```

#### ← Contenido que Claude Code inyecta (p. ej., el SKILL.md al cargar una skill)

```text
Base directory for this skill: ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\mapeando-enaho

# Mapear la ENAHO · versión tarea_4

> **Cuál versión es esta.** Hay otra `mapeando-enaho` en la raíz del repo (sesión 16) que pondera con `facpob07`.
> Esta pondera con **`factor07 × mieperho`** (base hogar), que es la base con la que se hizo la tabla de referencia
> de la sesión 16 y la que publica el INEI. Para usar esta versión se arranca `claude` dentro de `tarea_4/`.

1. **Si no existe `salidas/hogares_2024.parquet`, usa primero la skill `limpiando-enaho`** y espera a que termine
   sin error. Sin base validada no hay mapa. El script también lo detecta: termina con código 3 y dice qué correr.

2. Elige el indicador. **Solo estos valores exactos**; `$0` trae texto libre, nunca lo pases tal cual al script.

   | Si piden… | `--indicador` |
   |---|---|
   | po
… (recortado)
```

### → Llama a `Bash`

```json
{
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && ls salidas; uv run ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza --anio 2024"
}
```

#### ← Resultado (error)

```text
Exit code 3
indicadores.csv
validacion.txt
No existe ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\salidas\hogares_2024.parquet. Usa primero la skill limpiando-enaho: uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024
```

### Claude

Falta la base procesada; corro primero la limpieza, como indica la skill.

### → Llama a `Skill`

```json
{
 "skill": "limpiando-enaho"
}
```

#### ← Resultado

```text
Launching skill: limpiando-enaho
```

#### ← Contenido que Claude Code inyecta (p. ej., el SKILL.md al cargar una skill)

```text
Base directory for this skill: ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\limpiando-enaho

# Limpiar la ENAHO · versión tarea_4

> **Cuál versión es esta.** El repo tiene dos juegos de skills con el mismo nombre: los de la sesión 16, en
> `.claude/skills/` de la raíz, y estos, en `tarea_4/.claude/skills/`. Claude Code carga los del directorio desde
> donde arranca, así que **para la tarea 4 se arranca `claude` dentro de `tarea_4/`**, que es también donde está
> `.mcp.json`.
>
> **En qué difieren.** Aquí la cifra oficial sale de la **base hogar ponderada con `factor07 × mieperho`**, que es
> la que publica el INEI y la que pide el issue. La base persona con `facpob07` (la que usan los gráficos y el mapa
> de la sesión 16) queda como cifra secundaria, solo para cortes por atributos de la persona (sexo, edad). Las dos
> son correctas y difieren en una déc
… (recortado)
```

### → Llama a `Bash`

```json
{
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && ls datos; uv run ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024"
}
```

#### ← Resultado

```text
966-Modulo02
966-Modulo34
catalogo_bcrp.csv
peru_departamental_simple.geojson
ENAHO 2024 · validación de la limpieza (versión tarea_4)
Generado por .claude/skills/limpiando-enaho/scripts/limpiar.py. Ninguna cifra está escrita a mano.

Archivos
  sumaria : datos/966-Modulo34/966-Modulo34/sumaria-2024.dta (33,691 hogares)
  miembros: datos/966-Modulo02/966-Modulo02/enaho01-2024-200.dta (117,721 filas)
  otras sumarias en datos/, que no se usan: sumaria-2024-12g.dta

CIFRA OFICIAL · base hogar (sumaria), ponderada con factor07 × mieperho
  [OK]    Pobreza monetaria nacional    27.58 %   referencia  27.6 %   diferencia -0.02 pp (tolerancia ±0.1)
  [OK]    Pobreza urbana                24.81 %   referencia  24.8 %   diferencia +0.01 pp (tolerancia ±0.1)
  [OK]    Pobreza rural                 39.30 %   referencia  39.3 %   diferencia +0.00 pp (tolerancia ±0.1)
  [OK]    Residentes habituales       108,664     referencia 108,664
  [OK]    Unidades territoriales           25     referencia 25 (códigos 01 a 25; Lima 15 y Callao 07 separados)

Integridad de la limpieza (esenciales)
  [OK]    la llave conglome es texto de largo fijo (6 caracteres): conserva los ceros iniciales
  [OK]    la llave vivienda es texto de largo fijo (3 caracteres): conserva los ceros iniciales
  [OK]    la llave hogar es texto de largo fijo (2 caracteres): conserva los ceros iniciales
  [OK]    llaves de hogar únicas en la sumaria
  [OK]    llaves de persona únicas en el módulo 02
  [OK]    la unión m:1 personas-hogares conserva las 108,664 filas, sin perder ni duplicar
  [OK]    todos los hogares de la sumaria tienen residentes en el módulo 02 (0 sin ellos)
  [OK]    factor07 positivo y sin vacíos en todos los hogares
  [OK]    facpob07 positivo y sin vacíos en todos los residentes
  [OK]    los 8 grupos de gasto del INEI suman gashog2d en todos los hogares (diferencia máxima 0.014 soles)

Cifra secundaria · base persona (módulo 02 unido a la sumaria), ponderada con facpob07
  No es la cifra contra la que se valida: pondera personas, no hogares por su tamaño, y por eso
  difiere en una décima. Se usa solo para cortes por atributos de la persona (sexo, edad).
  Pobreza nacional 27.53 % · urbana 24.7 % · rural 39.4 % · extrema 5.50 %

Informativas (no detienen el proceso)
  [OK]    población expandida: 34,482,700 con factor07 × mieperho y 34,147,768 con facpob07 (difieren menos de 1 %)
  [OK]    pobreza extrema base hogar 5.50 % (INEI 5.5 %)
  Sin pondera
… (recortado)
```

### Claude

Limpieza validada (15/15). Ahora el mapa.

### → Llama a `Bash`

```json
{
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && uv run ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza --anio 2024"
}
```

#### ← Resultado

```text
Pobreza monetaria por departamento, 2024 (base hogar, factor07 × mieperho)
  25 unidades territoriales unidas por código, ninguna sin dato
  más alto : Cajamarca 45.0 %, Loreto 43.0 %, Puno 39.9 %
  más bajo : Ica 6.0 %, Moquegua 11.0 %, Madre de Dios 11.1 %
  contra la referencia de la sesión 16: diferencia máxima 0.049 puntos, mediana 0.030 (tolerancia 0.1)

Guardado en mapas/pobreza_departamento_2024.png (200 dpi) y las cifras en mapas/pobreza_departamento_2024.csv
```

### Claude

Hice el mapa de pobreza monetaria por departamento con ENAHO 2024. Está guardado en `mapas/pobreza_departamento_2024.png` (200 dpi), con las cifras en `mapas/pobreza_departamento_2024.csv`.

No existía la base procesada, así que corrí primero la limpieza. Pasó las 15 comprobaciones esenciales. La pobreza nacional salió 27.58 %, contra 27.6 % de referencia.

- **Más alta:** Cajamarca 45.0 %, Loreto 43.0 % y Puno 39.9 %.
- **Más baja:** Ica 6.0 %, Moquegua 11.0 % y Madre de Dios 11.1 %.
- **Cobertura:** las 25 unidades territoriales quedaron unidas por código y todas tienen dato, con Lima y Callao separados.
- **Contra la sesión 16:** la diferencia máxima es 0.049 puntos y la mediana 0.030, dentro de la tolerancia de 0.1.

Las cifras usan la base hogar ponderada con `factor07 × mieperho`.

No abrí la imagen, solo revisé lo que imprimió el script. El script no avisó de departamentos con menos de 100 hogares en la muestra.

## Resultado

- Herramientas, en orden: Skill(mapeando-enaho), Bash, Skill(limpiando-enaho), Bash, Bash
- Turnos: 8
- Segundos: 17.6
- Costo informado por Claude Code: US$ 0.1014
- ¿Terminó con error?: False
