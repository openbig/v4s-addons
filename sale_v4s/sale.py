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
import logging

from openerp.osv import fields, osv

# class sale_shop(osv.osv):
#     _inherit = "sale.shop"
#
#     _columns = {
#         'set_mto' : fields.boolean('MTO', help='If true, changes field "Procurement Method", in sale order lines, to "on order".'),
#     }
#
# sale_shop()

class sale_order(osv.osv):
    _inherit ="sale.order"



    _columns = {
        'note2' : fields.text("Comment on top"),
        'valid_until' : fields.date("Valid Until"),


    }
    # def onchange_shop_id(self, cr, uid, ids, shop_id):
    #     res = super(sale_order, self).onchange_shop_id(cr, uid, ids, shop_id)
    #     if not shop_id: return res
    #
    #     shop_brw = self.pool.get('sale.shop').browse(cr, uid, shop_id)
    #     if shop_brw.set_mto == True:
    #         for sale in self.browse(cr, uid , ids):
    #             for line in sale.order_line:
    #                 if line.product_id:
    #                     if line.product_id.type!='service':
    #                         self.pool.get('sale.order.line').write(cr, uid, line.id, { 'type' : 'make_to_order' })
    #     return res


    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        invoice_vals = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context=context)
        if invoice_vals['type'] in ('out_invoice', 'out_refund') and not invoice_vals.has_key('client_order_ref'):
            invoice_vals['client_order_ref'] = invoice_vals['name']
        return invoice_vals

sale_order()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    # def create(self, cr, uid, vals, context=None):
    #
    #     logger = logging.getLogger()
    #     logger.warn(vals)
    #     logger.warn("xD")
    #     adsad
    #
    #     product_id = vals.get('product_id', None)
    #     order_id = vals.get('order_id')
    #     if not order_id: return super(sale_order_line, self).create(cr, uid, vals, context)
    #
    #     if product_id:
    #         product_brw = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
    #     order_brw = self.pool.get('sale.order').browse(cr, uid, order_id, context=context)
    #     warehouse_id = order_brw.warehouse_id
    #
    #     type = vals.get('type', None)
    #
    #     if product_id and product_brw.type=='service':
    #         type = 'make_to_stock'
    #     elif shop_id.set_mto==True:
    #         type = 'make_to_order'
    #
    #     if type:
    #         vals['type'] = type
    #     return super(sale_order_line, self).create(cr, uid, vals, context)


    # def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
    #         uom=False, qty_uos=0, uos=False, name='', partner_id=False,
    #         lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
    #
    #     res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
    #         uom, qty_uos, uos, name, partner_id,
    #         lang, update_tax, date_order, packaging, fiscal_position, flag, context)
    #
    #     vals = {}
    #     if not product:
    #         return res
    #
    #     product_brw = self.pool.get('product.product').browse(cr, uid, product, context=context)
    #     procure_method = res['value'].get('type', 'None')
    #
    #     # correct procurement method. We cant apply make_to_order when product is service
    #     if product_brw.type=='service' and procure_method=='make_to_order':
    #         vals['type'] = 'make_to_stock'
    #
    #     res['value'].update(vals)
    #     return res

sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
