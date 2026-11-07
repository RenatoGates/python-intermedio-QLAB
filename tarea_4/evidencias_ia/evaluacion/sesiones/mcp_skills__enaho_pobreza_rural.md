# Evaluación · enaho_pobreza_rural · modo mcp_skills

Sesión nueva de `claude -p --model haiku` en la copia aislada de tarea_4/, con las opciones del modo `mcp_skills` (ver evaluacion/comparacion.md). Respuesta esperada: 39.3028 ± 0.1.

## Pedido

```text
Responde con un solo número en «valor», en la unidad que pide la pregunta. Si no puedes saberlo con certeza, pon valor null: no estimes. En «fuente» di de dónde sale la cifra; si combinas varias fuentes, nómbralas todas.

Según la ENAHO 2024 del INEI, ¿qué porcentaje de la población del área rural del Perú estaba en situación de pobreza monetaria en 2024, en %?
```

**Modelo:** claude-haiku-5-5  
**Directorio:** `<copia>/tarea_4`  
**Servidores MCP:** bcrp (connected), fetch (connected)  
**Herramientas:** Bash, Glob, Read, Skill, StructuredOutput, Write, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__graficar_series, mcp__bcrp__resumen, mcp__bcrp__serie, mcp__fetch__fetch

### Claude

Voy a buscar la cifra oficial del INEI para 2024.

### → Llama a `mcp__fetch__fetch`

```json
{
 "url": "https://www.gob.pe/institucion/inei/noticias",
 "max_length": 4000
}
```

#### ← Resultado (error)

```text
Claude requested permissions to use mcp__fetch__fetch, but you haven't granted it yet.
```

### → Llama a `mcp__fetch__fetch`

```json
{
 "url": "https://www.inei.gob.pe/prensa/noticias/",
 "max_length": 4000
}
```

#### ← Resultado (error)

```text
Claude requested permissions to use mcp__fetch__fetch, but you haven't granted it yet.
```

### Claude

La consulta a INEI no se pudo ejecutar, así que pruebo con las series del BCRP.

### → Llama a `mcp__bcrp__buscar_series`

```json
{
 "texto": "pobreza monetaria rural",
 "limite": 10
}
```

#### ← Resultado

```text
{"result":[]}
```

### → Llama a `mcp__bcrp__buscar_series`

```json
{
 "texto": "pobreza monetaria",
 "frecuencia": "Anual",
 "limite": 10
}
```

#### ← Resultado

```text
{"result":[]}
```

### Claude

El BCRP no tiene esa serie. Reviso si hay datos ENAHO locales en el proyecto.

### → Llama a `Glob`

```json
{
 "pattern": "**/*",
 "path": "<copia>/tarea_4"
}
```

#### ← Resultado

