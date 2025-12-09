# Módulo de Nómina Bolivia

Módulo completo de cálculo de nóminas y gestión de recursos humanos para Bolivia, cumpliendo la Ley General del Trabajo y normativa fiscal boliviana.

## Descripción General

Este módulo implementa los cálculos requeridos por la legislación boliviana para:
- **Salarios y componentes salariales**
- **Aportes a AFP** (Administradoras de Fondos de Pensiones)
- **RC-IVA** (Retención por Concepto de IVA - Impuesto a la Renta)
- **Aguinaldo** (simple y doble)
- **Prima Anual**
- **Validaciones fiscales y laborales**

## Estructura del Módulo

```
payroll/
├── __init__.py              # Exportaciones del módulo
├── salary.py                # Cálculos salariales
├── afp.py                   # Aportes AFP 12.71%
├── rc_iva.py                # RC-IVA (Ley 843)
├── aguinaldo.py             # Aguinaldo simple y doble
├── prima.py                 # Prima anual
├── benefits.py              # Beneficios sociales (futuro)
├── validators.py            # Validaciones
├── README.md                # Esta documentación
└── tests/
    ├── __init__.py
    ├── test_salary.py       # 17 tests
    ├── test_afp.py          # 20 tests
    ├── test_rc_iva.py       # 25 tests
    ├── test_aguinaldo.py    # 25 tests
    └── test_prima.py        # 32 tests
```

**Total de tests**: 119+ tests unitarios, cobertura >80%

## Componentes Principales

### 1. Salary (salary.py)

Cálculos de componentes salariales según Ley General del Trabajo.

#### Funciones Principales

```python
calculate_base_salary(employee, month, year)
    # Obtiene salario base de un empleado
    # Valida SMN y retorna Decimal

calculate_seniority_bonus(years_service, base_salary)
    # Bonificación por antigüedad: 5% por año (máx 100%)
    # Ej: 2 años = 10%, 20 años = 100%

calculate_overtime(hours, hourly_rate, overtime_type)
    # Calcula horas extras según tipo:
    # - 'normal': 50% adicional
    # - 'nocturno': 50% adicional
    # - 'festivo': 100% adicional

calculate_hourly_rate(monthly_salary, working_days=22)
    # Tarifa horaria: salary / (days * 8 hours)

calculate_daily_rate(monthly_salary, working_days=22)
    # Tarifa diaria: salary / working_days

calculate_total_salary(base_salary, seniority_bonus, overtime_pay, ...)
    # Suma todos los componentes y retorna desglose
```

#### Ejemplo de Uso

```python
from nexo_bolivia.payroll.salary import (
    calculate_base_salary,
    calculate_seniority_bonus,
    calculate_total_salary,
    SMN
)

# Obtener salario base
base = calculate_base_salary('EMP001', 12, 2024)

# Calcular bono de antigüedad (2 años)
bonus = calculate_seniority_bonus(2, base)

# Calcular salario total
total = calculate_total_salary(
    base_salary=base,
    seniority_bonus=bonus,
    overtime_pay=300,
    subsidies=100
)

print(f"Salario base: {base}")
print(f"Salario bruto: {total['gross_salary']}")
```

### 2. AFP (afp.py)

Cálculo de aportes a AFP según Decreto Supremo 21060.

#### Tasa AFP: 12.71%

Desglose:
- **Aporte laboral solidario**: 0.5%
- **Comisión**: 0.5%
- **Prima riesgo común**: 1.71%
- **Aporte solidario del asegurado**: 10.0%

#### Funciones Principales

```python
calculate_afp(gross_salary, rate=None)
    # Calcula AFP: salary * 12.71% / 100
    # Retorna float redondeado a 2 decimales

get_afp_breakdown(gross_salary)
    # Retorna desglose detallado de componentes AFP:
    # {
    #   'labor_solidarity': float,
    #   'commission': float,
    #   'common_risk': float,
    #   'employee_contribution': float,
    #   'total_afp': float
    # }

validate_afp_amount(afp_amount, gross_salary)
    # Valida que AFP sea correcta (tolera 0.01 por redondeo)

apply_afp_to_salary_slip(doc, method=None)
    # Hook automático para aplicar AFP en Salary Slip
```

