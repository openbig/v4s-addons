# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Module account_v4s
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

import openerp.tools as tools
from openerp.osv import fields,osv


class account_invoice_report(osv.osv):
    _inherit = "account.invoice.report"

    _columns = {
        'invoice_number': fields.char('Invoice number', size=64, readonly=True),
    }

    def _select(self):
        return  super(account_invoice_report, self)._select() + ", sub.invoice_number"

    def _sub_select(self):
        return  super(account_invoice_report, self)._sub_select() + ", ai.number as invoice_number"


account_invoice_report()