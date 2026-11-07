# Skills de la ENAHO en Claude Code · caso «lenguaje_natural»

Sesión nueva de `claude -p --model sonnet` arrancada en `tarea_4/`, sin servidores MCP y con las herramientas Skill, Bash, Read y Glob. Bases procesadas en `salidas/` al empezar: hogares_2024.parquet, personas_2024.parquet. Generado por `probar_skills.py`.

## Pedido

```text
¿Los hogares donde viven adultos mayores gastan una parte mayor de su presupuesto en alimentos? Compáralo con un gráfico, separando urbano y rural.
```

**Modelo:** claude-sonnet-5-5  
**Directorio:** `~\Documentos\GitHub\python-intermedio-QLAB\tarea_4`  
**Servidores MCP:** ninguno  
**Herramientas:** Bash, Glob, Read, Skill

### → Llama a `Skill`

```json
{
 "skill": "graficando-enaho"
}
```

#### ← Resultado

```text
Launching skill: graficando-enaho
```

#### ← Contenido que Claude Code inyecta (p. ej., el SKILL.md al cargar una skill)

```text
Base directory for this skill: ~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\graficando-enaho

# Graficar la ENAHO · versión tarea_4

> **Cuál versión es esta.** Hay otra `graficando-enaho` en la raíz del repo (sesión 16) que pondera todo con
> `facpob07`. Esta usa la **base hogar con `factor07 × mieperho`**, la de la cifra oficial, para los cortes de hogar,
> y `facpob07` solo para sexo y edad, rotulado en el pie del gráfico. Para usar esta versión se arranca `claude`
> dentro de `tarea_4/`.

1. **Si no existe `salidas/hogares_2024.parquet` (o `salidas/personas_2024.parquet` para sexo y edad), usa primero
   la skill `limpiando-enaho`** y espera a que termine sin error. Sin base validada no hay gráfico. El script
   también lo detecta: termina con código 3 y dice qué correr.

2. Elige el corte y el indicador según el pedido. **Solo estos valores exactos*
… (recortado)
```

### → Llama a `Bash`

```json
{
 "command": "cd ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4 && ls salidas && uv run ~/Documentos/GitHub/python-intermedio-QLAB/tarea_4/.claude/skills/graficando-enaho/scripts/graficar.py --corte tipo_hogar_area --indicador alimentos --anio 2024"
}
```

#### ← Resultado

```text
hogares_2024.parquet
indicadores.csv
personas_2024.parquet
validacion.txt
Participación de los alimentos en el gasto según presencia de adultos mayores (65+) y área, 2024 (% del gasto del hogar)
  Base hogar ponderada con factor07 × mieperho (la de la cifra oficial)
  Sin adultos mayores · Rural: 58.6 % (n = 7,803)
  Sin adultos mayores · Urbano: 44.8 % (n = 15,489)
  Con adultos mayores y menores de 65 · Rural: 58.7 % (n = 1,618)
  Con adultos mayores y menores de 65 · Urbano: 41.0 % (n = 4,312)
  Solo adultos mayores · Rural: 58.1 % (n = 2,239)
  Solo adultos mayores · Urbano: 39.9 % (n = 2,230)
  Perú: 46.6 %

Guardado en figuras/alimentos_tipo_hogar_area_2024.png (200 dpi) y las cifras en figuras/alimentos_tipo_hogar_area_2024.csv
```

### Claude

Hice el gráfico: `figuras/alimentos_tipo_hogar_area_2024.png`. Las cifras están en `figuras/alimentos_tipo_hogar_area_2024.csv`.

**No, los hogares con adultos mayores no gastan una parte mayor en alimentos. En el área urbana gastan menos, y en la rural gastan casi lo mismo.** Las cifras son el % del gasto del hogar en alimentos, ENAHO 2024, ponderado con `factor07 × mieperho`.

| Tipo de hogar | Urbano | Rural |
|---|---|---|
| Sin adultos mayores | 44.8 % | 58.6 % |
| Con adultos mayores y menores de 65 | 41.0 % | 58.7 % |
| Solo adultos mayores | 39.9 % | 58.1 % |

El promedio nacional es 46.6 %.

- **Urbano:** los hogares con adultos mayores gastan entre 3.8 y 4.9 puntos menos en alimentos que los hogares sin ellos. La diferencia es mayor en los hogares donde viven solo adultos mayores.
- **Rural:** las tres cifras están entre 58.1 % y 58.7 %. Esa diferencia, de menos de un punto, no permite decir que haya una brecha.
- **Área, no edad:** la brecha entre urbano y rural (unos 14 a 18 puntos) pesa mucho más que la presencia de adultos mayores.

El gráfico no trae intervalos de confianza, porque la ENAHO es una muestra. Las diferencias rurales, de menos de un punto, podrían no ser significativas. Los tamaños de muestra están en el pie del gráfico. El grupo con menos hogares es "Solo adultos mayores" urbano, con n = 2,230. Todos los grupos tienen más de 1,600 hogares.

## Resultado

- Herramientas, en orden: Skill(graficando-enaho), Bash
- Turnos: 4
- Segundos: 10.9
- Costo informado por Claude Code: US$ 0.0564
- ¿Terminó con error?: False
