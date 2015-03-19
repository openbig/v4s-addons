# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"

    _columns = {
        'merge_notes': fields.text("Merge Notes")
    }
        
stock_picking()


