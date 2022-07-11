# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    arabic_name = fields.Char(string="Arabic Name")
    street = fields.Char(translate=True)
    street2 = fields.Char(translate=True)
    city = fields.Char(translate=True)
    pobox = fields.Char(string="P.O.Box")
    invoices_bank_account_id = fields.Many2one(comodel_name='res.partner.bank', ondelete='cascade',
        domain="['|', ('company_id', '=', False), ('company_id', '=', id)]",
        string="Bank Account on Invoices",
        help="Bank Account for invoice reports.")
