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

from osv import osv, fields
from tools.translate import _
import tools
import re

import time

import pprint

class crm_lead2opportunity_partner(osv.osv_memory):
    _inherit = 'crm.lead2opportunity.partner'

    def action_apply(self, cr, uid, ids, context=None):
        """
        This converts lead to opportunity and opens Opportunity view
        """
        if not context:
            context = {}
        lead = self.pool.get('crm.lead')
        lead_ids = context.get('active_ids', [])
        data = self.browse(cr, uid, ids, context=context)[0]
        
        # duplicate all ids
        new_lead_ids = []
        for i in lead_ids:
            object_data = lead.copy_data(cr, uid, i)
            
            object_id = lead.create(cr, uid, {}, context=context) 
            # copy_data always copy state as 'new', need to update it
            lead_brw = lead.browse(cr, uid, i, context=context)
            object_data.update({'state' : lead_brw.state})
            lead.write(cr, uid, object_id, object_data, context=context)
            #for calls in 
            new_lead_ids.append(object_id)
        
        self._convert_opportunity(cr, uid, ids, {'lead_ids': new_lead_ids}, context=context)
        #self._convert_opportunity(cr, uid, ids, {'lead_ids': lead_ids}, context=context)
        self._merge_opportunity(cr, uid, ids, data.opportunity_ids, data.name, context=context)
        return lead.redirect_opportunity_view(cr, uid, lead_ids[0], context=context)


crm_lead2opportunity_partner()