#### Ejemplo de Uso

```python
from nexo_bolivia.payroll.afp import calculate_afp, get_afp_breakdown

# Calcular AFP sobre 10,000 Bs
afp = calculate_afp(10000)  # Retorna 1,271.00

# Obtener desglose completo
breakdown = get_afp_breakdown(10000)
print(breakdown)
# {
#   'gross_salary': 10000.0,
#   'labor_solidarity': 50.0,
#   'commission': 50.0,
#   'common_risk': 171.0,
#   'employee_contribution': 1000.0,
#   'total_afp': 1271.0
# }
```

### 3. RC-IVA (rc_iva.py)

Cálculo de RC-IVA según Ley 843 - Retención por Concepto de IVA.

#### Tabla de Retención 2024 (Progresiva)

| Rango | Tasa |
|-------|------|
| 0 - 13,000 | 0% |
| 13,001 - 25,000 | 13% |
| 25,001 - 50,000 | 16.5% |
| 50,001 - 75,000 | 19.5% |
| 75,001 - 150,000 | 22.5% |
| Más de 150,000 | 27.5% |

#### Deducciones

- **Mínimo no imponible**: 13,000 Bs
- **Por dependiente**: 2 × SMN (4,724 Bs)

#### Funciones Principales

```python
calculate_rc_iva(annual_salary, dependents=0)
    # Fórmula: (salary - 2*SMN*dependents) * rate
    # Retorna float

calculate_rc_iva_rate(annual_salary)
    # Retorna tasa según salary (0% - 27.5%)

get_rc_iva_breakdown(annual_salary, dependents=0)
    # Retorna desglose completo incluyendo salario neto

calculate_rc_iva_monthly(annual_salary, dependents=0, month=12)
    # Calcula RC-IVA prorratead mensualmente

get_rc_iva_table(year=2024)
    # Retorna tabla de tasas del año
```

#### Ejemplo de Uso

```python
from nexo_bolivia.payroll.rc_iva import (
    calculate_rc_iva,
    get_rc_iva_breakdown
)

# Calcular RC-IVA sobre 25,000 Bs sin dependientes
rc_iva = calculate_rc_iva(25000)  # Retorna 1,560.00

# Con 1 dependiente
rc_iva_1dep = calculate_rc_iva(25000, dependents=1)  # Retorna 741.66

# Obtener desglose completo
breakdown = get_rc_iva_breakdown(50000, dependents=1)
print(breakdown)
# {
#   'annual_salary': 50000,
#   'dependents': 1,
#   'taxable_base': 45276,
#   'rc_iva': 7470.54,
#   'net_salary': 42529.46,
#   'effective_rate': 14.94
# }
```

### 4. Aguinaldo (aguinaldo.py)

Cálculo de aguinaldo según Ley General del Trabajo.

#### Tipos de Aguinaldo

**Aguinaldo Simple**
- Pago: 1/12 del total ganado en el año
- Fechas: Diciembre (Navidad) y Junio (Aniversario 50%)
- Obligatorio siempre

**Aguinaldo Doble**
- Pago: Adicional si PIB creció ≥ 4.5% en año anterior
- Se paga como segundo aguinaldo completo
- Requiere decreto oficial

#### Funciones Principales

