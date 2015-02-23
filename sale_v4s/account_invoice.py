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

from openerp.osv import fields, osv, orm
#from tools.translate import _

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
        'write_uid': fields.many2one('res.users', 'Last Editor', readonly=True, states={'draft':[('readonly',False)]}),
        'client_order_ref': fields.char('Customer Reference', size=64),
    }
    

      
account_invoice()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
