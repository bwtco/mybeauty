# -*- coding: utf-8 -*-
from odoo import models, fields, api



class Sales(models.Model):
    _inherit = 'sale.order'

    customer_name = fields.Char(string="Customer Name", required=False, )
    customer_phone = fields.Char(string="Customer Phone", required=False, )
