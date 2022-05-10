# -*- coding: utf-8 -*-
import qrcode
import base64
from io import BytesIO
from datetime import datetime,date

from odoo import models, fields, api



class Account_move(models.Model):
	_inherit = 'account.move'

	cbs_servuces_taxable = fields.Float(string="", required=False, )
	total_taxes = fields.Float(string="", required=False, compute='get_total_taxes')
	total_discount = fields.Float(string="Total Discount",  required=False,compute='get_total_discount' )
	warehouse_name = fields.Char(string="Warehouse Name", required=False,compute='get_warehouse_name' )
	company_seal = fields.Html(string="ختم الشركة",  )
	check_pos = fields.Boolean(string="", compute='check_if_from_pos')
	# my_pos_config = fields.Many2one(comodel_name="pos.config", string="", compute='check_if_from_pos', required=False, )
	customer_name = fields.Char(string="Customer Name", compute='check_if_from_pos', required=False, )
	customer_phone = fields.Char(string="Customer Phone", compute='check_if_from_pos', required=False, )

	@api.depends('invoice_origin')
	def check_if_from_pos(self):
		for rec in self:
			rec = rec.sudo()
			# rec.my_pos_config = False
			rec.check_pos = False
			rec.customer_name = rec.partner_id.display_name
			rec.customer_phone = rec.partner_id.phone
			# pos_order = self.sudo().env['pos.order'].search([('name', '=', rec.invoice_origin)], limit=1)
			# if pos_order:
				# rec.my_pos_config = pos_order.session_id.config_id.id
			# 	rec.check_pos = True
			# else:
			sale_order = self.sudo().env['sale.order'].search([('name', '=', rec.invoice_origin)], limit=1)
			if sale_order:
				rec.customer_name = sale_order.customer_name if sale_order.customer_name else sale_order.partner_id.display_name
				rec.customer_phone = sale_order.customer_phone if sale_order.customer_phone else sale_order.partner_id.phone

	@api.depends('invoice_line_ids')
	def get_warehouse_name(self):
		for rec in self:
			rec.warehouse_name = ''
			invoice_line_sales = rec.invoice_line_ids.filtered(lambda x:x.sale_line_ids)
			if invoice_line_sales:
				rec.warehouse_name = invoice_line_sales[0].sale_line_ids[0].order_id.warehouse_id.display_name

	@api.depends()
	def get_total_discount(self):
		for rec in self:
			rec.total_discount = sum(rec.invoice_line_ids.mapped('discount_amount'))

	qr_code_image = fields.Binary(string='qr code image',store=True)

	def get_InvDateTime(self):
		for rec in self:
			date = False
			if rec.invoice_date:
				timezone = self._context.get('tz') or self.env.user.tz or 'UTC'
				self_tz = self.with_context(tz=timezone)
				mydatetime = datetime.combine(rec.invoice_date, datetime.now().time())
				date = fields.Datetime.context_timestamp(self_tz, mydatetime)
				date = date.strftime("%Y-%m-%d %H:%M:%S")
				date = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
			return date

	def get_qr_encoding(self,tag, field):
		value = field.encode('UTF-8')
		tag = tag.to_bytes(length=1, byteorder='big')
		length = len(value).to_bytes(length=1, byteorder='big')
		return tag + length + value

	def action_add_qrcode_zakat(self):
		for rec in self.env['account.move'].sudo().search([('type','!=', 'entry')]).filtered(lambda x : ((x.invoice_date)  and (x.invoice_date.month == date.today().month)) or ((x.create_date)  and (x.create_date.month == date.today().month))):
			rec.generate_qr_code()


	@api.constrains('company_id','invoice_date','amount_total','total_taxes')
	def generate_qr_code(self):
		""" Generate the qr code for Saudi e-invoicing. Specs are available at the following link at page 23
			https://zatca.gov.sa/ar/E-Invoicing/SystemsDevelopers/Documents/20210528_ZATCA_Electronic_Invoice_Security_Features_Implementation_Standards_vShared.pdf
		"""
		for rec in self:
			qr_code_str = ''
			get_InvDateTime = rec.get_InvDateTime()
			qr_img = False
			seller_name_enc = rec.get_qr_encoding(1, rec.company_id.display_name or "/")
			company_vat_enc = rec.get_qr_encoding(2, rec.company_id.vat or "/")
			# time_sa = fields.Datetime.context_timestamp(rec.with_context(tz='Asia/Riyadh'),
			#                                             rec.get_invDate_currentTime())
			timestamp_enc = rec.get_qr_encoding(3, get_InvDateTime.isoformat() if get_InvDateTime else "/")
			invoice_total_enc = rec.get_qr_encoding(4, str(rec.amount_total) or "/")
			total_vat_enc = rec.get_qr_encoding(5, str(rec.total_taxes) or "/")
			str_to_encode = seller_name_enc + company_vat_enc + timestamp_enc + invoice_total_enc + total_vat_enc
			qr_code_str = base64.b64encode(str_to_encode).decode('UTF-8')
			qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=40,border=4, )
			qr.add_data(qr_code_str.encode('utf-8'))
			qr.make(fit=True)
			img = qr.make_image()
			temp = BytesIO()
			img.save(temp, format="PNG")
			qr_img = base64.b64encode(temp.getvalue())
			rec.qr_code_image = qr_img
			return rec.qr_code_image
			# barcode = self.env['ir.actions.report'].sudo().barcode(barcode_type='QR', value=qr_code_str.encode('utf-8'), width=200,
			#                                                        height=200, humanreadable=0,
			#                                                        quiet=1)
			# return barcode
	@api.depends('invoice_line_ids')
	def get_total_taxes(self):
		for rec in self:
			total_with_out_tax = sum(rec.invoice_line_ids.mapped('price_subtotal'))
			total_with_tax = sum(rec.invoice_line_ids.mapped('price_total'))
			rec.total_taxes = total_with_tax - total_with_out_tax


class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	tax_amount = fields.Float(string="Tax Amount", required=False, compute='get_tax_amount')
	discount_amount = fields.Float('discount amount',compute='get_discount_amount')
	price_include = fields.Boolean(string='Included in Price', default=False,
								   help="Check this if the price you use on the product and invoices includes this tax",
								   compute='check_price_include', store=True)

	@api.depends('tax_ids')
	def check_price_include(self):
		for rec in self:
			rec.price_include = False
			if rec.tax_ids:
				if rec.tax_ids[0].price_include:
					rec.price_include = True


	@api.depends('product_id','discount','price_unit','quantity')
	def get_discount_amount(self):
		for rec in self:
			if rec.price_include:
				rec.discount_amount = rec.price_subtotal * rec.discount / 100
			else:
				rec.discount_amount = (rec.price_unit * rec.quantity) * rec.discount / 100


	@api.depends('price_subtotal', 'price_total')
	def get_tax_amount(self):
		for rec in self:
			rec.tax_amount = 0.0
			if rec.move_id.move_type == 'out_invoice':
				rec.tax_amount = round(rec.price_total - rec.price_subtotal, 2)
			if rec.move_id.move_type == 'out_refund':
				rec.tax_amount = round((rec.price_total - rec.price_subtotal), 2)




