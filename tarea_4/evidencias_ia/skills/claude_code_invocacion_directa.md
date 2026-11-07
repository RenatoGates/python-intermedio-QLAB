# Skills de la ENAHO en Claude Code · caso «invocacion_directa»

Sesión nueva de `claude -p --model sonnet` arrancada en `tarea_4/`, sin servidores MCP y con las herramientas Skill, Bash, Read y Glob. Bases procesadas en `salidas/` al empezar: hogares_2024.parquet, personas_2024.parquet. Generado por `probar_skills.py`.

## Pedido

```text
/limpiando-enaho 2024
```

**Modelo:** claude-sonnet-5-5  
**Directorio:** `~\Documentos\GitHub\python-intermedio-QLAB\tarea_4`  
**Servidores MCP:** ninguno  
**Herramientas:** Bash, Glob, Read, Skill

### → Llama a `Glob`

```json
{
 "pattern": "datos/*.dta"
}
```

#### ← Resultado

```text
No files found
```

### → Llama a `Bash`

```json
{
 "command": "ls -la datos 2>&1 | head; ls"
}
```

#### ← Resultado

```text
total 7008
drwxr-xr-x 1 Renat 197609       0 Nov  6 21:49 .
drwxr-xr-x 1 Renat 197609       0 Nov  6 21:47 ..
drwxr-xr-x 1 Renat 197609       0 Nov  6 21:46 966-Modulo02
drwxr-xr-x 1 Renat 197609       0 Nov  6 21:46 966-Modulo34
-rw-r--r-- 1 Renat 197609 7005225 Nov  6 21:49 catalogo_bcrp.csv
-rw-r--r-- 1 Renat 197609  157636 Nov  6 21:46 peru_departamental_simple.geojson
README.md
datos
evaluacion
evidencias_ia
figuras
informes
mapas
mcp
pyproject.toml
salidas
uv.lock
```

### → Llama a `Bash`

```json
{
 "command": "find datos/966-Modulo02 datos/966-Modulo34 -name \"*.dta\""
}
```

#### ← Resultado

```text
datos/966-Modulo02/966-Modulo02/enaho01-2024-200.dta
datos/966-Modulo34/966-Modulo34/sumaria-2024-12g.dta
datos/966-Modulo34/966-Modulo34/sumaria-2024.dta
```

### → Llama a `Bash`

```json
{
 "command": "grep -n \"datos\\|glob\\|rglob\" .claude/skills/limpiando-enaho/scripts/limpiar.py | head -30"
}
```

#### ← Resultado

```text
73:def descomprimir(datos: Path) -> None:
74:    for z in sorted(datos.glob("*.zip")):
75:        if not (datos / z.stem).exists():
77:                zf.extractall(datos / z.stem)
80:def buscar_dta(datos: Path, nombre: str) -> Path:
83:    todos = list(datos.rglob("*.dta"))
90:            f"No encontré {nombre} dentro de {datos}. Archivos parecidos: {parecidos or 'ninguno'}. "
91:            "No uso otro en su lugar. Bajen los zip del INEI (966-Modulo34.zip y 966-Modulo02.zip) a datos/.")
92:    raise FileNotFoundError(f"Hay {len(exactos)} copias de {nombre} en {datos}: {[str(p) for p in exactos]}. "
117:    ap.add_argument("--datos", default=None)
122:    datos = Path(args.datos) if args.datos else base_dir / "datos"
128:    if not datos.exists():
129:        print(f"Falta la carpeta {datos}.", file=sys.stderr)
140:    descomprimir(datos)
142:        ruta_s = buscar_dta(datos, f"sumaria-{args.anio}.dta")
143:        ruta_p = buscar_dta(datos, f"enaho01-{args.anio}-200.dta")
147:    otras_sumarias = sorted(p.name for p in datos.rglob("sumaria*.dta") if p != ruta_s)
264:        f"  otras sumarias en datos/, que no se usan: {', '.join(otras_sumarias) or 'ninguna'}",
```

### Claude

The script searches recursively and the exact files are present, so I'm running it.

### → Llama a `Bash`

```json
{
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && uv run ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024 2>&1 | tail -60; echo EXIT=${PIPESTATUS[0]}",
 "timeout": 400000
}
```

#### ← Resultado

```text
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
  Sin ponderar, la pobreza de la muestra de hogares sería 20.22 %: por eso toda cifra se po
… (recortado)
```

### Claude

La limpieza de la ENAHO 2024 terminó sin errores y pasó las 15 comprobaciones esenciales. El script usó `sumaria-2024.dta`, no la versión `-12g`. Las cifras salen de `salidas/validacion.txt`.

**Cifra oficial (base hogar, ponderada con `factor07 × mieperho`)**

| Indicador | Resultado | Referencia INEI | Diferencia |
|---|---|---|---|
| Pobreza nacional | 27.58 % | 27.6 % | −0.02 pp |
| Pobreza urbana | 24.81 % | 24.8 % | +0.01 pp |
| Pobreza rural | 39.30 % | 39.3 % | 0.00 pp |
| Pobreza extrema | 5.50 % | 5.5 % | — |

- **Residentes habituales:** 108,664, igual a la referencia.
- **Unidades territoriales:** 25. Lima (15) y Callao (07) quedan separados.
- **Integridad:**
  - Las llaves conservan los ceros iniciales y son únicas.
  - La unión personas–hogares no pierde ni duplica filas.
  - Todos los hogares tienen residentes.
  - Los factores de expansión son positivos y sin vacíos.
  - Los 8 grupos de gasto suman `gashog2d`, con una diferencia máxima de 0.014 soles.

**Cifra secundaria (base persona, `facpob07`)**
- Esta base sirve solo para cortes por sexo o edad. La pobreza nacional es 27.53 %, la urbana 24.7 %, la rural 39.4 % y la extrema 5.50 %.
- Difiere en una décima de la oficial porque es otra base, no por un error.

**Avisos que no detienen el proceso**
- Sin ponderar, la pobreza de la muestra sería 20.22 %, por eso toda cifra se pondera.
- La sumaria 2024 no trae `gru52hd2` del do-file del INEI, así que se toma como 0.
- La población expandida es 34,482,700 con `factor07 × mieperho` y 34,147,768 con `facpob07`, una diferencia menor al 1 %.

**Archivos guardados en `salidas/`:** `hogares_2024.parquet`, `personas_2024.parquet`, `indicadores.csv` (129 indicadores) y `validacion.txt`.

## Resultado

- Herramientas, en orden: Glob, Bash, Bash, Bash, Bash
- Turnos: 6
- Segundos: 16.4
- Costo informado por Claude Code: US$ 0.0791
- ¿Terminó con error?: False
