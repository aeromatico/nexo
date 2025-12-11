# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Basic predictive analytics for sales forecasting and trend detection
Uses simple linear regression for trend analysis
"""

import frappe
import json
from datetime import datetime, timedelta
from frappe.utils import now
import logging

logger = logging.getLogger(__name__)


@frappe.whitelist(methods=['GET'])
def forecast_sales(company=None, periods_ahead=3, lookback_months=12):
    """
    Proyecta ventas futuras basándose en histórico
    Usa regresión lineal simple sobre últimos 12 meses

    Args:
        company (str): Empresa a considerar
        periods_ahead (int): Número de períodos a proyectar
        lookback_months (int): Meses históricos a considerar

    Returns:
        dict: Proyecciones de ventas con nivel de confianza
    """
    try:
        if not company:
            company = frappe.defaults.get_user_default('company')

        # Obtener histórico de ventas por mes
        historical_data = _get_monthly_sales(company, lookback_months)

        if len(historical_data) < 2:
            return {
                'success': False,
                'error': 'Insufficient historical data',
                'forecast': []
            }

        # Aplicar regresión lineal simple
        x_values = list(range(len(historical_data)))
        y_values = [d['sales'] for d in historical_data]

        # Calcular media
        x_mean = sum(x_values) / len(x_values)
        y_mean = sum(y_values) / len(y_values)

        # Calcular pendiente (slope) e intersección
        numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(len(x_values)))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(len(x_values)))

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        intercept = y_mean - slope * x_mean

        # Calcular R² (coeficiente de determinación)
        ss_res = sum((y_values[i] - (slope * x_values[i] + intercept)) ** 2 for i in range(len(x_values)))
        ss_tot = sum((y_values[i] - y_mean) ** 2 for i in range(len(y_values)))

        if ss_tot == 0:
            r_squared = 0
        else:
            r_squared = 1 - (ss_res / ss_tot)

        # Hacer proyecciones
        forecast = []
        last_month = datetime.now()

        for i in range(periods_ahead):
            next_month = last_month + timedelta(days=30)
            x_pred = len(historical_data) + i
            predicted_sales = slope * x_pred + intercept

            forecast.append({
                'period': next_month.strftime('%Y-%m'),
                'predicted_sales': max(0, float(predicted_sales)),  # No valores negativos
                'confidence': round(r_squared * 100, 2),
                'trend': 'upward' if slope > 0 else 'downward'
            })

            last_month = next_month

        return {
            'success': True,
            'forecast': forecast,
            'confidence_level': round(r_squared * 100, 2),
            'slope': round(slope, 2),
            'method': 'Linear Regression'
        }

    except Exception as e:
        logger.error(f"Error forecasting sales: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'forecast': []
        }


@frappe.whitelist(methods=['GET'])
def detect_trends(company=None, months=3, metric='sales'):
    """
    Detecta tendencias (alcista, bajista, estable) en serie de tiempo

    Args:
        company (str): Empresa a considerar
        months (int): Número de meses a analizar
        metric (str): Métrica a analizar (sales, expenses, etc.)

    Returns:
        dict: Análisis de tendencias
    """
    try:
        if not company:
            company = frappe.defaults.get_user_default('company')

        # Obtener datos históricos
        data = _get_monthly_metric(company, metric, months)

        if len(data) < 2:
            return {
                'success': False,
                'error': 'Insufficient data',
                'trend': 'neutral'
            }

        values = [d['value'] for d in data]

        # Analizar últimos 3 puntos
        window_size = min(3, len(values))
        recent = values[-window_size:]

        # Detectar patrón
        if all(recent[i] < recent[i + 1] for i in range(len(recent) - 1)):
            trend = 'upward'
            direction_score = 0.9

        elif all(recent[i] > recent[i + 1] for i in range(len(recent) - 1)):
            trend = 'downward'
            direction_score = 0.9

        else:
            trend = 'stable'
            direction_score = 0.5

        # Calcular velocidad de cambio
        if len(recent) >= 2:
            change_rate = ((recent[-1] - recent[0]) / recent[0] * 100) if recent[0] != 0 else 0
        else:
            change_rate = 0

        return {
            'success': True,
            'trend': trend,
            'direction_score': direction_score,
            'change_rate': round(change_rate, 2),
            'data_points': len(data),
            'metric': metric,
            'recommendation': _get_trend_recommendation(trend, change_rate)
        }

    except Exception as e:
        logger.error(f"Error detecting trends: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'trend': 'neutral'
        }


@frappe.whitelist(methods=['GET'])
def detect_anomalies(company=None, metric='sales', sensitivity=2.0):
    """
    Detecta valores anómalos usando desviación estándar

    Args:
        company (str): Empresa a considerar
        metric (str): Métrica a analizar
        sensitivity (float): Número de desviaciones estándar (default: 2.0 = 95% de confianza)

    Returns:
        dict: Anomalías detectadas
    """
    try:
        if not company:
            company = frappe.defaults.get_user_default('company')

        # Obtener datos históricos (últimos 12 meses)
        data = _get_monthly_metric(company, metric, 12)

        if len(data) < 3:
            return {
                'success': False,
                'error': 'Insufficient data',
                'anomalies': []
            }

        values = [d['value'] for d in data]

        # Calcular media y desviación estándar
        mean = sum(values) / len(values)

        # Calcular varianza
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5  # Raíz cuadrada

        # Detectar anomalías
        threshold = sensitivity * std_dev
        anomalies = []

        for i, value in enumerate(values):
            deviation = abs(value - mean)

            if deviation > threshold:
                anomalies.append({
                    'period': data[i]['period'],
                    'value': float(value),
                    'expected': float(mean),
                    'deviation': round(deviation, 2),
                    'z_score': round((value - mean) / std_dev, 2) if std_dev != 0 else 0,
                    'severity': 'high' if deviation > threshold * 1.5 else 'medium'
                })

        return {
            'success': True,
            'anomalies': anomalies,
            'count': len(anomalies),
            'mean': float(mean),
            'std_dev': float(std_dev),
            'threshold': float(threshold),
            'sensitivity': sensitivity
        }

    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'anomalies': []
        }


@frappe.whitelist(methods=['GET'])
def get_forecast_vs_actual(company=None, months=6):
    """
    Compara predicciones vs resultados reales

    Args:
        company (str): Empresa a considerar
        months (int): Número de meses a comparar

    Returns:
        dict: Comparativa forecast vs actual
    """
    try:
        if not company:
            company = frappe.defaults.get_user_default('company')

        # Obtener datos reales
        actual_data = _get_monthly_sales(company, months)

        # Generar pronósticos históricos (simulado)
        forecast_data = []

        for i, actual in enumerate(actual_data):
            # Simular forecast (media móvil simple)
            if i > 0:
                forecast_value = actual_data[i - 1]['sales'] * 1.05  # Proyección simple +5%
            else:
                forecast_value = actual['sales']

            accuracy = (min(forecast_value, actual['sales']) / max(forecast_value, actual['sales'])) * 100

            forecast_data.append({
                'period': actual['period'],
                'actual': float(actual['sales']),
                'forecast': float(forecast_value),
                'variance': float(actual['sales'] - forecast_value),
                'accuracy': round(accuracy, 2)
            })

        # Calcular MAPE (Mean Absolute Percentage Error)
        mape = sum(abs((d['actual'] - d['forecast']) / d['actual']) for d in forecast_data if d['actual'] != 0) / len(forecast_data) * 100 if forecast_data else 0

        return {
            'success': True,
            'data': forecast_data,
            'mape': round(mape, 2),
            'forecast_accuracy': round(100 - mape, 2)
        }

    except Exception as e:
        logger.error(f"Error comparing forecast vs actual: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'data': []
        }


# Helper functions

def _get_monthly_sales(company, months=12):
    """Obtiene ventas mensuales históricas"""
    result = []

    for i in range(months, 0, -1):
        target_date = datetime.now() - timedelta(days=30 * i)

        # Obtener ventas del mes
        month_start = target_date.replace(day=1)
        if target_date.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)

        sales = frappe.db.get_value(
            'Sales Invoice',
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', month_start.date()],
                'posting_date': ['<=', month_end.date()]
            },
            'SUM(grand_total)'
        )
        sales_amount = sales[0] if sales and sales[0] else 0

        result.append({
            'period': target_date.strftime('%Y-%m'),
            'sales': float(sales_amount)
        })

    return result


def _get_monthly_metric(company, metric, months=12):
    """Obtiene métrica mensual histórica"""
    result = []

    doctype_map = {
        'sales': 'Sales Invoice',
        'expenses': 'Purchase Invoice',
        'orders': 'Sales Order'
    }

    doctype = doctype_map.get(metric, 'Sales Invoice')

    for i in range(months, 0, -1):
        target_date = datetime.now() - timedelta(days=30 * i)

        month_start = target_date.replace(day=1)
        if target_date.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)

        value = frappe.db.get_value(
            doctype,
            {
                'company': company,
                'docstatus': 1,
                'posting_date': ['>=', month_start.date()],
                'posting_date': ['<=', month_end.date()]
            },
            'SUM(grand_total)' if metric == 'sales' else 'COUNT(name)'
        )
        metric_value = value[0] if value and value[0] else 0

        result.append({
            'period': target_date.strftime('%Y-%m'),
            'value': float(metric_value)
        })

    return result


def _get_trend_recommendation(trend, change_rate):
    """Obtiene recomendación basada en tendencia"""
    if trend == 'upward':
        if change_rate > 20:
            return 'Excellent growth. Consider scaling operations.'
        else:
            return 'Positive trend. Continue current strategy.'

    elif trend == 'downward':
        if change_rate < -20:
            return 'Significant decline. Review pricing and marketing.'
        else:
            return 'Negative trend. Consider adjustments.'

    else:
        return 'Stable performance. Monitor for changes.'
