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

from osv import osv, fields

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'create_uid': fields.many2one('res.users', 'Warehouse Worker', readonly=1),
        'write_uid': fields.many2one('res.users', 'Warehouse Worker', readonly=1),
        'client_order_ref': fields.related('sale_id', 'client_order_ref', type='char', string='Customer Reference'),
    }
    
        
    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
      invoice_vals = super(stock_picking, self)._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)
      
      if picking.sale_id and inv_type in ('out_invoice', 'out_refund') and not invoice_vals.has_key('client_order_ref'):
            invoice_vals['client_order_ref'] = picking.client_order_ref or ''
      print 'Stock', invoice_vals
      return invoice_vals

      
      
stock_picking()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
