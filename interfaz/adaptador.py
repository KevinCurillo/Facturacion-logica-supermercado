"""Adaptador entre la interfaz (Streamlit) y el motor lógico.

Contrato (ver docs/GUIA_UI.md):
    evaluar_compra(compra: dict, config: dict) -> dict
Si el motor real (reglas.py) define evaluar_compra, se usa; si no, motor_demo.
"""
import itertools
import json
from pathlib import Path

CONFIG_POR_DEFECTO = {"limite_identificacion": 50.0, "descuento_fidelidad": 0.05, "iva": 0.15}


def cargar_config(ruta="configuracion.json"):
    """Lee configuracion.json; si no existe, usa valores por defecto."""
    try:
        with open(Path(ruta), encoding="utf-8") as f:
            return {**CONFIG_POR_DEFECTO, **json.load(f)}
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(CONFIG_POR_DEFECTO)


def cargar_catalogo(ruta="catalogo.json"):
    """Lee el catálogo de productos; lista vacía si no existe o está dañado."""
    try:
        with open(Path(ruta), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def productos_desde_carrito(catalogo, carrito):
    """Convierte {id: cantidad} en la lista de productos que recibe armar_compra."""
    return [
        {"nombre": p["nombre"], "precio": p["precio"], "cantidad": carrito[p["id"]],
         "tarifa0": p.get("tarifa0", False), "promo": p.get("promo", False),
         "alcohol": p.get("alcohol", False)}
        for p in catalogo if carrito.get(p["id"], 0) > 0
    ]


def tabla_verdad_r1():
    """R1: a → i (compra sobre el límite requiere cliente identificado)."""
    return tabla_verdad(lambda a, i: (not a) or i, ["a", "i"])


def _motor():
    try:
        import reglas  # motor real del proyecto
        if hasattr(reglas, "evaluar_compra"):
            return reglas.evaluar_compra, "reglas.py"
    except ImportError:
        pass
    from interfaz import motor_demo
    return motor_demo.evaluar_compra, "motor_demo (provisional)"


def nombre_motor():
    return _motor()[1]


def validar_producto(p):
    """Devuelve lista de errores de un producto ingresado en el formulario."""
    errores = []
    if not str(p.get("nombre", "")).strip():
        errores.append("El producto necesita nombre.")
    if p.get("precio", 0) < 0:
        errores.append("El precio no puede ser negativo.")
    if p.get("cantidad", 0) < 1:
        errores.append("La cantidad debe ser al menos 1.")
    return errores


def armar_compra(cliente, productos):
    """Construye el diccionario de compra con tipos limpios."""
    return {
        "cliente": {k: bool(cliente.get(k, False)) for k in ("identificado", "tarjeta", "mayor_edad")},
        "productos": [
            {"nombre": str(p["nombre"]).strip(), "precio": float(p["precio"]),
             "cantidad": int(p["cantidad"]), "tarifa0": bool(p.get("tarifa0", False)),
             "promo": bool(p.get("promo", False)), "alcohol": bool(p.get("alcohol", False))}
            for p in productos
        ],
    }


def evaluar(compra, config=None):
    config = config or cargar_config()
    for p in compra["productos"]:
        errs = validar_producto(p)
        if errs:
            raise ValueError("; ".join(errs))
    if not compra["productos"]:
        raise ValueError("El carrito está vacío.")
    funcion, _ = _motor()
    return funcion(compra, config)


def tabla_verdad(funcion, nombres):
    """Tabla de verdad de una fórmula: filas (valores..., resultado), V/F como bool."""
    filas = []
    for vals in itertools.product([True, False], repeat=len(nombres)):
        filas.append(list(vals) + [bool(funcion(*vals))])
    return filas


def tabla_verdad_d5():
    """(f ∧ ¬p) → D5, la tabla de 8 filas pedida en la guía (p = Promo(x))."""
    return tabla_verdad(lambda f, p, d5: (not (f and not p)) or d5, ["f", "p", "D5"])
