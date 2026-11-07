# Evaluación · enaho_pobreza_solo_am · modo mcp_skills

Sesión nueva de `claude -p --model haiku` en la copia aislada de tarea_4/, con las opciones del modo `mcp_skills` (ver evaluacion/comparacion.md). Respuesta esperada: 20.2572 ± 0.1.

## Pedido

```text
Responde con un solo número en «valor», en la unidad que pide la pregunta. Si no puedes saberlo con certeza, pon valor null: no estimes. En «fuente» di de dónde sale la cifra; si combinas varias fuentes, nómbralas todas.

Según la ENAHO 2024 del INEI, ¿qué porcentaje de las personas que viven en hogares donde todos los residentes habituales tienen 65 años o más estaba en pobreza monetaria? Pondera con factor07 × mieperho; en %.
```

**Modelo:** claude-haiku-5-5  
**Directorio:** `<copia>/tarea_4`  
**Servidores MCP:** bcrp (connected), fetch (connected)  
**Herramientas:** Bash, Glob, Read, Skill, StructuredOutput, Write, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__graficar_series, mcp__bcrp__resumen, mcp__bcrp__serie, mcp__fetch__fetch

### Claude

Voy a revisar qué datos hay en el directorio de trabajo antes de calcular.

### → Llama a `Bash`

```json
{
 "command": "cd \"<copia>/tarea_4\" && ls -la && find . -maxdepth 3 -type f | head -100",
 "description": "List working directory contents"
}
```

#### ← Resultado

```text
total 615
drwxr-xr-x 1 usuario 197609      0 Nov  6 23:10 .
drwxr-xr-x 1 usuario 197609      0 Nov  6 23:10 ..
drwxr-xr-x 1 usuario 197609      0 Nov  6 21:46 .claude
-rw-r--r-- 1 usuario 197609    321 Nov  6 21:46 .gitignore
-rw-r--r-- 1 usuario 197609    308 Nov  6 21:47 .mcp.json
drwxr-xr-x 1 usuario 197609      0 Nov  6 23:10 .venv
-rw-r--r-- 1 usuario 197609  18698 Nov  6 23:06 README.md
drwxr-xr-x 1 usuario 197609      0 Nov  6 21:49 datos
drwxr-xr-x 1 usuario 197609      0 Nov  6 23:10 evaluacion
drwxr-xr-x 1 usuario 197609      0 Nov  6 22:56 figuras
drwxr-xr-x 1 usuario 197609      0 Nov  6 23:02 informes
drwxr-xr-x 1 usuario 197609      0 Nov  6 22:28 mapas
drwxr-xr-x 1 usuario 197609      0 Nov  6 22:53 mcp
-rw-r--r-- 1 usuario 197609    415 Nov  6 22:22 pyproject.toml
drwxr-xr-x 1 usuario 197609      0 Nov  6 22:56 salidas
-rw-r--r-- 1 usuario 197609 570962 Nov  6 22:22 uv.lock
./.gitignore
./.mcp.json
./.venv/.gitignore
./.venv/.lock
./.venv/CACHEDIR.TAG
./.venv/pyvenv.cfg
./.venv/Scripts/activate
./.venv/Scripts/activate.bat
./.venv/Scripts/activate.csh
./.venv/Scripts/activate.fish
./.venv/Scripts/activate.nu
./.venv/Scripts/activate.ps1
./.venv/Scripts/activate.xsh
./.venv/Scripts/activate_this.py
./.venv/Scripts/cffi-gen-src.exe
./.venv/Scripts/cyclopts.exe
./.venv/Scripts/deactivate.bat
./.venv/Scripts/dotenv.exe
./.venv/Scripts/email_validator.exe
./.venv/Scripts/f2py.exe
./.venv/Scripts/fastmcp.exe
./.venv/Scripts/fonttools.exe
./.venv/Scripts/httpx.exe
./.venv/Scripts/httpx2.exe
./.venv/Scripts/idna.exe
./.venv/Scripts/jsonschema.exe
./.venv/Scripts/markdown-it.exe
./.venv/Scripts/mcp.exe
./.venv/Scripts/numpy-config.exe
./.venv/Scripts/py.test.exe
./.venv/Scripts/pydoc.bat
./.venv/Scripts/pyftmerge.exe
./.venv/Scripts/pyftsubset.exe
./.venv/Scripts/pygmentize.exe
./.venv/Scripts/pyproj.exe
./.venv/Scripts/pytest.exe
./.venv/Scripts/python.exe
./.venv/Scripts/pythonw.exe
./.venv/Scripts/pywin32_postinstall.exe
./.venv/Scripts/pywin32_postinstall.py
./.venv/Scripts/pywin32_testall.exe
./.venv/Scripts/pywin32_testall.py
./.venv/Scripts/ttx.exe
./.venv/Scripts/uvicorn.exe
./.venv/Scripts/watchfiles.exe
./.venv/Scripts/websockets.exe
./datos/catalogo_bcrp.csv
./datos/peru_departamental_simple.geojson
./evaluacion/comparar.py
./evaluacion/evaluar.py
./figuras/alimentos_tipo_hogar_2024.csv
./figuras/alimentos_tipo_hogar_2024.png
./figuras/alimentos_tipo_hogar_area_2024.csv
./figuras/alimentos_tipo_hogar_area_2024.png
./figuras/bcrp_inflacion_tasa_2021_2026.csv
./figuras/bc
… (recortado)
```

