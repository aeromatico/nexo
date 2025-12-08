"""
Nexo Bolivia - Configuraciones Específicas de Bolivia
"""

# Configuración de Impuestos
TAXES = {
    "IVA": {
        "rate": 13,
        "name": "Impuesto al Valor Agregado",
        "account": "IVA Fiscal - BOL",
    },
    "IT": {
        "rate": 3,
        "name": "Impuesto a las Transacciones",
        "account": "IT por Pagar - BOL",
    },
    "IUE": {
        "rate": 25,
        "name": "Impuesto sobre las Utilidades de las Empresas",
        "account": "IUE por Pagar - BOL",
    },
}

# Configuración SIN (Sistema de Impuestos Nacionales)
SIN_CONFIG = {
    "api_url": "https://pilotosiat.impuestos.gob.bo",
    "production_url": "https://siat.impuestos.gob.bo",
    "timeout": 30,
    "retry_attempts": 3,
}

# Modalidades de Facturación SIN
SIN_MODALIDADES = {
    1: "Electrónica en Línea",
    2: "Computarizada en Línea",
    3: "Electrónica Masiva",
    4: "Prevalorada Electrónica",
}

# Tipos de Documento de Identidad
DOCUMENT_TYPES = {
    "1": "CI - Cédula de Identidad",
    "2": "CEX - Cédula de Identidad de Extranjero",
    "3": "PAS - Pasaporte",
    "4": "OD - Otro Documento",
    "5": "NIT - Número de Identificación Tributaria",
}

# Plan Contable Base Bolivia
CHART_OF_ACCOUNTS = {
    "1": "ACTIVO",
    "11": "ACTIVO CORRIENTE",
    "111": "DISPONIBILIDADES",
    "1111": "Caja",
    "1112": "Caja Moneda Extranjera",
    "1113": "Bancos",
    "112": "CRÉDITOS",
    "1121": "Cuentas por Cobrar",
    "1122": "Documentos por Cobrar",
    "113": "INVENTARIOS",
    "1131": "Inventario de Mercaderías",
    "1132": "Inventario de Productos Terminados",
    "12": "ACTIVO NO CORRIENTE",
    "2": "PASIVO",
    "21": "PASIVO CORRIENTE",
    "211": "CUENTAS POR PAGAR",
    "2111": "Proveedores",
    "2112": "IVA por Pagar",
    "2113": "IT por Pagar",
    "22": "PASIVO NO CORRIENTE",
    "3": "PATRIMONIO",
    "31": "CAPITAL",
    "32": "RESERVAS",
    "33": "RESULTADOS",
    "4": "INGRESOS",
    "41": "INGRESOS OPERACIONALES",
    "42": "INGRESOS NO OPERACIONALES",
    "5": "EGRESOS",
    "51": "COSTO DE VENTAS",
    "52": "GASTOS OPERACIONALES",
    "53": "GASTOS NO OPERACIONALES",
}

# Formatos de Fecha Bolivia
DATE_FORMATS = {
    "default": "dd/mm/yyyy",
    "long": "dd de MMMM de yyyy",
    "short": "dd/mm/yy",
}

# Días Festivos Bolivia (2024-2025)
HOLIDAYS = [
    {"date": "2024-01-01", "name": "Año Nuevo"},
    {"date": "2024-01-22", "name": "Día del Estado Plurinacional"},
    {"date": "2024-02-12", "name": "Carnaval"},
    {"date": "2024-02-13", "name": "Carnaval"},
    {"date": "2024-03-29", "name": "Viernes Santo"},
    {"date": "2024-05-01", "name": "Día del Trabajo"},
    {"date": "2024-05-30", "name": "Corpus Christi"},
    {"date": "2024-06-21", "name": "Año Nuevo Andino Amazónico"},
    {"date": "2024-08-06", "name": "Día de la Independencia"},
    {"date": "2024-11-02", "name": "Todos los Santos"},
    {"date": "2024-12-25", "name": "Navidad"},
]
