# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    Module stock_sn_tracking_og is copyrighted by 
#    Grzegorz Grzelak of OpenGLOBE (www.openglobe.pl)
#    with the same rules as OpenObject and OpenERP platform
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

import time
import netsvc
import logging

from osv import fields,osv
from tools.translate import _

class stock_tracking(osv.osv):
    _inherit = "stock.tracking"
#    _description = "Packs"

    _columns = {
        'prodlot_ids': fields.one2many('stock.production.lot', 'tracking_id', 'Serial Numbers'),
#        'partner_id': fields.many2one('res.partner', 'Partner', help='Owner of the pack'),
#        'in_our_hands': fields.boolean('In Our Company', help='Indicates that pack is temporary in your company or is simply yours.'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        logger = logging.getLogger('Pack tracking')
        logger.warn("default: %s", default)
        prodlot_pooler = self.pool.get('stock.production.lot')
        default_lot = {'tracking_id': False}
        pack = self.browse(cr, uid, id, context)
        new_lot_ids = []
        for lot in pack.prodlot_ids:
            copy_id = prodlot_pooler.copy(cr, uid, lot.id, default_lot, context)
            if copy_id:
                new_lot_ids.append(copy_id)
        default = default.copy()
        default.update({'name': pack.name + _(" (copy)"), 'move_ids':[], 'prodlot_ids': [(6, 0, new_lot_ids)]})
        return super(stock_tracking, self).copy(cr, uid, id, default, context=context)

    '''
    def on_change_partner_id(self, cr, uid, ids, partner):
        """ Changes UoM and name if product_id changes.
        @param location_id: Location id
        @param product: Changed product_id
        @param uom: UoM product
        @return:  Dictionary of changed values
        """
        if not partner:
            serial = ''
        else:
            partner_rec = self.pool.get('res.partner').browse(cr, uid, partner)
            serial = partner_rec.name

        packs = self.pool.get('stock.tracking').browse(cr,uid,ids)
        pack = packs[0]
        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        for sn in pack.prodlot_ids:
            self.pool.get('stock.production.lot.revision').create(cr,uid,{
                'name': "Zmiana partnera",
                'description': "Partner zmieniony na " + serial,
#                'date': ,
                'indice': serial,
                'author_id': uid,
                'lot_id': sn.id,
                'company_id': company_id,
            })
        return {'value':{'serial': serial}}
    '''
    '''
    def on_change_our_hands(self, cr, uid, ids, in_our_hands):
        packs = self.pool.get('stock.tracking').browse(cr,uid,ids)
        pack = packs[0]
        for sn in pack.prodlot_ids:
            self.pool.get('stock.production.lot.revision').create(cr,uid,{
                'name': "Przyjęcie od partnera",
                'description': "Partner zmieniony na " + serial,
#                'date': ,
                'indice': serial,
                'author_id': uid,
                'lot_id': sn.id,
                'company_id': company_id,
            })
        return {'value':{'serial': serial}}
    '''

stock_tracking()

class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'
#    _description = 'Production lot'


    _columns = {
        'tracking_id': fields.many2one('stock.tracking', 'Pack', select=True, 
            help="Pack which this Production Lot belongs to. Can be used for collection of products consisting one kit with its own serial number."),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        logger = logging.getLogger('Pack tracking')
        logger.warn("default: %s", default)

        lot = self.browse(cr, uid, id, context)
        default = default.copy()
        default.update({'name': lot.name + _(" (copy)"), 'move_ids':[]})
        return super(stock_production_lot, self).copy(cr, uid, id, default, context=context)

stock_production_lot()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
