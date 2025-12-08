# Plan de Cuentas Bolivia

**DocType para gestión del Plan Contable Boliviano**

---

## Descripción

Este DocType implementa el **Plan de Cuentas** según normativa contable boliviana, con estructura jerárquica de 5 niveles y clasificación estándar.

## Características

### ✅ Estructura Jerárquica

```
1 - ACTIVO
  11 - ACTIVO CORRIENTE
    111 - DISPONIBILIDADES
      1111 - Caja
      1112 - Caja Chica
      1113 - Caja Moneda Extranjera
      1114 - Bancos
        11141 - Banco Nacional de Bolivia
        11142 - Banco Unión
```

### ✅ Clasificación de Cuentas

- **1** - ACTIVO
- **2** - PASIVO
- **3** - PATRIMONIO
- **4** - INGRESOS
- **5** - EGRESOS

### ✅ Cuentas Fiscales Bolivia

**Impuestos incluidos:**
- IVA Crédito Fiscal (1141) - 13%
- IVA por Pagar (2121) - 13%
- IT Pagado por Anticipado (1142) - 3%
- IT por Pagar (2122) - 3%
- IUE por Pagar (2123) - 25%
- RC-IVA por Pagar (2124)

**Nómina:**
- Aportes AFP por Pagar (2132) - 12.71%
- Aguinaldo por Pagar (2133)
- Sueldos y Salarios por Pagar (2131)

## Campos Principales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `account_number` | Data | Número de cuenta (único, 1-5+ dígitos) |
| `account_name` | Data | Nombre de la cuenta |
| `account_type` | Select | Tipo (Activo, Pasivo, Patrimonio, Ingreso, Egreso) |
| `is_group` | Check | Si es cuenta de grupo (puede tener hijas) |
| `parent_account` | Link | Cuenta padre en la jerarquía |
| `root_type` | Select | Tipo raíz (auto-determinado por 1er dígito) |
| `company` | Link | Empresa asociada |
| `balance_must_be` | Select | Débito o Crédito |
| `account_currency` | Link | Moneda (default: BOB) |

## Validaciones

### ✅ Formato de Número de Cuenta

```python
# Válidos
"1"      # Nivel 1 (raíz)
"11"     # Nivel 2
"111"    # Nivel 3
"1111"   # Nivel 4
"11141"  # Nivel 5

# Inválidos
"ABC"    # No numérico
"6"      # Primer dígito debe ser 1-5
```

### ✅ Jerarquía

- Cuenta padre debe ser de tipo "grupo" (`is_group = 1`)
- Número de cuenta hija debe comenzar con número de cuenta padre
- Cuentas con hijas deben ser marcadas como "grupo"

### ✅ Auto-determinación de Tipo Raíz

```python
Primer dígito → Root Type
1 → Activo
2 → Pasivo
3 → Patrimonio
4 → Ingreso
5 → Egreso
```

## Uso

### Crear Cuenta Raíz

```python
import frappe

account = frappe.get_doc({
    "doctype": "Plan Cuentas Bolivia",
    "account_number": "1",
    "account_name": "ACTIVO",
    "account_type": "Activo",
    "is_group": 1,
    "root_type": "Activo",
    "account_currency": "BOB"
})
account.insert()
```

### Crear Cuenta Hija

```python
# Primero obtener cuenta padre
parent = frappe.get_doc("Plan Cuentas Bolivia", "1")

# Crear cuenta hija
child = frappe.get_doc({
    "doctype": "Plan Cuentas Bolivia",
    "account_number": "11",
    "account_name": "ACTIVO CORRIENTE",
    "account_type": "Activo",
    "is_group": 1,
    "parent_account": parent.name,
    "root_type": "Activo",
    "account_currency": "BOB"
})
child.insert()
```

### Obtener Árbol de Cuentas

```python
from nexo_bolivia.nexo_bolivia.doctype.plan_cuentas_bolivia.plan_cuentas_bolivia import get_chart_of_accounts

# Obtener todo el plan de cuentas
tree = get_chart_of_accounts()

# Filtrar por empresa
tree = get_chart_of_accounts(company="Mi Empresa")
```

### Importar desde ERPNext

```python
from nexo_bolivia.nexo_bolivia.doctype.plan_cuentas_bolivia.plan_cuentas_bolivia import import_from_erpnext

# Importar cuentas existentes de ERPNext
result = import_from_erpnext(company="Mi Empresa")
print(f"Creadas: {result['created']}, Actualizadas: {result['updated']}")
```

## Sincronización con ERPNext

El DocType sincroniza automáticamente con `Account` de ERPNext:

```python
# Al guardar, se crea/actualiza automáticamente en ERPNext Account
account = frappe.get_doc("Plan Cuentas Bolivia", "1111")
account.company = "Mi Empresa"
account.save()  # Se sincroniza a ERPNext Account
```

