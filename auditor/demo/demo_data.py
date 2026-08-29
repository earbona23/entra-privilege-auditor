"""Tenant DEMO sintético para el auditor: un puñado de apps con distintos grados de
sobre-privilegio y abandono. Datos INVENTADOS, rotulados como demo en la salida.
Determinista, para que los tests afirmen sobre valores exactos.

Están pensadas para que el reporte muestre el rango completo: desde una app mínima
y bien cuidada hasta la clásica app olvidada con permisos de Administrador Global y
un secreto que nadie rotó en años.
"""
from __future__ import annotations


def apps() -> list[dict]:
    return [
        {
            "id": "11111111-app-crm-legacy",
            "nombre": "CRM Sync (heredada)",
            "tipo": "app registration",
            "permisos_aplicacion": ["Mail.ReadWrite", "Directory.ReadWrite.All", "User.Read.All"],
            "permisos_delegados": [],
            "sin_propietario": True,
            "credencial_vencida_o_por_vencer": True,
            "secreto_vigencia_excesiva": True,
            "sin_login_reciente": True,
        },
        {
            "id": "22222222-app-role-bot",
            "nombre": "Automatización de Roles",
            "tipo": "app registration",
            "permisos_aplicacion": ["RoleManagement.ReadWrite.Directory", "Application.ReadWrite.All"],
            "permisos_delegados": [],
            "sin_propietario": False,
            "credencial_vencida_o_por_vencer": False,
            "secreto_vigencia_excesiva": True,
            "sin_login_reciente": False,
        },
        {
            "id": "33333333-app-reporting",
            "nombre": "Panel de Reportes",
            "tipo": "app registration",
            "permisos_aplicacion": ["User.Read.All", "AuditLog.Read.All"],
            "permisos_delegados": ["User.Read"],
            "sin_propietario": False,
            "credencial_vencida_o_por_vencer": False,
            "secreto_vigencia_excesiva": False,
            "sin_login_reciente": True,
        },
        {
            "id": "44444444-app-files",
            "nombre": "Respaldo de Archivos",
            "tipo": "app registration",
            "permisos_aplicacion": ["Files.ReadWrite.All"],
            "permisos_delegados": [],
            "sin_propietario": True,
            "credencial_vencida_o_por_vencer": False,
            "secreto_vigencia_excesiva": False,
            "sin_login_reciente": False,
        },
        {
            "id": "55555555-app-signin",
            "nombre": "Portal de Empleados",
            "tipo": "app registration",
            "permisos_aplicacion": [],
            "permisos_delegados": ["User.Read", "openid", "profile", "offline_access"],
            "sin_propietario": False,
            "credencial_vencida_o_por_vencer": False,
            "secreto_vigencia_excesiva": False,
            "sin_login_reciente": False,
        },
        {
            "id": "66666666-app-unknown",
            "nombre": "Integración de Terceros",
            "tipo": "app registration",
            # Un permiso NO catalogado: debe tratarse como 'desconocido', no ignorarse.
            "permisos_aplicacion": ["ExternalConnection.ReadWrite.All"],
            "permisos_delegados": [],
            "sin_propietario": True,
            "credencial_vencida_o_por_vencer": True,
            "secreto_vigencia_excesiva": False,
            "sin_login_reciente": True,
        },
    ]
