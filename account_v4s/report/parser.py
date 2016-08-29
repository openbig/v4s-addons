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
from dateutil.relativedelta import relativedelta
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
        
        self.payment_description = {
            'de_DE': {
                #'payment': 'Zahlbar  ',
                #'or': ', ',
                'fixed': u'Zum {0} sind {1}. ',
                'procent': u'Zum {0} sind {2} € bei {1}% Abzug zahlbar. ',
                #'Zum 04.04.2014 sind 498,57 € bei 2,0% Abzug zahlbar. Ohne Abzug sind 508,74 € zum 20.04.2014 fällig.'
                'balance': u'Ohne Abzug sind {1} € zum {0} fällig. ',
                #'Ohne Abzug sind {1} € zum {0} fällig.'
                },
            'en_US': {
                #'payment': 'Payable ',
                #'or': ', ',
                'fixed': 'Until {0} you have to pay {1}. ',
                'procent': 'Until {0} you have to pay {2} with {1}% discount. ',
                'balance': 'Without any discount {1} are due lately on {0}. ',
                },
        }


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
                    res_address+=  ( address.company_ext and address.company_ext+'\n') or '' 
                    res_address+=  ( address.department_company_ext and address.department_company_ext+'\n') or '' 
                    res_address+=  ((address.title and address.title.name and address.title.name+' ') or '') + ((address.prename and address.prename+' ') or '') + ((address.name) or '') 
                    if address.title.name or address.prename or address.name: res_address+='\n'
                    res_address+=  (address.street and address.street+'\n') or '' 
                    res_address+=  (address.street2 and address.street2+'\n') or '' 
                    res_address+=  ((address.zip and address.zip+' ') or '')  + ((address.city and address.city+'\n') or '')

        return res_address


    
    def get_payment_term_description(self, invoice):
        invoice_pool = self.pool.get('account.invoice')
        obj_precision = self.pool.get('decimal.precision')
        precision = obj_precision.precision_get(self.cr, self.uid, 'Account')
        terms = [term for term in invoice.payment_term.line_ids]
        payment_term = invoice.payment_term
        
        if not terms:
            return False
        
        lang = self.localcontext['lang']
        description = ''
        payment_translation = self.payment_description[lang]
        date_due = invoice_pool.onchange_payment_term_date_invoice(self.cr, self.uid, invoice.id, payment_term.id, invoice.date_invoice or None)['value']['date_due']
        date_due = self.formatLang(date_due, date=True)
        
        digits = self.get_digits(dp='Account')
        if len(terms) == 1: # if we have only balance term line
            #description += description_translation['payment']
            total_amount = self.formatLang(invoice.amount_total, digits=digits)
            description += payment_translation['balance'].format(date_due, total_amount)
            
        if len(terms) > 1:  # if we have more lines
            i = 0
            #description = payment_translation['payment']
            for term_line in payment_term.line_ids:
                #if i > 0 and term_line.value != 'balance':
                    #description += payment_translation['or']
                    
                term_due_date = self.compute_payment_term_line_date(term_line, invoice.date_invoice or False)
                term_due_date = self.formatLang(term_due_date, date=True)
                if term_line.value == 'fixed':
                    term_amount = round(term_line.value_amount, precision)
                    description += payment_translation['fixed'].format(term_due_date, self.formatLang(term_amount, digits=digits))
                if term_line.value == 'procent':
                    term_amount = round(invoice.amount_total * term_line.value_amount, precision)
                    description += payment_translation['procent'].format(term_due_date, str(100-term_line.value_amount*100) ,self.formatLang(term_amount,digits=digits))                    
                if term_line.value == 'balance':
                    continue
                #i+=1
            description += payment_translation['balance'].format(date_due, self.formatLang(invoice.amount_total, digits=digits))
          
        return description
        
    def compute_payment_term_line_date(self, payment_line, date_ref=None):
        if not date_ref:
            date_ref = datetime.now().strftime('%Y-%m-%d')
        next_date = (datetime.strptime(date_ref, '%Y-%m-%d') + relativedelta(days=payment_line.days))
        if payment_line.days2 < 0:
            next_first_date = next_date + relativedelta(day=1,months=1) #Getting 1st of next month
            next_date = next_first_date + relativedelta(days=payment_line.days2)
        if payment_line.days2 > 0:
            next_date += relativedelta(day=payment_line.days2, months=1)
        return next_date.strftime('%Y-%m-%d')
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
