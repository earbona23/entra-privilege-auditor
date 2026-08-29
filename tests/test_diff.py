from auditor import diff
from auditor.demo import demo_data
from auditor.permissions import CatalogoRiesgo
from auditor.score import score_tenant

CAT = CatalogoRiesgo()


def test_detecta_app_nueva_y_permiso_agregado():
    apps = demo_data.apps()
    antes = score_tenant(apps[1:], CAT)          # sin la primera app
    apps2 = [dict(a) for a in apps]
    apps2[1]["permisos_aplicacion"] = apps2[1]["permisos_aplicacion"] + ["Mail.Read"]
    ahora = score_tenant(apps2, CAT)
    d = diff.comparar(antes, ahora)
    assert any(n["nombre"] == "CRM Sync (heredada)" for n in d["apps_nuevas"])
    cambio = [c for c in d["cambios"] if "Mail.Read" in c["permisos_agregados"]]
    assert cambio and cambio[0]["delta_score"] > 0


def test_sin_cambios_no_reporta_ruido():
    t = score_tenant(demo_data.apps(), CAT)
    d = diff.comparar(t, t)
    assert d["apps_nuevas"] == [] and d["cambios"] == [] and d["delta_total"] == 0
