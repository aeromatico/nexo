# Copyright (c) 2024, Aero and contributors
# For license information, please see license.txt

"""Data Aggregation for Data Warehouse"""

import frappe
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def aggregate_sales_data():
    """
    Agrega datos de ventas diariamente (ejecutado por scheduler)
    Llamado diariamente para consolidar datos de ventas
    """
    try:
        companies = frappe.get_all('Company', fields=['name'])

        for company_doc in companies:
            company = company_doc['name']

            # Agregar datos de ayer
            yesterday = datetime.now().date() - timedelta(days=1)

            # Obtener todas las ventas del día
            invoices = frappe.get_all(
                'Sales Invoice',
                filters={
                    'company': company,
                    'docstatus': 1,
                    'posting_date': yesterday
                },
                fields=['name', 'customer', 'grand_total', 'posting_date']
            )

            if not invoices:
                continue

            # Agregar por día
            total_sales = sum(inv['grand_total'] for inv in invoices)
            total_count = len(invoices)

            # Crear registro de agregación diaria (si la tabla existe)
            try:
                frappe.get_doc({
                    'doctype': 'Sales Aggregate',
                    'company': company,
                    'aggregate_date': yesterday,
                    'total_sales': total_sales,
                    'transaction_count': total_count
                }).insert()

                logger.info(f"Daily sales aggregation completed for {company} on {yesterday}")

            except frappe.DoesNotExistError:
                logger.info("Sales Aggregate table does not exist, skipping aggregation")

            # Agregar por producto
            _aggregate_sales_by_product(company, yesterday)

            # Agregar por cliente
            _aggregate_sales_by_customer(company, yesterday)

    except Exception as e:
        logger.error(f"Error in aggregate_sales_data: {str(e)}")


def _aggregate_sales_by_product(company, date):
    """Agrega ventas por producto"""
    try:
        sales_items = frappe.get_all(
            'Sales Invoice Item',
            filters={
                'parent': frappe.get_all(
                    'Sales Invoice',
                    filters={
                        'company': company,
                        'docstatus': 1,
                        'posting_date': date
                    },
                    pluck='name'
                )
            },
            group_by='item_code',
            fields=['item_code', 'SUM(qty) as total_qty', 'SUM(amount) as total_amount']
        )

        for item in sales_items:
            try:
                frappe.get_doc({
                    'doctype': 'Sales Product Aggregate',
                    'company': company,
                    'aggregate_date': date,
                    'item_code': item['item_code'],
                    'total_qty': item['total_qty'],
                    'total_amount': item['total_amount']
                }).insert()
            except frappe.DoesNotExistError:
                pass

    except Exception as e:
        logger.error(f"Error aggregating sales by product: {str(e)}")


def _aggregate_sales_by_customer(company, date):
    """Agrega ventas por cliente"""
    try:
        customer_sales = frappe.get_all(
            'Sales Invoice',
            filters={
                'company': company,
                'docstatus': 1,
                'posting_date': date
            },
            group_by='customer',
            fields=['customer', 'SUM(grand_total) as total_sales', 'COUNT(name) as order_count']
        )

        for sale in customer_sales:
            try:
                frappe.get_doc({
                    'doctype': 'Sales Customer Aggregate',
                    'company': company,
                    'aggregate_date': date,
                    'customer': sale['customer'],
                    'total_sales': sale['total_sales'],
                    'order_count': sale['order_count']
                }).insert()
            except frappe.DoesNotExistError:
                pass

    except Exception as e:
        logger.error(f"Error aggregating sales by customer: {str(e)}")


def aggregate_financial_data():
    """Agrega datos financieros mensualmente (ejecutado por scheduler)"""
    try:
        companies = frappe.get_all('Company', fields=['name'])

        for company_doc in companies:
            company = company_doc['name']

            # Obtener primer día del mes anterior
            today = datetime.now().date()
            first_day_current = today.replace(day=1)
            last_day_previous = first_day_current - timedelta(days=1)
            first_day_previous = last_day_previous.replace(day=1)

            # Calcular totales mensuales
            total_income = frappe.db.get_value(
                'Sales Invoice',
                {
                    'company': company,
                    'docstatus': 1,
                    'posting_date': ['>=', first_day_previous],
                    'posting_date': ['<=', last_day_previous]
                },
                'SUM(grand_total)'
            )
            total_income = total_income[0] if total_income else 0

            total_expenses = frappe.db.get_value(
                'Purchase Invoice',
                {
                    'company': company,
                    'docstatus': 1,
                    'posting_date': ['>=', first_day_previous],
                    'posting_date': ['<=', last_day_previous]
                },
                'SUM(grand_total)'
            )
            total_expenses = total_expenses[0] if total_expenses else 0

            # Crear registro de agregación mensual (si la tabla existe)
            try:
                frappe.get_doc({
                    'doctype': 'Financial Aggregate',
                    'company': company,
                    'period_start': first_day_previous,
                    'period_end': last_day_previous,
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'net_profit': total_income - total_expenses
                }).insert()

                logger.info(f"Monthly financial aggregation completed for {company}")

            except frappe.DoesNotExistError:
                logger.info("Financial Aggregate table does not exist, skipping aggregation")

    except Exception as e:
        logger.error(f"Error in aggregate_financial_data: {str(e)}")


@frappe.whitelist(methods=['GET'])
def get_aggregated_data(doctype, company=None, date_from=None, date_to=None):
    """
    Obtiene datos agregados del data warehouse

    Args:
        doctype (str): Tipo de dato agregado (Sales, Financial, etc.)
        company (str): Empresa específica
        date_from (str): Fecha inicio
        date_to (str): Fecha fin

    Returns:
        dict: Datos agregados
    """
    try:
        filters = {}

        if company:
            filters['company'] = company

        if date_from:
            filters['aggregate_date'] = ['>=', date_from]

        if date_to:
            filters['aggregate_date'] = ['<=', date_to]

        # Obtener datos
        data = frappe.get_all(
            doctype,
            filters=filters,
            limit_page_length=1000
        )

        return {
            'success': True,
            'data': data,
            'count': len(data)
        }

    except Exception as e:
        logger.error(f"Error getting aggregated data: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'data': []
        }
