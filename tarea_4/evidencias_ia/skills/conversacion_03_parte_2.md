# Conversación con Claude Code · Parte 2: Skills de la ENAHO

Exportada de la sesión `29e7d7fa-8938-4d4b-8486-6ce14556e6c6` con `evidencias_ia/exportar_conversacion.py`. Se muestran los mensajes del usuario, las respuestas de Claude, cada herramienta con sus argumentos y su resultado (recortados si son largos). Se omiten el razonamiento interno, las imágenes y los avisos del sistema; la carpeta personal aparece como «~».

## Usuario · 2026-11-07 03:17 UTC

Sí, sigue con la Parte 2. Verifiqué por mi cuenta que el blob de test_server.py en git coincide byte a byte con el del profesor, así que eso está cerrado.

Dos cosas antes de la Parte 3, para que no te agarren a mitad de camino.

1) Las skills de tarea_4/ no se van a activar si corro Claude Code desde la raíz del repo.
Claude Code carga las skills de .claude/skills/ del directorio desde donde arranca. Ahora hay dos juegos con el mismo nombre: el de la raíz (sesión 16) y el de tarea_4/. Desde la raíz se activan las viejas, no las de la tarea.
Para la Parte 3, la ejecución del agente tiene que hacerse arrancando Claude Code dentro de tarea_4/, que además es donde está .mcp.json. Documenta eso en el README, en el apartado de "ejemplo de una ejecución completa", con el comando exacto. Y asegúrate de que las dos versiones no se contradigan: si la de tarea_4 cambia la ponderación, deja claro en su SKILL.md cuál es cuál.

2) En la Parte 2, la trampa de los datos.
En datos/966-Modulo34/ hay dos sumarias. Usa sumaria-2024.dta, no sumaria-2024-12g.dta. Si tu script busca por patrón y elige la más grande, va a agarrar la equivocada y las cifras no van a cuadrar.
Validación esencial: pobreza nacional 27.6 % (±0.1 pp), urbana 24.8 %, rural 39.3 %, residentes habituales 108,664 y 25 unidades territoriales, todo con factor07 × mieperho. Si alguna falla, el script se detiene con error; no ajustes nada para que cuadre.

Lo del catálogo que dice Ene-2004 mientras la API trae datos desde setiembre de 2003 va a Limitaciones del informe, bien visto. Y sí, documenta lo de ReadMcpResourceTool en comparacion.md.

Avísame cuando validacion.txt esté en verde y seguimos con la Parte 3.

### Claude

Empiezo leyendo las tres skills tal como las copié de la raíz.

**→ Bash**

```json
{
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills && cat limpiando-enaho/SKILL.md && echo \"=========== REFERENCE ===========\" && cat limpiando-enaho/reference.md",
 "description": "Read limpiando-enaho SKILL.md and reference"
}
```

**→ Read**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\limpiando-enaho\\scripts\\limpiar.py"
}
```

<details><summary>← Resultado</summary>

```text
1	"""Pipeline de limpieza de la ENAHO: módulos 34 (sumaria) y 02 (miembros)."""
2	
3	import argparse
4	import re
5	import sys
6	import unicodedata
7	import zipfile
8	from pathlib import Path
9	
10	import pandas as pd
11	
12	LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]
13	LLAVES_PERSONA = LLAVES_HOGAR + ["codperso"]
14	POBREZA_OFICIAL = {2024: 27.6}
15	EXTREMA_OFICIAL = {2024: 5.5}
16	TOLERANCIA = 0.1
17	
18	
19	def raiz_repo() -> Path:
20	    return Path(__file__).resolve().parents[4]
21	
22	
23	def sin_tildes(texto: str) -> str:
24	    desc = unicodedata.normalize("NFD", texto)
25	    return "".join(c for c in desc if unicodedata.category(c) != "Mn")
26	
27	
28	def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
29	    nuevos = {}
30	    for col in df.columns:
31	        limpio = sin_tildes(str(col)).lower().strip()
32	        nuevos[col] = "anio" if limpio == "ano" else limpio
33	    return df.rename(columns=nuevos)
34	
35	
36	def descomprimir(datos: Path) -> None:
37	    for z in sorted(datos.glob("*.zip")):
38	        with zipfile.ZipFile(z) as zf:
39	            zf.extractall(datos / z.stem)
40	
41	
42	def buscar_dta(datos: Path, patron: str, preferido: str | None = None) -> Path:
43	    rx = re.compile(patron, re.IGNORECASE)
44	    candidatos = [p for p in datos.rglob("*.dta") if rx.search(p.name)]
45	    if not candidatos:
46	        raise FileNotFoundError(
47	            f"No encontré ningún .dta que coincida con '{patron}' dentro de {datos}. "
48	            "Baja los zip del INEI (966-Modulo34.zip y 966-Modulo02.zip) a esa carpeta."
49	        )
50	    if preferido:
51	        exactos = [p for p in candidatos if p.name.lower() == preferido.lower()]
52	        if exactos:
53	            return exactos[0]
54	    return min(candidatos, key=lambda p: len(p.name))
55	
56	
57	def leer(ruta: Path, llaves: list[str]) -> pd.DataFrame:
58	    df = pd.read_stata(ruta, convert_categoricals=False)
59	    df = normalizar_columnas(df)
60	    for k in llaves:
61	        if k in df.columns:
62	            df[k] = df[k].astype(str).str.strip()
63	    if "ubigeo" in df.columns:
64	        df["ubigeo"] = df["ubigeo"].astype(str).str.strip().str.zfill(6)
65	    return df
66	
67	
68	def pct_ponderado(df: pd.DataFrame, condicion: pd.Series, peso: str) -> float:
69	    w = df[peso]
70	    total = w.sum()
71	    return float(100 * w[condicion].sum() / total) if total else float("nan")
72	
73	
74	def main() -> int:
75	    ap = argparse.ArgumentParser()
76	    
… (recortado: 5,687 caracteres más)
```
</details>

<details><summary>← Resultado</summary>

```text
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

   ˋˋˋbash
   uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio 2024
   ˋˋˋ

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

La cifra que publica el 
… (recortado: 2,438 caracteres más)
```
</details>

**→ Bash**

```json
{
 "command": "cat graficando-enaho/SKILL.md && echo \"=========== graficar.py ===========\" && cat -n graficando-enaho/scripts/graficar.py",
 "description": "Read graficando-enaho skill and script"
}
```

**→ Bash**

```json
{
 "command": "cat mapeando-enaho/SKILL.md && echo \"=========== mapear.py ===========\" && cat -n mapeando-enaho/scripts/mapear.py",
 "description": "Read mapeando-enaho skill and script"
}
```

<details><summary>← Resultado</summary>

```text
---
name: graficando-enaho
description: Hace gráficos de barras de la pobreza monetaria de la ENAHO por área urbana o rural, sexo, grupo de edad o departamento, ponderando con el factor de expansión. Úsala cuando pidan graficar, comparar o visualizar la pobreza de la ENAHO del INEI.
argument-hint: [area|sexo|edad|departamento]
---

# Graficar la ENAHO

1. **Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`.**
   Sin base limpia no hay gráfico.

2. Corre exactamente:

   ˋˋˋbash
   uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --corte area --anio 2024
   ˋˋˋ

   Cortes válidos: `area` (urbano/rural), `sexo`, `edad`, `departamento`.
   Reemplaza `area` por el corte que pidió el usuario **solo si es uno de esos cuatro
   valores exactos**. `$0` trae el texto libre del pedido, no un corte: nunca lo pases
   tal cual al script.

3. El script imprime las cifras y guarda el PNG. Reporta las cifras que imprimió,
   no las recalcules, y menciona la ruta de la figura.

4. Si el usuario pide un corte que no está en la lista, lee
   `.claude/skills/limpiando-enaho/reference.md` para ver qué variables existen
   antes de proponer nada.

## Reglas que el script ya aplica

- Pondera siempre con **`facpob07`**. Nunca cuenta filas ni promedia la columna `pobreza`.
- Barras **desde cero**, ordenadas de mayor a menor. La excepción es `edad`, que va en
  orden de grupo etario porque es una escala ordinal y reordenarla haría ilegible el gráfico.
- **Un solo color** (`#b1491f`) y el valor escrito al final de cada barra.
- El título dice **qué y cuándo**: «Pobreza monetaria según área de residencia, 2024».
- Nota al pie: **«Fuente: INEI, ENAHO 2024»**.
- PNG a **200 dpi** en `figuras/`.

## Cifras de control, ENAHO 2024

Hay **dos bases** y dan cifras ligeramente distintas. Este script usa la de personas.

| Corte | Con personas y `facpob07` (lo que hace este script) | Con la sumaria y `factor07 × mieperho` (la cifra que publica el INEI) |
|---|---|---|
| Urbano | **24.7 %** | 24.8 % |
| Rural | **39.4 %** | 39.3 % |
| Nacional | **27.53 %** | 27.58 % |

La diferencia de una décima es normal y **no es un error**: la sumaria pondera hogares
por su tamaño y la base de personas pondera personas. Si el gráfico de área da 24.7 % y
39.4 %, está correcto.

Preocúpate solo si la diferencia pasa de medio punto; ahí sí vuelve a `limpiando-enaho`
y revisa `salidas/validacion.txt`.
=========== grafica
… (recortado: 4,859 caracteres más)
```
</details>

<details><summary>← Resultado</summary>

```text
---
name: mapeando-enaho
description: Hace un mapa coroplético de la pobreza monetaria de la ENAHO por departamento del Perú, uniendo la base limpia con los límites departamentales por código de ubigeo. Úsala cuando pidan un mapa, un coropleta o visualizar la pobreza del INEI por departamento, región o territorio.
argument-hint: [año]
---

# Mapear la ENAHO

1. **Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`.**
   Sin base limpia no hay mapa.

2. Corre exactamente:

   ˋˋˋbash
   uv run ${CLAUDE_SKILL_DIR}/scripts/mapear.py --anio 2024
   ˋˋˋ

   Cambia `2024` solo si el usuario pidió otro año y `$0` es un **número de cuatro
   dígitos**. `$0` trae el texto libre del pedido, no un año: nunca lo pases tal cual.

3. El script imprime las cifras y guarda `mapas/pobreza_departamento.png`.
   Reporta las cifras que imprimió y menciona la ruta del mapa.

4. Si el script se detiene porque hay departamentos sin dato, **no rellenes a mano
   ni unas por nombre**: el problema está en la limpieza o en el código de ubigeo.
   Vuelve a `limpiando-enaho`.

## Reglas que el script ya aplica

- Une **por código**: `ubigeo[:2]` de la base contra `FIRST_IDDP` del GeoJSON, los dos
  como texto de dos dígitos. **Nunca por nombre**: «APURIMAC» no es «Apurímac».
- Exige **25 departamentos y ninguno sin dato**; si falta uno, se detiene.
- Escala de **un solo color de claro a oscuro** (`Oranges`), **desde 0**. Nunca arcoíris.
- Leyenda con la unidad: **«Pobreza monetaria (% de personas)»**.
- **Lima (15) y Callao (07) van separados**, como polígonos distintos.
- Pondera con **`facpob07`**.
- PNG a **200 dpi** en `mapas/`.

## Los límites departamentales

El script busca `datos/peru_departamental_simple.geojson` y, si no está, lo descarga de:

ˋˋˋ
https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson
ˋˋˋ

Lo guarda en `datos/` para que la segunda corrida no necesite internet.

## Cifras de control, ENAHO 2024

| Departamento | Pobreza |
|---|---|
| Cajamarca | 45.0 % |
| Loreto | 43.0 % |
| Puno | 39.9 % |
| Moquegua | 11.0 % |
| Ica | 6.0 % |

La tabla completa de los 25 departamentos está en
`referencias/pobreza_departamento_2024.csv`; el script compara contra ella y reporta
la diferencia máxima.
=========== mapear.py ===========
     1	"""Mapa coroplético de la pobreza monetaria por departamento a pa
… (recortado: 5,512 caracteres más)
```
</details>

**→ Bash**

```json
{
 "command": "SP=\"~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad\"; cat > \"$SP/inspeccionar_enaho.py\" <<'EOF'\nimport sys, re\nsys.stdout.reconfigure(encoding=\"utf-8\")\nimport pandas as pd\nT = sys.argv[1]\nruta_s = f\"{T}/datos/966-Modulo34/966-Modulo34/sumaria-2024.dta\"\nwith pd.io.stata.StataReader(ruta_s) as r:\n    etiquetas = r.variable_labels()\ncols = list(etiquetas)\nprint(\"SUMARIA:\", len(cols), \"variables\")\nfor c in cols:\n    if re.match(r\"(gru\\d+hd|gashog|inghog|linea|linpe|pobreza|mieperho|totmieho|percepho|factor07|estrato|dominio|ubigeo|ld|ipcr|i00|g05|sg2|gpgru|percepho)\", c.lower()):\n        print(f\"  {c:12s} {etiquetas[c]}\")\nEOF\ncd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && uv run --with pyarrow python \"$SP/inspeccionar_enaho.py\" \"$(pwd)\" 2>&1 | head -120",
 "description": "List sumaria spending and poverty variables with labels",
 "timeout": 300000
}
```

<details><summary>← Resultado</summary>

```text
Downloading pyarrow (28.4MiB)
 Downloaded pyarrow
Installed 1 package in 166ms
SUMARIA: 163 variables
  ubigeo       ubicacion geográfica
  dominio      dominio geográfico
  estrato      estrato geográfico
  mieperho     total de miembros del hogar
  totmieho     total de personas en el hogar
  percepho     total de perceptores de ingresos
  sg23         gastos por alimentos para consumir dentro del hogar
  sg25         gastos por alimentos consumidos fuera del hogar (menores de 14 años)
  sg27         gastos por alimentos consumidos por ollas comunes
  g05hd        gastos por alimentos consumidos fuera del hogar - pago
  g05hd1       gastos por alimentos consumidos fuera del hogar en otro hogar- pago
  g05hd2       gastos por alimentos consumidos fuera del hogar prepara sus alimentos - pago
  g05hd3       gastos por alimentos consumidos fuera del hogar prepara sus alim en su centro de
  g05hd4       gastos por alimentos consumidos fuera del hogar en el aula del centro educativo
  g05hd5       gastos por alimentos consumidos fuera del hogar a autoconsumo
  g05hd6       gastos por alimentos consumidos fuera del hogar campamento - pago
  gru11hd      grupo 1: alimentos - gasto
  gru12hd1     grupo 1: alimentos - autoconsumo, autosuministro
  gru12hd2     grupo 1: alimentos - pago en especie
  gru13hd1     grupo 1: alimentos - donacion publica
  gru13hd2     grupo 1: alimentos - donacion privada
  gru13hd3     grupo 1: alimentos - otros gastos
  gru13hd4     grupo 1: alimentos consumidos dentro hogar -bienes libres
  gru14hd      alimentos preparados consumir en el hogar - pagado
  gru14hd1     alimentos preparados consumir en el hogar - autoconsumo , autosuministro
  gru14hd2     alimentos preparados consumir en el hogar - especie
  gru14hd3     alimentos preparados consumir en el hogar - donado  publico
  gru14hd4     alimentos preparados consumir en el hogar - donado privado
  gru14hd5     alimentos preparados consumir en el hogar - otros
  gru14hd6     grupo 1: alimentos consumidos fuera del hogar -bienes libres
  gru21hd      grupo 2: vestido y calzado - gasto
  gru22hd1     grupo 2: vestido y calzado - autoconsumo, autosuministro
  gru22hd2     grupo 2: vestido y calzado - pago en especie
  gru23hd1     grupo 2: vestido y calzado - donacion publica
  gru23hd2     grupo 2: vestido y calzado - donacion privada
  gru23hd3     grupo 2: vestido y calzado - otros
  gru24hd      grupo 2: vestido y calzado - no gasto, no sab
… (recortado: 4,589 caracteres más)
```
</details>

**→ Bash**

