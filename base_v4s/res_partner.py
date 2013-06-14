# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Module base_v4s
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

class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    
    _columns = {
        'phone2': fields.char('Phone2', size=64),
        'birthday_communication': fields.datetime('Birthday'),
        'company_ext' : fields.char('Company Name', size=128),
        'department_company_ext' : fields.char('Department Company', size=128),
        'title_communication' : fields.char('Title', size=255),
        'prename': fields.char('Prename', size=64),
        'website': fields.related('partner_id', 'website', type='char', string='Website'),
    }
    
res_partner_address()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    _columns = {
        'description': fields.text('Notes'),
        'prename': fields.related('address', 'prename', type='char', string='Prename'),
        #'type': fields.related('address', 'type', type='char', string='Address Type'),
        'phone2': fields.related('address', 'phone2', type='char', string='Phone2'),
        'street': fields.related('address', 'street', type='char', string='Street'),    
        'zip': fields.related('address', 'zip', type='char', string='Zip'),
        'city': fields.related('address', 'city', type='char', string='City', store=True),
        'birthday_communication': fields.related('address', 'birthday_communication', type='datetime', string='Birthday'),
        'company_ext': fields.related('address', 'company_ext', type='char', string='Company Name'),    
        'title_communication' : fields.related('address', 'title_communication', type='char', string='Title'), 
        'department_company_ext': fields.related('address', 'department_company_ext', type='char', string='Department Company'),
        'website': fields.char('Website',size=255, help="Website of Partner."),

    }
    
res_partner()