```text
.venv\Lib\site-packages\jsonschema_specifications\_core.py
.venv\Lib\site-packages\jsonschema_specifications\__init__.py
.venv\Lib\site-packages\multipart\__init__.py
.venv\Lib\site-packages\six.py
.venv\Lib\site-packages\typing_extensions.py
.venv\Lib\site-packages\multipart\decoders.py
.venv\Lib\site-packages\multipart\exceptions.py
.venv\Lib\site-packages\six-1.17.0.dist-info\LICENSE
.venv\Lib\site-packages\six-1.17.0.dist-info\METADATA
.venv\Lib\site-packages\typing_inspection\__init__.py
.venv\Lib\site-packages\typing_extensions-4.16.0.dist-info\licenses\LICENSE
.venv\Lib\site-packages\multipart\multipart.py
.venv\Lib\site-packages\typing_inspection\introspection.py
.venv\Lib\site-packages\jsonschema_specifications\schemas\draft201909\metaschema.json
.venv\Lib\site-packages\typing_extensions-4.16.0.dist-info\WHEEL
.venv\Lib\site-packages\typing_inspection\py.typed
.venv\Lib\site-packages\six-1.17.0.dist-info\WHEEL
.venv\Lib\site-packages\typing_extensions-4.16.0.dist-info\METADATA
.venv\Lib\site-packages\typing_inspection\typing_objects.py
.venv\Lib\site-packages\mdurl\__init__.py
.venv\Lib\site-packages\six-1.17.0.dist-info\top_level.txt
.venv\Lib\site-packages\jsonschema_specifications\schemas\draft201909\vocabularies\applicator
.venv\Lib\site-packages\python_multipart\__init__.py
.venv\Lib\site-packages\h11\__init__.py
.venv\Lib\site-packages\typing_inspection\typing_objects.pyi
.venv\Lib\site-packages\mdurl\_decode.py
.venv\Lib\site-packages\h11\_abnf.py
.venv\Lib\site-packages\jsonschema_specifications\schemas\draft201909\vocabularies\content
.venv\Lib\site-packages\python_multipart\decoders.py
.venv\Lib\site-packages\mdurl\_encode.py
.venv\Lib\site-packages\python_multipart\exceptions.py
.venv\Lib\site-packages\typing_inspection-0.4.4.dist-info\METADATA
.venv\Lib\site-packages\h11\_connection.py
.venv\Lib\site-packages\jsonschema_specifications\schemas\draft201909\vocabularies\core
.venv\Lib\site-packages\typing_inspection-0.4.4.dist-info\WHEEL
.venv\Lib\site-packages\h11\_events.py
.venv\Lib\site-packages\jsonschema_specifications\schemas\draft201909\vocabularies\format
.venv\Lib\site-packages\mdurl\_format.py
.venv\Lib\site-packages\python_multipart\multipart.py
.venv\Lib\site-packages\python_multipart\py.typed
.venv\Lib\site-packages\jsonschema_specifications\schemas\draft201909\vocabularies\meta-data
.venv\Lib\site-packages\typing_inspection-0.4.4.dist-info\licenses\LICENSE
.venv\Lib\site-packages\h11\_headers.py
.venv\Lib\site-packages\json
… (recortado)
```

### → Llama a `Glob`

```json
{
 "pattern": "**/*enaho*",
 "path": "<copia>/tarea_4"
}
```

#### ← Resultado

```text
datos\966-Modulo02\966-Modulo02\enaho01-2024-200.dta
```

### Claude

Hay datos de la ENAHO en `datos\`. Busco el módulo de sumaria (34), que es el que tiene la pobreza monetaria.

### → Llama a `Glob`

```json
{
 "pattern": "**/*{34,Sumaria,sumaria,Modulo34,modulo34}*",
 "path": "<copia>/tarea_4\\datos"
}
```

#### ← Resultado

```text
datos\966-Modulo34\966-Modulo34\sumaria-2024.dta
datos\966-Modulo34\966-Modulo34\sumaria-2024-12g.dta
```

### Claude

Calculo la tasa rural directamente desde la sumaria 2024 con los pesos oficiales (factor07 × mieperho).

### → Llama a `Bash`

```json
{
 "command": "python -c \"\nimport pandas as pd\ndf = pd.read_stata('datos/966-Modulo34/966-Modulo34/sumaria-2024.dta', convert_categoricals=False)\nprint(df.shape)\nprint([c for c in df.columns if c.lower() in ('pobreza','area','estrato','factor07','mieperho','dominio','ubigeo','a节')])\nprint(df['pobreza'].value_counts(dropna=False).sort_index())\nprint(df['area'].value_counts(dropna=False).sort_index())\n\" 2>&1",
 "description": "Inspect sumaria 2024 columns and category counts"
}
```

#### ← Resultado (error)

```text
Exit code 1
Traceback (most recent call last):
  File "~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.venv\Lib\site-packages\pandas\core\indexes\base.py", line 3816, in get_loc
    return self._engine.get_loc(casted_key)
           ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
  File "pandas/_libs/index.pyx", line 172, in pandas._libs.index.IndexEngine.get_loc
  File "pandas/_libs/index.pyx", line 201, in pandas._libs.index.IndexEngine.get_loc
  File "pandas/_libs/hashtable_class_helper.pxi", line 7726, in pandas._libs.hashtable.PyObjectHashTable.get_item
  File "pandas/_libs/hashtable_class_helper.pxi", line 7734, in pandas._libs.hashtable.PyObjectHashTable.get_item
KeyError: 'area'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "<string>", line 7, in <module>
    print(df['area'].value_counts(dropna=False).sort_index())
          ~~^^^^^^^^
  File "~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.venv\Lib\site-packages\pandas\core\frame.py", line 4330, in __getitem__
    indexer = self.columns.get_loc(key)
  File "~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.venv\Lib\site-packages\pandas\core\indexes\base.py", line 3823, in get_loc
    raise KeyError(key) from err