```json
{
 "command": "SP=\"~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad\"; cat > \"$SP/chequeos_enaho.py\" <<'EOF'\nimport sys\nsys.stdout.reconfigure(encoding=\"utf-8\")\nimport numpy as np, pandas as pd\nT, REF = sys.argv[1], sys.argv[2]\nK = [\"conglome\", \"vivienda\", \"hogar\"]\ns = pd.read_stata(f\"{T}/datos/966-Modulo34/966-Modulo34/sumaria-2024.dta\", convert_categoricals=False)\np = pd.read_stata(f\"{T}/datos/966-Modulo02/966-Modulo02/enaho01-2024-200.dta\", convert_categoricals=False,\n                  columns=K + [\"codperso\", \"p203\", \"p204\", \"p205\", \"p206\", \"p207\", \"p208a\", \"facpob07\"])\ns.columns = [c.lower() for c in s.columns]\nfor d in (s, p):\n    for k in K: d[k] = d[k].astype(str).str.strip()\nprint(\"tipos de llaves en el .dta:\", {k: str(pd.read_stata(f'{T}/datos/966-Modulo34/966-Modulo34/sumaria-2024.dta', convert_categoricals=False, columns=[k]).dtypes[k]) for k in K})\nprint(\"ejemplo conglome:\", s.conglome.iloc[:3].tolist())\nres = p[((p.p204 == 1) & (p.p205 == 2)) | ((p.p204 == 2) & (p.p206 == 1))]\nprint(\"filas m02:\", len(p), \"residentes:\", len(res), \"hogares sumaria:\", len(s))\nn_res = res.groupby(K).size().rename(\"n_res\")\nh = s.merge(n_res, on=K, how=\"left\", validate=\"1:1\")\nprint(\"hogares sin residentes:\", h.n_res.isna().sum())\nprint(\"n_res == mieperho:\", (h.n_res == h.mieperho).mean().round(4), \"| diferencias:\", (h.n_res != h.mieperho).sum())\nprint(h.loc[h.n_res != h.mieperho, [\"mieperho\", \"n_res\", \"totmieho\"]].head(8).to_string())\nw = h.factor07 * h.mieperho\nprint(\"pobreza f07*mieperho: %.4f\" % (100 * w[h.pobreza <= 2].sum() / w.sum()))\n# ¿la suma de los grupos reproduce gashog2d?\ngru = [c for c in s.columns if c.startswith(\"gru\")]\ng1 = [c for c in gru if c.startswith(\"gru1\")]\ntot = s[gru].fillna(0).sum(axis=1)\nrel = (tot - s.gashog2d).abs() / s.gashog2d.replace(0, np.nan)\nprint(\"gru*:\", len(gru), \"columnas; grupo 1:\", g1)\nprint(\"suma gru* vs gashog2d: mediana dif rel %.2e, p99 %.2e, max %.2e\" % (rel.median(), rel.quantile(.99), rel.max()))\nprint(\"gashog2d == 0:\", (s.gashog2d == 0).sum(), \" nulos:\", s.gashog2d.isna().sum())\nshare = s[g1].fillna(0).sum(axis=1) / s.gashog2d\nprint(\"participación alimentos: media ponderada f07 %.4f\" % np.average(share.dropna(), weights=s.factor07[share.notna()]))\nprint(\"p208a: min\", res.p208a.min(), \"max\", res.p208a.max(), \"nulos\", res.p208a.isna().sum())\nref = pd.read_csv(REF, dtype={\"ccdd\": str}); print(\"REFERENCIA:\", ref.columns.tolist(), len(ref)); print(ref.head(3).to_string())\n# base persona facpob07 vs hogar por departamento contra la referencia\nh[\"ccdd\"] = h.ubigeo.astype(str).str.zfill(6).str[:2]\ndep_h = h.assign(_w=w, _p=w * (h.pobreza <= 2)).groupby(\"ccdd\")[[\"_w\", \"_p\"]].sum(); dep_h = 100 * dep_h._p / dep_h._w\nr2 = res.merge(s[K + [\"pobreza\", \"ubigeo\"]], on=K, validate=\"m:1\"); r2[\"ccdd\"] = r2.ubigeo.astype(str).str.zfill(6).str[:2]\ndep_p = r2.assign(_w=r2.facpob07, _p=r2.facpob07 * (r2.pobreza <= 2)).groupby(\"ccdd\")[[\"_w\", \"_p\"]].sum(); dep_p = 100 * dep_p._p / dep_p._w\nc = ref.set_index(\"ccdd\").join(dep_h.rename(\"hogar\")).join(dep_p.rename(\"persona\"))\ncol = [x for x in ref.columns if x != \"ccdd\" and pd.api.types.is_numeric_dtype(ref[x])][0]\nprint(f\"max |ref - hogar| = {(c[col]-c.hogar).abs().max():.3f}   max |ref - persona| = {(c[col]-c.persona).abs().max():.3f}\")\nEOF\ncd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && uv run --with pyarrow python \"$SP/chequeos_enaho.py\" \"$(pwd)\" ~/Documentos/GitHub/Data-Science-Python/sessions/16-skills-enaho/referencias/pobreza_departamento_2024.csv 2>&1 | grep -v Warning",
 "description": "Check residents vs mieperho, spending sums, reference base",
 "timeout": 300000
}
```

<details><summary>← Resultado</summary>

```text
tipos de llaves en el .dta: {'conglome': 'str', 'vivienda': 'str', 'hogar': 'str'}
ejemplo conglome: ['015009', '015009', '015009']
filas m02: 117721 residentes: 108664 hogares sumaria: 33691
hogares sin residentes: 0
n_res == mieperho: 0.9452 | diferencias: 1846
     mieperho  n_res  totmieho
7           2      3         3
81          3      2         3
92          4      3         4
126         5      6         6
129         4      3         4
154         4      1         4
160         2      3         3
162         4      3         4
pobreza f07*mieperho: 27.5795
gru*: 69 columnas; grupo 1: ['gru11hd', 'gru12hd1', 'gru12hd2', 'gru13hd1', 'gru13hd2', 'gru13hd3', 'gru13hd4', 'gru14hd', 'gru14hd1', 'gru14hd2', 'gru14hd3', 'gru14hd4', 'gru14hd5', 'gru14hd6']
suma gru* vs gashog2d: mediana dif rel 1.03e-01, p99 5.48e-01, max 1.37e+00
gashog2d == 0: 0  nulos: 0
participación alimentos: media ponderada f07 0.3609
p208a: min 0.0 max 98.0 nulos 0
REFERENCIA: ['ccdd', 'departamento', 'pobreza_pct'] 25
  ccdd departamento  pobreza_pct
0   01     AMAZONAS         25.7
1   02       ANCASH         22.8
2   03     APURIMAC         24.0
max |ref - hogar| = 0.049   max |ref - persona| = 0.518
```
</details>

**→ Bash**

```json
{
 "command": "SP=\"~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad\"; cat > \"$SP/gasto_lstsq.py\" <<'EOF'\nimport sys\nsys.stdout.reconfigure(encoding=\"utf-8\")\nimport numpy as np, pandas as pd\ns = pd.read_stata(f\"{sys.argv[1]}/datos/966-Modulo34/966-Modulo34/sumaria-2024.dta\", convert_categoricals=False)\ns.columns = [c.lower() for c in s.columns]\nextra = [\"sg23\", \"sg25\", \"sg27\", \"g05hd\", \"g05hd1\", \"g05hd2\", \"g05hd3\", \"g05hd4\", \"g05hd5\", \"g05hd6\"]\ngru = [c for c in s.columns if c.startswith(\"gru\")]\nfor nombre, cols in [(\"gru*\", gru), (\"gru* + sg/g05\", gru + [c for c in extra if c in s.columns])]:\n    X = s[cols].fillna(0).to_numpy(float); y = s.gashog2d.to_numpy(float)\n    b, *_ = np.linalg.lstsq(X, y, rcond=None)\n    pred = X @ b; r = np.abs(pred - y) / y\n    print(f\"\\n== {nombre}: dif rel mediana {np.median(r):.2e}, p99 {np.quantile(r,.99):.2e}\")\n    print(\"   coef ~1:\", [c for c, v in zip(cols, b) if abs(v - 1) < 0.02])\n    print(\"   coef ~0:\", [c for c, v in zip(cols, b) if abs(v) < 0.02])\n    print(\"   otros  :\", {c: round(v, 3) for c, v in zip(cols, b) if abs(v) >= 0.02 and abs(v - 1) >= 0.02})\nEOF\ncd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && uv run --with pyarrow python \"$SP/gasto_lstsq.py\" \"$(pwd)\" 2>&1 | grep -v Warning",
 "description": "Regress gashog2d on spending components",
 "timeout": 300000
}
```

<details><summary>← Resultado</summary>

```text
== gru*: dif rel mediana 9.68e-02, p99 4.70e-01
   coef ~1: ['gru22hd1', 'gru43hd2']
   coef ~0: ['gru87hd']
   otros  : {'gru11hd': np.float64(1.177), 'gru12hd1': np.float64(1.115), 'gru12hd2': np.float64(1.746), 'gru13hd1': np.float64(1.021), 'gru13hd2': np.float64(1.078), 'gru13hd3': np.float64(1.048), 'gru13hd4': np.float64(-0.025), 'gru14hd': np.float64(1.161), 'gru14hd1': np.float64(1.056), 'gru14hd2': np.float64(1.199), 'gru14hd3': np.float64(1.166), 'gru14hd4': np.float64(1.142), 'gru14hd5': np.float64(2.414), 'gru14hd6': np.float64(5.818), 'gru21hd': np.float64(1.38), 'gru22hd2': np.float64(0.807), 'gru23hd1': np.float64(1.878), 'gru23hd2': np.float64(0.816), 'gru23hd3': np.float64(6.918), 'gru24hd': np.float64(0.063), 'gru31hd': np.float64(1.151), 'gru32hd1': np.float64(0.725), 'gru32hd2': np.float64(0.431), 'gru33hd1': np.float64(-3.127), 'gru33hd2': np.float64(1.037), 'gru33hd3': np.float64(2.623), 'gru34hd': np.float64(1.079), 'gru41hd': np.float64(1.13), 'gru42hd1': np.float64(1.539), 'gru42hd2': np.float64(2.87), 'gru43hd1': np.float64(1.221), 'gru43hd3': np.float64(2.393), 'gru44hd': np.float64(6.711), 'gru51hd': np.float64(1.085), 'gru52hd1': np.float64(0.368), 'gru53hd1': np.float64(1.026), 'gru53hd2': np.float64(1.023), 'gru53hd3': np.float64(1.166), 'gru53hd4': np.float64(0.387), 'gru54hd': np.float64(1.498), 'gru61hd': np.float64(1.225), 'gru62hd1': np.float64(1.335), 'gru62hd2': np.float64(1.768), 'gru63hd1': np.float64(1.219), 'gru63hd2': np.float64(1.168), 'gru63hd3': np.float64(0.817), 'gru64hd': np.float64(1.832), 'gru71hd': np.float64(1.182), 'gru72hd1': np.float64(0.675), 'gru72hd2': np.float64(2.329), 'gru73hd1': np.float64(1.468), 'gru73hd2': np.float64(1.049), 'gru73hd3': np.float64(0.911), 'gru74hd': np.float64(2.928), 'gru81hd': np.float64(1.499), 'gru82hd1': np.float64(0.945), 'gru82hd2': np.float64(1.033), 'gru83hd1': np.float64(5.75), 'gru83hd2': np.float64(0.864), 'gru83hd3': np.float64(1.103), 'gru83hd4': np.float64(0.494), 'gru84hd': np.float64(-2.476), 'gru84hd1': np.float64(0.297), 'gru85hd1': np.float64(-1.018), 'gru86hd1': np.float64(-0.048), 'gru86hd2': np.float64(-4.434)}

== gru* + sg/g05: dif rel mediana 3.74e-02, p99 2.34e-01
   coef ~1: ['gru12hd1', 'gru13hd2', 'gru14hd', 'gru14hd1', 'gru14hd4', 'gru53hd2', 'gru63hd2', 'gru73hd1', 'gru83hd2']
   coef ~0: ['gru87hd', 'g05hd3', 'g05hd4', 'g05hd5', 'g05hd6']
   otros  : {'gru11hd': np.float64(1.096), 'gru12hd2': np.float64(1.336), 'gru13hd1': np.float64(0.961),
… (recortado: 1,889 caracteres más)
```
</details>

**→ Bash**

```json
{
 "command": "SP=\"~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad\"; D=\"$SP/constvargasto\"; rm -rf \"$D\"; mkdir -p \"$D\" && cd \"$D\" && unzip -o -q \"~/Documentos/GitHub/python-intermedio-QLAB/datos/966-Modulo34/966-Modulo34/ConstVarGasto-Metodologia actualizada.zip\" -d \"$D\" && find \"$D\" -type f | head -20 && find \"$D\" -type f -exec file {} \\; | head",
 "description": "Extract INEI spending-construction methodology zip"
}
```

<details><summary>← Resultado</summary>

```text
~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad/constvargasto/Gasto2024/00_Instruccion_para_la_construccion_gasto-real.txt
~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad/constvargasto/Gasto2024/01.ConstrVarGastoIngreso2014-2024.do
~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad/constvargasto/Gasto2024/Bases/deflactores_base2024_new.dta
~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad/constvargasto/Gasto2024/Bases/despacial_ldnew.dta
~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad/constvargasto/Gasto2024/00_Instruccion_para_la_construccion_gasto-real.txt: ISO-8859 text, with CRLF line terminators
~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad/constvargasto/Gasto2024/01.ConstrVarGastoIngreso2014-2024.do: ISO-8859 text, with CRLF line terminators
~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad/constvargasto/Gasto2024/Bases/deflactores_base2024_new.dta: data
~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad/constvargasto/Gasto2024/Bases/despacial_ldnew.dta: data
```
</details>

**→ Bash**

```json
{
 "command": "cd \"~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad/constvargasto/Gasto2024\" && iconv -f latin1 -t utf-8 00_Instruccion_para_la_construccion_gasto-real.txt | head -40; echo \"=== .do: líneas con gru1/gashog2d/gpgru ===\"; iconv -f latin1 -t utf-8 01.ConstrVarGastoIngreso2014-2024.do > do.txt; wc -l do.txt; grep -n -i -E \"gpgru1|gru1|gashog2d|gpcrg1|gpgru0|egen|gen gpgru|gpcrg\" do.txt | head -60",
 "description": "Read INEI instructions and grep food-spending construction"
}
```

<details><summary>← Resultado</summary>

```text
CONSTRUCCION DEL GASTO E INGRESO REAL 2014 - 2024 NUEVA METODOLOGIA


Pasos a seguir para la construcción de variables del gasto e ingreso real:


1. Copiar el zipeado "ConstVarGasto-nuevaMetodologia.ZIP" en el disco D. Luego realizar el desempaquetado.


2. A continuación preparar los archivos en STATA: 

		* "sumaria-2014"
		* "sumaria-2015"
		* "sumaria-2016"
		* "sumaria-2017"
		* "sumaria-2018"
		* "sumaria-2019"
		* "sumaria-2020"
		* "sumaria-2021"
		* "sumaria-2022"
		* "sumaria-2023"
		* "sumaria-2024"



	Recuerde que estos archivos debe de grabarlos en:

        "D:\Gasto2024\Bases"


3. Luego aplicar el siguiente Stata Do-file
			
		* 01_ConstrVarGastoIngreso2014-2024=== .do: líneas con gru1/gashog2d/gpgru ===
365 do.txt
103:gen 		gpcrg3= (gru11hd + gru12hd1 + gru12hd2 + gru13hd1 + gru13hd2 + gru13hd3 )/(p*mieperho*ld*i01) 
104:gen 		gpcrg6 = ((g05hd + g05hd1 + g05hd2 + g05hd3 + g05hd4 + g05hd5 +g05hd6 +ig06hd)/(p*mieperho*ld*i01)) 
105:gen 		gpcrg8= ((sg23 + sig24)/(p*mieperho*ld*i01)) 
106:gen 		gpcrg9= ((gru14hd + gru14hd1 +  gru14hd2 + gru14hd3 + gru14hd4 + gru14hd5 + sg25 + sig26 + sg27 + sig28)/(p*mieperho*ld*i01)) 
107:gen    		gpcrg10= ((gru21hd + gru22hd1 + gru22hd2 + gru23hd1 + gru23hd2 + gru23hd3 + gru24hd)/(p*mieperho*ld*i02)) 
108:gen     	gpcrg12= ((gru31hd + gru32hd1 + gru32hd2 + gru33hd1 + gru33hd2 + gru33hd3 + gru34hd)/(p*mieperho*ld*i03)) 
109:gen     	gpcrg14= ((gru41hd + gru42hd1 + gru42hd2 + gru43hd1 + gru43hd2 + gru43hd3 + gru44hd + sg421 + sg42d1 + sg423 + sg42d3)/(p*mieperho*ld*i04)) 
110:gen    		gpcrg16= ((gru51hd + gru52hd1 + gru52hd2 + gru53hd1 + gru53hd2 + gru53hd3 + gru54hd)/(p*mieperho*ld*i05)) 
111:gen     	gpcrg18= ((gru61hd + gru62hd1 + gru62hd2 + gru63hd1 + gru63hd2 + gru63hd3 + gru64hd + g07hd + ig08hd + sg422 + sg42d2)/(p*mieperho*ld*i06)) 
112:gen     	gpcrg19= ((gru71hd + gru72hd1 + gru72hd2 + gru73hd1 + gru73hd2 + gru73hd3 + gru74hd + sg42 + sg42d)/(p*mieperho*ld*i07)) 
113:gen     	gpcrg21= ((gru81hd + gru82hd1 + gru82hd2 + gru83hd1 + gru83hd2 + gru83hd3 + gru84hd)/(p*mieperho*ld*i08)) 
115:label var gpcrg3	"Preparados dentro del hogar"
116:label var gpcrg6	"Adquiridos Fuera del hogar 559"
117:label var gpcrg8	"Adquiridos de instituciones beneficas 602a"
118:label var gpcrg9	"Adquiridos fuera del hogar item 47 y 50 y 602"
119:label var gpcrg10	"Vestido y calzado"
120:label var gpcrg12	"Gasto Alquiler de vivienda y combustible"
121:label var gpcrg14	"Muebles y enseres"
122:
… (recortado: 2,712 caracteres más)
```
</details>