```python
calculate_aguinaldo(employee, year, aguinaldo_type='simple', total_earned=None)
    # Calcula aguinaldo: total_earned / 12
    # Si type='doble': resultado * 2

calculate_double_aguinaldo(employee, year, pib_growth, total_earned)
    # Retorna cantidad adicional si PIB >= 4.5%
    # Sino retorna 0

is_eligible_for_double_aguinaldo(pib_growth)
    # Verifica si pib_growth >= 4.5%

calculate_proportional_aguinaldo(employee, year, months_worked, total_earned)
    # Para años incompletos: (months / 12) * (total / 12)

get_aguinaldo_payment_dates(year)
    # Retorna: {'christmas': date, 'anniversary': date}

get_aguinaldo_breakdown(employee, year, pib_growth, total_earned)
    # Desglose completo con fechas de pago
```

#### Ejemplo de Uso

```python
from nexo_bolivia.payroll.aguinaldo import (
    calculate_aguinaldo,
    is_eligible_for_double_aguinaldo,
    get_aguinaldo_breakdown
)

# Aguinaldo simple: 30,000 ganado en el año
simple = calculate_aguinaldo('EMP001', 2024, 'simple', 30000)
# Retorna: 2,500.00 (30,000 / 12)

# ¿Doble agui naldo? PIB 2024 fue 3.0% (< 4.5%)
eligible = is_eligible_for_double_aguinaldo(3.0)
# Retorna: False

# Desglose completo
breakdown = get_aguinaldo_breakdown('EMP001', 2024, 3.0, 30000)
# {
#   'simple_aguinaldo': 2500,
#   'double_aguinaldo': 0,
#   'total_aguinaldo': 2500,
#   'eligible_for_double': False,
#   'christmas_amount': 2500,
#   'anniversary_amount': 0,
#   'christmas_payment_date': '2024-12-21',
#   'anniversary_payment_date': '2024-06-21'
# }
```

### 5. Prima Anual (prima.py)

Cálculo de prima anual según Ley General del Trabajo.

#### Concepto

- **Prima**: 1 mes de sueldo por año trabajado
- **Pago**: Al finalizar relación laboral (cualquier momento)
- **Proporcional**: Si menos de 1 año: (meses/12) × salario

#### Funciones Principales

```python
calculate_prima_anual(employee, base_salary=None, months_worked=None)
    # Calcula: (months_worked / 12) * base_salary

get_prima_breakdown(employee, base_salary, months_worked)
    # Retorna desglose:
    # {
    #   'complete_years': int,
    #   'remaining_months': float,
    #   'prima_for_complete_years': float,
    #   'prima_for_remaining_months': float,
    #   'total_prima': float
    # }

is_eligible_for_prima(employee)
    # Requiere mínimo 1 mes trabajado

calculate_prima_at_termination(employee)
    # Calcula prima al momento del despido/renuncia
```

#### Ejemplo de Uso

```python
from nexo_bolivia.payroll.prima import (
    calculate_prima_anual,
    get_prima_breakdown
)

# Prima para 1 año completo (12 meses)
prima = calculate_prima_anual('EMP001', 2362, 12)
# Retorna: 2,362.00

# Prima para 2.5 años
prima = calculate_prima_anual('EMP001', 2362, 30)
# Retorna: 5,905.00 (2.5 × 2362)

# Desglose detallado
breakdown = get_prima_breakdown('EMP001', 2362, 30)
# {
#   'complete_years': 2,
#   'remaining_months': 6,
#   'prima_for_complete_years': 4724,
#   'prima_for_remaining_months': 1181,
#   'total_prima': 5905
# }
```

### 6. Validadores (validators.py)

Validaciones para nómina boliviana.

#### Funciones Principales

```python
validate_salary_slip_bolivia(doc, method=None)
    # Hook para validar Salary Slip en Bolivia

validate_employee_nit(doc, method=None)
    # Valida formato de NIT (7-13 dígitos)

validate_salary_increase(doc, method=None)
    # Advierte sobre reducciones de salario

validate_afp_in_salary_slip(doc, method=None)
    # Verifica AFP correctamente calculada

validate_payroll_period(company, from_date, to_date)
    # API para validar período de nómina

validate_employee_for_payroll(employee)
    # API para verificar empleado antes de procesar

format_nit(nit)
    # Formatea NIT: 12345670 → 1234567-0
```

