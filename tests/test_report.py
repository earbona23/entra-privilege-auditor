from auditor.demo import demo_data
from auditor.permissions import CatalogoRiesgo
from auditor.report import console, html
from auditor.score import score_tenant

CAT = CatalogoRiesgo()


def test_consola_incluye_rotulo_demo_y_score():
    t = score_tenant(demo_data.apps(), CAT)
    txt = console.render(t, demo=True, color=False)
    assert "DATOS DEMO" in txt and "Score de exposición del tenant" in txt


def test_html_es_autocontenido_sin_recursos_externos():
    t = score_tenant(demo_data.apps(), CAT)
    doc = html.render(t, demo=True)
    assert "<html" in doc and "DATOS DEMO" in doc
    for prohibido in ("http://", "https://", "src=", "cdn"):
        assert prohibido not in doc, f"el HTML no debe referenciar recursos externos ({prohibido})"
