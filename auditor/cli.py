"""Punto de entrada del auditor.

  python -m auditor.cli                 # demo, tabla en consola
  python -m auditor.cli --formato html  # demo, reporte HTML a stdout
  python -m auditor.cli --formato json --salida hoy.json
  python -m auditor.cli --live          # tenant real (solo lectura)
  python -m auditor.cli --diff ayer.json --formato json   # qué cambió
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from auditor import diff as diffmod
from auditor.config import cargar
from auditor.permissions import CatalogoRiesgo
from auditor.report import console, html
from auditor.score import score_tenant


def _obtener_apps(es_demo: bool, cfg) -> list[dict]:
    if es_demo:
        from auditor.demo import demo_data
        return demo_data.apps()
    from auditor.collect import recolectar
    from auditor.graph import GraphClient
    g = GraphClient(cfg.tenant_id, cfg.client_id, cfg.client_secret)
    return recolectar(g, cfg)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Auditor de sobre-privilegio en Entra ID (solo lectura)")
    p.add_argument("--live", action="store_true", help="Tenant real vía Graph (por defecto: demo)")
    p.add_argument("--formato", choices=["consola", "json", "html"], default="consola")
    p.add_argument("--salida", type=Path, help="Archivo de salida (por defecto: stdout)")
    p.add_argument("--diff", type=Path, help="JSON de una corrida anterior: reportar SOLO lo que cambió")
    p.add_argument("--sin-color", action="store_true")
    args = p.parse_args(argv)

    cfg = cargar(modo="live" if args.live else "demo")
    cat = CatalogoRiesgo()
    tenant = score_tenant(_obtener_apps(cfg.es_demo, cfg), cat)
    tenant["demo"] = cfg.es_demo

    if args.diff:
        anterior = json.loads(args.diff.read_text(encoding="utf-8"))
        resultado = diffmod.comparar(anterior, tenant)
        salida = json.dumps(resultado, ensure_ascii=False, indent=2)
    elif args.formato == "json":
        salida = json.dumps(tenant, ensure_ascii=False, indent=2)
    elif args.formato == "html":
        salida = html.render(tenant, demo=cfg.es_demo)
    else:
        salida = console.render(tenant, demo=cfg.es_demo, color=not args.sin_color)

    if args.salida:
        args.salida.write_text(salida + "\n", encoding="utf-8")
        print(f"Escrito: {args.salida}", file=sys.stderr)
    else:
        print(salida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