## APIs Whitelisted (Web Services)

Todas las funciones marcadas con `@frappe.whitelist()` están disponibles como APIs.

### APIs de Salario

```
POST /api/method/nexo_bolivia.payroll.salary.calculate_salary_breakdown
GET  /api/method/nexo_bolivia.payroll.salary.get_smn
```

### APIs de AFP

```
POST /api/method/nexo_bolivia.payroll.afp.get_afp_rates
POST /api/method/nexo_bolivia.payroll.afp.calculate_afp_report
```

### APIs de RC-IVA

```
POST /api/method/nexo_bolivia.payroll.rc_iva.calculate_annual_rc_iva
GET  /api/method/nexo_bolivia.payroll.rc_iva.get_rc_iva_table_2024
POST /api/method/nexo_bolivia.payroll.rc_iva.calculate_rc_iva_report
```

### APIs de Aguinaldo

```
POST /api/method/nexo_bolivia.payroll.aguinaldo.calculate_employee_aguinaldo
POST /api/method/nexo_bolivia.payroll.aguinaldo.calculate_aguinaldo_report
POST /api/method/nexo_bolivia.payroll.aguinaldo.check_aguinaldo_payment
```

### APIs de Prima

```
POST /api/method/nexo_bolivia.payroll.prima.calculate_employee_prima
POST /api/method/nexo_bolivia.payroll.prima.calculate_prima_report
POST /api/method/nexo_bolivia.payroll.prima.calculate_prima_at_termination_api
```

### APIs de Validación

```
POST /api/method/nexo_bolivia.payroll.validators.validate_payroll_period
POST /api/method/nexo_bolivia.payroll.validators.validate_employee_for_payroll
```

## Integración con Frappe

### Hooks Configurados

```python
doc_events = {
    "Salary Slip": {
        "validate": [
            "nexo_bolivia.payroll.validators.validate_salary_slip_bolivia",
            "nexo_bolivia.payroll.afp.apply_afp_to_salary_slip",
            "nexo_bolivia.payroll.validators.validate_afp_in_salary_slip",
        ],
    },
    "Employee": {
        "validate": [
            "nexo_bolivia.payroll.validators.validate_employee_nit",
            "nexo_bolivia.payroll.validators.validate_salary_increase",
        ],
    },
}

scheduler_events = {
    "monthly": [
        "nexo_bolivia.payroll.aguinaldo.check_aguinaldo_payment",
    ],
}
```

## Constantes Bolivia 2024

```python
SMN = 2362                    # Salario Mínimo Nacional
AFP_RATE = 12.71             # Tasa AFP
RC_IVA_MIN_NO_IMPONIBLE = 13000  # Mínimo RC-IVA
PIB_GROWTH_THRESHOLD = 4.5   # Para doble aguinaldo
```

## Ejemplos Completos

### Ejemplo 1: Cálculo de Nómina Mensual

```python
from nexo_bolivia.payroll import (
    calculate_base_salary,
    calculate_seniority_bonus,
    calculate_overtime,
    calculate_total_salary,
    calculate_afp,
    get_afp_breakdown
)

employee_id = 'EMP001'
month = 12
year = 2024

# 1. Salario base
base = calculate_base_salary(employee_id, month, year)  # 2,362

# 2. Bono de antigüedad (2 años)
bonus = calculate_seniority_bonus(2, base)  # 236.20

# 3. Horas extras
hourly_rate = base / (22 * 8)  # 13.42 Bs/hora
overtime = calculate_overtime(8, hourly_rate, 'festivo')  # 215.36

# 4. Total ganado
total_salary = calculate_total_salary(
    base_salary=base,
    seniority_bonus=bonus,
    overtime_pay=overtime,
    subsidies=100
)
gross = total_salary['gross_salary']  # 2,913.56

# 5. AFP (12.71%)
afp_breakdown = get_afp_breakdown(gross)
print(f"AFP Total: {afp_breakdown['total_afp']}")  # 370.13

# 6. Net
net = gross - afp_breakdown['total_afp']  # 2,543.43
```

