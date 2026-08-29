"""Modo diff: comparar dos ejecuciones y reportar SOLO lo que cambió.

El valor de una auditoría recurrente no es el número de hoy, es qué se movió desde
la última vez: una app nueva con permisos críticos, un permiso agregado a una app
existente, o un score que saltó. Eso es lo que merece atención.
"""
from __future__ import annotations


def _indexar(tenant: dict) -> dict[str, dict]:
    return {a["id"]: a for a in tenant.get("apps", [])}


def comparar(anterior: dict, actual: dict) -> dict:
    antes = _indexar(anterior)
    ahora = _indexar(actual)

    nuevas = [ahora[i] for i in ahora if i not in antes]
    eliminadas = [antes[i] for i in antes if i not in ahora]

    cambios = []
    for i in ahora:
        if i not in antes:
            continue
        a, b = antes[i], ahora[i]
        perms_antes = {p["permiso"] for p in a.get("permisos", [])}
        perms_ahora = {p["permiso"] for p in b.get("permisos", [])}
        agregados = sorted(perms_ahora - perms_antes)
        quitados = sorted(perms_antes - perms_ahora)
        delta_score = round(b["score"] - a["score"], 1)
        if agregados or quitados or delta_score:
            cambios.append({
                "id": i, "nombre": b["nombre"],
                "score_antes": a["score"], "score_ahora": b["score"], "delta_score": delta_score,
                "permisos_agregados": agregados, "permisos_quitados": quitados,
            })

    return {
        "score_antes": anterior.get("score_total", 0),
        "score_ahora": actual.get("score_total", 0),
        "delta_total": round(actual.get("score_total", 0) - anterior.get("score_total", 0), 1),
        "apps_nuevas": [{"id": a["id"], "nombre": a["nombre"], "score": a["score"],
                         "nivel_max": a["nivel_max"]} for a in nuevas],
        "apps_eliminadas": [{"id": a["id"], "nombre": a["nombre"]} for a in eliminadas],
        "cambios": sorted(cambios, key=lambda x: -abs(x["delta_score"])),
    }
