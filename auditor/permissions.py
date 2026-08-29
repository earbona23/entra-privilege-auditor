"""Clasificación de riesgo de permisos, cargada del catálogo editable.

El nivel de riesgo NO está en el código: vive en data/permission_risk.yaml. Este
módulo solo lo carga y lo aplica. Un permiso no catalogado es 'desconocido', que
pesa más que 'bajo' a propósito: lo que nadie revisó es incierto, no inofensivo.
"""
from __future__ import annotations

from pathlib import Path

try:
    import yaml
except ImportError:  # el catálogo es YAML; sin PyYAML no se puede clasificar
    yaml = None  # type: ignore

CATALOGO = Path(__file__).resolve().parent.parent / "data" / "permission_risk.yaml"

# Peso de cada nivel en el score. Documentado en el README.
PESOS = {"critico": 100, "alto": 40, "medio": 10, "bajo": 2, "desconocido": 15}


class CatalogoRiesgo:
    def __init__(self, ruta: Path | None = None) -> None:
        if yaml is None:
            raise SystemExit("Se necesita PyYAML: pip install -r requirements.txt")
        p = ruta or CATALOGO
        self._datos: dict = yaml.safe_load(p.read_text(encoding="utf-8")) or {}

    def nivel(self, permiso: str) -> str:
        entrada = self._datos.get(permiso)
        return entrada["nivel"] if entrada else "desconocido"

    def porque(self, permiso: str) -> str:
        entrada = self._datos.get(permiso)
        if entrada:
            return entrada["porque"]
        return "Permiso no catalogado: revisar manualmente qué alcanza."

    def peso(self, permiso: str) -> int:
        return PESOS[self.nivel(permiso)]

    def clasificar(self, permiso: str) -> dict:
        return {
            "permiso": permiso,
            "nivel": self.nivel(permiso),
            "peso": self.peso(permiso),
            "porque": self.porque(permiso),
        }
