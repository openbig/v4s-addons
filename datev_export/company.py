# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Module datev_export
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

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        "consultant_number" : fields.char('Beraternummer', size=32, help = "Number from 1000 to 9999999"),
        "client_number": fields.char('Mandantennummer', size=32, help = "Number from 0 to 99999"),
#        "guid_number" : fields.char('GUID', size=128, help = "Global Unique Identifier Datenbank - Weltweit eindeutiger Identifizierer (SQL-Server). Technisches Datenelement"),      # Check what is it   !!!!!!!
    }
res_company()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
