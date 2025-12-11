# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""
Analytics and Business Intelligence Module
Provides KPI engine, metrics, forecasting, and alerts
"""

from .kpi_engine import KPIEngine
from .metrics import (
    get_revenue_metrics,
    get_customer_metrics,
    get_operational_metrics
)
from .forecasting import (
    forecast_sales,
    detect_trends,
    detect_anomalies
)
from .alerts import (
    create_alert,
    check_all_alerts,
    get_triggered_alerts
)

__all__ = [
    'KPIEngine',
    'get_revenue_metrics',
    'get_customer_metrics',
    'get_operational_metrics',
    'forecast_sales',
    'detect_trends',
    'detect_anomalies',
    'create_alert',
    'check_all_alerts',
    'get_triggered_alerts',
]