**→ Bash**

```json
{
 "command": "cd \"~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad/constvargasto/Gasto2024\" && sed -n '60,102p' do.txt | grep -v -E \"^\\s*$\" | head -40",
 "description": "Read the do-file preamble defining p and deflators"
}
```

<details><summary>← Resultado</summary>

```text
replace dominioA=2 if dominio==1 & area==2
replace dominioA=3 if dominio==2 & area==1
replace dominioA=4 if dominio==2 & area==2
replace dominioA=5 if dominio==3 & area==1
replace dominioA=6 if dominio==3 & area==2
replace dominioA=7 if dominio==4 & area==1
replace dominioA=8 if dominio==4 & area==2
replace dominioA=9 if dominio==5 & area==1
replace dominioA=10 if dominio==5 & area==2
replace dominioA=11 if dominio==6 & area==1
replace dominioA=12 if dominio==6 & area==2
replace dominioA=13 if dominio==7 & area==1
replace dominioA=14 if dominio==7 & area==2
replace dominioA=15 if dominio==7 & (dpto==16 | dpto==17 | dpto==25) & area==1
replace dominioA=16 if dominio==7 & (dpto==16 | dpto==17 | dpto==25) & area==2
replace dominioA=17 if dominio==8 & area==1
replace dominioA=17 if dominio==8 & area==2
label define dominioA 1 "Costa norte urbana" 2 "Costa norte rural" 3 "Costa centro urbana" 4 "Costa centro rural" /*
*/ 5 "Costa sur urbana" 6 "Costa sur rural"	7 "Sierra norte urbana"	8 "Sierra norte rural"	9 "Sierra centro urbana" /* 
*/ 10 "Sierra centro rural"	11 "Sierra sur urbana" 12 "Sierra sur rural" 13 "Selva alta urbana"	14 "Selva alta rural" /*
*/ 15 "Selva baja urbana" 16 "Selva baja rural" 17"Lima Metropolitana"
lab val dominioA dominioA 
drop ld
sort  dominioA
merge dominioA using "d:\gasto2024\bases\despacial_ldnew.dta"
tab _m
drop _m
gen factornd07=round(factor07*mieperho,1)
gen p = 12 //periodo anual
svyset [pweight = factornd07], psu(conglome)
****************************************************
******Gasto por 8  grupos de la canastas************
****************************************************
```
</details>

**→ Bash**

```json
{
 "command": "SP=\"~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad\"; cat > \"$SP/gasto_inei.py\" <<'EOF'\nimport sys\nsys.stdout.reconfigure(encoding=\"utf-8\")\nimport numpy as np, pandas as pd\ns = pd.read_stata(f\"{sys.argv[1]}/datos/966-Modulo34/966-Modulo34/sumaria-2024.dta\", convert_categoricals=False)\ns.columns = [c.lower() for c in s.columns]\nG = {  # do-file oficial del INEI (01.ConstrVarGastoIngreso2014-2024.do), en valores nominales anuales\n \"g1_alimentos\": \"gru11hd gru12hd1 gru12hd2 gru13hd1 gru13hd2 gru13hd3 g05hd g05hd1 g05hd2 g05hd3 g05hd4 g05hd5 g05hd6 ig06hd sg23 sig24 gru14hd gru14hd1 gru14hd2 gru14hd3 gru14hd4 gru14hd5 sg25 sig26 sg27 sig28\",\n \"g2_vestido\": \"gru21hd gru22hd1 gru22hd2 gru23hd1 gru23hd2 gru23hd3 gru24hd\",\n \"g3_vivienda\": \"gru31hd gru32hd1 gru32hd2 gru33hd1 gru33hd2 gru33hd3 gru34hd\",\n \"g4_muebles\": \"gru41hd gru42hd1 gru42hd2 gru43hd1 gru43hd2 gru43hd3 gru44hd sg421 sg42d1 sg423 sg42d3\",\n \"g5_salud\": \"gru51hd gru52hd1 gru52hd2 gru53hd1 gru53hd2 gru53hd3 gru54hd\",\n \"g6_transporte\": \"gru61hd gru62hd1 gru62hd2 gru63hd1 gru63hd2 gru63hd3 gru64hd g07hd ig08hd sg422 sg42d2\",\n \"g7_esparcimiento\": \"gru71hd gru72hd1 gru72hd2 gru73hd1 gru73hd2 gru73hd3 gru74hd sg42 sg42d\",\n \"g8_otros\": \"gru81hd gru82hd1 gru82hd2 gru83hd1 gru83hd2 gru83hd3 gru84hd\",\n}\nfaltan = [v for cols in G.values() for v in cols.split() if v not in s.columns]\nprint(\"variables que faltan en la sumaria:\", faltan)\nfor g, cols in G.items():\n    s[g] = s[[c for c in cols.split() if c in s.columns]].fillna(0).sum(axis=1)\ns[\"g0_total\"] = s[list(G)].sum(axis=1)\nd = (s.g0_total - s.gashog2d)\nprint(\"g0_total - gashog2d: max abs %.4f | hogares con |dif|>1 sol: %d de %d\" % (d.abs().max(), (d.abs() > 1).sum(), len(s)))\nprint(\"nulos en componentes:\", int(s[[c for cols in G.values() for c in cols.split() if c in s.columns]].isna().sum().sum()))\nw = s.factor07 * s.mieperho\nshare = 100 * s.g1_alimentos / s.g0_total\nprint(\"participación de alimentos, media de hogares (factor07×mieperho): %.2f %%\" % np.average(share, weights=w))\nprint(\"participación de alimentos, media de hogares (factor07): %.2f %%\" % np.average(share, weights=s.factor07))\nEOF\ncd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && uv run --with pyarrow python \"$SP/gasto_inei.py\" \"$(pwd)\" 2>&1 | grep -v Warning",
 "description": "Rebuild INEI spending groups and compare with gashog2d",
 "timeout": 300000
}
```

<details><summary>← Resultado</summary>

```text
variables que faltan en la sumaria: ['gru52hd2']
g0_total - gashog2d: max abs 0.0142 | hogares con |dif|>1 sol: 0 de 33691
nulos en componentes: 0
participación de alimentos, media de hogares (factor07×mieperho): 46.57 %
participación de alimentos, media de hogares (factor07): 45.80 %
```
</details>

**→ Skill**

```json
{
 "skill": "dataviz"
}
```

<details><summary>← Resultado</summary>

```text
Launching skill: dataviz
```
</details>

<details><summary>Contenido inyectado por Claude Code (skill o comando)</summary>

```text
Base directory for this skill: ~\AppData\Local\Temp\claude\bundled-skills\2.1.318\6835aca7f91fb92cdd0d95ff428dd985\dataviz

# Data Visualization

A chart is **read by people and executed by you**. This skill turns "make it look
good" into a procedure with checks, so the result is right by construction rather
than by taste.

**The method here is design-system-agnostic.** Nothing in the procedure, the form
heuristic, the six checks, or the mark specs is specific to one product. A design
system supplies a small set of *parameters* (its ramps, a categorical order, a
diverging pair, a status palette, a texture, its surfaces, its filter components);
the method consumes them unchanged. A **validated default palette** is the
reference instance, fully specified in `references/palette.md`. To target your
brand, read that file's structure and substitute its values - touch nothing else.

> The single most important habit: **the color part is computable, so compute it.**
> Never eyeball whether a palette is colorblind-safe - run `scripts/validate_palette.js`.

## The procedure - do these in order

Color comes LAST. Most bad charts pick colors first.

1. **Pick the form.** What is the data's job
… (recortado: 6,009 caracteres más)
```
</details>

**→ Bash**

```json
{
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB && ls referencias/ && head -3 referencias/pobreza_departamento_2024.csv 2>/dev/null; cmp referencias/pobreza_departamento_2024.csv ~/Documentos/GitHub/Data-Science-Python/sessions/16-skills-enaho/referencias/pobreza_departamento_2024.csv && echo \"idéntica a la de la sesión 16\"",
 "description": "Check root reference CSV matches session 16"
}
```

<details><summary>← Resultado</summary>

```text
pobreza_departamento_2024.csv
ccdd,departamento,pobreza_pct
01,AMAZONAS,25.7
02,ANCASH,22.8
idéntica a la de la sesión 16
```
</details>

**→ Bash**

```json
{
 "command": "D=\"~/AppData/Local/Temp/claude/bundled-skills/2.1.318/6835aca7f91fb92cdd0d95ff428dd985/dataviz/references\"; sed -n '1,200p' \"$D/palette.md\" | head -150",
 "description": "Read dataviz reference palette"
}
```

<details><summary>← Resultado</summary>

```text
# Reference palette

This is the **reference instance** of the data-viz method: every parameter the
method needs, filled in with a validated default palette. The rest of the skill
is system-agnostic - **to target your brand, substitute this file's values** and
re-run the validator. Nothing else changes.

## How to use these values

Everything below is plain hex. In an HTML chart, **define the slots you use as
CSS custom properties in a local `<style>` block** at the top of the file, then
reference them by role throughout - so the light/dark values swap in one place,
and the chart body is written against roles rather than raw hex:

ˋˋˋcss
.viz-root {
  color-scheme: light;
  --surface-1:      #fcfcfb;   /* chart surface */
  --text-primary:   #0b0b0b;
  --text-secondary: #52514e;
  --series-1:       #2a78d6;   /* categorical slot 1 */
  /* ...only the roles this chart uses */
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) .viz-root {
    color-scheme: dark;
    --surface-1:      #1a1a19;
    --text-primary:   #f0efec;
    --text-secondary: #c3c2b7;
    --series-1:       #3987e5;
  }
}
:root[data-theme="dark"] .viz-root {
  color-scheme: dark;
  --surface-1:      #1a1a19;
  --text-primary:   #f0efec;
  --text-secondary: #c3c2b7;
  --series-1:       #3987e5;
}
ˋˋˋ

Declare the dark values under both scopes as above - the media query covers
the OS setting; the `data-theme` scope covers the viewer's theme toggle,
which must win both ways (the `:not(...)` guard lets a light stamp beat
OS-dark; `:where()` keeps the media block below the toggle scope).

## Categorical palette

Both modes are selected. The dark column is the same eight hues stepped for the
dark surface, not a separate palette:

| Slot | Hue | Light | Dark |
|------|-----|-------|------|
| 1 | blue | `#2a78d6` | `#3987e5` |
| 2 | orange | `#eb6834` | `#d95926` |
| 3 | aqua | `#1baf7a` | `#199e70` |
| 4 | yellow | `#eda100` | `#c98500` |
| 5 | magenta | `#e87ba4` | `#d55181` |
| 6 | green | `#008300` | `#008300` |
| 7 | violet | `#6250d6` | `#9085e9` |
| 8 | red | `#e34948` | `#e66767` |

This order passes every hard gate in both modes on the default *adjacent*
pairlist (stacks, bars, lines): worst adjacent CVD Delta E 9.1 light / 8.4 dark
(OKLab ×100, >=8 target), worst adjacent normal-vision Delta E 19.6 light / 19.3
dark (>=15 floor). Under `--pairs all` (scatter, bubble, choropleth, small
multiples) the full eight cannot clear the floors - with all 28 pairs in
p
… (recortado: 4,832 caracteres más)
```
</details>

**→ Bash**

```json
{
 "command": "D=\"~/AppData/Local/Temp/claude/bundled-skills/2.1.318/6835aca7f91fb92cdd0d95ff428dd985/dataviz/references\"; grep -v '^$' \"$D/anti-patterns.md\" | head -70; echo ======; grep -n -i -E \"^#|bar|label|grid|axis|title|baseline|choropleth|surface|text\" \"$D/marks-and-anatomy.md\" | head -60",
 "description": "Skim anti-patterns and mark specs"
}
```

<details><summary>← Resultado</summary>

```text
# Anti-patterns - what goes wrong
Check every chart against this list. If your output matches an entry, it is wrong -
fix it before shipping. These are real failure modes, each caught in shipping
dashboards.
## Color & encoding
**Bad: Dual-axis charts (two y-scales on one plot).**
Why it misleads: the alignment of the two scales is arbitrary, so the chart invents a
correlation that isn't in the data. Real example: an "Adoption" chart plotting Users
(0-30k) against Sessions (0-800k) - a reviewer flagged it as looking "hallucinated."
Good: Do instead: two charts, small multiples, or index both series to a common base
(=100 at t0) on **one** axis.
**Bad: Recolor-on-filter.** Assigning colors by current rank, so filtering out a series
repaints the survivors.
Why: a reader who learned "Acme is blue" is now misled.
Good: Color follows the entity, not its row number. Survivors keep their hue.
**Bad: Cycling / generating hues past 8.** A 9th categorical color, generated or reused.
Why: indistinguishable from an existing slot under CVD; breaks the order check.
Good: Fold the tail into "Other," facet into small multiples, or use composite encoding.
**Bad: Eyeballing colorblind-safety.** "These look different enough."
Good: Run `scripts/validate_palette.js`. Adjacent Delta E >= 8 (OKLab ×100), or 6-8 WITH secondary encoding.
**Bad: A value-ramp on nominal categories.** Coloring each bar darker-where-bigger
when the categories have no natural order (products, teams, endpoints).
Why: it double-encodes bar length as hue, burns the only free channel on
information the chart already shows, and fails the categorical checks by design
(a ramp spans the lightness band and drops below the chroma floor).
Good: One series -> one color (slot 1) for every bar. Ordered categories (funnel,
tiers, age bands) -> the ordinal ramp, validated with `--ordinal`.
**Bad: Rainbow / non-neighbor sequential.** A multi-hue ramp for magnitude.
Good: One hue, light->dark. (Analogous neighbors or semantic heat are the only multi-hue
sequential exceptions, always with a scale legend.)
**Bad: A hue at the diverging midpoint, or two cool hues as the two poles.**
Why: the midpoint must read as "nothing"; poles must read as opposite. blue<->aqua
fails this (both cool); blue<->red or blue<->orange succeed (warm/cool).
Good: Two hues that read as opposite + a neutral gray midpoint.
**Bad: Status color used for a non-status series** (or a series color used for status).
Good: Status tokens only when the col
… (recortado: 6,625 caracteres más)
```
</details>

**→ Bash**

```json
{
 "command": "cd \"~/AppData/Local/Temp/claude/bundled-skills/2.1.318/6835aca7f91fb92cdd0d95ff428dd985/dataviz\" && node --version && echo \"== ordinal edad (5 pasos, 250→650) ==\" && node scripts/validate_palette.js \"#86b6ef,#5598e7,#2a78d6,#1c5cab,#104281\" --mode light --ordinal 2>&1 | tail -15 && echo \"== categórica 3 slots (gráfico BCRP de la parte 3) ==\" && node scripts/validate_palette.js \"#2a78d6,#eb6834,#1baf7a\" --mode light --pairs all 2>&1 | tail -12",
 "description": "Validate ordinal and categorical palettes"
}
```

<details><summary>← Resultado</summary>

```text
v24.18.0
== ordinal edad (5 pasos, 250→650) ==