### → Llama a `Bash`

```json
{
 "command": "cd \"<copia>/tarea_4\" && cat figuras/pobreza_tipo_hogar_2024.csv && echo ---- && cat salidas/validacion.txt && echo ---- && cat salidas/indicadores.csv | head -50 && echo ---- && grep -n -i \"65\\|adulto\\|tipo_hogar\\|solo_mayor\" README.md | head -40",
 "description": "Show existing poverty by household type outputs and README notes"
}
```

#### ← Resultado

```text
tipo,valor,n_muestral
Sin adultos mayores,27.8543,23292
Con adultos mayores y menores de 65,28.3717,5930
Solo adultos mayores,20.2572,4469
----
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
 
… (recortado)
```

### Claude

Ya hay una cifra calculada para «Solo adultos mayores» (20.2572 %). Antes de usarla, verifico cómo se definió ese corte y la recalculo desde la base de personas.

### → Llama a `Bash`

```json
{
 "command": "cd \"<copia>/tarea_4\" && ls .claude/skills/limpiando-enaho/scripts/ 2>/dev/null; grep -rn \"Solo adultos\\|tipo_hogar_am\\|65\" .claude/skills/limpiando-enaho/scripts/*.py 2>/dev/null | head -30; ./.venv/Scripts/python.exe -I -c \"\nimport pandas as pd\np=pd.read_parquet('salidas/personas_2024.parquet'); h=pd.read_parquet('salidas/hogares_2024.parquet')\nprint(p.columns.tolist()); print(h.columns.tolist())\n\"",
 "description": "Inspect cleaning script definition and parquet columns"
}
```

#### ← Resultado

```text
limpiar.py
28:EDAD_ADULTO_MAYOR = 65
40:TIPOS_HOGAR = ["Sin adultos mayores", "Con adultos mayores y menores de 65", "Solo adultos mayores"]
179:    comp["tipo_hogar_am"] = np.select(
204:                  "departamento", "estrato", "urbano", "dominio", "tipo_hogar_am", "n_am", "part_alimentos"]
299:                    "jefe_am", "tipo_hogar_am", "am_vive_solo", "tamano_hogar", *GRUPOS_GASTO, "g0_total", "gashog2d",
321:    # estructura del hogar según la presencia de adultos mayores (65+)
322:    for corte, grupos in (("tipo_hogar_am", hogares.groupby("tipo_hogar_am")),
323:                          ("tipo_hogar_am × area", hogares.groupby(["tipo_hogar_am", "urbano"]))):
333:            if corte == "tipo_hogar_am":
339:    for (tipo, tam), g in hogares.groupby(["tipo_hogar_am", "tamano_hogar"]):
340:        agregar("pobreza", "tipo_hogar_am × tamano", f"{tipo} · {tam}", pct(g.pobre, g.peso_personas),
342:        agregar("part_alimentos", "tipo_hogar_am × tamano", f"{tipo} · {tam}", media(g.part_alimentos, g.peso_personas),
357:    for am, nombre in ((True, "65 años o más"), (False, "Menos de 65 años")):
['conglome', 'vivienda', 'hogar', 'codperso', 'p203', 'p207', 'p208a', 'adulto_mayor', 'facpob07', 'pobreza', 'pobre', 'pobre_extremo', 'mieperho', 'factor07', 'peso_personas', 'ubigeo', 'departamento', 'estrato', 'urbano', 'dominio', 'tipo_hogar_am', 'n_am', 'part_alimentos']
['conglome', 'vivienda', 'hogar', 'ubigeo', 'departamento', 'estrato', 'urbano', 'dominio', 'mieperho', 'factor07', 'peso_personas', 'pobreza', 'pobre', 'pobre_extremo', 'n_residentes', 'n_am', 'n_menores_18', 'jefe_am', 'tipo_hogar_am', 'am_vive_solo', 'tamano_hogar', 'g1_alimentos', 'g2_vestido', 'g3_vivienda', 'g4_muebles', 'g5_salud', 'g6_transporte', 'g7_esparcimiento', 'g8_otros', 'g0_total', 'gashog2d', 'part_alimentos', 'gasto_pc_mensual']
Shell cwd was reset to <copia>/tarea_4
```

