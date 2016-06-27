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
l = logging.getLogger()

from openerp import models, fields, api, _
from openerp import api
import datetime


class StockPicking(models.Model):  # jak w sale.py
    _inherit = "stock.picking"


    @api.one
    def _compute_purchase_id(self):
        purchase_ids = []
        for move_id in self.move_lines:
            if move_id.purchase_line_id:
                if move_id.purchase_line_id.order_id:
                    self.purchase_id = move_id.purchase_line_id.order_id
                    return

    purchase_id = fields.Many2one(string="Purchase Order",comodel_name="purchase.order", compute=_compute_purchase_id)