Palette (light, surface #fcfcfb, ordinal ramp): 5 slots
  [PASS] Lightness monotone     steps read light→dark
  [PASS] Adjacent ΔL            all gaps >= 0.06
  [PASS] Light-end contrast     #86b6ef at 2.06:1 vs surface
  [PASS] Single hue             hue spread 3°

  → ALL CHECKS PASS  (ordinal: one hue, monotone L, visible step gaps, light end clears surface)
== categórica 3 slots (gráfico BCRP de la parte 3) ==

Palette (light, surface #fcfcfb, categorical): 3 slots
  [PASS] Lightness band         all 3 inside L 0.43–0.77
  [PASS] Chroma floor           all 3 >= 0.1
  [PASS] CVD separation         worst all-pairs #1baf7a↔#eb6834 ΔE 9.2 (deutan) · tritan 9.6
  [PASS] Normal-vision floor    worst all-pairs #1baf7a↔#2a78d6 ΔE 24.0 (normal)
  [WARN] Contrast vs surface    below 3:1 — relief required (visible labels or table view): [["#1baf7a",2.74]]

  → ALL CHECKS PASS  (CVD in the 6–8 floor band is legal ONLY with secondary encoding: direct labels, gaps, or texture)
  scope: categorical palettes only. For a lone status/text color check text contrast with this script's apca() or contrast(); for a sequential ramp, lightness monotonicity.
```
</details>

**→ Bash**

```json
{
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && uv add pyarrow geopandas matplotlib 2>&1 | tail -4 && cat pyproject.toml",
 "description": "Add pyarrow, geopandas, matplotlib dependencies",
 "timeout": 600000
}
```

<details><summary>← Resultado</summary>

```text
+ pyogrio==0.13.0
 + pyparsing==3.3.3
 + pyproj==3.8.0
 + shapely==2.2.0
[project]
name = "tarea-4-agente-investigacion"
version = "0.1.0"
description = "Agente de investigación socioeconómica: MCP del BCRP y Skills de la ENAHO 2024"
requires-python = ">=3.11"
dependencies = [
    "fastmcp>=4,<5",
    "geopandas>=1.2.0",
    "httpx",
    "matplotlib>=3.11.2",
    "pandas",
    "pyarrow>=26.0.1",
]

[dependency-groups]
dev = ["pytest"]

[tool.pytest.ini_options]
testpaths = ["mcp"]
```
</details>

**→ Write**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\limpiando-enaho\\scripts\\limpiar.py",
 "content": "\"\"\"Limpieza de la ENAHO para la tarea 4: módulos 34 (sumaria) y 02 (miembros).\n\n    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024        # desde tarea_4/\n\nVERSIÓN TAREA 4. Difiere de la de la sesión 16 (raíz del repo) en la ponderación: aquí la cifra oficial sale de la\nbase hogar ponderada con factor07 × mieperho, que es la que publica el INEI (27.6 %, urbana 24.8 %, rural 39.3 %).\nLa base persona con facpob07 (27.53 %, 24.7 %, 39.4 %) queda como cifra secundaria, solo para cortes por atributos\nde la persona (sexo, edad).\n\nSalidas en tarea_4/salidas/:\n  hogares_<año>.parquet   una fila por hogar: pobreza, territorio, gasto por grupos y estructura por edad\n  personas_<año>.parquet  una fila por residente habitual, con las variables de su hogar\n  indicadores.csv         indicadores ponderados (los que usan gráficos, mapa e informe)\n  validacion.txt          comprobaciones; si una esencial falla, el script termina con error y no deja bases\n\"\"\"\n\nimport argparse\nimport sys\nimport unicodedata\nimport zipfile\nfrom pathlib import Path\n\nimport numpy as np\nimport pandas as pd\n\nLLAVES_HOGAR = [\"conglome\", \"vivienda\", \"hogar\"]\nLLAVES_PERSONA = LLAVES_HOGAR + [\"codperso\"]\nEDAD_ADULTO_MAYOR = 65\nTOLERANCIA = 0.1                     # puntos porcentuales\nREFERENCIAS = {                      # issue #201 y cifras publicadas por el INEI, base hogar\n    2024: {\"pobreza_nacional\": 27.6, \"pobreza_urbana\": 24.8, \"pobreza_rural\": 39.3, \"residentes\": 108_664,\n           \"unida… (recortado; el archivo completo está en el repo)"
}
```

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\limpiando-enaho\scripts\limpiar.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

### Claude

Corrijo un resto que me quedó en la agregación del hogar (una columna `jefe_am` provisional que luego se reemplaza) antes de correr.

**→ Edit**

```json
{
 "replace_all": false,
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\limpiando-enaho\\scripts\\limpiar.py",
 "old_string": "    comp = personas.groupby(LLAVES_HOGAR).agg(\n        n_residentes=(\"codperso\", \"size\"), n_am=(\"adulto_mayor\", \"sum\"),\n        n_menores_18=(\"p208a\", lambda e: int((e < 18).sum())),\n        jefe_am=(\"p203\", lambda _: False)).reset_index()\n    jefes = personas.loc[personas.p203 == 1, LLAVES_HOGAR + [\"adulto_mayor\"]].rename(columns={\"adulto_mayor\": \"jefe_am\"})\n    comp = comp.drop(columns=\"jefe_am\").merge(jefes, on=LLAVES_HOGAR, how=\"left\", validate=\"1:1\")",
 "new_string": "    comp = (personas.assign(menor_18=personas.p208a < 18)\n            .groupby(LLAVES_HOGAR)\n            .agg(n_residentes=(\"codperso\", \"size\"), n_am=(\"adulto_mayor\", \"sum\"), n_menores_18=(\"menor_18\", \"sum\"))\n            .reset_index())\n    jefes = personas.loc[personas.p203 == 1, LLAVES_HOGAR + [\"adulto_mayor\"]].rename(columns={\"adulto_mayor\": \"jefe_am\"})\n    comp = comp.merge(jefes, on=LLAVES_HOGAR, how=\"left\", validate=\"1:1\")"
}
```

**→ Bash**

```json
{
 "command": "time uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024; echo \"exit=$?\"",
 "description": "Run the adapted ENAHO cleaning script",
 "timeout": 600000
}
```

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\limpiando-enaho\scripts\limpiar.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

<details><summary>← Resultado</summary>

```text
ENAHO 2024 � validaci�n de la limpieza (versi�n tarea_4)
Generado por .claude/skills/limpiando-enaho/scripts/limpiar.py. Ninguna cifra est� escrita a mano.

Archivos
  sumaria : datos/966-Modulo34/966-Modulo34/sumaria-2024.dta (33,691 hogares)
  miembros: datos/966-Modulo02/966-Modulo02/enaho01-2024-200.dta (117,721 filas)
  otras sumarias en datos/, que no se usan: ninguna

CIFRA OFICIAL � base hogar (sumaria), ponderada con factor07 � mieperho
  [OK]    Pobreza monetaria nacional    27.58 %   referencia  27.6 %   diferencia -0.02 pp (tolerancia �0.1)
  [OK]    Pobreza urbana                24.81 %   referencia  24.8 %   diferencia +0.01 pp (tolerancia �0.1)
  [OK]    Pobreza rural                 39.30 %   referencia  39.3 %   diferencia +0.00 pp (tolerancia �0.1)
  [OK]    Residentes habituales       108,664     referencia 108,664
  [OK]    Unidades territoriales           25     referencia 25 (c�digos 01 a 25; Lima 15 y Callao 07 separados)

Integridad de la limpieza (esenciales)
  [OK]    la llave conglome es texto de largo fijo (6 caracteres): conserva los ceros iniciales
  [OK]    la llave vivienda es texto de largo fijo (3 caracteres): conserva los ceros iniciales
  [OK]    la llave hogar es texto de largo fijo (2 caracteres): conserva los ceros iniciales
  [OK]    llaves de hogar �nicas en la sumaria
  [OK]    llaves de persona �nicas en el m�dulo 02
  [OK]    la uni�n m:1 personas-hogares conserva las 108,664 filas, sin perder ni duplicar
  [OK]    todos los hogares de la sumaria tienen residentes en el m�dulo 02 (0 sin ellos)
  [OK]    factor07 positivo y sin vac�os en todos los hogares
  [OK]    facpob07 positivo y sin vac�os en todos los residentes
  [OK]    los 8 grupos de gasto del INEI suman gashog2d en todos los hogares (diferencia m�xima 0.014 soles)

Cifra secundaria � base persona (m�dulo 02 unido a la sumaria), ponderada con facpob07
  No es la cifra contra la que se valida: pondera personas, no hogares por su tama�o, y por eso
  difiere en una d�cima. Se usa solo para cortes por atributos de la persona (sexo, edad).
  Pobreza nacional 27.53 % � urbana 24.7 % � rural 39.4 % � extrema 5.50 %

Informativas (no detienen el proceso)
  [OK]    poblaci�n expandida: 34,482,700 con factor07 � mieperho y 34,147,768 con facpob07 (difieren menos de 1 %)
  [OK]    pobreza extrema base hogar 5.50 % (INEI 5.5 %)
  Sin ponderar, la pobreza de la muestra de hogares ser�a 20.22 %: por eso toda cifra se pondera.
  Var
… (recortado: 335 caracteres más)
```
</details>

**→ Edit**

```json
{
 "replace_all": false,
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\limpiando-enaho\\scripts\\limpiar.py",
 "old_string": "    # ---------------------------------------------------------------------------------------------------- leer\n    descomprimir(datos)\n    ruta_s = buscar_dta(datos, f\"sumaria-{args.anio}.dta\")\n    ruta_p = buscar_dta(datos, f\"enaho01-{args.anio}-200.dta\")",
 "new_string": "    # ---------------------------------------------------------------------------------------------------- leer\n    descomprimir(datos)\n    try:\n        ruta_s = buscar_dta(datos, f\"sumaria-{args.anio}.dta\")\n        ruta_p = buscar_dta(datos, f\"enaho01-{args.anio}-200.dta\")\n    except FileNotFoundError as e:\n        print(f\"ERROR: {e}\", file=sys.stderr)\n        return 1"
}
```

**→ Edit**

```json
{
 "replace_all": false,
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\limpiando-enaho\\scripts\\limpiar.py",
 "old_string": "def main() -> int:\n    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])",
 "new_string": "def main() -> int:\n    sys.stdout.reconfigure(encoding=\"utf-8\")         # la consola de Windows usa cp1252 y rompe las tildes\n    sys.stderr.reconfigure(encoding=\"utf-8\")\n    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])"
}
```

**→ Bash**

```json
{
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB && cp datos/966-Modulo34/966-Modulo34/sumaria-2024-12g.dta tarea_4/datos/966-Modulo34/966-Modulo34/ && cd tarea_4 && uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024 | sed -n '4,8p;37,40p'; echo \"exit=${PIPESTATUS[0]}\"; echo; column -s, -t < salidas/indicadores.csv | grep -E \"tipo_hogar_am |hogares_con_am|am_vive_solo|nacional|edad_persona\" | cut -c1-170",
 "description": "Copy 12g decoy, rerun cleaning, show research indicators",
 "timeout": 600000
}
```

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\limpiando-enaho\scripts\limpiar.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\limpiando-enaho\scripts\limpiar.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

<details><summary>← Resultado</summary>

```text
Archivos
  sumaria : datos/966-Modulo34/966-Modulo34/sumaria-2024.dta (33,691 hogares)
  miembros: datos/966-Modulo02/966-Modulo02/enaho01-2024-200.dta (117,721 filas)
  otras sumarias en datos/, que no se usan: sumaria-2024-12g.dta

  Variables del do-file del INEI que no trae la sumaria 2024: gru52hd2 (se toman como 0).

Resultado: 15 de 15 comprobaciones esenciales aprobadas.

exit=0

pobreza                 nacional              Perú                                          27.5795             % de personas                        factor07 × mieperho
pobreza_extrema         nacional              Perú                                          5.5045              % de personas                        factor07 × mieperho
pobreza                 tipo_hogar_am         Con adultos mayores y menores de 65            28.3717             % de personas                        factor07 × mieperho
pobreza_extrema         tipo_hogar_am         Con adultos mayores y menores de 65            5.3606              % de personas                        factor07 × mieperho
part_alimentos          tipo_hogar_am         Con adultos mayores y menores de 65            43.4124             % del gasto del hogar                factor07 × mieperho
gasto_pc_mensual        tipo_hogar_am         Con adultos mayores y menores de 65            770.1944            soles corrientes por persona al mes  factor07 × mieperho
hogares                 tipo_hogar_am         Con adultos mayores y menores de 65            18.87310028076172   % de hogares                         factor07            
personas                tipo_hogar_am         Con adultos mayores y menores de 65            21.468299865722656  % de personas                        factor07 × mieperho
rural                   tipo_hogar_am         Con adultos mayores y menores de 65            13.4301             % de personas                        factor07 × mieperho
pobreza                 tipo_hogar_am         Sin adultos mayores                            27.8543             % de personas                        factor07 × mieperho
pobreza_extrema         tipo_hogar_am         Sin adultos mayores                            5.5796              % de personas                        factor07 × mieperho
part_alimentos          tipo_hogar_am         Sin adultos mayores                            47.5286             % del gasto del hogar                factor07 × mieperho
gasto_pc_mensual        tipo_hogar_am         Sin adultos mayores     
… (recortado: 6,669 caracteres más)
```
</details>

**→ Edit**

```json
{
 "replace_all": false,
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\limpiando-enaho\\scripts\\limpiar.py",
 "old_string": "        filas.append({\"indicador\": indicador, \"corte\": corte, \"grupo\": grupo, \"valor\": round(valor, 4),",
 "new_string": "        filas.append({\"indicador\": indicador, \"corte\": corte, \"grupo\": grupo, \"valor\": round(float(valor), 4),"
}
```

**→ Bash**

```json
{
 "command": "SP=\"~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad\"; T=~/Documentos/GitHub/python-intermedio-QLAB/tarea_4\nrm -rf \"$SP/falla_a\" \"$SP/falla_b\"; mkdir -p \"$SP/falla_a/datos\" \"$SP/falla_a/salidas\" \"$SP/falla_b/datos\" \"$SP/falla_b/salidas\"\ncp \"$T/datos/966-Modulo34/966-Modulo34/sumaria-2024-12g.dta\" \"$T/datos/966-Modulo02/966-Modulo02/enaho01-2024-200.dta\" \"$SP/falla_a/datos/\"\ncp \"$T/datos/966-Modulo34/966-Modulo34/sumaria-2024-12g.dta\" \"$SP/falla_b/datos/sumaria-2024.dta\"; cp \"$T/datos/966-Modulo02/966-Modulo02/enaho01-2024-200.dta\" \"$SP/falla_b/datos/\"\ncd \"$T\"\necho \"===== A: solo está la sumaria 12g =====\"; uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --datos \"$SP/falla_a/datos\" --salidas \"$SP/falla_a/salidas\" ; echo \"exit=$?\"\necho; echo \"===== B: la 12g renombrada como sumaria-2024.dta =====\"; uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --datos \"$SP/falla_b/datos\" --salidas \"$SP/falla_b/salidas\" 2>&1 | grep -E \"FALLA|Resultado|ERROR|  - |Error|Traceback\" ; echo \"exit=${PIPESTATUS[0]}\"; ls \"$SP/falla_b/salidas\"",
 "description": "Test missing-file and wrong-sumaria failure paths",
 "timeout": 600000
}
```

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\limpiando-enaho\scripts\limpiar.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

<details><summary>← Resultado</summary>

```text
===== A: solo está la sumaria 12g =====
ERROR: No encontré sumaria-2024.dta dentro de ~\AppData\Local\Temp\claude\d8ae03e7fec106ea\29e7d7fa-8938-4d4b-8486-6ce14556e6c6\scratchpad\falla_a\datos. Archivos parecidos: ['sumaria-2024-12g.dta']. No uso otro en su lugar. Bajen los zip del INEI (966-Modulo34.zip y 966-Modulo02.zip) a datos/.
exit=1

===== B: la 12g renombrada como sumaria-2024.dta =====
ERROR: fallaron comprobaciones esenciales:
  - los 8 grupos de gasto del INEI suman gashog2d en todos los hogares (diferencia máxima 185990.641 soles)
  [FALLA] los 8 grupos de gasto del INEI suman gashog2d en todos los hogares (diferencia máxima 185990.641 soles)
Resultado: 14 de 15 comprobaciones esenciales aprobadas. PROCESO DETENIDO: no se guardaron las bases.
exit=2
validacion.txt
```
</details>

**→ Bash**

```json
{
 "command": "SP=\"~/AppData/Local/Temp/claude/d8ae03e7fec106ea/29e7d7fa-8938-4d4b-8486-6ce14556e6c6/scratchpad\"; sed -n '9,15p' \"$SP/falla_b/salidas/validacion.txt\"; cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && uv run python -c \"\nimport sys; sys.stdout.reconfigure(encoding='utf-8')\nimport pandas as pd\nr='datos/966-Modulo34/966-Modulo34/'\na=pd.read_stata(r+'sumaria-2024.dta',convert_categoricals=False); b=pd.read_stata(r+'sumaria-2024-12g.dta',convert_categoricals=False)\nprint('columnas:', a.shape[1], 'vs', b.shape[1], '| hogares:', len(a), 'vs', len(b))\nprint('solo en 12g:', sorted(set(b.columns)-set(a.columns))[:25])\nprint('solo en la normal:', sorted(set(a.columns)-set(b.columns))[:25])\nk=['conglome','vivienda','hogar']; m=a.merge(b,on=k,suffixes=('','_12g'))\nfor c in ['pobreza','factor07','mieperho','gashog2d','linea']:\n    if c+'_12g' in m: print(c, 'iguales en', round((m[c]==m[c+'_12g']).mean()*100,2), '% de hogares')\n\"",
 "description": "Compare normal and 12g sumaria files",
 "timeout": 300000
}
```

<details><summary>← Resultado</summary>

```text
CIFRA OFICIAL · base hogar (sumaria), ponderada con factor07 × mieperho
  [OK]    Pobreza monetaria nacional    27.58 %   referencia  27.6 %   diferencia -0.02 pp (tolerancia ±0.1)
  [OK]    Pobreza urbana                24.81 %   referencia  24.8 %   diferencia +0.01 pp (tolerancia ±0.1)
  [OK]    Pobreza rural                 39.30 %   referencia  39.3 %   diferencia +0.00 pp (tolerancia ±0.1)
  [OK]    Residentes habituales       108,664     referencia 108,664
  [OK]    Unidades territoriales           25     referencia 25 (códigos 01 a 25; Lima 15 y Callao 07 separados)

columnas: 163 vs 242 | hogares: 33691 vs 33691
solo en 12g: ['g07hd1', 'g07hd2', 'gru101hd', 'gru102hd', 'gru103hd', 'gru104hd', 'gru105hd', 'gru106hd', 'gru10hd', 'gru110hd', 'gru110hd2', 'gru111hd', 'gru111hd1', 'gru111hd2', 'gru112hd', 'gru112hd1', 'gru112hd2', 'gru113hd', 'gru113hd2', 'gru114hd', 'gru114hd2', 'gru115hd', 'gru115hd1', 'gru115hd2', 'gru116hd']
solo en la normal: ['g07hd', 'gru12hd1', 'gru12hd2', 'gru13hd1', 'gru13hd2', 'gru13hd3', 'gru13hd4', 'gru14hd1', 'gru14hd2', 'gru14hd3', 'gru14hd4', 'gru14hd5', 'gru14hd6', 'gru22hd2', 'gru23hd1', 'gru23hd2', 'gru23hd3', 'gru32hd1', 'gru32hd2', 'gru33hd1', 'gru33hd2', 'gru33hd3', 'gru42hd1', 'gru42hd2', 'gru43hd1']
pobreza iguales en 100.0 % de hogares
factor07 iguales en 100.0 % de hogares
mieperho iguales en 100.0 % de hogares
gashog2d iguales en 96.55 % de hogares
linea iguales en 100.0 % de hogares
```
</details>

**→ Bash**

```json
{
 "command": "mkdir -p .claude/skills/mapeando-enaho/referencias && cp ~/Documentos/GitHub/Data-Science-Python/sessions/16-skills-enaho/referencias/pobreza_departamento_2024.csv .claude/skills/mapeando-enaho/referencias/ && uv run python -c \"\nimport sys; sys.stdout.reconfigure(encoding='utf-8')\nimport geopandas as gpd\ng=gpd.read_file('datos/peru_departamental_simple.geojson'); print(g.columns.tolist(), len(g), g.crs); print(g.drop(columns='geometry').head(3).to_string())\"",
 "description": "Copy reference CSV and inspect GeoJSON columns",
 "timeout": 120000
}
```

<details><summary>← Resultado</summary>

```text
['NOMBDEP', 'COUNT', 'FIRST_IDDP', 'HECTARES', 'geometry'] 25 EPSG:4326
    NOMBDEP  COUNT FIRST_IDDP     HECTARES
0  AMAZONAS     84         01  3930646.567
1    ANCASH    166         02  3596224.600
2  APURIMAC     80         03  2111415.170
```
</details>

**→ Write**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\graficando-enaho\\scripts\\graficar.py",
 "content": "\"\"\"Gráficos de barras de la ENAHO a partir de las bases limpias (versión tarea_4).\n\n    uv run .claude/skills/graficando-enaho/scripts/graficar.py --corte area --indicador pobreza     # desde tarea_4/\n\nCortes de hogar (base hogar, factor07 × mieperho, la de la cifra oficial):\n  area, departamento, tipo_hogar (con o sin adultos mayores de 65+), tipo_hogar_area (tipo de hogar × área)\nCortes de persona (base persona, facpob07, cifra secundaria): sexo, edad\nIndicadores: pobreza, extrema, alimentos (participación de los alimentos en el gasto; solo cortes de hogar)\n\nGuarda figuras/<indicador>_<corte>_<año>.png y, al lado, el .csv con las cifras graficadas.\n\"\"\"\n\nimport argparse\nimport sys\nfrom pathlib import Path\n\nimport matplotlib\n\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\nimport numpy as np\nimport pandas as pd\n\n# Paleta de referencia de la skill dataviz (validada con validate_palette.js)\nSUPERFICIE, TINTA, TINTA_2, GRILLA = \"#fcfcfb\", \"#0b0b0b\", \"#52514e\", \"#e6e5e1\"\nSERIE = [\"#2a78d6\", \"#eb6834\", \"#1baf7a\"]                              # categórica, slots 1 a 3\nORDINAL = [\"#86b6ef\", \"#5598e7\", \"#2a78d6\", \"#1c5cab\", \"#104281\"]     # rampa ordinal azul (grupos de edad)\nBINS_EDAD = [-1, 14, 24, 44, 64, 200]\nETIQUETAS_EDAD = [\"0 a 14\", \"15 a 24\", \"25 a 44\", \"45 a 64\", \"65 a más\"]\nDEPARTAMENTOS = {\n    \"01\": \"Amazonas\", \"02\": \"Áncash\", \"03\": \"Apurímac\", \"04\": \"Arequipa\", \"05\": \"Ayacucho\", \"06\": \"Cajamarca\",\n    \"07\": \"Callao\", \"08\": \"Cusco\", \"09\": \"Huancavelica\", \"10\": \"Huá… (recortado; el archivo completo está en el repo)"
}
```

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\graficando-enaho\scripts\graficar.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

### Claude

Corro los cortes que pide el issue (área, sexo, departamento) más los de la pregunta (tipo de hogar, tipo de hogar × área, edad y la participación de alimentos).

**→ Bash**

```json
{
 "command": "for args in \"area pobreza\" \"sexo pobreza\" \"departamento pobreza\" \"edad pobreza\" \"tipo_hogar pobreza\" \"tipo_hogar alimentos\" \"tipo_hogar_area pobreza\" \"tipo_hogar_area alimentos\"; do set -- $args; echo \"===== $1 / $2\"; uv run .claude/skills/graficando-enaho/scripts/graficar.py --corte $1 --indicador $2 2>&1 | grep -v -E \"^  [0-9A-ZÁ][a-zé]+ ?[a-z]*: [0-9]\" | head -12; done; echo \"===== alimentos con corte de persona (debe rechazar)\"; uv run .claude/skills/graficando-enaho/scripts/graficar.py --corte sexo --indicador alimentos; echo \"exit=$?\"",
 "description": "Render all ENAHO chart cuts",
 "timeout": 600000
}
```

<details><summary>← Resultado</summary>

```text
===== area / pobreza
Pobreza monetaria según área de residencia, 2024 (% de personas)
  Base hogar ponderada con factor07 × mieperho (la de la cifra oficial)
  Perú: 27.6 %

Guardado en figuras/pobreza_area_2024.png (200 dpi) y las cifras en figuras/pobreza_area_2024.csv
===== sexo / pobreza
Pobreza monetaria según sexo, 2024 (% de personas)
  Base persona ponderada con facpob07 (secundaria: no es la base de la cifra oficial)
  Perú: 27.5 %

Guardado en figuras/pobreza_sexo_2024.png (200 dpi) y las cifras en figuras/pobreza_sexo_2024.csv
===== departamento / pobreza
Pobreza monetaria por departamento, 2024 (% de personas)
  Base hogar ponderada con factor07 × mieperho (la de la cifra oficial)
  Huánuco: 39.0 % (n = 1,244)
  La Libertad: 30.2 % (n = 1,509)
  Apurímac: 24.0 % (n = 913)
  Áncash: 22.8 % (n = 1,393)
  San Martín: 22.0 % (n = 1,347)
  Junín: 18.5 % (n = 1,506)
  Madre de Dios: 11.1 % (n = 603)
  Perú: 27.6 %

Guardado en figuras/pobreza_departamento_2024.png (200 dpi) y las cifras en figuras/pobreza_departamento_2024.csv
===== edad / pobreza
Pobreza monetaria según grupo de edad, 2024 (% de personas)
  Base persona ponderada con facpob07 (secundaria: no es la base de la cifra oficial)
  0 a 14: 37.5 % (n = 26,489)
  15 a 24: 26.3 % (n = 16,730)
  25 a 44: 27.2 % (n = 27,040)
  45 a 64: 21.2 % (n = 24,735)
  65 a más: 22.7 % (n = 13,670)
  Perú: 27.5 %

Guardado en figuras/pobreza_edad_2024.png (200 dpi) y las cifras en figuras/pobreza_edad_2024.csv
===== tipo_hogar / pobreza
Pobreza monetaria según presencia de adultos mayores (65+) en el hogar, 2024 (% de personas)
  Base hogar ponderada con factor07 × mieperho (la de la cifra oficial)
  Sin adultos mayores: 27.9 % (n = 23,292)
  Con adultos mayores y menores de 65: 28.4 % (n = 5,930)
  Solo adultos mayores: 20.3 % (n = 4,469)
  Perú: 27.6 %

Guardado en figuras/pobreza_tipo_hogar_2024.png (200 dpi) y las cifras en figuras/pobreza_tipo_hogar_2024.csv
===== tipo_hogar / alimentos
Participación de los alimentos en el gasto según presencia de adultos mayores (65+) en el hogar, 2024 (% del gasto del hogar)
  Base hogar ponderada con factor07 × mieperho (la de la cifra oficial)
  Sin adultos mayores: 47.5 % (n = 23,292)
  Con adultos mayores y menores de 65: 43.4 % (n = 5,930)
  Solo adultos mayores: 46.1 % (n = 4,469)
  Perú: 46.6 %

Guardado en figuras/alimentos_tipo_hogar_2024.png (200 dpi) y las cifras en figuras/alimentos_tipo_hogar_2024.csv
===== tipo_hogar_area / pobreza
Pobreza monetaria se
… (recortado: 1,496 caracteres más)
```
</details>

### Claude

Todas las cifras salen. Antes de dar los gráficos por buenos, los abro para revisar si hay etiquetas que chocan o textos cortados (el paso final de la skill de visualización).

**→ Read**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\figuras\\pobreza_area_2024.png"
}
```

<details><summary>← Resultado</summary>

```text
[imagen]
```
</details>

**→ Read**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\figuras\\pobreza_tipo_hogar_area_2024.png"
}
```

<details><summary>← Resultado</summary>

```text
[imagen]
```
</details>

**→ Read**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\figuras\\pobreza_departamento_2024.png"
}
```

