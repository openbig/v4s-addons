# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv

class insert_package(osv.osv_memory):
    _name = 'insert.package'
    _description = 'Insert Package'

    _columns = {
        'location_id': fields.many2one('stock.location', 'Source', required=True),
        'location_dest_id': fields.many2one('stock.location', 'Destination', required=True),
        'package_id': fields.many2one('stock.quant.package', 'Pack', required=True),
    }

    def insert_package(self, cr, uid, ids, context=None):
        stock_move_obj = self.pool.get('stock.move')
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False

#        res = super(insert_tracking, self).default_get(cr, uid, fields, context=context)
        picking = self.pool.get('stock.picking').browse(cr, uid, record_id, context=context)

        for form in self.browse(cr, uid, ids, context=context):
#            wh = wh_obj.browse(cr, uid, proc.warehouse_id.id, context=context)
            for quant in form.package_id.quant_ids:
                move_id = stock_move_obj.create(cr, uid, {
                    'name': quant.product_id.name,
#                    'date_planned': form.date_planned,
                    'quant_ids': [quant.id],
                    'product_id': quant.product_id.id,
                    # 'product_qty': quant.qty,
                    'product_uom': quant.product_id.uom_id.id,
                    'location_id': form.location_id.id,
                    'location_dest_id': form.location_dest_id.id,
                    'picking_id': picking.id,
                    'company_id': picking.company_id.id,
                })

        return


insert_package()