### → Llama a `Bash`

```json
{
 "command": "cd \"<copia>/tarea_4\" && sed -n 170,190p .claude/skills/limpiando-enaho/scripts/limpiar.py; ./.venv/Scripts/python.exe -I -c \"\nimport pandas as pd\nh=pd.read_parquet('salidas/hogares_2024.parquet')\nprint('hogares',len(h), 'residentes', h.n_residentes.sum())\nw=h.factor07*h.mieperho\ns=h[h.n_am==h.n_residentes]\nprint('n hogares solo AM (n_am==n_residentes):',len(s), 'tipo:', s.tipo_hogar_am.value_counts().to_dict())\nprint('personas pond. solo AM:', (s.factor07*s.mieperho).sum())\nprint('pobreza pct personas (solo AM, n_am==n_res):', 100*(s.factor07*s.mieperho*s.pobre).sum()/(s.factor07*s.mieperho).sum())\nt=h[h.tipo_hogar_am=='Solo adultos mayores']\nprint('pobreza pct tipo=Solo AM:', 100*(t.factor07*t.mieperho*t.pobre).sum()/(t.factor07*t.mieperho).sum(), len(t))\nprint('pobre dtype/unique', h.pobre.unique()[:5])\n\"",
 "description": "Recompute poverty for households with only 65+ residents"
}
```

#### ← Resultado

```text
    # ------------------------------------------------------------- estructura del hogar según edad (residentes)
    comp = (personas.assign(menor_18=personas.p208a < 18)
            .groupby(LLAVES_HOGAR)
            .agg(n_residentes=("codperso", "size"), n_am=("adulto_mayor", "sum"), n_menores_18=("menor_18", "sum"))
            .reset_index())
    jefes = personas.loc[personas.p203 == 1, LLAVES_HOGAR + ["adulto_mayor"]].rename(columns={"adulto_mayor": "jefe_am"})
    comp = comp.merge(jefes, on=LLAVES_HOGAR, how="left", validate="1:1")
    comp["jefe_am"] = comp.jefe_am.fillna(False).astype(bool)
    comp["tipo_hogar_am"] = np.select(
        [comp.n_am == 0, comp.n_am < comp.n_residentes], TIPOS_HOGAR[:2], default=TIPOS_HOGAR[2])
    comp["am_vive_solo"] = (comp.n_residentes == 1) & (comp.n_am == 1)

    # ------------------------------------------------------------------------------------------ base hogar
    faltan_gasto = [v for cols in GRUPOS_GASTO.values() for v in cols.split() if v not in sumaria.columns]
    for g, cols in GRUPOS_GASTO.items():
        sumaria[g] = sumaria[[c for c in cols.split() if c in sumaria.columns]].fillna(0).sum(axis=1)
    sumaria["g0_total"] = sumaria[list(GRUPOS_GASTO)].sum(axis=1)
    dif_gasto = (sumaria.g0_total - sumaria.gashog2d).abs().max()

    hogares = sumaria.merge(comp, on=LLAVES_HOGAR, how="left", validate="1:1", indicator=True)
hogares 33691 residentes 108664
n hogares solo AM (n_am==n_residentes): 4469 tipo: {'Solo adultos mayores': 4469}
personas pond. solo AM: 1.7515352e+06
pobreza pct personas (solo AM, n_am==n_res): 20.257175
pobreza pct tipo=Solo AM: 20.257175 4469
pobre dtype/unique [False  True]
Shell cwd was reset to <copia>/tarea_4
```

### → Llama a `StructuredOutput`

```json
{
 "valor": 20.2572,
 "unidad": "%",
 "fuente": "INEI, ENAHO 2024 (módulo 34 sumaria-2024.dta y módulo 02 enaho01-2024-200.dta), procesado en salidas/hogares_2024.parquet y salidas/indicadores.csv (indicador pobreza, corte tipo_hogar_am = «Solo adultos mayores», n muestral 4,469 hogares). Recalculado directamente desde salidas/hogares_2024.parquet: pobreza ponderada por factor07 × mieperho entre hogares donde todos los residentes habituales tienen 65+ años. Cifra validada con 15/15 comprobaciones en salidas/validacion.txt."
}
```

#### ← Resultado

```text
Structured output provided successfully
```

## Resultado

- Herramientas, en orden: Bash, Bash, Bash, Bash, StructuredOutput
- Turnos: 6
- Segundos: 21.2
- Costo informado por Claude Code: US$ 0.0063
- ¿Terminó con error?: False