### Mapeo de Tipos

| Plan Cuentas Bolivia | ERPNext Account |
|---------------------|-----------------|
| Activo | Asset |
| Pasivo | Liability |
| Patrimonio | Equity |
| Ingreso | Income |
| Egreso | Expense |
| Costo de Ventas | Cost of Goods Sold |

## API Whitelisted

### `get_chart_of_accounts(company=None)`

Obtiene el plan de cuentas organizado jerárquicamente.

**Parámetros:**
- `company` (opcional): Filtrar por empresa

**Retorna:**
```json
[
  {
    "name": "1",
    "account_number": "1",
    "account_name": "ACTIVO",
    "is_group": 1,
    "children": [
      {
        "name": "11",
        "account_number": "11",
        "account_name": "ACTIVO CORRIENTE",
        "is_group": 1,
        "children": [...]
      }
    ]
  }
]
```

### `import_from_erpnext(company)`

Importa cuentas desde ERPNext Account.

**Parámetros:**
- `company` (requerido): Empresa

**Retorna:**
```json
{
  "success": true,
  "created": 15,
  "updated": 5,
  "errors": []
}
```

## Fixtures

El módulo incluye **75+ cuentas** pre-configuradas para Bolivia:

### Cuentas Principales

- 1 - ACTIVO (30 sub-cuentas)
- 2 - PASIVO (20 sub-cuentas)
- 3 - PATRIMONIO (5 sub-cuentas)
- 4 - INGRESOS (5 sub-cuentas)
- 5 - EGRESOS (15 sub-cuentas)

### Cargar Fixtures

```bash
# Dentro del contenedor Frappe
bench --site [sitename] migrate
```

Los fixtures se cargan automáticamente durante la instalación de la app.

## JavaScript (Frontend)

### Funcionalidades del Formulario

**Botones disponibles:**
- 📊 **Ver Balance**: Muestra débito, crédito y balance de la cuenta
- 🔄 **Sincronizar a ERPNext**: Fuerza sincronización manual
- 🌳 **Ver Árbol de Cuentas**: Visualización jerárquica
- 📥 **Importar desde ERPNext**: Importación masiva (solo System Manager)

**Auto-completado:**
- Tipo raíz se determina automáticamente según primer dígito
- Sugerencias de tipo de cuenta según clasificación
- Validación en tiempo real

## Tests

### Ejecutar Tests

```bash
# Todos los tests
bench --site [sitename] run-tests --app nexo_bolivia --module plan_cuentas_bolivia

# Test específico
bench --site [sitename] run-tests nexo_bolivia.nexo_bolivia.doctype.plan_cuentas_bolivia.test_plan_cuentas_bolivia.TestPlanCuentasBolivia.test_create_root_account
```

### Cobertura de Tests

- ✅ Creación de cuentas raíz y hijas
- ✅ Validación de formato de número
- ✅ Validación de primer dígito (1-5)
- ✅ Auto-determinación de tipo raíz
- ✅ Validación de jerarquía
- ✅ Cuentas con hijos deben ser grupo
- ✅ Unicidad de número de cuenta
- ✅ Balance debe ser (Débito/Crédito)
- ✅ Fixtures cargados correctamente
- ✅ Cuentas fiscales Bolivia

## Integración con Módulos

### Facturación (IVA, IT)

```python
# Obtener cuenta IVA Crédito Fiscal
iva_cf = frappe.get_doc("Plan Cuentas Bolivia", "1141")

# Obtener cuenta IVA por Pagar
iva_pagar = frappe.get_doc("Plan Cuentas Bolivia", "2121")
```

### Nómina

```python
# Cuenta aportes AFP
afp = frappe.get_doc("Plan Cuentas Bolivia", "2132")

# Cuenta aguinaldo
aguinaldo = frappe.get_doc("Plan Cuentas Bolivia", "2133")
```

## Permisos

| Role | Create | Read | Write | Delete |
|------|--------|------|-------|--------|
| System Manager | ✅ | ✅ | ✅ | ✅ |
| Accounts Manager | ✅ | ✅ | ✅ | ✅ |
| Accounts User | ❌ | ✅ | ❌ | ❌ |

## Roadmap

### Próximas Funcionalidades

- [ ] Reportes de balance por cuenta
- [ ] Exportación a formatos SIN
- [ ] Comparativos de gestiones
- [ ] Dashboard de análisis contable
- [ ] Integración con libros contables oficiales
- [ ] Validación automática de asientos

## Soporte

**Autor**: Aero
**Versión**: 0.1.0
**Licencia**: GNU GPL v3

---

**Documentación actualizada**: Diciembre 2024
