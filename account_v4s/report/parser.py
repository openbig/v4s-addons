# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Module account_v4s
#    Copyrigt (C) 2010 OpenGLOBE Grzegorz Grzelak (www.openglobe.pl)
#                       and big-consulting GmbH (www.openbig.de)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime
from report import report_sxw
import logging

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_picking': self.get_picking,
            'get_delivery_address': self.get_delivery_address,
            'get_payment_term_description': self.get_payment_term_description,
        })


    def get_picking(self, invoice):
        if invoice.type == 'out_invoice':
            if self.pool.get("sale.order"):
                 self.cr.execute("SELECT p.id, max(p.date), p.name FROM stock_picking as p \
                             LEFT JOIN sale_order as s \
                                 ON (p.sale_id = s.id) \
                                 LEFT JOIN sale_order_invoice_rel as i \
                                     ON (s.id = i.order_id) \
                             WHERE (i.invoice_id = %s) AND (p.state = 'done') \
                             GROUP BY p.id",(invoice.id,))
                 res = self.cr.fetchone()
                 if res:
                     return res[2]
        elif invoice.type == 'in_invoice':
            if self.pool.get("purchase.order"):
                self.cr.execute("SELECT p.id, max(p.date), p.name FROM stock_picking as p \
                            LEFT JOIN purchase_order as po \
                                ON (p.purchase_id = po.id) \
                                LEFT JOIN purchase_invoice_rel as i \
                                    ON (po.id = i.purchase_id) \
                            WHERE (i.invoice_id = %s) AND (p.state = 'done') \
                            GROUP BY p.id",(invoice.id,))
                res = self.cr.fetchone()
                if res:
                    return res[2] 
        return ""

    def get_delivery_address(self, invoice):
        res_address = ""
        if invoice.type == 'out_invoice':
            if self.pool.get("sale.order"):
                self.cr.execute("SELECT order_id \
                                FROM sale_order_invoice_rel \
                                WHERE invoice_id = %s",(invoice.id,))
                res = self.cr.fetchone()
                if res and res[0]:
                    so = self.pool.get('sale.order').browse(self.cr, self.uid, res[0])
                    address = so.partner_shipping_id
                    res_address = ''
                    res_address+=  (address.partner_id and address.partner_id.company_ext and address.partner_id.company_ext+'\n') or '' 
                    res_address+=  (address.partner_id and address.partner_id.department_company_ext and address.partner_id.department_company_ext+'\n') or '' 
                    res_address+=  ((address.title and address.title.name and address.title.name+' ') or '') + ((address.prename and address.prename+' ') or '') + ((address.name) or '') 
                    if address.title.name or address.prename or address.name: res_address+='\n'
                    res_address+=  (address.street and address.street+'\n') or '' 
                    res_address+=  (address.street2 and address.street2+'\n') or '' 
                    res_address+=  ((address.zip and address.zip+' ') or '')  + ((address.city and address.city+'\n') or '')

        return res_address

    
    def get_payment_term_description(self, invoice):

        terms = self.pool.get('account.payment.term').compute(self.cr, self.uid, invoice.payment_term.id, invoice.residual)
        payment_term = invoice.payment_term
        
        if not terms:
            return False
        
        description = ''
        today = datetime.today()
        if len(terms) == 1: # we have only balance term line
            term_line = terms[0]
            term_due_date, amount_term = term_line
            description = invoice.payment_term.note
                        
        if len(terms) > 1:  # with more lines
            description = 'Payment '
            i = 0
            for term_line in payment_term.line_ids:
                term_due_date, term_amount = terms[i]
                if term_line.value == 'fixed':
                    description += 'until {0} with amount {1}'.format(self.formatLang(term_due_date, date=True), self.formatLang(term_amount, digits=2))
                if term_line.value == 'procent':
                    description += 'until {0} with {1}% = {2} less'.format(self.formatLang(term_due_date, date=True), str(term_line.value_amount*100) ,self.formatLang(term_amount,digits=2))                    
                break
            term_due_date, term_amount = terms[-1]    
            description += ' or with total amount until {0}.'.format(self.formatLang(term_due_date, date=True))
        print description
        return description
    
    def get_balance_amount(self, invoice):
        pass
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
