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

from osv import fields, osv

class sale_shop(osv.osv):
    _inherit = "sale.shop"
    
    _columns = {
        'set_mto' : fields.boolean('MTO', help='If true, changes field "Procurement Method", in sale order lines, to "on order".'),
    }
    
sale_shop()

class sale_order(osv.osv):
    _inherit ="sale.order"
    
    
    def onchange_shop_id(self, cr, uid, ids, shop_id):
        res = super(sale_order, self).onchange_shop_id(cr, uid, ids, shop_id)        
        if not shop_id: return res

        shop_brw = self.pool.get('sale.shop').browse(cr, uid, shop_id)
        if shop_brw.set_mto == True:
            for sale in self.browse(cr, uid , ids):
                for line in sale.order_line:
                    self.pool.get('sale.order.line').write(cr, uid, line.id, { 'type' : 'make_to_order' })
        
        return res
    
sale_order()    

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    
    def create(self, cr, uid, vals, context=None):
        order_id = vals.get('order_id')
        if not order_id: return super(sale_order_line, self).create(cr, uid, vals, context)

        order_brw = self.pool.get('sale.order').browse(cr, uid, order_id, context=context)
        mto = order_brw.shop_id.set_mto

        if mto==True: 
            vals.update(
            {
                'type' : 'make_to_order'
            })
                        
        return super(sale_order_line, self).create(cr, uid, vals, context)

sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: