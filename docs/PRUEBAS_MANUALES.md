# Pruebas manuales de la interfaz

Ejecutar `streamlit run app.py` y verificar cada caso (sin tarjeta ni identificación salvo que se indique).

| # | Caso | Pasos | Resultado esperado |
|---|------|-------|--------------------|
| 1 | Compra pequeña válida | Arroz ×2, sin marcar nada, Pagar | Factura emitida; IVA $0.00 (tarifa 0%) |
| 2 | R1 falla | Licuadora ×1, sin identificar, Pagar | No se emite factura; error R1 |
| 3 | R1 cumple | Licuadora ×1, marcar "identificado", Pagar | Factura emitida; fila a=V, i=V marcada |
| 4 | Borde del límite | Productos que sumen exactamente $50.00 sin identificar | Válida (a es F: 50 no supera 50) |
| 5 | Justo sobre el límite | Total $50.01 sin identificar | Falla R1 |
| 6 | R4 alcohol, menor | Cerveza, sin "mayor de edad", Pagar | Falla R4 |
| 7 | R4 alcohol, mayor | Cerveza, con "mayor de edad" | Factura emitida |
| 8 | R2 descuento | Aceite + Gaseosa (PROMO), con tarjeta | 5% solo al aceite; gaseosa sin descuento |
| 9 | R3 IVA | Arroz + Aceite | IVA solo sobre el aceite (15%) |
| 10 | Carrito vacío | Sin productos | Botón Pagar deshabilitado |
| 11 | Cantidades | ➕ y ➖ hasta quitar el producto | Desaparece al llegar a 0 |
| 12 | Vaciar | Vaciar carrito con resultado visible | Carrito y resultado se limpian |
| 13 | Cambiar datos | Pagar, cambiar casilla, Pagar de nuevo | El resultado se recalcula |
| 14 | Config | Cambiar `limite_identificacion` en configuracion.json | Los casos 4 y 5 cambian de umbral |
