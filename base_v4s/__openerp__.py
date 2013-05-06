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


{
    "name" : "V4S - BASE",
    "version" : "0.05 (6.1)",
    "author" : "Grzegorz Grzelak / Thorsten Vocks for openbig.org",
    "website": "http://www.openbig.org",
    "category" : "Localisation/Country specific stuff",
    "description": """
    Added new fields to customer view.
    """,
    "depends" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "res_partner_view.xml",
                    ],
    "active": False,
    "installable": True
}

