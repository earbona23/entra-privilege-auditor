from auditor.demo import demo_data
from auditor.permissions import CatalogoRiesgo
from auditor.score import score_app, score_tenant

CAT = CatalogoRiesgo()


def test_app_de_aplicacion_pesa_mas_que_delegada():
    base_app = {"permisos_aplicacion": ["User.Read.All"], "permisos_delegados": []}
    base_del = {"permisos_aplicacion": [], "permisos_delegados": ["User.Read.All"]}
    assert score_app(base_app, CAT)["base"] > score_app(base_del, CAT)["base"]


def test_multiplicadores_de_abandono_se_componen():
    limpia = {"permisos_aplicacion": ["User.Read.All"]}
    abandonada = {"permisos_aplicacion": ["User.Read.All"], "sin_propietario": True,
                  "credencial_vencida_o_por_vencer": True}
    assert score_app(abandonada, CAT)["score"] > score_app(limpia, CAT)["score"]


def test_permiso_no_catalogado_es_desconocido_no_cero():
    a = {"permisos_aplicacion": ["Permiso.Inventado.All"]}
    r = score_app(a, CAT)
    assert r["score"] > 0, "un permiso sin catalogar debe pesar (incierto), no valer cero"
    assert r["permisos"][0]["nivel"] == "desconocido"


def test_tenant_suma_no_promedia():
    apps = demo_data.apps()
    t = score_tenant(apps, CAT)
    assert t["score_total"] == round(sum(a["score"] for a in t["apps"]), 1)
    assert t["apps_evaluadas"] == len(apps)


def test_la_app_mas_peligrosa_del_demo_queda_primera():
    t = score_tenant(demo_data.apps(), CAT)
    # La CRM heredada tiene Mail.ReadWrite + Directory.ReadWrite.All + 3 señales de abandono.
    assert t["apps"][0]["nombre"] == "CRM Sync (heredada)"
    assert t["apps"][0]["nivel_max"] == "critico"