<details><summary>← Resultado</summary>

```text
[imagen]
```
</details>

<details><summary>Contenido inyectado por Claude Code (skill o comando)</summary>

```text
[Image: original 1720x2920, displayed at 1178x2000. Multiply coordinates by 1.46 to map to original image.]
```
</details>

**→ Edit**

```json
{
 "replace_all": false,
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\graficando-enaho\\scripts\\graficar.py",
 "old_string": "def graficar(tabla, corte, indicador, anio, texto_base, nacional, destino):\n    nombre, _, unidad, _ = INDICADORES[indicador]\n    agrupado = corte == \"tipo_hogar_area\"\n    filas = tabla.index.get_level_values(0).unique() if agrupado else tabla.index\n    fig, eje = plt.subplots(figsize=(8.6, max(3.4, 0.5 * len(filas) * (1.6 if agrupado else 1) + 2.1)),\n                            facecolor=SUPERFICIE)\n    estilo(eje)\n    maximo = float(tabla.valor.max())\n    y = np.arange(len(filas))\n    if agrupado:\n        t = tabla.valor.unstack().reindex(filas)\n        for i, (area, color) in enumerate(zip([\"Urbano\", \"Rural\"], SERIE)):\n            pos = y + (i - 0.5) * 0.36\n            eje.barh(pos, t[area], height=0.32, color=color, label=area)\n            for yy, v in zip(pos, t[area]):\n                eje.text(v + maximo * 0.012, yy, f\"{v:.1f} %\", va=\"center\", fontsize=9, color=TINTA)\n        eje.legend(loc=\"lower right\", frameon=False, fontsize=9.5, labelcolor=TINTA)\n    else:\n        colores = ORDINAL if corte == \"edad\" else SERIE[0]\n        eje.barh(y, tabla.valor, height=0.52, color=colores)\n        for yy, v in zip(y, tabla.valor):\n            eje.text(v + maximo * 0.012, yy, f\"{v:.1f} %\", va=\"center\", fontsize=9.5, color=TINTA)\n    if nacional is not None:\n        eje.axvline(nacional, color=TINTA_2, linewidth=1)\n        eje.text(nacional, -0.75, f\" Perú {nacional:.1f} %\", color=TINTA_2, fontsize=8.5, va=\"bottom\")\n    eje.set_yticks(y, [str(f) for f in filas], color=TINTA, fontsiz… (recortado; el archivo completo está en el repo)",
 "new_string": "def graficar(tabla, corte, indicador, anio, texto_base, nacional, destino):\n    \"\"\"Maqueta en pulgadas: la barra tiene el mismo grosor con 2 o con 25 filas, y el texto se parte en líneas\n    en vez de salirse del borde.\"\"\"\n    nombre, _, unidad, _ = INDICADORES[indicador]\n    agrupado = corte == \"tipo_hogar_area\"\n    filas = list(tabla.index.get_level_values(0).unique() if agrupado else tabla.index)\n    n = int(tabla.n_muestral.sum())\n    titulo = textwrap.wrap(titular(tabla, corte, nombre), 76)\n    subtitulo = textwrap.wrap(f\"{nombre} {DESCRIPCION_CORTE[corte]}, Perú {anio} ({unidad})\", 100)\n    pie = textwrap.wrap(f\"Fuente: INEI, ENAHO {anio} (módulos 34 y 02). {texto_base}. n = {n:,} \"\n                        f\"{'hogares' if corte in CORTES_HOGAR else 'residentes'} en la muestra.\", 135)\n\n    ancho, fila_in = 8.6, (0.62 if agrupado else 0.40)\n    alto_plot = len(filas) * fila_in + 0.35\n    cabeza = 0.16 + 0.25 * len(titulo) + 0.20 * len(subtitulo) + 0.14\n    pies = 0.5 + 0.15 * len(pie) + 0.08\n    alto = alto_plot + cabeza + pies\n    izquierda = 0.3 + 0.074 * max(len(str(f)) for f in filas)\n    fig = plt.figure(figsize=(ancho, alto), facecolor=SUPERFICIE)\n    eje = fig.add_axes((izquierda / ancho, pies / alto, 1 - (izquierda + 0.45) / ancho, alto_plot / alto))\n    estilo(eje)\n\n    maximo = float(tabla.valor.max())\n    y = np.arange(len(filas))\n    caja = {\"facecolor\": SUPERFICIE, \"edgecolor\": \"none\", \"pad\": 0.6}       # la línea de referencia pasa detrás\n    if agrupado:\n  … (recortado; el archivo completo está en el repo)"
}
```

