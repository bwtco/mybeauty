# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, api, models, _
from odoo.tools.float_utils import float_round


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sfda_number = fields.Char(string="Certificate Number", translate=True)
    product_name_arabic = fields.Char(string="Product Name Arabic", translate=True)
    product_tag_ids = fields.Many2many('product.tag', string="Tags")