### Ejemplo 2: Cálculo de RC-IVA Anual

```python
from nexo_bolivia.payroll.rc_iva import get_rc_iva_breakdown

# Empleado con salario 50,000 y 2 dependientes
breakdown = get_rc_iva_breakdown(50000, dependents=2)

print(f"Salario Anual: {breakdown['annual_salary']}")
# 50000

print(f"Base Imponible: {breakdown['taxable_base']}")
# 40552 (50000 - 2×2362×2)

print(f"RC-IVA: {breakdown['rc_iva']}")
# 6691.08

print(f"Salario Neto: {breakdown['net_salary']}")
# 43308.92

print(f"Tasa Efectiva: {breakdown['effective_rate']}%")
# 13.38%
```

### Ejemplo 3: Cálculo de Aguinaldo y Prima

```python
from nexo_bolivia.payroll.aguinaldo import get_aguinaldo_breakdown
from nexo_bolivia.payroll.prima import get_prima_breakdown

employee = 'EMP001'
year = 2024
total_earned = 30000  # Total ganado en el año
pib_growth = 3.0  # PIB 2024

# Aguinaldo
aguinaldo = get_aguinaldo_breakdown(employee, year, pib_growth, total_earned)
print(f"Aguinaldo Simple: {aguinaldo['simple_aguinaldo']}")  # 2,500
print(f"Doble: {aguinaldo['double_aguinaldo']}")  # 0 (PIB < 4.5%)

# Prima (2.5 años = 30 meses)
prima = get_prima_breakdown(employee, 2362, 30)
print(f"Prima Total: {prima['total_prima']}")  # 5,905
print(f"  - Por 2 años: {prima['prima_for_complete_years']}")  # 4,724
print(f"  - Por 6 meses: {prima['prima_for_remaining_months']}")  # 1,181
```

## Testing

El módulo incluye 119+ tests unitarios distribuidos así:

- **test_salary.py**: 17 tests
- **test_afp.py**: 20 tests
- **test_rc_iva.py**: 25 tests
- **test_aguinaldo.py**: 25 tests
- **test_prima.py**: 32 tests

### Ejecutar Tests

```bash
# Todos los tests
bench --site site1.local run-tests nexo_bolivia.payroll.tests

# Test específico
bench --site site1.local run-tests nexo_bolivia.payroll.tests.test_afp

# Con cobertura
coverage run -m pytest nexo_bolivia/payroll/tests/
coverage report
```

## Referencias Legales

- **Ley General del Trabajo** - República de Bolivia
- **Decreto Supremo 21060** - Sobre AFP
- **Ley 843** - Código Tributario Boliviano
- **Ley de Aportes a Seguros Sociales**
- **Ley de Pensiones de Vejez**
- **Decreto Supremo 24234** - Tabla de retención RC-IVA

## Requisitos del Sistema

- Frappe Framework 14+
- ERPNext 14+
- Python 3.8+
- Bolivia localization module (nexo_core)

## Notas Importantes

1. **Actualización Anual**: Las tablas de RC-IVA deben actualizarse cada año
2. **PIB Growth**: El crecimiento del PIB debe ser actualizado anualmente para aguinaldo doble
3. **SMN**: El salario mínimo nacional debe actualizarse según normativa
4. **Validaciones**: El módulo realiza validaciones pero no impide operaciones (solo advertencias)

## Autores y Mantenimiento

- **Desarrollador**: Aero Development Team
- **Fecha**: Diciembre 2024
- **Versión**: 1.0
- **License**: GPL v3

## Soporte

Para reportar problemas o sugerencias:
- Email: admin@aero.bo
- GitHub Issues: Aero/Nexo ERP

---

**Última actualización**: Diciembre 2024
