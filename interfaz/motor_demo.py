"""Motor PROVISIONAL solo para desarrollar y probar la interfaz.

No es el motor lógico del proyecto: ese es reglas.py (Desarrollador de Algoritmos).
Cuando reglas.py exponga evaluar_compra(), el adaptador lo usa y este archivo
deja de ejecutarse.
"""


def evaluar_compra(compra, config):
    productos = compra["productos"]
    cliente = compra["cliente"]
    limite = config["limite_identificacion"]
    pct_desc = config["descuento_fidelidad"]
    pct_iva = config["iva"]

    base = sum(p["precio"] * p["cantidad"] for p in productos)
    a = base > limite
    i = bool(cliente["identificado"])
    f = bool(cliente["tarjeta"])

    lineas, descuento, iva = [], 0.0, 0.0
    for p in productos:
        sub = p["precio"] * p["cantidad"]
        d5 = f and not p["promo"]
        desc = sub * pct_desc if d5 else 0.0
        tasa = 0.0 if p["tarifa0"] else pct_iva
        imp = (sub - desc) * tasa
        descuento += desc
        iva += imp
        lineas.append({"nombre": p["nombre"], "subtotal": round(sub, 2),
                       "descuento": round(desc, 2), "iva": round(imp, 2)})

    hay_alcohol = any(p["alcohol"] for p in productos)
    r1 = (not a) or i
    r4 = (not hay_alcohol) or bool(cliente["mayor_edad"])
    reglas = [
        {"id": "R1", "formula": "a → i", "cumple": r1,
         "detalle": "Compra sobre el límite requiere cliente identificado."},
        {"id": "R2", "formula": "∀x ((f ∧ ¬Promo(x)) → D5(x))", "cumple": True,
         "detalle": "Descuento aplicado a los productos sin promoción." if f else "Sin tarjeta: no aplica."},
        {"id": "R3", "formula": "∀x (Tarifa0(x) → IVA(x) = 0%)", "cumple": True,
         "detalle": "Productos de tarifa 0% sin IVA."},
        {"id": "R4", "formula": "(∃x Alcohol(x)) → MayorEdad(c)", "cumple": r4,
         "detalle": "Venta de alcohol requiere mayoría de edad."},
    ]
    errores = [f"{r['id']}: {r['detalle']}" for r in reglas if not r["cumple"]]
    return {
        "variables": {"a": a, "i": i, "f": f},
        "reglas": reglas, "lineas": lineas,
        "subtotal": round(base, 2), "descuento": round(descuento, 2),
        "iva": round(iva, 2), "total": round(base - descuento + iva, 2),
        "valida": not errores, "errores": errores,
    }
