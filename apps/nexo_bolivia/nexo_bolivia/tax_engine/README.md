# Tax Engine - Motor de Impuestos Bolivia

**Motor de cálculo automático de impuestos bolivianos para Nexo ERP**

---

## Descripción

El Tax Engine implementa la lógica completa de cálculo de impuestos bolivianos:
- **IVA** (Impuesto al Valor Agregado) - 13%
- **IT** (Impuesto a las Transacciones) - 3%
- **IUE** (Impuesto sobre Utilidades de Empresas) - 25%

Se integra automáticamente con Sales Invoice, Purchase Invoice y Payment Entry mediante hooks de Frappe.

---

## Módulos

### 1. IVA (iva.py)

**Tasa**: 13%
**Aplica en**: Ventas y compras de bienes/servicios

#### Funciones principales:

```python
from nexo_bolivia.tax_engine.iva import calculate_iva, calculate_total_with_iva

# Calcular IVA sobre monto
iva = calculate_iva(1000)  # 130.0

# Calcular total con IVA
result = calculate_total_with_iva(1000)
# {'base': 1000.0, 'iva': 130.0, 'total': 1130.0, 'rate': 13.0}

# Extraer IVA de total que ya incluye IVA
from nexo_bolivia.tax_engine.iva import extract_iva_from_total
result = extract_iva_from_total(1130)
# {'base': 1000.0, 'iva': 130.0, 'total': 1130.0}
```

#### Hook automático:

```python
# Se aplica automáticamente en validate de Sales/Purchase Invoice
# No requiere configuración adicional
```

#### API:

```python
# Obtener balance IVA de un periodo
frappe.call('nexo_bolivia.tax_engine.iva.get_iva_report', {
    company: 'Mi Empresa',
    from_date: '2024-01-01',
    to_date: '2024-01-31'
})
```

### 2. IT (it.py)

**Tasa**: 3%
**Aplica en**: Todas las transacciones económicas
**Compensable**: 100% con IUE

#### Funciones principales:

```python
from nexo_bolivia.tax_engine.it import calculate_it, calculate_total_with_it

# Calcular IT sobre monto
it = calculate_it(1000)  # 30.0

# Calcular total con IT
result = calculate_total_with_it(1000)
# {'base': 1000.0, 'it': 30.0, 'total': 1030.0, 'rate': 3.0}
```

#### Hook automático:

```python
# Se aplica automáticamente en:
# - Sales Invoice (validate)
# - Payment Entry (on_submit)
```

#### API:

```python
# Obtener reporte IT de un periodo
frappe.call('nexo_bolivia.tax_engine.it.get_it_report', {
    company: 'Mi Empresa',
    from_date: '2024-01-01',
    to_date: '2024-01-31'
})
```

### 3. IUE (iue.py)

**Tasa**: 25%
**Aplica en**: Utilidad neta anual
**Periodo**: Anual

#### Funciones principales:

```python
from nexo_bolivia.tax_engine.iue import calculate_iue, calculate_iue_with_it_compensation

# Calcular IUE sobre utilidad
iue = calculate_iue(10000)  # 2500.0

# Calcular IUE con compensación IT
result = calculate_iue_with_it_compensation(10000, 500)
# {
#   'net_profit': 10000.0,
#   'iue_base': 2500.0,
#   'it_paid': 500.0,
#   'it_compensation': 500.0,
#   'iue_to_pay': 2000.0,
#   'rate': 25.0
# }
```

#### API:

```python
# Obtener reporte IUE anual
frappe.call('nexo_bolivia.tax_engine.iue.get_iue_report', {
    company: 'Mi Empresa',
    fiscal_year: '2024'
})

# Crear asiento contable de IUE
frappe.call('nexo_bolivia.tax_engine.iue.create_iue_provision', {
    company: 'Mi Empresa',
    fiscal_year: '2024'
})
```

### 4. Validators (validators.py)

Validaciones automáticas de impuestos:

```python
from nexo_bolivia.tax_engine.validators import validate_nit, validate_tax_amounts

# Validar NIT boliviano
is_valid = validate_nit('1234567890')

# Validar montos de impuestos en factura
validate_tax_amounts(invoice_doc)

# Validar año fiscal
fiscal_year = validate_fiscal_year('2024-01-15', 'Mi Empresa')
```

---

## Integración Automática

### Hooks Configurados

El Tax Engine se integra automáticamente mediante hooks en `nexo_bolivia/hooks.py`:

```python
doc_events = {
    "Sales Invoice": {
        "validate": [
            "nexo_bolivia.tax_engine.validators.validate_invoice_for_bolivia",
            "nexo_bolivia.tax_engine.iva.apply_iva_to_invoice",
            "nexo_bolivia.tax_engine.it.apply_it_to_invoice",
        ],
    },
    "Purchase Invoice": {
        "validate": [
            "nexo_bolivia.tax_engine.validators.validate_invoice_for_bolivia",
            "nexo_bolivia.tax_engine.iva.apply_iva_to_invoice",
        ],
    },
    "Payment Entry": {
        "on_submit": "nexo_bolivia.tax_engine.it.apply_it_to_payment",
    },
}
```

### Flujo Automático

**Sales Invoice**:
1. Usuario crea factura de venta
2. Al guardar (validate):
   - Valida NIT del cliente
   - Aplica IVA 13% automáticamente
   - Aplica IT 3% sobre total con IVA
3. Factura lista para submit

**Purchase Invoice**:
1. Usuario crea factura de compra
2. Al guardar (validate):
   - Valida NIT del proveedor
   - Aplica IVA Crédito Fiscal 13%
