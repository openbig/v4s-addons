# -*- encoding: utf-8 -*-
##############################################################################
#
#    stock_lot_reservation
#    (C) 2015 OpenGlobe
#    Author: Mikołaj Dziurzyński, Grzegorz Grzelak (OpenGlobe)
#
#    All Rights reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class stock_picking(models.Model):
    _inherit = "stock.picking"

    @api.cr_uid_ids_context
    def do_enter_transfer_details(self, cr, uid, picking, context=None):
        if not context:
            context = {}

        context.update({
            'active_model': self._name,
            'active_ids': picking,
            'active_id': len(picking) and picking[0] or False
        })

        created_id = self.pool['stock.transfer_details'].create(
            cr, uid, {'picking_id': len(picking) and picking[0] or False}, context)

        # compute the lot ids
        for pick in self.pool['stock.picking'].browse(cr, uid, picking):
            self.pool['stock.production.lot'].set_transfer_id(
                cr, uid, pick.move_lines, created_id, context)

        return self.pool['stock.transfer_details'].wizard_view(cr, uid, created_id, context)


class stock_production_lot(models.Model):
    _inherit = "stock.production.lot"

    is_transferable = fields.Boolean(compute='_check', string="Is Transferable", store=True,
                                     help="Check if there may be any quantity of the product on any internal \
                                     location within this lot id. For search optimalization.")

    transfer_id = fields.Many2one('stock.transfer_details', 'Transfer')

    def search(self, cr, uid, args, offset=0, limit=None, order=None,context=None, count=False):
        new_args = args
        ctx = context.copy()
        if context.get('drop_ids', False):
            new_args = []
            for arg in args:
                if 'id' not in arg:
                    for item in arg:
                        if isinstance(item, int):
                            break
                    else:
                        new_args.append(arg)
            new_args.append(['product_id','=',context.get('product_id')])
                        
            ctx['drop_ids'] = False
        if context.get('available'):
            new_args.append(['transfer_id','=',context.get('transfer_id')])
        return super(stock_production_lot, self).search(cr, uid, new_args, offset, limit,
                order, context=ctx, count=count)

    @api.model
    def set_transfer_id(self, items, transfer_id):
        for line in items:

            lot_ids = self.search(
                [['product_id', '=', line.product_id.id], ['is_transferable', '=', True]])
            for lot in lot_ids:
                available_quantity = 0
                for quant in lot.quant_ids:
                    if quant.location_id == line.location_id and quant.qty > 0:
                        available_quantity += quant.qty
                if available_quantity >= line.product_uom_qty:
                    lot.transfer_id = transfer_id
        return

    @api.depends('quant_ids')
    def _check(self):
        for quant in self.quant_ids:
            if quant.location_id.usage != 'internal':
                continue
            if quant.qty > 0:
                self.is_transferable = True
                return
        self.is_transferable = False
