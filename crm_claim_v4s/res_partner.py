# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Module crm_claim_v4s
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


from openerp.osv import fields, osv


class res_partner(osv.osv):
    """
    Partner
    """
    _inherit = "res.partner"

    def _claim_count2(self, cr, uid, ids, field_name, arg, context=None):
        Claim = self.pool['crm.claim']
        return {
            partner_id: Claim.search_count(cr,uid, [('partner_id2', '=', partner_id)], context=context)
            for partner_id in ids
        }

    _columns = {
        'claims_ids': fields.one2many('crm.claim', 'partner_id', 'Claims'),
        'claims_ids2': fields.one2many('crm.claim', 'partner_id2', 'Customer Claims'),
        'claim_count2': fields.function(_claim_count2, string='# Claims', type='integer'),
    }


res_partner()