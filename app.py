"""Tienda de demostración (Streamlit). Ejecutar: streamlit run app.py"""
import streamlit as st

from interfaz import adaptador as ad
from interfaz.estilos import CSS

st.set_page_config(page_title="SuperLógica – Compras en línea", page_icon="🛒", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

config = ad.cargar_config()
catalogo = ad.cargar_catalogo()

if "carrito" not in st.session_state:
    st.session_state.carrito = {}
if "resultado" not in st.session_state:
    st.session_state.resultado = None


def agregar(pid):
    c = st.session_state.carrito
    c[pid] = c.get(pid, 0) + 1


def quitar(pid):
    c = st.session_state.carrito
    if c.get(pid, 0) <= 1:
        c.pop(pid, None)
    else:
        c[pid] -= 1


def vaciar():
    st.session_state.carrito = {}
    st.session_state.resultado = None


def insignias(p):
    html = ""
    if p.get("tarifa0"):
        html += '<span class="badge b-iva0">IVA 0%</span>'
    if p.get("promo"):
        html += '<span class="badge b-promo">PROMO</span>'
    if p.get("alcohol"):
        html += '<span class="badge b-alc">+18</span>'
    return html


def sv(valor):
    return "V" if valor else "F"


def dinero(x):
    return f"${x:,.2f}"


st.markdown(
    '<div class="topbar"><span class="logo">🛒 SuperLógica</span>'
    '<span class="lema">Tu supermercado con reglas claras</span></div>',
    unsafe_allow_html=True,
)

if not catalogo:
    st.error("No se encontró catalogo.json. Ejecuta la app desde la carpeta del proyecto.")
    st.stop()

izq, der = st.columns([2.2, 1], gap="large")

# ---------------- Catálogo ----------------
with izq:
    st.subheader("Productos")
    for inicio in range(0, len(catalogo), 3):
        cols = st.columns(3)
        for col, p in zip(cols, catalogo[inicio:inicio + 3]):
            with col.container(border=True):
                st.markdown(f'<div class="emoji">{p["emoji"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="nombre">{p["nombre"]}</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<span class="precio">{dinero(p["precio"])}</span>{insignias(p)}',
                    unsafe_allow_html=True,
                )
                st.button("Agregar", key=f"add_{p['id']}", on_click=agregar,
                          args=(p["id"],), use_container_width=True)

# ---------------- Carrito ----------------
with der:
    with st.container(border=True):
        st.subheader("🧺 Mi carrito")
        items = ad.productos_desde_carrito(catalogo, st.session_state.carrito)
        if not items:
            st.info("Tu carrito está vacío.")
        for p in catalogo:
            cant = st.session_state.carrito.get(p["id"], 0)
            if cant:
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.markdown(f"{p['emoji']} {p['nombre']}  \n**{cant} × {dinero(p['precio'])}**")
                c2.button("➖", key=f"menos_{p['id']}", on_click=quitar, args=(p["id"],))
                c3.button("➕", key=f"mas_{p['id']}", on_click=agregar, args=(p["id"],))
        if items:
            est = sum(i["precio"] * i["cantidad"] for i in items)
            st.markdown(f"**Subtotal aprox.: {dinero(est)}**")

        st.divider()
        st.markdown("**Datos del cliente**")
        identificado = st.checkbox("Cliente identificado (cédula, RUC o pasaporte)", key="identificado")
        tarjeta = st.checkbox("Tengo tarjeta de fidelidad", key="tarjeta")
        mayor = st.checkbox("Soy mayor de edad", key="mayor_edad")

        pagar = st.button("Pagar", type="primary", use_container_width=True, disabled=not items)
        st.button("Vaciar carrito", on_click=vaciar, use_container_width=True, disabled=not items)

        if pagar:
            try:
                compra = ad.armar_compra(
                    {"identificado": identificado, "tarjeta": tarjeta, "mayor_edad": mayor}, items)
                st.session_state.resultado = {"compra": compra, "res": ad.evaluar(compra, config)}
            except (ValueError, KeyError) as e:
                st.session_state.resultado = None
                st.error(f"Datos inválidos: {e}")

# ---------------- Resultado ----------------
datos = st.session_state.resultado
if datos:
    res, compra = datos["res"], datos["compra"]
    st.divider()
    tab_f, tab_r, tab_t = st.tabs(["🧾 Factura", "📋 Reporte interno", "🔢 Tabla de verdad"])

    with tab_f:
        if res["valida"]:
            st.success("Compra válida: factura emitida")
            cant = {p["nombre"]: p["cantidad"] for p in compra["productos"]}
            st.table([{"Producto": l["nombre"], "Cant.": cant.get(l["nombre"], ""),
                       "Subtotal": dinero(l["subtotal"]), "Descuento": dinero(l["descuento"]),
                       "IVA": dinero(l["iva"])} for l in res["lineas"]])
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Subtotal", dinero(res["subtotal"]))
            m2.metric("Descuento", dinero(res["descuento"]))
            m3.metric("IVA", dinero(res["iva"]))
            m4.metric("TOTAL", dinero(res["total"]))
        else:
            st.error("No se puede emitir la factura:")
            for e in res["errores"]:
                st.write(f"• {e}")

    with tab_r:
        st.caption("Reporte para el equipo: variables, reglas evaluadas y resultado.")
        st.markdown("**Variables proposicionales**")
        st.table([
            {"Variable": "a", "Significado": "El total supera el límite", "Valor": sv(res["variables"]["a"])},
            {"Variable": "i", "Significado": "Cliente identificado", "Valor": sv(res["variables"]["i"])},
            {"Variable": "f", "Significado": "Tiene tarjeta de fidelidad", "Valor": sv(res["variables"]["f"])},
        ])
        st.markdown("**Reglas evaluadas**")
        st.table([{"Regla": r["id"], "Fórmula": r["formula"], "Resultado": sv(r["cumple"]),
                   "Detalle": r["detalle"]} for r in res["reglas"]])
        with st.expander("Configuración usada (configuracion.json)"):
            st.json(config)

    with tab_t:
        a_act, i_act = res["variables"]["a"], res["variables"]["i"]
        t1, t2 = st.columns(2)
        with t1:
            st.markdown("**R1: a → i** (la fila de tu compra está marcada)")
            st.table([{"a": sv(a), "i": sv(i), "a → i": sv(r),
                       "": "◀ tu compra" if (a == a_act and i == i_act) else ""}
                      for a, i, r in ad.tabla_verdad_r1()])
        with t2:
            st.markdown("**(f ∧ ¬p) → D5**, con p = Promo(x)")
            st.table([{"f": sv(f), "p": sv(p), "D5": sv(d), "(f ∧ ¬p) → D5": sv(r)}
                      for f, p, d, r in ad.tabla_verdad_d5()])

st.markdown(f'<div class="pie">Demo académica · ESPOCH · Motor en uso: {ad.nombre_motor()}</div>',
            unsafe_allow_html=True)