**→ Edit**

```json
{
 "replace_all": false,
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\graficando-enaho\\scripts\\graficar.py",
 "old_string": "import argparse\nimport sys\nfrom pathlib import Path",
 "new_string": "import argparse\nimport sys\nimport textwrap\nfrom pathlib import Path"
}
```

**→ Bash**

```json
{
 "command": "for args in \"area pobreza\" \"sexo pobreza\" \"departamento pobreza\" \"edad pobreza\" \"tipo_hogar pobreza\" \"tipo_hogar alimentos\" \"tipo_hogar_area pobreza\" \"tipo_hogar_area alimentos\"; do set -- $args; uv run .claude/skills/graficando-enaho/scripts/graficar.py --corte $1 --indicador $2 > /dev/null || echo \"FALLÓ $args\"; done; ls figuras/",
 "description": "Re-render all charts with new layout",
 "timeout": 600000
}
```

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\graficando-enaho\scripts\graficar.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\graficando-enaho\scripts\graficar.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

<details><summary>← Resultado</summary>

```text
alimentos_tipo_hogar_2024.csv
alimentos_tipo_hogar_2024.png
alimentos_tipo_hogar_area_2024.csv
alimentos_tipo_hogar_area_2024.png
pobreza_area_2024.csv
pobreza_area_2024.png
pobreza_departamento_2024.csv
pobreza_departamento_2024.png
pobreza_edad_2024.csv
pobreza_edad_2024.png
pobreza_sexo_2024.csv
pobreza_sexo_2024.png
pobreza_tipo_hogar_2024.csv
pobreza_tipo_hogar_2024.png
pobreza_tipo_hogar_area_2024.csv
pobreza_tipo_hogar_area_2024.png
```
</details>

**→ Read**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\figuras\\pobreza_area_2024.png"
}
```

<details><summary>← Resultado</summary>

```text
[imagen]
```
</details>

**→ Read**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\figuras\\alimentos_tipo_hogar_area_2024.png"
}
```

<details><summary>← Resultado</summary>

```text
[imagen]
```
</details>

**→ Read**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\figuras\\pobreza_edad_2024.png"
}
```

<details><summary>← Resultado</summary>

```text
[imagen]
```
</details>

**→ Edit**

```json
{
 "replace_all": false,
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\graficando-enaho\\scripts\\graficar.py",
 "old_string": "    cabeza = 0.16 + 0.25 * len(titulo) + 0.20 * len(subtitulo) + 0.14",
 "new_string": "    cabeza = 0.16 + 0.25 * len(titulo) + 0.20 * len(subtitulo) + 0.14 + (0.3 if agrupado else 0)   # fila de leyenda"
}
```

**→ Edit**

```json
{
 "replace_all": false,
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\graficando-enaho\\scripts\\graficar.py",
 "old_string": "        eje.legend(loc=\"lower right\", frameon=False, fontsize=9.5, labelcolor=TINTA)",
 "new_string": "        eje.legend(loc=\"lower left\", bbox_to_anchor=(0, 1.0), ncol=2, frameon=False, fontsize=9.5,\n                   labelcolor=TINTA, handlelength=1.2, borderaxespad=0.2)   # en una fila sobre el gráfico"
}
```

**→ Bash**

```json
{
 "command": "for i in pobreza alimentos; do uv run .claude/skills/graficando-enaho/scripts/graficar.py --corte tipo_hogar_area --indicador $i > /dev/null; done; echo ok",
 "description": "Re-render grouped charts with legend above",
 "timeout": 300000
}
```

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\graficando-enaho\scripts\graficar.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\graficando-enaho\scripts\graficar.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

<details><summary>← Resultado</summary>

```text
ok
```
</details>

**→ Read**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\figuras\\alimentos_tipo_hogar_area_2024.png"
}
```

<details><summary>← Resultado</summary>

```text
[imagen]
```
</details>

### Claude

Limpio. Ahora `mapear.py`: base hogar, unión por código, comparación esencial contra la referencia de la sesión 16 y rampa secuencial azul desde 0.

**→ Write**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\mapeando-enaho\\scripts\\mapear.py",
 "content": "\"\"\"Mapa coroplético de la ENAHO por departamento (versión tarea_4).\n\n    uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza       # desde tarea_4/\n\nIndicadores, todos con la base hogar ponderada con factor07 × mieperho (la de la cifra oficial):\n  pobreza                  pobreza monetaria (% de personas); se compara con la referencia de la sesión 16\n  pobreza_hogares_am       pobreza monetaria de las personas que viven en hogares con adultos mayores (65+)\n  personas_en_hogares_am   % de personas que viven en un hogar con al menos un adulto mayor\n\nUne por código, nunca por nombre: ubigeo[:2] de la base contra FIRST_IDDP del GeoJSON. Exige 25 unidades, todas\ncon dato, con Lima (15) y Callao (07) separados. Guarda mapas/<indicador>_departamento_<año>.png y su .csv.\n\"\"\"\n\nimport argparse\nimport sys\nimport textwrap\nfrom pathlib import Path\n\nimport geopandas as gpd\nimport matplotlib\n\nmatplotlib.use(\"Agg\")\nimport matplotlib.pyplot as plt\nimport pandas as pd\nfrom matplotlib.colors import LinearSegmentedColormap\n\nGEOJSON_URL = (\"https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/\"\n               \"sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson\")\nN_DEPARTAMENTOS = 25\nTOLERANCIA_REFERENCIA = 0.1          # puntos: la referencia viene redondeada a un decimal\nN_MINIMO = 100                       # hogares en la muestra por departamento; por debajo, se avisa\nSUPERFICIE, TINTA, TINTA_2 = \"#fcfcfb\", \"#0b0b0b\", \"#52514e\"\nAZUL = Linear… (recortado; el archivo completo está en el repo)"
}
```

**→ Bash**

```json
{
 "command": "for i in pobreza pobreza_hogares_am personas_en_hogares_am; do echo \"===== $i\"; uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador $i; echo \"exit=$?\"; done",
 "description": "Render the three department maps",
 "timeout": 600000
}
```

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\mapeando-enaho\scripts\mapear.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

<details><summary>← Resultado</summary>

```text
===== pobreza
Pobreza monetaria por departamento, 2024 (base hogar, factor07 × mieperho)
  25 unidades territoriales unidas por código, ninguna sin dato
  más alto : Cajamarca 45.0 %, Loreto 43.0 %, Puno 39.9 %
  más bajo : Ica 6.0 %, Moquegua 11.0 %, Madre De Dios 11.1 %
  contra la referencia de la sesión 16: diferencia máxima 0.049 puntos, mediana 0.030 (tolerancia 0.1)

Guardado en mapas/pobreza_departamento_2024.png (200 dpi) y las cifras en mapas/pobreza_departamento_2024.csv
exit=0
===== pobreza_hogares_am
Pobreza monetaria en hogares con adultos mayores (65+) por departamento, 2024 (base hogar, factor07 × mieperho)
  25 unidades territoriales unidas por código, ninguna sin dato
  más alto : Cajamarca 49.4 %, Loreto 43.8 %, Puno 43.1 %
  más bajo : Ica 2.8 %, Madre De Dios 3.8 %, Arequipa 13.5 %

Guardado en mapas/pobreza_hogares_am_departamento_2024.png (200 dpi) y las cifras en mapas/pobreza_hogares_am_departamento_2024.csv
exit=0
===== personas_en_hogares_am
Personas que viven en un hogar con adultos mayores (65+) por departamento, 2024 (base hogar, factor07 × mieperho)
  25 unidades territoriales unidas por código, ninguna sin dato
  más alto : Callao 33.9 %, Lambayeque 31.5 %, Lima 31.3 %
  más bajo : Madre De Dios 10.8 %, Ucayali 16.6 %, Pasco 17.7 %

Guardado en mapas/personas_en_hogares_am_departamento_2024.png (200 dpi) y las cifras en mapas/personas_en_hogares_am_departamento_2024.csv
exit=0
```
</details>

**→ Bash**

```json
{
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills/mapeando-enaho/scripts && python - <<'EOF'\nfrom pathlib import Path\np = Path(\"mapear.py\"); s = p.read_text(encoding=\"utf-8\")\ns = s.replace('''INDICADORES = {   # título, unidad de la leyenda, filtro de hogares, condición''', '''DEPARTAMENTOS = {   # solo para rotular: la unión es por código\n    \"01\": \"Amazonas\", \"02\": \"Áncash\", \"03\": \"Apurímac\", \"04\": \"Arequipa\", \"05\": \"Ayacucho\", \"06\": \"Cajamarca\",\n    \"07\": \"Callao\", \"08\": \"Cusco\", \"09\": \"Huancavelica\", \"10\": \"Huánuco\", \"11\": \"Ica\", \"12\": \"Junín\",\n    \"13\": \"La Libertad\", \"14\": \"Lambayeque\", \"15\": \"Lima\", \"16\": \"Loreto\", \"17\": \"Madre de Dios\", \"18\": \"Moquegua\",\n    \"19\": \"Pasco\", \"20\": \"Piura\", \"21\": \"Puno\", \"22\": \"San Martín\", \"23\": \"Tacna\", \"24\": \"Tumbes\", \"25\": \"Ucayali\",\n}\nINDICADORES = {   # título y unidad de la leyenda''')\ns = s.replace('mapa[\"etiqueta\"] = mapa.NOMBDEP.str.title()', 'mapa[\"etiqueta\"] = mapa.ccdd.map(DEPARTAMENTOS)')\np.write_text(s, encoding=\"utf-8\")\nprint(s.count(\"DEPARTAMENTOS\"))\nEOF\ncd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && for i in pobreza pobreza_hogares_am personas_en_hogares_am; do uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador $i | sed -n '3,4p'; done",
 "description": "Use accented department names as labels",
 "timeout": 600000
}
```

<details><summary>← Resultado</summary>

```text
6
  más alto : Cajamarca 45.0 %, Loreto 43.0 %, Puno 39.9 %
  más bajo : Ica 6.0 %, Moquegua 11.0 %, Madre de Dios 11.1 %
  más alto : Cajamarca 49.4 %, Loreto 43.8 %, Puno 43.1 %
  más bajo : Ica 2.8 %, Madre de Dios 3.8 %, Arequipa 13.5 %
  más alto : Callao 33.9 %, Lambayeque 31.5 %, Lima 31.3 %
  más bajo : Madre de Dios 10.8 %, Ucayali 16.6 %, Pasco 17.7 %
```
</details>

**→ Read**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\mapas\\pobreza_departamento_2024.png"
}
```

<details><summary>← Resultado</summary>

```text
[imagen]
```
</details>

**→ Write**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\limpiando-enaho\\SKILL.md",
 "content": "---\nname: limpiando-enaho\ndescription: Limpia y valida los módulos 34 (sumaria) y 02 (miembros) de la ENAHO del INEI y arma las bases de hogares y de personas con pobreza monetaria, departamento, área urbana o rural, gasto en alimentos y presencia de adultos mayores (65+), ponderadas con factor07 × mieperho. Úsala cuando pidan limpiar, unir, validar o analizar la ENAHO, o calcular pobreza, pobreza extrema, gasto en alimentos u hogares con adultos mayores por departamento, área, sexo o edad, y siempre antes de graficar o mapear si no existe la base procesada. Versión de la tarea 4.\nargument-hint: [año]\n---\n\n# Limpiar la ENAHO · versión tarea_4\n\n> **Cuál versión es esta.** El repo tiene dos juegos de skills con el mismo nombre: los de la sesión 16, en\n> `.claude/skills/` de la raíz, y estos, en `tarea_4/.claude/skills/`. Claude Code carga los del directorio desde\n> donde arranca, así que **para la tarea 4 se arranca `claude` dentro de `tarea_4/`**, que es también donde está\n> `.mcp.json`.\n>\n> **En qué difieren.** Aquí la cifra oficial sale de la **base hogar ponderada con `factor07 × mieperho`**, que es\n> la que publica el INEI y la que pide el issue. La base persona con `facpob07` (la que usan los gráficos y el mapa\n> de la sesión 16) queda como cifra secundaria, solo para cortes por atributos de la persona (sexo, edad). Las dos\n> son correctas y difieren en una décima: son bases distintas, no un error.\n\n1. Si `datos/` no tiene `sumaria-2024.dta` y `enaho01-2024-200.dta`, pide… (recortado; el archivo completo está en el repo)"
}
```

**→ Write**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\limpiando-enaho\\reference.md",
 "content": "# Variables de las bases limpias de la ENAHO · versión tarea_4\n\nDos bases, una por unidad de análisis. Elige la del corte: **hogar** para todo lo que describe al hogar (pobreza\noficial, área, departamento, tipo de hogar, gasto) y **persona** solo para atributos de la persona (sexo, edad).\n\n## `salidas/hogares_<año>.parquet` · una fila por hogar (33,691 en 2024)\n\n| Columna | Qué es |\n|---|---|\n| `conglome`, `vivienda`, `hogar` | Llaves del hogar, **texto** de largo fijo (`conglome` = «015009»; como número perdería el cero). |\n| `ubigeo` | Seis dígitos como texto: departamento (2) + provincia (2) + distrito (2). |\n| `departamento` | `ubigeo[:2]`. Lima es `15` y Callao `07`, separados. Se une al mapa con `FIRST_IDDP`. |\n| `estrato`, `urbano` | Estrato 1 a 5 urbano, 6 a 8 rural; `urbano = estrato <= 5`. |\n| `dominio` | 1 a 8. Lima Metropolitana es `dominio == 8`. |\n| `mieperho` | Miembros del hogar según la sumaria. |\n| `factor07` | Factor de expansión del hogar. Úsalo solo para cifras **de hogares** («% de hogares»). |\n| `peso_personas` | `factor07 × mieperho`. **El peso de la cifra oficial** («% de personas»). |\n| `pobreza` | 1 pobre extremo · 2 pobre no extremo · 3 no pobre. **Códigos, no una escala**: nunca promedies. |\n| `pobre`, `pobre_extremo` | `pobreza <= 2` y `pobreza == 1`. |\n| `n_residentes` | Residentes habituales del hogar en el módulo 02. Coincide con `mieperho` en la gran mayoría de hogares, no en todos. |\n| `n_am`, `n_menores_18` | Residentes de 65 años o más y m… (recortado; el archivo completo está en el repo)"
}
```

