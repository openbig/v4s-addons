# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Module crm_v4s
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
from datetime import datetime
from openerp.addons.crm import crm
import time
from openerp.addons.crm import wizard

from openerp.tools.translate import _
import binascii
import openerp.tools


class crm_claim(osv.osv):
    """
    Crm claim
    """
    _inherit = "crm.claim"
    
    _columns = {
        'ref2' : fields.reference('Reference2', selection=openerp.addons.base.res.res_request.referencable_models, size=128),
    }
    
    def create_purchase(self, cr, uid, ids, partner_id, context=None):
        context = context and context or {}
        context.update({'partner_id':partner_id})
        
        purchase_pool = self.pool.get('purchase.order')
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
        
        values = purchase_pool.onchange_partner_id(cr, uid, ids, partner_id)['value']
        values.update( {
            'location_id': partner.property_stock_customer.id,
            'partner_id': partner_id,
            })
        
        purchase_id = purchase_pool.create(cr, uid, values, context=context)
        return purchase_id
    
    def create_purchase_line(self, cr, uid, ids, product_id, purchase_id, context=None):
        context = context and context or {}
        
        purchase_line_pool = self.pool.get('purchase.order.line')
        purchase_brw = self.pool.get('purchase.order').browse(cr, uid, purchase_id)
        
        line_uom = purchase_line_pool._get_uom_id(cr, uid, context=context)
        date_order = purchase_brw.date_order
        partner_id = purchase_brw.partner_id.id
        pricelist_id = purchase_brw.pricelist_id.id
        line_vals = purchase_line_pool.onchange_product_id(cr, uid, ids, pricelist_id, product_id, 1, line_uom, partner_id, date_order=date_order)['value']
        line_vals.update({
            'order_id': purchase_id,
            'product_id': product_id,
            })
        purchase_line_id = purchase_line_pool.create(cr, uid, line_vals, context=context)
        return purchase_line_id

    def convert_to_purchase(self, cr, uid, ids, context):
        context = context and context or {}

        brw = self.browse(cr, uid, ids[0], context)
        partner = self.pool.get('res.partner')

        if not brw.ref:
            raise osv.except_osv(_('Warning'), _('Ref dont link to production lot.'))
            return True

        if brw.ref._name != 'stock.production.lot':
            raise osv.except_osv(_('Warning'), _('Ref dont link to production lot.'))
            return True

        if not brw.partner_id:
            raise osv.except_osv(_('Warning'), _('No partner set.'))
            return True

        if brw.ref._name != 'stock.production.lot' or not brw.partner_id: return True

        # creating new purchase order
        partner_id = brw.partner_id.id
        purchase_id = self.create_purchase(cr, uid, ids, partner_id)

        # getting product id to create purchase_line
        product_id = brw.ref.product_id.id
        logger = logging.getLogger()
        logger.warn(product_id)

        # creating new purchase line
        purchase_line_id = self.create_purchase_line(cr, uid, ids, product_id, purchase_id)

        # update field ref2
        self.write(cr, uid, ids, {
            'ref2' : 'purchase.order,%d' % purchase_id,
            }, context=context)

        return {
            'name':_("Requests for Quotation"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'purchase.order',
            'res_id': purchase_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'domain': '[]',
            'context': context,
        }