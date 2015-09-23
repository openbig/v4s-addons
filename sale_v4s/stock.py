# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Module stock_v4s
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

from openerp.osv import osv, fields

# class stock_warehouse(osv.osv):
#     _inherit = "stock.warehouse"
#
#     def _get_set_mto(self, cr, uid, ids, name, arg, context=None):
#         # sale_shop_obj = self.pool.get('sale.shop')
#         # self.browse(cr, uid, ids, context=context)
#         ret = {}
#         for id in ids:
#             cr.execute('SELECT set_mto FROM sale_shop WHERE warehouse_id='+str(id))
#             res1 = cr.fetchall()
#             if len(res1) > 0:
#                 if len(res1[0]) > 0:
#                     res1 = res1[0][0]
#                     if res1 == True:
#                         ret[id] = True
#                     else:
#                         ret[id] = False
#             else:
#                 ret[id] = False
#         return ret
#
#     _columns = {
#         'set_mto':  fields.function(_get_set_mto, store=True, type='boolean', string='MTO'),
#
#     }
#
# stock_warehouse()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    # def _get_default_client_order_ref(self, cr, uid, ids, context=None):
    #     logger = logging.getLogger()
    #     logger.warn("xoxo xD")
    #     rasdsa

    _columns = {
        'create_uid': fields.many2one('res.users', 'Warehouse Worker', readonly=1),
        'write_uid': fields.many2one('res.users', 'Warehouse Worker', readonly=1),
        'client_order_ref': fields.char('Customer Reference', size=128),
        # 'client_order_ref': fields.related('sale_id', 'client_order_ref', type='char', string='Customer Reference'),
    }

    # _defaults = {
    #     'client_order_ref': _get_default_client_order_ref,
    #     }


    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        invoice_vals = super(stock_picking, self)._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)

        if picking.sale_id and inv_type in ('out_invoice', 'out_refund') and not invoice_vals.has_key('client_order_ref'):
            invoice_vals['client_order_ref'] = picking.client_order_ref or ''

        return invoice_vals

stock_picking()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
