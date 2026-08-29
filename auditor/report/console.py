"""Reporte de consola: tabla legible priorizada por score."""
from __future__ import annotations

_COLOR = {
    "critico": "\033[91m", "alto": "\033[93m", "medio": "\033[96m",
    "bajo": "\033[92m", "desconocido": "\033[95m",
}
_RESET = "\033[0m"


def render(tenant: dict, demo: bool, color: bool = True) -> str:
    def c(nivel: str, txt: str) -> str:
        if not color:
            return txt
        return f"{_COLOR.get(nivel, '')}{txt}{_RESET}"

    lineas = []
    if demo:
        lineas.append("  ●  DATOS DEMO — tenant sintético, nada de esto es real  ●\n")
    lineas.append("AUDITORÍA DE SOBRE-PRIVILEGIO EN ENTRA ID")
    lineas.append("=" * 60)
    lineas.append(f"Score de exposición del tenant : {tenant['score_total']}")
    lineas.append(f"Aplicaciones evaluadas         : {tenant['apps_evaluadas']}")
    lineas.append(f"  con permiso crítico          : {tenant['apps_criticas']}")
    lineas.append(f"  sin propietario asignado     : {tenant['apps_sin_propietario']}")
    lineas.append("")
    lineas.append(f"{'SCORE':>7}  {'NIVEL':<12} APLICACIÓN")
    lineas.append("-" * 60)
    for a in tenant["apps"]:
        etiqueta = c(a["nivel_max"], f"{a['nivel_max']:<12}")
        lineas.append(f"{a['score']:>7}  {etiqueta} {a['nombre']}")
        if a["señales"]:
            lineas.append(f"{'':>9}⚠ {', '.join(a['señales'])}")
        criticos = [p for p in a["permisos"] if p["nivel"] in ("critico", "alto")]
        for p in criticos[:3]:
            lineas.append(f"{'':>9}• {p['permiso']} ({p['tipo']}, {p['nivel']}) — {p['porque']}")
    lineas.append("")
    lineas.append("Herramienta de SOLO LECTURA. No modifica nada en el tenant.")
    return "\n".join(lineas)
