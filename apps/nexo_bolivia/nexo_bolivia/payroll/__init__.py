# Payroll Module for Bolivia
# Módulo de Nómina para Bolivia

from .salary import calculate_base_salary, calculate_overtime, calculate_seniority_bonus
from .afp import calculate_afp, get_afp_breakdown, AFP_RATE
from .rc_iva import calculate_rc_iva, get_rc_iva_table
from .aguinaldo import calculate_aguinaldo, calculate_double_aguinaldo, is_eligible_for_double_aguinaldo
from .prima import calculate_prima_anual

__all__ = [
    'calculate_base_salary',
    'calculate_overtime',
    'calculate_seniority_bonus',
    'calculate_afp',
    'get_afp_breakdown',
    'AFP_RATE',
    'calculate_rc_iva',
    'get_rc_iva_table',
    'calculate_aguinaldo',
    'calculate_double_aguinaldo',
    'is_eligible_for_double_aguinaldo',
    'calculate_prima_anual',
]
