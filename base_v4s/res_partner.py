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

from openerp.osv import fields, osv

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'birthday_communication': fields.datetime('Birthday'),
        'company_ext' : fields.char('Company Name', size=128),
        'department_company_ext' : fields.char('Department Company', size=128),
        'phone2': fields.char('Phone2', size=64),
        'prename': fields.char('Prename', size=64),
        'title_communication' : fields.char('Title', size=255),
        'description': fields.text('Notes'),
    }

res_partner()