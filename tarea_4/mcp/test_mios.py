"""Dos pruebas propias: la herramienta correlacion y el recurso bcrp://serie/{codigo}.

    uv run pytest -q mcp/test_mios.py

Igual que test_server.py, llaman al servidor en memoria y piden datos reales al BCRP. No fijan el valor de r
(el INEI y el BCRP revisan cifras), sino que lo recalculan por otro camino a partir de lo que devuelve serie.
"""
import asyncio
import json

import numpy as np
import pytest
from fastmcp import Client
from fastmcp.exceptions import McpError, ToolError

from server import mcp

ALIMENTOS, REFERENCIA = "PN09822PM", "PD04722MM"     # inflación de alimentos a 12 meses y tasa de referencia


async def _con_cliente(f):
    async with Client(mcp) as c:
        return await f(c)


def llamar(herramienta, **args):
    return asyncio.run(_con_cliente(lambda c: c.call_tool(herramienta, args))).data


def test_correlacion_coincide_con_un_calculo_independiente():
    a = llamar("serie", codigo=ALIMENTOS, desde="2021-01", hasta="2025-12")["datos"]
    b = llamar("serie", codigo=REFERENCIA, desde="2021-01", hasta="2025-12")["datos"]
    meses = [f"{y}-{m:02d}" for y in range(2021, 2026) for m in range(1, 13)]
    assert [d["periodo"] for d in a] == meses == [d["periodo"] for d in b]   # 60 meses seguidos, sin huecos
    va, vb = np.array([d["valor"] for d in a]), np.array([d["valor"] for d in b])

    # sin rezago: mismo mes contra mismo mes
    r0 = llamar("correlacion", codigo_a=ALIMENTOS, codigo_b=REFERENCIA, desde="2021-01", hasta="2025-12")
    assert r0["n_pares"] == 60
    assert r0["periodo_comun"] == {"primero": "2021-01", "ultimo": "2025-12"}
    assert r0["r"] == pytest.approx(np.corrcoef(va, vb)[0, 1], abs=1e-4)
    assert r0["brecha_media"] == pytest.approx((va - vb).mean(), abs=1e-4)
    assert r0["periodos_a_mayor_que_b"] == int((va > vb).sum())
    assert all(f.startswith("https://estadisticas.bcrp.gob.pe") for f in r0["fuentes"])
    assert ALIMENTOS in r0["fuentes"][0] and REFERENCIA in r0["fuentes"][1]

    # rezago 3: la inflación de alimentos de t contra la tasa de t + 3, por posición; se pierden 3 pares
    r3 = llamar("correlacion", codigo_a=ALIMENTOS, codigo_b=REFERENCIA, desde="2021-01", hasta="2025-12", rezago=3)
    assert r3["n_pares"] == 57
    assert r3["periodo_comun"] == {"primero": "2021-01", "ultimo": "2025-09"}
    assert r3["r"] == pytest.approx(np.corrcoef(va[:-3], vb[3:])[0, 1], abs=1e-4)
    assert r3["r"] != pytest.approx(r0["r"], abs=1e-3)      # el rezago cambia de verdad el emparejamiento

    # series de frecuencias distintas: error claro en vez de un r sin sentido
    with pytest.raises(ToolError, match="misma frecuencia"):
        llamar("correlacion", codigo_a=ALIMENTOS, codigo_b="PD04638PD", desde="2025-01", hasta="2025-03")


def test_recurso_da_la_ficha_real_de_la_serie():
    async def leer(c):
        plantillas = [p.uri_template for p in await c.list_resource_templates()]
        contenido = (await c.read_resource(f"bcrp://serie/{ALIMENTOS}"))[0]
        return plantillas, contenido.mime_type, json.loads(contenido.text)

    plantillas, mime, ficha = asyncio.run(_con_cliente(leer))
    assert "bcrp://serie/{codigo}" in plantillas
    assert mime == "application/json"
    assert ficha["nombre"] == "Índice de precios Lima Metropolitana (var% 12 meses) - IPC Alimentos y Bebidas"
    assert (ficha["frecuencia"], ficha["inicio"], ficha["origen_de_los_datos"]) == ("Mensual", "Ene-1993", "INEI")
    assert ficha["web"] == ("https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/"
                            f"{ALIMENTOS}/html")

    # la ficha dice lo mismo que buscar_series sobre la misma serie
    encontrada = next(x for x in llamar("buscar_series", texto="ipc alimentos bebidas 12 meses")
                      if x["codigo"] == ALIMENTOS)
    assert {k: ficha[k] for k in encontrada} == encontrada

    # un código que no existe da un error que lo nombra
    with pytest.raises(McpError, match="XX999"):
        asyncio.run(_con_cliente(lambda c: c.read_resource("bcrp://serie/XX999")))