**→ Write**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\graficando-enaho\\SKILL.md",
 "content": "---\nname: graficando-enaho\ndescription: Hace gráficos de barras ponderados de la ENAHO 2024 del INEI - pobreza monetaria, pobreza extrema o participación de los alimentos en el gasto - por área urbana o rural, departamento, presencia de adultos mayores (65+) en el hogar, sexo o grupo de edad. Úsala cuando pidan graficar, comparar o visualizar la pobreza o el gasto de los hogares de la ENAHO. Si no existe la base procesada, usa antes limpiando-enaho. Versión de la tarea 4.\nargument-hint: [area|departamento|tipo_hogar|tipo_hogar_area|sexo|edad]\n---\n\n# Graficar la ENAHO · versión tarea_4\n\n> **Cuál versión es esta.** Hay otra `graficando-enaho` en la raíz del repo (sesión 16) que pondera todo con\n> `facpob07`. Esta usa la **base hogar con `factor07 × mieperho`**, la de la cifra oficial, para los cortes de hogar,\n> y `facpob07` solo para sexo y edad, rotulado en el pie del gráfico. Para usar esta versión se arranca `claude`\n> dentro de `tarea_4/`.\n\n1. **Si no existe `salidas/hogares_2024.parquet` (o `salidas/personas_2024.parquet` para sexo y edad), usa primero\n   la skill `limpiando-enaho`** y espera a que termine sin error. Sin base validada no hay gráfico. El script\n   también lo detecta: termina con código 3 y dice qué correr.\n\n2. Elige el corte y el indicador según el pedido. **Solo estos valores exactos**; `$0` trae texto libre, nunca lo\n   pases tal cual al script.\n\n   | Si piden… | `--corte` | Base y peso |\n   |---|---|---|\n   | urbano y rural, área de residencia | `area` … (recortado; el archivo completo está en el repo)"
}
```

**→ Write**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\.claude\\skills\\mapeando-enaho\\SKILL.md",
 "content": "---\nname: mapeando-enaho\ndescription: Hace un mapa coroplético por departamento del Perú con la ENAHO 2024 del INEI - pobreza monetaria, pobreza en hogares con adultos mayores (65+) o porcentaje de personas que viven con adultos mayores - uniendo la base limpia con los límites departamentales por código de ubigeo. Úsala cuando pidan un mapa, un coropleta o visualizar la pobreza del INEI por departamento, región o territorio. Si no existe la base procesada, usa antes limpiando-enaho. Versión de la tarea 4.\nargument-hint: [pobreza|pobreza_hogares_am|personas_en_hogares_am]\n---\n\n# Mapear la ENAHO · versión tarea_4\n\n> **Cuál versión es esta.** Hay otra `mapeando-enaho` en la raíz del repo (sesión 16) que pondera con `facpob07`.\n> Esta pondera con **`factor07 × mieperho`** (base hogar), que es la base con la que se hizo la tabla de referencia\n> de la sesión 16 y la que publica el INEI. Para usar esta versión se arranca `claude` dentro de `tarea_4/`.\n\n1. **Si no existe `salidas/hogares_2024.parquet`, usa primero la skill `limpiando-enaho`** y espera a que termine\n   sin error. Sin base validada no hay mapa. El script también lo detecta: termina con código 3 y dice qué correr.\n\n2. Elige el indicador. **Solo estos valores exactos**; `$0` trae texto libre, nunca lo pases tal cual al script.\n\n   | Si piden… | `--indicador` |\n   |---|---|\n   | pobreza monetaria por departamento (por defecto) | `pobreza` |\n   | pobreza de los hogares con adultos mayores | `pobreza_hogares_am` |\n   | dónd… (recortado; el archivo completo está en el repo)"
}
```

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\limpiando-enaho\SKILL.md has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\limpiando-enaho\reference.md has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\graficando-enaho\SKILL.md has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\mapeando-enaho\SKILL.md has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

**→ Bash**

```json
{
 "command": "timeout 120 claude -p \"di ok\" --model haiku --output-format stream-json --verbose --no-session-persistence --strict-mcp-config 2>/dev/null | head -1 | python -c \"\nimport sys,json; sys.stdout.reconfigure(encoding='utf-8'); d=json.loads(sys.stdin.readline()); print('claves init:', sorted(d)); print('skills:', d.get('skills')); print('cwd:', d.get('cwd')[-40:])\"; echo \"--- desde la raíz ---\"; cd .. && timeout 120 claude -p \"di ok\" --model haiku --output-format stream-json --verbose --no-session-persistence --strict-mcp-config 2>/dev/null | head -1 | python -c \"\nimport sys,json; d=json.loads(sys.stdin.readline()); print('skills:', d.get('skills'))\"",
 "description": "Check which skills load from tarea_4 vs repo root",
 "timeout": 300000
}
```

<details><summary>← Resultado</summary>

```text
claves init: ['additional_directories', 'agents', 'analytics_disabled', 'apiKeySource', 'capabilities', 'claude_code_version', 'cwd', 'fast_mode_disabled_reason', 'fast_mode_state', 'mcp_servers', 'memory_paths', 'messaging_socket_path', 'model', 'original_cwd', 'output_style', 'per_turn_effort_active', 'permissionMode', 'plugins', 'powershell_path', 'product_feedback_disabled', 'scratchpad_path', 'session_id', 'skills', 'slash_commands', 'startup_timing', 'subtype', 'terminal_slash_commands', 'tools', 'type', 'ultrathink_available', 'ultrathink_typed_raises', 'uuid', 'view_mode']
skills: ['graficando-enaho', 'limpiando-enaho', 'mapeando-enaho', 'design', 'slides', 'design-sync', 'dataviz', 'artifact-diagramming', 'artifact-capabilities', 'update-config', 'verify', 'debug', 'code-review', 'simplify', 'batch', 'fewer-permission-prompts', 'doctor', 'loop', 'schedule', 'claude-api', 'run', 'run-skill-generator', 'plugin-authoring', 'anthropic-skills:built-in-browser', 'anthropic-skills:caveman', 'anthropic-skills:chrome-browser', 'anthropic-skills:computer-use', 'anthropic-skills:deep-research', 'anthropic-skills:docs', 'anthropic-skills:docx', 'anthropic-skills:google-workspace', 'anthropic-skills:grill-me', 'anthropic-skills:handoff', 'anthropic-skills:humanizer', 'anthropic-skills:import-memory', 'anthropic-skills:morning', 'anthropic-skills:pdf', 'anthropic-skills:pptx', 'anthropic-skills:write-a-skill', 'anthropic-skills:xlsx']
cwd: os\GitHub\python-intermedio-QLAB\tarea_4
--- desde la raíz ---
skills: ['graficando-enaho', 'limpiando-enaho', 'mapeando-enaho', 'design', 'slides', 'design-sync', 'dataviz', 'artifact-diagramming', 'artifact-capabilities', 'update-config', 'verify', 'debug', 'code-review', 'simplify', 'batch', 'fewer-permission-prompts', 'doctor', 'loop', 'schedule', 'claude-api', 'run', 'run-skill-generator', 'plugin-authoring', 'anthropic-skills:built-in-browser', 'anthropic-skills:caveman', 'anthropic-skills:chrome-browser', 'anthropic-skills:computer-use', 'anthropic-skills:deep-research', 'anthropic-skills:docs', 'anthropic-skills:docx', 'anthropic-skills:google-workspace', 'anthropic-skills:grill-me', 'anthropic-skills:handoff', 'anthropic-skills:humanizer', 'anthropic-skills:import-memory', 'anthropic-skills:morning', 'anthropic-skills:pdf', 'anthropic-skills:pptx', 'anthropic-skills:write-a-skill', 'anthropic-skills:xlsx']
```
</details>

**→ Write**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\evidencias_ia\\traza.py",
 "content": "\"\"\"Corre `claude -p` en una sesión nueva y pasa su traza (stream-json) a Markdown legible.\n\nLo usan los scripts de evidencias_ia/*/ para dejar constancia de qué herramientas, skills y servidores MCP usó\nClaude, con qué argumentos, qué recibió y qué respondió. Las rutas de la carpeta personal se reemplazan por «~».\n\"\"\"\nimport json\nimport shutil\nimport subprocess\nimport time\nfrom pathlib import Path\n\nTAREA = Path(__file__).resolve().parents[1]\nRECORTE = 2500\n\n\ndef ejecutar(prompt: str, opciones: list[str], modelo: str, cwd: Path = TAREA,\n             timeout: int = 1800) -> tuple[list[dict], float]:\n    cmd = [shutil.which(\"claude\"), \"-p\", prompt, \"--model\", modelo, \"--output-format\", \"stream-json\", \"--verbose\",\n           \"--no-session-persistence\", *opciones]\n    t = time.time()\n    proc = subprocess.run(cmd, capture_output=True, text=True, encoding=\"utf-8\", cwd=cwd, timeout=timeout)\n    eventos = [json.loads(l) for l in proc.stdout.splitlines() if l.strip().startswith(\"{\")]\n    if proc.returncode:\n        eventos.append({\"type\": \"error\", \"stderr\": proc.stderr[-2000:]})\n    return eventos, round(time.time() - t, 1)\n\n\ndef anonimizar(texto: str) -> str:\n    casa = str(Path.home())\n    for forma in (casa, casa.replace(\"\\\\\", \"/\"), casa.replace(\"\\\\\", \"\\\\\\\\\"), \"/c/Users/\" + Path.home().name):\n        texto = texto.replace(forma, \"~\")\n    return texto\n\n\ndef _bloque(texto: str, lenguaje: str = \"text\") -> list[str]:\n    texto = texto if len(texto) < RECORTE else texto[:RECORTE] + \"\\n…… (recortado; el archivo completo está en el repo)"
}
```

**→ Write**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\evidencias_ia\\skills\\probar_skills.py",
 "content": "\"\"\"Prueba las tres skills de la ENAHO dentro de Claude Code: activación por lenguaje natural, coordinación e\ninvocación directa.\n\n    uv run evidencias_ia/skills/probar_skills.py                       # desde tarea_4/, todos los casos con Sonnet\n    uv run evidencias_ia/skills/probar_skills.py haiku coordinacion    # un modelo y algunos casos\n\nCada caso es una sesión nueva de `claude -p` sin servidores MCP y con solo las herramientas que las skills necesitan\n(Skill, Bash, Read, Glob). El caso «coordinacion» borra antes las bases procesadas de salidas/, para comprobar que\nClaude corre limpiando-enaho antes de mapeando-enaho. El caso «desde_la_raiz» arranca en la raíz del repo para\nmostrar que ahí se cargan las skills de la sesión 16, no las de tarea_4. Guarda una traza Markdown por caso.\n\"\"\"\nimport sys\nfrom pathlib import Path\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\nfrom traza import TAREA, a_markdown, ejecutar, usadas  # noqa: E402\n\nSALIDA = Path(__file__).parent\nHERRAMIENTAS = [\"--strict-mcp-config\", \"--tools\", \"Skill,Bash,Read,Glob\", \"--allowedTools\", \"Skill\", \"Bash\", \"Read\",\n                \"Glob\"]\nPREGUNTA_VERSION = (\"Usa la skill limpiando-enaho, pero no ejecutes ningún comando. Solo dime la ruta de «Base \"\n                    \"directory» que te da la skill y con qué factor de expansión dice que se calcula la cifra oficial.\")\nCASOS = {   # nombre: (pedido, directorio de trabajo, borrar las bases antes)\n    \"coordinacion\": (\"Haz un mapa de la pobreza… (recortado; el archivo completo está en el repo)"
}
```

<details><summary>← Resultado</summary>

```text
File created successfully at: ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\evidencias_ia\traza.py (file state is current in your context — no need to Read it back)
```
</details>

<details><summary>← Resultado</summary>

```text
File created successfully at: ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\evidencias_ia\skills\probar_skills.py (file state is current in your context — no need to Read it back)
```
</details>

### Claude

Corro primero los dos casos de versión con Haiku, que son baratos, para confirmar qué skill carga cada directorio.

**→ Bash**

```json
{
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && uv run evidencias_ia/skills/probar_skills.py haiku desde_tarea_4 desde_la_raiz && for c in desde_tarea_4 desde_la_raiz; do echo \"===== $c\"; grep -m1 -i \"Base directory\" evidencias_ia/skills/claude_code_$c.md; awk '/^### Claude/{f=1} f' evidencias_ia/skills/claude_code_$c.md | grep -v '^$' | head -8 | cut -c1-300; done",
 "description": "Check which skill version loads per directory",
 "timeout": 600000
}
```

<details><summary>← Resultado</summary>

```text
desde_tarea_4: 4.9 s, ['Skill(limpiando-enaho)'] -> claude_code_desde_tarea_4.md
desde_la_raiz: 6.7 s, ['Skill(limpiando-enaho)'] -> claude_code_desde_la_raiz.md
===== desde_tarea_4
Usa la skill limpiando-enaho, pero no ejecutes ningún comando. Solo dime la ruta de «Base directory» que te da la skill y con qué factor de expansión dice que se calcula la cifra oficial.
### Claude
**Base directory:** `~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\limpiando-enaho`
**Factor de expansión de la cifra oficial:** `factor07 × mieperho` sobre la base hogar. Es la que publica el INEI y la que pide el issue. La base persona con `facpob07` queda como cifra secundaria, solo para cortes por atributos de la persona, como sexo o edad.
No ejecuté ningún comando.
## Resultado
- Herramientas, en orden: Skill(limpiando-enaho)
- Turnos: 3
- Segundos: 4.9
===== desde_la_raiz
Usa la skill limpiando-enaho, pero no ejecutes ningún comando. Solo dime la ruta de «Base directory» que te da la skill y con qué factor de expansión dice que se calcula la cifra oficial.
### Claude
**Base directory:** `~\Documentos\GitHub\python-intermedio-QLAB\.claude\skills\limpiando-enaho`
**Factor de expansión de la cifra oficial:** la skill dice que el 27.6 % del INEI sale de la sumaria, ponderando hogares con `factor07 × mieperho`. Con ese factor, la pobreza monetaria da 27.58 %.
La base de personas, ponderada con `facpob07`, da 27.53 %. La skill indica que ambas son correctas, porque la sumaria pondera hogares por su tamaño y la de personas pondera personas. Además, el paso 4 pide ponderar toda cifra con `facpob07`, así que la skill mezcla dos factores; si necesitas cuad
## Resultado
- Herramientas, en orden: Skill(limpiando-enaho)
- Turnos: 3
- Segundos: 6.7
```
</details>

**→ Bash**

```json
{
 "command": "uv run evidencias_ia/skills/probar_skills.py sonnet coordinacion lenguaje_natural invocacion_directa; ls salidas/",
 "description": "Run skill coordination, natural language, direct invocation",
 "timeout": 1800000
}
```

<details><summary>← Resultado</summary>

```text
coordinacion: 17.6 s, ['Skill(mapeando-enaho)', 'Bash', 'Skill(limpiando-enaho)', 'Bash', 'Bash'] -> claude_code_coordinacion.md
lenguaje_natural: 10.9 s, ['Skill(graficando-enaho)', 'Bash'] -> claude_code_lenguaje_natural.md
invocacion_directa: 16.4 s, ['Glob', 'Bash', 'Bash', 'Bash', 'Bash'] -> claude_code_invocacion_directa.md
hogares_2024.parquet
indicadores.csv
personas_2024.parquet
validacion.txt
```
</details>

**→ Bash**

```json
{
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/evidencias_ia/skills && for c in coordinacion lenguaje_natural invocacion_directa; do echo \"=================== $c\"; grep -A4 -E \"^### → Llama a .(Bash|Glob)\" claude_code_$c.md | grep -E '\"command\"|\"pattern\"' | cut -c1-220; grep -m2 -E \"^No existe|Base directory|código 3|exit code\" claude_code_$c.md | cut -c1-200; awk '/^### Claude/{f=1} f' claude_code_$c.md | grep -v '^$' | tail -14 | cut -c1-260; done",
 "description": "Review commands and answers in skill traces"
}
```

<details><summary>← Resultado</summary>

```text
=================== coordinacion
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && ls salidas; uv run ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza --anio 2024"
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && ls datos; uv run ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024"
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && uv run ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza --anio 2024"
Base directory for this skill: ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\mapeando-enaho
   sin error. Sin base validada no hay mapa. El script también lo detecta: termina con código 3 y dice qué correr.
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
=================== lenguaje_natural
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && ls salidas && uv run ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills/graficando-enaho/scripts/graficar.py --corte tipo_hogar_area --
Base directory for this skill: ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\graficando-enaho
   también lo detecta: termina con código 3 y dice qué correr.
| Sin adultos mayores | 44.8 % | 58.6 
… (recortado: 2,438 caracteres más)
```
</details>

**→ Bash**

```json
{
 "command": "grep -n -m3 \"No existe\\|Exit code\\|exit code 3\" claude_code_coordinacion.md | cut -c1-250; grep -c \"Users.usuario\\|renatogates\\|@gmail\" *.md",
 "description": "Confirm missing-base detection and scan for personal data"
}
```

<details><summary>← Resultado</summary>

```text
63:Exit code 3
66:No existe ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\salidas\hogares_2024.parquet. Usa primero la skill limpiando-enaho: uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024
claude_code_coordinacion.md:0
claude_code_desde_la_raiz.md:0
claude_code_desde_tarea_4.md:0
claude_code_invocacion_directa.md:0
claude_code_lenguaje_natural.md:0
```
</details>

**→ Write**

