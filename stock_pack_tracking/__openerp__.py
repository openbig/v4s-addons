##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004 -2010 Tiny SPRL (<http://tiny.be>).aking
#
#    Module stock_pack_tracking is copyrighted by 
#    Grzegorz Grzelak of OpenGLOBE (www.openglobe.pl)
#    with the same rules as OpenObject and OpenERP platform
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
    "name" : "Kits tracking as sn collection in Packs",
    "version" : "0.1 (6.1)",
    "author" : "Grzegorz Grzelak - OpenGLOBE",
    "category" : "Enterprise Specific Modules",
    "website" : "http://www.openglobe.pl",
    "description": """
    This module allows you to collect serial numbers
    into packs.

    Functionality:
    * Serial number is treated as production lot number 
        for 1 piece of product.
    * Packs can collect few serial numbers and work as 
        kit consisting few products with serial numbers.
        Kit itself can have its own serial number as 
        Pack number.
    * This collection which is defined in Pack form
        as list on second tab can be used in Pickings
        (Delivery orders, Incoming Shipments and
        Inernal Moves) with wizard Insert Pack.
    * Wizard allows to set Source and Destination
        location for stock moves. And allows to select
        particular Pack. When Pack is selected
        the wizard place in Picking all products from
        Pack with defined serial numbers and with Pack
        number as well.
    * To define new Pack of the same contents (with
        different serial numbers) you can duplicate it.
    REMARKS: This functionality is suitable for unique 
    serial number per 1 piece of product.
""",
    "depends" : ["stock"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
#                    "security/purchase_tender.xml",
                    "wizard/picking_insert_tracking_view.xml",
#                    "purchase_requisition_data.xml",
                    "stock_pack_tracking_view.xml",
#                    "purchase_requisition_report.xml",
#                    "security/ir.model.access.csv",
#                    "purchase_requisition_sequence.xml"
    ],
    "active": False,
    "test":[],
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

