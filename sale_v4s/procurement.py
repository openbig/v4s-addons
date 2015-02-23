# # -*- coding: utf-8 -*-
# ##############################################################################
# #
# #    OpenERP, Open Source Management Solution
# #    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
# #
# #    Module sale_v4s
# #    Copyrigt (C) 2010 OpenGLOBE Grzegorz Grzelak (www.openglobe.pl)
# #                       and big-consulting GmbH (www.openbig.de)
# #
# #    This program is free software: you can redistribute it and/or modify
# #    it under the terms of the GNU Affero General Public License as
# #    published by the Free Software Foundation, either version 3 of the
# #    License, or (at your option) any later version.
# #
# #    This program is distributed in the hope that it will be useful,
# #    but WITHOUT ANY WARRANTY; without even the implied warranty of
# #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# #    GNU Affero General Public License for more details.
# #
# #    You should have received a copy of the GNU Affero General Public License
# #    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# #
# ##############################################################################
#
# from openerp.tools.translate import _
# from openerp.osv import fields, osv
#
# class procurement_order(osv.osv):
#     _inherit = "procurement.order"
#
#
#     """
#     Used override to comment a log
#     """
#     def _check_make_to_stock_product(self, cr, uid, procurement, context=None):
#         """ Checks procurement move state.
#         @param procurement: Current procurement.
#         @return: True or move id.
#         """
#         ok = True
#         if procurement.move_id:
#             message = False
#             id = procurement.move_id.id
#             if not (procurement.move_id.state in ('done','assigned','cancel')):
#                 ok = ok and self.pool.get('stock.move').action_assign(cr, uid, [id])
#                 order_point_id = self.pool.get('stock.warehouse.orderpoint').search(cr, uid, [('product_id', '=', procurement.product_id.id)], context=context)
#                 if not order_point_id and not ok:
#                      message = _("Not enough stock and no minimum orderpoint rule defined.")
#                 elif not order_point_id:
#                     message = _("No minimum orderpoint rule defined.")
#                 elif not ok:
#                     message = _("Not enough stock.")
#
#                 if message:
#                     #self.log(cr, uid, procurement.id, _("Procurement '%s' is in exception: ") % (procurement.name) + message)
#                     cr.execute('update procurement_order set message=%s where id=%s', (message, procurement.id))
#         return ok
#
# procurement_order()