KeyError: 'area'
(33691, 163)
['ubigeo', 'dominio', 'estrato', 'mieperho', 'pobreza', 'factor07']
pobreza
1     1588
2     5224
3    26879
Name: count, dtype: int64
```

### Claude

La columna de área no se llama `area`. Reviso `estrato` y `dominio` para identificar lo rural.

### → Llama a `Bash`

```json
{
 "command": "python -c \"\nimport pandas as pd\ndf = pd.read_stata('datos/966-Modulo34/966-Modulo34/sumaria-2024.dta', convert_categoricals=False)\nprint(df['estrato'].value_counts().sort_index())\nprint(df['dominio'].value_counts().sort_index())\nprint(df[['factor07','mieperho']].describe())\n\" 2>&1",
 "description": "Check estrato and dominio codes for rural area"
}
```

#### ← Resultado

```text
estrato
1    5963
2    6349
3    2738
4    2584
5    4397
6    2039
7    6797
8    2824
Name: count, dtype: int64
dominio
1    4751
2    3287
3    2283
4    2015
5    5531
6    4523
7    7211
8    4090
Name: count, dtype: int64
           factor07      mieperho
count  33691.000000  33691.000000
mean     307.524597      3.260277
std      314.511841      1.762953
min        1.116235      1.000000
25%      120.713737      2.000000
50%      230.468079      3.000000
75%      352.102783      4.000000
max     1996.372314     17.000000
Shell cwd was reset to <copia>/tarea_4
```

### Claude

Según la codificación estándar de ENAHO, `estrato` 6–8 es rural. Calculo la tasa de pobreza monetaria ponderada por personas y verifico con la cifra nacional.

### → Llama a `Bash`

```json
{
 "command": "python -c \"\nimport pandas as pd\ndf = pd.read_stata('datos/966-Modulo34/966-Modulo34/sumaria-2024.dta', convert_categoricals=False)\ndf['w'] = df['factor07']*df['mieperho']\ndf['pobre'] = df['pobreza'].isin([1,2]).astype(int)\ndf['rural'] = (df['estrato']>=6).astype(int)\ndef tasa(d): return 100*(d['w']*d['pobre']).sum()/d['w'].sum()\nprint('Nacional personas:', round(tasa(df),2))\nfor r,g in df.groupby('rural'): print('rural' if r else 'urbano', round(tasa(g),2), 'hogares', len(g))\ng=df.groupby('dominio'); print({k:round(tasa(v),2) for k,v in g})\n\" 2>&1",
 "description": "Compute weighted monetary poverty rate, rural vs urban"
}
```

#### ← Resultado

```text
Nacional personas: 27.58
urbano 24.81 hogares 22031
rural 39.3 hogares 11660
{1: np.float64(24.28), 2: np.float64(14.01), 3: np.float64(20.15), 4: np.float64(45.7), 5: np.float64(30.1), 6: np.float64(25.6), 7: np.float64(30.02), 8: np.float64(28.21)}
Shell cwd was reset to <copia>/tarea_4
```

### → Llama a `StructuredOutput`

```json
{
 "valor": 39.3,
 "unidad": "%",
 "fuente": "Cálculo propio sobre la ENAHO 2024 (INEI), módulo 34 sumaria-2024.dta (datos\\966-Modulo34\\966-Modulo34\\sumaria-2024.dta). Pobreza monetaria = pobreza ∈ {1,2}; área rural = estrato 6–8; ponderado por personas con factor07 × mieperho. Control: la tasa nacional resultante es 27.58%, consistente con la cifra oficial del INEI (27.6%). No pude contrastar el dato rural contra la publicación del INEI porque el acceso web fue denegado, y el BCRP no tiene esa serie."
}
```

#### ← Resultado

```text
Structured output provided successfully
```

## Resultado

- Herramientas, en orden: mcp__fetch__fetch, mcp__fetch__fetch, mcp__bcrp__buscar_series, mcp__bcrp__buscar_series, Glob, Glob, Glob, Bash, Bash, Bash, StructuredOutput
- Turnos: 12
- Segundos: 34.8
- Costo informado por Claude Code: US$ 0.0076
- ¿Terminó con error?: False
