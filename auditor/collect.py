"""Enumeración de aplicaciones del tenant vía Graph — SOLO LECTURA.

Normaliza cada app registration / service principal a la misma forma que consume
score.py, resolviendo los GUID de permisos a sus nombres legibles (Mail.Read, etc.)
usando el catálogo de roles del service principal de Microsoft Graph en el tenant.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from auditor.config import Config
from auditor.graph import GraphClient, GraphError

# App ID fijo del service principal de Microsoft Graph (igual en todos los tenants).
GRAPH_APP_ID = "00000003-0000-0000-c000-000000000000"


def _mapa_permisos_graph(g: GraphClient) -> dict[str, str]:
    """GUID de permiso -> nombre legible, para app roles y scopes delegados de Graph."""
    mapa: dict[str, str] = {}
    try:
        sps = list(g.get_all(
            "/servicePrincipals",
            {"$filter": f"appId eq '{GRAPH_APP_ID}'", "$select": "appRoles,oauth2PermissionScopes"},
        ))
    except GraphError:
        return mapa
    for sp in sps:
        for rol in sp.get("appRoles", []):
            mapa[rol["id"]] = rol.get("value", rol["id"])
        for scope in sp.get("oauth2PermissionScopes", []):
            mapa[scope["id"]] = scope.get("value", scope["id"])
    return mapa


def _analizar_credenciales(app: dict, dias_excesivo: int) -> tuple[bool, bool]:
    """Devuelve (credencial_vencida_o_por_vencer, secreto_vigencia_excesiva)."""
    ahora = datetime.now(timezone.utc)
    pronto = ahora + timedelta(days=30)
    vencida_o_pronto = False
    excesiva = False
    for cred in app.get("passwordCredentials", []) + app.get("keyCredentials", []):
        fin = cred.get("endDateTime", "")
        ini = cred.get("startDateTime", "")
        try:
            f = datetime.fromisoformat(fin.replace("Z", "+00:00")) if fin else None
            i = datetime.fromisoformat(ini.replace("Z", "+00:00")) if ini else None
        except ValueError:
            continue
        if f and f <= pronto:
            vencida_o_pronto = True
        if f and i and (f - i).days > dias_excesivo:
            excesiva = True
    return vencida_o_pronto, excesiva


def _sin_login_reciente(g: GraphClient, sp_id: str, dias: int) -> bool:
    """Usa el reporte de actividad de sign-in del service principal, si está disponible."""
    try:
        r = g.get(f"/servicePrincipals/{sp_id}",
                  {"$select": "id"})  # placeholder para mantener la firma
    except GraphError:
        return False
    del r
    try:
        actividad = list(g.get_all(
            "/reports/servicePrincipalSignInActivities",
            {"$filter": f"appId eq '{sp_id}'"},
        ))
    except GraphError:
        return False  # sin datos de actividad no afirmamos abandono
    if not actividad:
        return False
    ultimo = actividad[0].get("lastSignInActivity", {}).get("lastSignInDateTime", "")
    if not ultimo:
        return False
    try:
        f = datetime.fromisoformat(ultimo.replace("Z", "+00:00"))
    except ValueError:
        return False
    return (datetime.now(timezone.utc) - f).days > dias


def recolectar(g: GraphClient, cfg: Config) -> list[dict]:
    mapa = _mapa_permisos_graph(g)
    apps: list[dict] = []

    for app in g.get_all("/applications", {"$top": "100"}):
        app_perms: list[str] = []
        del_perms: list[str] = []
        for req in app.get("requiredResourceAccess", []):
            if req.get("resourceAppId") != GRAPH_APP_ID:
                continue
            for acc in req.get("resourceAccess", []):
                nombre = mapa.get(acc.get("id"), acc.get("id", "?"))
                if acc.get("type") == "Role":
                    app_perms.append(nombre)
                else:
                    del_perms.append(nombre)

        cred_venc, secreto_viejo = _analizar_credenciales(app, cfg.dias_secreto_excesivo)

        sin_prop = True
        try:
            propietarios = list(g.get_all(f"/applications/{app['id']}/owners", {"$select": "id"}))
            sin_prop = len(propietarios) == 0
        except GraphError:
            sin_prop = True

        apps.append({
            "id": app.get("appId", app.get("id", "")),
            "nombre": app.get("displayName", "?"),
            "tipo": "app registration",
            "permisos_aplicacion": app_perms,
            "permisos_delegados": del_perms,
            "sin_propietario": sin_prop,
            "credencial_vencida_o_por_vencer": cred_venc,
            "secreto_vigencia_excesiva": secreto_viejo,
            "sin_login_reciente": _sin_login_reciente(g, app.get("appId", ""), cfg.dias_sin_login),
        })
    return apps
