# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Module sale_v4s
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
    "name" : "V4S - SALE",
    "version" : "0.10 (6.1)",
    "author" : "Grzegorz Grzelak / Thorsten Vocks for openbig.org",
    "website": "http://www.openbig.org",
    "category" : "Localisation/Country specific stuff",
    "description": """
    * Added MTO fields for Sale Shop.
    * new Sale Order report (0.02)
    """,
    "depends" : ["sale","report_aeroo", "base_v4s"],
    "demo_xml" : [],
    "update_xml" : [
                    "sale_view.xml",
                    "stock_view.xml",
                    "account_invoice_view.xml",
                    "report/sale_report.xml",
                    ],
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


