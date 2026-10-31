import pytest
from interfaz import adaptador as ad


def compra(identificado=True, tarjeta=False, mayor=True, productos=None):
    productos = productos or [{"nombre": "Arroz", "precio": 10, "cantidad": 1, "tarifa0": True}]
    return ad.armar_compra({"identificado": identificado, "tarjeta": tarjeta, "mayor_edad": mayor}, productos)


def test_tabla_verdad_d5_tiene_8_filas_y_una_sola_falsa():
    filas = ad.tabla_verdad_d5()
    assert len(filas) == 8
    assert [f for f in filas if not f[3]] == [[True, False, False, False]]


def test_r1_falla_sin_identificar_sobre_50():
    p = [{"nombre": "TV", "precio": 60, "cantidad": 1}]
    r = ad.evaluar(compra(identificado=False, productos=p), ad.CONFIG_POR_DEFECTO)
    assert not r["valida"] and r["reglas"][0]["cumple"] is False


def test_r1_cumple_bajo_el_limite():
    p = [{"nombre": "Pan", "precio": 5, "cantidad": 1}]
    assert ad.evaluar(compra(identificado=False, productos=p), ad.CONFIG_POR_DEFECTO)["valida"]


def test_r4_alcohol_menor_de_edad():
    p = [{"nombre": "Vino", "precio": 8, "cantidad": 1, "alcohol": True}]
    r = ad.evaluar(compra(mayor=False, productos=p), ad.CONFIG_POR_DEFECTO)
    assert not r["valida"]


def test_tarifa0_no_paga_iva_y_descuento_fidelidad():
    p = [{"nombre": "Arroz", "precio": 10, "cantidad": 1, "tarifa0": True},
         {"nombre": "Aceite", "precio": 10, "cantidad": 1}]
    r = ad.evaluar(compra(tarjeta=True, productos=p), ad.CONFIG_POR_DEFECTO)
    assert r["descuento"] == 1.0
    assert abs(r["iva"] - 1.43) < 0.01  # solo Aceite paga IVA: (10 - 0.5) * 0.15


def test_carrito_vacio_y_precio_negativo():
    with pytest.raises(ValueError):
        ad.evaluar({"cliente": {}, "productos": []}, ad.CONFIG_POR_DEFECTO)
    with pytest.raises(ValueError):
        ad.evaluar(compra(productos=[{"nombre": "X", "precio": -1, "cantidad": 1}]), ad.CONFIG_POR_DEFECTO)


def test_config_por_defecto_si_no_hay_archivo(tmp_path):
    assert ad.cargar_config(tmp_path / "no_existe.json")["iva"] == 0.15


def test_productos_desde_carrito_solo_incluye_los_agregados():
    cat = [{"id": "a", "nombre": "A", "precio": 1.0, "tarifa0": True},
           {"id": "b", "nombre": "B", "precio": 2.0}]
    prods = ad.productos_desde_carrito(cat, {"a": 3, "b": 0})
    assert [p["nombre"] for p in prods] == ["A"]
    assert prods[0]["cantidad"] == 3 and prods[0]["tarifa0"] is True


def test_catalogo_real_es_valido():
    cat = ad.cargar_catalogo("catalogo.json")
    assert len(cat) >= 10
    assert len({p["id"] for p in cat}) == len(cat)
    assert all(p["precio"] > 0 for p in cat)


def test_tabla_verdad_r1_solo_falla_con_a_verdadero_e_i_falso():
    falsas = [f for f in ad.tabla_verdad_r1() if not f[2]]
    assert falsas == [[True, False, False]]
