"""Cálculo del score de exposición. La fórmula está acá y en el README, entera.

POR APLICACIÓN
  base = Σ peso(permiso de aplicación)  +  0.5 · Σ peso(permiso delegado)

  Los permisos de APLICACIÓN pesan el doble que los DELEGADOS a propósito: un
  permiso de aplicación actúa sin un usuario presente y suele cubrir todo el tenant;
  uno delegado está limitado a lo que el usuario que inició sesión ya podía hacer.

  Sobre esa base se aplican multiplicadores por señales de abandono, que no agregan
  privilegio pero sí probabilidad de que ese privilegio sea explotable sin que nadie
  lo note:
    sin propietario asignado ......... ×1.30
    credencial vencida o por vencer .. ×1.20
    sin inicio de sesión reciente .... ×1.20
    secreto con vigencia excesiva .... ×1.15
  Los multiplicadores se componen (se multiplican entre sí).

DEL TENANT
  Suma de los scores de todas las aplicaciones. Es deliberadamente una suma y no un
  promedio: veinte apps de riesgo medio son un problema mayor que una sola, y un
  promedio lo escondería.
"""
from __future__ import annotations

from auditor.permissions import CatalogoRiesgo

MULT_SIN_PROPIETARIO = 1.30
MULT_CRED_VENCIDA = 1.20
MULT_SIN_LOGIN = 1.20
MULT_SECRETO_VIEJO = 1.15


def score_app(app: dict, cat: CatalogoRiesgo) -> dict:
    """Recibe una app normalizada (ver collect.py) y devuelve su score con desglose."""
    peso_app = sum(cat.peso(p) for p in app.get("permisos_aplicacion", []))
    peso_del = sum(cat.peso(p) for p in app.get("permisos_delegados", []))
    base = peso_app + 0.5 * peso_del

    multiplicadores: list[tuple[str, float]] = []
    if app.get("sin_propietario"):
        multiplicadores.append(("sin propietario", MULT_SIN_PROPIETARIO))
    if app.get("credencial_vencida_o_por_vencer"):
        multiplicadores.append(("credencial vencida/por vencer", MULT_CRED_VENCIDA))
    if app.get("sin_login_reciente"):
        multiplicadores.append(("sin inicio de sesión reciente", MULT_SIN_LOGIN))
    if app.get("secreto_vigencia_excesiva"):
        multiplicadores.append(("secreto de vigencia excesiva", MULT_SECRETO_VIEJO))

    final = base
    for _, m in multiplicadores:
        final *= m

    nivel_max = "bajo"
    orden = ["bajo", "medio", "alto", "critico", "desconocido"]
    for p in app.get("permisos_aplicacion", []) + app.get("permisos_delegados", []):
        n = cat.nivel(p)
        if orden.index(n) > orden.index(nivel_max):
            nivel_max = n

    return {
        "id": app.get("id", ""),
        "nombre": app.get("nombre", "?"),
        "tipo": app.get("tipo", "?"),
        "score": round(final, 1),
        "base": round(base, 1),
        "nivel_max": nivel_max,
        "multiplicadores": [n for n, _ in multiplicadores],
        "señales": _señales(app),
        "permisos": _detalle_permisos(app, cat),
    }


def _señales(app: dict) -> list[str]:
    s = []
    if app.get("sin_propietario"):
        s.append("Sin propietario asignado")
    if app.get("credencial_vencida_o_por_vencer"):
        s.append("Credencial vencida o próxima a vencer")
    if app.get("sin_login_reciente"):
        s.append("Sin inicio de sesión reciente")
    if app.get("secreto_vigencia_excesiva"):
        s.append("Secreto con vigencia excesiva")
    return s


def _detalle_permisos(app: dict, cat: CatalogoRiesgo) -> list[dict]:
    filas = []
    for p in app.get("permisos_aplicacion", []):
        d = cat.clasificar(p)
        d["tipo"] = "aplicación"
        filas.append(d)
    for p in app.get("permisos_delegados", []):
        d = cat.clasificar(p)
        d["tipo"] = "delegado"
        filas.append(d)
    orden = {"critico": 0, "alto": 1, "medio": 2, "desconocido": 3, "bajo": 4}
    return sorted(filas, key=lambda x: orden.get(x["nivel"], 9))


def score_tenant(apps: list[dict], cat: CatalogoRiesgo) -> dict:
    scored = sorted((score_app(a, cat) for a in apps), key=lambda x: -x["score"])
    total = round(sum(a["score"] for a in scored), 1)
    return {
        "score_total": total,
        "apps_evaluadas": len(scored),
        "apps_criticas": sum(1 for a in scored if a["nivel_max"] == "critico"),
        "apps_sin_propietario": sum(1 for a in scored if "sin propietario" in a["multiplicadores"]),
        "apps": scored,
    }
