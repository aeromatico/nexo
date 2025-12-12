# Guía de Contribución - Nexo ERP

¡Gracias por tu interés en contribuir a Nexo ERP! 🎉

## Cómo Contribuir

### 1. Fork y Clone

```bash
# Fork el repositorio en GitHub
# Luego clona tu fork
git clone https://github.com/tu-usuario/nexo.git
cd nexo
```

### 2. Crear Branch

```bash
# Siempre crea un branch para tu feature
git checkout -b feature/mi-nueva-feature

# O para un bugfix
git checkout -b fix/descripcion-del-bug
```

### 3. Desarrollar

- Sigue las convenciones de código (ver abajo)
- Escribe tests para tu código
- Documenta tus cambios
- Asegúrate que los tests pasen

### 4. Commit

Usa commits descriptivos siguiendo esta convención:

```
Add: Nueva funcionalidad
Update: Mejora a funcionalidad existente
Fix: Corrección de bug
Docs: Cambios en documentación
Test: Agregar o modificar tests
Refactor: Refactorización de código
Style: Cambios de formato/estilo
```

Ejemplo:
```bash
git commit -m "Add: Integración con API SIN Bolivia"
```

### 5. Push y Pull Request

```bash
git push origin feature/mi-nueva-feature
```

Luego crea un Pull Request en GitHub con:
- Descripción clara de los cambios
- Screenshots si aplica
- Referencias a issues relacionados

## Convenciones de Código

### Python

```python
# Snake case para funciones y variables
def calculate_total_with_iva(amount):
    pass

# PascalCase para clases
class BolivianInvoice:
    pass

# Constantes en MAYÚSCULAS
IVA_RATE = 0.13

# Docstrings en todas las funciones
def process_payment(amount, currency="BOB"):
    """
    Procesa un pago

    Args:
        amount (float): Monto del pago
        currency (str): Moneda (default: BOB)

    Returns:
        dict: Resultado del procesamiento
    """
    pass
```

### JavaScript

```javascript
// Camel case
function formatCurrency(amount) {
    return `Bs ${amount.toFixed(2)}`;
}

// Constantes en UPPER_CASE
const TAX_RATE = 0.13;
```

### Frappe Hooks

```python
# hooks.py debe seguir la estructura de Frappe
doc_events = {
    "Sales Invoice": {
        "before_submit": "path.to.function",
        "on_submit": "path.to.function"
    }
}
```

## Testing

### Ejecutar Tests

```bash
# Todos los tests
docker-compose exec backend bench --site nexo.local run-tests --app nexo_core

# Tests específicos
docker-compose exec backend bench --site nexo.local run-tests \
    nexo_bolivia.tests.test_sin_integration
```

### Escribir Tests

```python
import frappe
import unittest

class TestBolivianTaxes(unittest.TestCase):
    def setUp(self):
        # Preparación
        self.invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": "Test Customer"
        })

    def test_iva_calculation(self):
        """Test cálculo de IVA 13%"""
        result = calculate_iva(100)
        self.assertEqual(result, 13.0)

    def tearDown(self):
        # Limpieza
        frappe.db.rollback()
```

## Estructura de Commits

Mantén commits atómicos y significativos:

✅ **Buenos commits**:
```
Add: Cálculo automático de IVA en facturas
Fix: Error en validación de NIT boliviano
Update: Mejorar performance de libro de ventas
```

❌ **Malos commits**:
```
cambios
fix
update
asdf
```

## Revisión de Código

Tu Pull Request será revisado considerando:

- ✅ Código limpio y bien documentado
- ✅ Tests que pasen
- ✅ Sin errores de linting
- ✅ Documentación actualizada
- ✅ Cumplimiento con normativa Bolivia (si aplica)
- ✅ Compatibilidad multi-tenant

## Preguntas o Problemas

Si tienes dudas:

1. Revisa la documentación en `/docs`
2. Abre un Issue en GitHub
3. Contacta a: admin@aero.bo

## Código de Conducta

- Sé respetuoso con otros contribuidores
- Acepta críticas constructivas
- Enfócate en lo mejor para el proyecto
- Ayuda a otros cuando puedas

## Recursos Útiles

- [PROGRESS.md](./docs/PROGRESS.md) - Progreso de desarrollo (9 fases)
- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - Arquitectura del sistema
- [API_REFERENCE.md](./docs/API_REFERENCE.md) - Referencia de APIs (150+)
- [INSTALLATION.md](./docs/INSTALLATION.md) - Guía de instalación
- [CHANGELOG.md](./CHANGELOG.md) - Historial de versiones
- [README.md](./README.md) - Información general

## Licencia

Al contribuir, aceptas que tu código sea licenciado bajo MIT License.

Ver [LICENSE](./LICENSE) para detalles.

---

¡Gracias por contribuir a Nexo ERP! 🚀🇧🇴
