# -*- coding: utf-8 -*-

import base64
from datetime import datetime,date
from num2words import num2words
from odoo import models, fields

class Account_move(models.Model):
    _inherit = 'account.move'

    qr_code_image = fields.Char("QR Code", copy=False, readonly=1, compute='generate_qr_code')
    
    def amount_to_words(self,amount):
        return num2words(amount,lang=self.partner_id.lang)
    
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
    
    def generate_qr_code(self):
        """ Generate the qr code for Saudi e-invoicing. Specs are available at the following link at page 23
            https://zatca.gov.sa/ar/E-Invoicing/SystemsDevelopers/Documents/20210528_ZATCA_Electronic_Invoice_Security_Features_Implementation_Standards_vShared.pdf
        """

        def get_qr_encoding(tag, field):
            value = field.encode('UTF-8')
            tag = tag.to_bytes(length=1, byteorder='big')
            length = len(value).to_bytes(length=1, byteorder='big')
            return tag + length + value

        for rec in self:
            qr_code_str = ''
            date = rec.get_InvDateTime()
            if rec.company_id and date and rec.company_id.vat:
                seller_name_enc = get_qr_encoding(1, rec.company_id.display_name)
                company_vat_enc = get_qr_encoding(2, rec.company_id.vat)
                timestamp_enc = get_qr_encoding(3, date.isoformat())
                invoice_total_enc = get_qr_encoding(4, str(rec.amount_total))
                total_vat_enc = get_qr_encoding(5, str(rec.total_taxes))
                str_to_encode = seller_name_enc + company_vat_enc + timestamp_enc + invoice_total_enc + total_vat_enc
                qr_code_str = base64.b64encode(str_to_encode).decode('UTF-8')
            rec.qr_code_image = qr_code_str
            
            