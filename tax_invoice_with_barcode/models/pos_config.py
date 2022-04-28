# -*- coding: utf-8 -*-
from datetime import datetime,date
from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = 'pos.config'
    show_tax_invoice_header = fields.Boolean(string="Show Tax Invoice Header & footer",  )
    invoice_tax_header_logo = fields.Binary(string="Invoice Tax Header Logo",  )
    invoice_tax_footer_logo = fields.Binary(string="Invoice Tax Footer Logo",  )
