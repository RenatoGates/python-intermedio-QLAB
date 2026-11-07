# Skills de la ENAHO en Claude Code · caso «desde_tarea_4»

Sesión nueva de `claude -p --model haiku` arrancada en `tarea_4/`, sin servidores MCP y con las herramientas Skill, Bash, Read y Glob. Bases procesadas en `salidas/` al empezar: hogares_2024.parquet, personas_2024.parquet. Generado por `probar_skills.py`.

## Pedido

```text
Usa la skill limpiando-enaho, pero no ejecutes ningún comando. Solo dime la ruta de «Base directory» que te da la skill y con qué factor de expansión dice que se calcula la cifra oficial.
```

**Modelo:** claude-haiku-5-5  
**Directorio:** `~\Documentos\GitHub\python-intermedio-QLAB\tarea_4`  
**Servidores MCP:** ninguno  
**Herramientas:** Bash, Glob, Read, Skill

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

### Claude

**Base directory:** `~\Documentos\GitHub\python-intermedio-QLAB\tarea_4\.claude\skills\limpiando-enaho`

**Factor de expansión de la cifra oficial:** `factor07 × mieperho` sobre la base hogar. Es la que publica el INEI y la que pide el issue. La base persona con `facpob07` queda como cifra secundaria, solo para cortes por atributos de la persona, como sexo o edad.

No ejecuté ningún comando.

## Resultado

- Herramientas, en orden: Skill(limpiando-enaho)
- Turnos: 3
- Segundos: 4.9
- Costo informado por Claude Code: US$ 0.0040
- ¿Terminó con error?: False