```json
{
 "file_path": "~\\Documentos\\GitHub\\python-intermedio-QLAB\\tarea_4\\evidencias_ia\\mcp\\probar_en_claude_code.py",
 "content": "\"\"\"Prueba el MCP bcrp dentro de Claude Code: una herramienta, el recurso con @ y el prompt con /.\n\n    uv run evidencias_ia/mcp/probar_en_claude_code.py                     # desde tarea_4/, los tres casos con Haiku\n    uv run evidencias_ia/mcp/probar_en_claude_code.py haiku recurso       # un modelo y algunos casos\n\nCada caso es una sesión nueva de `claude -p` que solo tiene el servidor bcrp de .mcp.json (sin terminal, sin\narchivos, sin web). Guarda la traza de cada caso en Markdown junto a este script: qué herramientas llamó Claude,\ncon qué argumentos, qué recibió y qué respondió.\n\nEn modo -p la mención @bcrp:bcrp://... no adjunta el recurso por sí sola: Claude lo lee con las herramientas\ninternas ListMcpResourcesTool y ReadMcpResourceTool, que `--tools \"\"` apaga. Por eso el caso «recurso» las habilita\n(claude_code_recurso_sin_lector_de_recursos.md es el primer intento, sin ellas).\n\"\"\"\nimport sys\nfrom pathlib import Path\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\nfrom traza import TAREA, a_markdown, ejecutar, usadas  # noqa: E402\n\nSALIDA = Path(__file__).parent\nLECTOR_DE_RECURSOS = [\"ListMcpResourcesTool\", \"ReadMcpResourceTool\"]\nCASOS = {   # nombre: (pedido, herramientas internas de Claude Code que se habilitan además del MCP)\n    \"herramientas\": (\"¿Estuvo la inflación de alimentos y bebidas de Lima Metropolitana (var% 12 meses) por encima \"\n                     \"de la inflación total entre enero de 2021 y octubre de 2026? Dime en cuántos meses y con qué… (recortado; el archivo completo está en el repo)"
}
```

**→ Bash**

```json
{
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && uv run evidencias_ia/mcp/probar_en_claude_code.py haiku && grep -h -A3 \"^## Resultado\" evidencias_ia/mcp/claude_code_{herramientas,recurso,prompt}.md | grep Herramientas",
 "description": "Rerun MCP evidence cases with shared tracer",
 "timeout": 900000
}
```

<details><summary>← Resultado</summary>

```text
The file ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\evidencias_ia\mcp\probar_en_claude_code.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>

<details><summary>← Resultado</summary>

```text
herramientas: 21.1 s, ['mcp__bcrp__buscar_series', 'mcp__bcrp__buscar_series', 'mcp__bcrp__buscar_series', 'mcp__bcrp__buscar_series', 'mcp__bcrp__correlacion', 'mcp__bcrp__serie', 'mcp__bcrp__serie'] -> claude_code_herramientas.md
recurso: 8.6 s, ['ReadMcpResourceTool'] -> claude_code_recurso.md
prompt: 17.4 s, ['mcp__bcrp__buscar_series', 'mcp__bcrp__buscar_series', 'mcp__bcrp__buscar_series', 'mcp__bcrp__resumen', 'mcp__bcrp__resumen', 'mcp__bcrp__resumen', 'mcp__bcrp__correlacion'] -> claude_code_prompt.md
- Herramientas, en orden: mcp__bcrp__buscar_series, mcp__bcrp__buscar_series, mcp__bcrp__buscar_series, mcp__bcrp__buscar_series, mcp__bcrp__correlacion, mcp__bcrp__serie, mcp__bcrp__serie
- Herramientas, en orden: ReadMcpResourceTool
- Herramientas, en orden: mcp__bcrp__buscar_series, mcp__bcrp__buscar_series, mcp__bcrp__buscar_series, mcp__bcrp__resumen, mcp__bcrp__resumen, mcp__bcrp__resumen, mcp__bcrp__correlacion
```
</details>

**→ Bash**

```json
{
 "command": "uv run pytest -q 2>&1 | tail -1 && cat salidas/validacion.txt | sed -n '9,14p;37,38p' && cd .. && git status --short && git status --short --ignored tarea_4 | grep '^!!'",
 "description": "Re-run tests and review git status before commit",
 "timeout": 300000
}
```

<details><summary>← Resultado</summary>

```text
10 passed in 4.33s
CIFRA OFICIAL · base hogar (sumaria), ponderada con factor07 × mieperho
  [OK]    Pobreza monetaria nacional    27.58 %   referencia  27.6 %   diferencia -0.02 pp (tolerancia ±0.1)
  [OK]    Pobreza urbana                24.81 %   referencia  24.8 %   diferencia +0.01 pp (tolerancia ±0.1)
  [OK]    Pobreza rural                 39.30 %   referencia  39.3 %   diferencia +0.00 pp (tolerancia ±0.1)
  [OK]    Residentes habituales       108,664     referencia 108,664
  [OK]    Unidades territoriales           25     referencia 25 (códigos 01 a 25; Lima 15 y Callao 07 separados)
  Variables del do-file del INEI que no trae la sumaria 2024: gru52hd2 (se toman como 0).

 M tarea_4/.claude/skills/graficando-enaho/SKILL.md
 M tarea_4/.claude/skills/graficando-enaho/scripts/graficar.py
 M tarea_4/.claude/skills/limpiando-enaho/SKILL.md
 M tarea_4/.claude/skills/limpiando-enaho/reference.md
 M tarea_4/.claude/skills/limpiando-enaho/scripts/limpiar.py
 M tarea_4/.claude/skills/mapeando-enaho/SKILL.md
 M tarea_4/.claude/skills/mapeando-enaho/scripts/mapear.py
 M tarea_4/evidencias_ia/mcp/claude_code_herramientas.md
 M tarea_4/evidencias_ia/mcp/claude_code_prompt.md
 M tarea_4/evidencias_ia/mcp/claude_code_recurso.md
 M tarea_4/evidencias_ia/mcp/probar_en_claude_code.py
 M tarea_4/pyproject.toml
 M tarea_4/uv.lock
?? tarea_4/.claude/skills/mapeando-enaho/referencias/
?? tarea_4/evidencias_ia/skills/
?? tarea_4/evidencias_ia/traza.py
?? tarea_4/figuras/
?? tarea_4/mapas/
?? tarea_4/salidas/
!! tarea_4/.pytest_cache/
!! tarea_4/.venv/
!! tarea_4/datos/
!! tarea_4/evidencias_ia/__pycache__/
!! tarea_4/mcp/__pycache__/
!! tarea_4/salidas/hogares_2024.parquet
!! tarea_4/salidas/personas_2024.parquet
```
</details>

### Claude

Todo en orden: las bases `.parquet` y `datos/` quedan fuera, y `validacion.txt` e `indicadores.csv` entran. Commiteo la Parte 2 en tres pasos.

**→ Bash**

```json
{
 "command": "git add tarea_4/.claude/skills/limpiando-enaho tarea_4/pyproject.toml tarea_4/uv.lock tarea_4/salidas && git commit -q -F - <<'EOF'\nTarea 4, parte 2: limpiando-enaho valida contra la base hogar\n\nLa cifra oficial pasa a ser la base hogar ponderada con factor07 × mieperho\n(27.58 %, urbana 24.81 %, rural 39.30 %); facpob07 queda como línea\nsecundaria rotulada. 15 comprobaciones esenciales: pobreza nacional, urbana\ny rural ±0.1 pp, 108,664 residentes, 25 códigos territoriales, llaves de\ntexto sin perder ceros, unión m:1 sin pérdidas ni duplicados, factores sin\nvacíos y gasto por grupos igual a gashog2d. Si una falla, sale con código 2\ny borra las bases para que nadie use datos viejos.\n\nBusca sumaria-2024.dta por nombre exacto (nunca la 12g) y agrega lo que pide\nla pregunta: tipo de hogar según adultos mayores (65+) y participación de\nlos alimentos en el gasto con los 8 grupos del do-file oficial del INEI.\nEscribe hogares y personas en parquet, indicadores.csv y validacion.txt.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nEOF\ngit add tarea_4/.claude/skills/graficando-enaho tarea_4/.claude/skills/mapeando-enaho tarea_4/figuras tarea_4/mapas && git commit -q -F - <<'EOF'\nTarea 4, parte 2: gráficos y mapa con la base oficial\n\ngraficando-enaho: cortes de hogar (área, departamento, tipo de hogar y tipo\nde hogar × área) con factor07 × mieperho y de persona (sexo, edad) con\nfacpob07, rotulado en el pie. Indicadores: pobreza, pobreza extrema y\nparticipación de los alimentos. Título analítico calculado con las cifras,\nunidad, fuente, base y n en cada figura; paleta validada con dataviz.\n\nmapeando-enaho: une ubigeo[:2] con FIRST_IDDP (validate 1:1), exige 25\nunidades con dato y Lima y Callao separados, y se detiene si la pobreza\ndifiere más de 0.1 pp de la referencia de la sesión 16 (máx. 0.049).\nAgrega mapas de pobreza en hogares con adultos mayores y de personas que\nviven con ellos. Ambas skills salen con código 3 si falta la base y dicen\nque hay que correr limpiando-enaho.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nEOF\ngit add tarea_4/evidencias_ia && git commit -q -F - <<'EOF'\nTarea 4, parte 2: evidencias de activación y coordinación de las skills\n\nprobar_skills.py corre sesiones nuevas de claude -p y guarda cada traza:\n- coordinación: sin bases, «Haz un mapa de la pobreza…» carga\n  mapeando-enaho, recibe el código 3, corre limpiando-enaho y vuelve al mapa;\n- lenguaje natural: una pregunta sobre adultos mayores y alimentos activa\n  graficando-enaho con tipo_hogar_area;\n- invocación directa con /limpiando-enaho 2024;\n- desde tarea_4/ carga las skills de la tarea y desde la raíz las de la\n  sesión 16 (Base directory distinto).\n\ntraza.py reúne el paso de stream-json a Markdown; el script del MCP lo usa\ny sus trazas se regeneraron.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nEOF\ngit log --oneline -7 && git status --short",
 "description": "Commit Part 2 in three commits"
}
```

<details><summary>← Resultado</summary>

```text
warning: in the working copy of 'tarea_4/.claude/skills/limpiando-enaho/SKILL.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tarea_4/.claude/skills/limpiando-enaho/reference.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tarea_4/.claude/skills/limpiando-enaho/scripts/limpiar.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tarea_4/pyproject.toml', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tarea_4/uv.lock', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tarea_4/.claude/skills/graficando-enaho/SKILL.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tarea_4/.claude/skills/graficando-enaho/scripts/graficar.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tarea_4/.claude/skills/mapeando-enaho/SKILL.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tarea_4/evidencias_ia/mcp/probar_en_claude_code.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tarea_4/evidencias_ia/skills/probar_skills.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tarea_4/evidencias_ia/traza.py', LF will be replaced by CRLF the next time Git touches it
718ad5d Tarea 4, parte 2: evidencias de activación y coordinación de las skills
fbf5588 Tarea 4, parte 2: gráficos y mapa con la base oficial
125ea00 Tarea 4, parte 2: limpiando-enaho valida contra la base hogar
63a46eb Tarea 4, parte 1: evidencias del MCP dentro de Claude Code
3638fbb Tarea 4, parte 1: servidor MCP del BCRP con 10 pruebas en verde
ad359c5 Tarea 4, parte 0: estructura y punto de partida
d1b1a8c Portafolio: resalta Demo en la navegación
```
</details>

### Claude

Actualizo la memoria del proyecto con dos datos que no se deducen del código y sirven en las próximas partes.

**→ Edit**

```json
{
 "replace_all": false,
 "file_path": "~\\.claude\\projects\\~\\memory\\tarea-4-qlab.md",
 "old_string": "- Evidencias: exportar",
 "new_string": "- Claude Code debe arrancar DENTRO de tarea_4/ (ahí están .mcp.json y las skills de la tarea); desde la raíz carga las skills homónimas de la sesión 16 (verificado por el «Base directory»). Documentarlo en el README con el comando exacto.\n- sumaria-2024-12g.dta tiene pobreza/factor07/mieperho idénticos a sumaria-2024.dta; difiere en el gasto (otros grupos, gashog2d distinto en 3.45 % de hogares). La comprobación esencial de gasto la detecta.\n- Limitaciones para el informe: el catálogo BCRP dice Ene-2004 para PD04722MM pero la API trae datos desde 2003-09; en claude -p, --tools \"\" apaga ReadMcpResourceTool (documentar en comparacion.md).\n- Evidencias: exportar"
}
```

<details><summary>← Resultado</summary>

```text
The file ~\.claude\projects\~\memory\tarea-4-qlab.md has been updated successfully.
```
</details>

### Claude

`validacion.txt` está en verde: 15 de 15 comprobaciones esenciales, todas con `factor07 × mieperho`. La Parte 2 quedó en tres commits (`125ea00`, `fbf5588`, `718ad5d`), sin push todavía, y `uv run pytest -q` sigue en 10 passed.

| Cifra oficial | Calculado | Referencia |
|---|---|---|
| Pobreza nacional | 27.58 % | 27.6 % (diferencia −0.02 pp) |
| Pobreza urbana / rural | 24.81 % / 39.30 % | 24.8 % / 39.3 % |
| Residentes habituales | 108,664 | 108,664 |
| Unidades territoriales | 25 (Lima 15 y Callao 07 separados) | 25 |

La base con `facpob07` (27.53 / 24.7 / 39.4) aparece en su propio bloque, rotulada como secundaria, y no se valida contra el 27.6 %.

**Lo que cambió en las skills**
- **`limpiando-enaho`:**
  - Busca `sumaria-2024.dta` por nombre exacto.
  - Si falla una validación esencial, sale con código 2 y borra las bases para que nadie use datos viejos. Lo probé con el archivo faltante y con la `12g` renombrada como si fuera la correcta.
  - Arma lo que necesita la pregunta: tipo de hogar según adultos mayores (65+) y participación de los alimentos en el gasto. Esta última sale de la definición oficial del INEI (el do-file del zip del módulo 34), y la suma de los ocho grupos reproduce `gashog2d` en los 33,691 hogares.
- **`graficando-enaho` y `mapeando-enaho`:**
  - Usan la base hogar, salvo sexo y edad, que van con `facpob07` y lo dicen en el pie del gráfico.
  - El mapa se detiene si un departamento se aleja más de 0.1 pp de la referencia de la sesión 16; la diferencia máxima fue de 0.049.
  - Si falta la base procesada, ambas salen con código 3 e indican correr la limpieza.
- **Cada SKILL.md** dice al inicio que es la versión de `tarea_4`, en qué se diferencia de la de la sesión 16 y que Claude Code se arranca dentro de `tarea_4/`.

**Una corrección a lo que me dijiste de la `12g`:** las cifras de pobreza **sí cuadran** con ella. `pobreza`, `factor07` y `mieperho` son idénticos al 100 %. Lo que cambia es el gasto: usa otros grupos y su `gashog2d` difiere en el 3.45 % de los hogares. El riesgo real era el indicador de alimentos, y la comprobación esencial de gasto lo detecta.

**Evidencias en [evidencias_ia/skills/](tarea_4/evidencias_ia/skills/)**
- **Coordinación:** sin bases procesadas, el pedido "Haz un mapa de la pobreza monetaria…" cargó `mapeando-enaho`, recibió el código 3, corrió `limpiando-enaho` y luego hizo el mapa.
- **Lenguaje natural:** una pregunta sobre adultos mayores y alimentos activó `graficando-enaho` sin nombrarla.
- **Invocación directa:** `/limpiando-enaho 2024` corrió la limpieza.
- **Tu punto 1, verificado:** desde `tarea_4/` se carga `tarea_4\.claude\skills\…`; desde la raíz, la versión de la sesión 16. El comando exacto para el README lo agrego en la Parte 4.

**Adelanto para la Parte 3:** los datos no apoyan la hipótesis tal como está planteada.

| Tipo de hogar | Pobreza | Participación de alimentos en el gasto |
|---|---|---|
| Sin adultos mayores | 27.9 % | 47.5 % |
| Solo adultos mayores | 20.3 % | 46.1 % |

Dentro de cada área, en la zona rural los tres tipos de hogar gastan en alimentos entre 58.1 % y 58.7 %. La exposición se explica más por el área que por la presencia de adultos mayores. El informe lo va a decir así, como asociación descriptiva.

¿Sigo con la Parte 3?

