// Copyright (c) 2024, Aero and contributors
// For license information, please see license.txt

frappe.ui.form.on('Plan Cuentas Bolivia', {
    refresh: function(frm) {
        // Agregar botones personalizados
        if (!frm.is_new()) {
            // Botón para ver balance
            frm.add_custom_button(__('Ver Balance'), function() {
                show_account_balance(frm);
            }, __('Acciones'));

            // Botón para sincronizar con ERPNext
            if (frm.doc.company) {
                frm.add_custom_button(__('Sincronizar a ERPNext'), function() {
                    sync_to_erpnext(frm);
                }, __('Acciones'));
            }
        }

        // Botón para importar desde ERPNext
        if (frappe.user.has_role('System Manager')) {
            frm.add_custom_button(__('Importar desde ERPNext'), function() {
                import_from_erpnext();
            }, __('Herramientas'));
        }

        // Mostrar árbol de cuentas
        if (frm.doc.is_group) {
            frm.add_custom_button(__('Ver Árbol de Cuentas'), function() {
                show_account_tree(frm);
            });
        }

        // Configurar filtros
        setup_filters(frm);
    },

    account_number: function(frm) {
        // Auto-determinar tipo raíz según primer dígito
        if (frm.doc.account_number && frm.doc.account_number.length > 0) {
            const first_digit = frm.doc.account_number[0];
            const root_types = {
                '1': 'Activo',
                '2': 'Pasivo',
                '3': 'Patrimonio',
                '4': 'Ingreso',
                '5': 'Egreso'
            };

            if (root_types[first_digit] && !frm.doc.root_type) {
                frm.set_value('root_type', root_types[first_digit]);
            }

            // Sugerir tipo de cuenta
            if (!frm.doc.account_type) {
                if (first_digit === '1') frm.set_value('account_type', 'Activo');
                else if (first_digit === '2') frm.set_value('account_type', 'Pasivo');
                else if (first_digit === '3') frm.set_value('account_type', 'Patrimonio');
                else if (first_digit === '4') frm.set_value('account_type', 'Ingreso');
                else if (first_digit === '5') frm.set_value('account_type', 'Egreso');
            }
        }
    },

    parent_account: function(frm) {
        // Al seleccionar cuenta padre, sugerir número de cuenta
        if (frm.doc.parent_account && !frm.doc.account_number) {
            frappe.db.get_value('Plan Cuentas Bolivia', frm.doc.parent_account, 'account_number')
                .then(r => {
                    if (r.message && r.message.account_number) {
                        // Sugerir el siguiente número
                        const parent_number = r.message.account_number;
                        frappe.msgprint(__('La cuenta debe comenzar con: ') + parent_number);
                    }
                });
        }
    },

    is_group: function(frm) {
        // Si no es grupo, no puede tener cuenta padre en algunos casos
        if (!frm.doc.is_group) {
            // Verificar si tiene hijos
            frappe.call({
                method: 'frappe.client.get_count',
                args: {
                    doctype: 'Plan Cuentas Bolivia',
                    filters: {
                        parent_account: frm.doc.name
                    }
                },
                callback: function(r) {
                    if (r.message > 0) {
                        frappe.msgprint({
                            title: __('Advertencia'),
                            indicator: 'orange',
                            message: __('Esta cuenta tiene {0} cuenta(s) hija(s). Debe ser una cuenta de grupo.', [r.message])
                        });
                        frm.set_value('is_group', 1);
                    }
                }
            });
        }
    }
});

function setup_filters(frm) {
    // Filtro para cuenta padre - solo mostrar cuentas de grupo
    frm.set_query('parent_account', function() {
        return {
            filters: {
                'is_group': 1,
                'disabled': 0
            }
        };
    });

    // Filtro para empresa
    frm.set_query('company', function() {
        return {
            filters: {
                'country': 'Bolivia'
            }
        };
    });
}

function show_account_balance(frm) {
    frappe.call({
        method: 'get_balance',
        doc: frm.doc,
        callback: function(r) {
            if (r.message) {
                const balance = r.message;
                frappe.msgprint({
                    title: __('Balance de Cuenta: {0}', [frm.doc.account_name]),
                    message: `
                        <table class="table table-bordered">
                            <tr>
                                <th>Débito</th>
                                <td>${format_currency(balance.debit, frm.doc.account_currency)}</td>
                            </tr>
                            <tr>
                                <th>Crédito</th>
                                <td>${format_currency(balance.credit, frm.doc.account_currency)}</td>
                            </tr>
                            <tr>
                                <th>Balance</th>
                                <td><strong>${format_currency(balance.balance, frm.doc.account_currency)}</strong></td>
                            </tr>
                        </table>
                    `
                });
            }
        }
    });
}

function sync_to_erpnext(frm) {
    frappe.confirm(
        __('¿Desea sincronizar esta cuenta con ERPNext?'),
        function() {
            frappe.call({
                method: 'sync_to_erpnext_account',
                doc: frm.doc,
                callback: function(r) {
                    frappe.show_alert({
                        message: __('Cuenta sincronizada exitosamente'),
                        indicator: 'green'
                    });
                    frm.reload_doc();
                }
            });
        }
    );
}

function import_from_erpnext() {
    const d = new frappe.ui.Dialog({
        title: __('Importar Plan de Cuentas desde ERPNext'),
        fields: [
            {
                label: __('Empresa'),
                fieldname: 'company',
                fieldtype: 'Link',
                options: 'Company',
                reqd: 1,
                get_query: function() {
                    return {
                        filters: {
                            'country': 'Bolivia'
                        }
                    };
                }
            }
        ],
        primary_action_label: __('Importar'),
        primary_action(values) {
            frappe.call({
                method: 'nexo_bolivia.nexo_bolivia.doctype.plan_cuentas_bolivia.plan_cuentas_bolivia.import_from_erpnext',
                args: {
                    company: values.company
                },
                callback: function(r) {
                    if (r.message) {
                        const result = r.message;
                        let message = `
                            <p>Importación completada:</p>
                            <ul>
                                <li>Creadas: ${result.created}</li>
                                <li>Actualizadas: ${result.updated}</li>
                            </ul>
                        `;

                        if (result.errors && result.errors.length > 0) {
                            message += '<p><strong>Errores:</strong></p><ul>';
                            result.errors.forEach(error => {
                                message += `<li>${error}</li>`;
                            });
                            message += '</ul>';
                        }

                        frappe.msgprint({
                            title: __('Resultado de Importación'),
                            message: message,
                            indicator: result.errors.length > 0 ? 'orange' : 'green'
                        });

                        d.hide();
                    }
                }
            });
        }
    });
    d.show();
}

function show_account_tree(frm) {
    frappe.route_options = {
        "company": frm.doc.company,
        "root_type": frm.doc.root_type
    };
    frappe.set_route("Tree", "Plan Cuentas Bolivia");
}
