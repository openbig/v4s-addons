# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Module stock_v4s
#    Copyrigt (C) 2010 OpenGLOBE Andrzej Grymkowski (www.openglobe.pl)
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

from osv import osv, fields
import netsvc
from tools.translate import _

class procurement_order(osv.osv):
    _inherit = 'procurement.order'

    def action_move_create(self, cr, uid, ids, context=None):
        super(procurement_order, self).action_move_create(cr, uid, ids)
        picking_pool = self.pool.get('stock.picking')
        sale_pool = self.pool.get('sale.order')
        
        sale_names = self.find_sale_orders(cr, uid, ids)
        picking_ids = self.find_delivery_orders(cr, uid, ids)
        
        for procurement in self.browse(cr, uid, ids):
            if not sale_names.has_key(procurement.id) or not picking_ids.has_key(procurement.id):
                continue
            sale_name = sale_names[procurement.id]
            pickings = picking_ids[procurement.id]
            self.write_sale_to_pickings(cr, uid, pickings, sale_name)
            
            
    def write_sale_to_pickings(self, cr, uid, picking_ids, sale_name, context=None):
        picking_pool = self.pool.get('stock.picking')
        sale_pool = self.pool.get('sale.order')
        
        sale_ids = sale_pool.search(cr, uid, [('name','=',sale_name)], limit=1)
        if sale_ids:
            sale_id = sale_ids[0]
        
        for picking in picking_pool.browse(cr, uid, picking_ids):
            if picking.sale_id:
                print 'znalazlem sale'
                print 'original', picking.sale_id.id, 'znaleziony', sale_id
                continue
            print 'write'
            picking.write({'sale_id': sale_id})
    
    def find_sale_orders(self, cr, uid, procurement_ids, context=None):
        result = {}
        sale_pool = self.pool.get('sale.order')
        for procurement in self.browse(cr, uid, procurement_ids):
            origin_list = procurement.origin.split(":")
            for source in origin_list:
                if 'SO' not in source:
                    continue
                result[procurement.id] = source
        print result        
        return result
            
    def find_delivery_orders(self, cr, uid, procurement_ids, context=None):
        result = {}
        picking_pool = self.pool.get('stock.picking')
        sale_names = self.find_sale_orders(cr, uid, procurement_ids)
        for procurement in self.browse(cr, uid, procurement_ids):
            if not sale_names.has_key(procurement.id): 
                continue
            sale_name = sale_names[procurement.id]
            picking_ids = picking_pool.search(cr, uid, [('origin','like', sale_name)])
            print 'sale', sale_name, picking_ids
            result[procurement.id] = picking_ids
        return result
    
procurement_order()    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
