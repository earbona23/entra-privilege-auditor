"""Configuración del auditor. Igual que el resto de mis herramientas: demo por
defecto, live solo con credenciales, secretos NUNCA en el repo.

Permisos de Graph que el propio auditor necesita (SOLO LECTURA):
  Application.Read.All   — enumerar app registrations y service principals
  Directory.Read.All     — leer propietarios y asignaciones
  AuditLog.Read.All      — última actividad de inicio de sesión de cada app
El auditor lee sobre-privilegio; sería una ironía que él mismo pidiera escritura.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

RAIZ = Path(__file__).resolve().parent.parent
CONFIG_LOCAL = RAIZ / "config.yaml"

SCOPES = ("Application.Read.All", "Directory.Read.All", "AuditLog.Read.All")


@dataclass
class Config:
    modo: str = "demo"
    tenant_id: str = ""
    client_id: str = ""
    client_secret: str = field(default="", repr=False)
    # Umbrales de las señales de abandono (editables por el usuario).
    dias_secreto_excesivo: int = 180
    dias_sin_login: int = 90

    @property
    def es_demo(self) -> bool:
        return self.modo != "live"


def cargar(modo: str = "demo") -> Config:
    cfg = Config(modo=modo)
    if cfg.es_demo:
        return cfg
    if yaml is None:
        raise SystemExit("Modo --live necesita PyYAML: pip install -r requirements.txt")

    datos: dict = {}
    if CONFIG_LOCAL.exists():
        datos = yaml.safe_load(CONFIG_LOCAL.read_text(encoding="utf-8")) or {}
    cfg.tenant_id = os.getenv("EPA_TENANT_ID", datos.get("tenant_id", ""))
    cfg.client_id = os.getenv("EPA_CLIENT_ID", datos.get("client_id", ""))
    cfg.client_secret = os.getenv("EPA_CLIENT_SECRET", datos.get("client_secret", ""))
    cfg.dias_secreto_excesivo = int(datos.get("dias_secreto_excesivo", cfg.dias_secreto_excesivo))
    cfg.dias_sin_login = int(datos.get("dias_sin_login", cfg.dias_sin_login))

    faltan = [n for n, v in (("tenant_id", cfg.tenant_id), ("client_id", cfg.client_id),
                             ("client_secret", cfg.client_secret)) if not v]
    if faltan:
        raise SystemExit(
            "Modo --live pero falta: " + ", ".join(faltan) + ".\n"
            "Copiá config.example.yaml a config.yaml, o exportá "
            "EPA_TENANT_ID / EPA_CLIENT_ID / EPA_CLIENT_SECRET."
        )
    return cfg
