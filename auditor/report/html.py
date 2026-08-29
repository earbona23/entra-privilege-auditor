"""Reporte HTML autocontenido para presentar a dirección. Sin recursos externos."""
from __future__ import annotations

import html as _h
import json

_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0b0f1a;color:#e7ecf6;font-family:system-ui,Segoe UI,Roboto,sans-serif;padding:28px;line-height:1.5}
h1{font-size:22px;background:linear-gradient(90deg,#667eea,#c549d0);-webkit-background-clip:text;background-clip:text;color:transparent}
.demo{display:inline-block;margin-left:12px;padding:4px 10px;border-radius:999px;background:#3a2a00;color:#f4b740;font-size:12px;font-weight:700}
.kpis{display:flex;gap:14px;flex-wrap:wrap;margin:18px 0}
.kpi{background:#141a2b;border:1px solid #26304d;border-radius:12px;padding:12px 16px;min-width:150px}
.kpi .n{font-size:26px;font-weight:800}.kpi .l{font-size:12px;color:#8b97b5}
.app{background:#141a2b;border:1px solid #26304d;border-radius:14px;padding:14px 16px;margin:10px 0}
.app h2{font-size:16px;display:flex;align-items:center;gap:10px}
.score{font-size:22px;font-weight:800}
.pill{padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700;margin-left:auto}
.critico{background:#3a0d13;color:#ff5c6c}.alto{background:#3a2a00;color:#f4b740}
.medio{background:#0a2233;color:#4aa8ff}.bajo{background:#06240f;color:#2ecc71}.desconocido{background:#2a1533;color:#c549d0}
.sig{color:#f4b740;font-size:13px;margin:6px 0}
table{width:100%;border-collapse:collapse;font-size:13px;margin-top:8px}
td,th{text-align:left;padding:6px;border-bottom:1px solid #26304d;vertical-align:top}
th{color:#8b97b5;font-size:11px;text-transform:uppercase}
footer{color:#8b97b5;font-size:12px;margin-top:24px}
"""


def render(tenant: dict, demo: bool) -> str:
    def esc(x) -> str:
        return _h.escape(str(x))

    kpis = f"""
    <div class="kpis">
      <div class="kpi"><div class="n">{esc(tenant['score_total'])}</div><div class="l">Score del tenant</div></div>
      <div class="kpi"><div class="n">{esc(tenant['apps_evaluadas'])}</div><div class="l">Apps evaluadas</div></div>
      <div class="kpi"><div class="n">{esc(tenant['apps_criticas'])}</div><div class="l">Con permiso crítico</div></div>
      <div class="kpi"><div class="n">{esc(tenant['apps_sin_propietario'])}</div><div class="l">Sin propietario</div></div>
    </div>"""

    apps_html = []
    for a in tenant["apps"]:
        filas = "".join(
            f"<tr><td>{esc(p['permiso'])}</td><td>{esc(p['tipo'])}</td>"
            f"<td><span class='pill {esc(p['nivel'])}'>{esc(p['nivel'])}</span></td>"
            f"<td>{esc(p['porque'])}</td></tr>"
            for p in a["permisos"]
        )
        sig = f"<div class='sig'>⚠ {esc(', '.join(a['señales']))}</div>" if a["señales"] else ""
        apps_html.append(f"""
        <div class="app">
          <h2>{esc(a['nombre'])}<span class="pill {esc(a['nivel_max'])}">{esc(a['nivel_max'])}</span></h2>
          <div class="score">{esc(a['score'])}</div>{sig}
          <table><thead><tr><th>Permiso</th><th>Tipo</th><th>Riesgo</th><th>Por qué</th></tr></thead>
          <tbody>{filas or '<tr><td colspan=4>Sin permisos de Graph</td></tr>'}</tbody></table>
        </div>""")

    banner = '<span class="demo">DATOS DEMO</span>' if demo else ""
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Auditoría de sobre-privilegio · Entra ID</title><style>{_CSS}</style></head><body>
<h1>Auditoría de sobre-privilegio · Entra ID{banner}</h1>
{kpis}
{''.join(apps_html)}
<footer>Herramienta de SOLO LECTURA. Score = Σ peso(permiso app) + 0.5·Σ peso(permiso delegado),
por multiplicadores de abandono. Datos embebidos:
<script type="application/json" id="raw">{json.dumps(tenant, ensure_ascii=False)}</script></footer>
</body></html>"""
