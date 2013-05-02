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
from report import report_sxw
import logging

class account_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_picking': self.get_picking,
            'get_delivery_address': self.get_delivery_address,
        })

    def get_picking(self, invoice, *args):
        if invoice.type == 'out_invoice':
            if self.pool.get("sale.order"):
#                 netsvc.Logger().notifyChannel("Pickings",netsvc.LOG_DEBUG,str(is_so))
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
#                netsvc.Logger().notifyChannel("Pickings",netsvc.LOG_DEBUG,str(is_so))
                self.cr.execute("SELECT p.id, max(p.date), p.name FROM stock_picking as p \
                            LEFT JOIN purchase_order as po \
                                ON (p.purchase_id = po.id) \
                                LEFT JOIN purchase_invoice_rel as i \
                                    ON (po.id = i.purchase_id) \
                            WHERE (i.invoice_id = %s) AND (p.state = 'done') \
                            GROUP BY p.id",(invoice.id,))
                res = self.cr.fetchone()
                if res:
                    return res[2]  #self.pick_done_last(cr, uid, picking_ids)  # search for last done pick list
        return ""

    def get_delivery_address(self, invoice, *args):
#        logger = logging.getLogger('GET_ADDRESS')

        res_address = ""
#        logger.warn("res_address: %s", res_address)
        if invoice.type == 'out_invoice':
#            logger.warn("invoice_type: %s", invoice.type)
            if self.pool.get("sale.order"):
#                logger.warn(" is object: %s", self.pool.get("sale.order"))
                self.cr.execute("SELECT order_id \
                                FROM sale_order_invoice_rel \
                                WHERE invoice_id = %s",(invoice.id,))
                res = self.cr.fetchone()
                if res[0]:
#                    logger.warn("res: %s", res[0])
                    so = self.pool.get('sale.order').browse(self.cr, self.uid, res[0])
                    address = so.partner_shipping_id
                    res_address = address.partner_id.name + '\n' + address.name + '\n' + address.street + '\n' + \
                            address.zip + ' ' + address.city + '\n' + (address.country_id and address.country_id.name or '')
#                    logger.warn("addres: %s", res_address)
        return res_address


#        elif invoice.type == 'in_invoice':
#            if self.pool.get("purchase.order"):
##                netsvc.Logger().notifyChannel("Pickings",netsvc.LOG_DEBUG,str(is_so))
#                cr.execute("SELECT p.id, max(p.date), p.name FROM stock_picking as p \
#                            LEFT JOIN purchase_order as po \
#                                ON (p.purchase_id = po.id) \
#                                LEFT JOIN purchase_invoice_rel as i \
#                                    ON (po.id = i.purchase_id) \
#                            WHERE (i.invoice_id = %s) AND (p.state = 'done') \
#                            GROUP BY p.id",(invoice.id,))
#                res = cr.fetchone()
#                if res:
#                    return res[2]  #self.pick_done_last(cr, uid, picking_ids)  # search for last done pick list
#        return ""

report_sxw.report_sxw(
    'report.account_v4s.invoice_v4s',
    'account.invoice',
    'addons/account_v4s/report/account_print_invoice.rml',
    parser=account_invoice
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