3. Factura lista para submit

**Payment Entry**:
1. Usuario registra pago
2. Al submit:
   - Calcula IT sobre monto pagado (si aplica)
   - Crea asiento contable

---

## Cuentas Contables

El Tax Engine utiliza las siguientes cuentas del Plan de Cuentas Bolivia:

| Impuesto | Cuenta | Número | Tipo |
|----------|--------|--------|------|
| IVA Crédito Fiscal | IVA Crédito Fiscal | 1141 | Activo |
| IVA por Pagar | IVA por Pagar | 2121 | Pasivo |
| IT Pagado Anticipado | IT Pagado por Anticipado | 1142 | Activo |
| IT por Pagar | IT por Pagar | 2122 | Pasivo |
| IUE por Pagar | IUE por Pagar | 2123 | Pasivo |
| IUE Gasto | IUE (Gasto) | 5412 | Egreso |

---

## Tests

### Ejecutar Tests

```bash
# Todos los tests del tax engine
bench --site nexo.local run-tests --app nexo_bolivia --module tax_engine

# Tests específicos
bench --site nexo.local run-tests nexo_bolivia.tax_engine.tests.test_iva
bench --site nexo.local run-tests nexo_bolivia.tax_engine.tests.test_it
bench --site nexo.local run-tests nexo_bolivia.tax_engine.tests.test_iue
```

### Cobertura

- ✅ Test IVA: 12 tests
- ✅ Test IT: 10 tests
- ✅ Test IUE: 10 tests
- ✅ Cobertura: 85%+

---

## Ejemplos de Uso

### Ejemplo 1: Factura de Venta con IVA e IT

```python
import frappe

# Crear factura de venta
invoice = frappe.get_doc({
    'doctype': 'Sales Invoice',
    'customer': 'Cliente Test',
    'company': 'Mi Empresa Bolivia',
    'items': [{
        'item_code': 'Producto 1',
        'qty': 10,
        'rate': 100
    }]
})

# Al guardar, se aplican automáticamente:
# - IVA 13% sobre 1000 = 130
# - IT 3% sobre 1130 = 33.90
# - Total: 1163.90

invoice.save()
print(f"Gran Total: {invoice.grand_total}")  # 1163.90
```

### Ejemplo 2: Cálculo Manual de IVA

```python
from nexo_bolivia.tax_engine.iva import calculate_iva, calculate_total_with_iva

# Producto cuesta 850 Bs
base = 850

# Calcular IVA
iva = calculate_iva(base)  # 110.5

# Calcular total
result = calculate_total_with_iva(base)
print(f"Base: Bs {result['base']}")      # 850.0
print(f"IVA: Bs {result['iva']}")        # 110.5
print(f"Total: Bs {result['total']}")    # 960.5
```

### Ejemplo 3: Balance IVA Mensual

```python
from nexo_bolivia.tax_engine.iva import calculate_iva_balance

# Obtener balance IVA de enero 2024
balance = calculate_iva_balance(
    company='Mi Empresa Bolivia',
    from_date='2024-01-01',
    to_date='2024-01-31'
)

print(f"IVA Débito Fiscal (ventas): Bs {balance['iva_debit_fiscal']}")
print(f"IVA Crédito Fiscal (compras): Bs {balance['iva_credit_fiscal']}")
print(f"Balance: Bs {balance['balance']}")
print(f"Estado: {balance['status']}")  # 'Por Pagar' o 'A Favor'
```

### Ejemplo 4: Cálculo IUE Anual con Compensación IT

```python
from nexo_bolivia.tax_engine.iue import calculate_iue_for_fiscal_year

# Calcular IUE para 2024
iue_data = calculate_iue_for_fiscal_year(
    company='Mi Empresa Bolivia',
    fiscal_year='2024'
)

print(f"Utilidad Neta: Bs {iue_data['net_profit']}")
print(f"IUE Base (25%): Bs {iue_data['iue_base']}")
print(f"IT Pagado: Bs {iue_data['it_paid']}")
print(f"IT Compensado: Bs {iue_data['it_compensation']}")
print(f"IUE a Pagar: Bs {iue_data['iue_to_pay']}")
```

---

## Configuración

### Activar/Desactivar Aplicación Automática

Para empresas no bolivianas, los hooks no se ejecutan automáticamente (verifican country='Bolivia').

Para desactivar temporalmente en empresa boliviana:

```python
# En hooks.py, comentar los hooks específicos
doc_events = {
    "Sales Invoice": {
        "validate": [
            # "nexo_bolivia.tax_engine.iva.apply_iva_to_invoice",  # Desactivado
        ],
    },
}
```

---

## Limitaciones Conocidas

1. **IT en Payment Entry**: Implementación básica, pendiente refinamiento
2. **Balance IVA**: No considera ajustes manuales
3. **IUE**: Cálculo de utilidad neta simplificado
4. **Validación NIT**: Algoritmo de dígito verificador pendiente

---

## Roadmap

- [ ] Algoritmo completo de validación NIT (dígito verificador)
- [ ] Reportes visuales de impuestos
- [ ] Libro de Ventas IVA oficial
- [ ] Libro de Compras IVA oficial
- [ ] Exportación formato SIN
- [ ] Dashboard de impuestos
- [ ] Proyección de impuestos

---

## Autor

**Aero**
Email: admin@aero.bo
Versión: 0.1.0
Licencia: GNU GPL v3

---

**Última actualización**: Diciembre 2024
