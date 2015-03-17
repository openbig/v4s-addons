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

from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.tools
import re

import time

import pprint

class crm_lead2opportunity_partner(osv.osv_memory):
    _inherit = 'crm.lead2opportunity.partner'


    def action_apply(self, cr, uid, ids, context=None):
        """
        Convert lead to opportunity or merge lead and opportunity and open
        the freshly created opportunity view.
        """
        if context is None:
            context = {}

        lead_obj = self.pool['crm.lead']

        w = self.browse(cr, uid, ids, context=context)[0]
        opp_ids = [o.id for o in w.opportunity_ids]
        if w.name == 'merge':
            lead_id = lead_obj.merge_opportunity(cr, uid, opp_ids, context=context)
            lead_ids = [lead_id]
            lead = lead_obj.read(cr, uid, lead_id, ['type', 'user_id'], context=context)
            if lead['type'] == "lead":
                context = dict(context, active_ids=lead_ids)
                self._convert_opportunity(cr, uid, ids, {'lead_ids': lead_ids, 'user_ids': [w.user_id.id], 'section_id': w.section_id.id}, context=context)
            elif not context.get('no_force_assignation') or not lead['user_id']:
                lead_obj.write(cr, uid, lead_id, {'user_id': w.user_id.id, 'section_id': w.section_id.id}, context=context)
        else:
            lead_ids = context.get('active_ids', [])
            new_lead_ids = []
            for i in lead_ids:
                object_data = lead_obj.copy_data(cr, uid, i)
                object_id = lead_obj.create(cr, uid, object_data, context=context)
                new_lead_ids.append(object_id)
            self._convert_opportunity(cr, uid, ids, {'lead_ids': new_lead_ids, 'user_ids': [w.user_id.id], 'section_id': w.section_id.id}, context=context)

        return self.pool.get('crm.lead').redirect_opportunity_view(cr, uid, lead_ids[0], context=context)


crm_lead2opportunity_partner()
