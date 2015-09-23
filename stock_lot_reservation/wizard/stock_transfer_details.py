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

from openerp import models, api, fields
from openerp.tools.translate import _

import logging

_logger = logging.getLogger(__name__)


class stock_transfer_details(models.Model):
    _inherit = 'stock.transfer_details'

    name = fields.Char("Picking Wizard")

    @api.model
    def create(self, vals):
        res = super(stock_transfer_details, self).create(vals)
        res.name = str(res.id)
        return res

    def default_get(self, cr, uid, fields, context):
        res = super(stock_transfer_details, self).default_get(
            cr, uid, fields, context)
        if 'item_ids' in res:
            for line in res['item_ids']:
                line['lot_id'] = False
        return res

    @api.multi
    def wizard_view(self):
        if self.picking_id.picking_type_id.code == 'incoming':
            view = self.env.ref('stock.view_stock_enter_transfer_details')
        else:
            view = self.env.ref('stock_lot_reservation.view_stock_enter_transfer_details_lot_id_mod')

        return {
            'name': _('Enter transfer details'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.transfer_details',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': self.env.context,
        }

class stock_transfer_details_items(models.Model):
    _inherit = 'stock.transfer_details_items'
