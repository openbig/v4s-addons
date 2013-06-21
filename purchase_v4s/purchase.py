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

from osv import fields, osv
from datetime import datetime
import time
from tools.translate import _
import binascii
import tools


class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def do_merge(self, cr, uid, ids, context=None):
        new_orders = super(purchase_order, self).do_merge(cr, uid, ids, context=context)
        
        #update former claims to new purchase_order
        claim_pool = self.pool.get('crm.claim')
        for new in new_orders.keys():
            #finding claims
            claim_ids = []
            for id in new_orders[new]:
                t = claim_pool.search(cr, uid, [('ref2','=','purchase.order,%d' % id)], context=context)
                for p in t: claim_ids.append(p)
            print claim_ids
            claim_pool.write(cr, uid, claim_ids, {
                'ref2': 'purchase.order,%d' % new,
                }, context=context)
        
        return new_orders

purchase_order()    