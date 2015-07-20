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
import logging

from openerp.osv import osv, fields
from datetime import datetime

class stock_journal(osv.osv):
    _name = "stock.journal"
    _description = "Stock Journal"
    _columns = {
        'name': fields.char('Stock Journal', size=32, required=True),
        'user_id': fields.many2one('res.users', 'Responsible'),
    }
    _defaults = {
        'user_id': lambda s, c, u, ctx: u
    }

stock_journal()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'create_uid': fields.many2one('res.users', 'Warehouse Worker', readonly=1),
        'write_uid': fields.many2one('res.users', 'Warehouse Worker', readonly=1),

        'stock_journal_id': fields.many2one('stock.journal','Stock Journal', select=True),

        'notice': fields.text('Notice'),
    }

stock_picking()

class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    def name_get(self, cr, uid, ids, context=None):
        ret = []
        for lot in self.browse(cr, uid, ids):
            stuff = ()
            if lot.life_date:
                date = datetime.strptime(lot.life_date, '%Y-%m-%d %H:%M:%S')
                str_date = date.strftime('%Y-%m-%d')
                stuff = (lot.id,'%s [%s]' % (lot.name,str_date))
            else:
                stuff = (lot.id,lot.name)
            ret.append(stuff)
        return ret



stock_production_lot()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
