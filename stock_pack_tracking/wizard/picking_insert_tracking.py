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

import netsvc
import time

from osv import fields, osv

class insert_tracking(osv.osv_memory):
    _name = 'insert.tracking'
    _description = 'Insert Pack'
    
    '''
    def onchange_product_id(self, cr, uid, ids, prod_id):
        """ On Change of Product ID getting the value of related UoM.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: List of IDs selected 
         @param prod_id: Changed ID of Product 
         @return: A dictionary which gives the UoM of the changed Product 
        """
        product = self.pool.get('product.product').browse(cr, uid, prod_id)
        return {'value': {'uom_id': product.uom_id.id}}
    '''

    _columns = {
        'location_id': fields.many2one('stock.location', 'Source', required=True),
        'location_dest_id': fields.many2one('stock.location', 'Destination', required=True),
        'tracking_id': fields.many2one('stock.tracking', 'Pack', required=True),
#        'date_planned': fields.date('Planned Date', required=True),
    }

#    _defaults = {
#        'date_planned': lambda *args: time.strftime('%Y-%m-%d'),
#        'qty': lambda *args: 1.0,
#    }

    def insert_tracking(self, cr, uid, ids, context=None):
        """ Creates procurement order for selected product.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return: A dictionary which loads Pack form view.
        """
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context).login
        wh_obj = self.pool.get('stock.warehouse')
        procurement_obj = self.pool.get('procurement.order')
        wf_service = netsvc.LocalService("workflow")
        data_obj = self.pool.get('ir.model.data')

        stock_move_obj = self.pool.get('stock.move')
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False

#        res = super(insert_tracking, self).default_get(cr, uid, fields, context=context)
        picking = self.pool.get('stock.picking').browse(cr, uid, record_id, context=context)

        for form in self.browse(cr, uid, ids, context=context):
#            wh = wh_obj.browse(cr, uid, proc.warehouse_id.id, context=context)
            for lot in form.tracking_id.prodlot_ids:
                move_id = stock_move_obj.create(cr, uid, {
                    'name': lot.product_id.name,
#                    'date_planned': form.date_planned,
                    'product_id': lot.product_id.id,
                    'product_qty': 1.00,
                    'product_uom': lot.product_id.uom_id.id,
                    'location_id': form.location_id.id,
                    'location_dest_id': form.location_dest_id.id,
                    'prodlot_id': lot.id,
                    'tracking_id': lot.tracking_id.id,
                    'picking_id': picking.id,
                    'company_id': picking.company_id.id,

#                    'procure_method':'make_to_order',
                })

#            wf_service.trg_validate(uid, 'procurement.order', procure_id, 'button_confirm', cr)


#        id2 = data_obj._get_id(cr, uid, 'procurement', 'procurement_tree_view')
#        id3 = data_obj._get_id(cr, uid, 'procurement', 'procurement_form_view')

#        if id2:
#            id2 = data_obj.browse(cr, uid, id2, context=context).res_id
#        if id3:
#            id3 = data_obj.browse(cr, uid, id3, context=context).res_id

        return {
#            'view_type': 'form',
#            'view_mode': 'tree,form',
#            'res_model': 'procurement.order',
#            'res_id' : procure_id,
#            'views': [(id3,'form'),(id2,'tree')],
#            'type': 'ir.actions.act_window',
         }

    '''
    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False

        res = super(make_procurement, self).default_get(cr, uid, fields, context=context)
        product_id = self.pool.get('product.product').browse(cr, uid, record_id, context=context).id
        if 'product_id' in fields:
            res.update({'product_id':product_id})
        return res
    '''

insert_tracking()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

