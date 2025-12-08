# Nexo Bolivia

**Localización Completa para Bolivia - Nexo ERP**

## 🇧🇴 Descripción

`nexo_bolivia` es el módulo de localización que adapta Nexo ERP completamente para Bolivia, incluyendo:

- ✅ Facturación Electrónica SIN
- ✅ Impuestos Bolivianos (IVA 13%, IT 3%, IUE 25%)
- ✅ Plan Contable Boliviano
- ✅ Nómina según Código Laboral
- ✅ Formatos de Documentos Oficiales
- ✅ Integración con Bancos Bolivianos

## Características Principales

### 1. Facturación Electrónica (SIN)

Integración completa con el Sistema de Impuestos Nacionales:

- Generación automática de facturas electrónicas
- Código QR en facturas según normativa
- Sincronización en tiempo real con SIAT
- Anulación de facturas
- Reportes fiscales automáticos

### 2. Impuestos Bolivia

Configuración automática de:

- **IVA 13%**: Impuesto al Valor Agregado
- **IT 3%**: Impuesto a las Transacciones
- **IUE 25%**: Impuesto sobre Utilidades de Empresas
- Cálculos automáticos en facturas
- Libros de compras y ventas IVA

### 3. Plan Contable Boliviano

Plan de cuentas según normativa contable boliviana:

```
1 - ACTIVO
  11 - Activo Corriente
    111 - Disponibilidades
    112 - Créditos
    113 - Inventarios
  12 - Activo No Corriente

2 - PASIVO
  21 - Pasivo Corriente
  22 - Pasivo No Corriente

3 - PATRIMONIO

4 - INGRESOS

5 - EGRESOS
```

### 4. Nómina Boliviana

Cálculos según legislación laboral:

- Sueldos y salarios
- Aguinaldo (doble aguinaldo cuando aplique)
- Prima anual
- Aportes AFP (12.71%)
- Aportes patronales
- RC-IVA
- Finiquitos y liquidaciones

### 5. Configuración Regional

- **Moneda**: BOB (Bolivianos)
- **Timezone**: America/La_Paz
- **Formato de fecha**: dd/mm/yyyy
- **Formato numérico**: #.###,## (punto miles, coma decimales)
- **Departamentos**: 9 departamentos de Bolivia
- **Días festivos**: Calendario boliviano

## Estructura

```
nexo_bolivia/
├── config/              # Configuraciones Bolivia
│   └── bolivia.py      # Impuestos, plan contable, etc.
├── fixtures/           # Datos iniciales
├── sin_integration/    # Integración SIN
│   ├── invoice.py     # Facturación electrónica
│   ├── qr.py          # Generación de QR
│   └── sync.py        # Sincronización
├── tax_engine/         # Motor de impuestos
├── public/             # Assets estáticos
├── templates/          # Templates de impresión
├── hooks.py           # Configuración de hooks
└── utils.py           # Funciones utilitarias
```

## Instalación

```bash
# Dentro del contenedor Frappe
bench get-app /home/frappe/frappe-bench/apps/nexo_bolivia
bench --site [sitename] install-app nexo_bolivia
```

## Configuración

### Variables de Entorno

```bash
# En .env
SIN_API_URL=https://pilotosiat.impuestos.gob.bo
SIN_NIT=tu_nit_aqui
SIN_TOKEN=tu_token_sin
SIN_MODALIDAD=1
```

### Primera Configuración

1. Configurar NIT de la empresa
2. Obtener credenciales SIN
3. Configurar modalidad de facturación
4. Configurar punto de venta
5. Sincronizar con SIAT

## Uso

### Factura Electrónica

```python
# La facturación electrónica es automática
# Al hacer submit de una Sales Invoice:
doc = frappe.get_doc("Sales Invoice", invoice_name)
doc.submit()  # Automáticamente genera factura SIN
```

### Cálculo de Impuestos

```python
from nexo_bolivia.utils import calculate_iva, calculate_it

# Calcular IVA 13%
iva = calculate_iva(1000)  # 130

# Calcular IT 3%
it = calculate_it(1000)  # 30
```

### Validar NIT

```python
from nexo_bolivia.utils import validate_nit, format_nit

# Validar NIT
is_valid = validate_nit("1234567890")

# Formatear NIT
nit_formatted = format_nit("1234567890")  # "123456789-0"
```

## Reportes Disponibles

- **Libro de Ventas IVA**: Registro de ventas con IVA
- **Libro de Compras IVA**: Registro de compras con IVA
- **Reporte IT Mensual**: Declaración IT
- **Reporte IUE Anual**: Declaración IUE
- **Planilla de Sueldos**: Nómina mensual

## Compliance

Este módulo cumple con:

- ✅ Normativa SIN (Sistema Impuestos Nacionales)
- ✅ Código Laboral Boliviano
- ✅ Normas Contables Bolivianas
- ✅ Resoluciones Administrativas ADSIB

## Soporte

Autor: **Aero**
Email: admin@aero.bo
Versión: 0.1.0
Licencia: GNU GPL v3

## TODO

- [ ] Implementar API completa SIN
- [ ] Agregar más códigos de actividad económica
- [ ] Integración con bancos bolivianos
- [ ] Conversión de números a letras en español
- [ ] Reportes fiscales adicionales
- [ ] Validación dígito verificador NIT
