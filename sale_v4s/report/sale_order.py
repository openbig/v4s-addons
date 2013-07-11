# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Module sale_v4s
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

from openerp.report import report_sxw


class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'check_taxes': self.check_taxes,
            'get_taxes': self.get_taxes,
        })
        
    # function checks taxes in sale order line. If find any, return true    
    def check_taxes(self, order):
        sale_brw = self.pool.get('sale.order').browse(self.cr, self.uid, order)
        for line in sale_brw.order_line:
            if line.tax_id: return True
        return False
    
    # function compute taxes in order line
    # return { 'tax_id' : [ uncomputed_value, taxed_value ] }
    def get_taxes(self, order):
        sale_brw = self.pool.get('sale.order').browse(self.cr, self.uid, order)
        tax_ids = {}
        for line in sale_brw.order_line:
            if line.tax_id:
                taxes = self.pool.get('account.tax').compute_all(self.cr, self.uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)['taxes']
                #print taxes
                for tax in taxes:
                    tax_id = tax['id']
                    if not tax_ids.has_key(tax['id']):
                        tax_ids[tax['id']] = [0,0, tax['name']]
                        
                    tax_ids[tax['id']][0] += line.price_subtotal
                    tax_ids[tax['id']][1] += tax['amount']
                
                    #val += c.get('amount', 0.0)
        
                  #tax_ids[tax_id][1] += sale_brw._amount_line_tax(line)
        #print tax_ids          
        return tax_ids

report_sxw.report_sxw('report.sale_v4s.sale_order_v4s', 'sale.order', 'addons/sale_v4s/report/sale_order.rml', parser=order, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

