# Skills de la ENAHO en Claude Code · caso «desde_la_raiz»

Sesión nueva de `claude -p --model haiku` arrancada en `./`, sin servidores MCP y con las herramientas Skill, Bash, Read y Glob. Bases procesadas en `salidas/` al empezar: hogares_2024.parquet, personas_2024.parquet. Generado por `probar_skills.py`.

## Pedido

```text
Usa la skill limpiando-enaho, pero no ejecutes ningún comando. Solo dime la ruta de «Base directory» que te da la skill y con qué factor de expansión dice que se calcula la cifra oficial.
```

**Modelo:** claude-haiku-5-5  
**Directorio:** `~\Documentos\GitHub\python-intermedio-QLAB`  
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
Base directory for this skill: ~\Documentos\GitHub\python-intermedio-QLAB\.claude\skills\limpiando-enaho

# Limpiar la ENAHO

1. Si no hay zip ni `.dta` en `datos/`, pide al usuario bajarlos del INEI antes de seguir.
   El código de la ENAHO 2024 es **966**:
   - `https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip`
   - `https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip`

2. Corre exactamente:

   ˋˋˋbash
   uv run ~/Documentos/GitHub/python-intermedio-QLAB/.claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024
   ˋˋˋ

   Cambia `2024` solo si el usuario pidió otro año y `$0` es un **número de cuatro
   dígitos**. `$0` trae el texto libre del pedido, no un año: nunca lo pases tal cual.

3. Lee `salidas/validacion.txt`. **Si la pobreza difiere del INEI en más de 0.1 puntos, detente**
   
… (recortado)
```

### Claude

**Base directory:** `~\Documentos\GitHub\python-intermedio-QLAB\.claude\skills\limpiando-enaho`

**Factor de expansión de la cifra oficial:** la skill dice que el 27.6 % del INEI sale de la sumaria, ponderando hogares con `factor07 × mieperho`. Con ese factor, la pobreza monetaria da 27.58 %.

La base de personas, ponderada con `facpob07`, da 27.53 %. La skill indica que ambas son correctas, porque la sumaria pondera hogares por su tamaño y la de personas pondera personas. Además, el paso 4 pide ponderar toda cifra con `facpob07`, así que la skill mezcla dos factores; si necesitas cuadrar exactamente con el INEI, conviene usar el de la sumaria.

## Resultado

- Herramientas, en orden: Skill(limpiando-enaho)
- Turnos: 3
- Segundos: 6.7
- Costo informado por Claude Code: US$ 0.0027
- ¿Terminó con error?: False
