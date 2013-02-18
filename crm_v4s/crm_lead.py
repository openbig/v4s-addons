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

from osv import fields, osv
from datetime import datetime
import time
from tools.translate import _
import binascii
import tools

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
        
        'nbr' : fields.integer('# Opportunities'),
    }
    
    _defaults ={
        'nbr' : 1,
    }
    
    
