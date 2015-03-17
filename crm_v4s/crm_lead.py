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

from openerp.osv import fields, osv
from datetime import datetime
import time
from openerp.tools.translate import _
import binascii
import openerp.tools

class crm_lead(osv.osv):
    _inherit = "crm.lead"
    
    _columns = {
        'prename': fields.char('Prename', size=64),
        'company_ext' : fields.char('Company Name', size=128),
        'department_company_ext' : fields.char('Department Company', size=128),
        'title_communication' : fields.char('Title', size=255),
        'phone2': fields.char('Phone2', size=64),
        'birthday_communication': fields.datetime('Birthday'),
        'partner_address_website': fields.char('Partner Webpage', size=255),
        #'partner_address_website': fields.related('partner_id', 'website', type='char', size=64, string='Partner Webpage'),
        #'partner_address_category_id': fields.related('partner_id', 'category_id', type='one2many', string='Partner Category'),
        'phonecall' : fields.one2many('crm.phonecall', 'opportunity_id', 'Phone Calls', ),
    
        # field for analysis
        'nbr' : fields.integer('# Opportunities'),
        
        #'parent_id': fields.many2one('crm.lead', 'Parent', ondelete='cascade'),
        #'opportunity_ids': fields.one2many('crm.lead','parent_id','Opportunities'),
        
    }
    
    _defaults ={
        'nbr' : 1,
    }

    # def _lead_create_partner(self, cr, uid, lead, context=None):
    #     partner = self.pool.get('res.partner')
    #     partner_id = super(crm_lead,self)._lead_create_partner(cr, uid, lead, context=context)
    #     vals = {
    #             'description' : lead.description,
    #         }
    #     partner.write(cr, uid, partner_id, vals, context=context)
    #     return partner_id
    #
    # def _lead_create_partner_address(self, cr, uid, lead, partner_id, context=None):
    #     address = self.pool.get('res.partner.address')
    #     address_id = super(crm_lead,self)._lead_create_partner_address(cr, uid, lead, partner_id, context=context)
    #     vals = {
    #             'prename': lead.prename,
    #             'company_ext': lead.company_ext,
    #             'title_communication': lead.title_communication,
    #             'phone2': lead.phone2,
    #             'department_company_ext': lead.department_company_ext,
    #             'birthday_communication': lead.birthday_communication,
    #             'website': lead.partner_address_website,
    #         }
    #     address.write(cr, uid, address_id, vals, context=context)
    #     return address_id

crm_lead()