# Guía de la interfaz (Full Stack / UI)

## Ejecutar
```bash
pip install -r requirements.txt
streamlit run app.py
pytest --cov=interfaz tests/
```

## Contrato con el motor lógico
La interfaz llama a `evaluar_compra(compra, config) -> dict`. Si `reglas.py` la define, se usa;
si no, corre `interfaz/motor_demo.py` (provisional, solo para desarrollar la UI).

**compra**: `{"cliente": {"identificado", "tarjeta", "mayor_edad"}, "productos": [{"nombre", "precio", "cantidad", "tarifa0", "promo", "alcohol"}]}`

**config** (de `configuracion.json`): `limite_identificacion`, `descuento_fidelidad`, `iva`.

**resultado**: `variables {a,i,f}`, `reglas [{id, formula, cumple, detalle}]`, `lineas`, `subtotal`, `descuento`, `iva`, `total`, `valida`, `errores`.

> Acordar con el Desarrollador de Algoritmos y el Matemático si los nombres de campos cambian; solo se edita `interfaz/adaptador.py`.

## Flujo de trabajo
- Rama: `feat/interfaz-streamlit`; cambios a `main` por Pull Request.
- Commits: `feat:`, `fix:`, `test:`, `docs:`. Ejemplo: `feat: formulario de carrito y tabla de verdad en Streamlit`.
