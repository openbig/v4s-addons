# -*- coding: utf-8 -*-

from osv import fields, osv

class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"

    _columns = {
        'merge_notes': fields.text("Merge Notes")
    }
        
stock_picking()


